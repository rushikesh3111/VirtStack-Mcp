# VirtStack Read-Only MCP Server

A **standalone, read-only** MCP (Model Context Protocol) server that lets AI agents (OpenWebUI, Claude Desktop) safely inspect VirtStack private cloud infrastructure.

- ✅ **28 read-only tools** — hosts, VMs, storage, networks, HA, forensics
- ✅ **Auto-login** — enter username/password in `.env`, tokens managed in memory
- ✅ **Zero VirtStack code changes** — fully standalone
- ✅ **Dual interface** — FastMCP for AI agents, FastAPI Swagger UI for humans

---

## Quick Start

### 1. Install dependencies

```bash
cd virtstack-read-mcp
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.example .env
# Edit .env with your VirtStack URL, username, and password
nano .env
```

Your `.env` should look like:
```
VIRTSTACK_API_URL=http://192.168.1.100:8000
VIRTSTACK_USERNAME=admin
VIRTSTACK_PASSWORD=your_password
```

### 3. Start the MCP server (for OpenWebUI)

```bash
python server.py
# MCP SSE endpoint: http://localhost:8765/sse
```

### 4. Start the web API (for browser/Swagger testing)

```bash
python api.py
# Swagger UI: http://localhost:8080/docs
```

---

## OpenWebUI Integration

In OpenWebUI → **Settings → Tools → MCP Servers**, add:

| Field | Value |
|-------|-------|
| Name  | VirtStack |
| URL   | `http://localhost:8765/sse` |

That's it — all 28 tools will appear automatically.

---

## Claude Desktop Integration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "virtstack": {
      "command": "python",
      "args": ["/path/to/virtstack-read-mcp/server.py"],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

---

## Available Tools (28 total)

| Category | Tools |
|----------|-------|
| **System** | `get_health`, `get_server_info`, `global_search` |
| **Hosts** | `list_hosts`, `get_host_detail`, `get_host_capabilities`, `get_host_metrics` |
| **VMs** | `list_vms`, `list_host_vms`, `get_vm_detail`, `get_vm_metrics`, `get_vm_xml`, `get_vm_hardware`, `get_vm_dependents`, `list_vm_snapshots` |
| **Storage** | `list_storage_pools`, `list_pool_volumes`, `list_iso_images` |
| **Networks** | `list_networks`, `list_bridges` |
| **HA** | `list_ha_clusters`, `get_ha_cluster_state`, `get_ha_preflight` |
| **Forensics** | `get_placement_log`, `get_placement_preview`, `get_task_status`, `get_audit_events` |

---

## Run Tests

```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

---

## Safety

- **Only GET requests** — `POST`, `PUT`, `PATCH`, `DELETE` raise `ReadOnlyViolationError`
- **No terminal/shell** — `/api/v1/shell` is completely excluded
- **Token in memory only** — credentials never written to disk beyond `.env`
- **VirtStack code untouched** — this is a completely separate program
