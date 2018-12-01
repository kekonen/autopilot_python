import socket
import pickle
import numpy as np

class MemoryClient:
	def __init__(self):
		self.UDP_IP = "127.0.0.1"
		self.UDP_PORT_SERVER = 1337
		self.UDP_PORT = 1338
		self.PACKAGE_SIZE = 4096
		# self.UDP_PORT_IN  = 228


		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind((self.UDP_IP, self.UDP_PORT))

		# self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


	def send(self, data):
		self.sock.sendto(pickle.dumps(data), (self.UDP_IP, self.UDP_PORT_SERVER))
		return self.sock.recvfrom(self.PACKAGE_SIZE)
		# sock.sendto(message, (UDP_IP, UDP_PORT))

a = MemoryClient()

print(a.send(np.array([1,3,3,7])))
# print()
# ncat -v localhost 1337 -u
