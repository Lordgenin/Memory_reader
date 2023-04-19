import ctypes
from ctypes.util import find_library
import sys

# Check if the current OS is Windows
if sys.platform == "win32":
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

else:
    # raise NotImplementedError("This code currently supports only Windows.")

    # Check if the current OS is macOS
    if sys.platform == "darwin":
        libc = ctypes.CDLL("libc.dylib")

        # Define task_t type
        task_t = ctypes.c_uint

        # Define vm_map_t type
        vm_map_t = ctypes.c_uint

        # Load the macOS libraries
        libsystem = ctypes.CDLL(find_library("System"))
        libproc = ctypes.CDLL(find_library("libproc"))

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


        # Structure: VM_REGION_BASIC_INFO_64
        class VM_REGION_BASIC_INFO_64(ctypes.Structure):
            _fields_ = [
                ("protection", ctypes.c_uint),
                ("max_protection", ctypes.c_uint),
                ("inheritance", ctypes.c_uint),
                ("shared", ctypes.c_uint, 1),
                ("reserved", ctypes.c_uint, 1),
                ("offset", ctypes.c_ulonglong),
                ("behavior", ctypes.c_uint),
                ("user_wired_count", ctypes.c_ushort),
                ("user_tag", ctypes.c_ushort),
                ("pages_resident", ctypes.c_uint),
                ("pages_shared_now_private", ctypes.c_uint),
                ("pages_swapped_out", ctypes.c_uint),
                ("pages_dirtied", ctypes.c_uint),
                ("ref_count", ctypes.c_uint),
                ("shadow_depth", ctypes.c_uint),
                ("external_pager", ctypes.c_uint, 1),
                ("share_mode", ctypes.c_uint, 2),
                ("is_submap", ctypes.c_uint, 1),
                ("object_id", ctypes.c_ulonglong),
            ]


        # Function: task_for_pid
        kern_return_t = ctypes.c_int
        task_port_t = ctypes.c_uint
        mach_port_name_t = ctypes.c_uint
        pid_t = ctypes.c_int

        task_for_pid = libsystem.task_for_pid
        task_for_pid.argtypes = [mach_port_name_t, pid_t, ctypes.POINTER(task_port_t)]
        task_for_pid.restype = kern_return_t
        #Second info given unsure was to what is does exactly but will test shortly


        # Define the necessary function signatures
        task_for_pid = libc.task_for_pid
        task_for_pid.argtypes = [task_t, ctypes.c_int, ctypes.POINTER(task_t)]
        task_for_pid.restype = ctypes.c_int

        vm_read = libc.vm_read
        vm_read.argtypes = [task_t, ctypes.c_ulonglong, ctypes.c_ulonglong, ctypes.POINTER(ctypes.POINTER(ctypes.c_byte)),
                            ctypes.POINTER(ctypes.c_ulonglong)]
        vm_read.restype = ctypes.c_int

        vm_region_recurse_64 = libc.vm_region_recurse_64
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
        mach_task_self.restype = mach_port_name_t

        mach_error = libc.mach_error
        mach_error.argtypes = [ctypes.c_char_p, ctypes.c_int]
        mach_error.restype = None

        # Type: mach_msg_type_number_t
        mach_msg_type_number_t = ctypes.c_uint

        def open_process(pid):
            task = task_t()
            result = task_for_pid(task_t(0), pid, ctypes.byref(task))
            if result != 0:
                mach_error(ctypes.create_string_buffer(b"task_for_pid"), result)
                raise OSError("Failed to open process.")
            return task


        def read_process_memory(task, address, size):
            data = ctypes.POINTER(ctypes.c_byte)()
            data_count = ctypes.c_ulonglong()
            result = vm_read(task, address, size, ctypes.byref(data), ctypes.byref(data_count))
            if result != 0:
                mach_error(ctypes.create_string_buffer(b"vm_read"), result)
                raise OSError("Failed to read process memory.")

            buffer = bytearray(data_count.value)
            ctypes.memmove(buffer, data, data_count.value)
            return buffer


        def close_handle(handle):
            pass  # No need to close the handle on macOS

'''
It imports the os_api module to use the open_process, read_process_memory, and close_handle functions.
In the read_memory function, it uses the os_api.open_process function to get a handle to the target process, 
reads memory using the os_api.read_process_memory function, 
and then closes the handle using the os_api.close_handle function.
'''