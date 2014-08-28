#!/usr/bin/python

import select
import logging
import socket
import os
import base64

class CryptPipeClient(object):

	def __init__(self, directory):
		self.directory = directory

	def send(self, address, message):
		client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		client.connect(address)
		client.sendall('%s\n\n' % message)
		responses = self.receive(client)
		client.shutdown(socket.SHUT_RDWR)
		client.close()
		return responses

	def receive(self, sock, count=1):

		responses = []
		data = ''

		while True:
			
			[rl, wl, xl] = select.select([sock], [], [], .1) 
			for r in rl:
				buf = r.recv(4096)
				if buf:
					data += buf
					if '\n\n' in data:
						values = data.split('\n\n')
						data = values.pop()
						responses.extend(values)
				else:
					return responses

			if len(responses) >= count:
				break

		return responses[:count]

	def encrypt(self, value):
		return self.send('%s/encrypt' % self.directory, value)[0]

	def decrypt(self, value):
		return self.send('%s/decrypt' % self.directory, value)[0]
