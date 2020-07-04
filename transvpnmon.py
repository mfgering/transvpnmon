#!/usr/local/bin/python3

import argparse
import re
import smtplib
import time
import email
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.parser import HeaderParser

import settings

#TODO: Check for multiple tun devices
#TODO: Add email option for problems/status
#TODO: Logging?

from subprocess import Popen, PIPE

def get_tun_ip():
    global args

    if args.mock:
        return None
    pipe = Popen("ifconfig tun0", shell=True, stdout=PIPE, stderr=PIPE).stdout
    x = pipe.read().decode("utf-8")
    if len(x) == 0:
        return None
    x2 = x.split("inet ")
    if len(x2) < 2:
        return None
    x3 = x2[1].split(" ")
    if len(x3) < 1:
        return None
    return x3[0]

def get_tun_ifaces():
    global args

    pipe = Popen("ifconfig | grep tun", shell=True, stdout=PIPE, stderr=PIPE).stdout
    ifaces = pipe.read().decode("utf-8").split("\n")

    return [i[0:i.find(':')] for i in ifaces if i.find(':') >= 0]

def destroy_ifaces(ifaces):
    global args

    for iface in ifaces:
        pipe = Popen(f"ifconfig {iface} destroy", shell=True, stdout=PIPE, stderr=PIPE).stdout
        result = pipe.read().decode("utf-8")
        if args.verbose:
            if len(result) == 0:
                print(f"{iface} destroyed")
            else:
                print(f"{iface} ERROR: {result}")

def status_transmission():
    """Return True if running, False if not."""
    global args

    if args.mock:
        return True 
    p = Popen("service transmission status", shell=True, stdout=PIPE, stderr=PIPE)
    (_, _) = p.communicate()
    return True if p.returncode == 0 else False

def status_3proxy():
    """Return True if running, False if not."""
    p = Popen("service 3proxy status", shell=True, stdout=PIPE, stderr=PIPE)
    (_, _) = p.communicate()
    return True if p.returncode == 0 else False

def start_3proxy():
    global args

    if args.verbose:
        print("Starting 3proxy")
    p = Popen("service 3proxy start", shell=True, stdout=PIPE, stderr=PIPE)
    (_, _) = p.communicate()
    return p.returncode

def stop_3proxy():
    global args

    if args.verbose:
        print("Stopping 3proxy")
    p = Popen("service 3proxy stop", shell=True, stdout=PIPE, stderr=PIPE)
    (_, _) = p.communicate()
    return p.returncode

def start_transmission():
    global args

    if args.verbose:
        print("Starting transmission")
    p = Popen("service transmission start", shell=True, stdout=PIPE, stderr=PIPE)
    (_, _) = p.communicate()
    return p.returncode

def stop_transmission():
    global args

    if args.verbose:
        print("Stopping transmission")
    p = Popen("service transmission stop", shell=True, stdout=PIPE, stderr=PIPE)
    (_, _) = p.communicate()
    return p.returncode

def status_openvpn():
    """Return True if running, False if not."""
    p = Popen("service openvpn status", shell=True, stdout=PIPE, stderr=PIPE)
    (_, _) = p.communicate()
    return True if p.returncode == 0 else False

def start_openvpn():
    #NOTE: command is:
    # /usr/local/sbin/openvpn --script-security 2 --cd /usr/local/etc/openvpn --daemon openvpn --config /openvpn/default.ovpn --writepid /var/run/openvpn.pid
    global args

    if args.verbose:
        print("Starting openvpn")
    p = Popen("service openvpn start", shell=True, stdout=PIPE, stderr=PIPE)
    (_, _) = p.communicate()
    return p.returncode

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
            if args.verbose:
                print("Updated transmission settings for %s" % addr)
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
            if args.verbose:
                print("Updated 3proxy settings for %s" % addr)
    return result

def check_tun_devs():
    global args

    ifaces = get_tun_ifaces()
    if len(ifaces) > 1:
        # Big problem! There should be only zero or one tun device
        fix_result = fix_tun_problem(ifaces)
        notify_tun_problem(ifaces, fix_result)

def notify_tun_problem(ifaces, fix_result):
    global args, config
    if args.verbose:
        print(f"ERROR: There are too many ({len(ifaces)}) tun interfaces.")
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
        conn = smtplib.SMTP(email_acct['smtp_server'])
        conn.set_debuglevel(False)
        conn.login(email_acct['smtp_user_name'], email_acct['smtp_password'])
        try:
            conn.send_message(message)
        finally:
            conn.quit()
    except Exception as exc:
        print("ERROR sending message (Subject: %s): %s" % (message['Subject'], str(exc)))
        return False
    if args.verbose:
        print("Sent message: %s" % message['Subject'])

def fix_tun_problem(ifaces):
    global args
    result = True
    #TODO: Fix/delete the problem, set result False if problem
    return result

def run():
    global args

    while True:
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
        time.sleep(args.interval)

def parse_options():
    parser = argparse.ArgumentParser(description="Monitor important processes")
    parser.add_argument('--debug', default=False, action='store_true')
    parser.add_argument('--verbose', default=False, action='store_true')
    parser.add_argument('--mock', default=False, action='store_true')
    parser.add_argument('--config', default='default')
    parser.add_argument('--interval', default=30, type=int)
    parser.add_argument('--settings')
    #TODO: Read local settings file
    return parser.parse_args()

def test():
    global args, config
    #args = parse_options()
    notify_tun_problem(['tun42'], False)
    return
    #ifaces = get_tun_ifaces()
    #ifaces = ['tun1', 'tun22']
    #destroy_ifaces(ifaces)
    #run()

if __name__ == "__main__":
    global args, config
    args = parse_options()
    config_name = args.config
    config = settings.CONFIG[config_name]
    if args.mock:
        test()
    else:
        run()
