
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

This creates an ssh tunnel that can be used for vscode debugging:

```
ssh -2 -L 5678:127.0.0.1:5678 mgering@192.168.1.13
```
