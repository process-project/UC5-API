"""Main executable for a papi instance"""
from config import CONFIG
from papi.papi import Papi
from papi.handler import Status, Submit

PAPI = Papi(CONFIG)
PAPI.add_resource(Status, '/status/<int:task_id>')
PAPI.add_resource(Submit, '/submit/')
if __name__ == '__main__':

    PAPI.app.run(use_reloader=False,
                 host=CONFIG['PAPI']['HTTP']['HOSTNAME'],
                 port=CONFIG['PAPI']['HTTP']['PORT'])
else:
    APP = PAPI.app
