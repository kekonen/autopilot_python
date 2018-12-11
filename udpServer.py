import socket
import pickle
import numpy as np
import math
# reload(sys)
# sys.setdefaultencoding("utf-8")
# from future import unicode_literals
# fgfs --generic=socket,out,10,localhost,1337,udp,my_protocol

class Pilot:
	def __init__(self, delimeter= ';'):
		self.name = 'kek'
		self.delimeter = delimeter

		self.goal_latitude = 21.32525
		self.goal_longitude = -157.94319 

		# self.tick = 0
		self.rad = 0
		# self.order = order

	def handleInput(self, rawInput):
		# self.tick += 1
		# print(rawInput)
		data = np.array(rawInput.split(self.delimeter)).astype(np.float)

		self.g = data
		self.heading = data[10]

		
		d_lat = self.goal_latitude - data[7]
		d_long = self.goal_longitude - data[8] 

		rad = math.atan2(d_lat, d_long)
		heading = rad * 180 / math.pi
		print(int(heading), (450 - int(heading)) % 360)
		gps_heading = (450 - int(heading)) % 360

		print(data[7], data[8])

		print(f'{data[0]}g|atl: {"%.2f" % (data[2]*0.3048)}:{"%.2f" % (data[6])}|head:{"%.2f" % (data[10])} | Δgps{gps_heading}') # Δx:{data[7] - self.goal_latitude},Δy:{data[8] - self.goal_longitude}

		


# G
# Indicated airspeed
# Indicated altitude ft
# Indicated pitch
# Indicated roll
# GPS vertical speed
# GPS altitude
# GPS latitude
# GPS longitude
# GPS ground speed
# Indicated heading
# Indicated turn rate
# Indicated vertical speed


class MemoryServer:
	def __init__(self, UDP_IP="127.0.0.1", UDP_PORT=1337, PACKAGE_SIZE=1024):
		self.UDP_IP = UDP_IP
		self.UDP_PORT = UDP_PORT
		self.PACKAGE_SIZE = PACKAGE_SIZE


		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind((self.UDP_IP, self.UDP_PORT))

		self.pilot = Pilot()

	def serve(self):
		while True:
			data = self.sock.recvfrom(self.PACKAGE_SIZE)
			address = data[1]
			data = data[0]#.decode('utf8')   keep as bytes for unpickle
			

			if not data:
				break

			self.pilot.handleInput(data.decode().strip())

a = MemoryServer("127.0.0.1", 1337, 1024)

a.serve()
# ncat -v localhost 1337 -u
