import sys
import os

activate_this = '<PATH-TO-PYTHON-ENV>/bin/activate_this.py'
with open(activate_this) as f:
    code = compile(f.read(), activate_this, 'exec')
    exec(code, dict(__file__=activate_this))

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)),'.'))
sys.path.append('<PATH-TO-SRC-DIR>')


from papi import APP as application
application.config['title'] = 'Process API'
