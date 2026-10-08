"""tools/system.py — Health check and global search tools."""

from virtstack_client import client


async def get_health() -> dict:
    """
    Check if the VirtStack control plane is online.
    Returns platform status and connected agent count.
    """
    return await client.get("/api/v1/health")


async def get_server_info() -> dict:
    """
    Get VirtStack server configuration info.
    Returns API URL, ports, and TLS certificate fingerprint.
    """
    return await client.get("/api/v1/server-info")


async def global_search(query: str) -> dict:
    """
    Search for any VM, host, IP address, or disk across the entire platform.

    Args:
        query: Search term (e.g. hostname, IP address, VM name, disk name)

    Returns:
        Matching VMs, hosts, networks, and storage volumes.
    """
    return await client.get("/api/v1/search", params={"q": query})
