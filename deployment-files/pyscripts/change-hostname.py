#!/usr/bin/env python3

import requests
import uuid
import os
import shutil
import sys

mac_addr = hex(uuid.getnode()).replace('0x', '')

# Set Hostname #
if len(sys.argv) == 2:
    hostname = sys.argv[1]
else:
    hostname = 'PiSpot_Voucher_' + mac_addr
os.system('hostnamectl set-hostname ' + hostname)

with open("/etc/hosts", "r+") as file:
    for line in file:
        if hostname in line:
           break
    # We are at the EOF
    file.write("127.0.1.1 " + hostname + "\n")
