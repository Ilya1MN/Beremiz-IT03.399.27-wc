"""Minimalistic PySciter sample for Windows."""

import sciter
from sciter.capi.scbehavior import BEHAVIOR_EVENTS
from threading import Thread
import connectors
import getopt
import sys
import os
import util.paths as paths
import json
import time
from runtime.SerialPortList import GetComPorts

def usage():
    print("""
Usage of PLC Emulator:\n
%s {[-i IP] [-p port]|-h|--help} working_dir
           -i        - IP address of interface to bind to PYRO (default:localhost)
           -p        - port number default:3000
""" % sys.argv[0])


try:
    opts, argv = getopt.getopt(sys.argv[1:], "i:p:h")
except getopt.GetoptError as err:
    # print help information and exit:
    print(str(err))  # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

# default values
given_ip = "localhost"
port = 3000

extensions = []

for o, a in opts:
    if o == "-h":
        usage()
        sys.exit()
    elif o == "-i":
        if len(a.split(".")) == 4 or a == "localhost":
            given_ip = a
        else:
            usage()
            sys.exit()
    elif o == "-p":
        # port: port that the service runs on
        port = int(a)
    else:
        usage()
        sys.exit()


beremiz_dir = paths.AbsDir(__file__)
sciter_dir = beremiz_dir + "\\Sciter"


class Frame(sciter.Window):
    def __init__(self, _ip_address, _port, settings, connector=None, obj=None):
        super().__init__(ismain=True, uni_theme=True)
        self._connector = connector
        self.EmulationStart = False
        self.pins_out = None
        self.pins_in = None#{"DI": 8, "AI": 5, "PT": 3, "DT": 10}
        self.logger = None
        self.given_ip = _ip_address
        self.parent_settings = settings
        if self.parent_settings is not None:
            self.port = self.parent_settings["port"]
        else:
            self.port = _port
        self.mbrtu_log_timer = None
        self.parent = obj
        if self.parent is not None:
            self.parent.emulatorFrame = self
            if self.parent._connector is not None:
                self._connector =  self.parent._connector


    def SetLogger(self):
        class Logger(object):
            def __init__(self, doc):
                self.document = doc

            def write(self, m):
                if self.document is not None:
                    self.document.fire_event(BEHAVIOR_EVENTS.CUSTOM, name="write", post=True, data={"msg": m})

            def write_error(self, m):
                if self.document is not None:
                    self.document.fire_event(BEHAVIOR_EVENTS.CUSTOM, name="write_error", post=True, data={"msg": m})

            def write_warning(self, m):
                if self.document is not None:
                    self.document.fire_event(BEHAVIOR_EVENTS.CUSTOM, name="write_warning", post=True, data={"msg": m})
        self.logger = Logger(sciter.Element.from_window(self.hwnd))

    def load(self, url):
        self.set_title("PLC Emulator")
        self.load_file(url)

    def SetConnector(self, _ip_address, _port):
        uri = "PYRO://%s:%s" % (_ip_address, _port)
        try:
            self._connector = connectors.ConnectorFactory(uri, self)
        except Exception as msg:
            self.logger.write_error("PYRO server not found. Can`t connect to %s" % uri)

    def RunFunctionInterfaces(self):
        """This is method for debug"""

        self.EmulationStart = True
        for key in self.pins_out.keys():
            get_status = getattr(self._connector, ("%(s)sStatus") % {"s": key})
            get_values = getattr(self._connector, ("Get%(s)s_Value") % {"s": key})
            self.InterfaceThread(get_status, get_values, key)

    def SetPinsOut(self, plc_name):
        output_interface = {}
        plc_config = os.path.join(os.path.join(sciter_dir, "targets"), plc_name + ".json")
        with open(plc_config, 'r', encoding='utf-8') as plc:
            data = json.load(plc)
        output = data.get("output", False)
        if output:
            for interface_type in output.keys():
                for inteface_name in output[interface_type].keys():
                    output_interface[inteface_name] = {"size": output[interface_type][inteface_name]["size"], "thread": None}
        self.pins_out = output_interface

    def SetPinsIn(self, plc_name):
        input_interface = {}
        plc_config = os.path.join(os.path.join(sciter_dir, "targets"), plc_name + ".json")
        with open(plc_config, 'r', encoding='utf-8') as plc:
            data = json.load(plc)
        input = data.get("input", False)
        if input:
            for interface_type in input.keys():
                for inteface_name in input[interface_type].keys():
                    input_interface[inteface_name] = input[interface_type][inteface_name]["size"]
        self.pins_in = input_interface

    def InitSoftPlcEmulatorIO(self):
        document = sciter.Element.from_window(self.hwnd)
        document = document.find_first("frame#editor")
        for key in self.pins_out.keys():
            get_status = getattr(self._connector, ("%(s)sStatus") % {"s": key.upper()})
            get_values = getattr(self._connector, ("Get%(s)s_Value") % {"s": key.upper()})
            for pin_num in range(self.pins_out[key]["size"]):
                status = get_status(pin_num)
                if status is not None:
                    ch_status = status["OM"]
                    new_value = get_values(pin_num, ch_status)
                    document.fire_event(BEHAVIOR_EVENTS.CUSTOM, name="Interface" + key.upper(), post=True,
                                        data={"pin_num": pin_num, "mode": ch_status, "value": new_value,
                                              "status": status})
                else:
                    document.fire_event(BEHAVIOR_EVENTS.CUSTOM, name="Interface" + key.upper(), post=True,
                                        data={"pin_num": pin_num})
        return

    def RunThread(self):
        self.InitSoftPlcEmulatorIO()
        for key in self.pins_out.keys():
            get_status = getattr(self._connector, ("%(s)sStatus") % {"s": key.upper()})
            get_values = getattr(self._connector, ("Get%(s)s_Value") % {"s": key.upper()})
            self.pins_out[key]["thread"] = Thread(target=self.InterfaceThread, args=(get_status, get_values, key))
            self.pins_out[key]["thread"].start()


    @sciter.script
    def SetPlcSettingsSciter(self, str):
        if self._connector is None:
            self.SetConnector(self.given_ip, self.port)
        if self._connector is not None:
            self._connector.SetSettingsMBRTU(str)
            if self.mbrtu_log_timer is None:
                self.mbrtu_log_timer = Thread(target=self.LogTimer)
            if not self.mbrtu_log_timer.is_alive():
                self.mbrtu_log_timer.start()


    @sciter.script
    def PYRO_GetSettings(self):
        settings = {"Hostname": self.given_ip, "Port": self.port}
        return settings

    @sciter.script
    def MBRTU_GetMessages(self):
        if self._connector:
            return self._connector.GetMsgInQueue()

    @sciter.script
    def SetSettingsSciter(self, params):
        if params is not None:
            self.given_ip = params["Hostname"] if params.get("Hostname", False) else self.given_ip
            self.port = params["Port"] if params.get("Port", False) else self.port
            self.SetConnector(self.given_ip, self.port)

    @sciter.script
    def StartEmulation(self, params):
        document = sciter.Element.from_window(self.hwnd)
        document.fire_event(BEHAVIOR_EVENTS.CUSTOM, name="MBRTU_Status", post=False, data={"mbrtuIsRun": True})
        if self._connector is None:
            if self.parent_settings is not None:
                if self.parent_settings["port"] != self.port:
                    print("Port в RTE Beremiz и в эмуляторе не соответствуют!")
                    self.port = self.parent_settings["port"]
            self.SetConnector(self.given_ip, self.port)

        if not self.EmulationStart and self._connector is not None:
            if self._connector.GetPLCstatus()[0] == "Stopped":
                self._connector.StartPLC()
            if self.pins_out is None:
                self.SetPinsOut(params["plc_name"])

            self.EmulationStart = True
            self.RunThread()
            self.logger.write("Emulator running")

    @sciter.script
    def GetListComPorts(self):
        return GetComPorts()

    @sciter.script
    def GetProjectPath(self):
        if self.parent is not None:
            return self.parent._getBuildPath()

    def GetDIValue(self, ChNum):
        modes = {"normal": 0,
                 "count": 1,
                 "tachometer": 2,
                 "encoder": 3,
                 "encoder_tacho": 4}
        plc_status_di = self._connector.DIStatus(ChNum)
        res = None
        if plc_status_di is not None:
            if plc_status_di is modes["normal"]:
                res = self._connector.DIVal(ChNum)
            elif plc_status_di is modes["count"]:
                res = self._connector.DICnt(ChNum)["OV"]
            elif plc_status_di is modes["tachometer"]:
                res = self._connector.DICntT(ChNum)["OV"]
            elif plc_status_di is modes["encoder"]:
                ChA = ChNum - 1 if ChNum % 2 != 0 else ChNum
                di_end = self._connector.DIEnc(ChA)
                res = di_end["OVA"] if ChA == ChNum else di_end["OVB"]
            elif plc_status_di is modes["encoder_tacho"]:
                ChA = ChNum - 1 if ChNum % 2 != 0 else ChNum
                di_end = self._connector.DIEnc(ChA)
                res = str(di_end["OVA"]) if ChA == ChNum else str(di_end["OVB"]) + " | " + str(di_end["OVT"]) + "rpm"

        return res

    def GetAIValue(self, ChNum):
        plc_status_ai = self._connector.AIStatus(ChNum)
        if plc_status_ai is not None:
            return self._connector.AIVal(ChNum)

    def GetPTValue(self, ChNum):
        plc_status_pt = self._connector.PTStatus(ChNum)
        if plc_status_pt is not None:
            return self._connector.PTVal(ChNum)

    def GetDTValue(self, ChNum):
        plc_status_dt = self._connector.DTStatus(ChNum)
        if plc_status_dt is not None:
            return self._connector.DTVal(ChNum)

    def SetDI(self, ChNum, SetValue):
        if self._connector is not None:
            res = self._connector.TaskDI_IRQ(ChNum, SetValue)
            return res

    def SetAI(self, ChNum, SetValue):
        if self._connector is not None:
            return self._connector.TaskAI_IRQ(ChNum, SetValue)

    def SetPT(self, ChNum, SetValue):
        if self._connector is not None:
            return self._connector.TaskPT_IRQ(ChNum, SetValue)

    def SetDT(self, ChNum, SetValue):
        if self._connector is not None:
            return self._connector.TaskDT_IRQ(ChNum, SetValue)

    @sciter.script
    def GetInputNativeApi(self):
        api = {"DI": {"set": self.SetDI, "get": self.GetDIValue},
               "AI": {"set": self.SetAI, "get": self.GetAIValue},
               "PT": {"set": self.SetPT, "get": self.GetPTValue},
               "DT": {"set": self.SetDT, "get": self.GetDTValue}}
        return api

    @sciter.script
    def StartEditor(self, params):

        self.SetPinsOut(params["plc_name"])
        self.SetPinsIn(params["plc_name"])

    def _Pause(self):
        self._connector.CloseThreadMBRTU()
        #document = sciter.Element.from_window(self.hwnd)

        self.EmulationStart = False
        for key in self.pins_out.keys():
            if self.pins_out[key]["thread"] is not None:
                if self.pins_out[key]["thread"].is_alive():
                    self.pins_out[key]["thread"].join()

    @sciter.script
    def StopEmulation(self):
        self._Pause()
        if self._connector is not None:
            if self._connector.GetPLCstatus()[0] == "Started":
                Thread(target=self._connector.StopPLC).start()
        self.logger.write("Emulator stopped")

    @sciter.script
    def PauseEmulation(self):
        self._Pause()
        self.logger.write("Emulator suspended")


    def InterfaceThread(self, get_status_func, get_value_func, key):
        document = sciter.Element.from_window(self.hwnd)
        document = document.find_first("frame#editor")
        mbrtu_status = False
        while self.EmulationStart and self._connector is not None:
            if mbrtu_status != self._connector.MBRTUThreadIsAlive():
                mbrtu_status = not mbrtu_status
                document.fire_event(BEHAVIOR_EVENTS.CUSTOM, name="MBRTU_Status", post=True, data={"mbrtuIsRun": mbrtu_status})
                print("status mbrtu is: " + str(mbrtu_status))

            for pin_num in range(self.pins_out[key]["size"]):
                status = get_status_func(pin_num)
                if status is not None:
                    ch_status = status["OM"]
                    new_value = get_value_func(pin_num, ch_status)
                    document.fire_event(BEHAVIOR_EVENTS.CUSTOM, name="Interface" + key.upper(), post=True,
                                        data={"pin_num": pin_num, "mode": ch_status, "value": new_value, "status": status})
                else:
                    document.fire_event(BEHAVIOR_EVENTS.CUSTOM, name="Interface" + key.upper(), post=True,
                                        data={"pin_num": pin_num})
            time.sleep(0.1)
        return

    def LogTimer(self):
        while True:
            msg = self.MBRTU_GetMessages()
            if len(msg) > 0:
                document = sciter.Element.from_window(self.hwnd)
                document.fire_event(BEHAVIOR_EVENTS.CUSTOM, name="add_mbrtu_log", post=True,
                                data=msg)
            time.sleep(1)

    def Close(self):
        document = sciter.Element.from_window(self.hwnd)
        document.fire_event(BEHAVIOR_EVENTS.CUSTOM, name="NativeCallClose", post=True)
        if self._connector is not None:
            self._connector

def SoftPlcEmulationRun(_ip, _port, settings=None, file_name="\\index_frame.html", obj=None):
    sciter.runtime_features(file_io=True, allow_sysinfo=True)

    frame = Frame(_ip_address=_ip, _port=_port, settings=settings, obj=obj)

    frame.minimal_menu()
    frame.load(sciter_dir + file_name)
    frame.expand()
    frame.SetLogger()
    frame.run_app(False)

def SoftPlcEmulationThread(_ip, _port, parent=None, file_name="\\index_frame.html"):
    sciter.runtime_features(file_io=True, allow_sysinfo=True)

    frame = Frame(_ip_address=_ip, _port=_port, obj=parent, settings=None)

    frame.minimal_menu()
    frame.load(sciter_dir + file_name)
    frame.expand()
    frame.SetLogger()
    frame.run_app(False)



def Hex(num):
    num_str = ""
    while num % 16 != 0:
        print(str(num) + " ")
        num = int(num / 16)



if __name__ == '__main__':
    SoftPlcEmulationRun(given_ip, port)#, "\\index.htm")
