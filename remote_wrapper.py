import os
import ptvsd
import socket
import transvpnmon
ptvsd.enable_attach(address = ('0.0.0.0', 8567))
 
# Enable the line of source code below only if you want the application to wait until the debugger has attached to it
print("Waiting for attach\n")
ptvsd.wait_for_attach()
 
#ptvsd.break_into_debugger()
 
print("Starting remote test\n")
transvpnmon.test()
print("Done")