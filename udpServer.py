import socket
import pickle
import numpy as np
import math

from pid import PID
# reload(sys)
# sys.setdefaultencoding("utf-8")
# from future import unicode_literals
# fgfs --generic=socket,out,10,localhost,1337,udp,my_out_protocol --generic=socket,in,10,,1338,udp,my_in_protocol --enable-fuel-freeze

# maxG = 7



class Pilot:
	def __init__(self, delimeter= ';'):
		self.name = 'kek'
		self.delimeter = delimeter
		self.i = 0

		self.dest_latitude = 21.32525     	# 19.754154
		self.dest_longitude = -157.94319      # -156.044102

		self.throttle = 0
		self.aileron = 0
		self.elevator = 0
		self.rudder = 0

		self.last_heading = 0
		self.last_gps_altitude = 0

		# self.tick = 0
		self.rad = 0

		self.maxG = 10
		self.maxDelta_gps_altitude = 50
		self.maxPitch = 90
		self.maxRoll = 90
		self.maxGps_vertical_speed = 20000
		self.maxGps_ground_speed = 160

		self.rollPID = PID(0.2, 0.01, 0.5)
		# self.order = order

	def handleInput(self, rawInput):
		# self.tick += 1
		# print(rawInput)
		data = np.array(rawInput.split(self.delimeter)).astype(np.float)

		g = data[0] #cool
		heading = data[10] #cool
		delta_heading = heading - self.last_heading

		pitch = data[3] #cool
		roll =  data[4] #cool

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
		delta_destination_heading = destination_heading - heading
		# print(delta_destination_heading)
		if delta_destination_heading >  180: delta_destination_heading -=360
		if delta_destination_heading < -180: delta_destination_heading +=360

		# Altitude
		gps_altitude = data[6] #feet    if want meters *=.3048
		delta_gps_altitude = gps_altitude - self.last_gps_altitude


		# NORMALIZATION
		g /= self.maxG

		pitch /= self.maxPitch
		roll /= self.maxRoll

		delta_heading /= 360
		if delta_heading >  0.5: delta_heading - 1
		if delta_heading < -0.5: delta_heading + 1
		
		delta_destination_heading /= 360

		delta_gps_altitude /= self.maxDelta_gps_altitude

		gps_vertical_speed /= self.maxGps_vertical_speed
		gps_ground_speed /= self.maxGps_ground_speed

		

		

		print(f'{"%.2f" % g}g|atl: {"%.2f" % (gps_altitude)} Δ{"%.2f" % (delta_gps_altitude)}|pitch: {"%.2f" % (pitch)}|roll: {"%.2f" % (roll)}|ver: {"%.2f" % (gps_vertical_speed)}|gr: {"%.2f" % (gps_ground_speed)}|head:{"%.2f" % (heading)} | gps{destination_heading}| Δhead{delta_destination_heading}') # Δx:{data[7] - self.dest_latitude},Δy:{data[8] - self.dest_longitude}


		back = self.process([g, gps_altitude, delta_gps_altitude, pitch, roll, gps_vertical_speed, gps_ground_speed, heading, destination_heading, delta_destination_heading])

		self.last_heading = heading
		self.last_gps_altitude = gps_altitude

		
		return self.delimeter.join([str(val) for val in back]) + '\n'
		# data = np.array(rawInput.split(self.delimeter)).astype(np.float)


	
	def process(self, input_data):
		g, gps_altitude, delta_gps_altitude, pitch, roll, gps_vertical_speed, gps_ground_speed, heading, destination_heading, delta_destination_heading = input_data

		# throttle = 0

		self.rollPID.update(roll)
		out = self.rollPID.output
		print('o:', out)

		self.aileron += out #
		self.i+=1

		# aileron = 0
		# elevator = 0
		# rudder = 0

		return [self.aileron]

		


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

		self.client_address = (self.UDP_IP, 1338)


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

			answer = self.pilot.handleInput(data.decode().strip())
			print(answer)
			self.sock.sendto(answer.encode(), self.client_address)

a = MemoryServer("127.0.0.1", 1337, 1024)

a.serve()
# ncat -v localhost 1337 -u
