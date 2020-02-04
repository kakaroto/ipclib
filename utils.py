import ipccli
import time
import os

ipc = None

def connect():
    global ipc
    
    if ipc is None:
        ipc = ipccli.baseaccess()
    else:
        ipc.reconnect()

    return ipc

def setLogging(path=None, echo=False, logger="ipc", level="DEBUG"):
    manager = ipccli.cli_logging.getManager()
    manager.setFile(path)
    manager.echo(echo)
    manager.level(logger, level)

def usleep(us):
    time.sleep(us / 1000000.0)

def log(str):
    print(str)
    
def debug(str):
    pass
    
def genTaps(max, depth=0, max_depth=1, parent="SPT_TAP"):
    res = ""
    for i in xrange(0, max, 2):
        name = "%s_%s" % (parent, i)
        res += ('  ' * depth + '<Tap Name="%s" IrLen="8" IdcodeIr="0x0C"  VerifyProc="verify_idcode()" SerializeProc="common.tap.add_tap(0x11,%s,%s)" DeserializeProc="common.tap.remove_tap(0x11,%s,%s)" AdjustProc="common.tap.read_idcode_and_remove_if_zero()" InsertBeforeParent="false">\n' % (name, i, max, i, max))
        if depth + 1 < max_depth:
            res += genTaps(max, depth + 1, max_depth, name)
        res += ('  ' * depth + '</Tap>\n')
    return res
    # ProductInfo.xml needs this line added :
    # <TapInfo TapName="SPT_TAP.*" NodeType="Box" Stepping="$(Stepping)" AddInstanceNameSuffix="false"/>
    # Or whatever parent/prefix you use for the initial call set in TapName

def displayValidIdcodes(prefix=""):
    for d in ipc.devs:
        if d.name.startswith(prefix):
            idcode = d.idcode()
            proc_id = d.irdrscan(0x2, 32)
            if proc_id != 0:
                idcode += " (" + proc_id.ToHex() + ")"
            print("%s : %s" % (d.name, idcode))

ipc = connect()
print(ipc.devicelist)
try:
    t = ipc.threads[0]
except:
    pass

# Display hex values when using ipython
try:
    formatter = get_ipython().display_formatter.formatters['text/plain']
    formatter.for_type(int, lambda n, p, cycle: p.text("0x%X" % n))
except:
    pass

debug = log
pwd = os.path.join(os.getcwd(), "IPC_Dumps")
