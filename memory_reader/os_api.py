import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.platform == "win32":
    from .os_api_windows import open_process, read_process_memory, close_handle
elif sys.platform == "darwin":
    from .os_api_mac import open_process, read_process_memory, close_handle
else:
    raise NotImplementedError("This code currently supports only Windows and macOS.")
