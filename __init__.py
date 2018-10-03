import os
import yaml

SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".msrc.yaml")


def _load_settings():
    try:
        with open(SETTINGS_FILE, "rt") as f:
            d = yaml.safe_load(f)
    except IOError:
        # If there are any errors, default to using environment variables
        # if present.
        d = {}
        for k, v in os.environ.items():
            if k.startswith("MATSTRACT_"):
                d[k] = v
    return d


SETTINGS = _load_settings()