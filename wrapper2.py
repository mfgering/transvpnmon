import debugpy
import os

# 5678 is the default attach port in the VS Code debug configurations. Unless a host and port are specified, host defaults to 127.0.0.1
debugpy.listen(('192.168.1.13', 5678))
print("Waiting for debugger attach")
debugpy.wait_for_client()
debugpy.breakpoint()
print(os.system("ls /"))
print('break on this line')
