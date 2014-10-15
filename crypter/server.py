#!/usr/bin/python
from Crypto.Util.asn1 import DerSequence
from Crypto.PublicKey import RSA
from threading import Thread
import select
import logging
import socket
import ssl
import os
import base64

class CryptPipeServer(object):

	def __init__(self, certfile=None, keyfile=None):

		self.log = logging.getLogger(__name__)

		if certfile is not None:
			self.cert = RSA.importKey(self.extract_pubkey(open(certfile).read()))
		else:
			self.cert = None

		print self.cert

		if keyfile is not None:
			self.key = RSA.importKey(open(keyfile))
		else:
			self.key = None

		self.decpipe = None
		self.decrypter = None

		self.encpipe = None
		self.encrypter = None

	def extract_pubkey(self, x509):

		der = ssl.PEM_cert_to_DER_cert(x509)

		# Extract subjectPublicKeyInfo field from X.509 certificate (see RFC3280)
		cert = DerSequence()
		cert.decode(der)
		tbsCertificate = DerSequence()
		tbsCertificate.decode(cert[0])

		return tbsCertificate[6]

	def encrypt(self, value):

		if self.cert is None:
			raise Exception('Public key not available, encrypt not supported')

		return base64.encodestring(self.cert.encrypt(value, 0)[0]).strip()

	def decrypt(self, value):

		if self.key is None:
			raise Exception('Private key not available, decrypt not supported')

		return self.key.decrypt(base64.decodestring("%s\n" % value))

	def run(self, directory):

		if not os.path.exists(directory):
			os.makedirs(directory)

		self.encrypter = PipeMonitor('%s/encrypt' % directory, self.encrypt)
		self.encrypter.start();

		self.decrypter = PipeMonitor('%s/decrypt' % directory, self.decrypt)
		self.decrypter.start();
	
		self.log.info('Running at %s' % directory)

		try:

			while self.encrypter is not None and self.encrypter.isAlive():
				self.encrypter.join(60)

			while self.decrypter is not None and self.decrypter.isAlive():
				self.decrypter.join(60)

		except KeyboardInterrupt:
			self.log.info('Caught interrupt')
			self.stop()

	def stop(self):

		self.log.info('Shutting down')

		if self.encrypter is not None:
			self.encrypter.stop()
			self.encrypter.join()

		if self.decrypter is not None:
			self.decrypter.stop()
			self.decrypter.join()
	
class PipeMonitor(Thread):

	def __init__(self, pipe, handler):

		Thread.__init__(self)

		self.daemon = True
		self.pipe = pipe
		self.handler = handler

	def run(self):

		if os.path.exists(self.pipe):
			os.unlink(self.pipe)

		server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		server.bind(self.pipe)
		server.listen(1)

		self.running = True

		inputs = [ server ]
		data = {}

		def register(conn):
			data[conn.fileno()] = ''
			conn.setblocking(0)
			inputs.append(conn)

		def shutdown(conn):
			del data[conn.fileno()]
			inputs.remove(conn)
			conn.shutdown(socket.SHUT_RDWR)
			conn.close()

		try:

			while self.running and len(inputs):

				[rl, wl, xl] = select.select(inputs, [], [], .1)

				for r in rl:

					try:

						if r is server:

							(conn, addr) = r.accept()
							register(conn)

						else:

							buf = r.recv(4096)

							if len(buf):

								data[r.fileno()] += buf

								if '\n\n' in data[r.fileno()]:
									values = data[r.fileno()].split('\n\n');
									# Last entry will be empty string or partial value
									data[r.fileno()] = values.pop()
									for v in values:
										r.sendall('%s\n\n' % self.handler(v))

							else:

								if len(data[r.fileno()]):
									r.sendall('%s\n\n' % self.handler(data[r.fileno()]))

								shutdown(r)

					except Exception as e:
						print e
						shutdown(r)

		except Exception as e:
			print e

		server.shutdown(socket.SHUT_RDWR)
		os.unlink(self.pipe)

	def stop(self):
		self.running = False
