# VirtStack-Mcp Architecture & Design

## Overview
`VirtStack-Mcp` is a standalone, strictly read-only Model Context Protocol (MCP) server that connects AI assistants (OpenWebUI, Claude Desktop, Cursor) and human operators to VirtStack private cloud infrastructure without modifying any VirtStack core code.

```
┌─────────────────────────┐          ┌──────────────────────────┐
│  AI Agent (OpenWebUI)   │          │  Human Operator (Browser)│
│  via MCP Streamable HTTP│          │  via Swagger UI (:8080)  │
└────────────┬────────────┘          └────────────┬─────────────┘
             │ :8765/mcp                          │ :8080/docs
             ▼                                    ▼
┌─────────────────────────┐          ┌──────────────────────────┐
│        server.py        │          │          api.py          │
│     (FastMCP Server)    │          │      (FastAPI App)       │
└────────────┬────────────┘          └────────────┬─────────────┘
             │                                    │
             └──────────────────┬─────────────────┘
                                │ Calls
                                ▼
                     ┌─────────────────────┐
                     │   tools/ Modules    │
                     │  27 Read-Only Tools │
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │ virtstack_client.py │
                     │  (Enforces GET Only)│
                     └──────────┬──────────┘
                                │ HTTPS (self-signed TLS)
                                ▼
                     ┌─────────────────────┐
                     │  VirtStack Backend  │
                     │  https://<ip>:3000  │
                     └─────────────────────┘
```

---

## Key Design Principles

### 1. Zero Code Modification to VirtStack
The server runs completely external to VirtStack as a separate process or container. It communicates solely over VirtStack's standard REST API (`/api/v1/...`).

### 2. Strictly Read-Only Enforcement
Safety is guaranteed at the client layer:
- `virtstack_client.py` only exposes `get()`.
- Any attempt to invoke `post()`, `put()`, `patch()`, or `delete()` immediately raises a `ReadOnlyViolationError`.
- Mutating endpoints, administrative control actions, and dangerous shells (`/api/v1/shell`) are explicitly excluded.

### 3. Dual-Interface Pattern
- **For AI Agents:** `server.py` implements FastMCP with universal transport support:
  - **Streamable HTTP (`/mcp`)**: Native protocol used by OpenWebUI.
  - **Server-Sent Events (`/sse`)**: Compatible with SSE clients.
  - **Standard I/O (`stdio`)**: Compatible with Claude Desktop and command-line clients.
- **For Humans & Testing:** `api.py` exposes all 27 tools as standard HTTP REST routes with interactive Swagger documentation (`http://localhost:8080/docs`).

### 4. Headless In-Memory Authentication
- User credentials (`VIRTSTACK_USERNAME`, `VIRTSTACK_PASSWORD`) are loaded securely from `.env`.
- Auto-login performs JWT acquisition on demand via `POST /api/v1/auth/login`.
- JWT access tokens are cached strictly in process memory and refreshed automatically on expiry (HTTP 401).
- Self-signed TLS certificates are handled safely via `verify=False` configuration in `httpx.AsyncClient`.

---

## Directory Structure

```text
VirtStack-Mcp/
├── server.py              # Universal FastMCP server (Streamable HTTP + SSE + stdio)
├── api.py                 # FastAPI application with Swagger documentation
├── virtstack_client.py    # Authenticated, read-only HTTP client
├── requirements.txt       # Python dependencies (fastmcp, fastapi, uvicorn, httpx)
├── .env.example           # Configuration template
├── .gitignore             # Excludes .env and Python build artifacts
├── README.md              # Project documentation and quick start
├── docs/
│   ├── ARCHITECTURE.md    # System design & security architecture
│   ├── OPENWEBUI_SETUP.md # OpenWebUI integration & troubleshooting
│   └── TOOLS_REFERENCE.md # Complete reference of all 27 inspection tools
├── tests/
│   ├── __init__.py
│   └── test_virtstack_client.py # Client and read-only enforcement tests
└── tools/
    ├── __init__.py
    ├── system.py          # Health, info, global search
    ├── hosts.py           # Physical hypervisor hosts, metrics, capabilities
    ├── vms.py             # Virtual machines, state, specs, snapshots, XML
    ├── storage.py         # Storage pools, volumes, ISO library
    ├── networks.py        # Virtual networks and Linux bridges
    ├── ha.py              # HA clusters, Pacemaker state, preflight checks
    └── forensics.py       # Placement engine logs, audit trail, background tasks
```

---

## Tool Category Mapping

| Category | Module | Tools | VirtStack API Prefix |
| :--- | :--- | :--- | :--- |
| **System** | `tools/system.py` | `get_health`, `get_server_info`, `global_search` | `/api/v1/system`, `/api/v1/search` |
| **Hosts** | `tools/hosts.py` | `list_hosts`, `get_host_detail`, `get_host_capabilities`, `get_host_metrics` | `/api/v1/hosts` |
| **VMs** | `tools/vms.py` | `list_vms`, `list_host_vms`, `get_vm_detail`, `get_vm_metrics`, `get_vm_xml`, `get_vm_hardware`, `get_vm_dependents`, `list_vm_snapshots` | `/api/v1/vms` |
| **Storage** | `tools/storage.py` | `list_storage_pools`, `list_pool_volumes`, `list_iso_images` | `/api/v1/storage` |
| **Networks** | `tools/networks.py` | `list_networks`, `list_bridges` | `/api/v1/networks` |
| **HA** | `tools/ha.py` | `list_ha_clusters`, `get_ha_cluster_state`, `get_ha_preflight` | `/api/v1/ha` |
| **Forensics** | `tools/forensics.py` | `get_placement_log`, `get_placement_preview`, `get_task_status`, `get_audit_events` | `/api/v1/placement`, `/api/v1/tasks`, `/api/v1/audit` |
