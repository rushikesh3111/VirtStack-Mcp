"""tools/storage.py — Storage pool and volume inspection tools."""

from virtstack_client import client


async def list_storage_pools() -> list:
    """
    List all storage pools across the platform.
    Returns pool name, total size, free space, and type (dir, lvm, zfs, etc.).
    """
    return await client.get("/api/v1/storage-pools")


async def list_pool_volumes(host_id: str, pool_name: str) -> list:
    """
    List all virtual disk volumes inside a storage pool.

    Args:
        host_id: Host UUID where the pool lives
        pool_name: Name of the storage pool (e.g. "default", "fast-ssd")

    Returns:
        Volume filenames, sizes, formats (qcow2/raw), and allocation.
    """
    return await client.get(
        f"/api/v1/hosts/{host_id}/storage-pools/{pool_name}/volumes"
    )


async def list_iso_images() -> list:
    """
    List all ISO images available in the ISO library.
    Returns ISO filename, size, and upload date.
    """
    return await client.get("/api/v1/storage/isos")
