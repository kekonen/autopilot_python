import socket
import pickle
import numpy as np
import math
import sys
import select
from collections import deque


from pid import PID
from qagent import DQNAgent
# reload(sys)
# sys.setdefaultencoding("utf-8")
# from future import unicode_literals
# fgfs --generic=socket,out,10,localhost,1337,udp,my_out_protocol --generic=socket,in,10,,1338,udp,my_in_protocol --enable-fuel-freeze
# --generic=socket,out,10,localhost,1337,udp,my_out_protocol --generic=socket,in,10,,1338,udp,my_in_protocol --prop:/sim/sound/voices/enabled=false --enable-fuel-freeze --altitude=20000 --heading=0 --pitch=-20 --prop:/controls/engines/engine/magnetos=1 --prop:/controls/engines/engine/throttle=1
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
	def __init__(self, delimeter= ';'):
		self.name = 'kek'
		self.human_training = True
		self.delimeter = delimeter
		self.i = 0
		self.tact = 0

		self.dest_latitude = 21.32525     	# 19.754154
		self.dest_longitude = -157.94319      # -156.044102

		self.desired_pitch, self.desired_roll, self.desired_heading, self.desired_altitude = 0, 0, 0, 0.5

		self.throttle = 0
		self.aileron = 0
		self.elevator = 0
		self.rudder = 0

		self.last_heading = 0
		self.last_gps_altitude = 0

		self.last_g = 0
		self.last_pitch = 0
		self.last_roll = 0

		# self.tick = 0
		self.rad = 0

		self.maxG = 10
		self.maxDelta_gps_altitude = 50
		self.maxGps_altitude = 27000

		self.maxPitch = 90
		self.maxRoll = 180
		self.maxGps_vertical_speed = 20000
		self.maxGps_ground_speed = 160
# a, b, c, d = np.array(1, 2, 3, 4) + np.random.rand(4)/4
		self.rollPID = PID(0.2, 0.01, 0.5)
		self.headingPID = PID(-1.4, -0.3, -1)

		state_size = 12
		action_size = 7 # aileron(2), elevator(2), rudder(2), idle(1)  #9 directions * 3 throttle
		self.agent = DQNAgent(state_size, action_size)
		self.memory = deque(maxlen=5) 

		self.replay_size = 12

		self.ithLast = 0

		self.last_reward = 0

	def handleInput(self, rawInput):
		# self.tick += 1
		# print(rawInput)
		data = np.array(rawInput.split(self.delimeter)).astype(np.float)
		# print('d:',rawInput)

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
		# delta_gps_altitude = gps_altitude - self.memory[self.ithLast, 4]


		# NORMALIZATION
		g /= self.maxG
		# delta_g = g - self.memory[1, 0]


		pitch /= self.maxPitch
		roll /= self.maxRoll
	
		delta_destination_heading /= 360

		gps_altitude /= self.maxGps_altitude

		gps_vertical_speed /= self.maxGps_vertical_speed
		gps_ground_speed /= self.maxGps_ground_speed

		actual_state = [g, pitch, roll, heading, gps_altitude, gps_vertical_speed, gps_ground_speed, delta_destination_heading] # 8 , gps_latitude, gps_longitude
		target = [self.desired_pitch, self.desired_roll, self.desired_heading, self.desired_altitude] # 4
		state = np.array(actual_state + target)

		# if self.i > 0:
		# 	print(f'{"%.2f" % g}g|atl: {"%.2f" % (gps_altitude)} |pitch: {"%.2f" % (pitch)}|roll: {"%.2f" % (roll)}|ver: {"%.2f" % (gps_vertical_speed)}|gr: {"%.2f" % (gps_ground_speed)}|head:{"%.2f" % (heading)} | gps{destination_heading}| Δhead{delta_destination_heading}') # Δx:{data[7] - self.dest_latitude},Δy:{data[8] - self.dest_longitude}        Δ"%.2f" % ((gps_altitude - self.memory[self.ithLast][0][4])/self.maxDelta_gps_altitude)


		back = self.process(state)

		if back:
			return self.delimeter.join([str(val) for val in back]) + '\n'
		else:
			return False
		# data = np.array(rawInput.split(self.delimeter)).astype(np.float)

	
	def reward(self, s0, s1):

		# dif0 = s0[8]-s0[1] + s0[9]-s0[2] + s0[10]-s0[3] + s0[11]-s0[4]
		# dif1 = s1[8]-s1[1] + s1[9]-s1[2] + s1[10]-s1[3] + s1[11]-s1[4]

		# reward = dif0-dif1
		target = s1[8:10]
		current = s1[1:3]
		g = (s1[0] - 0.1)

		# print(f'{s1[8]}-{s1[1]} + {s1[9]}-{s1[2]}')
		reward =  np.square((1- np.square(target-current).mean())  * (1-g if g>=0 else 1+g)) * 10

		print( 'r:',reward , len(self.agent.memory))

		if reward>1:
			return 0


		return reward

        # des = np.array(state[10:])
        # sa = np.array(state[1:5])

        # nsa = np.array(next_state[1:5])

        # dS = mse_custom(des, sa) - mse_custom(des, nsa)

        # return dS # + last_reward*self.discount_rate_last
	
	def parseAction(self, raw_action):
		# raw_action.reshape((3,3,3,3))
		# number = raw_action.argmax() + 1
		# return np.array([int(i)-1 for i in (convert_base(raw_action, 3, 10)[::-1] + '000')[:4]]) * 0.05    CRAZY for 81 sized action
		# print(raw_action)
		if raw_action == 0:
			return np.array((0, 1, 0, 0)) * 0.05
		elif raw_action == 1:
			return np.array((0, -1, 0, 0)) * 0.05
		elif raw_action == 2:
			return np.array((0, 0, 1, 0)) * 0.05
		elif raw_action == 3:
			return np.array((0, 0, -1, 0)) * 0.05
		elif raw_action == 4:
			return np.array((0, 0, 0, 1)) * 0.05
		elif raw_action == 5:
			return np.array((0, 0, 0, -1)) * 0.05
		else:
			return np.array((0, 0, 0, 0))



	
	def process(self, state):
		# g, delta_g, gps_altitude, delta_gps_altitude, pitch, roll, delta_pitch, delta_roll, gps_vertical_speed, gps_ground_speed, heading, delta_heading, destination_heading, delta_destination_heading = input_data
		self.i+=1
		
		reward = 0
		if self.i > 4:
			# print('memory size:', len(self.memory))
			reward = self.reward(self.memory[self.ithLast][0], state)

			self.agent.remember(*self.memory[self.ithLast], reward, state)
			# self.last_reward = reward

		action = self.agent.act(state)


		


		# previous_action = self.memory[self.ithLast]
		# print(action)
		

		# print(np.array((self.throttle, self.aileron, self.elevator, self.rudder)))

		self.memory.appendleft((state, action))
		# return False
		parsed_action = self.parseAction(action)
#																			\/self.throttle
		self.throttle, self.aileron, self.elevator, self.rudder = np.array((1, self.aileron, self.elevator, self.rudder)) + parsed_action
		

		
		## throttle = 0
		# if self.tact == 0:
		# 	# Initiate act controls with random values, or actual network can be used
		# 	self.throttle, self.aileron, self.elevator, self.rudder = np.array((self.throttle, self.aileron, self.elevator, self.rudder)) + np.random.rand(4)/4
		# elif self.tact == 1:
		# 	#			  [					Δ State 1-2										   ],  [			State 2						 ],  [					Act 1-2, 2-3						 ]
		# 	self.last = [*[delta_g, delta_pitch, delta_roll,  delta_heading, delta_gps_altitude], *[g, pitch, roll, delta_destination_heading], *[self.throttle, self.aileron, self.elevator, self.rudder]]
		# elif self.tact == 2:
		# 	self.agent.remember(self.last, np.array([g, pitch, roll, delta_destination_heading]))
		# 	self.tact = -1
		
		if len(self.agent.memory) > self.replay_size:
			self.agent.replay(self.replay_size)
		
		# self.tact+=1

		return [self.throttle, self.aileron, self.elevator, self.rudder] #[]#

		


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
		True_var = True
		default_answer = ''
		while True:
			data = self.sock.recvfrom(self.PACKAGE_SIZE)
			address = data[1]
			data = data[0].decode().strip()#.decode('utf8')   keep as bytes for unpickle
			# print(data)

			if not data:
				break
			
			if data == "s":
				command = input(f"c for continue, s for Stop, h for {'off' if self.pilot.human_training else 'on'} human training: >")
				if command == 'c': continue
				if command == 'h': self.pilot.human_training != self.pilot.human_training
				if command == 's': break

			answer = self.pilot.handleInput(data)
			# print(answer)
			if answer and len(answer) > 0:
				self.sock.sendto(answer.encode(), self.client_address)

a = MemoryServer("127.0.0.1", 1337, 1024)

a.serve()
# ncat -v localhost 1337 -u
# ncat -v 127.0.0.1 1337 -u
