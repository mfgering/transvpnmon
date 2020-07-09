#!/usr/local/bin/python3
import subprocess
import pprint

def service_action(service_name, action, timeout=10):
	out_str = ""
	err_str = ""
	cmd = ["service", service_name, action]
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	try:
		stdout, stderr = p.communicate(timeout=8)
	except subprocess.TimeoutExpired:
		pass
	stdout = stdout.decode('utf-8')
	stderr = stderr.decode('utf-8')
	return stdout.decode('utf-8'), 
service_name = "3proxy"
print("out: {}".format())
print("err: {}".format(stderr.decode('utf-8')))
print(f"rc: {p.returncode}")
