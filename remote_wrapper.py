import os
import ptvsd
import socket
import transvpnmon
ptvsd.enable_attach(address = ('0.0.0.0', 8567))
 
# Enable the line of source code below only if you want the application to wait until the debugger has attached to it
#ptvsd.wait_for_attach()
ptvsd.wait_for_attach()
 
ptvsd.break_into_debugger()
 
cwd = os.getcwd()
 
print("Hello world you are here %s" % cwd )
print("On machine %s" % socket.gethostname())

transvpnmon.run()