import pyaudio
import numpy as np
from scipy import interpolate, signal

class SineWave:
	def __init__(self, frequency, rate, buffer_size, ADSR, 
				 attack_curve=None, sus_height=None, partial=1):
		self.partial = partial
		self.frequency = frequency * self.partial
		self.rate = rate
		self.samps_per_period = int(self.rate / float(frequency))
		self.buffer_size = buffer_size
		self.previous_state = "on"
		self.last_end_point = -1
		self.ADSR = ADSR
		if attack_curve == None:
			self.attack_curve = self.get_attack_curve(ADSR)
		else:
			self.attack_curve = attack_curve
			self.attack_time = len(attack_curve)
		if sus_height == None:
			self.sus_height = ADSR[3]
		else:
			self.sus_height = 1.0
		self.release_curve = self.get_release_curve(ADSR)
		self.delete_all = False
		self.last_point = 0
		self.lowest_pos = None
		self.master_vol = 0.5
		
	def frequency(self, index, octave):
		numeric = (octave * 12) + index - 8
		return 440.0 * (2 ** (1.0/12.0)) ** (numeric - 49)
		
	def __float__(self):
		return self.frequency()
		
	def get_attack_curve(self, ADSR):
		attack_in_sec = (3000.0 * (ADSR[0] ** 5) + 2) / 1000.0
		decay_in_sec = (3000.0 * (ADSR[2] ** 5) + 2) / 1000.0
		self.attack_time = (attack_in_sec + decay_in_sec) * self.rate
		# attack time (in samples) includes attack and decay
		x_mid = attack_in_sec / (attack_in_sec + decay_in_sec)
		top_of_curve = dB_to_output(ADSR[1])
		sus_height = dB_to_output(ADSR[3])
		attack_x = [0.0, x_mid, 1.0]
		attack_y = [0.0, top_of_curve, sus_height]
		attack_interp = interpolate.interp1d(attack_x, attack_y, kind='slinear')
		a_factor = 1.0/self.attack_time
		return attack_interp(np.arange(self.attack_time) * a_factor)
		
	def get_release_curve(self, ADSR, start_height=None):
		release_in_sec = (3000.0 * (ADSR[4] ** 5) + 2) / 1000.0
		self.release_time = release_in_sec * self.rate
		# total release time in samples
		if start_height == None:
			sus_height = dB_to_output(ADSR[3])
		else:
			sus_height = start_height
		release_x = [0.0, 1.0]
		release_y = [sus_height, 0.0]
		release_interp = interpolate.interp1d(release_x, release_y, 
											  kind='slinear')
		r_factor = 1.0/self.release_time
		return release_interp(np.arange(self.release_time) * r_factor)
		
	def update_stuff(self, sus_height):
		pass
		#self.sus_height = sus_height
		
	def release_envelope(self, start, end, state, length, release_height):
		if self.previous_state == "on":
			self.decay_start = start
			if start < self.attack_time:
				start_height = self.attack_curve[start]
				self.release_curve = self.get_release_curve(self.ADSR, 
															start_height)
			elif release_height != None:
				if release_height > 1.0:
					release_height = 1.0
				self.release_curve = self.get_release_curve(self.ADSR,
															release_height)
		envelope_start = start - self.decay_start
		envelope_end = envelope_start + length
		if envelope_end > len(self.release_curve):
			env1 = self.release_curve[envelope_start:]
			remaining_length = length - len(env1)
			env2 = np.zeros(remaining_length)
			envelope = np.concatenate([env1, env2])
		else:
			envelope = self.release_curve[envelope_start: envelope_end]
		if envelope_start > len(self.release_curve):
			self.delete_all = True
		return envelope
		
	def get_envelope(self, start, end, state, release_height=None):
		length = self.buffer_size
		if state == "off":
			envelope = self.release_envelope(start, end, state, length, 
									     release_height)
		elif start < self.attack_time:
			# beginning sample of this chunk within the attack curve
			if end <= self.attack_time:
				envelope = self.attack_curve[start:end+1]
			elif end > self.attack_time:
				env1 = self.attack_curve[start:]
				remain_len = length - len(env1)
				env2 = np.ones(remain_len) * self.sus_height
				envelope = np.concatenate([env1, env2])
		else:
			envelope = np.ones(length) * self.sus_height
		self.previous_state = state
		return envelope
		
	def get_lookup_table(self):
		samps_per_period = int(self.rate / float(self.frequency)) # in samples
		factor = 1.0 / samps_per_period
		table = np.arange(int(self.samps_per_period)) * factor * (2 * np.pi)
		lookup_table = np.sin(table)
		return lookup_table
		
	def sine(self, state, release_height):
		length = self.buffer_size
		start = self.last_end_point + 1
		this_chunk = np.arange(start, start + length)
		new_freq = self.frequency # temporary
		if self.frequency == new_freq:
			#samps_per_period = int(self.rate / float(self.frequency))
			#print samps_per_period
			lookup_table = self.get_lookup_table()
			data = lookup_table[this_chunk % self.samps_per_period]
		#else:
		#	factor = float(self.frequency) * (2 * np.pi) / self.rate
		#	new_array = this_chunk * factor
		#	framerate = self.buffer_size / float(self.rate)
		#	t = np.linspace(self.last_point, self.last_point + framerate, 
		#					self.buffer_size)
		#	self.last_point = t[-1]
		#	data = signal.chirp(t, f0=self.frequency, t1=framerate, 
		#				 f1=new_freq, method='linear', phi=-180)
		self.last_end_point = this_chunk[-1]
		envelope = self.get_envelope(this_chunk[0], this_chunk[-1], state, 
									 release_height)
		return data * envelope

def dB_to_output(val):
	# converts value from model to actual output volume using decibels
	minimum_dB = -48.0
	dB = (1.0 - val) * minimum_dB
	output = 10 ** (dB / 20.0)
	return output

class Player:

	def __init__(self):
		p = pyaudio.PyAudio()
		self.rate = 44100
		self.threshold = 200
		# vertical threshold where the Leap Keyboard starts playing a note
		self.buffer_size = 2048
		self.leap_notes = {}
		self.leap_note_updates = {}
		self.last_positions = {}
		self.note_dictionary = {}
		self.note_dictionary_updates = {}
		self.dead_notes = []
		self.stream = p.open(format = pyaudio.paFloat32, 
							 rate = self.rate,
							 channels = 1,
							 output = True,
							 frames_per_buffer = self.buffer_size,
							 stream_callback = self.callback)
		
	def frequency(self, octave, index):
		numeric = (octave * 12) + index - 8   # needed to shift 8 to the right
		return 440.0 * (2 ** (1.0/12.0)) ** (numeric - 49)
							 
	def update_data(self, patch, leap_notes, mode):
		# updated in timerFired (in Interface) every 30ms
		self.osc_states = [patch[0][0], patch[1][0], patch[2][0], patch[3][0]]
		self.ADSR = [patch[0][1], patch[1][1], patch[2][1], patch[3][1]]
		self.master_vals = [patch[0][2], patch[1][2], patch[2][2], patch[3][2]]
		self.num_of_bars = [patch[0][3], patch[1][3], patch[2][3], patch[3][3]]
		self.bar_heights = [patch[0][4], patch[1][4], patch[2][4], patch[3][4]]
		self.leap_note_updates = leap_notes
		self.note_dictionary_updates = self.note_dictionary
		for note in self.leap_note_updates.keys():
			if ((note not in self.note_dictionary_updates) and 
				(self.leap_note_updates[note][0] == "on")):
				self.note_dictionary_updates[note] = self.create_note(note)
		for note in self.note_dictionary_updates.keys():
			if note not in self.leap_note_updates:
				del self.note_dictionary_updates[note]
		print "from update: ", self.note_dictionary.keys()
		if mode == "Leap Play":
			self.is_leap = True
		else:
			self.is_leap = False
				
	def get_leap_keys(self, leap_keys):
		# passing the leap keyboard player here for stuff n things
		self.leap_keys = leap_keys
				
	def get_fine(self, osc, fundamental):
		fine = self.master_vals[osc][0]
		new_frequency = (fundamental * (2 ** fine))
		frequency_change = new_frequency - fundamental
		return frequency_change
		
	def create_oscillator(self, octave, index, osc, fundamental, new_note, 
						  note):
		coarse = self.master_vals[osc][1] * 24
		fine = self.get_fine(osc, fundamental)
		new_fundamental = (fundamental + fine) * coarse
		ADSR = self.ADSR[osc]
		num_of_bars = self.num_of_bars[osc]
		bar_heights = self.bar_heights[osc]
		if self.is_leap:
			attack_curve, sus_height = self.get_attack_curve(note)
		for bar in range(num_of_bars):
			if bar_heights[bar] > 0.0:
				if self.is_leap:
					new_note[osc][bar] = SineWave(fundamental, self.rate, 
						self.buffer_size, ADSR, attack_curve, sus_height, 
						partial=(bar + 1))
				else:
					new_note[osc][bar] = SineWave(fundamental, self.rate, 
										  self.buffer_size, ADSR)
		return new_note[osc]
		
	def create_note(self, note):
		# creates an array of sine wave instances all organized into their 
		# corresponding slots, mapped to the finger index.
		x_val = self.leap_note_updates[note][1][0]
		octave, index = self.leap_keys.get_note_index(x_val)
		# getting the correct note assignment for the horizontal position
		fundamental = self.frequency(octave, index)
		max_bar_nums = 32
		new_note = [[None for bar in range(max_bar_nums)] for osc in 
					range(len(self.osc_states))]
		for osc in xrange(len(self.osc_states)):
			if self.osc_states[osc] == "on":
				new_note[osc] = self.create_oscillator(octave, index, osc,
												 fundamental, new_note, note)
		return new_note
		
	def get_osc_chunk(self, note, state, chunk, osc, current_note):
		this_osc_chunk = np.zeros(self.buffer_size)
		num_of_bars = self.num_of_bars[osc]
		master_vals = self.master_vals[osc]
		bar_heights = self.bar_heights[osc]
		for bar in range(num_of_bars):
			harmonic = current_note[osc][bar] # note object
			if harmonic != None:
				level = dB_to_output(bar_heights[bar])
				if ((note in self.leap_notes) and 
					(self.leap_notes[note][0] == "off")):
					actual_height = self.leap_notes[note][1]
					release_height = (abs(self.threshold-actual_height) / 
										100.0)
				else:
					release_height = None
				this_osc_chunk += (harmonic.sine(state, release_height) 
												 * level)
				if harmonic.delete_all == True:
					self.dead_notes.append(note)
		return this_osc_chunk
		
	def get_next_chunk(self, note, state):
		chunk = np.zeros(self.buffer_size)
		current_note = self.note_dictionary[note]
		for osc in range(len(self.osc_states)):
			if self.osc_states[osc] == "on":
				this_osc_chunk = self.get_osc_chunk(note, state, chunk, osc,
													current_note)
				chunk += this_osc_chunk
		return chunk
						
	def get_attack_curve(self, note):
		new_note = self.leap_note_updates[note]
		init_velocity = new_note[3]
		init_height = self.threshold - new_note[1][1]
		right_shift = 1850
		pre_scaler = 200.0
		scaler = 10.0
		if init_velocity < 0:
			init_velocity = abs(init_velocity)
		attack_time = (np.exp(-(init_velocity-right_shift)/pre_scaler))/scaler
		# exponentially decreasing attack time as the attack velocity increases
		max_height = 100.0
		if init_height > max_height:
			init_height = max_height
		y_mid = init_height/(2.0 * max_height)
		max_makeup = max_height - y_mid
		peak_velocity = 800.0  # where the attack volume has reached its peak
		if init_velocity <= peak_velocity:
			multiplier = (init_velocity / peak_velocity) ** 2
		else:
			multiplier = 1.0
		actual_makeup = (max_makeup * multiplier) / max_height
		attack_peak_vol = dB_to_output(y_mid + actual_makeup)
		end_height = init_height / max_height
		# convert to decibel_scaled output value
		x_vals = [0.0, 0.5, 1.0]
		y_vals = [0.0, attack_peak_vol, end_height]
		length = ((attack_time) * self.rate) / float(self.buffer_size) # in samples
		factor = 1.0 / length
		interp = interpolate.interp1d(x_vals, y_vals, kind='slinear')
		curve = interp(np.arange(length) * factor)
		return curve, end_height	
	
						
	def get_level_curve(self, note):
		# creates a smooth curve for changes in amplitude when playing
		# in Leap Play mode
		note_position = self.leap_notes[note][1]
		minimum_level = 0.3
		if self.leap_notes[note][0] == "on":
			dist_from_thresh = (self.threshold - note_position[1]) / 100.0
			if dist_from_thresh <= 1.0:
				# create a concave curve to rapidly increase the amplitude
				scaler = 1.0 - minimum_level
				height = (np.log10(10 * dist_from_thresh) * scaler) + minimum_level
				level = dB_to_output(height)
			else:
				level = 1.0
		else:
			level = 1.0
		if note not in self.last_positions: # what is this?
			self.last_positions[note] = level
			return level
		else:
			x_vals = [0.0, 1.0]
			y_vals = [self.last_positions[note], level]
			interp = interpolate.interp1d(x_vals, y_vals, kind='slinear')
			factor = 1.0 / self.buffer_size
			volume_curve = interp(np.arange(self.buffer_size) * factor)
			self.last_positions[note] = level
			return volume_curve
	
	def get_dead_notes(self):
		return self.dead_notes
		
	def update_notes(self):
		note_dictionary = self.note_dictionary_updates
		print self.dead_notes
		leap_notes = self.leap_note_updates
		for note in self.dead_notes:
			if note in note_dictionary:
				del note_dictionary[note]
			if note in leap_notes:
				del leap_notes[note]
		self.leap_notes = leap_notes
		self.note_dictionary = note_dictionary
		self.dead_notes = []
		
	def callback(self, in_data, frame_count, time_info, status):
		chunk = np.zeros(self.buffer_size)
		new_frequency = None
		self.update_notes()
		for note in self.note_dictionary.keys():
			state = self.leap_notes[note][0]
			note_chunk = self.get_next_chunk(note, state)
			if self.is_leap:
				#if self.note_states[note] == "on" and note in self.leap_notes:
				if self.leap_notes[note][0] == "on":
					note_level = self.get_level_curve(note)
				else:
					note_level = self.last_positions[note]
			else:
				note_level = 1.0
			chunk += note_chunk * note_level * 0.2
		data = (chunk).astype(np.float32)
		return (data, pyaudio.paContinue)
						
		