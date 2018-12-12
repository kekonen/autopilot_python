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

		self.dest_latitude = 21.32525     	# 19.754154
		self.dest_longitude = -157.94319      # -156.044102

		# self.tick = 0
		self.rad = 0
		# self.order = order

	def handleInput(self, rawInput):
		# self.tick += 1
		# print(rawInput)
		data = np.array(rawInput.split(self.delimeter)).astype(np.float)

		g = data[0]
		heading = data[10]

		pitch = data[3]
		roll =  data[4]

		gps_vertical_speed = data[5]
		gps_ground_speed = data[9]


		# Heading
		gps_latitude = data[7]
		gps_longitude = data[8]

		delta_lat = self.dest_latitude - gps_latitude
		delta_long = self.dest_longitude - gps_longitude 
		rad = math.atan2(delta_lat, delta_long)
		gps_heading = rad * 180 / math.pi
		destination_heading = (450 - int(gps_heading)) % 360 # degrees
		delta_heading = destination_heading - heading
		# print(delta_heading)
		if delta_heading > 180: delta_heading -=360
		if delta_heading < -180: delta_heading +=360
		

		# Altitude
		gps_altitude = data[6] #feet    if want meters *=.3048

		print(f'{data[0]}g|atl: {"%.2f" % (gps_altitude)}|pitch: {"%.2f" % (pitch)}|roll: {"%.2f" % (roll)}|ver: {"%.2f" % (gps_vertical_speed)}|gr: {"%.2f" % (gps_ground_speed)}|head:{"%.2f" % (heading)} | gps{destination_heading}| Δhead{delta_heading}') # Δx:{data[7] - self.dest_latitude},Δy:{data[8] - self.dest_longitude}

		


# G                         0
# Indicated airspeed		1
# Indicated altitude ft		2
# Indicated pitch			3
# Indicated roll			4
# GPS vertical speed		5
# GPS altitude				6
# GPS latitude				7
# GPS longitude				8
# GPS ground speed			9
# Indicated heading			10
# Indicated turn rate		11
# Indicated vertical speed	12


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
