#!/usr/local/bin/python3
import subprocess
import pprint

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


tun = get_tun_ip()
print(f"tun: {tun}")
