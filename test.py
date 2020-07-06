import sys
import getopt
from datetime import datetime, timedelta
import jwt
import requests
from urllib3.exceptions import InsecureRequestWarning

class JwtAuth(requests.auth.AuthBase):
    """Extends requests module to do jwt auth"""
    def __call__(self, r):
        exp = datetime.utcnow() + timedelta(seconds=60)
        nbf = datetime.utcnow() - timedelta(seconds=60)

        data = {'data': 'param',
                'exp': exp,
                'iat': datetime.utcnow(),
                'nbf': nbf,
               }

        key = ''
        with open("keys/private_dev.pem", "r") as myfile:
            key = myfile.read()
        encoded_jwt = jwt.encode(data, key, algorithm='ES256')
        r.headers['Authorization'] = "Bearer " + encoded_jwt.decode('utf-8')
        return r

try:
    arguments = getopt.getopt(sys.argv[1:], "m:i:p:", ["method=", "id=", "payload="])
except getopt.error as err:
    print(err)
    sys.exit(2)

HOSTNAME = '127.0.0.1'
PORT = 5001
path = ''
method = ''
payload = ''
for arg in arguments[0]:
    if arg[0] == '-i' or arg[0] == '--id':
        task_id = arg[1]
    elif arg[0] == '-m' or arg[0] == '--method':
        path = arg[1]
    elif arg[0] == '-p' or arg[0] == '--payload':
        payload = arg[1]

headers = {'content-type': 'application/json'}
resp = None

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


if path == 'status':
    method = 'GET'
    url = f"https://{HOSTNAME}:{PORT}/{path}/{task_id}"
    resp = requests.get(url, auth=JwtAuth(), headers=headers, verify=False)
elif path == 'submit':
    method = 'POST'
    url = f"https://{HOSTNAME}:{PORT}/{path}/"
    print(f"payload: {payload}")
    print(f"url: {url}")
    resp = requests.post(url, auth=JwtAuth(), data=payload, headers=headers, verify=False)
else:
    print(f"Invalid path: '{path}'")


if resp.status_code != 200:
    print(f"{method}/{path}/{resp.status_code}")

print(resp)
print(resp.json())
