#!/usr/bin/python3
import os
import hvac
import sys
from tempfile import mkstemp
from shutil import move

vault_addr = "https://secrets.your-vault.us"
role_id = os.environ['VAULT_ROLE_ID']
wrapped_secretid = sys.argv[1]

client = hvac.Client(url=vault_addr)
client.token = wrapped_secretid
secret_id = client.unwrap()['data']['secret_id']

client_auth = client.auth_approle(role_id, secret_id)
token = client_auth['auth']['client_token']

def writeEnvironment(filepath, regex, newline):
    matched_regex = False
    fh, tmp_absolute_path = mkstemp()
    with open(tmp_absolute_path, 'w') as tmp_stream:
        with open(filepath, 'r') as stream:
            for line in stream:
                if line.startswith(regex):
                    matched_regex = True
                    tmp_stream.write(regex + newline + "\n")
                else:
                    tmp_stream.write(line)
        if not matched_regex:
            tmp_stream.write(regex + newline + "\n")
    os.close(fh)
    move(tmp_absolute_path, filepath)
    os.chmod(filepath, 0o644)

writeEnvironment("/etc/profile", 'export VAULT_TOKEN=', token)
writeEnvironment("/etc/profile_systemd", 'VAULT_TOKEN=', token)
writeEnvironment("/etc/profile", 'export VAULT_ADDR=', vault_addr)
writeEnvironment("/etc/profile_systemd", 'VAULT_ADDR=', vault_addr)
