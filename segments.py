import sys
import os
from utils import *
from asm import *

class Selector:
    def __init__(self, bits):
        self.bits = bits
        self.rpl = bits[0:1]
        self.table = bits[2]
        self.idx = bits[3:15]

    def __str__(self):
        return "%s %d (Privilege level %d)" % ("LDT" if self.table else "GDT", self.idx.ToUInt32(), self.rpl.ToUInt32())
    
class GDTEntry:
    def __init__(self, bits):
        # https://wiki.osdev.org/Global_Descriptor_Table
        self.bits = bits
        self.base_addr = bits[16:31]
        self.base_addr.Append(bits[32:39])
        self.base_addr.Append(bits[56:63])
        self.limit = bits[0:15]
        self.limit.Append(bits[48:51])
        self.access = bits[40:47]
        self.flags = bits[52:55]
        self.ac = self.access[0]
        self.rw = self.access[1]
        self.dc = self.access[2]
        self.ex = self.access[3]
        self.s = self.access[4]
        self.privl = self.access[5:6]
        self.pr = self.access[7]
        self.avl = self.flags[0]
        self.l = self.flags[1]
        self.sz = self.flags[2]
        self.gr = self.flags[3]

        

    def __str__(self):
        return "Segment: %s\n" \
            "  Base Address: %s\n" \
            "  Segment Limit: %s (%s)\n" \
            "  Flags: %s\n" \
            "    Granularity: %s\n" \
            "    Default operand size: %s\n" \
            "    Long-mode segment: %s\n" \
            "    Available for system: %s\n" \
            "  Access Byte: %s\n" \
            "    Present: %s\n" \
            "    Descriptor Privilege Level: %s\n" \
            "    Segment type: %s\n" \
            "    Read/Write/Execute: %s\n" \
            "    %s: %s\n" \
            "    Accessed: %s\n" % \
            (self.bits,
             self.base_addr,
             self.limit.ToHex() if self.gr == 0 else hex(self.limit.ToUInt32() * 0x1000), self.limit,
             self.flags,
             "4K Page" if self.gr else "Byte",
             "32-Bit" if self.sz else "16-Bit",
             "x86-64" if self.ex and self.l else ("x86-32" if self.ex else "Not a code segment"),
             self.avl,
             self.access,
             self.pr,
             "Ring-%d" % self.privl.ToUInt32(),
             "System Segment" if not self.s else ("Code" if self.ex else "Data"),
             "R-X" if self.ex and self.rw else ("--X" if self.ex else ("RW-" if self.rw else "R--")),
             "Conforming" if self.ex else "Direction",
             ("Grown down" if self.dc else "Grows up") if not self.ex else (("" if self.dc else "Not ") + "Conforming"),
             self.ac)

class IDTEntry:
    def __init__(self, bits):
        # https://wiki.osdev.org/Interrupt_Descriptor_Table
        self.bits = bits
        self.offset = bits[0:15]
        self.offset.Append(bits[48:63])
        self.selector = bits[16:31]
        self.zero = bits[32:39]
        self.type_attr = bits[40:47]
        self.gate_type = self.type_attr[0:3]
        self.s = self.type_attr[4]
        self.privl = self.type_attr[5:6]
        self.pr = self.type_attr[7]

        

    def __str__(self):
        GATE_TYPES = {5: "32-bit Task Gate",
                      6: "16-bit Interrupt Gate",
                      7: "16-bit Trap Gate",
                      14: "32-bit Interrupt Gate",
                      15: "32-bit Trap Gate"}
        
        return "Segment: %s\n" \
            "  Selector: %s (%s)\n" \
            "  Offset: %s\n" \
            "  Type and attributes: %s\n" \
            "    Present: %s\n" \
            "    Descriptor Privilege Level: %s\n" \
            "    Storage segment: %s\n" \
            "    Gate Type: %s\n" % \
            (self.bits,
             Selector(self.selector), self.selector,
             self.offset,
             self.type_attr,
             self.pr,
             "Ring-%d" % self.privl.ToUInt32(),
             self.s,
             GATE_TYPES.get(self.gate_type.ToUInt32(), "Invalid"))
    
def print_segment(name, base, limit):
    entries = (limit.ToUInt32() + 1) // 8
    print("%s (%s, %s) has %d entries" % (name, base, limit, entries))
    for i in xrange(entries):
        segment = t.memblock(str(base.ToUInt32() + 8 * i) + "L", 8, 1)
        if name == "IDT":
            entry = IDTEntry(segment)
        else:
            entry = GDTEntry(segment)
        if entry.pr:
            print("**** %s Entry %d ****" % (name, i))
            print("%s" % str(entry))

def print_segments():
    gdtbas = t.arch_register("gdtbas")
    gdtlim = t.arch_register("gdtlim")
    print_segment("GDT", gdtbas, gdtlim)
    idtbas = t.arch_register("idtbas")
    idtlim = t.arch_register("idtlim")
    print_segment("IDT", idtbas, idtlim)
    ldtbas = t.arch_register("ldtbas")
    ldtlim = t.arch_register("ldtlim")
    print_segment("LDT", ldtbas, ldtlim)

def print_selector(selector):
    if selector.__class__ != ipccli.bitdata.BitData:
        selector = ipccli.bitdata.BitData(16, selector)
    table = selector[2]
    idx = selector[3:15]
    base = t.arch_register("ldtbas" if table else "gdtbas")
    segment = t.memblock(str(base.ToUInt32() + 8 * idx.ToUInt32()) + "L", 8, 1)
    entry = GDTEntry(segment)
    print "**** %s:%d (%s) ****\n%s" % ("LDT" if table else "GDT", idx.ToUInt32(), selector.ToHex(), str(entry))

def segment_addr_to_linear(selector, addr):
    if type(selector) == str:
        selector = reg(selector)
    elif selector.__class__ != ipccli.bitdata.BitData:
        selector = ipccli.bitdata.BitData(16, selector)
    table = selector[2]
    idx = selector[3:15].ToUInt32()
    base = t.arch_register("ldtbas" if table else "gdtbas")
    segment = t.memblock(str(base.ToUInt32() + 8 * idx) + "L", 8, 1)
    entry = GDTEntry(segment)
    if addr < entry.limit:
        return entry.base_addr + addr
    else:
        return None

def table_to_mmio(base, limit):
    entries = (limit.ToUInt32() + 1) // 8
    mmios = []
    for i in xrange(entries):
        segment = t.memblock(str(base.ToUInt32() + 8 * i) + "L", 8, 1)
        entry = GDTEntry(segment)
        if entry.pr:
            mmios.append((entry.base_addr.ToHex(), entry.limit.ToHex()))
    print mmios

def gdt_ldt_to_mmio():
    gdtbas = t.arch_register("gdtbas")
    gdtlim = t.arch_register("gdtlim")
    table_to_mmio(gdtbas, gdtlim)
    ldtbas = t.arch_register("ldtbas")
    ldtlim = t.arch_register("ldtlim")
    table_to_mmio(ldtbas, ldtlim / 2)

    
def save_to_file(filename, cmd):
    stdout = sys.stdout
    stderr = sys.stderr
    sys.stdout = open(filename, "w")
    sys.stderr = sys.stdout
    exception = None
    try:
        cmd()
    except Exception as e:
        exception = e
    sys.stdout = stdout
    sys.stderr = stderr
    if exception:
        raise e

def dump_segments(filename):
    save_to_file(filename, print_segments)
    
def dump_ldts():
    base = t.arch_register("ldtbas")
    limit = t.arch_register("ldtlim")
    entries = (limit.ToUInt32() + 1) // 8
    for i in xrange(entries):
        segment = t.memblock(str(base.ToUInt32() + 8 * i) + "L", 8, 1)
        entry = GDTEntry(segment)
        if entry.pr:
            t.memsave("LDT-" + i + ".bin", str(entry.base.ToUInt32()) + "L")
    
