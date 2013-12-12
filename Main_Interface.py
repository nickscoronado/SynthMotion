"""
This is the interface.  It is controllable via the Leap Motion controller, 
and can display and store most of the data required for the synthesizer.  
Currently I have a default setting written on another file that it loads as the
default patch.  Later on I'll try and add the option to save and store ones 
created by the user, and will have more presets to choose from. 

The couple things I have left to do are get it to display the current mode it's
in, and have the complete set of color configurations for when an oscillator is
off and not active.  I've written the file that will display the current 
handshapes, I just have to add in the conditionals required to create the right 
one. 

Still working on getting the keyboard engine set up.
"""

from Tkinter import *
import leap_UI
import numpy as np
import Patches
from scipy import interpolate
import math
import DrawHands
import Generator
import keyboard_play2 as keyboard  # probably gonna get rid of this

class Interface():
	def __init__(self):
		self.pallet = ['black', 'gray10', 'gray15', 'gray20', 'gray30',
					   'gray38', 'gray56', 'white', 'cyan', 'dark cyan']
		self.color_configs()
		self.osc_colors = ['orange', 'yellow', 'green', 'pink']
		self.keyboard_margin = 50
		self.pattern = [0,1,0,1,0,0,1,0,1,0,1,0,0,1,0,1,0,0,1,0,1,0,1,0]
		# kind of keys; 0=white, 1=black. pattern in chromatic order, 'c' first.
		self.white_key_width = 45
		self.black_key_width = self.white_key_width * 2 / 3
		self.half_or_full = {'half': 16, 'full': 32}
		self.leap = leap_UI.leapNav()
		self.controller = self.leap.controller
		self.player = Generator.Player()
		self.stream = self.player.stream
		self.keyboard = keyboard.Keyboard()
		self.radial_width = 80
		self.inner_margin = 5
		self.dial_init_pos = [-90, 135, 135]
		self.radial_names = ["Attack Time", "Attack Level", "Decay Time", 
							 "Sustain Level", "Release Time", "Fine", 
							 "Coarse", "Level"]
		self.tab_height = 40
		self.tab_width = 160
		self.menu_width = 200
		self.dial_name_height = 25
		self.keyboard_gap = 50
		self.keyboard_height = 200
		self.key_coords = []
		self.tab_coords = []
		self.dial_coords = []
		self.bar_coords = []
		self.button_coords = []
		self.patches = Patches.Patches()
		self.patch_parser("Default")
	
	def color_configs(self):
		self.ADSR_on = { 'box': self.pallet[5], 'outline' : self.pallet[5],
					     'polygon' : self.pallet[6], 
					     'verticals' : self.pallet[3], 
						 'graph lines' : self.pallet[8]
						 }
		self.ADSR_off = { 'box': self.pallet[3], 'outline' : self.pallet[9],
						  'polygon' : self.pallet[4], 
						  'verticals' : self.pallet[2], 
						  'graph lines' : self.pallet[6]
						  }
						  
		self.tab_selected = { 'text color' : self.pallet[0],
							  'fill color' : self.pallet[8],
							  'outline color' : self.pallet[8] 
							 }
		self.tab_on_current = {  'text color' : self.pallet[0],
								 'fill color' : self.pallet[9],
								 'outline color' : self.pallet[8] 
								}
		self.tab_off_current = { 'text color' : self.pallet[0],
								 'fill color' : self.pallet[5],
								 'outline color' : self.pallet[6]
								}
		self.tab_unselected = {  'text color' : self.pallet[9],
								 'fill color' : self.pallet[0],
								 'outline color' : self.pallet[8]
						  		}
						  		
		self.dial_on_selected = {'text box fill' : self.pallet[8],
								 'text color' : self.pallet[0], 
								 'text box outline' : self.pallet[6],
								 'dial box fill' : self.pallet[6], 
								 'dial fill' : self.pallet[5], 
								 'dial box outline' : self.pallet[7], 
								 'dial outline' : self.pallet[1],
								 'arc fill' : self.pallet[8], 
								 'arc outline' : self.pallet[9],
								 'dial line' : self.pallet[7],
								 'button fill' : self.pallet[9],
								 'button outline' : self.pallet[6]  
								 }
		self.dial_on_unselected = {'text box fill' : self.pallet[0],
								   'text color' : self.pallet[9], 
								   'text box outline' : self.pallet[6],
								   'dial box fill' : self.pallet[5], 
								   'dial fill' : self.pallet[3], 
								   'dial box outline' : self.pallet[0], 
								   'dial outline' : self.pallet[1],
								   'arc fill' : self.pallet[9], 
								   'arc outline' : self.pallet[8],
								   'dial line' : self.pallet[7],
								   'button fill' : self.pallet[7],
								   'button outline' : self.pallet[6]  
								   }
		self.dial_off_selected = {'text box fill' : self.pallet[6],
								  'text color' : self.pallet[0], 
								  'text box outline' : self.pallet[8],
								  'dial box fill' : self.pallet[5], 
								  'dial fill' : self.pallet[4], 
								  'dial box outline' : self.pallet[9], 
								  'dial outline' : self.pallet[8],
								  'arc fill' : self.pallet[6], 
								  'arc outline' : self.pallet[5],
								  'dial line' : self.pallet[7],
								  'button fill' : self.pallet[9],
								  'button outline' : self.pallet[3]  
								  }
		self.dial_off_unselected = {'text box fill' : self.pallet[0],
							 	    'text color' : self.pallet[6], 
							 	    'text box outline' : self.pallet[5],
								    'dial box fill' : self.pallet[4], 
								    'dial fill' : self.pallet[2], 
								    'dial box outline' : self.pallet[9], 
								    'dial outline' : self.pallet[1],
								    'arc fill' : self.pallet[5], 
								    'arc outline' : self.pallet[4],
								    'dial line' : self.pallet[6],
								    'button fill' : self.pallet[6],
								    'button outline' : self.pallet[9]  
								    }
		
		self.keyboard_on = { 'white key' : '#00AFAF', # this one is special
							 'black key' : self.pallet[4],
							 'key outline' : self.pallet[6],
							 'background' : self.pallet[0],
							 'white pressed' : self.pallet[8],
							 'black pressed' : self.pallet[6]
							 }
		self.keyboard_off = { 'white key' : self.pallet[4],
							  'black key' : self.pallet[2],
							  'key outline' : self.pallet[0],
							  'background' : self.pallet[0],
							  'white pressed' : self.pallet[6],
							  'black pressed' : self.pallet[4],
							  'off text' : self.pallet[9]
							  }
							
		self.bar_chart_on = { 'background' : self.pallet[3], 
							  'background outline' : self.pallet[7],
							  'selected' : [self.pallet[9], self.pallet[7],
							  				self.pallet[8]],
							  'unselected' : [self.pallet[4], self.pallet[8],
							  				  self.pallet[0]],
							  'on colors' : [self.pallet[8], self.pallet[7],
							  				   self.pallet[0]],
							  'off colors' : [self.pallet[4], self.pallet[0],
							  				  self.pallet[9]]
							  }
		self.bar_chart_off = { 'background' : self.pallet[3], 
							   'background outline' : self.pallet[7],
							   'selected' : [self.pallet[2], self.pallet[7], 
							  			     self.pallet[8]],
							   'unselected' : [self.pallet[4], self.pallet[6], 
							  				   self.pallet[9]],
							   'on colors' : [self.pallet[6], self.pallet[8],
							  		 		  self.pallet[1]],
							   'off colors' : [self.pallet[2], self.pallet[9],
							  		 		   self.pallet[6]]
							   }
		
	def patch_parser(self, patch_name):
		# this will be called for each new instantiation any time a new patch
		# is loaded.  
		patch = self.patches.load_patch(patch_name)
		self.osc_states = [patch[0][0], patch[1][0], patch[2][0], patch[3][0]]
		self.ADSR = [patch[0][1], patch[1][1], patch[2][1], patch[3][1]]
		self.master_vals = [patch[0][2], patch[1][2], patch[2][2], patch[3][2]]
		self.num_of_bars = [patch[0][3], patch[1][3], patch[2][3], patch[3][3]]
		self.bar_heights = [patch[0][4], patch[1][4], patch[2][4], patch[3][4]]
		
	def patch_packer(self):
		# this packages the current state of all the oscillators into a patch
		# for either saving or movement to another module
		patch = []
		for osc in xrange(len(self.osc_states)):
			state = self.osc_states[osc]
			ADSR = self.ADSR[osc]
			master_vals = self.master_vals[osc]
			num_of_bars = self.num_of_bars[osc]
			bar_heights = self.bar_heights[osc]
			this_osc = [state, ADSR, master_vals, num_of_bars, bar_heights]
			patch.append(this_osc)
		return patch
			
		
	def draw_mode(self):
		# this will draw a box a little above the keyboard that will display 
		# the current hand shape.  
		left_dial_edge = self.dial_coords[4][1][0]
		on_colors = [self.pallet[6], self.pallet[8]]
		off_colors = [self.pallet[4], self.pallet[2]]
		right_dial_edge = self.dial_coords[5][0][0]
		hand_top, hand_bottom = self.hand_height
		left = left_dial_edge + self.inner_margin
		right = right_dial_edge - self.inner_margin
		hand = DrawHands.Hands(self.canvas, left, hand_top, right, hand_bottom,
								on_colors, off_colors)
		if self.mode != None:
			hand.draw_hand(self.mode)
			self.last_mode = self.mode
			state = "on"
		elif self.last_mode:
			hand.draw_hand(None, last_mode = self.last_mode)
			state = "dormant"
		else:
			self.canvas.create_rectangle(left, hand_top, right, hand_bottom,
										 fill = self.pallet[2])
			state = "off"
		self.draw_mode_name(state, left, right, hand_top)
		
	def draw_mode_name(self, state, left, right, hand_top):
		if state == "on":
			colors = { 'box fill' : self.pallet[8], 'text' : self.pallet[0],
					   'box outline' : self.pallet[7]
					  }
			msg = "%s Mode" % self.mode
		elif state in ["dormant", "off"]:
			colors = {'box fill' : self.pallet[2], 'text' : self.pallet[5],
					  'box outline' : self.pallet[5]
					  }
			if state == "dormant":
				msg = "%s Mode" % self.last_mode
			else:
				msg = "Leap Motion Off"
		top = self.radials_top
		bottom = hand_top
		cx = (left + right) / 2.0
		cy = (top + bottom) / 2.0
		self.canvas.create_rectangle(left, top, right, bottom, 
									 fill = colors['box fill'],
									 outline = colors['box outline'])
		self.canvas.create_text(cx, cy, text = msg, font = "arial 12", 
								fill = colors['text'])
			
	def draw_tabs(self):
		tabs = 5
		for tab in xrange(tabs):
			left = self.menu_width + (tab * self.tab_width)
			right = left + self.tab_width
			if tab == self.selected_tab:
				colors = self.tab_selected
			elif tab == self.cur_osc:
				if self.osc_states[self.cur_osc] == "on":
					colors = self.tab_on_current
				else:
					colors = self.tab_off_current
			else:
				colors = self.tab_unselected
			self.canvas.create_rectangle(left, 0, right, self.tab_height, 
									     fill = colors['fill color'], 
										 outline = colors['outline color'],
										 width = 2)
			self.tab_coords.append([ (left, 0), (right, self.tab_height) ])
			cx = ((left + right) / 2) - (self.tab_height/2)
			cy = self.tab_height/2
			if tab < 4:
				self.draw_button(right, tab)
				name = "Oscillator %d" % (tab+1)
			else:
				name = "Effects"
			self.canvas.create_text(cx, cy, text=name, 
									fill = colors['text color'], 
									font = "verdana 12")
				
	def draw_button(self, right, tab):
		state = self.osc_states[tab]
		margin = self.inner_margin * 2.5
		width = self.tab_height - (2 * margin)
		right_edge = right - margin
		left = right_edge - width
		top = margin
		bottom = margin + width
		self.button_coords.append([ (left, top), (right_edge, bottom) ])
		if state == "on":
			color = self.osc_colors[tab]
			o_color = self.pallet[0]
		else:
			color = self.pallet[3]
			o_color = self.osc_colors[tab]
		self.canvas.create_rectangle(left, top, right_edge, bottom, fill=color,
									 outline = o_color)
	
	def draw_info(self):
		margin = self.inner_margin * 2
		box_height = 150
		title_height = 32
		left = 0 + margin
		right = self.menu_width - margin
		bottom = self.canvas_height - self.keyboard_height - margin
		top = bottom - box_height
		current_info = Patches.CELL_TO_TEXT[self.selected_cell]
		self.canvas.create_rectangle(left, top, right, bottom, 
								     fill=self.pallet[2], 
								     outline=self.pallet[9], 
								     width=2)
		self.canvas.create_rectangle(left, top, right, top+title_height, 
									 fill=self.pallet[2], 
									 outline=self.pallet[7])
		text_cy = (title_height / 2) + top
		if self.selected_cell[0] == 0 and self.selected_cell[1] < 4:
			state = self.osc_states[self.selected_cell[1]]
		title = current_info['title']
		self.canvas.create_text(left + 2*margin, text_cy, text=title, 
								anchor=W, font="arial 14", fill=self.pallet[8])
		body = current_info['msg']
		vertical_shift = (title_height * 0.20) * (len(body) / 34)
		body_cy = text_cy + title_height + vertical_shift
		self.canvas.create_text(left + margin, body_cy, text=body,
								anchor=W, font="arial 11", fill=self.pallet[8])
		
	def get_brightness(self, height):
		(min, max) = (200, 300)
		if min <= height <= max:
			return (max - height)
		elif height < min:
			return min/2
		else:
			return 0
		
	def get_white_color(self, height):
		# returns a cyan color scaling from grayish to bright depending on
		# how close to the threshold that finger is
		brightness = self.get_brightness(height)
		(blue_scalar, other_scalar) = (1.4, 0.8)
		min_other = 175
		blue_int = int(brightness * blue_scalar)
		other_int = int(brightness * other_scalar) + 175
		if blue_int >= 16:
			blue_hex_str = str(hex(blue_int))[2:] # only grabs digits
		else:
			blue_hex_str = '0' + str(hex(blue_int))[-1]
		other_hex_str = str(hex(other_int))[2:]
		return '#%s%s%s' % (blue_hex_str, other_hex_str, other_hex_str)
		
	def get_black_color(self, height):
		brightness = self.get_brightness(height)
		min = 100
		partial_int = int(brightness) + min
		hex_piece_str = str(hex(partial_int))[2:]
		return '#%s%s%s' % (hex_piece_str, hex_piece_str, hex_piece_str)
			
	def draw_key(self, margin, key, key_width, pressed_keys, colors):
		if self.last_right == 0:
			left = margin
		else:
			left = self.last_right
		key_type = self.pattern[key]
		right = left + key_width[key_type]
		if self.pattern[key] == 0:
			if key in pressed_keys:
				index = pressed_keys.index(key)
				height = self.pressed[index][1]
				key_color = self.get_white_color(height)
				#key_color = colors['white pressed']
			else:
				key_color = colors['white key']
		else: 
			if key in pressed_keys:
				index = pressed_keys.index(key)
				height = self.pressed[index][1]
				key_color = self.get_black_color(height)
				#key_color = colors['black pressed']
			else:
				key_color = colors['black key']
		self.canvas.create_rectangle(left, self.top, right, self.bottom, 
									 fill = key_color, 
									 outline = colors['key outline'])
		self.key_coords.append([ (left, self.top), (right, self.bottom) ])
		self.last_right = right
			
	def draw_keyboard(self):
		self.last_right = 0
		self.key_coords = []
		margin = self.keyboard_margin
		key_width = [self.white_key_width, self.black_key_width]
		self.top = self.canvas_height - self.keyboard_height
		self.bottom = self.canvas_height
		if self.keyboard_on_off == 0:
			colors = self.keyboard_off
		else:
			colors = self.keyboard_on
		self.canvas.create_rectangle(0, self.top, margin, self.bottom, 
									 fill = colors['background'])
		pressed_keys = [self.pressed[i][0] for i in range(len(self.pressed))]
		# just the key number
		for key in xrange(len(self.pattern)):
			self.draw_key(margin, key, key_width, pressed_keys, colors)
		right = self.last_right
		self.canvas.create_rectangle(right, self.top, self.canvas_width, 
									 self.bottom, fill = colors['background'])
		if self.keyboard_on_off == 0:
			self.draw_keyboard_off_text(margin, colors)
									
	def draw_keyboard_off_text(self, margin, colors):
		cx = (self.canvas_width / 2) + margin / 2
		cy = (2 * self.canvas_height - self.keyboard_height) / 2
		msg = "Keyboard off"
		self.canvas.create_text(cx, cy, text=msg, font="palatina 96", 
								fill = colors['off text'])	
									
	def draw_mini_keyboard(self):
		# this little guy shows you which range of keys you are playing
		left = self.menu_width + self.inner_margin
		right = self.canvas_width - self.inner_margin
		top = self.radial_bottom + self.inner_margin
		bottom = self.canvas_height - self.keyboard_height - self.inner_margin
		number_of_keys = 88
		deltaX = (right-left) / float(number_of_keys)
		first_note = 9  # first note on any piano is an A, which is 9
		pattern = [0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0]
		keys = (np.arange(number_of_keys) + first_note) % 12
		player_keys = np.arange(24) + ((self.leap_oct-1) * 12) + 3
		for i in xrange(number_of_keys):
			left_edge = i * deltaX + left
			right_edge = left_edge + deltaX
			key_type = pattern[keys[i]]
			outline_color = self.pallet[0]
			if key_type == 0:
				if i in player_keys:
					key_color = self.pallet[8]
					outline_color = self.pallet[7]
				else:
					key_color = self.pallet[7]
			else:
				key_color = self.pallet[0]
			self.canvas.create_rectangle(left_edge, top, right_edge, bottom, 
										 fill = key_color, 
										 outline = outline_color)
									
	def draw_oscillator(self):
		left, right = (self.menu_width, self.canvas_width)
		top, bottom = (self.tab_height, self.canvas_height-self.keyboard_height)
		self.canvas.create_rectangle(left, top, right, bottom, 
									 fill=self.pallet[0])
		self.draw_radials()
		self.draw_ADSR_graph()
		self.draw_harmonics_chart()
		
	def draw_ADSR_graph(self):
		cur_osc = self.cur_osc
		osc_state = self.osc_states[cur_osc]
		if osc_state == "on":
			colors = self.ADSR_on
		else:
			colors = self.ADSR_off
		margin = 2 * self.inner_margin
		left = self.menu_width + margin
		right = self.dial_coords[4][1][0]
		top = self.tab_height + margin
		bottom = self.radials_top - margin
		self.split_point = right + margin
		self.canvas.create_rectangle(left, top, right, bottom, 
									 fill = colors['box'], 
									 outline = colors['box'], width=3)
		self.draw_ADSR_lines(left, right, top, bottom, colors, cur_osc)
									 
	def draw_ADSR_lines(self, left, right, top, bottom, colors, cur_osc):
		total_width = right - left
		total_height = bottom - top
		attack_left = left
		attack_right = attack_left + ((total_width * 2.0 / 7.0) * 
									   self.ADSR[cur_osc][0]) + 10
		attack_height = bottom - (total_height * self.ADSR[cur_osc][1])
		decay_left = attack_right
		decay_right = decay_left + ((total_width * 2.0 / 7.0) * 
								     self.ADSR[cur_osc][2]) + 10
		sustain_height = bottom - (total_height * self.ADSR[cur_osc][3])
		release_left = right - ((total_width * 2.0 / 7.0) * 
							    self.ADSR[cur_osc][4])
		self.canvas.create_polygon(left, bottom, attack_right, attack_height, 
								   decay_right, sustain_height, release_left, 
								   sustain_height, right, bottom, 
								   fill= colors['polygon'])
		self.canvas.create_line(attack_right, top, attack_right, bottom, 
								fill = colors['verticals'])
		self.canvas.create_line(decay_right, top, decay_right, bottom, 
								fill = colors['verticals'])
		self.canvas.create_line(release_left, top, release_left, bottom, 
								fill = colors['verticals'])
		self.canvas.create_line(attack_left, bottom, attack_right, 
								attack_height, fill=colors['graph lines'], 
								width = 3)
		self.canvas.create_line(decay_left, attack_height, decay_right, 
								sustain_height, fill=colors['graph lines'], 
								width = 3)
		self.canvas.create_line(decay_right, sustain_height, release_left,
								sustain_height, fill=colors['graph lines'], 
								width = 3)
		self.canvas.create_line(release_left, sustain_height, right, bottom, 
								fill=colors['graph lines'], width = 3)
	 
	def draw_bar(self, colors, bar_width, left, top, bottom, right, i, cur_osc,
				  bar_height):
		if self.selected_cell == (1, 0):
			if self.mode == "Shape":
				this_bar = colors['selected']
			elif self.mode == "Draw" and self.selected_bar == i:
				this_bar = colors['selected']
			else: 	
				this_bar = colors['unselected']
		else:
			this_bar = colors['unselected']
		left_shift = bar_width * i
		bar_left = left + left_shift
		bar_right = bar_left + bar_width
		self.canvas.create_rectangle(bar_left, top, bar_right, bottom,
									 fill = this_bar[0])
		self.bar_coords.append([ (left, top), (right, bottom) ])
		if self.bar_heights[cur_osc][i] != 0.0:
			bar_top = bottom - (bar_height * self.bar_heights[cur_osc][i])
			self.canvas.create_rectangle(bar_left, bar_top, bar_right, bottom,
										 fill = this_bar[1],
										 outline = this_bar[2])
	 
	def draw_harmonics_chart(self):
		cur_osc = self.cur_osc
		osc_state = self.osc_states[cur_osc]
		if osc_state == "on":
			colors = self.bar_chart_on
		else:
			colors = self.bar_chart_off
		margin = 2 * self.inner_margin
		left = self.split_point + margin
		right = self.canvas_width - 3*margin
		top = self.tab_height + margin
		bottom = self.radials_top - margin
		chart_width = right - left
		bar_height = bottom - top
		self.canvas.create_rectangle(left, top, right, bottom,
									 fill = colors['background'], 
									 outline = colors['background outline'])
		bar_width = float(chart_width) / self.num_of_bars[cur_osc]
		for i in xrange(self.num_of_bars[cur_osc]):
			self.draw_bar(colors, bar_width, left, top, bottom, right, 
						  i, cur_osc, bar_height)
		self.draw_bar_nums(margin, bottom, right, colors)
						  
	def draw_bar_nums(self, margin, bottom, right, colors):
		box_height = 2 * margin
		full_box_top = bottom - box_height
		half_box_top = full_box_top - box_height
		box_right = self.canvas_width - margin
		cx = right + margin
		if self.num_of_bars == 32:
			bottom_colors = colors['on colors']
			top_colors = colors['off colors']
		else:
			bottom_colors = colors['off colors']
			top_colors = colors['on colors']
		self.canvas.create_rectangle(right, full_box_top, box_right, bottom,
									 fill = bottom_colors[0], 
									 outline = bottom_colors[1])
		cy1 = (bottom + full_box_top) / 2
		self.canvas.create_text(cx, cy1, text=32, fill = bottom_colors[2], 
								font='verdana 10')
		self.canvas.create_rectangle(right, half_box_top, box_right, 
									 full_box_top, fill = top_colors[0], 
									 outline = top_colors[1])
		cy2 = cy1 - box_height
		self.canvas.create_text(cx, cy2, text=16, fill = top_colors[2], 
							    font='verdana 10')
		self.draw_more_arrow(half_box_top, box_height, right, box_right)
		
	def draw_more_arrow(self, half_box_top, box_height, right, box_right):
		left = right
		right = box_right
		bottom = half_box_top - 4*box_height
		top = bottom - 4*box_height
		mid_height = bottom - 2*box_height
		self.canvas.create_rectangle(left, top, right, bottom, 
									 fill=self.pallet[4])
		self.canvas.create_polygon((left, bottom), (right, mid_height), 
								   (left, top), fill=self.pallet[8])
		
	def get_width_and_shape(self, finger_list):
		keys = [(finger_list[i][0] - finger_list[0][0]) 
				for i in np.arange(len(finger_list))]
		width = keys[-1] - keys[0]
		factor = 1.0/width
		keys_array = np.array(keys) * factor
		min_height = 100
		vals = [(finger_list[i][1] - min_height) for i in 
				np.arange(len(finger_list))]
		height_factor = 1.0/400.0
		vals_array = np.array(vals) * height_factor
		interp = interpolate.interp1d(keys_array, vals_array, kind='slinear')
		shape = interp(np.arange(width) * factor)
		return shape
		
	def shape_bar_graph(self, frame):
		cur_osc = self.cur_osc
		# will only execute if whole graph is selected AND 2 hands are seen.
		finger_list = self.leap.get_fingertip_list(frame)
		x = [finger_list[i][0] for i in range(len(finger_list))]
		width = max(x) - min(x)
		shape = self.get_width_and_shape(finger_list)
		if ((width < 250) and (self.num_of_bars[cur_osc] == 
				self.half_or_full['full'])):
			self.num_of_bars[cur_osc] = self.half_or_full['half']
		elif ((width > 350) and (self.num_of_bars[cur_osc] == 
				self.half_or_full['half'])):
			self.num_of_bars[cur_osc] = self.half_or_full['full']
		bar_width = float(width) / self.num_of_bars[cur_osc]
		for bar in range(self.num_of_bars[cur_osc]):
			left_edge = bar * bar_width
		 	right_edge = left_edge + bar_width
		 	xmid = (left_edge + right_edge) / 2
		 	xmid_rel_height = shape[xmid]
		 	bar_height = xmid_rel_height
		 	if bar_height < 0.0:
		 		bar_height = 0.0
		 	elif bar_height > 1.0:
		 		bar_height = 1.0
		 	self.bar_heights[cur_osc][bar] = bar_height
		
	def draw_radials(self):
		self.get_dial_values()
		self.dial_coords = []
		value_bottom = (self.canvas_height - self.keyboard_height - 
						self.keyboard_gap - self.inner_margin*2)
		self.radial_bottom = value_bottom
		value_top = value_bottom - self.dial_name_height
		dial_bottom = value_top
		dial_top = dial_bottom - self.radial_width
		self.hand_height = (dial_top, value_bottom)
		name_bottom = dial_top
		name_top = name_bottom - self.dial_name_height
		self.radials_top = name_top
		margin = self.inner_margin
		self.r = self.radial_width/2 - self.inner_margin
		cur_osc = self.cur_osc
		osc_state = self.osc_states[cur_osc]
		for i in xrange(8):
			if osc_state == "on":
				if (2, i) == self.selected_cell:
					colors = self.dial_on_selected
				else:
					colors = self.dial_on_unselected
			else:
				if (2, i) == self.selected_cell:
					colors = self.dial_off_selected
				else:
					colors = self.dial_off_unselected
			left = (margin * 2) + (self.radial_width * i) + self.menu_width
			right = left + self.radial_width
			cy = (dial_top + dial_bottom) / 2
			cy2 = (name_top + name_bottom) / 2
			cy3 = (value_top + value_bottom) / 2
			name = self.radial_names[i]
			if i > 4:
				right = (self.canvas_width - 2 * margin) - (self.radial_width * 
						 (7-i))
				left = right - self.radial_width
			cx = (left + right) / 2
			self.canvas.create_rectangle(left, name_top, right, name_bottom, 
										 fill = colors['text box fill'], 
										 outline = colors['text box outline'])
			self.canvas.create_text(cx, cy2, text=name,
									fill = colors['text color'], 
									font="arial 12")
			self.canvas.create_rectangle(left, dial_top, right, dial_bottom, 
										 fill = colors['dial box fill'], 
										 outline=colors['dial box outline'])
			self.canvas.create_rectangle(left, value_top, right, value_bottom, 
										 fill = colors['text box fill'], 
										 outline = colors['text box outline'])
			self.canvas.create_text(cx, cy3, text=self.ADSR_text[i],
									fill = colors['text color'], 
									font="arial 12")
			self.canvas.create_oval(cx-self.r, cy-self.r, cx+self.r, cy+self.r,
								    fill = colors['dial fill'], 
								    outline = colors['dial outline'])
			self.dial_coords.append([ (left, dial_top), (right, dial_bottom) ])
			self.last_radial_right = right
			self.draw_dial_contents(cx, cy, i, colors)
			
	def draw_dial_contents(self, cx, cy, i, colors):
		r = self.r
		mini_r = 3
		if i < 5:
			self.draw_ADSR_dial(cx, cy, i, colors)
		else:
			init_pos = self.dial_init_pos[i-5]
			if i == 5:
				self.draw_fine_dial(cx, cy, i, colors, init_pos)
			elif i == 6:
				self.draw_coarse_dial(cx, cy, i, colors, init_pos)
			else:
				self.draw_trans_and_level(cx, cy, i, colors, init_pos)
		self.canvas.create_oval(cx-mini_r, cy-mini_r, cx+mini_r, cy+mini_r, 
								fill = colors['button fill'], 
								outline = colors['button outline'])
								
	def draw_waveform_choices(self):
		left = self.canvas_width/5.0
		right = self.canvas_width * 0.8
		top = self.canvas_height /4.0
		bottom = self.canvas_height * 0.75
		self.canvas.create_rectangle(left, top, right, bottom, 
									 fill=self.pallet[9], stipple='gray12')
								
	def draw_ADSR_dial(self, cx, cy, i, colors):
		cur_osc = self.cur_osc
		r = self.r
		total_angle = 270
		init_pos = -90
		extend_to = -(total_angle * self.ADSR[cur_osc][i])
		endX = cx + (np.sin((-np.pi * 3/2) * self.ADSR[cur_osc][i]) * self.r)
		endY = cy + (np.cos((-np.pi * 3/2) * self.ADSR[cur_osc][i]) * self.r)
		self.canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=init_pos, 
						   extent = extend_to, fill = colors['arc fill'], 
						   outline = colors['arc outline'])
		self.canvas.create_line(cx, cy, endX, endY, fill = colors['dial line'], 
								width=3)
		
	def draw_fine_dial(self, cx, cy, i, colors, init_pos):
		cur_osc = self.cur_osc
		r = self.r
		total_angle = 359
		extend_to = -(total_angle * self.master_vals[cur_osc][0])
		endX = cx + (np.sin((2 * -np.pi) * self.master_vals[cur_osc][0])*self.r)
		endY = cy + (np.cos((2 * -np.pi) * self.master_vals[cur_osc][0])*self.r)
		self.canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=init_pos, 
					   extent = extend_to, fill = colors['arc fill'], 
					   outline = colors['arc outline'])
		self.canvas.create_line(cx, cy, endX, endY, fill = colors['dial line'], 
								width=3)
								
	def draw_coarse_dial(self, cx, cy, i, colors, init_pos):
		cur_osc = self.cur_osc
		r = self.r
		total_angle = 270
		init_pos = -90
		catcher = int(self.master_vals[cur_osc][1] * 24) / 24.0
		extend_to = -(total_angle * catcher)
		endX = cx + (np.sin((-np.pi * 3/2) * catcher) * self.r)
		endY = cy + (np.cos((-np.pi * 3/2) * catcher) * self.r)
		self.canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=init_pos, 
						   extent = extend_to, fill = colors['arc fill'], 
						   outline = colors['arc outline'])
		self.canvas.create_line(cx, cy, endX, endY, fill = colors['dial line'],
								width = 3)
		
	def draw_trans_and_level(self, cx, cy, i, colors, init_pos):	
		cur_osc = self.cur_osc
		r = self.r
		total_angle = 135
		init_angle = np.pi * 5/4
		extend_to = -(total_angle * self.master_vals[cur_osc][i-5])
		endX = cx + (np.sin((-np.pi * 3/4) * self.master_vals[cur_osc][i-5] + 
					 init_angle) * self.r)
		endY = cy + (np.cos((-np.pi * 3/4) * self.master_vals[cur_osc][i-5] + 
					 init_angle) * self.r)
		self.canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=init_pos, 
							   extent = extend_to, fill = colors['arc fill'], 
							   outline = colors['arc outline'])
		self.canvas.create_line(cx, cy, endX, endY, fill = colors['dial line'], 
								width=3)
			
	def get_dial_values(self):
		cur_osc = self.cur_osc
		# an exponential function to scale the attack from ms to seconds
		self.attack_time = 3000 * (self.ADSR[cur_osc][0] ** 5) + 2
		if self.attack_time < 10:
			attack_time_text = "%0.2f ms" % self.attack_time
		elif self.attack_time < 100:
			attack_time_text = "%0.1f ms" % self.attack_time
		elif self.attack_time < 1000:
			attack_time_text = "%d ms" % int(self.attack_time)
		else:
			attack_time_text = "%0.2f s" % (self.attack_time/1000.0)
			
		# formula for calculating decibels
		if self.ADSR[cur_osc][1] > 0.0:
			attack_height = (-1.0 + self.ADSR[cur_osc][1]) * 48.0
		# no need to save the value, only calculated for the display text
			if attack_height <= -48.0:
				attack_height_text = "-inf"
			elif attack_height > -10: 
				attack_height_text = "%0.2f dB" % attack_height
			else:
				attack_height_text = "%0.1f dB" % attack_height
		else:
			attack_height_text = "-inf"
			
		self.decay_time = 3000 * (self.ADSR[cur_osc][2] ** 5) + 2
		if self.decay_time < 10:
			decay_time_text = "%0.2f ms" % self.decay_time
		elif self.decay_time < 100:
			decay_time_text = "%0.1f ms" % self.decay_time
		elif self.decay_time < 1000:
			decay_time_text = "%d ms" % int(self.decay_time)
		else:
			decay_time_text = "%0.2f s" % (self.decay_time/1000.0)
			
		if self.ADSR[3] > 0.0:
			sustain_height = (-1.0 + self.ADSR[cur_osc][3]) * 48.0
			if sustain_height <= -48.0:
				sustain_height_text = "-inf"
			elif sustain_height > -10: 
				sustain_height_text = "%0.2f dB" % sustain_height
			else:
				sustain_height_text = "%0.1f dB" % sustain_height
		else: 
			sustain_height_text = "-inf"
			
		self.release_time = 3000 * (self.ADSR[cur_osc][4] ** 5) + 2
		if self.release_time < 10:
			release_time_text = "%0.2f ms" % self.release_time
		elif self.release_time < 100:
			release_time_text = "%0.1f ms" % self.release_time
		elif self.release_time < 1000:
			release_time_text = "%d ms" % int(self.release_time)
		else:
			release_time_text = "%0.2f s" % (self.release_time/1000.0)
			
		self.fine_tune = int(1000 * self.master_vals[cur_osc][0])
		fine_text = "%d" % self.fine_tune
		
		self.coarse = int(self.master_vals[cur_osc][1] * 24)
		coarse_text = "%d" % self.coarse
		
		if self.master_vals[cur_osc][2] > 0.0:
			level = (-1.0 + self.master_vals[cur_osc][2]) * 48.0
			if level <= -48.0:
				level_text = "-inf"
			elif level > -10: 
				level_text = "%0.2f dB" % sustain_height
			else:
				level_text = "%0.1f dB" % sustain_height
		else: 
			level_text = "-inf"
			
		self.ADSR_text = [attack_time_text, attack_height_text, 
						  decay_time_text, sustain_height_text, 
						  release_time_text, fine_text, coarse_text, level_text]
								
	def get_cell(self, frame):
		shift = self.leap.get_next_cell(frame)
		# shift is a tuple with (delta row, delta col)
		if (self.selected_cell[0] == 0):
			# row 0 is the tabs
			if (shift[0] == 1):
				self.selected_tab = None
				self.last_sel_tab = self.selected_cell[1]
				if self.selected_cell[1] in range(0, 2):
					self.selected_cell = (2, self.last_sel_dial)
				else:
					self.selected_cell = (1, 0)
			elif (shift[1] != 0 and self.selected_cell[1] + shift[1] in 
					range(0, 5)):
				next_tab = self.selected_cell[1] + shift[1]
				self.cur_osc = next_tab
				self.selected_cell = (0, next_tab)
				self.selected_tab = next_tab
		elif (self.selected_cell[0] == 1):
			# the bar graph
			if (shift[0] == -1):
				self.selected_tab = self.last_sel_tab
				self.selected_cell = (0, self.last_sel_tab)
			elif (shift[0] == 1):
				if self.last_sel_dial in range(5, 8):
					self.selected_cell = (2, self.last_sel_dial)
				else:
					self.selected_cell = (2, 5)
			#elif (shift[1] == 1):
			#	self.selected_cell = (1, 1)
		elif (self.selected_cell[0] == 2):
			# the dials.
			if (shift[0] == -1):
				self.last_sel_dial = self.selected_cell[1]
				if self.selected_cell[1] in range(0, 5):
					self.selected_tab = self.last_sel_tab
					self.selected_cell = (0, self.last_sel_tab)
				else:
					self.selected_cell = (1, 0)
			elif ((shift[-1] != 0) and (self.selected_cell[1] + shift[1] in
				   range(0, 8))):
				self.selected_cell = (2, self.selected_cell[1] + shift[1])
		elif ((self.mode != "Leap Play") and (len(frame.hands) == 2) and 
			  (shift[0] == -1)):
			self.leap_keys = Leap_UI.LeapKeyboard(self.leap.controller, 
										    self.leap_oct)
			self.keyboard_on_off = 1
			self.mode = "Leap Play"
				
	def change_val(self, frame):
		cur_osc = self.cur_osc
		scalar = 260.0
		if self.init_position == None:
			self.init_position = self.leap.get_current(frame)
			if self.selected_cell[0] == 2:
				if self.selected_cell[1] <= 4:
					self.start_point = self.ADSR[cur_osc][self.selected_cell[1]]
				else:
					self.start_point = self.master_vals[cur_osc][
													    self.selected_cell[1]-5]
			elif self.selected_cell[0] == 0:
				self.start_point = self.leap.get_current(frame)
		else:
			if self.selected_cell[0] == 2:
				deltaY = self.leap.get_current(frame) - self.init_position
				new_pos = self.start_point + (deltaY / scalar)
				if new_pos > 1.0:
					new_pos = 1.0
				elif self.selected_cell[1] == 6 and new_pos < (1.0/24):
					new_pos = 1.0 / 24
				elif new_pos < 0.0: 
					if self.selected_cell[1] < 6:
						new_pos = 0.0
					elif new_pos < -1.0:
						new_pos = -1.0
				if self.selected_cell[1] <= 4:
					self.ADSR[cur_osc][self.selected_cell[1]] = new_pos
				else:
					self.master_vals[cur_osc][self.selected_cell[1]-5] = new_pos
			elif self.selected_cell[0] == 0:
				deltaY = self.leap.get_current(frame) - self.start_point
				if self.osc_states[cur_osc] == "on":
					if deltaY < -100.0:
						self.osc_states[cur_osc] = "off"
				else:
					if deltaY > 100.0:
						self.osc_states[cur_osc] = "on"
				
	def draw_bar_graph(self, frame, mode):
		cur_osc = self.cur_osc
		total_range = 260.0
		right_shift = 150
		height_min = 250
		height_range = 200
		avg_pos = self.leap.get_avg_pos(frame, mode)
		for bar in range(self.num_of_bars[cur_osc]):
			current_pos = avg_pos + right_shift
			bar_width = total_range / self.num_of_bars[cur_osc]
			left_edge = bar_width * bar
			right_edge = left_edge + bar_width
			if current_pos in range(int(left_edge), int(right_edge) + 1):
				self.selected_bar = bar
				if mode == "Grab":
					height = self.leap.get_current(frame) - height_min
					if height > height_range:
						height = height_range
					elif height < 0.0:
						height = 0.0
					self.bar_heights[cur_osc][bar] = height / 200.0
			
	def get_key_notes(self, octave=4):
		return None
		
	def get_pressed_keys(self, frame):
		indexes_and_heights = self.leap_keys.get_pressed_keys(frame)
		chromatic_notes = 12
		for tuple in indexes_and_heights:
			(octave, index) = tuple[0]
			height = tuple[1]
			key = (octave - self.leap_oct) * chromatic_notes + index
			# value from 0 to 23 to correspond with a note on the keyboard
			self.pressed.append((key, height))
		
	def update_stuff(self):
		current_mode = self.mode
		frame = self.leap.controller.frame()
		mode = self.leap.get_mode(frame, current_mode)
		patch = self.patch_packer()
		if mode == "Leap Play":
			self.pressed = []
			if self.mode == "Leap Play":
				old_leap_notes = self.leap_notes
				self.leap_notes = self.leap_keys.leap_notes(frame, 
												old_leap_notes)
				self.get_pressed_keys(frame)
				self.key_notes = {}
			else:
				self.keyboard_on_off = 1
				self.leap_keys = leap_UI.LeapKeyboard(self.leap.controller, 
										    self.leap_oct)
				self.player.get_leap_keys(self.leap_keys)
		else:
			# force all notes to go into release mode somewhere here.
			self.turn_off_leap_keys(mode, frame)
		self.player.update_data(patch, self.leap_notes, self.mode)
		return mode
		
	def turn_off_leap_keys(self, mode, frame):
		if self.mode == "Leap Play":
			self.leap_keys = None
			self.leap_notes = {}
			self.keyboard_on_off = 0
		if mode == "Navigation":
			self.get_cell(frame)
		elif mode == "Grab":
			self.change_val(frame)
		else:
			self.init_position = None
			self.start_point = None
		key_notes = self.get_key_notes()
						
	def timerFired(self):
		delay = 30
		leap_state = self.leap.controller.is_connected
		frame = self.leap.controller.frame()
		patch = self.patch_packer()
		#self.keyboard.update_data(patch) # probs don't need.
		mode = self.update_stuff()
		self.mode = mode
		if self.selected_cell == (1, 0):
			if (len(frame.hands) == 2 and len(frame.fingers) >= 2):
				self.mode = "Shape"
				self.shape_bar_graph(frame)
			elif mode in ("Navigation", "Grab"):
				self.mode = "Draw"
				if mode == "Grab":
					self.is_drawing = True
				else:
					self.is_drawing = False
				self.draw_bar_graph(frame, mode)
		self.redraw_all()	
		self.canvas.after(delay, self.timerFired)					
			
	def redraw_all(self):
		self.canvas.delete(ALL)
		#self.canvas.create_window(100, 50, width=160, window=self.load_menu)
		#self.canvas.create_window(70, 85, width=100, window=self.load_button)
		self.draw_menu()
		self.draw_info()
		self.draw_tabs()
		self.draw_keyboard()
		if self.selected_tab < 4:
			# the effects page (selected_tab == 4) isn't decided on yet.
			self.draw_oscillator()
			self.draw_mode()
		self.draw_mini_keyboard()
		if self.selected_cell == (1, 1):
			self.draw_waveform_choices()
			
	def init(self):
		# called upon instantiation of any new patch.
		self.reset_UI()
		self.redraw_all()
		self.stream.start_stream()
		self.timerFired()
		"""
	def load_menu(self):
		self.var = StringVar(self.canvas)
		options_list = self.patches.get_keys()
		self.var.set(options_list[0])
		self.load_menu = OptionMenu(self.canvas, self.var, *options_list)
		self.load_menu.config(bg=self.pallet[0])
		self.load_menu['menu'].config(bg=self.pallet[9])
		self.load_button = Button(self.canvas, text='Load Preset', 
								  command=self.load(), bg='black')
		"""
	def reset_UI(self):
		self.cur_osc = 0
		self.current_keys = None
		self.cur_tab = 0
		self.selected_tab = 0
		self.leap_oct = 4
		self.last_right = 0
		self.last_radial_right = 0
		self.selected_cell = (2 , 5)
		self.selected_bar = None
		self.leap_notes = {}
		self.key_notes = {}
		self.pressed = []
		self.last_sel_dial = 0
		self.new_pos = 0
		self.last_sel_tab = 0
		self.init_position = None
		self.keyboard_on_off = 0
		self.mode = None
		self.last_mode = None
		
	def draw_menu(self):
		height = self.canvas_height - self.keyboard_height
		self.canvas.create_rectangle(0, 0, self.menu_width, height,
									 fill = self.pallet[0], 
									 outline=self.pallet[2],
									 width = 2)
	
	def start_move(self, event):
		for i in range(len(self.dial_coords)):
			# self.dial_coords[dial][corner][x or y]
			left = self.dial_coords[i][0][0]
			top = self.dial_coords[i][0][1]
			right = self.dial_coords[i][1][0]
			bottom = self.dial_coords[i][1][1]
			if (event.x in range(left, right+1) and event.y in range(top, 
				bottom+1)):
				self.selected_dial = i % len(self.dial_coords)
				self.y = event.y
				self.init_val = self.ADSR[self.selected_dial]
				
	def track_move(self, event):
		scalar = 200.0
		deltaY = (self.y - event.y) / scalar
		new_val = self.init_val + deltaY
		if new_val > 1.0:
			new_val = 1.0
		elif new_val < 0.0:
			new_val = 0.0
		self.ADSR[cur_osc][self.selected_dial] = new_val
		#self.redraw_all()
		
	def stop_move(self, event):
		self.y = 0
		self.selected_dial = None
			
	def run(self):
		root = Tk()
		self.canvas_width = 1000
		self.canvas_height = 700
		self.canvas = Canvas(root, width=self.canvas_width, 
							 height=self.canvas_height)
		#self.load_menu()
		self.canvas.pack()
		#root.bind("<Button>", self.click)
		#root.bind("<ButtonPress-1>", self.start_move)
		#root.bind("<B1-Motion>", self.track_move)
		#root.bind("<ButtonRelease-1>", self.stop_move)
		#root.bind("<KeyPress>", self.keyboard.key_press)
		#root.bind("<KeyRelease>", self.keyboard.key_release)
		self.init()
		root.mainloop()
		
if __name__ == '__main__':
		
	UI = Interface()
	UI.run()