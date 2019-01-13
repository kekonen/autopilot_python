import socket
import pickle
import numpy as np
import math



# from pid import PID
# from qagent import DQNAgent
# reload(sys)
# sys.setdefaultencoding("utf-8")
# from future import unicode_literals
# fgfs --generic=socket,out,10,localhost,1337,udp,my_out_protocol --generic=socket,in,10,,1338,udp,my_in_protocol --enable-fuel-freeze
# --generic=socket,out,10,localhost,1337,udp,my_out_protocol --generic=socket,in,10,,1338,udp,my_in_protocol --prop:/sim/sound/voices/enabled=false --enable-fuel-freeze --altitude=20000 --heading=0 --pitch=-20 --prop:/controls/engines/engine/magnetos=1 --prop:/controls/engines/engine/throttle=1 --timeofday=noon
# 
# 

# maxG = 7

mse = lambda A, B, ax=0: (np.square(A - B)).mean(axis=ax)

def convert_base(num, to_base=10, from_base=10):
    # first convert to decimal number
    if isinstance(num, str):
        n = int(num, from_base)
    else:
        n = int(num)
    # now convert decimal to 'to_base' base
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if n < to_base:
        return alphabet[n]
    else:
        return convert_base(n // to_base, to_base) + alphabet[n % to_base]




class Pilot:
	def __init__(self, state_size = 24, action_size = 3, desired_pitch = 0, desired_roll = 0, desired_heading = 0, desired_altitude = 0.5):
		self.dest_latitude = 21.32525     	# 19.754154
		self.dest_longitude = -157.94319      # -156.044102

		self.desired_pitch, self.desired_roll, self.desired_heading, self.desired_altitude = desired_pitch, desired_roll, desired_heading, desired_altitude


		self.maxG = 10
		self.maxDelta_gps_altitude = 50
		self.maxGps_altitude = 27000

		self.maxPitch = 90
		self.maxRoll = 180
		self.maxGps_vertical_speed = 20000
		self.maxGps_ground_speed = 160

		self.maxAxy = 20.
		self.maxAz = 100.

		self.maxVx = 200.
		self.maxVyz = 6.
		
		self.action_size = action_size 
		self.state_size = state_size
	
	def action_state_sizes(self):
		return self.action_size, self.state_size

	def parseState(self, data):
		#                                                          GATHERING from data[]
		g = data[0] #cool
		heading = data[10] #cool
		# delta_heading = heading - self.memory[self.ithLast, 9]
		# delta_heading /= 360
		# if delta_heading >  0.5: delta_heading - 1
		# if delta_heading < -0.5: delta_heading + 1

		pitch = data[3] #cool
		roll =  data[4] #cool

		gps_vertical_speed = data[5]
		gps_ground_speed = data[9]

		# Accelerations
		a_x = data[13]
		a_y = data[14]
		a_z = data[15]

		arot_x = data[16]
		arot_y = data[17]
		arot_z = data[18]

		# Velocities
		v_x = data[19]
		v_y = data[20]
		v_z = data[21]

		vrot_x = data[22]
		vrot_y = data[23]
		vrot_z = data[24]

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


		#                                                                       NORMALIZATION
		g /= self.maxG
		# delta_g = g - self.memory[1, 0]

		# Accelerations
		a_x /= self.maxAxy
		a_y /= self.maxAxy
		a_z /= self.maxAz
		# Velocities
		v_x /= self.maxVx
		v_y /= self.maxVyz
		v_z /= self.maxVyz

		pitch /= self.maxPitch
		roll /= self.maxRoll
	
		delta_destination_heading /= 360

		gps_altitude /= self.maxGps_altitude

		gps_vertical_speed /= self.maxGps_vertical_speed
		gps_ground_speed /= self.maxGps_ground_speed

		actual_state = [g, pitch, roll, heading, gps_altitude, gps_vertical_speed, gps_ground_speed, delta_destination_heading, a_x, a_y, a_z, arot_x, arot_y, arot_z, v_x, v_y, v_z, vrot_x, vrot_y, vrot_z] # 20 , gps_latitude, gps_longitude
		target = [self.desired_pitch, self.desired_roll, self.desired_heading, self.desired_altitude] # 4
		state = np.array(actual_state + target)

		return state

	def handleOutput(self, data):

		state = self.parseState(data)

		# if self.i > 0:
		# 	print(f'{"%.2f" % g}g|atl: {"%.2f" % (gps_altitude)} |pitch: {"%.2f" % (pitch)}|roll: {"%.2f" % (roll)}|ver: {"%.2f" % (gps_vertical_speed)}|gr: {"%.2f" % (gps_ground_speed)}|head:{"%.2f" % (heading)} | gps{destination_heading}| Δhead{delta_destination_heading}') # Δx:{data[7] - self.dest_latitude},Δy:{data[8] - self.dest_longitude}        Δ"%.2f" % ((gps_altitude - self.memory[self.ithLast][0][4])/self.maxDelta_gps_altitude)


		reward = self.reward(state)
		done = False
		info = ''
		#					   \/For now always not done
		return [state, reward, done, info]

	
	def reward(self, state):

		# dif0 = s0[8]-s0[1] + s0[9]-s0[2] + s0[10]-s0[3] + s0[11]-s0[4]
		# dif1 = s1[8]-s1[1] + s1[9]-s1[2] + s1[10]-s1[3] + s1[11]-s1[4]

		# reward = dif0-dif1
		target = state[8:10]
		current = state[1:3]
		g = (state[0] - 0.1)

		# print(f'{s1[8]}-{s1[1]} + {s1[9]}-{s1[2]}')

		# np.square((1- np.square(target-current).mean())  * (1-g if g>=0 else 1+g))         [0;1]
		reward =  (           np.square((1- np.square(target-current).mean())  * (1-g if g>=0 else 1+g))          - 0.5) *10

		# print( 'r:',reward))

		# if reward>1:
		# 	return 0


		return reward




	
	
		


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


class Environment:
	def __init__(self, UDP_IP="127.0.0.1", UDP_PORT=1337, PACKAGE_SIZE=1024, delimeter= ';'):
		self.UDP_IP = UDP_IP
		self.UDP_PORT = UDP_PORT
		self.PACKAGE_SIZE = PACKAGE_SIZE

		self.delimeter = delimeter

		self.client_address = (self.UDP_IP, 1338)


		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind((self.UDP_IP, self.UDP_PORT))

		self.pilot = Pilot()


	def reset(self, relaunch = False):
		# add total recet of the environment

		data = self.receive()

		return self.pilot.handleOutput(data)[0]


	def action_state_sizes(self):
		return self.pilot.action_state_sizes()

	def end(self):
		self.sock.close()

	def receive(self):
		data = False
		while not data:
			data = self.sock.recvfrom(self.PACKAGE_SIZE)
			address = data[1]
			data = data[0]#.decode('utf8')   keep as bytes for unpickle
			# print(data)
		
		data = np.array(data.decode().strip().split(self.delimeter)).astype(np.float)

		return data

	def send(self, action): # action as an array
		action_encoded = (self.delimeter.join([str(val) for val in action]) + '\n').encode()
		self.sock.sendto(action_encoded, self.client_address)

	def step(self, action):
		self.send(action)

		# may be needed to wait, or pass some inputs in order to get relevat info
		data = self.receive()

		# state, reward, done, info = self.pilot.handleOutput(data)

		return self.pilot.handleOutput(data)



# a = Environment("127.0.0.1", 1337, 1024)

# a.serve()
# ncat -v localhost 1337 -u
# ncat -v 127.0.0.1 1337 -u
