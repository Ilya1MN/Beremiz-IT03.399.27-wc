import serial.tools.list_ports as ports
from natsort import natsorted


def GetSerialPorts():
    other_servers = ["LOCAL://", "PYRO://localhost:3000"]
    return natsorted(["YAPLC://%s" % port.device for port in ports.comports()] + other_servers)


def GetComPorts():
    return natsorted([port.device for port in ports.comports()])

if __name__ == '__main__':
    print(GetSerialPorts())
