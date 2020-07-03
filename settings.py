EMAIL_ACCOUNTS = {}

CONFIG = {}

try:
    LOCAL_SETTINGS
except NameError:
    try:
        from local_settings import *
    except ImportError:
        pass

