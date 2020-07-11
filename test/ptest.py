#!/usr/local/bin/python3
import subprocess
import pprint
import logging

def service_action(service_name, action, timeout=10):
	out_str = ""
	err_str = ""
	rc = 1
	cmd = ["service", service_name, action]
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
	try:
		out_str, err_str = p.communicate(timeout=8)
		rc = p.returncode
	except subprocess.TimeoutExpired as exc:
		pass
		print("*** timeout")
		#print(f"rc: {p.returncode}\nout:{str(p.stdout.read(None))}\nerr:{str(p.stderr.read(None))}")
		pprint.pprint(exc)
	return rc, out_str, err_str

def get_tun_ip():
	out_str = ""
	err_str = ""
	rc = 1
	cmd = ["ifconfig", "tun0"]
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
	try:
		out_str, err_str = p.communicate(timeout=8)
		rc = p.returncode
	except subprocess.TimeoutExpired:
		rc = 0
	print(f"ifconfig tun0: rc: {rc} out: '{out_str}' err: '{err_str}")
	if rc != 0:
		return None
	x2 = out_str.split("inet ")
	if len(x2) < 2:
		return None
	x3 = x2[1].split(" ")
	if len(x3) < 1:
		return None
	return x3[0]

def destroy_ifaces(ifaces):
	num_destroyed = 0
	for iface in ifaces:
		out_str = ""
		err_str = ""
		rc = 1
		cmd = ["ifconfig", iface, "destroy"]
		cmd_str = " ".join(cmd)
		p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
		try:
			out_str, err_str = p.communicate(timeout=8)
			rc = p.returncode
		except subprocess.TimeoutExpired:
			rc = 0
		logging.debug(f"cmd: '{cmd_str}' rc: {rc} out: '{out_str}' err: '{err_str}'")
		if rc == 0:
			num_destroyed = num_destroyed + 1 
			logging.warning(f"{iface} destroyed")
		else:
			logging.error(f"{iface} ERROR: out: '{out_str}', err: '{err_str}'")
		return num_destroyed

logging.getLogger().setLevel(logging.DEBUG)
ifaces = ["tun33", "tun44"]
num_destroyed = destroy_ifaces(ifaces)
print(f"Destroyed {num_destroyed}")
