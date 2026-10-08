"""tools/ha.py — High Availability cluster inspection tools."""

from virtstack_client import client


async def list_ha_clusters() -> list:
    """
    List all HA clusters in the platform.
    Returns cluster name, member servers, and fencing configuration.
    """
    return await client.get("/api/v1/ha/clusters")


async def get_ha_cluster_state(host_id: str) -> dict:
    """
    Get live Pacemaker cluster state for a specific host.

    Args:
        host_id: Host UUID of any member node in the cluster

    Returns:
        Quorum status, offline nodes, fail counts, and resource state.
    """
    return await client.get(f"/api/v1/ha/cluster-status/{host_id}")


async def get_ha_preflight(host_id: str) -> dict:
    """
    Run HA preflight checks on a server before adding it to a cluster.

    Args:
        host_id: Host UUID to check

    Returns:
        Pass/fail status for each preflight requirement (corosync, fencing, etc.).
    """
    return await client.get(f"/api/v1/ha/preflight/{host_id}")
