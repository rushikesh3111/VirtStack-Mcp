"""tools/forensics.py — Audit, placement, and task debugging tools."""

from virtstack_client import client


async def get_placement_log(limit: int = 20) -> list:
    """
    Get the VM placement decision log from the scheduler.
    Shows why a host was chosen and why others were rejected.

    Args:
        limit: Number of log entries to return (default: 20, max: 500)

    Returns:
        List of placement decisions with scores, reasons, and timestamps.
    """
    return await client.get("/api/v1/placement/log", params={"limit": limit})


async def get_placement_preview(vm_id: str) -> dict:
    """
    Simulate which host would be chosen for a VM right now.
    Shows current resource scores without actually migrating.

    Args:
        vm_id: VM UUID (from list_vms)

    Returns:
        Ranked host list with scores and available resources.
    """
    return await client.get(f"/api/v1/vms/{vm_id}/placement-preview")


async def get_task_status(task_id: str) -> dict:
    """
    Get the current status and error details of a background task.

    Args:
        task_id: Task UUID (returned by any write operation or visible in audit logs)

    Returns:
        Task state (pending/running/done/failed), progress %, and error message if failed.
    """
    return await client.get(f"/api/v1/tasks/{task_id}")


async def get_audit_events(limit: int = 50) -> list:
    """
    Get recent audit log entries showing who changed what in the platform.
    Covers actions like snapshot flatten, VM resize, live migration, etc.

    Args:
        limit: Number of audit entries to return (default: 50, max: 100)

    Returns:
        List of audit records with user, action, resource, and timestamp.
    """
    return await client.get("/api/v1/audit-logs", params={"limit": limit})
