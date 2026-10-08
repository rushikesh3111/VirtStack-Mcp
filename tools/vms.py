"""tools/vms.py — Virtual machine inspection tools."""

from virtstack_client import client


async def list_vms() -> list:
    """
    List all virtual machines across the entire platform.
    Returns VM name, state (running/stopped), host, vCPUs, and RAM.
    """
    return await client.get("/api/v1/vms")


async def list_host_vms(host_id: str) -> list:
    """
    List all VMs running on a specific physical host. Useful for noisy neighbor detection.

    Args:
        host_id: Host UUID (from list_hosts)

    Returns:
        All VMs on that host with their resource usage.
    """
    return await client.get(f"/api/v1/hosts/{host_id}/vms")


async def get_vm_detail(vm_id: str) -> dict:
    """
    Get full details of a virtual machine.

    Args:
        vm_id: VM UUID (from list_vms)

    Returns:
        vCPUs, RAM, IP address, disk list, state, host, and network interfaces.
    """
    return await client.get(f"/api/v1/vms/{vm_id}")


async def get_vm_metrics(host_id: str, vm_id: str) -> dict:
    """
    Get real-time CPU, RAM, disk IOPS, and network metrics for a VM.

    Args:
        host_id: Host UUID where the VM is running
        vm_id: VM UUID

    Returns:
        Live CPU %, memory usage, disk read/write speed, network rx/tx.
    """
    return await client.get(f"/api/v1/hosts/{host_id}/vms/{vm_id}/metrics")


async def get_vm_xml(vm_id: str) -> str:
    """
    Get the raw KVM/Libvirt XML definition of a virtual machine.
    Useful for deep hypervisor debugging and configuration inspection.

    Args:
        vm_id: VM UUID (from list_vms)

    Returns:
        Raw XML string of the Libvirt domain definition.
    """
    return await client.get(f"/api/v1/vms/{vm_id}/xml")


async def get_vm_hardware(vm_id: str) -> dict:
    """
    Get the emulated hardware configuration of a virtual machine.

    Args:
        vm_id: VM UUID (from list_vms)

    Returns:
        Emulated devices: TPM 2.0, virtio drivers, watchdog, BIOS type, etc.
    """
    return await client.get(f"/api/v1/vms/{vm_id}/hardware")


async def get_vm_dependents(vm_id: str) -> dict:
    """
    Get all child clones and linked VMs that depend on this VM's disk.

    Args:
        vm_id: VM UUID (from list_vms)

    Returns:
        List of dependent clones linked to this base image.
    """
    return await client.get(f"/api/v1/vms/{vm_id}/dependents")


async def list_vm_snapshots(vm_id: str) -> list:
    """
    List all saved snapshots for a virtual machine.

    Args:
        vm_id: VM UUID (from list_vms)

    Returns:
        Snapshot names, creation dates, and restore point info.
    """
    return await client.get(f"/api/v1/vms/{vm_id}/snapshots")
