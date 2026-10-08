"""
server.py — VirtStack Read-Only MCP Server (FastMCP)

Exposes 28 read-only tools that AI agents (OpenWebUI, Claude Desktop) can call
to inspect VirtStack infrastructure. Supports both stdio and SSE transports.

Run:
    python server.py              # SSE mode (default) — for OpenWebUI
    MCP_TRANSPORT=stdio python server.py   # stdio mode — for Claude Desktop
"""

import logging
import os
import sys

# Add current directory to path so imports resolve correctly
sys.path.insert(0, os.path.dirname(__file__))

from fastmcp import FastMCP
from virtstack_client import client

# ── Tool imports ───────────────────────────────────────────────────────────────
from tools.system import get_health, get_server_info, global_search
from tools.hosts import list_hosts, get_host_detail, get_host_capabilities, get_host_metrics
from tools.vms import (
    list_vms, list_host_vms, get_vm_detail, get_vm_metrics,
    get_vm_xml, get_vm_hardware, get_vm_dependents, list_vm_snapshots,
)
from tools.storage import list_storage_pools, list_pool_volumes, list_iso_images
from tools.networks import list_networks, list_bridges
from tools.ha import list_ha_clusters, get_ha_cluster_state, get_ha_preflight
from tools.forensics import get_placement_log, get_placement_preview, get_task_status, get_audit_events

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("virtstack_mcp.server")

# ── Create MCP app ─────────────────────────────────────────────────────────────
mcp = FastMCP(
    name="VirtStack Read-Only MCP",
    instructions=(
        "You have access to VirtStack — a KVM/libvirt-based private cloud platform. "
        "Use these tools to inspect hosts, VMs, storage, networks, and HA clusters. "
        "All tools are strictly read-only; no changes can be made through this interface."
    ),
)

# ── Register tools ─────────────────────────────────────────────────────────────

# System
mcp.tool()(get_health)
mcp.tool()(get_server_info)
mcp.tool()(global_search)

# Hosts
mcp.tool()(list_hosts)
mcp.tool()(get_host_detail)
mcp.tool()(get_host_capabilities)
mcp.tool()(get_host_metrics)

# VMs
mcp.tool()(list_vms)
mcp.tool()(list_host_vms)
mcp.tool()(get_vm_detail)
mcp.tool()(get_vm_metrics)
mcp.tool()(get_vm_xml)
mcp.tool()(get_vm_hardware)
mcp.tool()(get_vm_dependents)
mcp.tool()(list_vm_snapshots)

# Storage
mcp.tool()(list_storage_pools)
mcp.tool()(list_pool_volumes)
mcp.tool()(list_iso_images)

# Networks
mcp.tool()(list_networks)
mcp.tool()(list_bridges)

# HA
mcp.tool()(list_ha_clusters)
mcp.tool()(get_ha_cluster_state)
mcp.tool()(get_ha_preflight)

# Forensics
mcp.tool()(get_placement_log)
mcp.tool()(get_placement_preview)
mcp.tool()(get_task_status)
mcp.tool()(get_audit_events)

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "http").lower()

    if transport == "stdio":
        logger.info("Starting VirtStack MCP in stdio mode (Claude Desktop)")
        mcp.run(transport="stdio")
    else:
        import uvicorn
        from starlette.applications import Starlette
        from starlette.routing import Route

        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "8765"))

        # Build both SSE and Streamable HTTP (FastMCP) apps
        app_sse = mcp.http_app(transport="sse")
        app_http = mcp.http_app(transport="http")

        http_app = app_http.routes[0].app
        sse_app = app_sse.routes[0].app

        # Universal dispatcher on /sse:
        # OpenWebUI uses Streamable HTTP (POST), standard SSE clients use GET
        class UniversalDispatcher:
            def __init__(self, sse, http):
                self.sse = sse
                self.http = http

            async def __call__(self, scope, receive, send):
                if scope.get("method") == "POST":
                    await self.http(scope, receive, send)
                else:
                    await self.sse(scope, receive, send)

        dispatcher = UniversalDispatcher(sse_app, http_app)

        routes = [
            Route("/mcp", endpoint=http_app),
            Route("/sse", endpoint=dispatcher),
            Route("/", endpoint=http_app),
        ] + [r for r in app_sse.routes if r.path != "/sse"]

        combined_app = Starlette(
            routes=routes,
            lifespan=app_http.router.lifespan_context,
        )

        logger.info("Starting VirtStack MCP Server on http://%s:%s", host, port)
        logger.info("OpenWebUI MCP URL: http://172.17.0.1:%s/mcp (or /sse)", port)
        uvicorn.run(combined_app, host=host, port=port, log_level="info")
