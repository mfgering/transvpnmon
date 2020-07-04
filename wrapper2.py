import debugpy
import os
import transvpnmon

# 5678 is the default attach port in the VS Code debug configurations. Unless a host and port are specified, host defaults to 127.0.0.1
debugpy.listen(('192.168.1.13', 8567))
print("Waiting for debugger attach")
debugpy.wait_for_client()
#debugpy.breakpoint()
transvpnmon.test()
print("Done")
