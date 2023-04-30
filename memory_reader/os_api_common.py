import sys
import os

if sys.platform == "win32":
    from .os_api_windows import *
elif sys.platform == "darwin":
    from .os_api_mac import *
else:
    raise NotImplementedError("This code currently supports only Windows and macOS.")
