#!/usr/local/bin/python3
import subprocess
import pprint

service_name = "3proxy"
cmd = ["service", service_name, "start"]
try:
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = p.communicate(timeout=8)
print("out: {}".format(stdout.decode('utf-8')))
print("err: {}".format(stderr.decode('utf-8')))
print(f"rc: {p.returncode}")
