import time
from utils import *
from segments import *
from proc import *

def get_registers(thread):
    registers = []
    register_list = ["eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "esp", "eip"]
    for reg in register_list:
        registers.append((reg, thread.arch_register(reg)))
    return registers

def print_registers(thread=None):
    if thread is None:
        thread = t
        
    was_running = False
    # Halt the thread if needed
    if thread.isrunning():
        thread.halt()
        was_running = True
    registers = get_registers(thread)
    print ("Registers : ")
    for (reg, val) in registers:
        print("%s: %s" % (reg, val.ToHex()))
    if was_running:
        thread.go()

def write_asm(thread, *instructions):
    if thread.isrunning():
        thread.halt()
    entry = proc_get_address(thread, "BUP_ENTRY")
    cs = thread.arch_register("cs")
    addr = cs.ToHex() + ":%X" % entry
    thread.asm(addr, *instructions + ("jmp $", ))
    thread.arch_register("eip", entry)
    
def execute_asm(thread, *instructions):
    write_asm(thread, *instructions)
    thread.go()
    wait_until_infinite_loop(thread)

def wait_until_infinite_loop(thread, print_regs=True):
    while True:
        time.sleep(1)
        thread.halt()
        # If we don't read the registers (and I assume get a cached version of it)
        # then the thread.asm() instruction will cause it to overwrite the
        # eax, ebx and edx registers, giving us wrong values.
        get_registers(thread)
        asm = thread.asm("$")
        # Check opcode for "jmp $" infinite loop
        if asm[0].opcode == '\xeb\xfe':
            break
        thread.go()
    if print_regs:
        print_registers()

def read_pci_dev_0(thread=None):
    if thread is None:
        thread=t
    execute_asm(thread,
                "mov dx, 0xcf8",
                "mov eax, 0x80000000",
                "out dx, eax",
                "in eax, dx",
                "mov ebx, eax",
                "mov dx, 0xcfc",
                "in eax, dx",
                "mov ecx, eax")
    wait_until_infinite_loop(thread)


def v3_resume():
    try:
        t.halt()
    except:
        # Sometimes times out for no good reason, but still halts
        pass
    t.halt()
    t.arch_register("eip", 0x0003d25b)
    print("Just call : thread.go()")

def pop():
    ss = reg("ss")
    ret = t.mem(ss.ToHex() + ":" + reg("esp").ToHex(), 4)
    reg("esp", reg("esp") + 4)
    return ret

def v4_resume():
    try:
        t.halt()
    except:
        # Sometimes times out for no good reason, but still halts
        pass
    t.halt()
    reg("eip", pop())
    print("Just call : thread.go()")

def asm(addr, size=1):
    # t.asm changes the register values, so we need to save them first!
    eax = t.arch_register("eax")
    ebx = t.arch_register("ebx")
    ecx = t.arch_register("ecx")
    edx = t.arch_register("edx")
    result = t.asm(addr,size)
    t.arch_register("eax", eax)
    t.arch_register("ebx", ebx)
    t.arch_register("ecx", ecx)
    t.arch_register("edx", edx)
    
    print result
    return result
    
def step(num=1):
    t.step("branch", num)
    asm("$", 5)

def stepOver(num=1):
    instructions = asm("$", num + 1)
    goUntil(instructions[-1].address)
    
def stepToBR(num=1):
    t.brdisable()
    t.step("into", num)
    while (t.isrunning()):
        pass
    t.brenable()
    t.go()
    while (t.isrunning()):
        pass
    t.halt()
    asm("$", 5)

def goUntil(addr):
    br = t.brnew(addr)
    t.go()
    while (t.isrunning()):
        pass
    t.brremove(br)
    asm("$", 5)

def printStack():
    ss = t.arch_register("ss")
    cs = t.arch_register("cs")
    ebp = t.arch_register("ebp")
    esp = t.arch_register("esp")
    eip = t.arch_register("eip")
    while True:
        print "%s:%s (ebp: %s - local stack of %s bytes)" % (cs.ToHex(), eip.ToHex(), ebp.ToHex(), (ebp - esp).ToHex())
        try:
            try:
                asm(cs.ToHex() + ":" + eip.ToHex(), 2)
            except:
                pass
            eip = t.mem(ss.ToHex() + ":" + (ebp + 4).ToHex(), 4)
            esp = ebp + 8
            ebp = t.mem(ss.ToHex() + ":" + ebp.ToHex(), 4)
        except Exception as e:
            print "Cannot read stack further (eip:%s, ebp=%s, esp=%s)" % (eip.ToHex(), ebp.ToHex(), esp.ToHex())
            break

def printStackContent():
    ss = t.arch_register("ss")
    esp = t.arch_register("esp")
    table = ss[2]
    idx = ss[3:15]
    base = t.arch_register("ldtbas" if table else "gdtbas")
    segment = GDTEntry(t.memblock(str(base.ToUInt32() + 8 * idx.ToUInt32()) + "L", 8, 1))
    limit = segment.limit
    print("ESP : %s" % esp.ToHex())
    esp = esp & ~0xF
    t.memdump(ss.ToHex() + ":" + esp.ToHex(), limit - esp, 1)

def peek(register, offset=0, size=4, value=None):
    ds = reg("ds")
    reg_value = reg(register)
    return t.mem(ds.ToHex() + ":" + hex(reg_value + offset), size, value)

def poke(register, offset=0, value=None, size=4):
    return peek(register, offset, size, value)

def register(register_name, offset=None, value=None, size=4):
    if offset is None:
        return t.arch_register(register_name, value)
    else:
        return poke(register_name, offset, value, size)

def reg(name, value=None):
    return register(name, value=value)

    
def ebp(*args, **kwargs):
    return register("ebp", *args, **kwargs)

def force_32_bit_asmmode(did):
    return '32Bit'
ipc.devs.base.cmds._instruction_size = force_32_bit_asmmode


def reset_me():
    t.halt()
    reg("eip", proc("RESET_ME_CALL"))
    ebp = reg("ebp")
    stepOver(4)
    t.mem(ebp-8, 4, 0xd)
    t.go()
    


def reset_me_with_fuse():
    t.halt()
    # Set CSE Zeroing regiser
    t.mem("0xff:0", 4, t.mem("0xff:0", 4) | 1)
    # Lock Fuse controller
    ipc.stateport.spt_tpsb0.sbreg(4, 0, 0, 0xd5, 1, 4, 7, 0, 0x20000)
    ipc.stateport.spt_tpsb0.sbreg(4, 0, 0, 0xd5, 1, 4, 6)
    # Reset target
    t.mem("0x17:200", 4, t.mem("0x17:200", 4) | 0x41)
    #ipc.resettarget()

def escalate_to_ring0():
    t.halt()
    t.brremove()
    t.brnew("0x8:20ac0")
    execute_asm(t, "int 0x80")
