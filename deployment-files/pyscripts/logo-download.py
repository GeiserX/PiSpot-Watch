#!/usr/bin/python
from minio import Minio
from minio.error import ResponseError
import pwd
import grp
import os
import sys

if len(sys.argv) > 1:
    filename_logo = sys.argv[1]
else:
    filename_logo = 'logoGPConnect.png'

try:
    client = Minio('minio.your-net.local', access_key='access-key', secret_key='secret-key', secure=False)
    client.fget_object('voucher', filename_logo, '/tmp/logo.png')
#    uid = pwd.getpwnam("gpconnect").pw_uid
#    gid = grp.getgrnam("gpconnect").gr_gid
#    os.chown('/opt/PiSpot/logoGPConnect.png', uid, gid)
except ResponseError as err:
    print(err)

# Command to update policy: ./mc admin policy add s3 ansible ansiblePolicy.json
#
# Policy in JSON:
# {"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["s3:GetBucketLocation"],"Resource":["arn:aws:s3:::voucher"]},
# {"Effect":"Allow","Action":["s3:GetObject"],"Resource":["arn:aws:s3:::voucher/*"]}]}
