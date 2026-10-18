"""Run the first local image workflow through the standard MCP protocol.

This is intentionally a normal command-line MCP client. It is not coupled to
Codex and can also serve as a reference for any other Agent or UI adapter.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import anyio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = PROJECT_ROOT / "runtime"
SCRIPTS_DIR = RUNTIME_ROOT / "python" / "Scripts"
MCP_COMMAND = SCRIPTS_DIR / "comfy-mcp.exe"
COMFY_COMMAND = SCRIPTS_DIR / "comfy.exe"
DEFAULT_WORKFLOW = (
    PROJECT_ROOT / "workflows" / "official" / "image_z_image_turbo_int8.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate one local image through Comfy MCP."
    )
    parser.add_argument("--prompt", required=True, help="Natural-language image prompt")
    parser.add_argument(
        "--workflow",
        type=Path,
        default=DEFAULT_WORKFLOW,
        help="Frontend-format ComfyUI workflow JSON",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=1800.0,
        help="Maximum seconds to wait for generation",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help=(
            "Skip MCP validate_workflow only when a separate official template "
            "check has already reported the workflow runnable"
        ),
    )
    return parser.parse_args()


def replace_prompt(value: Any, prompt: str) -> list[str]:
    """Replace CLIPTextEncode widget text anywhere in a UI workflow."""
    changed: list[str] = []
    if isinstance(value, dict):
        if value.get("type") == "CLIPTextEncode":
            widgets = value.get("widgets_values")
            if isinstance(widgets, list) and widgets and isinstance(widgets[0], str):
                widgets[0] = prompt
                changed.append(str(value.get("id", "unknown")))
        for child in value.values():
            changed.extend(replace_prompt(child, prompt))
    elif isinstance(value, list):
        for child in value:
            changed.extend(replace_prompt(child, prompt))
    return changed


def result_payload(result: Any) -> Any:
    if result.is_error:
        rendered = [getattr(item, "text", repr(item)) for item in result.content]
        raise RuntimeError("MCP tool failed: " + "\n".join(rendered))
    for item in result.content:
        text = getattr(item, "text", None)
        if not text:
            continue
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            continue
    return result.model_dump(mode="json")


def find_key(value: Any, key: str) -> Any | None:
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for child in value.values():
            found = find_key(child, key)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_key(child, key)
            if found is not None:
                return found
    return None


async def run(args: argparse.Namespace) -> None:
    workflow_path = args.workflow.resolve()
    if not workflow_path.is_file():
        raise FileNotFoundError(f"Workflow not found: {workflow_path}")

    workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    changed = replace_prompt(workflow, args.prompt)
    if len(changed) != 1:
        raise RuntimeError(
            "Expected exactly one CLIPTextEncode prompt node, "
            f"but changed {len(changed)} nodes: {changed}"
        )

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-z-image-mvp"
    run_dir = RUNTIME_ROOT / "runs" / run_id
    output_dir = run_dir / "outputs"
    run_dir.mkdir(parents=True, exist_ok=False)
    output_dir.mkdir()
    prepared_workflow = run_dir / "workflow.json"
    prepared_workflow.write_text(
        json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    manifest: dict[str, Any] = {
        "schema_version": 1,
        "run_id": run_id,
        "created_at": datetime.now().astimezone().isoformat(),
        "source_workflow": str(workflow_path),
        "prepared_workflow": str(prepared_workflow),
        "prompt": args.prompt,
        "prompt_node_ids": changed,
        "transport": "MCP stdio",
        "mcp_server": str(MCP_COMMAND),
        "status": "prepared",
    }
    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    child_env = {
        "COMFY_BIN": str(COMFY_COMMAND),
        "COMFY_LOCAL_URL": "http://127.0.0.1:8188",
        "COMFY_WHERE": "local",
        "PATH": f"{SCRIPTS_DIR}{os.pathsep}{os.environ.get('PATH', '')}",
    }
    server = StdioServerParameters(command=str(MCP_COMMAND), args=[], env=child_env)

    try:
        async with stdio_client(server) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()

                if args.skip_validation:
                    manifest["validation"] = {
                        "skipped": True,
                        "reason": (
                            "Explicit compatibility workaround; run only after "
                            "official template check reports runnable."
                        ),
                    }
                else:
                    validation = result_payload(
                        await session.call_tool(
                            "validate_workflow",
                            {"workflow_path": str(prepared_workflow)},
                        )
                    )
                    manifest["validation"] = validation
                    if find_key(validation, "valid") is not True:
                        raise RuntimeError(
                            "Workflow did not pass validation: "
                            + json.dumps(validation, ensure_ascii=False)
                        )

                submitted = result_payload(
                    await session.call_tool(
                        "run_workflow",
                        {
                            "workflow_path": str(prepared_workflow),
                            "wait": False,
                            "confirm_spend": False,
                        },
                    )
                )
                manifest["submission"] = submitted
                prompt_id = find_key(submitted, "prompt_id")
                if not isinstance(prompt_id, str) or not prompt_id:
                    raise RuntimeError(
                        "MCP submission returned no prompt_id: "
                        + json.dumps(submitted, ensure_ascii=False)
                    )
                manifest["prompt_id"] = prompt_id
                manifest["status"] = "submitted"
                manifest_path.write_text(
                    json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                print(json.dumps({"event": "submitted", "prompt_id": prompt_id}))

                completed = result_payload(
                    await session.call_tool(
                        "job",
                        {
                            "action": "wait",
                            "prompt_id": prompt_id,
                            "timeout_seconds": args.timeout,
                        },
                    )
                )
                manifest["completion"] = completed
                if find_key(completed, "timed_out") is True:
                    raise TimeoutError(f"Generation timed out: {prompt_id}")

                fetched = result_payload(
                    await session.call_tool(
                        "fetch_outputs",
                        {
                            "prompt_id": prompt_id,
                            "out_dir": str(output_dir),
                            "url_only": False,
                            "inline_images": False,
                        },
                    )
                )
                manifest["outputs"] = fetched
                manifest["status"] = "completed"
                manifest["completed_at"] = datetime.now().astimezone().isoformat()
    except BaseException as exc:
        manifest["status"] = "failed"
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        raise

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    files = [str(path) for path in output_dir.rglob("*") if path.is_file()]
    print(
        json.dumps(
            {
                "event": "completed",
                "run_id": run_id,
                "manifest": str(manifest_path),
                "files": files,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    anyio.run(run, parse_args())
