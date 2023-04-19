from .os_api import open_process, read_process_memory, close_handle
from .os_api import task_for_pid, mach_task_self, vm_region_recurse_64, VM_REGION_BASIC_INFO_64, mach_msg_type_number_t, VM_PROT_READ
import ctypes
import sys

class MemoryRegion:
    def __init__(self, base_address, size, protection):
        self.base_address = base_address
        self.size = size
        self.protection = protection

    def __repr__(self):
        return f"<MemoryRegion base_address={hex(self.base_address)}, size={self.size}, protection={self.protection}>"

def get_memory_regions(pid):
    # This function should be implemented for each platform separately
    # Here's an example for the Windows platform:
    return get_memory_regions_windows(pid)

def list_memory_regions(pid):

    # Check the platform and call the appropriate function
    if sys.platform == "win32":
        return get_memory_regions_windows(pid)
    elif sys.platform == "darwin":
        return get_memory_regions_mac(pid)
    elif sys.platform.startswith("linux"):
        return get_memory_regions_linux(pid)
    else:
        raise NotImplementedError("Listing memory regions is not implemented for this platform.")

    # This function should be implemented for each platform separately
    # using the platform-specific APIs to list the memory regions of a process
    # For example, on Windows, you can use VirtualQueryEx

def get_memory_regions_windows(pid):
    # ... existing Windows implementation ...
    pass

def get_memory_regions_mac(pid):

    # Get the task for the target process
    target_task = ctypes.c_uint32()
    ret = task_for_pid(mach_task_self(), pid, ctypes.byref(target_task))

    if ret != 0:
        raise RuntimeError(f"Failed to get task for PID {pid}")

    # Initialize variables for vm_region_recurse_64
    address = 0
    size = 0
    info = VM_REGION_BASIC_INFO_64()
    count = mach_msg_type_number_t(ctypes.sizeof(info) // ctypes.sizeof(ctypes.c_int))

    memory_regions = []

    while True:
        # Call vm_region_recurse_64 to get the memory region information
        ret = vm_region_recurse_64(target_task, ctypes.byref(ctypes.c_ulong(address)), ctypes.byref(ctypes.c_ulong(size)), 0, ctypes.byref(info), ctypes.byref(count))

        # Break the loop if vm_region_recurse_64 returns an error
        if ret != 0:
            break

        # Check if the memory region has read permissions
        if info.protection & VM_PROT_READ:
            memory_regions.append(MemoryRegion(address, size, info.protection))

        # Update the address for the next iteration
        address += size

    return memory_regions

def get_memory_regions_linux(pid):
    # ... Linux implementation ...
    pass

def read_memory(pid, base_address, size):
    process_handle = open_process(pid)
    try:
        return read_process_memory(process_handle, base_address, size)
    finally:
        close_handle(process_handle)

def read_memory_region(pid, memory_region):
    process_handle = open_process(pid)
    try:
        memory_data = read_process_memory(process_handle, memory_region.base_address, memory_region.size)
    finally:
        close_handle(process_handle)

    return memory_data

def get_memory_regions_windows(pid):
    import ctypes
    import os_api

    MEM_COMMIT = 0x1000
    MEM_FREE = 0x10000
    PAGE_READWRITE = 0x04
    PAGE_READONLY = 0x02

    process_handle = os_api.open_process(pid)
    if not process_handle:
        raise RuntimeError(f"Failed to open process with PID {pid}")

    memory_regions = []
    base_address = 0
    memory_basic_information = os_api.MEMORY_BASIC_INFORMATION()

    while True:
        result = os_api.kernel32.VirtualQueryEx(
            process_handle,
            ctypes.c_void_p(base_address),
            ctypes.byref(memory_basic_information),
            ctypes.sizeof(memory_basic_information),
        )

        if result == 0:
            break

        if (
            memory_basic_information.State == MEM_COMMIT
            and (memory_basic_information.Protect == PAGE_READONLY or memory_basic_information.Protect == PAGE_READWRITE)
        ):
            memory_regions.append(
                MemoryRegion(
                    memory_basic_information.BaseAddress,
                    memory_basic_information.RegionSize,
                    memory_basic_information.Protect,
                )
            )

        base_address += memory_basic_information.RegionSize

    os_api.close_handle(process_handle)

    return memory_regions
