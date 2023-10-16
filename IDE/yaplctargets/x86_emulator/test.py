import _ctypes
import ctypes
import os


if __name__ == '__main__':
	dll_dir = os.path.abspath(os.path.join("extra_files", "SoftPlc.dll"))
	CurrentPLCFilename = os.path.join("test")

	_PLClibraryHandle = _ctypes.LoadLibrary(dll_dir, False)

	PLClibraryHandle = ctypes.CDLL(CurrentPLCFilename, handle=_PLClibraryHandle)