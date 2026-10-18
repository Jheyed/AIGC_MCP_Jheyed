"""Statically inventory imported ComfyUI workflows without loading custom nodes."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKFLOW_DIR = (
    PROJECT_ROOT / "runtime" / "comfy" / "user" / "default" / "workflows"
)
MODEL_SUFFIXES = {
    ".safetensors",
    ".ckpt",
    ".pt",
    ".pth",
    ".bin",
    ".gguf",
    ".onnx",
}

# These nodes are serialized in workflow JSON for canvas/UI behavior but are not
# expected to appear in the backend /object_info registry.
CORE_FRONTEND_VIRTUAL_TYPES = {
    "MarkdownNote",
    "Note",
    "Reroute",
}

# Static provenance gathered from the archived custom-node source tree.  This
# lets the audit distinguish a known, currently inactive backend extension from
# a genuinely unidentified node without importing any archived Python code.
KNOWN_BACKEND_CUSTOM_SOURCES = {
    "AnimaArtistCrossAttn": "Anima-Artist-Mixer",
    "AnimaArtistOptions": "Anima-Artist-Mixer",
    "AnimaArtistPack": "Anima-Artist-Mixer",
    "AnimaBoosterLoader": "ANIMA_BOOSTER",
    "AnimaDexBrowser": "ComfyUI-Danbooru-Anima-Prompt",
    "AnimaLayerReplayPatcher": "ComfyUI-Anima-Enhancer",
    "AnimaPromptConverter": "ComfyUI-Danbooru-Anima-Prompt",
    "AnimaTeaCache": "ANIMA_BOOSTER",
    "Any Switch (rgthree)": "rgthree-comfy",
    "Comfly_LLm_API": "Comfyui-zhenzhen",
    "DanbooruBrowser": "ComfyUI-Danbooru-Anima-Prompt",
    "DanbooruNodeBypass": "ComfyUI-Danbooru-Anima-Prompt",
    "DanbooruTagClassifier": "ComfyUI-Danbooru-Anima-Prompt",
    "DanbooruTagDedup": "ComfyUI-Danbooru-Anima-Prompt",
    "DanbooruTagPreview": "ComfyUI-Danbooru-Anima-Prompt",
    "DanbooruText": "ComfyUI-Danbooru-Anima-Prompt",
    "DanbooruTextAdvanced": "ComfyUI-Danbooru-Anima-Prompt",
    "DanbooruTextConcat": "ComfyUI-Danbooru-Anima-Prompt",
    "DanbooruTextPassthrough": "ComfyUI-Danbooru-Anima-Prompt",
    "FLS_SamplerV4": "ComfyUI-BSS_FLSampler",
    "Float": "ComfyLiterals",
    "GroupIgnoreManager": "ComfyUI-Danbooru-Gallery",
    "Image Comparer (rgthree)": "rgthree-comfy",
    "LayerUtility: ImageScaleByAspectRatio V2": "ComfyUI_Swwan",
    "Lora Loader (LoraManager)": "ComfyUI-Lora-Manager",
    "RTXVideoSuperResolution": "Nvidia_RTX_Nodes_ComfyUI",
    "Seed (rgthree)": "rgthree-comfy",
    "TTResolutionSelector": "ComfyUI-TT-Resolution_selector-Node",
    "TagMapper": "ComfyUI-Danbooru-Anima-Prompt",
    "WD14Tagger|pysssss": "ComfyUI-WD14-Tagger",
    "easy cleanGpuUsed": "ComfyUI-Easy-Use",
    "easy float": "ComfyUI-Easy-Use",
    "easy showAnything": "ComfyUI-Easy-Use",
    "llama_cpp_instruct_adv": "ComfyUI-llama-cpp_vlm",
    "llama_cpp_model_loader": "ComfyUI-llama-cpp_vlm",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inventory legacy workflows and compare nodes with live ComfyUI."
    )
    parser.add_argument("--workflow-dir", type=Path, default=DEFAULT_WORKFLOW_DIR)
    parser.add_argument("--comfy-url", default="http://127.0.0.1:8188")
    parser.add_argument(
        "--compact", action="store_true", help="Omit per-node details from output"
    )
    return parser.parse_args()


def fetch_core_node_types(comfy_url: str) -> set[str]:
    with urllib.request.urlopen(f"{comfy_url.rstrip('/')}/object_info", timeout=20) as response:
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise RuntimeError("ComfyUI object_info did not return an object")
    return set(payload)


def iter_graphs(workflow: dict[str, Any]):
    yield "root", workflow
    definitions = workflow.get("definitions")
    if not isinstance(definitions, dict):
        return
    subgraphs = definitions.get("subgraphs")
    if not isinstance(subgraphs, list):
        return
    for subgraph in subgraphs:
        if isinstance(subgraph, dict):
            name = subgraph.get("name") or subgraph.get("id") or "unnamed"
            yield f"subgraph:{name}", subgraph


def collect_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for child in value:
            yield from collect_strings(child)
    elif isinstance(value, dict):
        for child in value.values():
            yield from collect_strings(child)


def is_model_reference(value: str) -> bool:
    lowered = value.lower().split("?", 1)[0]
    return any(lowered.endswith(suffix) for suffix in MODEL_SUFFIXES)


def classify_unavailable_type(
    node_type: str, origin_ids: set[str]
) -> tuple[str, str | None]:
    """Classify a type absent from the live backend without importing plugins."""
    if node_type in CORE_FRONTEND_VIRTUAL_TYPES or "comfy-core" in origin_ids:
        return "core_frontend_virtual", None
    source = KNOWN_BACKEND_CUSTOM_SOURCES.get(node_type)
    if source:
        return "backend_custom", source
    custom_origin_ids = sorted(origin_id for origin_id in origin_ids if origin_id)
    if custom_origin_ids:
        return "backend_custom", ", ".join(custom_origin_ids)
    return "missing", None


def audit_workflow(path: Path, core_types: set[str]) -> dict[str, Any]:
    workflow = json.loads(path.read_text(encoding="utf-8-sig"))
    nodes: list[dict[str, Any]] = []
    node_type_counts: Counter[str] = Counter()
    node_origin_ids: dict[str, set[str]] = {}
    model_references: set[str] = set()
    workflow_format = "ui" if isinstance(workflow.get("nodes"), list) else "api"
    if workflow_format == "api":
        api_nodes = []
        for node_id, node in workflow.items():
            if not isinstance(node, dict) or "class_type" not in node:
                continue
            inputs = node.get("inputs") if isinstance(node.get("inputs"), dict) else {}
            api_nodes.append(
                {
                    "id": node_id,
                    "type": node.get("class_type"),
                    "title": (node.get("_meta") or {}).get("title"),
                    "mode": 0,
                    "widgets_values": inputs,
                    "inputs": [{"name": name} for name in inputs],
                    "outputs": [],
                }
            )
        graphs = [("root", {"nodes": api_nodes})]
    else:
        graphs = list(iter_graphs(workflow))

    for graph_name, graph in graphs:
        graph_nodes = graph.get("nodes", [])
        if not isinstance(graph_nodes, list):
            continue
        for node in graph_nodes:
            if not isinstance(node, dict):
                continue
            node_type = str(node.get("type", "<missing>"))
            properties = node.get("properties")
            if not isinstance(properties, dict):
                properties = {}
            origin_id = properties.get("cnr_id")
            if isinstance(origin_id, str) and origin_id:
                node_origin_ids.setdefault(node_type, set()).add(origin_id)
            widgets = node.get("widgets_values")
            for text in collect_strings(widgets):
                if is_model_reference(text):
                    model_references.add(text)
            node_type_counts[node_type] += 1
            nodes.append(
                {
                    "graph": graph_name,
                    "id": node.get("id"),
                    "type": node_type,
                    "title": node.get("title"),
                    "mode": node.get("mode", 0),
                    "origin_id": origin_id,
                    "widgets_values": widgets,
                    "input_names": [
                        item.get("name")
                        for item in node.get("inputs", [])
                        if isinstance(item, dict)
                    ],
                    "output_names": [
                        item.get("name")
                        for item in node.get("outputs", [])
                        if isinstance(item, dict)
                    ],
                }
            )

    unavailable_types = sorted(
        node_type for node_type in node_type_counts if node_type not in core_types
    )
    unavailable_type_classification: dict[str, dict[str, str]] = {}
    classified_types: dict[str, list[str]] = {
        "backend_custom": [],
        "core_frontend_virtual": [],
        "missing": [],
    }
    for node_type in unavailable_types:
        category, source = classify_unavailable_type(
            node_type, node_origin_ids.get(node_type, set())
        )
        classified_types[category].append(node_type)
        details = {"category": category}
        if source:
            details["source"] = source
        unavailable_type_classification[node_type] = details
    return {
        "file": path.name,
        "bytes": path.stat().st_size,
        "workflow_id": workflow.get("id"),
        "format": workflow_format,
        "node_count": sum(node_type_counts.values()),
        "node_type_counts": dict(sorted(node_type_counts.items())),
        "unavailable_types": unavailable_types,
        "backend_custom_types": classified_types["backend_custom"],
        "core_frontend_virtual_types": classified_types[
            "core_frontend_virtual"
        ],
        "missing_types": classified_types["missing"],
        "unavailable_type_classification": unavailable_type_classification,
        "model_references": sorted(model_references),
        "nodes": nodes,
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    workflow_dir = args.workflow_dir.resolve()
    core_types = fetch_core_node_types(args.comfy_url)
    reports = []
    for path in sorted(workflow_dir.glob("*.json")):
        if path.name.startswith("."):
            continue
        reports.append(audit_workflow(path, core_types))
    if args.compact:
        for report in reports:
            report.pop("nodes", None)
    output = {
        "schema_version": 2,
        "workflow_dir": str(workflow_dir),
        "core_node_type_count": len(core_types),
        "workflow_count": len(reports),
        "workflows": reports,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
