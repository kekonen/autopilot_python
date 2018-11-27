import socket
import pickle
import numpy as np

class MemoryClient:
	def __init__(self):
		self.UDP_IP = "127.0.0.1"
		self.UDP_PORT = 1337
		# self.UDP_PORT_IN  = 228


		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# self.sock.bind((self.UDP_IP, self.UDP_PORT))

		# self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


	def send(self, data):
		self.sock.sendto(pickle.dumps(data), (self.UDP_IP, self.UDP_PORT))
		# sock.sendto(message, (UDP_IP, UDP_PORT))

a = MemoryClient()

a.send(np.array([1,3,3,7]))
# ncat -v localhost 1337 -u
