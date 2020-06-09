from setuptools import setup

req = ['Flask-RESTful', 'flask-jwt-extended', 'paramiko', 'SQLAlchemy', 'requests']

setup(
   name='papi',
   version='1.0',
   description='',
   author='Robin Loesch',
   author_email='robin@chilio.net',
   packages=['papi'],
   install_requires=req,
)
