"""
api.py — VirtStack Read-Only MCP Web API (FastAPI + Swagger UI)

Exposes all 28 MCP tools as REST endpoints so humans can test them
in a browser at http://localhost:8080/docs

Run:
    python api.py
    # Then open: http://localhost:8080/docs
"""

import logging
import os
import sys
from typing import Any, Optional

# Add current directory to path so imports resolve correctly
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic_settings import BaseSettings, SettingsConfigDict

from virtstack_client import client, ReadOnlyViolationError

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

app = FastAPI(
    title="VirtStack Read-Only MCP — Web API",
    description=(
        "A **read-only** inspection API for VirtStack private cloud infrastructure.\n\n"
        "All endpoints are safe `GET` requests — no changes can be made.\n\n"
        "**This is the human-facing Swagger interface for the VirtStack FastMCP server.**"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ── Error helper ───────────────────────────────────────────────────────────────
def _handle(exc: Exception):
    if isinstance(exc, ReadOnlyViolationError):
        raise HTTPException(status_code=403, detail=str(exc))
    raise HTTPException(status_code=502, detail=f"VirtStack API error: {exc}")


# ── System endpoints ───────────────────────────────────────────────────────────
@app.get("/api/v1/mcp/health", tags=["System"], summary="Check VirtStack control plane health")
async def api_get_health() -> Any:
    try:
        return await get_health()
    except Exception as e:
        _handle(e)


@app.get("/api/v1/mcp/server-info", tags=["System"], summary="Get VirtStack server configuration info")
async def api_get_server_info() -> Any:
    try:
        return await get_server_info()
    except Exception as e:
        _handle(e)


@app.get("/api/v1/mcp/search", tags=["System"], summary="Search for VMs, hosts, IPs, or disks")
async def api_global_search(q: str = Query(..., description="Search term (e.g. hostname, IP, VM name)")) -> Any:
    try:
        return await global_search(q)
    except Exception as e:
        _handle(e)


# ── Host endpoints ─────────────────────────────────────────────────────────────
@app.get("/api/v1/mcp/hosts", tags=["Hosts"], summary="List all physical servers")
async def api_list_hosts() -> Any:
    try:
        return await list_hosts()
    except Exception as e:
        _handle(e)


@app.get("/api/v1/mcp/hosts/{host_id}", tags=["Hosts"], summary="Get physical server details")
async def api_get_host_detail(host_id: str) -> Any:
    try:
        return await get_host_detail(host_id)
    except Exception as e:
        _handle(e)


@app.get("/api/v1/mcp/hosts/{host_id}/capabilities", tags=["Hosts"], summary="Get CPU, RAM, NUMA capabilities")
async def api_get_host_capabilities(host_id: str) -> Any:
    try:
        return await get_host_capabilities(host_id)
    except Exception as e:
        _handle(e)


@app.get("/api/v1/mcp/hosts/{host_id}/metrics", tags=["Hosts"], summary="Get live CPU, RAM, disk, and network metrics")
async def api_get_host_metrics(host_id: str) -> Any:
    try:
        return await get_host_metrics(host_id)
    except Exception as e:
        _handle(e)


# ── VM endpoints ───────────────────────────────────────────────────────────────
@app.get("/api/v1/mcp/vms", tags=["Virtual Machines"], summary="List all VMs across the platform")
async def api_list_vms() -> Any:
    try:
        return await list_vms()
    except Exception as e:
        _handle(e)


@app.get("/api/v1/mcp/hosts/{host_id}/vms", tags=["Virtual Machines"], summary="List VMs on a specific host")
async def api_list_host_vms(host_id: str) -> Any:
    try:
        return await list_host_vms(host_id)
    except Exception as e:
        _handle(e)


@app.get("/api/v1/mcp/vms/{vm_id}", tags=["Virtual Machines"], summary="Get full VM details")
async def api_get_vm_detail(vm_id: str) -> Any:
    try:
        return await get_vm_detail(vm_id)
    except Exception as e:
        _handle(e)


@app.get("/api/v1/mcp/hosts/{host_id}/vms/{vm_id}/metrics", tags=["Virtual Machines"], summary="Get live VM metrics")
async def api_get_vm_metrics(host_id: str, vm_id: str) -> Any:
    try:
        return await get_vm_metrics(host_id, vm_id)
    except Exception as e:
        _handle(e)


@app.get("/api/v1/mcp/vms/{vm_id}/xml", tags=["Virtual Machines"], summary="Get raw KVM Libvirt XML definition", response_class=PlainTextResponse)
async def api_get_vm_xml(vm_id: str) -> str:
    try:
        return await get_vm_xml(vm_id)
    except Exception as e:
        _handle(e)


@app.get("/api/v1/mcp/vms/{vm_id}/hardware", tags=["Virtual Machines"], summary="Get emulated hardware config (TPM, virtio, etc.)")
async def api_get_vm_hardware(vm_id: str) -> Any:
    try:
        return await get_vm_hardware(vm_id)
    except Exception as e:
        _handle(e)


@app.get("/api/v1/mcp/vms/{vm_id}/dependents", tags=["Virtual Machines"], summary="Get child clones linked to this VM disk")
async def api_get_vm_dependents(vm_id: str) -> Any:
    try:
        return await get_vm_dependents(vm_id)
    except Exception as e:
        _handle(e)


@app.get("/api/v1/mcp/vms/{vm_id}/snapshots", tags=["Virtual Machines"], summary="List all VM snapshots")
async def api_list_vm_snapshots(vm_id: str) -> Any:
    try:
        return await list_vm_snapshots(vm_id)
    except Exception as e:
        _handle(e)


# ── Storage endpoints ──────────────────────────────────────────────────────────
@app.get("/api/v1/mcp/storage-pools", tags=["Storage"], summary="List all storage pools")
async def api_list_storage_pools() -> Any:
    try:
        return await list_storage_pools()
    except Exception as e:
        _handle(e)


@app.get("/api/v1/mcp/hosts/{host_id}/storage-pools/{pool_name}/volumes", tags=["Storage"], summary="List volumes in a storage pool")
async def api_list_pool_volumes(host_id: str, pool_name: str) -> Any:
    try:
        return await list_pool_volumes(host_id, pool_name)
    except Exception as e:
        _handle(e)


@app.get("/api/v1/mcp/storage/isos", tags=["Storage"], summary="List ISO images in the library")
async def api_list_iso_images() -> Any:
    try:
        return await list_iso_images()
    except Exception as e:
        _handle(e)


# ── Network endpoints ──────────────────────────────────────────────────────────
@app.get("/api/v1/mcp/networks", tags=["Networks"], summary="List all virtual networks")
async def api_list_networks() -> Any:
    try:
        return await list_networks()
    except Exception as e:
        _handle(e)


@app.get("/api/v1/mcp/hosts/{host_id}/bridges", tags=["Networks"], summary="List physical network bridges on a host")
async def api_list_bridges(host_id: str) -> Any:
    try:
        return await list_bridges(host_id)
    except Exception as e:
        _handle(e)


# ── HA endpoints ───────────────────────────────────────────────────────────────
@app.get("/api/v1/mcp/ha/clusters", tags=["High Availability"], summary="List all HA clusters")
async def api_list_ha_clusters() -> Any:
    try:
        return await list_ha_clusters()
    except Exception as e:
        _handle(e)


@app.get("/api/v1/mcp/ha/cluster-status/{host_id}", tags=["High Availability"], summary="Get live Pacemaker cluster state")
async def api_get_ha_cluster_state(host_id: str) -> Any:
    try:
        return await get_ha_cluster_state(host_id)
    except Exception as e:
        _handle(e)


@app.get("/api/v1/mcp/ha/preflight/{host_id}", tags=["High Availability"], summary="Run HA preflight checks on a host")
async def api_get_ha_preflight(host_id: str) -> Any:
    try:
        return await get_ha_preflight(host_id)
    except Exception as e:
        _handle(e)


# ── Forensics endpoints ────────────────────────────────────────────────────────
@app.get("/api/v1/mcp/placement/log", tags=["Forensics"], summary="Get VM placement scheduler decision log")
async def api_get_placement_log(limit: int = Query(20, ge=1, le=500, description="Number of entries")) -> Any:
    try:
        return await get_placement_log(limit)
    except Exception as e:
        _handle(e)


@app.get("/api/v1/mcp/vms/{vm_id}/placement-preview", tags=["Forensics"], summary="Preview which host would be chosen for a VM")
async def api_get_placement_preview(vm_id: str) -> Any:
    try:
        return await get_placement_preview(vm_id)
    except Exception as e:
        _handle(e)


@app.get("/api/v1/mcp/tasks/{task_id}", tags=["Forensics"], summary="Get background task status and error details")
async def api_get_task_status(task_id: str) -> Any:
    try:
        return await get_task_status(task_id)
    except Exception as e:
        _handle(e)


@app.get("/api/v1/mcp/audit-logs", tags=["Forensics"], summary="Get recent audit events (who changed what)")
async def api_get_audit_events(limit: int = Query(50, ge=1, le=100, description="Number of entries")) -> Any:
    try:
        return await get_audit_events(limit)
    except Exception as e:
        _handle(e)


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", "8080"))
    print(f"\n{'='*60}")
    print(f"  VirtStack MCP Web API")
    print(f"  Swagger UI:  http://localhost:{port}/docs")
    print(f"  ReDoc:       http://localhost:{port}/redoc")
    print(f"{'='*60}\n")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
