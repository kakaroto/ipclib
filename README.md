# IPCLib

This is more a set of functions than a library. It is meant to be used with OpenIPC's ipccli in order to access a device via DCI.

The proper way to use it is :
`from ipclib import *`

Then you can all the functions available, and you can use `t` as the variable containing the first thread of the device. The ipc object itself is available under `ipc`.

Please look at the code itself to figure out which functions are available and what they do. There is no guarantee that none of them are broken.

This code is licensed under the GPL v3 license.

The XHCI Controller code was heavily inspired by coreboot and the seabios implementation.