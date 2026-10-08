"""tools/hosts.py — Physical server monitoring tools."""

from virtstack_client import client


async def list_hosts() -> list:
    """
    List all physical servers registered in VirtStack.
    Returns hostname, online/offline status, and agent version for each host.
    """
    return await client.get("/api/v1/hosts")


async def get_host_detail(host_id: str) -> dict:
    """
    Get detailed info about one physical server.

    Args:
        host_id: Host UUID (from list_hosts)

    Returns:
        OS version, agent status, IP address, last heartbeat timestamp.
    """
    return await client.get(f"/api/v1/hosts/{host_id}")


async def get_host_capabilities(host_id: str) -> dict:
    """
    Get hardware capabilities of a physical server.

    Args:
        host_id: Host UUID (from list_hosts)

    Returns:
        CPU model, core count, thread count, RAM per NUMA cell.
    """
    return await client.get(f"/api/v1/hosts/{host_id}/capabilities")


async def get_host_metrics(host_id: str) -> dict:
    """
    Get live CPU, RAM, disk, and network metrics for a physical server.

    Args:
        host_id: Host UUID (from list_hosts)

    Returns:
        Current CPU %, RAM usage in MB, disk I/O speed, network throughput.
    """
    return await client.get(f"/api/v1/hosts/{host_id}/metrics")
