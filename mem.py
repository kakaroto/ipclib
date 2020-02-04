from utils import *
from asm import *
from segments import *

class PDE:
    def __init__(self, offset, bits):
        # https://wiki.osdev.org/Paging
        self.offset = offset
        self.bits = bits
        self.base_addr = bits[12:31]
        self.avail = bits[9:11]
        self.glob = bits[8]
        self.size = bits[7]
        self.reserved = bits[6]
        self.accessed = bits[5]
        self.cache_disabled = bits[4]
        self.write_through = bits[3]
        self.user_supervisor = bits[2]
        self.read_write = bits[1]
        self.present = bits[0]


        

    def __str__(self):
        return "Page Directory Entry: %s\n" \
            "  Memory address : %s-%s\n" \
            "  Page-Table Base Address: %s\n" \
            "  Available for system programmer's use: %s\n" \
            "  Global page (ignored): %s\n" \
            "  Page Size: %s (%s)\n" \
            "  Reserved: %s\n" \
            "  Accessed: %s\n" \
            "  Cache Disabled: %s\n" \
            "  Write-through: %s\n" \
            "  User-Supervisor: %s\n" \
            "  Read-Write: %s\n" \
            "  Present: %s\n" % \
            (self.bits,
             hex(self.offset << 22), hex(self.offset << 22 | 0x3FFFFF),
             self.base_addr,
             self.avail,
             self.glob,
             self.size, "4MB" if self.size else "4KB",
             self.reserved,
             self.accessed,
             self.cache_disabled,
             self.write_through,
             self.user_supervisor,
             self.read_write,
             self.present)
    
class PTE(PDE):
    def __init__(self, pde, offset, bits):
        PDE.__init__(self, offset, bits)
        self.pde = pde
        self.dirty = self.reserved
        
        
    def __str__(self):
        return "Page Table Entry: %s\n" \
            "  Memory address : %s-%s\n" \
            "  Page Base Address: %s\n" \
            "  Available for system programmer's use: %s\n" \
            "  Global page: %s\n" \
            "  Reserved: %s\n" \
            "  Dirty: %s\n" \
            "  Accessed: %s\n" \
            "  Cache Disabled: %s\n" \
            "  Write-through: %s\n" \
            "  User-Supervisor: %s\n" \
            "  Read-Write: %s\n" \
            "  Present: %s\n" % \
            (self.bits,
             hex(self.pde.offset << 22 | self.offset << 12),
             hex(self.pde.offset << 22 | self.offset << 12 | 0xFFF),
             self.base_addr,
             self.avail,
             self.glob,
             self.size,
             self.dirty,
             self.accessed,
             self.cache_disabled,
             self.write_through,
             self.user_supervisor,
             self.read_write,
             self.present)

def print_memory_mapping():
    cr0 = reg("cr0")
    pd = reg("cr3")
    pse = (reg("cr4") & 0x10) == 0x10
    if cr0 & 0x80000001 != 0x80000001:
        print "Paging not Enabled"
        return
    memory = []
    for i in range(1024):
        pde = t.memblock(phys(pd + i*4), 4, 1)
        pde = PDE(i, pde)
        if pde.present:
            if pde.size == 0:
                pt = pde.base_addr << 12
                for j in range(1024):
                    pte = t.memblock(phys(pt + j*4), 4, 1)
                    pte = PTE(pde, j, pte)
                    if pte.present:
                        print(pte)
def print_pages():
    cr0 = reg("cr0")
    pd = reg("cr3")
    pse = (reg("cr4") & 0x10) == 0x10
    if cr0 & 0x80000001 != 0x80000001:
        print "Paging not Enabled"
        return
    for i in range(1024):
        pde = t.memblock(phys(pd + i*4), 4, 1)
        pde = PDE(i, pde)
        if pde.present:
            print(pde)
            if pde.size == 0:
                pt = pde.base_addr << 12
                for j in range(1024):
                    pte = t.memblock(phys(pt + j*4), 4, 1)
                    pte = PTE(pde, j, pte)
                    if pte.present:
                        print(pte)

def linear_to_pages(addr):
    addr_bits = ipc.BitData(32, addr)
    directory = addr_bits[22:31].ToUInt32()
    offset = addr_bits[0:21].ToUInt32()
    pd = reg("cr3")
    pde = t.memblock(phys(pd + directory*4), 4, 1)
    pde = PDE(directory, pde)
    if pde.present:
        if pde.size == 0:
            table = addr_bits[12:21].ToUInt32()
            offset = addr_bits[0:11].ToUInt32()
            pt = pde.base_addr << 12
            pte = t.memblock(phys(pt + table*4), 4, 1)
            pte = PTE(pde, table, pte)
            return (pde, pte, offset)

    return (pde, None, offset)
        
    
                        
def print_page_info(addr):
    (pde, pte, offset) = linear_to_pages(addr)
    if pde.present:
        if pte is not None:
            if pte.present:
                print(pte)
                print "Offset in table : %s" % hex(offset)
                print "Physical address : 0x%XP" % (pte.base_addr.ToUInt32() << 12 | offset)
                return pte
            else:
                print "Table not present"
        else:
            print(pde)
            print "Offset in table : %s" % hex(offset)
            print "Physical address : %sP" % hex(pde.base_addr.ToUInt32() << 12 | offset)
            return pde
    else:
        print "Directory not present"


def virt_to_phys(addr, selector="ds"):
    linear = segment_addr_to_linear(selector, addr)
    return linear_to_phys(linear)

def linear_to_phys(addr):
    (pde, pte, offset) = linear_to_pages(addr)
    if pte:
        if pte.present:
            return pte.base_addr.ToUInt32() << 12 | offset
        return None
    if pde.present:
        return pde.base_addr.ToUInt32() << 12 | offset
    return None
    
def dump_pages(filename):
    save_to_file(filename, print_pages)

def memdump_ds(addr, size=0x10):
    ds = reg("ds")
    return t.memdump(ds.ToHex() + ":" + hex(addr), size, 1)

def memset(addr, value, size):
    t.memblock(phys(addr), int(size), 4, value)
    #for i in range(0, size, 4):
    #    t.mem(phys(addr + i), 4, value)

def memtostr(addr, size):
    return "".join(map(chr, t.memblock(addr, size, 1).ToRawBytes()))

def phys(addr):
    return hex(addr).replace("L", "") + "P"

def malloc(size):
    malloc_func = proc_get_address(t, "SYSLIB:MALLOC")
    execute_asm(t,
                "push %s" % hex(size),
                # Need to call using register because asm uses near call and if I
                # do a far call with 'cs:addr', it pushes cs to the stack so it always
                # allocates 0x1bc bytes
                "mov eax, %s" % hex(malloc_func).replace("L", ""),
                "call eax")
    wait_until_infinite_loop(t, False)
    return reg("eax")

def malign(alignment, size):
    malign_func = proc_get_address(t, "SYSLIB:MALIGN")
    execute_asm(t,
                "push 0",
                "push %s" % hex(size),
                "push %s" % hex(alignment),
                "push 0",
                "mov eax, %s" % hex(malign_func).replace("L", ""),
                "call eax")
    wait_until_infinite_loop(t, False)
    return reg("eax")

dma_heap = None

def dma_init_heap():
    global dma_heap
    setup_att(0x20000000, 0x10000000, 0x20000000, 0x03060001)
    dma_heap = 0x20000000
    
def dma_alloc(size, memset_value=None):
    global dma_heap
    size = int(size)
    if dma_heap is None:
        dma_init_heap()
    addr = dma_heap
    dma_heap = (addr + size) & ~3
    if memset_value is not None:
        memset(addr, memset_value, size)
    return addr

def dma_align(alignment, size, memset_value=None):
    global dma_heap
    alignment = int(alignment)
    size = int(size)
    if dma_heap is None:
        dma_init_heap()
    addr = (dma_heap + alignment - 1) & ~(alignment - 1)
    dma_heap = (addr + size) & ~3
    if memset_value is not None:
        memset(addr, memset_value, size)
    return addr

def setup_att(addr, size, external, control):
    t.mem(phys(0xf00a80c0), 4, addr)
    t.mem(phys(0xf00a80c4), 4, size)
    t.mem(phys(0xf00a80c8), 4, external & 0xFFFFFFFF)
    t.mem(phys(0xf00a80cc), 4, external >> 32)
    t.mem(phys(0xf00a80d0), 4, control)

def dram(addr, size):
    att = t.memblock(phys(0xf00a8000), 0x20, 1)
    t.mem(phys(0xf00a8000), 4, 0x30000000)
    t.mem(phys(0xf00a8004), 4, (size + 0xffffff) & ~0xffffff)
    t.mem(phys(0xf00a8008), 4, addr & 0xFFFFFFFF)
    t.mem(phys(0xf00a800c), 4, addr >> 32)
    t.mem(phys(0xf00a8010), 4, 0x03060001)
    data = t.memblock(0x30000000, size, 1).ToRawBytes()
    t.memdump(phys(0x30000000), size, 1)
    t.memblock(phys(0xf00a8000), 0x20, 1, att.ToRawBytes())
    return data
