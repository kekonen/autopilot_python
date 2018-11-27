import socket
import pickle
import numpy as np

class MemoryServer:
	def __init__(self):
		self.UDP_IP = "127.0.0.1"
		self.UDP_PORT = 1337
		# self.UDP_PORT_IN  = 228


		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind((self.UDP_IP, self.UDP_PORT))

		# self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


	def serve(self):
		while True:
			data = self.sock.recvfrom(1024)
			address = data[1]
			data = data[0]#.decode('utf8')   keep as bytes for unpickle
			

			if not data:
				break
			
			unpickled = pickle.loads(data)
			print(unpickled)
			answer = f'KEK: lol'
			# answer = f'KEK: {data}'

			print('Received from:', address)
			self.sock.sendto(answer.encode('utf8'), address)

		# sock.sendto(message, (UDP_IP, UDP_PORT))

a = MemoryServer()

a.serve()
# ncat -v localhost 1337 -u
