import Leap
from Leap import SwipeGesture, KeyTapGesture
import time

class leapNav:

	"""
	Add a function that scales the keyboard in a curve.  So the average 
	finger position would center the top of this curve, and the height of said 
	curve would determine the width of a key.  So if you scroll your hand over the
	keyboard, you'd get the full range of the keyboard, and where your hand was would
	zoom into those keys
	"""
	
	def __init__(self):
		self.controller = Leap.Controller()
		self.controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)
		self.mode = None
		self.minimum_time = 0.3 # 300 milliseconds
		self.minimum_vel = 0.7 
		self.total_gestures = 0
		self.five_finger_hold = 0
		self.no_fingers_hold = 0
		self.minimum_on_time = 40  # number of timerFired calls needed
		self.minimum_off_time = 70
		self.start_Y = None
		self.swipe_start_time = 0.0
		
	def get_frame(self):
		self.frame = self.controller.frame()
		
	def get_mode(self, frame, current_mode):
		finger_list = []
		if not frame.hands.is_empty:
			self.no_fingers_hold = 0
			hand = frame.hands[0]
			fingers = hand.fingers
			if len(fingers) == 5 and current_mode != "Leap Play":
				self.five_finger_hold += 1
				if self.five_finger_hold >= self.minimum_on_time:
				# turns on the leap motion keyboard, disables all other modes
					return "Leap Play"
			elif current_mode == "Leap Play":
				return "Leap Play"
			else:
				self.five_finger_hold = 0
			if len(fingers) == 1:
				return "Navigation"
			elif len(fingers) == 3:
				return "Grab"
			else:
				return None
		elif current_mode == "Leap Play":
		# if no fingers are seen for 3 seconds, the leap keyboard shuts off
			self.no_fingers_hold += 1
			if self.no_fingers_hold >= self.minimum_off_time:
				return None
				                                                                                                                                                              
	def get_all_fingers(self, frame):
		if not frame.hands.is_empty:
			hands_fingers = []
			for hand in frame.hands:
				this_hand = []
				for finger in hand.fingers:
					finger_pos = Leap.Vector()
					finger_pos += finger.tip_position
					this_hand.append((int(finger_pos[0]), int(finger_pos[1]),
									  int(finger_pos[3])))
					finger_vel = Leap.Vector()
					finger_vel += finger.tip_velocity
				hands_fingers.append(this_hand)
		return hands_fingers
		
	def get_play_fingers(self, frame):
		both_hands = get_all_fingers(frame)
		
	def get_next_cell(self, frame):
		for gesture in frame.gestures():
			self.total_gestures += 1
			if gesture.type == Leap.Gesture.TYPE_SWIPE:
				if time.time() - self.swipe_start_time > 0.7:
					self.swipe_start_time = time.time()
					self.swipe = SwipeGesture(gesture)
					if self.swipe.direction[0] > self.minimum_vel:
						return (0, 1)
					elif self.swipe.direction[0] < -self.minimum_vel:
						return (0, -1)
					elif self.swipe.direction[1] > self.minimum_vel:
						return (-1, 0)
					elif self.swipe.direction[1] < -self.minimum_vel:
						return (1, 0)
					else:
						return (0, 0)
		return (0, 0)
		
	def get_fingertip_list(self, frame):
		finger_list = []
		for finger in frame.fingers:
			finger_pos = Leap.Vector()
			finger_pos += finger.tip_position
			finger_list.append((int(finger_pos[0]), int(finger_pos[1])))
		return sorted(finger_list)
		
	def get_avg_pos(self, frame, mode):
		hand = frame.hands[0]
		fingers = hand.fingers
		fingerList = []
		for finger in fingers:
			finger_pos = Leap.Vector()
			finger_pos += finger.tip_position
			fingerList.append((int(finger_pos[0]), int(finger_pos[1])))
		if mode == "Navigation":
			return fingerList[0][0]
		elif mode == "Grab":
			return (fingerList[0][0]+fingerList[1][0]+fingerList[2][0]) / 3.0
		
	def get_current(self, frame):
		hand = frame.hands[0]
		fingers = hand.fingers
		fingerList = []
		for finger in fingers:
			finger_pos = Leap.Vector()
			finger_pos += finger.tip_position
			fingerList.append((int(finger_pos[0]), int(finger_pos[1])))
		return fingerList[0][1]
	
							
class LeapKeyboard:

	def __init__(self, controller, octave=4):
		self.controller = controller
		self.octave = octave
		self.left_edge = -230.0
		self.right_edge = 230.0
		self.play_threshold = 200.0
		self.total_width = self.right_edge - self.left_edge
		self.total_keys = 24
		self.chromatic_notes = 12
		self.lowest_y = {}
		self.previous_y = {}
		self.leap_key_width = self.total_width/float(self.total_keys)
		
	def get_note_index(self, x_val):  
		# feed the x-coord here
		x_shift = x_val + self.right_edge
		key = int(x_shift / self.leap_key_width)
		octave, index = divmod(key, self.chromatic_notes)
		octave += self.octave
		return (octave, index)
		
	def get_pressed_keys(self, frame):
		indexes_and_heights = []
		if not frame.hands.is_empty:
			for finger in frame.fingers:
				finger_pos = Leap.Vector()
				finger_pos += finger.tip_position
				index = self.get_note_index(finger_pos[0])
				y_pos = finger_pos[1]
				indexes_and_heights.append((index, y_pos))
		return indexes_and_heights
				
	def get_cur_leap_notes(self, finger, last_leap_notes, finger_pos, 
						   finger_vel, leap_notes):
		y_pos = finger_pos[1]
		index = str(finger) # reads as a finger ID number. perfect index
		if index not in last_leap_notes:
			if y_pos <= self.play_threshold:
				init_velocity = finger_vel[1]
				leap_notes[index] = ["on", finger_pos, finger_vel[0], 
									  init_velocity]
		elif last_leap_notes[index][0] == "on":
			if y_pos >= self.play_threshold or finger_vel[1] >= 450.0:
				leap_notes[index] = ["off", self.last_y_pos]
			else:
				leap_notes[index] = last_leap_notes[index]
				leap_notes[index][1:3] = finger_pos, finger_vel[0]
			self.last_y_pos = y_pos
		else:
			leap_notes[index] = last_leap_notes[index]
		return leap_notes
		
	def leap_notes(self, frame, last_leap_notes):
		leap_notes = {}
		if not frame.hands.is_empty:
			for finger in frame.fingers:
				finger_pos = Leap.Vector()
				finger_pos += finger.tip_position
				finger_vel = Leap.Vector()
				finger_vel += finger.tip_velocity
				leap_notes = self.get_cur_leap_notes(finger, last_leap_notes, 
												     finger_pos, finger_vel, 
												     leap_notes)
		missing_notes = self.get_missing_notes(last_leap_notes, leap_notes)
		if len(missing_notes) != 0:
			for note in missing_notes:
				leap_notes[note] = ["off", self.last_y_pos]
		return leap_notes
		
	def get_missing_notes(self, last_leap_notes, leap_notes):
		missing_notes = []
		for note in last_leap_notes:
			if note not in leap_notes:
				missing_notes.append(note)
		return missing_notes
							
						
							
	