import ctypes
from ctypes import wintypes

# Define the necessary constants and function signatures
PROCESS_VM_READ = 0x0010

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

kernel32.OpenProcess.argtypes = [
    wintypes.DWORD, wintypes.BOOL, wintypes.DWORD
]
kernel32.OpenProcess.restype = wintypes.HANDLE

kernel32.ReadProcessMemory.argtypes = [
    wintypes.HANDLE, wintypes.LPVOID, wintypes.LPVOID, wintypes.SIZE_T, wintypes.LPVOID
]
kernel32.ReadProcessMemory.restype = wintypes.BOOL

kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", ctypes.c_uint32),
        ("RegionSize", ctypes.c_size_t),
        ("State", ctypes.c_uint32),
        ("Protect", ctypes.c_uint32),
        ("Type", ctypes.c_uint32),
    ]

def open_process(pid):
    return kernel32.OpenProcess(PROCESS_VM_READ, False, pid)

def read_process_memory(process_handle, base_address, size):
    buffer = ctypes.create_string_buffer(size)
    bytes_read = wintypes.SIZE_T()

    if not kernel32.ReadProcessMemory(process_handle, base_address, buffer, size, ctypes.byref(bytes_read)):
        raise ctypes.WinError(ctypes.get_last_error())

    return buffer.raw[:bytes_read.value]

def close_handle(handle):
    kernel32.CloseHandle(handle)
