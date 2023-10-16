'''from ctypes import c_uint8 as BYTE
from ctypes import c_uint16 as WORD
from ctypes import c_uint32 as DWORD
from ctypes import c_uint8 as BOOL
from ctypes import c_float as REAL'''

import ctypes

class BYTE(ctypes.Structure):
	_fields_ = [("value", ctypes.c_uint8), ("flags", ctypes.c_uint8)]

class WORD(ctypes.Structure):
	_fields_ = [("value", ctypes.c_uint16), ("flags", ctypes.c_uint8)]

class DWORD(ctypes.Structure):
	_fields_ = [("value", ctypes.c_uint32), ("flags", ctypes.c_uint8)]

class BOOL(ctypes.Structure):
	_fields_ = [("value", ctypes.c_uint8), ("flags", ctypes.c_uint8)]

class REAL(ctypes.Structure):
	_fields_ = [("value", ctypes.c_float), ("flags", ctypes.c_uint8)]

class DISTATUS(ctypes.Structure):
	_fields_ = [('EN', BOOL),
				('ENO', BOOL),
				('DIN', BYTE),
				('OM', BYTE),
				('OK', BYTE)]

class DIVAL(ctypes.Structure):
	_fields_ = [('EN', BOOL),
				('ENO', BOOL),
				('EX', BOOL),
				('DIN', BYTE),
				('OV', BOOL),
				('OK', BYTE)]

class DICNTT(ctypes.Structure):
	_fields_ = [('EN', BOOL),
				('ENO', BOOL),
				('EX', BOOL),
				('DIN', BYTE),
				('OV', WORD),
				('OISSET', BOOL),
				('OK', BYTE)]

class DISTATECFGCNTT(ctypes.Structure):
	_fields_ = [("EN", BOOL),
				("ENO", BOOL),
				('DIN', BYTE),
				('OSP', WORD),
				('OENCMPMD', BOOL),
				('OK', BYTE)]

class DICNT(ctypes.Structure):
	_fields_ = [('EN', BOOL),
				('ENO', BOOL),
				('EX', BOOL),
				('DIN', BYTE),
				('OV', DWORD),
				('OISSET', BOOL),
				('OK', BYTE)]

class DISTATECFGCNT(ctypes.Structure):
	_fields_ = [("EN", BOOL),
				("ENO", BOOL),
				("DIN", BYTE),
				("OSP", DWORD),
				("OENCMPMD", BOOL),
				("OK", BYTE)]

class DIENC(ctypes.Structure):
	_fields_ = [("EN", BOOL),
				("ENO", BOOL),
				("EX", BOOL),
				("DIN", BYTE),
				("OVA", DWORD),
				("OISSETA", BOOL),
				("OVB", DWORD),
				("OISSETB", BOOL),
				("OVT", WORD),
				("OISSETT", BOOL),
				("OK", BYTE)]

class DISTATECFGENC(ctypes.Structure):
	_fields_ = [("EN", BOOL),
				("ENO", BOOL),
				("DIN", BYTE),
				("OSPA", DWORD),
				("OENCMPMDA", BOOL),
				("OSPB", DWORD),
				("OENCMPMDB", BOOL),
				("OSPT", WORD),
				("OENCMPMDT", BOOL),
				("SPMULTIPLIER", BYTE),
				("OK", BYTE)]

class AISTATUS(ctypes.Structure):
	_fields_ = [("EN", BOOL),
				("ENO", BOOL),
				("AIN", BYTE),
				("OM", BYTE),
				("OS", BYTE),
				("OK", BYTE)]

class AIVAL(ctypes.Structure):
	_fields_ = [("EN", BOOL),
				("ENO", BOOL),
				("EX", BOOL),
				("AIN", BYTE),
				("OV", REAL),
				("OK", BYTE)]

class PTSTATUS(ctypes.Structure):
	_fields_ = [("EN", BOOL),
				("ENO", BOOL),
				("PTN", BYTE),
				("OM", BYTE),
				("OS", BYTE),
				("OK", BYTE)]

class PTVAL(ctypes.Structure):
	_fields_ = [("EN", BOOL),
				("ENO", BOOL),
				("EX", BOOL),
				("PTN", BYTE),
				("OV", REAL),
				("OK", BYTE)]

class DTSTATUS(ctypes.Structure):
	_fields_ = [("EN", BOOL),
				("ENO", BOOL),
				("DTN", BYTE),
				("OM", BYTE),
				("OS", BYTE),
				("OK", BYTE)]

class DTVAL(ctypes.Structure):
	_fields_ = [("EN", BOOL),
				("ENO", BOOL),
				("EX", BOOL),
				("DTN", BYTE),
				("OV", REAL),
				("OK", BYTE)]

class DOSTATUS(ctypes.Structure):
	_fields_ = [("EN", BOOL),
				("ENO", BOOL),
				("DON", BYTE),
				("OM", BYTE),
				("OEPWM", BOOL),
				("OTPWM", DWORD),
				("ODPWM", REAL),
				("OESF", BOOL),
				("OVSF", BOOL),
				("OK", BYTE)]

class AOSTATUS(ctypes.Structure):
	_fields_ = [("EN", BOOL),
				("ENO", BOOL),
				("AON", BYTE),
				("OM", BYTE),
				("OESF", BOOL),
				("OVSF", REAL),
				("OK", BYTE)]

class SoftPLC_IRQ(ctypes.Structure):
	_fields_ = [("TaskDI_IRQ", ctypes.CFUNCTYPE(ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint32)),
				("TaskAI_IRQ", ctypes.CFUNCTYPE(ctypes.c_uint8, ctypes.c_uint8, ctypes.c_float)),
				("TaskPT_IRQ", ctypes.CFUNCTYPE(ctypes.c_uint8, ctypes.c_uint8, ctypes.c_float)),
				("TaskDT_IRQ", ctypes.CFUNCTYPE(ctypes.c_uint8, ctypes.c_uint8, ctypes.c_float)),
				("GetDO_Value", ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_uint8, ctypes.c_uint8)),
				("GetAO_Value", ctypes.CFUNCTYPE(ctypes.c_float, ctypes.c_uint8, ctypes.c_uint8))]

class LOG_MBRTU_T(ctypes.Structure):
	_fields_ = [("msg_time", ctypes.c_uint64),
				("isTx", ctypes.c_uint8),
				("mbrtu_msg", ctypes.POINTER(ctypes.c_uint8)),
				("m_msg_sz", ctypes.c_uint32),
				("service_msg", ctypes.c_char_p),
				("s_msg_sz", ctypes.c_uint32)]