from distutils.core import setup

setup(name='crypter',
	description='Encryption daemon that listens on unix domain sockets',
	long_description="""
	Encryption/decryption daemon that handles requests via unix domain sockets. The daemon
	can be run on a container host, and trusted Docker containers can mount the socket
	directory to decrypt sensitive configuration values (i.e. credentials) without
	requiring direct access to the private key.

	Due to the messy state of Python encryption libraries related to S/MIME and PKCS#7,
	OpenSSL binaries are required.
	""",
	author='Jeremy Jongsma',
	author_email='jeremy@barchart.com',
	url='https://github.com/barchart/crypter',
	version='1.0.3',
	packages=['crypter'],
	scripts=['bin/crypter', 'bin/crypter-client'],
	data_files=[
		('/etc/crypter', ['etc/crypter.cfg'])
	])
