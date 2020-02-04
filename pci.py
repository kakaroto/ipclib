import os
import mmio
from utils import *

class PCIDevice(object):
    def __init__(self, bus, dev, func, thread, base_address=0xE0000000):
        self._bus = bus & 0xFF
        self._dev = dev & 0x1F
        self._func = func & 0x7
        self._thread = thread
        self._base_addr = base_address

    def getID(self):
        return (self._bus << 8) | (self._dev << 3) | self._func
    
    def getIOAddress(self, offset=0):
        return self._base_addr | (self._bus << 20) | (self._dev << 15) | (self._func << 12) | (offset & 0xFFF)

    def getVID(self):
        return self.readWord(0)
    
    def readWord(self, offset):
        return self._thread.memblock(hex(self.getIOAddress(offset)).replace("L", "") + "P", 0x4, 1)

    
def list_pci_devices(base_addr=0xE0000000, alt="", bars=True):
    pwd = os.path.join(os.getcwd(), "PCI")
    for bus in range(32):
        for dev in range (32):
            for func in range (8):
                device = PCIDevice(bus, dev, func, t, base_addr)
                vid = device.getVID()
                if vid != 0xFFFFFFFF and vid != 0x0:
                    print("PCI %d.%d.%d : %s" % (bus, dev, func, vid.ToHex()))
                    mmio.save_mmios(pwd, [(device.getIOAddress(), 0x1000)], "PCI_" + alt + "%d.%d.%d_" % (bus, dev, func) )
                    if bars:
                        for offset in range(0x10, 0x28, 4):
                            bar = device.readWord(offset)
                            if bar != 0:
                                bar[0:7] = 0
                                mmio.save_mmios(pwd, [(bar, 0x1000)], "BAR_" + alt + "%d.%d.%d_" % (bus, dev, func))
                elif dev == 0 and func == 0:
                    break
            else:
                continue
            break

def alt_list_pci_devices():
    list_pci_devices(0xF1000000, "alt_")
