from distutils.core import setup

setup(name='crypter',
	description='Encryption daemon that listens on unix domain sockets',
	long_description="""
	Encryption/decryption daemon that handles requests via unix domain sockets. The daemon
	can be run on a container host, and trusted Docker containers can mount the socket
	directory to decrypt sensitive configuration values (i.e. credentials) without
	requiring direct access to the private key.
	""",
	author='Jeremy Jongsma',
	author_email='jeremy@barchart.com',
	url='http://github.com/barchart',
	version='1.0',
	packages=['crypter'],
	scripts=['bin/crypter'],
	data_files=[
		('/etc/crypter', ['etc/crypter.cfg'])
	],
	install_requires=['pycrypto>=2.6.1'])
