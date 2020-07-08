
# Installation

## Create/Modify *local_settings.py*
The *local_settings.py* file contains sensitive information, so it is not stored in git.

## Modify *transvpnmon*
Change the command to point to the python script

Verify that the command interpreter (e.g. python3) is correct

Copy *transvpnmon* to */usr/local/etc/rc.d/*

## Edit *rc.conf*

Add/edit an entry to enable *transvpnmon*, e.g:
```
transvpnmon_enable="YES"
```

## Start the *transvpnmon* service
Start the service:
```
service transvpnmon start
```

# Additional Notes

## /etc/rc.conf

Pertinent settings in */etc/rc.conf* for other services:
```
transmission_enable="YES"
transmission_conf_dir="/transmission/config"
transmission_download_dir="/transmission/downloads"
transmission_watch_dir="/transmission/watched"
transmission_user="media"
transmission_flags="--logfile /transmission/config/transmission.log"
openvpn_enable="YES"
openvpn_configfile="/openvpn/default.ovpn"
openvpn_flags="--script-security 2"
threeproxy_enable="YES"
transvpnmon_enable="YES"
```

## Log file
Logging is controlled by the *LOG_FILE* and *LOG_LEVEL* settings. The log file defaults to */var/log/transvpnmon.log*

## Mountpoints
The *fstab* for the jail:
```
/mnt/vol1/apps/openvpn  /mnt/vol1/iocage/jails/transmission/root/openvpn        nullfs  rw      0       0
/mnt/vol1/apps/transmission/watched     /mnt/vol1/iocage/jails/transmission/root/transmission/watched   nullfs  rw      0       0
/mnt/vol1/apps/transmission/incomplete-downloads        /mnt/vol1/iocage/jails/transmission/root/transmission/incomplete-downloads      nullfs
rw      0       0
/mnt/vol1/media/downloads       /mnt/vol1/iocage/jails/transmission/root/transmission/downloads nullfs  rw      0       0
/mnt/vol1/apps/transmission/config      /mnt/vol1/iocage/jails/transmission/root/transmission/config    nullfs  rw      0       0 # Added by iocage on 2020-02-03 01:27:44
```

## SSH Tunnel for Vscode
This creates an ssh tunnel that can be used for vscode debugging:

```
ssh -2 -L 5678:127.0.0.1:5678 mgering@192.168.1.13
```
