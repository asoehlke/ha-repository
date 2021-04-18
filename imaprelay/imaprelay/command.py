"""Plug-in for filtering and forwarding emails"""
import json
import logging
import os
import stat
import sys

from relay import Relay

logging.basicConfig(
    format="%(asctime)-15s  %(levelname)-8s  %(message)s", level=logging.INFO
)

log = logging.getLogger("imaprelay")


def main():
    if "-v" in sys.argv:
        log.setLevel(logging.DEBUG)

    configfile = "data/options.json"

    st = os.stat(configfile)
    if bool(st.st_mode & (stat.S_IRGRP | stat.S_IROTH)):
        raise Exception(
            "Config file (%s) appears to be group- or "
            "world-readable. Please `chmod 400` or similar." % configfile
        )
    with open(configfile) as f:
        config = json.load(f)

    rly = Relay(config)

    rly.loop()


if __name__ == "__main__":
    main()
