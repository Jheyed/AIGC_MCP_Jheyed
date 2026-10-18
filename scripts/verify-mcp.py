"""Verify the installed Comfy MCP over the standard stdio transport.

This is intentionally an ordinary Python client rather than an Agent-specific
test. A successful run proves that any conforming MCP client can initialize the
server, discover its tools, and call the local server_info tool.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import anyio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = PROJECT_ROOT / "runtime"
SCRIPTS_DIR = RUNTIME_ROOT / "python" / "Scripts"
MCP_COMMAND = SCRIPTS_DIR / "comfy-mcp.exe"
COMFY_COMMAND = SCRIPTS_DIR / "comfy.exe"


async def verify() -> None:
    if not MCP_COMMAND.is_file():
        raise FileNotFoundError(f"MCP command not found: {MCP_COMMAND}")
    if not COMFY_COMMAND.is_file():
        raise FileNotFoundError(f"Comfy CLI not found: {COMFY_COMMAND}")

    child_env = {
        "COMFY_BIN": str(COMFY_COMMAND),
        "COMFY_LOCAL_URL": "http://127.0.0.1:8188",
        "PATH": f"{SCRIPTS_DIR}{os.pathsep}{os.environ.get('PATH', '')}",
    }
    server = StdioServerParameters(
        command=str(MCP_COMMAND),
        args=[],
        env=child_env,
    )

    async with stdio_client(server) as streams:
        async with ClientSession(*streams) as session:
            initialized = await session.initialize()
            tools = await session.list_tools()
            tool_names = sorted(tool.name for tool in tools.tools)

            if "server_info" not in tool_names:
                raise RuntimeError("MCP initialized but did not advertise server_info")

            server_info = await session.call_tool("server_info", {})
            if server_info.is_error:
                raise RuntimeError(f"server_info failed: {server_info}")

            report = {
                "initialized": True,
                "server": initialized.server_info.model_dump(mode="json"),
                "tool_count": len(tool_names),
                "has_server_info": True,
                "server_info": server_info.model_dump(mode="json"),
            }
            print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    anyio.run(verify)
