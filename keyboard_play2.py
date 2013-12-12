from Tkinter import *
import pyaudio
import numpy as np
import time
#import generator

class Note:
	def __init__(self, index, octave):
		self.chunk = 2048
		self.rate = 44100
		self.index = index
		self.octave = octave + 4
		self.harmonics = 1
		self.last_endpoint = 0
		self.harmonic_shape = [1.0, 0.5, 0.2, 0.125]
		
	def frequency(self):
		# this is not my formula, I borrowed it from blogger Wybiral online
		base_frequency = 16.35159783128741 * 2.0 ** (float(self.index) / 12.0)
		return base_frequency * (2.0 ** self.octave)
		
	def __float__(self):
		return self.frequency()
		
	def sine(self, frequency):
		length = self.chunk
		factor = float(frequency) * (2 * np.pi) / self.rate
		this_chunk = np.arange(self.last_endpoint+1, self.last_endpoint+length+1)
		data = np.sin(this_chunk * factor)
		self.last_endpoint = this_chunk[-1]
		return data
		
	def get_chunk(self):
		fundamental = self.frequency()
		chunk = np.zeros(self.chunk)
		for harmonic in range(1, self.harmonics+1):
			this_harm = self.sine(fundamental * float(harmonic))
			amplitude = self.harmonic_shape[harmonic-1]
			chunk += (this_harm * amplitude) * 0.25
		return chunk

class Keyboard:
	def __init__(self):
		self.pressed_keys = []
		self.keys = ['a', 'w', 's', 'e', 'd', 'f', 't', 'g', 'y', 'h', 'u', 
					 'j', 'k', 'o', 'l', 'p']
		self.current_notes = [None] * 16
		self.buffer_size = 2048
		self.rate = 44100
		p = pyaudio.PyAudio()
		self.note_dictionary = {}
		self.harmonics = 4
		self.key_press_count = 0
		self.harmonic_shape = [1.0, 0.5, 0.2, 0.125]
		self.stream = p.open(format = pyaudio.paFloat32, 
							 channels = 1,
						 	 rate = self.rate, 
						 	 output = True,
					     	 frames_per_buffer = self.buffer_size,
						 	 stream_callback = self.callback) 
						 	 # figure out where to store this guy
		self.stream.start_stream()
		
	def frequency(self, index, octave):
		# this is not my formula, I borrowed it from blogger Wybiral online
		base_frequency = 16.35159783128741 * 2.0 ** (float(index) / 12.0)
		return base_frequency * (2.0 ** octave)
		
	def __float__(self):
		return self.frequency()
		
	def update_data(self, patch):
		self.osc_states = [patch[0][0], patch[1][0], patch[2][0], patch[3][0]]
		self.ADSR = [patch[0][1], patch[1][1], patch[2][1], patch[3][1]]
		self.master_vals = [patch[0][2], patch[1][2], patch[2][2], patch[3][2]]
		self.num_of_bars = [patch[0][3], patch[1][3], patch[2][3], patch[3][3]]
		self.bar_heights = [patch[0][4], patch[1][4], patch[2][4], patch[3][4]]
		self.main_bar_heights = self.bar_heights[0]
		self.main_num_of_bars = self.num_of_bars[0]
		print self.main_num_of_bars, self.main_bar_heights
					 
	def key_tap(self, event):
		if event.keysym in self.keys and event.keysym not in self.pressed_keys:
			self.pressed_keys.append(event.keysym)
			octave, index = divmod(self.keys.index(event.keysym), 12)
			frequency = self.frequency(index, octave)
			self.note_dictionary[event.keysym] = [Note(index, octave+i) for i in range(self.harmonics)]
			empty_channel = self.current_notes.index(None)
			
	
	def key_press(self, event):
		self.key_press_count += 1
		if event.keysym in self.keys:
			self.key_press_count += 1
			if event.keysym not in self.pressed_keys:
				# only create the instance when the key is pressed, not held.
				self.pressed_keys.append(event.keysym)
				octave, index = divmod(self.keys.index(event.keysym), 12)
				frequency = self.frequency(index, octave)
				self.note_dictionary[event.keysym] = [Note(index, octave+i) for i in range(self.main_num_of_bars)]
				empty_channel = self.current_notes.index(None)
			
	def callback(self, in_data, frame_count, time_info, status):
		chunk = np.zeros(self.buffer_size)
		for key in self.note_dictionary:
			notes = self.note_dictionary[key]
			for i in range(len(notes)):
				note = self.note_dictionary[key][i]
				note_chunk = note.get_chunk() * self.main_bar_heights[i]
				chunk += note_chunk
		data = chunk.astype(np.float32)
		return (data, pyaudio.paContinue)
			
	def key_release(self, event):
		index = self.pressed_keys.index(event.keysym)
		self.pressed_keys.remove(event.keysym)
		del self.note_dictionary[event.keysym]
		print self.pressed_keys, self.note_dictionary
		
	def timerFired(self):
		# this will be taken care of by the interface
		delay = 20
		current_num = self.key_press_count
		# turn off the note I need to turn off
		self.last_num = current_num
		self.canvas.after(delay, self.timerFired)
		
	def run(self):
		root = Tk()
		self.canvas = Canvas(root, width=200, height=200)
		self.canvas.pack()
		#root.bind("<Key>", self.key_tap)
		root.bind("<KeyPress>", self.key_press)
		root.bind("<KeyRelease>", self.key_release)
		self.timerFired()
		root.mainloop()
		self.stream.stop_stream()
		self.stream.close()
	