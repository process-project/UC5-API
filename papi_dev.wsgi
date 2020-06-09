import sys
import os

activate_this = '<PATH-TO-PYTHON-ENV>/bin/activate_this.py'
with open(activate_this) as f:
    code = compile(f.read(), activate_this, 'exec')
    exec(code, dict(__file__=activate_this))

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)),'.'))
sys.path.append('<PATH-TO-SRC-DIR>')

from papi.papi import Papi
from papi.handler import Status, Submit
from test_config import CONFIG
PAPI = Papi(CONFIG)
PAPI.add_resource(Status, '/status/<int:task_id>')
PAPI.add_resource(Submit, '/submit/')
if __name__ == '__main__':

    PAPI.app.run(use_reloader=False,
                 host=CONFIG['PAPI']['HTTP']['HOSTNAME'],
                 port=CONFIG['PAPI']['HTTP']['PORT'])
else:
    application = PAPI.app
application.config['title'] = 'Process API'
