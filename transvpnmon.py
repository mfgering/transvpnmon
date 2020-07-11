#!/usr/local/bin/python3
import argparse
import logging
import re
import smtplib
import subprocess
import time
import email
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.parser import HeaderParser

import settings

from subprocess import Popen, PIPE

logging.basicConfig(filename=settings.LOG_FILE, filemode='a',
					format='[%(asctime)s] %(message)s',
					datefmt='%Y/%d/%m %H:%M:%S',
					level=logging.INFO)

def service_action(service_name, action, timeout=10):
	out_str = ""
	err_str = ""
	rc = 1
	cmd = ["service", service_name, action]
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
	try:
		out_str, err_str = p.communicate(timeout=8)
		rc = p.returncode
	except subprocess.TimeoutExpired:
		rc = 0
	logging.debug(f"Service {service_name} {action} rc: {rc} out: '{out_str}' err: '{err_str}'")
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
	logging.debug(f"ifconfig tun0: rc: {rc} out: '{out_str}' err: '{err_str}")
	if rc != 0:
		return None
	x2 = out_str.split("inet ")
	if len(x2) < 2:
		return None
	x3 = x2[1].split(" ")
	if len(x3) < 1:
		return None
	return x3[0]

def get_tun_ifaces():
	global args

	pipe = Popen("ifconfig | grep tun", shell=True, stdout=PIPE, stderr=PIPE).stdout
	ifaces = pipe.read().decode("utf-8")

	arr = [t[1] for t in re.finditer(r'(tun\d+):', ifaces)]
	return arr

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

def status_3proxy():
	"""Return True if running, False if not."""
	(rc, _, _) = service_action("3proxy", "status")
	return True if rc == 0 else False

def start_3proxy():
	logging.info("Starting 3proxy")
	(rc, _, _) = service_action("3proxy", "start")
	return True if rc == 0 else False

def stop_3proxy():
	logging.info("Stopping 3proxy")
	(rc, _, _) = service_action("3proxy", "stop")
	return True if rc == 0 else False

def status_transmission():
	"""Return True if running, False if not."""
	(rc, _, _) = service_action("transmission", "status")
	return True if rc == 0 else False

def start_transmission():
	logging.info("Starting transmission")
	(rc, _, _) = service_action("transmission", "start")
	return True if rc == 0 else False

def stop_transmission():
	logging.info("Stopping transmission")
	(rc, _, _) = service_action("transmission", "stop")
	return True if rc == 0 else False

def status_openvpn():
	"""Return True if running, False if not."""
	(rc, _, _) = service_action("openvpn", "status")
	return True if rc == 0 else False

def start_openvpn():
	(rc, _, _) = service_action("openvpn", "status")
	return True if rc == 0 else False

def update_transmission_bind_addr(addr, settings_file='/transmission/config/settings.json', try_stop_transmission=True):
	"""Update the transmission settings and return True if changed."""
	global args

	result = False
	pattern = r'(.*bind-address-ipv4\"\s*:\s*\")(.*?)(\".*)'
	p = re.compile(pattern, re.DOTALL)
	with open(settings_file) as f:
		contents = f.read()
	m = p.match(contents)
	bind_ip = m.group(2)
	if bind_ip != addr:
		if try_stop_transmission and status_transmission():
			stop_transmission()
		updated_contents = m.group(1)+addr+m.group(3)
		with open(settings_file, 'w') as f:
			f.write(updated_contents)
			result = True
			logging.warn("Updated transmission settings for %s" % addr)
	return result

def update_3proxy_bind_addr(addr, cfg_file='/usr/local/etc/3proxy.cfg', try_stop_3proxy=True):
	"""Update the 3proxy settings and return True if changed."""
	global args

	result = False
	pattern = r'(.*external )(.*?)(\n.*)'
	p = re.compile(pattern, re.DOTALL)
	with open(cfg_file) as f:
		contents = f.read()
	m = p.match(contents)
	bind_ip = m.group(2)
	if bind_ip != addr:
		if try_stop_3proxy and status_3proxy():
			stop_3proxy()
		updated_contents = m.group(1)+addr+m.group(3)
		with open(cfg_file, 'w') as f:
			f.write(updated_contents)
			result = True
			logging.warn("Updated 3proxy settings for %s" % addr)
	return result

def check_tun_devs():
	global args

	ifaces = get_tun_ifaces()
	if len(ifaces) > 1:
		# Big problem! There should be only zero or one tun device
		logging.error(f"ERROR: There are too many ({len(ifaces)}) tun interfaces: "+
			", ".join(ifaces))
		fix_result = fix_tun_problem(ifaces)
		notify_tun_problem(ifaces, fix_result)

def notify_tun_problem(ifaces, fix_result):
	global args, config
	message = MIMEMultipart()
	message['Subject'] = 'Transmission jail interface problem.'
	msg_content = f"ERROR: There are too many ({len(ifaces)}) tun interfaces."
	if fix_result:
		msg_content += "\nThe fix worked.\n"
	else:
		msg_content += "\nThe fix FAILED.\n"
	message.attach(MIMEText(msg_content, 'text/plain'))
	send_email(message)
	
def send_email(message):
	global args, config

	email_acct = settings.EMAIL_ACCOUNTS[config['email_account']]
	message['From'] = email_acct['from_address']
	message['To'] = config['to_addr']
	try:
		conn = smtplib.SMTP_SSL(email_acct['smtp_server'])
		conn.set_debuglevel(False)
		conn.login(email_acct['smtp_user_name'], email_acct['smtp_password'])
		try:
			conn.send_message(message)
		finally:
			conn.quit()
	except Exception as exc:
		logging.error("ERROR sending message (Subject: %s): %s" % (message['Subject'], str(exc)))
		return False
	logging.info("Sent message: %s" % message['Subject'])

def fix_tun_problem(ifaces):
	global args
	result = True
	to_destroy = [ iface for iface in ifaces if iface != 'tun0']
	destroyed = destroy_ifaces(to_destroy)
	if len(to_destroy) != destroyed:
		result = False
	return result

def run():
	global args

	while True:
		logging.info("Checking...")
		check_tun_devs()
		tun_ip = get_tun_ip()
		if tun_ip is None:
			if status_transmission():
				stop_transmission()
			start_openvpn()
			# Note: check addr next iteration
		else:
			is_updated = update_transmission_bind_addr(tun_ip)
			is_updated = update_3proxy_bind_addr(tun_ip) or is_updated
			if is_updated or not status_transmission():
				start_transmission()
			if is_updated or not status_3proxy():
				start_3proxy()
		logging.info(f"Finished checking, sleeping for {settings.CHECK_INTERVAL_SECS} seconds.")
		time.sleep(settings.CHECK_INTERVAL_SECS)

def parse_options():
	parser = argparse.ArgumentParser(description="Monitor important processes")
	parser.add_argument('--debug', default=False, action='store_true')
	parser.add_argument('--verbose', default=False, action='store_true')
	parser.add_argument('--test', default=False, action='store_true')
	parser.add_argument('--config', default='default')
	parser.add_argument('--settings')
	return parser.parse_args()

def test():
	logging.getLogger().setLevel(logging.DEBUG)
	logging.info("Testing started")
	global args, config
	(rc, out, err) = service_action("3proxy", "status")
	(rc, out, err) = service_action("3proxy", "stop")
	(rc, out, err) = service_action("3proxy", "stop")
	(rc, out, err) = service_action("3proxy", "start")
	(rc, out, err) = service_action("3proxy", "start")
	(rc, out, err) = service_action("3proxy", "stop")
	logging.info("Testing ended")

if __name__ == "__main__":
	global args, config
	logging.info("Starting transvpnmon")
	try:
		args = parse_options()
		config_name = args.config
		config = settings.CONFIG[config_name]
		if args.test:
			test()
		else:
			run()
	finally:
		logging.info("Ending transvpnmon")
