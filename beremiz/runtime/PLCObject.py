#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Beremiz runtime.
#
# Copyright (C) 2007: Edouard TISSERANT and Laurent BESSARD
#
# See COPYING.Runtime file for copyrights details.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

from threading import Timer, Thread, Lock, Semaphore, Event
import ctypes
import shutil
import os
import io
import subprocess
#import types
import sys
import traceback
from targets.typemapping import LogLevelsDefault, LogLevelsCount, TypeTranslator, UnpackDebugBuffer
from time import time
from time import strftime
from time import localtime
import Pyro4
import base64
from .FB_types import *

import pathlib

DEBUG = True

if os.name in ("nt", "ce"):
    #from _ctypes import LoadLibrary as dlopen
    import _ctypes
    from _ctypes import FreeLibrary as dlclose

    def dlopen(name):
        _ctypes.LoadLibrary(name, False)
        #ctypes.WinDLL(name, False)


elif os.name == "posix":
    from _ctypes import dlopen, dlclose


def get_last_traceback(tb):
    while tb.tb_next:
        tb = tb.tb_next
    return tb


lib_ext = {
     "linux2": ".so",
     "win32":  ".dll",
     }.get(sys.platform, "")


def PLCprint(message):
    sys.stdout.write(("PLCobject : "+message+"\n"))
    sys.stdout.flush()

@Pyro4.expose
class PLCObject(object):
    def __init__(self, workingdir, daemon, argv, statuschange, evaluator, pyruntimevars):
        object.__init__(self)
        self.evaluator = evaluator
        self.argv = [workingdir] + argv  # force argv[0] to be "path" to exec...
        self.workingdir = workingdir
        self.PLCStatus = "Empty"
        self.PLClibraryHandle = None
        self.PLClibraryLock = Lock()
        self.DummyIteratorLock = None
        # Creates fake C funcs proxies
        self._FreePLC()
        self.daemon = daemon
        self.statuschange = statuschange
        self.hmi_frame = None
        self.pyruntimevars = pyruntimevars
        self._loading_error = None
        self.python_runtime_vars = None
        self.TraceThread = None
        self.TraceLock = Lock()
        self.TraceWakeup = Event()
        self.Traces = []
        self.mbrtu_settings = ""

    def AutoLoad(self):
        # Get the last transfered PLC if connector must be restart
        try:
            self.CurrentPLCFilename = open(
                             self._GetMD5FileName(),
                             "r").read().strip() + lib_ext
            if self.LoadPLC():
                self.PLCStatus = "Stopped"
        except Exception as e:
            self.PLCStatus = "Empty"
            self.CurrentPLCFilename = None

    def StatusChange(self):
        if self.statuschange is not None:
            for callee in self.statuschange:
                callee(self.PLCStatus)

    def LogMessage(self, *args):
        if len(args) == 2:
            level, msg = args
        else:
            level = LogLevelsDefault
            msg, = args

        return self._LogMessage(level, msg.encode(), len(msg))

    def ResetLogCount(self):
        if self._ResetLogCount is not None:
            self._ResetLogCount()

    def GetLogCount(self, level):
        if self._GetLogCount is not None:
            return int(self._GetLogCount(level))
        elif self._loading_error is not None and level == 0:
            return 1

    def GetLogMessage(self, level, msgid):
        tick = ctypes.c_uint32()
        tv_sec = ctypes.c_uint32()
        tv_nsec = ctypes.c_uint32()
        if self._GetLogMessage is not None:
            maxsz = len(self._log_read_buffer)-1
            sz = self._GetLogMessage(level, msgid,
                                     self._log_read_buffer, maxsz,
                                     ctypes.byref(tick),
                                     ctypes.byref(tv_sec),
                                     ctypes.byref(tv_nsec))
            if sz and sz <= maxsz:
                self._log_read_buffer[sz] = b'\x00'
                return self._log_read_buffer.value.decode(), tick.value, tv_sec.value, tv_nsec.value
        elif self._loading_error is not None and level == 0:
            return self._loading_error, 0, 0, 0
        return None

    def _GetMD5FileName(self):
        return os.path.join(self.workingdir, "lasttransferedPLC.md5")

    def _GetLibFileName(self):
        return os.path.join(self.workingdir, self.CurrentPLCFilename)

    def LoadPLC(self):
        """
        Load PLC library
        Declare all functions, arguments and return values
        """
        md5 = open(self._GetMD5FileName(), "r").read()
        try:
            dll_dir = self._GetLibFileName()
            self._PLClibraryHandle = dlopen(dll_dir)
            self.PLClibraryHandle = ctypes.CDLL(self.CurrentPLCFilename, handle=self._PLClibraryHandle)

            self.PLC_ID = ctypes.c_char_p.in_dll(self.PLClibraryHandle, "PLC_ID")

            if len(md5) == 32:
                self.PLC_ID.value = md5.encode()

            self._startPLC = self.PLClibraryHandle.startPLC
            self._startPLC.restype = ctypes.c_int
            self._startPLC.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_char_p)]

            self._stopPLC_real = self.PLClibraryHandle.stopPLC
            self._stopPLC_real.restype = None

            self._PythonIterator = getattr(self.PLClibraryHandle, "PythonIterator", None)
            if self._PythonIterator is not None:
                self._PythonIterator.restype = ctypes.c_char_p
                self._PythonIterator.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p)]

                self._stopPLC = self._stopPLC_real
            else:
                # If python confnode is not enabled, we reuse _PythonIterator
                # as a call that block pythonthread until StopPLC
                self.PlcStopping = Event()

                def PythonIterator(res, blkid):
                    self.PlcStopping.clear()
                    self.PlcStopping.wait()
                    return None
                self._PythonIterator = PythonIterator

                def __StopPLC():
                    self._stopPLC_real()
                    self.PlcStopping.set()
                self._stopPLC = __StopPLC

            self._ResetDebugVariables = self.PLClibraryHandle.ResetDebugVariables
            self._ResetDebugVariables.restype = None

            self._RegisterDebugVariable = self.PLClibraryHandle.RegisterDebugVariable
            self._RegisterDebugVariable.restype = None
            self._RegisterDebugVariable.argtypes = [ctypes.c_int, ctypes.c_void_p]

            self._FreeDebugData = self.PLClibraryHandle.FreeDebugData
            self._FreeDebugData.restype = None

            self._GetDebugData = self.PLClibraryHandle.GetDebugData
            self._GetDebugData.restype = ctypes.c_int
            self._GetDebugData.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_void_p)]

            self._suspendDebug = self.PLClibraryHandle.suspendDebug
            self._suspendDebug.restype = ctypes.c_int
            self._suspendDebug.argtypes = [ctypes.c_int]

            self._resumeDebug = self.PLClibraryHandle.resumeDebug
            self._resumeDebug.restype = None

            self._ResetLogCount = self.PLClibraryHandle.ResetLogCount
            self._ResetLogCount.restype = None

            self._GetLogCount = self.PLClibraryHandle.GetLogCount
            self._GetLogCount.restype = ctypes.c_uint32
            self._GetLogCount.argtypes = [ctypes.c_uint8]

            self._LogMessage = self.PLClibraryHandle.LogMessage
            self._LogMessage.restype = ctypes.c_int
            self._LogMessage.argtypes = [ctypes.c_uint8, ctypes.c_char_p, ctypes.c_uint32]

            self._log_read_buffer = ctypes.create_string_buffer(1 << 14)  # 16K
            self._GetLogMessage = self.PLClibraryHandle.GetLogMessage
            self._GetLogMessage.restype = ctypes.c_uint32
            self._GetLogMessage.argtypes = [ctypes.c_uint8, ctypes.c_uint32, ctypes.c_char_p, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
            try:
                self.load_for_emulator()
            except Exception as e:
                print("!!!DLL Load error: " + e)

            self._loading_error = None

            self.PythonRuntimeInit()

            return True
        except Exception:
            self._loading_error = traceback.format_exc()
            PLCprint(self._loading_error)
            return False

    def load_for_emulator(self):
        self._Set_Settings_MBRTU = self.PLClibraryHandle.Set_Settings_MBRTU
        self._Set_Settings_MBRTU.restype = ctypes.c_int
        self._Set_Settings_MBRTU.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_char_p)]

        self._CloseThreadMBRTU = self.PLClibraryHandle.CloseThreadMBRTU
        self._CloseThreadMBRTU.restype = None
        self._CloseThreadMBRTU.argtypes = None

        self._MBRTUThreadIsAlive = self.PLClibraryHandle.MBRTUIsAlive
        self._MBRTUThreadIsAlive.restype = ctypes.c_uint8
        self._MBRTUThreadIsAlive.argtypes = None

        self._DIStatus = self.PLClibraryHandle.App_DIStatus
        self._DIStatus.restype = None
        self._DIStatus.argtypes = [ctypes.POINTER(DISTATUS)]

        self._DIVal = self.PLClibraryHandle.App_DIVal
        self._DIVal.restype = None
        self._DIVal.argtypes = [ctypes.POINTER(DIVAL)]

        self._DICntT = self.PLClibraryHandle.App_DICntT
        self._DICntT.restype = None
        self._DICntT.argtypes = [ctypes.POINTER(DICNTT)]

        self._DIStateCfgCntT = self.PLClibraryHandle.App_DIStateCfgCntT
        self._DIStateCfgCntT.restype = None
        self._DIStateCfgCntT.argtypes = [ctypes.POINTER(DISTATECFGCNTT)]

        self._DICnt = self.PLClibraryHandle.App_DICnt
        self._DICnt.restype = None
        self._DICnt.argtypes = [ctypes.POINTER(DICNT)]

        self._DIStateCfgCnt = self.PLClibraryHandle.App_DIStateCfgCnt
        self._DIStateCfgCnt.restype = None
        self._DIStateCfgCnt.argtypes = [ctypes.POINTER(DISTATECFGCNT)]

        self._DIEnc = self.PLClibraryHandle.App_DIEnc
        self._DIEnc.restype = None
        self._DIEnc.argtypes = [ctypes.POINTER(DIENC)]

        self._DIStateCfgEnc = self.PLClibraryHandle.App_DIStateCfgEnc
        self._DIStateCfgEnc.restype = None
        self._DIStateCfgEnc.argtypes = [ctypes.POINTER(DISTATECFGENC)]

        self._AIStatus = self.PLClibraryHandle.App_AIStatus
        self._AIStatus.restype = None
        self._AIStatus.argtypes = [ctypes.POINTER(AISTATUS)]

        self._AIVal = self.PLClibraryHandle.App_AIVal
        self._AIVal.restype = None
        self._AIVal.argtypes = [ctypes.POINTER(AIVAL)]

        self._PTStatus = self.PLClibraryHandle.App_PTStatus
        self._PTStatus.restype = None
        self._PTStatus.argtypes = [ctypes.POINTER(PTSTATUS)]

        self._PTVal = self.PLClibraryHandle.App_PTVal
        self._PTVal.restype = None
        self._PTVal.argtypes = [ctypes.POINTER(PTVAL)]

        self._DTStatus = self.PLClibraryHandle.App_DTStatus
        self._DTStatus.restype = None
        self._DTStatus.argtypes = [ctypes.POINTER(DTSTATUS)]

        self._DTVal = self.PLClibraryHandle.App_DTVal
        self._DTVal.restype = None
        self._DTVal.argtypes = [ctypes.POINTER(DTVAL)]

        self._DOStatus = self.PLClibraryHandle.App_DOStatus
        self._DOStatus.restype = None
        self._DOStatus.argtypes = [ctypes.POINTER(DOSTATUS)]

        self._AOStatus = self.PLClibraryHandle.App_AOStatus
        self._AOStatus.restype = None
        self._AOStatus.argtypes = [ctypes.POINTER(AOSTATUS)]
        #self._InterfacesFunction = SoftPLC_IRQ.in_dll(self.PLClibraryHandle, "SoftPLC_Interfaces")
        #print(int(self._InterfacesFunction.TaskAI_IRQ(ctypes.c_uint8(0), ctypes.c_float(10.0))))
        self._GetAO_Value = self.PLClibraryHandle.GetAO_Value
        self._GetAO_Value.restype = ctypes.c_float
        self._GetAO_Value.argtypes = [ctypes.c_uint8, ctypes.c_uint8]

        self._GetDO_Value = self.PLClibraryHandle.GetDO_Value
        self._GetDO_Value.restype = ctypes.c_uint32
        self._GetDO_Value.argtypes = [ctypes.c_uint8, ctypes.c_uint8]

        self._TaskDI_IRQ = self.PLClibraryHandle.TaskDI_IRQ
        self._TaskDI_IRQ.restype = ctypes.c_uint8
        self._TaskDI_IRQ.argtypes = [ctypes.c_uint8, ctypes.c_uint32]

        self._TaskAI_IRQ = self.PLClibraryHandle.TaskAI_IRQ
        self._TaskAI_IRQ.restype = ctypes.c_uint8
        self._TaskAI_IRQ.argtypes = [ctypes.c_uint8, ctypes.c_float]

        self._TaskPT_IRQ = self.PLClibraryHandle.TaskPT_IRQ
        self._TaskPT_IRQ.restype = ctypes.c_uint8
        self._TaskPT_IRQ.argtypes = [ctypes.c_uint8, ctypes.c_float]

        self._TaskDT_IRQ = self.PLClibraryHandle.TaskDT_IRQ
        self._TaskDT_IRQ.restype = ctypes.c_uint8
        self._TaskDT_IRQ.argtypes = [ctypes.c_uint8, ctypes.c_float]

        self._GetMsgInQueue = self.PLClibraryHandle.GetMsgInQueue
        self._GetMsgInQueue.restype = ctypes.c_size_t
        self._GetMsgInQueue.argtypes = [ctypes.POINTER(LOG_MBRTU_T)]

        self._freeMBRTU_msg = self.PLClibraryHandle.freeMBRTU_msg
        self._freeMBRTU_msg.restype = ctypes.POINTER(LOG_MBRTU_T)
        self._freeMBRTU_msg.argtypes = None

    def UnLoadPLC(self):
        self.PythonRuntimeCleanup()
        self._FreePLC()

    def _FreePLC(self):
        """
        Unload PLC library.
        This is also called by __init__ to create dummy C func proxies
        """
        self.PLClibraryLock.acquire()
        # Forget all refs to library
        self._startPLC = lambda x, y: None
        self._stopPLC = lambda: None
        self._ResetDebugVariables = lambda: None
        self._RegisterDebugVariable = lambda x, y: None
        self._IterDebugData = lambda x, y: None
        self._FreeDebugData = lambda: None
        self._GetDebugData = lambda: -1
        self._suspendDebug = lambda x: -1
        self._resumeDebug = lambda: None
        self._PythonIterator = lambda: ""
        self._GetLogCount = None
        self._LogMessage = lambda l, m, s: PLCprint("OFF LOG :"+m.decode())
        self._GetLogMessage = None

        self._Set_Settings_MBRTU = None
        self._DIStatus = None
        self._DIVal = None
        self._DICntT = None
        self._DIStateCfgCntT = None
        self._DICnt = None
        self._DIStateCfgCnt = None
        self._DIEnc = None
        self._DIStateCfgEnc = None
        self._AIStatus = None
        self._AIVal = None
        self._PTStatus = None
        self._PTVal = None
        self._DTStatus = None
        self._DTVal = None
        self._DOStatus = None
        self._AOStatus = None
        self._GetAO_Value = None
        self._GetDO_Value = None
        self._TaskDI_IRQ = None
        self._TaskAI_IRQ = None
        self._TaskPT_IRQ = None
        self._TaskDT_IRQ = None

        self.PLClibraryHandle = None
        # Unload library explicitely
        if getattr(self, "_PLClibraryHandle", None) is not None:
            dlclose(self._PLClibraryHandle)
            self._PLClibraryHandle = None

        self.PLClibraryLock.release()
        return False

    def PythonRuntimeCall(self, methodname):
        """
        Calls init, start, stop or cleanup method provided by
        runtime python files, loaded when new PLC uploaded
        """
        for method in self.python_runtime_vars.get("_runtime_%s" % methodname, []):
            res, exp = self.evaluator(method)
            if exp is not None:
                self.LogMessage(0, '\n'.join(traceback.format_exception(*exp)))

    def PythonRuntimeInit(self):
        MethodNames = ["init", "start", "stop", "cleanup"]
        self.python_runtime_vars = globals().copy()
        self.python_runtime_vars.update(self.pyruntimevars)

        class PLCSafeGlobals:
            def __getattr__(_self, name):
                try:
                    t = self.python_runtime_vars["_"+name+"_ctype"]
                except KeyError:
                    raise KeyError("Try to get unknown shared global variable : %s" % name)
                v = t()
                r = self.python_runtime_vars["_PySafeGetPLCGlob_"+name](ctypes.byref(v))
                return self.python_runtime_vars["_"+name+"_unpack"](v)

            def __setattr__(_self, name, value):
                try:
                    t = self.python_runtime_vars["_"+name+"_ctype"]
                except KeyError:
                    raise KeyError("Try to set unknown shared global variable : %s" % name)
                v = self.python_runtime_vars["_"+name+"_pack"](t, value)
                self.python_runtime_vars["_PySafeSetPLCGlob_"+name](ctypes.byref(v))

        self.python_runtime_vars.update({
            "PLCGlobals":     PLCSafeGlobals(),
            "WorkingDir":     self.workingdir,
            "PLCObject":      self,
            "PLCBinary":      self.PLClibraryHandle,
            "PLCGlobalsDesc": []})

        for methodname in MethodNames:
            self.python_runtime_vars["_runtime_%s" % methodname] = []

        try:
            filenames = os.listdir(self.workingdir)
            filenames.sort()
            for filename in filenames:
                name, ext = os.path.splitext(filename)
                if name.upper().startswith("RUNTIME") and ext.upper() == ".PY":
                    exec(compile(open(os.path.join(self.workingdir, filename), "rb").read(), os.path.join(self.workingdir, filename), 'exec'), self.python_runtime_vars)
                    for methodname in MethodNames:
                        method = self.python_runtime_vars.get("_%s_%s" % (name, methodname), None)
                        if method is not None:
                            self.python_runtime_vars["_runtime_%s" % methodname].append(method)
        except Exception:
            self.LogMessage(0, traceback.format_exc())
            raise

        self.PythonRuntimeCall("init")

    def PythonRuntimeCleanup(self):
        if self.python_runtime_vars is not None:
            self.PythonRuntimeCall("cleanup")

        self.python_runtime_vars = None

    def PythonThreadProc(self):
        self.StartSem.release()
        res, blkid = b"None", ctypes.c_void_p()

        compile_cache = {}
        while True:
            # print "_PythonIterator(", res, ")",
            cmd = self._PythonIterator(res, blkid)
            FBID = blkid.value
            # print " -> ", cmd, blkid
            if cmd is None:
                break
            try:
                self.python_runtime_vars["FBID"] = FBID
                ccmd, AST = compile_cache.get(FBID, (None, None))
                if ccmd is None or ccmd != cmd:
                    AST = compile(cmd, '<plc>', 'eval')
                    compile_cache[FBID] = (cmd, AST)
                result, exp = self.evaluator(eval, AST, self.python_runtime_vars)
                if exp is not None:
                    res = "#EXCEPTION : "+str(exp[1])
                    self.LogMessage(1, ('PyEval@0x%x(Code="%s") Exception "%s"') % (
                        FBID, cmd, '\n'.join(traceback.format_exception(*exp))))
                else:
                    res = str(result)
                self.python_runtime_vars["FBID"] = None
            except Exception as e:
                res = "#EXCEPTION : "+str(e)
                self.LogMessage(1, ('PyEval@0x%x(Code="%s") Exception "%s"') % (FBID, cmd, str(e)))

    def StartPLC(self):
        if self.CurrentPLCFilename is not None and self.PLCStatus == "Stopped":
            c_argv = ctypes.c_char_p * len(self.argv)
            c_argv_encode = c_argv(*[argv.encode() for argv in self.argv])
            c_argc = ctypes.c_int()
            c_argc.value = len(self.argv)
            res = self._startPLC(c_argc, c_argv_encode)
            if res == 0:
                self.PLCStatus = "Started"
                self.StatusChange()
                self.PythonRuntimeCall("start")
                self.StartSem = Semaphore(0)
                self.PythonThread = Thread(target=self.PythonThreadProc)
                self.PythonThread.start()
                self.StartSem.acquire()
                self.LogMessage("PLC started")
                #self._SetSettingsMBRTU("Soft_Plc -b 7 -d 0 -p 0 -s 0 -m 1 -o 2 -c 3 -i 1")
                #if self.mbrtu_settings != "":
                #    self._SetSettingsMBRTU(self.mbrtu_settings)
                    #self.DIStatus(3)
            else:
                self.LogMessage(0, _("Problem starting PLC : error %d" % res))
                self.PLCStatus = "Broken"
                self.StatusChange()

    def StopPLC(self):
        if self.PLCStatus == "Started":

            self.LogMessage("PLC stopped")

            self._stopPLC()
            self.PythonThread.join()
            self.PLCStatus = "Stopped"
            self.StatusChange()
            self.PythonRuntimeCall("stop")
            if self.TraceThread is not None:
                self.TraceWakeup.set()
                self.TraceThread.join()
                self.TraceThread = None
            return True
        return False

    def _Reload(self):
        self.daemon.shutdown(True)
        self.daemon.sock.close()
        os.execv(sys.executable, [sys.executable]+sys.argv[:])
        # never reached
        return 0

    def ForceReload(self):
        # respawn python interpreter
        Timer(0.1, self._Reload).start()
        return True

    def GetPLCstatus(self):
        return self.PLCStatus, list(map(self.GetLogCount, range(LogLevelsCount)))

    def NewPLC(self, md5sum, data, extrafiles):
        if self.PLCStatus in ["Stopped", "Empty", "Broken"]:
            NewFileName = md5sum + lib_ext
            extra_files_log = os.path.join(self.workingdir, "extra_files.txt")

            self.UnLoadPLC()

            self.LogMessage("NewPLC (%s)" % md5sum)
            self.PLCStatus = "Empty"

            try:
                if self.CurrentPLCFilename is not None:
                    path = pathlib.Path(os.path.join(self.workingdir,
                                           self.CurrentPLCFilename))
                    path.unlink()
                for filename in open(extra_files_log, "r").readlines() + [extra_files_log]:
                    try:
                        os.remove(os.path.join(self.workingdir, filename.strip()))
                    except Exception:
                        pass
            except Exception as e:
                pass

            try:
                # Create new PLC file
                _data_bytes = base64.b64decode(data["data"])
                open(os.path.join(self.workingdir, NewFileName),
                     'wb').write(_data_bytes)

                # Store new PLC filename based on md5 key
                open(self._GetMD5FileName(), "w").write(md5sum)

                # Then write the files
                log = open(extra_files_log, "w")
                for fname, fdata in extrafiles:
                    ext_file_path = ("%(path)s\\%(filename)s") % {"path": fdata, "filename": fname}
                    work_file_path = ("%(path)s\\%(filename)s") % {"path": self.workingdir, "filename": fname}
                    shutil.copyfile(ext_file_path, work_file_path)
                    log.write(fname+'\n')

                # Store new PLC filename
                self.CurrentPLCFilename = NewFileName
            except Exception:
                self.PLCStatus = "Broken"
                self.StatusChange()
                PLCprint(traceback.format_exc())
                return False

            if self.LoadPLC():
                self.PLCStatus = "Stopped"
            else:
                self.PLCStatus = "Broken"
                self._FreePLC()
            self.StatusChange()

            return self.PLCStatus == "Stopped"
        return False

    def MatchMD5(self, MD5):
        try:
            last_md5 = open(self._GetMD5FileName(), "r").read()
            return last_md5 == MD5
        except Exception:
            pass
        return False

    def SetTraceVariablesList(self, idxs):
        """
        Call ctype imported function to append
        these indexes to registred variables in PLC debugger
        """
        if idxs:
            # suspend but dont disable
            if self._suspendDebug(False) == 0:
                # keep a copy of requested idx
                self._ResetDebugVariables()
                for idx, iectype, force in idxs:
                    if force is not None:
                        c_type, unpack_func, pack_func = \
                            TypeTranslator.get(iectype,
                                               (None, None, None))
                        force = ctypes.byref(pack_func(c_type, force))
                    self._RegisterDebugVariable(idx, force)
                self._TracesSwap()
                self._resumeDebug()
        else:
            self._suspendDebug(True)

    def _TracesPush(self, trace):
        self.TraceLock.acquire()
        lT = len(self.Traces)
        if lT != 0 and lT * len(self.Traces[0]) > 1024 * 1024:
            self.Traces.pop(0)
        self.Traces.append(trace)
        self.TraceLock.release()

    def _TracesSwap(self):
        self.LastSwapTrace = time()
        if self.TraceThread is None and self.PLCStatus == "Started":
            self.TraceThread = Thread(target=self.TraceThreadProc)
            self.TraceThread.start()
        self.TraceLock.acquire()
        Traces = self.Traces
        self.Traces = []
        self.TraceLock.release()
        self.TraceWakeup.set()
        return Traces

    def _TracesAutoSuspend(self):
        # TraceProc stops here if Traces not polled for 3 seconds
        traces_age = time() - self.LastSwapTrace
        if traces_age > 3:
            self.TraceLock.acquire()
            self.Traces = []
            self.TraceLock.release()
            self._suspendDebug(True)  # Disable debugger
            self.TraceWakeup.clear()
            self.TraceWakeup.wait()
            self._resumeDebug()  # Re-enable debugger

    def _TracesFlush(self):
        self.TraceLock.acquire()
        self.Traces = []
        self.TraceLock.release()

    def GetTraceVariables(self):
        _Traces = self._TracesSwap()
        return (self.PLCStatus, _Traces)

    def TraceThreadProc(self):
        """
        Return a list of traces, corresponding to the list of required idx
        """
        while self.PLCStatus == "Started":
            tick = ctypes.c_uint32()
            size = ctypes.c_uint32()
            buff = ctypes.c_void_p()
            TraceBuffer = None
            if self.PLClibraryLock.acquire(False):
                if self._GetDebugData(ctypes.byref(tick),
                                      ctypes.byref(size),
                                      ctypes.byref(buff)) == 0:
                    if size.value:
                        TraceBuffer = ctypes.string_at(buff.value, size.value)
                        #TraceBuffer = ctypes.string_at(buff.value, size.value)
                    self._FreeDebugData()
                self.PLClibraryLock.release()
            if TraceBuffer is not None:
                self._TracesPush((tick.value, TraceBuffer))
            self._TracesAutoSuspend()
        self._TracesFlush()

    def RemoteExec(self, script, *kwargs):
        try:
            exec(script, kwargs)
        except Exception:
            e_type, e_value, e_traceback = sys.exc_info()
            line_no = traceback.tb_lineno(get_last_traceback(e_traceback))
            return (-1, "RemoteExec script failed!\n\nLine %d: %s\n\t%s" %
                        (line_no, e_value, script.splitlines()[line_no - 1]))
        return (0, kwargs.get("returnVal", None))

    def SetSettingsMBRTU(self, string_sett):
        argc = len(string_sett.split())
        argv = string_sett.split()
        c_argv = ctypes.c_char_p * argc
        c_argv_encode = c_argv(*[s.encode() for s in argv])
        c_argc = ctypes.c_int()
        c_argc.value = argc
        self._Set_Settings_MBRTU(c_argc, c_argv_encode)
        pass

    def CloseThreadMBRTU(self):
        self._CloseThreadMBRTU()

    def MBRTUThreadIsAlive(self):
        uint8_res = self._MBRTUThreadIsAlive()
        res = bool(uint8_res)
        return res

    def  DIStatus(self, ch_num):
        di_status = DISTATUS(BOOL(True), BOOL(True), BYTE(ch_num))
        self._DIStatus(ctypes.byref(di_status))
        if di_status.OK.value == 1:
            return di_status.OM.value
        return None

    def DIVal(self, ChNum):
        di_val = DIVAL(BOOL(True), BOOL(True), BOOL(True), BYTE(ChNum))

        self._DIVal(ctypes.byref(di_val))
        if di_val.OK.value == 1:
            return di_val.OV.value

    def DICntT(self, ch_num):
        di_cntt = DICNTT(BOOL(True), BOOL(True), BOOL(True), BYTE(ch_num))
        self._DICntT(ctypes.byref(di_cntt))
        if di_cntt.OK.value == 1:
            return {"OISSET": di_cntt.OISSET.value, "OV": di_cntt.OV.value}

    def DIStateCfgCntT(self, ch_num):
        di_state_cfg_cnt_t = DISTATECFGCNTT(BOOL(True), BOOL(True), BYTE(ch_num))
        self._DIStateCfgCntT(ctypes.byref(di_state_cfg_cnt_t))
        if di_state_cfg_cnt_t.OK.value == 1:
            return {'OSP', di_state_cfg_cnt_t.OSP.value, 'OENCMPMD', di_state_cfg_cnt_t.OENCMPMD.value}

    def DICnt(self, ch_num):
        di_cnt = DICNT(BOOL(True), BOOL(True), BOOL(True), BYTE(ch_num))
        self._DICnt(ctypes.byref(di_cnt))
        if di_cnt.OK.value == 1:
            return {'OISSET': di_cnt.OISSET.value, 'OV': di_cnt.OV.value}

    def DIStateCfgCnt(self, ch_num):
        di_state_cnt = DISTATECFGCNT(BOOL(True), BOOL(True), BYTE(ch_num))
        self._DIStateCfgCnt(ctypes.byref(di_state_cnt))
        if di_state_cnt.OK.value == 1:
            return {"OSP": di_state_cnt.OSP.value, "OENCMPMD": di_state_cnt.OENCMPMD.value}

    def DIEnc(self, ChA):
        di_enc = DIENC(BOOL(True), BOOL(True), BOOL(True), BYTE(ChA))
        self._DIEnc(ctypes.byref(di_enc))
        if di_enc.OK.value == 1:
            return {"OVA": di_enc.OVA.value, "OISSETA": di_enc.OISSETA.value, "OVB": di_enc.OVB.value,
                        "OISSETB": di_enc.OISSETB.value, "OVT": di_enc.OVT.value, "OISSETT": di_enc.OISSETT.value }

    def DIStateCfgEnc(self, ch_num):
        enc_state = DISTATECFGENC(BOOL(True), BOOL(True), BYTE(ch_num))
        self._DIStateCfgEnc(ctypes.byref(enc_state))
        if enc_state.OK.value == 1:
            return {"OSPA": enc_state.OSPA.value, "OENCMPMDA": enc_state.OENCMPMDA.value,
                    "OSPB": enc_state.OSPB.value, "OENCMPMDB": enc_state.OENCMPMDB.value,
                    "OSPT": enc_state.OSPT.value, "OENCMPMDT": enc_state.OENCMPMDT.value}

    def AIStatus(self, ch_num):
        ai_status = AISTATUS(BOOL(True), BOOL(True), BYTE(ch_num))
        self._AIStatus(ctypes.byref(ai_status))
        if ai_status.OK.value == 1:
            return {"OM": ai_status.OM.value, "OS": ai_status.OS.value}

    def AIVal(self, ch_num):
        ai_val = AIVAL(BOOL(True), BOOL(True), BOOL(True), BYTE(ch_num))
        self._AIVal(ctypes.byref(ai_val))
        if ai_val.OK.value == 1:
            return ai_val.OV.value

    def PTStatus(self, ch_num):
        pt_status = PTSTATUS(BOOL(True), BOOL(True), BYTE(ch_num))
        self._PTStatus(ctypes.byref(pt_status))
        if pt_status.OK.value == 1:
            return {"OM": pt_status.OM.value, "OS": pt_status.OS.value}

    def PTVal(self, ch_num):
        pt_val = PTVAL(BOOL(True), BOOL(True), BOOL(True), BYTE(ch_num))
        self._PTVal(ctypes.byref(pt_val))
        if pt_val.OK.value == 1:
            return pt_val.OV.value

    def DTStatus(self, ch_num):
        dt_status = DTSTATUS(BOOL(True), BOOL(True), BYTE(ch_num))
        self._DTStatus(ctypes.byref(dt_status))
        if dt_status.OK.value == 1:
            return {"OM": dt_status.OM.value, "OS": dt_status.OS.value}

    def DTVal(self, ch_num):
        dt_val = DTVAL(BOOL(True), BOOL(True), BOOL(True), BYTE(ch_num))
        self._DTVal(ctypes.byref(dt_val))
        if dt_val.OK.value == 1:
            return dt_val.OV.value

    def DOStatus(self, ch_num):
        do_status = DOSTATUS(BOOL(True), BOOL(True), BYTE(ch_num))
        self._DOStatus(ctypes.byref(do_status))
        if do_status.OK.value == 1:
            res = {"OM": do_status.OM.value, "OEPWM": do_status.OEPWM.value, "OTPWM": do_status.OTPWM.value,
                    "ODPWM": do_status.ODPWM.value, "OESF": do_status.OESF.value, "OVSF": do_status.OVSF.value}
            return res

    def AOStatus(self, ch_num):
        ao_status = AOSTATUS(BOOL(True), BOOL(True), BYTE(ch_num))
        self._AOStatus(ctypes.byref(ao_status))
        if ao_status.OK.value == 1:
            return {"OM": ao_status.OM.value, "OESF": ao_status.OESF.value, "OVSF": ao_status.OVSF.value }

    def GetAO_Value(self, ch_num, status):
        c_status = ctypes.c_uint8(status)
        c_ch_num = ctypes.c_uint8(ch_num)
        res = float(self._GetAO_Value(c_ch_num, c_status))
        return res

    def GetDO_Value(self, ch_num, status):
        c_status = ctypes.c_uint8(status)
        c_ch_num = ctypes.c_uint8(ch_num)
        return int(self._GetDO_Value(c_ch_num, c_status))

    def TaskDI_IRQ(self, ch_num, set_val):
        c_ch_num = ctypes.c_uint8(ch_num)
        c_set_val = ctypes.c_uint32(set_val)
        return int(self._TaskDI_IRQ(c_ch_num, c_set_val))

    def TaskAI_IRQ(self, ch_num, set_val):
        return self.GetAnalog(ch_num, set_val, self._TaskAI_IRQ)

    def TaskPT_IRQ(self, ch_num, set_val):
        return self.GetAnalog(ch_num, set_val, self._TaskPT_IRQ)

    def TaskDT_IRQ(self, ch_num, set_val):
        return self.GetAnalog(ch_num, set_val, self._TaskDT_IRQ)

    def GetAnalog(self, ch_num, set_val, func):
        c_ch_num = ctypes.c_uint8(ch_num)
        c_set_val = ctypes.c_float(set_val)
        return float(func(c_ch_num, c_set_val))

    def GetMsgInQueue(self):
        msg_list = []
        log_struct = LOG_MBRTU_T()
        while(self._GetMsgInQueue(ctypes.byref(log_struct)) > 1):
            msg_data = {}
            msg_data["direction"] = "TX" if log_struct.isTx == 1 else "RX"
            msg_data["time"] = strftime("%H:%M:%S", localtime(log_struct.msg_time))
            #msg_data["time"] = strftime("%H:%M:%S", gmtime(log_struct.msg_time))
            msg_data["mbrtu_msg"] = " ".join([MBRTU_Hex(log_struct.mbrtu_msg[i]) for i in range(log_struct.m_msg_sz)])
            msg_data["service_msg"] = log_struct.service_msg.decode()
            msg_list.append(msg_data)
            self._freeMBRTU_msg(ctypes.byref(log_struct))
        return msg_list


def MBRTU_Hex(num):
    hex_num = str(hex(num)).replace("0x", "").upper()
    return hex_num if len(hex_num) > 1 else "0" + hex_num