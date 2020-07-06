EMAIL_ACCOUNTS = {}

CONFIG = {}

LOG_FILE = "/var/log/transvpnmon.log"

try:
    LOCAL_SETTINGS
except NameError:
    try:
        from local_settings import *
    except ImportError:
        pass

