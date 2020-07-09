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
print("try stopping")
(rc, out, err) = service_action('3proxy', 'stop')
print(f"rc: {rc}\nout: {out}\nerr: {err}")
print("try starting")
(rc, out, err) = service_action('3proxy', 'start')
print(f"rc: {rc}\nout: {out}\nerr: {err}")

