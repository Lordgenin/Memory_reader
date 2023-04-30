import ctypes
from ctypes.util import find_library

# Load the macOS libraries
libsystem = ctypes.CDLL(find_library("System"))
libproc = ctypes.CDLL(find_library("libproc"))

# Define task_t and vm_map_t types
task_t = ctypes.c_uint
vm_map_t = ctypes.c_uint

# Constants: VM_PROT_READ
VM_PROT_READ = 0x01

# Define vm_region_basic_info_data_t struct
class VMRegionBasicInfoData64(ctypes.Structure):
    _fields_ = [
        ("protection", ctypes.c_uint),
        ("max_protection", ctypes.c_uint),
        ("inheritance", ctypes.c_uint),
        ("shared", ctypes.c_uint, 1),
        ("reserved", ctypes.c_uint, 1),
        ("offset", ctypes.c_ulonglong),
        ("behavior", ctypes.c_uint),
        ("user_wired_count", ctypes.c_ushort),
        ("reserved2", ctypes.c_ushort)
    ]

# Define the necessary function signatures
task_for_pid = libsystem.task_for_pid
task_for_pid.argtypes = [task_t, ctypes.c_int, ctypes.POINTER(task_t)]
task_for_pid.restype = ctypes.c_int

vm_read = libsystem.vm_read
vm_read.argtypes = [task_t, ctypes.c_ulonglong, ctypes.c_ulonglong, ctypes.POINTER(ctypes.POINTER(ctypes.c_byte)),
                    ctypes.POINTER(ctypes.c_ulonglong)]
vm_read.restype = ctypes.c_int

vm_region_recurse_64 = libsystem.vm_region_recurse_64
vm_region_recurse_64.argtypes = [
    task_t,
    ctypes.POINTER(ctypes.c_ulonglong),
    ctypes.POINTER(ctypes.c_ulonglong),
    ctypes.c_uint,
    ctypes.POINTER(VMRegionBasicInfoData64),
    ctypes.POINTER(ctypes.c_uint),
    ctypes.POINTER(ctypes.c_uint),
]
vm_region_recurse_64.restype = ctypes.c_int

# Function: mach_task_self
mach_task_self = libsystem.mach_task_self
mach_task_self.argtypes = []
mach_task_self.restype = task_t

# Type: mach_msg_type_number_t
mach_msg_type_number_t = ctypes.c_uint

def open_process(pid):
    task = task_t()
    result = task_for_pid(task_t(0), pid, ctypes.byref(task))
    if result != 0:
        raise OSError("Failed to open process.")
    return task

def read_process_memory(task, address, size):
    data = ctypes.POINTER(ctypes.c_byte)()
    data_count = ctypes.c_ulonglong()
    result = vm_read(task, address, size, ctypes.byref(data), ctypes.byref(data_count))
    if result != 0:
        raise OSError("Failed to read process memory.")

    buffer = bytearray(data_count.value)
    ctypes.memmove(buffer, data, data_count.value)
    return buffer

def close_handle(handle):
    pass  # No need to close the handle on macOS