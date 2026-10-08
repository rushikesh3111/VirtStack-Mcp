# VirtStack Read-Only MCP Server

A standalone, strictly **read-only** Model Context Protocol (MCP) server that empowers AI agents and DevOps teams to safely inspect and diagnose **VirtStack** private cloud infrastructure.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-4.0+-brightgreen.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Highlights

- 🛡️ **Strictly Read-Only Guarantee:** Enforced at the client layer. Non-GET operations raise `ReadOnlyViolationError`. Mutating endpoints and shell access are excluded.
- ⚡ **27 Infrastructure Tools:** Comprehensive coverage across hosts, virtual machines, storage, networks, HA clusters, and forensic logs.
- 🔑 **Headless Auto-Login:** Configure username and password in `.env`. JWT tokens are acquired and kept in-memory with automatic refresh.
- 🌐 **Dual Interface Architecture:**
  - **FastMCP Server (`server.py`):** Universal transport supporting Streamable HTTP (`/mcp`), Server-Sent Events (`/sse`), and `stdio`.
  - **FastAPI Web App (`api.py`):** Interactive Swagger UI (`http://localhost:8080/docs`) for manual exploration.
- 🧩 **Zero Code Modifications:** Completely standalone — requires no changes to the VirtStack core codebase.

---

## Repository Structure

```text
VirtStack-Mcp/
├── server.py              # Universal FastMCP server (Streamable HTTP + SSE + stdio)
├── api.py                 # FastAPI application with Swagger documentation
├── virtstack_client.py    # Authenticated, read-only HTTP client
├── requirements.txt       # Dependencies
├── .env.example           # Configuration template
├── .gitignore             # Git ignore rules (.env protected)
├── docs/
│   ├── ARCHITECTURE.md    # System design & security architecture
│   └── TOOLS_REFERENCE.md # Complete reference of all 27 inspection tools
├── tests/
│   └── test_virtstack_client.py # Client and read-only test suite
└── tools/
    ├── system.py          # Control plane health, version, global search
    ├── hosts.py           # Hypervisors, resource usage, CPU capabilities
    ├── vms.py             # VM state, specs, snapshots, XML, dependents
    ├── storage.py         # Storage pools, volumes, ISO catalog
    ├── networks.py        # Virtual networks and Linux bridges
    ├── ha.py              # Pacemaker/Corosync clusters, preflight checks
    └── forensics.py       # Placement engine traces, audit logs, task status
```

---

## Quick Start

### 1. Installation
Clone the repository and install requirements:

```bash
git clone https://github.com/rushikesh3111/VirtStack-Mcp.git
cd VirtStack-Mcp
pip install -r requirements.txt
```

### 2. Configuration
Copy the template and configure your VirtStack endpoint and credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```ini
# VirtStack control plane endpoint (HTTPS supported, self-signed TLS handled)
VIRTSTACK_API_URL=https://10.0.33.16:3000

# VirtStack operator credentials
VIRTSTACK_USERNAME=admin@virtstack.local
VIRTSTACK_PASSWORD=VirtStack@2026!

# Server ports
MCP_HOST=0.0.0.0
MCP_PORT=8765
API_PORT=8080
```

### 3. Run the FastMCP Server (for AI Agents)
```bash
python server.py
```
- **Streamable HTTP Endpoint:** `http://<ip>:8765/mcp`
- **SSE Endpoint:** `http://<ip>:8765/sse`

To run in `stdio` mode (e.g. for Claude Desktop):
```bash
MCP_TRANSPORT=stdio python server.py
```

### 4. Run the FastAPI Web Interface (for Humans)
```bash
python api.py
```
- **Swagger Documentation:** `http://localhost:8080/docs`
- **ReDoc Documentation:** `http://localhost:8080/redoc`

---

## Tool Categories Overview

| Category | Tools | Capabilities |
| :--- | :--- | :--- |
| **System** | `get_health`, `get_server_info`, `global_search` | Inspect control plane status and query entities |
| **Hosts** | `list_hosts`, `get_host_detail`, `get_host_capabilities`, `get_host_metrics` | Hypervisor specs, CPU topology, resource load |
| **VMs** | `list_vms`, `list_host_vms`, `get_vm_detail`, `get_vm_metrics`, `get_vm_xml`, `get_vm_hardware`, `get_vm_dependents`, `list_vm_snapshots` | VM lifecycle state, metrics, XML, disks, snapshots |
| **Storage** | `list_storage_pools`, `list_pool_volumes`, `list_iso_images` | Storage capacities, volumes, ISO library |
| **Networks** | `list_networks`, `list_bridges` | Virtual networks, subnets, Linux bridges |
| **HA** | `list_ha_clusters`, `get_ha_cluster_state`, `get_ha_preflight` | Quorum verification, cluster health, preflight |
| **Forensics** | `get_placement_log`, `get_placement_preview`, `get_task_status`, `get_audit_events` | Scheduler decisions, audit trail, background tasks |

For complete tool documentation, see [TOOLS_REFERENCE.md](file:///home/rushi/VirtStack/VirtStack-Mcp/docs/TOOLS_REFERENCE.md).

---

## Testing

Run unit tests to verify read-only enforcement and client behavior:

```bash
pytest tests/ -v
```

---

## Security Model

- **Read-Only Enforcement:** Safe by construction. All mutating HTTP methods are disabled.
- **In-Memory Secrets:** Credentials and tokens are held only in process memory; never logged or saved to disk.
- **Network Isolation:** Does not open any external network connections outside the designated VirtStack API URL.
