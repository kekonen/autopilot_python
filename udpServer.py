import socket
import pickle
import numpy as np

# reload(sys)
# sys.setdefaultencoding("utf-8")
# from future import unicode_literals

# fgfs --generic=socket,out,10,localhost,1337,udp,my_protocol

class Pilot:
	def __init__(self):
		self.name = 'kek'
		# self.order = order

	def handleInput(self, inputArr):
		print(inputArr)



class MemoryServer:
	def __init__(self, UDP_IP="127.0.0.1", UDP_PORT=1337, PACKAGE_SIZE=1024):
		self.UDP_IP = UDP_IP
		self.UDP_PORT = UDP_PORT
		self.PACKAGE_SIZE = PACKAGE_SIZE
		# self.UDP_PORT_IN  = 228


		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind((self.UDP_IP, self.UDP_PORT))

		# self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.pilot = Pilot()

	def serve(self):
		while True:
			data = self.sock.recvfrom(self.PACKAGE_SIZE)
			address = data[1]
			data = data[0]#.decode('utf8')   keep as bytes for unpickle
			

			if not data:
				break


			
			# unpickled = pickle.loads(data)
			# print(unpickled)
			# answer = f'KEK: lol'
			# answer = f'KEK: {data}'

			# print('Received from:', address, data.decode())

			self.pilot.handleInput(np.array(data.decode().strip().split(';')).astype(np.float))
			# self.sock.sendto(answer.encode('utf8'), address)

		# sock.sendto(message, (UDP_IP, UDP_PORT))

a = MemoryServer("127.0.0.1", 1337, 1024)

a.serve()
# ncat -v localhost 1337 -u
