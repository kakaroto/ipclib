from mmio import *
from utils import *
from segments import *
from proc import *
from asm import *

xhci_debug = debug

class Data:
    def __init__(self, size, data=0, addr=None):
        self.size = size
        self.data = ipc.BitData(size, data)
        self.addr = addr
    
    def get(self, register):
        if type(register) == int:
            offset, start, length = (register, 0, 32)
        else:
            offset, start, length = register
        if self.addr is not None:
            self.read(self.addr)
        value = self.data[offset:offset+31]
        return value[start:start+length-1]
    
    def set(self, register, value):
        if type(register) == int:
            offset, start, length = (register, 0, 32)
        else:
            offset, start, length = register
        value = ipc.BitData(length, value)
        if self.addr is not None:
            self.read(self.addr)
        self.data[offset+start:offset+start+length-1] = value
        if self.addr is not None:
            self.write(self.addr)

    def read(self, addr):
        self.data = t.memblock(phys(addr), self.size / 8, 1)
    def write(self, addr):
         t.memblock(phys(addr), self.size / 8, 1, self.data.ToRawBytes())
        
class TRB(Data):
    PTR_LOW = 0
    PTR_HIGH = 32
    STATUS = 64
    CONTROL = 96
    
    def __init__(self, data=0):
        Data.__init__(self, 128, data)

    def __repr__(self):
        return "TRB : {}\n" \
            "  PTR Low : {}\n" \
            "  PTR High: {}\n" \
            "  Status: {}\n" \
            "  Control: {}\n" \
            .format(self.data,
                    self.get(self.PTR_LOW),
                    self.get(self.PTR_HIGH),
                    self.get(self.STATUS),
                    self.get(self.CONTROL))

        
class TRBPtrBits:
    PTR = [TRB.PTR_LOW, 0, 64]
    PORT = [TRB.PTR_LOW, 24, 8]

class TRBStatusBits:
    TL = [TRB.STATUS, 0, 17] # TL - Transfer Length 
    EVTL = [TRB.STATUS, 0, 24] #  EVTL - (Event TRB) Transfer Length 
    TDS = [TRB.STATUS, 17, 5] # TDS - TD Size 
    CC = [TRB.STATUS, 24, 8] # CC - Completion Code

class TRBControlBits:
    C = [TRB.CONTROL, 0, 1] # C - Cycle Bit
    TC = [TRB.CONTROL, 1, 1] # TC - Toggle Cycle
    ENT = [TRB.CONTROL, 1, 1] # ENT - Evaluate Next TRB
    ISP = [TRB.CONTROL, 2, 1] # ISP - Interrupt-on Short Packet
    CH = [TRB.CONTROL, 4, 1] # CH - Chain Bit
    IOC = [TRB.CONTROL, 5, 1] # IOC - Interrupt On Completion
    IDT = [TRB.CONTROL, 6, 1] # IDT - Immediate Data
    DC = [TRB.CONTROL, 9, 1] # DC - Deconfigure
    TT = [TRB.CONTROL, 10, 6] # TT - TRB Type
    TRT = [TRB.CONTROL, 16, 2] # TRT - Transfer Type
    DIR = [TRB.CONTROL, 16, 1] # DIR - Direction
    EP = [TRB.CONTROL, 16, 5] # EP - Endpoint ID
    ID = [TRB.CONTROL, 24, 8] # ID - Slot ID

class TRBEnum:
    @staticmethod
    def name(value):
        types = TRBType.__dict__
        for key in types.keys():
            if key.startswith("__"):
                continue
            if types[key] == value:
                return key
        return "UNKNOWN"
    
class TRBType(TRBEnum):
    NORMAL = 1
    SETUP_STAGE = 2
    DATA_STAGE = 3
    STATUS_STAGE = 4
    LINK = 6
    EVENT_DATA = 7
    CMD_ENABLE_SLOT = 9
    CMD_DISABLE_SLOT = 10
    CMD_ADDRESS_DEV = 11
    CMD_CONFIGURE_EP = 12
    CMD_EVAL_CTX = 13
    CMD_RESET_EP = 14
    CMD_STOP_EP = 15
    CMD_SET_TR_DQ = 16
    CMD_NOOP = 23
    EV_TRANSFER = 32
    EV_CMD_CMPL = 33
    EV_PORTSC = 34
    EV_HOST = 37


class TRBCompletionCode(TRBEnum):
    SUCCESS = 1
    TRB_ERROR = 5
    STALL_ERROR = 6
    RESOURCE_ERROR = 7
    BANDWIDTH_ERROR = 8
    NO_SLOTS_AVAILABLE = 9
    SHORT_PACKET = 13
    EVENT_RING_FULL_ERROR = 21
    COMMAND_RING_STOPPED = 24
    COMMAND_ABORTED = 25
    STOPPED = 26
    STOPPED_LENGTH_INVALID = 27
    
class XHCICycleRing:
    def __init__(self, size):
        self.ring = dma_align(64, size * 0x10)
        self.size = size
        self.init()
    
    def __len__(self):
        return self.size
    def __getitem__(self, idx):
        if int(idx) > self.size:
            raise IndexError()
        return self.ring + int(idx) * 0x10

    def init(self):
        memset(self.ring, 0, self.size * 0x10)
        self.current = self.ring
        self.pcs = 1

    def clear_trb(self, trb):
        trb.set(TRB.PTR_LOW, 0)
        trb.set(TRB.PTR_HIGH, 0)
        trb.set(TRB.STATUS, 0)
        trb.set(TRB.CONTROL, 0)
        trb.set(TRBControlBits.C, not self.pcs)

    def TRB(self):
        trb = TRB()
        trb.read(self.current)
        return trb

class XHCICommandRing(XHCICycleRing):

    def init(self):
        XHCICycleRing.init(self)
        trb = TRB()
        trb.read(self[self.size - 1])
        # Set TRB Type to LINK
        trb.set(TRBControlBits.TT, TRBType.LINK)
        # Enable Toggle Cycle
        trb.set(TRBControlBits.TC, 1)
        trb.set(TRB.PTR_LOW, self.ring)
        trb.write(self[self.size - 1])
        
    def advance_enqueue_pointer(self):
        trb = TRB()
        self.current = self.current + 0x10
        trb.read(self.current)
        # Check for LINK Type
        while trb.get(TRBControlBits.TT) == TRBType.LINK:
            tc = trb.get(TRBControlBits.TC)
            trb.set(TRBControlBits.C, self.pcs)
            trb.write(self.current)
            self.current = trb.get(TRB.PTR_LOW)
            trb.read(self.current)
            if tc:
                self.pcs ^= 1
                
    def next_command_trb(self, cmd=0):
        trb = TRB()
        trb.set(TRBControlBits.C, not self.pcs)
        # Set TRB Type
        trb.set(TRBControlBits.TT, cmd)
        trb.write(self.current)
        return trb

    def post_command(self):
        trb = self.TRB()
        xhci_debug("Posting command %s" % TRBType.name(trb.get(TRBControlBits.TT)))
        # Set Cycle bit
        trb.set(TRBControlBits.C, self.pcs)
        trb.write(self.current)

        # Ring the doorbell
        xhci.bar_write32(0x3000, 0)

        self.advance_enqueue_pointer()

    def wait_for_command(self, addr, clear_event):
        cc = xhci.er.wait_for_command_done(addr, clear_event)
        if cc is not None:
            return cc
        
        xhci.bar_write32(0x98, xhci.bar_read32(0x98) | 0x6) # CS | CA
        xhci.bar_write32(0x9c, 0)

        cc = xhci.er.wait_for_command_aborted(addr)
        if xhci.bar_read32(0x98) & 8:
            xhci_debug("**FATAL**: xhci_wait_for_command: Command ring still running")
        return cc

    def noop(self):
        self.next_command_trb(TRBType.CMD_NOOP)
        cmd = self.current
        self.post_command()
        return self.wait_for_command(cmd, True)
    
    def enable_slot(self):
        self.next_command_trb(TRBType.CMD_ENABLE_SLOT)
        cmd = self.current
        self.post_command()
        cc = self.wait_for_command(cmd, False)
        if cc == TRBCompletionCode.SUCCESS:
            trb = xhci.er.TRB()
            slot_id = trb.get(TRBControlBits.ID)
            return slot_id
        return None
            
    def address_device(self, slot_id, ic):
        trb = self.next_command_trb(TRBType.CMD_ADDRESS_DEV)
        trb.set(TRBControlBits.ID, slot_id)
        trb.set(TRB.PTR_LOW, ic)
        cmd = self.current
        self.post_command()
        return self.wait_for_command(cmd, True)

class XHCIEventRing(XHCICycleRing):

    def reset(self):
        trb = TRB()
        for i in range(self.size):
            trb.read(self[i])
            trb.set(TRBControlBits.C, 0)
        self.current = self.ring
        self.pcs = 1
        
    def event_ready(self, trb):
        return trb.get(TRBControlBits.C) == self.pcs
    
    def wait_for_event(self, timeout):
        trb = self.TRB()
        while not self.event_ready(trb) and timeout > 0:
            usleep(1)
            timeout -= 1
            trb.read(self.current)
        return timeout
    
    def wait_for_event_type(self, tt, timeout):
        while True:
            timeout = self.wait_for_event(timeout)
            if timeout == 0:
                break
            trb = self.TRB()
            if trb.get(TRBControlBits.TT) == tt:
                break
            self.handle_event(trb)
        return timeout

    def advance_dequeue_pointer(self):
        self.current = self.current + 0x10
        if self.current == self.ring + self.size * 0x10:
            self.current = self.ring
        xhci.bar_write32(0x2038, self.current)
            
    def handle_event(self, trb):
        tt = trb.get(TRBControlBits.TT)
        cc = trb.get(TRBStatusBits.CC)
        xhci_debug("Received event : %s, Completion Code: %s\n%s" % (TRBType.name(tt), TRBCompletionCode.name(cc), trb))
        if tt == TRBType.EV_CMD_CMPL:
            xhci_debug("Warning: Spurious command completion event")
        elif tt == TRBType.EV_PORTSC:
            xhci_debug("Port Status Change Event for %d: %s\n" %
                       (trb.get(TRBPtrBits.PORT), TRBCompletionCode.name(cc)))
        elif tt == TRBType.EV_HOST:
            if cc == TRBCompletionCode.EVENT_RING_FULL_ERROR:
                xhci_debug("Event ring full!")
        else:
            xhci_debug("Warning: Spurious event: %s, Completion Code: %s\n" %
                       (TRBType.name(tt), TRBCompletionCode.name(cc)))
        self.advance_dequeue_pointer()
        
    def handle_events(self):
        trb = self.TRB()
        while self.event_ready(trb):
            self.handle_event(trb)
            trb.read(self.current)
        
    def wait_for_command_done(self, addr, clear_event):
        timeout = 100 * 1000 # 100ms
        cc = None
        while True:
            timeout = self.wait_for_event_type(TRBType.EV_CMD_CMPL, timeout)
            if timeout == 0:
                xhci_debug("Warning: Timed out waiting for TRB_EV_CMD_CMPL.\n")
                break
            trb = self.TRB()
            if trb.get(TRB.PTR_LOW) == addr:
                cc = trb.get(TRBStatusBits.CC)
                break
            self.handle_event(trb)
        if clear_event:
            self.advance_dequeue_pointer()
        return cc
    
    def wait_for_command_aborted(self, addr, clear_event):
        timeout = 5 * 1000 * 1000 # 5s
        cc = None
        while True:
            timeout = self.wait_for_event_type(TRBType.EV_CMD_CMPL, timeout)
            if timeout == 0:
                xhci_debug("Warning: Timed out waiting for TRB_EV_CMD_CMPL.\n")
                break
            trb = self.TRB()
            if trb.get(TRB.PTR_LOW) == addr:
                cc = trb.get(TRBStatusBits.CC)
                self.advance_dequeue_pointer()
                break
            self.handle_event(trb)

            
        while True:
            timeout = self.wait_for_event_type(TRBType.EV_CMD_CMPL, timeout)
            if timeout == 0:
                xhci_debug("Warning: Timed out waiting for COMMAND_RING_STOPPED.\n")
                break
            trb = self.TRB()
            if trb.get(TRBStatusBits.CC) == TRBCompletionCode.COMMAND_RING_STOPPED:
                self.current = trb.read(TRB.PTR_LOW)
                self.advance_dequeue_pointer()
                break
            self.handle_event(trb)

        return cc


class SlotContext(Data):
    F1 = 0
    F2 = 32
    F3 = 64
    F4 = 96
    RSVD = 128

    def __init__(self, addr=None):
        Data.__init__(self, 0x20 * 8, addr=addr)

class SlotContextBits:
    ROUTE = [SlotContext.F1, 0, 20] # ROUTE - Route String
    SPEED1 = [SlotContext.F1, 20, 4] # SPEED - Port speed plus one (compared to usb_speed enum)
    MTT = [SlotContext.F1, 25, 1] # MTT - Multi Transaction Translator
    HUB = [SlotContext.F1, 26, 1] # HUB - Is this a hub?
    CTXENT = [SlotContext.F1, 27, 5] # CTXENT - Context Entries (number of following ep contexts)
    RHPORT = [SlotContext.F2, 16, 8] # RHPORT - Root Hub Port Number
    NPORTS = [SlotContext.F2, 24, 8] # NPORTS - Number of Ports
    TTID = [SlotContext.F3, 0, 8] # TTID - TT Hub Slot ID
    TTPORT = [SlotContext.F3, 8, 8] # TTPORT - TT Port Number
    TTT = [SlotContext.F3, 16, 2] # TTT - TT Think Time
    UADDR = [SlotContext.F4, 0, 8] # UADDR - USB Device Address
    STATE = [SlotContext.F4, 27, 8] # STATE - Slot State

class EPContext(Data):
    F1 = 0
    F2 = 32
    TR_DQ_LOW = 64
    TR_DQ_HIGH = 96
    F5 = 128
    RSVD0 = 160
    RSVD1_3 = 192

    def __init__(self, addr=None):
        Data.__init__(self, 0x20 * 8, addr=addr)

class EPContextBits:
    STATE = [EPContext.F1, 0, 3] # STATE - Endpoint State
    INTVAL = [EPContext.F1, 16, 8] # INTVAL - Interval
    CERR = [EPContext.F2, 1, 2] # CERR - Error Count
    TYPE = [EPContext.F2, 3, 3] # TYPE - EP Type
    MBS = [EPContext.F2, 8, 8] # MBS - Max Burst Size
    MPS = [EPContext.F2, 16, 16] # MPS - Max Packet Size
    DCS = [EPContext.TR_DQ_LOW, 0, 1] # DCS - Dequeue Cycle State
    AVRTRB = [EPContext.F5, 0, 16] # AVRTRB - Average TRB Length
    MXESIT = [EPContext.F5, 16, 16] # MXESIT - Max ESIT Payload
    BPKTS = [EPContext.RSVD0, 0, 6] # BPKTS - packets tx in scheduled uframe
    BBM = [EPContext.RSVD0, 11, 1] # BBM - burst mode for scheduling

class XHCIEndPoint:
    def __init__(self, addr):
        self.addr = addr
        
class XHCIDevice:
    NUM_EPS=32
    def __init__(self, slot_id, addr=None):
        self.slot_id = slot_id
        if addr is None:
            addr = dma_align(64, self.NUM_EPS * 0x20, memset_value=0)
        self.ctx = addr
        self.slot = SlotContext(self.ctx)
        self.ep0 = EPContext(self.ctx + 0x20)
        self.eps = []
        for i in range(0x40, 0x40 + 0x20 * (self.NUM_EPS - 2), 0x20):
            self.eps.append(EPContext(self.ctx + i))

    def __getitem__(self, idx):
        if int(idx) > 30:
            raise IndexError()
        return self.ctx + int(idx) * 0x20

    def doorbell(self, value=0):
        xhci.bar_write32(0x3000 + 4 * self.slot_id, value)
        
class XHCIInputContext:
    NUM_EPS=32
    def __init__(self, slot_id, add_list=[], drop_list=[]):
        self.slot_id = slot_id
        self.ctx = dma_align(64, 0x20 + self.NUM_EPS * 0x20, memset_value=0)
        add = ipc.BitData(32, 0)
        drop = ipc.BitData(32, 0)
        for ep in add_list:
            add[ep] = 1
        t.mem(phys(self.ctx), 4, add)
        t.mem(phys(self.ctx + 4), 4, drop)
        self.dev = XHCIDevice(slot_id, self.ctx + 0x20)
        
class XHCI:
    def __init__(self, thread):
        self.port = proc_get_address(thread, "XHCI_PORTID")
        self.fid = proc_get_address(thread, "XHCI_PCI_DEVICE")

    def dump_pci_config(self):
        sb_mmio, _ = setup_sideband_channel(0x050400 | self.port, 0, self.fid << 3)
        t.memdump(phys(sb_mmio), 0x100, 1)
        save_mmios(pwd, [(sb_mmio, 0x1000)], "PCI_" + str(self.fid) + ".0_")
    
    def check_pci_from_ME(self):
        sb_mmio, _ = setup_sideband_channel(0x050400 | self.port, 0, self.fid << 3)
        base = t.arch_register("ldtbas")
        selector = 0
        for idx in range(128):
            segment = t.memblock(str(base.ToUInt32() + 8 * idx) + "L", 8, 1)
            entry = GDTEntry(segment)
            if entry.base_addr == sb_mmio:
                selector = idx << 3 | 0xf
                break

        execute_asm(t,
                    "mov edx, fs",
                    "mov eax, 0x%X" % selector,
                    "mov fs, eax",
                    "mov eax, 0",
                    "mov eax, fs:[eax]",
                    "mov fs, edx")
        wait_until_infinite_loop(t)
        print "Read from XHCI USB Using ME processor : %s" % reg("eax")

    def sb_read(self, rw_opcode, fid, size, offset):
        sb_channel = 1 << 28 | (rw_opcode | 1) << 16 | (rw_opcode & ~1) << 8 | self.port
        sb_mmio, _ = setup_sideband_channel(sb_channel, 0, fid << 3)
        return t.mem(phys(sb_mmio + offset), size)
    def sb_write(self, rw_opcode, fid, size, offset, value):
        sb_channel = 1 << 28 | (rw_opcode | 1) << 16 | (rw_opcode & ~1) << 8 | self.port
        sb_mmio, _ = setup_sideband_channel(sb_channel, 0, fid << 3)
        t.mem(phys(sb_mmio + offset), size, value)

    def pci_read(self, size, offset):
        return self.sb_read(4, self.fid, size, offset)
    def pci_write(self, size, offset, value):
        return self.sb_write(4, self.fid, size, offset, value)

    def pci_read32(self, offset):
        return self.pci_read(4, offset)
    def pci_read16(self, offset):
        return self.pci_read(2, offset)
    def pci_read8(self, offset):
        return self.pci_read(1, offset)
    def pci_write32(self, offset, value):
        self.pci_write(4, offset, value)
    def pci_write16(self, offset, value):
        self.pci_write(2, offset, value)   
    def pci_write8(self, offset, value):
        self.pci_write(1, offset, value)

    def bar_read(self, size, offset):
        return self.sb_read(0, self.fid, size, offset)
    def bar_write(self, size, offset, value):
        return self.sb_write(0, self.fid, size, offset, value) 

    def bar_read32(self, offset):
        return self.bar_read(4, offset)
    def bar_read16(self, offset):
        return self.bar_read(2, offset)
    def bar_read8(self, offset):
        return self.bar_read(1, offset)
    def bar_write32(self, offset, value):
        self.bar_write(4, offset, value)
    def bar_write16(self, offset, value):
        self.bar_write(2, offset, value)   
    def bar_write8(self, offset, value):
        self.bar_write(1, offset, value)
    def get(self, addr):
        return t.mem(phys(addr), 4)
    def set(self, addr, value):
        t.mem(phys(addr), 4, value)

    def status(self):
        return self.bar_read32(0x84)

    def print_status(self):
        sts = self.status()
        xhci_debug("XHCI Status : \n" \
                   "  Host Controller Error : %s\n" \
                   "  Controller Not Ready : %s\n" \
                   "  Save/Restore Error : %s\n" \
                   "  Restore State Status : %s\n" \
                   "  Save State Status : %s\n" \
                   "  Port Change Detect : %s\n" \
                   "  Event Interrupt : %s\n" \
                   "  Host System Error : %s\n" \
                   "  Host Controller Halted : %s\n" \
                   % (sts[12], sts[11], sts[10], sts[9], sts[8],
                      sts[4], sts[3], sts[2], sts[0]))

    def handshake(self, reg, mask, value, timeout=100000):
        while ((self.bar_read32(reg) & mask) != value and timeout > 0):
            usleep(1)
            timeout -= 1
        if timeout == 0:
            xhci_debug("Timeout waiting for 0x%X & 0x%X to reach 0x%X!" % (reg, mask, value))
        return timeout

    def wait_ready(self):
        xhci_debug("Waiting for controller to be ready...")
        if self.handshake(0x84, 1 << 11, 0) == 0:
            xhci_debug("Timeout!")
            return -1
        xhci_debug("OK")
        return 0

    def command(self, command, set=True):
        cmd = self.bar_read32(0x80)
        if set:
            cmd |= command
        else:
            cmd &= ~command
        self.bar_write32(0x80, cmd)

    def start(self):
        # Set Running Command
        self.command(1)
        # Check Halted Status
        if self.handshake(0x84, 1, 0):
            xhci_debug("XHCI Controller started")
    def stop(self):
        self.command(1, False)
        if self.handshake(0x84, 1, 1):
            xhci_debug("XHCI Controller stopped")
    def reset(self):
        if self.bar_read32(0x80) & 1:
            self.stop()
        self.command(2)
        xhci_debug("Resetting controller...")
        usleep(1000)
        # Check Command cleared
        if self.handshake(0x80, 2, 0):
            xhci_debug("OK")
        # Check Not Ready status
        if self.handshake(0x84, 1<<11, 0):
            xhci_debug("OK")
        
    def setup(self):
        # Enable COMMAND MEMORY and BUS MASTER 
        self.pci_write16(4, 6)
        self.reset()
        self.init()

    def init(self):
        self.page_size = self.bar_read16(0x88).ToUInt32() << 12
        self.max_slots = self.bar_read32(0x4).ToUInt32() & 0xff
        self.max_ports = (self.bar_read32(0x4).ToUInt32() & 0xff000000) >> 24
        xhci_debug("caplen:  %s" % hex(self.bar_read32(0)))
        xhci_debug("rtsoff:  %s" % hex(self.bar_read32(0x18)))
        xhci_debug("dboff:   %s" % hex(self.bar_read32(0x14)))
        xhci_debug("hciversion: %d.%d" % (self.bar_read8(0x3), self.bar_read8(0x2)))
        xhci_debug("Max Slots:   %d" % self.max_slots)
        xhci_debug("Max Ports:   %d" % self.max_ports)
        xhci_debug("Page Size:   %d" % self.page_size)

        
        # Allocate resources
        self.dcbaa = dma_align(64, (self.max_slots + 1 ) * 8, memset_value=0)
        max_sp_hi = (self.bar_read32(0x8) & 0x03E00000) >> 21
        max_sp_lo = (self.bar_read32(0x8) & 0xF8000000) >> 27
        self.max_sp_bufs = max_sp_hi << 5 | max_sp_lo
        xhci_debug("Max Scratch Pad Buffers:   %d" % self.max_sp_bufs)
        if self.max_sp_bufs:
            self.sp_ptrs = dma_align(64, self.max_sp_bufs * 8, memset_value=0)
            for i in range(self.max_sp_bufs):
                page = dma_align(self.page_size, self.page_size)
                self.set(self.sp_ptrs + i*8, page)
            self.set(self.dcbaa, self.sp_ptrs)
        self.dma_buffer = dma_align(64 * 1024, 64 * 1024)
        self.cr = XHCICommandRing(4)
        xhci_debug("command ring %s" % hex(self.cr.ring))
        self.er = XHCIEventRing(64)
        xhci_debug("event ring %s" % hex(self.er.ring))
        self.ev_ring_table = dma_align(64, 0x10, memset_value=0)
        xhci_debug("event ring table %s" % hex(self.ev_ring_table))

        # Setup hardware
        self.wait_ready()
        self.bar_write8(0xb8, self.max_slots)
        self.bar_write32(0xb0, self.dcbaa)
        self.bar_write32(0xb4, 0)

        self.bar_write32(0x98, self.cr.ring | 0x1)
        self.bar_write32(0x9c, 0)
        
        self.set(self.ev_ring_table, self.er.ring)
        self.set(self.ev_ring_table + 8, 64)
        
        self.bar_write32(0x2028, 1) # Size of evet ring table
        self.bar_write32(0x2030, self.ev_ring_table)
        self.bar_write32(0x2034, 0)
        xhci.bar_write32(0x2038, self.er.current)

        self.start()

        # Wait 20ms to stabilize
        usleep(20 * 1000)

        cc = self.cr.noop()
        running = self.bar_read32(0x98) & 8
        xhci_debug("NOOP result : %s" % TRBCompletionCode.name(cc))
        xhci_debug("Command ring is %s" % ("running" if running else "not running"))

        self.devs = [None]* self.max_ports
        self.transfer_rings = [None]* self.max_ports
        self.check_ports()
        
    def check_ports(self):
        for i in range(self.max_ports):
            portsc = self.bar_read32(0x480 + 0x10 * i)
            if portsc & 1:
                xhci_debug("Port %d has a connected device" % (i + 1))
                speed = self.hub_reset(i)
                if speed > 0:
                    self.set_address(i)

    def hub_reset(self, port):
        portsc = self.bar_read32(0x480 + 0x10 * port)
        pls = portsc[5:7]
        if pls == 0:
            # USB3 port, already reset
            xhci_debug("USB3 Port")
        elif pls == 7:
            # Initiate reset
            portsc[4] = 1
            self.bar_write32(0x480 + 0x10 *port, portsc)
        else:
            xhci_debug("Unknown port state %s" % pls)
        timeout = 100
        while True:
            portsc = self.bar_read32(0x480 + 0x10 * port)
            if portsc[0] == 0:
                xhci_debug("Disconnected while resetting")
                return -1
            if portsc[1] == 1:
                break
            timeout -= 1
            if timeout == 0:
                xhci_debug("Timeout on reset")
                return -1
            usleep(1)
        speed = portsc[10:12]
        XHCI_PORT_SPEEDS = {
            0: " - ",
            1: "Full",
            2: "Low",
            3: "High",
            4: "Super"
        }
        xhci_debug("Port %d reset. SC=%s - %s Speed" % (port + 1, portsc, XHCI_PORT_SPEEDS.get(int(speed), "Super")))
        return speed

    def gen_route(self, port):
        return ipc.BitData(20, port & 0xf)
    def set_address(self, port):
        slot_id = self.cr.enable_slot()
        if slot_id is None:
            xhci_debug("No available slots!")
            return None
        ic = XHCIInputContext(slot_id, add_list=[0, 1])
        tr = XHCICycleRing(32)
        speed = self.bar_read32(0x480 + 0x10 * port)[10:12]
        
        # Set Slot Context
        ic.dev.slot.set(SlotContextBits.ROUTE, self.gen_route(port))
        ic.dev.slot.set(SlotContextBits.SPEED1, speed+1)
        ic.dev.slot.set(SlotContextBits.CTXENT, 1)
        ic.dev.slot.set(SlotContextBits.RHPORT, port)

        # Set EP Context
        ic.dev.ep0.set(EPContext.TR_DQ_LOW, tr.ring)
        
        ic.dev.ep0.set(EPContext.TR_DQ_HIGH, 0)
        ic.dev.ep0.set(EPContextBits.TYPE, 4) # EP_CONTROL
        ic.dev.ep0.set(EPContextBits.AVRTRB, 8)
        ic.dev.ep0.set(EPContextBits.MPS, 8 if speed < 2 else (64 if speed < 4 else 512))
        ic.dev.ep0.set(EPContextBits.CERR, 3)
        ic.dev.ep0.set(EPContextBits.DCS, 1)
        
        self.devs[port] = XHCIDevice(slot_id)
        self.transfer_rings[port] = tr
        self.set(self.dcbaa + slot_id, ic.dev.ctx)
        self.cr.address_device(slot_id, ic.ctx)
        
        
try:
    xhci = XHCI(t)
except:
    pass

