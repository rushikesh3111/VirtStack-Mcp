# VirtStack-Mcp Tool Reference (27 Read-Only Tools)

This document provides the complete specification of all 27 read-only inspection tools provided by the **VirtStack-Mcp** server.

---

## 1. System & Discovery Tools (`tools/system.py`)

### `get_health()`
- **Description:** Returns the overall health and status of the VirtStack control plane and subsystems.
- **Parameters:** None
- **API Endpoint:** `GET /api/v1/system/health`

### `get_server_info()`
- **Description:** Retrieves VirtStack server version, runtime environment, and build metadata.
- **Parameters:** None
- **API Endpoint:** `GET /api/v1/system/info`

### `global_search(query: str, limit: int = 20)`
- **Description:** Performs a cross-entity search for VMs, hosts, pools, or networks matching a query string (name, IP, MAC).
- **Parameters:**
  - `query` (str): Search term.
  - `limit` (int, default 20): Maximum number of search results.
- **API Endpoint:** `GET /api/v1/search?q={query}&limit={limit}`

---

## 2. Host & Hypervisor Tools (`tools/hosts.py`)

### `list_hosts()`
- **Description:** Lists all hypervisor hosts in the VirtStack cluster, including state, OS, CPU cores, and total RAM.
- **Parameters:** None
- **API Endpoint:** `GET /api/v1/hosts`

### `get_host_detail(host_id: str)`
- **Description:** Retrieves detailed host information including CPU topology, memory layout, and libvirt URI.
- **Parameters:**
  - `host_id` (str): Unique host identifier.
- **API Endpoint:** `GET /api/v1/hosts/{host_id}`

### `get_host_capabilities(host_id: str)`
- **Description:** Inspects virtualization capabilities, supported CPU models, and KVM features of a host.
- **Parameters:**
  - `host_id` (str): Unique host identifier.
- **API Endpoint:** `GET /api/v1/hosts/{host_id}/capabilities`

### `get_host_metrics(host_id: str)`
- **Description:** Fetches current CPU utilization, memory pressure, and performance counters for a host.
- **Parameters:**
  - `host_id` (str): Unique host identifier.
- **API Endpoint:** `GET /api/v1/hosts/{host_id}/metrics`

---

## 3. Virtual Machine Tools (`tools/vms.py`)

### `list_vms()`
- **Description:** Lists all virtual machines across the entire cluster with status, vCPU, and memory.
- **Parameters:** None
- **API Endpoint:** `GET /api/v1/vms`

### `list_host_vms(host_id: str)`
- **Description:** Lists all virtual machines hosted on a specific hypervisor host.
- **Parameters:**
  - `host_id` (str): Unique host identifier.
- **API Endpoint:** `GET /api/v1/hosts/{host_id}/vms`

### `get_vm_detail(vm_id: str)`
- **Description:** Retrieves complete metadata, current power state, IP addresses, and configuration for a VM.
- **Parameters:**
  - `vm_id` (str): Unique VM identifier.
- **API Endpoint:** `GET /api/v1/vms/{vm_id}`

### `get_vm_metrics(vm_id: str)`
- **Description:** Fetches real-time CPU, RAM, disk I/O, and network throughput metrics for a VM.
- **Parameters:**
  - `vm_id` (str): Unique VM identifier.
- **API Endpoint:** `GET /api/v1/vms/{vm_id}/metrics`

### `get_vm_xml(vm_id: str)`
- **Description:** Retrieves the raw libvirt XML domain definition for configuration inspection.
- **Parameters:**
  - `vm_id` (str): Unique VM identifier.
- **API Endpoint:** `GET /api/v1/vms/{vm_id}/xml`

### `get_vm_hardware(vm_id: str)`
- **Description:** Details assigned virtual hardware devices (vCPUs, memory, disk controllers, NICs).
- **Parameters:**
  - `vm_id` (str): Unique VM identifier.
- **API Endpoint:** `GET /api/v1/vms/{vm_id}/hardware`

### `get_vm_dependents(vm_id: str)`
- **Description:** Lists dependencies, snapshots, attached disks, and storage volumes tied to a VM.
- **Parameters:**
  - `vm_id` (str): Unique VM identifier.
- **API Endpoint:** `GET /api/v1/vms/{vm_id}/dependents`

### `list_vm_snapshots(vm_id: str)`
- **Description:** Lists all point-in-time snapshots created for a virtual machine.
- **Parameters:**
  - `vm_id` (str): Unique VM identifier.
- **API Endpoint:** `GET /api/v1/vms/{vm_id}/snapshots`

---

## 4. Storage Tools (`tools/storage.py`)

### `list_storage_pools()`
- **Description:** Lists all configured storage pools (dir, LVM, NFS, Ceph) with capacity and free space.
- **Parameters:** None
- **API Endpoint:** `GET /api/v1/storage/pools`

### `list_pool_volumes(pool_id: str)`
- **Description:** Lists individual disk volumes stored within a specific storage pool.
- **Parameters:**
  - `pool_id` (str): Storage pool identifier.
- **API Endpoint:** `GET /api/v1/storage/pools/{pool_id}/volumes`

### `list_iso_images()`
- **Description:** Lists all installation ISO images available in the VirtStack storage library.
- **Parameters:** None
- **API Endpoint:** `GET /api/v1/storage/isos`

---

## 5. Network Tools (`tools/networks.py`)

### `list_networks()`
- **Description:** Lists all virtual networks, bridge assignments, VLANs, and IP subnets.
- **Parameters:** None
- **API Endpoint:** `GET /api/v1/networks`

### `list_bridges(host_id: str = "")`
- **Description:** Lists physical and virtual Linux bridge interfaces across cluster hosts.
- **Parameters:**
  - `host_id` (str, optional): Target host identifier.
- **API Endpoint:** `GET /api/v1/networks/bridges`

---

## 6. High Availability (HA) Tools (`tools/ha.py`)

### `list_ha_clusters()`
- **Description:** Lists configured HA clusters and member nodes.
- **Parameters:** None
- **API Endpoint:** `GET /api/v1/ha/clusters`

### `get_ha_cluster_state(cluster_id: str)`
- **Description:** Retrieves real-time cluster health, quorum status, Pacemaker/Corosync state, and active fencing devices.
- **Parameters:**
  - `cluster_id` (str): HA cluster identifier.
- **API Endpoint:** `GET /api/v1/ha/clusters/{cluster_id}/state`

### `get_ha_preflight(cluster_id: str)`
- **Description:** Runs non-intrusive preflight checks for failover readiness, network splits, and quorum stability.
- **Parameters:**
  - `cluster_id` (str): HA cluster identifier.
- **API Endpoint:** `GET /api/v1/ha/clusters/{cluster_id}/preflight`

---

## 7. Forensics & Audit Tools (`tools/forensics.py`)

### `get_placement_log(limit: int = 50)`
- **Description:** Retrieves historical VM placement scheduler logs and decision traces.
- **Parameters:**
  - `limit` (int, default 50): Maximum entries to return.
- **API Endpoint:** `GET /api/v1/placement/log?limit={limit}`

### `get_placement_preview(vm_id: str)`
- **Description:** Simulates placement evaluation to see which host the scheduler would recommend without executing migration.
- **Parameters:**
  - `vm_id` (str): VM identifier to evaluate.
- **API Endpoint:** `GET /api/v1/placement/preview/{vm_id}`

### `get_task_status(task_id: str)`
- **Description:** Fetches progress, state, and error logs for an asynchronous VirtStack background task.
- **Parameters:**
  - `task_id` (str): Background task identifier.
- **API Endpoint:** `GET /api/v1/tasks/{task_id}`

### `get_audit_events(limit: int = 50)`
- **Description:** Retrieves security and operational audit logs for root-cause analysis and forensics.
- **Parameters:**
  - `limit` (int, default 50): Maximum entries to return.
- **API Endpoint:** `GET /api/v1/audit/events?limit={limit}`
