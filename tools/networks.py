"""tools/networks.py — Network and bridge inspection tools."""

from virtstack_client import client


async def list_networks() -> list:
    """
    List all virtual networks defined in the platform.
    Returns network name, subnet, DHCP status, and bridge interface.
    """
    return await client.get("/api/v1/networks")


async def list_bridges(host_id: str) -> list:
    """
    List all physical network bridges on a specific host.

    Args:
        host_id: Host UUID (from list_hosts)

    Returns:
        Bridge name, attached physical interface, MTU, and IP address.
    """
    return await client.get(f"/api/v1/hosts/{host_id}/inventory/bridges")
