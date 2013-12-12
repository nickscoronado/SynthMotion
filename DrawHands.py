# draw hands
import math

class Hands:

	def __init__(self, canvas, left, top, right, bottom, on_colors, off_colors):
		self.box_width = right - left
		self.box_height = bottom - top
		self.left_border = left
		self.top_border = top
		self.canvas = canvas
		self.on_colors = on_colors
		self.off_colors = off_colors
		
	def nav_hand(self):
		self.hand_shape(self.box_height/50.0)
		self.draw_index()

	def grab_hand(self):
		self.hand_shape(self.box_height/50.0)
		self.draw_index()
		self.draw_middle_finger()
		self.draw_thumb()
		
	def shape_hand(self):
		self.hand_shape(self.box_height/20.0)
		self.draw_index()
		self.draw_middle_finger()
		self.draw_thumb()
		self.draw_outer_fingers()
		self.draw_2x()
		
	def draw_outer_fingers(self):
		ring_cx = self.finger_cxs[2]
		pinky_cx = self.finger_cxs[3]
		r = self.finger_radius * 0.9
		ring_left = ring_cx - r
		ring_right = ring_cx + r
		ring_top = self.index_top
		bottom = self.top
		self.canvas.create_rectangle(ring_left, ring_top, ring_right, bottom, 
									 fill=self.colors[1], outline=self.colors[1])
		ring_tip_cy = ring_top
		self.canvas.create_oval(ring_cx - r, ring_tip_cy - r,
								ring_cx + r, ring_tip_cy + r,
								fill=self.colors[1], outline=self.colors[1])
		pinky_left = pinky_cx - r
		pinky_right = pinky_left + (2 * r)
		pinky_top = self.box_height * 0.3 + self.top_border
		self.canvas.create_rectangle(pinky_left, pinky_top, pinky_right, bottom, 
									 fill=self.colors[1], outline=self.colors[1])
		pinky_tip_cy = pinky_top
		self.canvas.create_oval(pinky_cx - r, pinky_tip_cy - r,
								pinky_cx + r, pinky_tip_cy + r,
								fill=self.colors[1], outline=self.colors[1])
		
	def draw_2x(self):
		cx = (self.box_width * 0.85) + self.left_border
		cy = (self.box_height * 0.1) + self.top_border
		font_size = 12 * (self.box_width / 100)
		self.canvas.create_text(cx, cy, text="2x",
								font=('Arial', font_size, 'bold'))
		
	def draw_index(self):	
		left = self.left
		right = self.left + (2 * self.finger_radius)
		bottom = self.top
		self.index_top = (self.box_height * 0.2) + self.top_border
		self.canvas.create_rectangle(left, self.index_top, right, bottom,
		                             fill=self.colors[1], outline=self.colors[1])
		cx = left + self.finger_radius
		cy = self.index_top
		r = self.finger_radius
		self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, 
								fill=self.colors[1], outline=self.colors[1])
		
	def draw_middle_finger(self):
		left = (self.right - (2 * self.knuckle_width) - (2 * self.finger_radius)
		 		- self.finger_gap / 2.0)
		right = left + self.knuckle_width - (self.finger_gap / 2.0)
		top = self.box_height * 0.15 + self.top_border
		bottom = self.top
		self.canvas.create_rectangle(left, top, right, bottom, 
									 fill=self.colors[1], outline=self.colors[1])
		cx = left + self.finger_radius + (self.finger_gap / 4.0)
		cy = top
		r = self.finger_radius + (self.finger_gap / 4.0)
		self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, 
							    fill=self.colors[1], outline=self.colors[1])
		
	def draw_thumb(self):
		point1_x = self.thumb_base_cx + (self.thumb_radius * math.sin(math.pi *
										 5 / 4.0))
		point1_y = self.thumb_base_cy - (self.thumb_radius * math.cos(math.pi *
										 5 / 4.0))
		point2_x = self.thumb_base_cx + (self.thumb_radius * math.sin(math.pi / 
										 4.0))
		point2_y = self.thumb_base_cy - (self.thumb_radius * math.cos(math.pi /
										 4.0))
		point3_x = point2_x - (1.3 * self.knuckle_width) 
		point3_y = point2_y - (1.3 * self.knuckle_width)								 
		point4_x = point1_x - (1.3 * self.knuckle_width) 
		point4_y = point1_y - (1.3 * self.knuckle_width)
		self.canvas.create_polygon((point1_x, point1_y), (point2_x, point2_y),
								   (point3_x, point3_y), (point4_x, point4_y),
								   fill = self.colors[1], outline=self.colors[1])
		thumb_tip_cx = (point3_x + point4_x) / 2.0
		thumb_tip_cy = (point3_y + point4_y) / 2.0
		self.canvas.create_oval(thumb_tip_cx - self.thumb_radius,
								thumb_tip_cy - self.thumb_radius,
								thumb_tip_cx + self.thumb_radius,
								thumb_tip_cy + self.thumb_radius,
								fill = self.colors[1], outline=self.colors[1])
		self.canvas.create_polygon((self.left+1, self.top), (self.left+1, 
									self.bottom), (self.left - 
									self.thumb_radius/2, self.bottom - 
									self.thumb_radius), fill = self.colors[1], 
									outline=self.colors[1])
									
	def draw_body(self, anchor, height, thick, slant):
		(anchor_x, anchor_y) = anchor
		length = height * (1.0 / math.tan(slant))
		anchor_point = anchor
		point1 = (anchor_x+length, anchor_y-height) # points going c-clockwise
		point2 = (point1[0]-(thick*math.tan(slant)), point1[1]-thick)
		point3 = (anchor_x-(thick*math.tan(slant)), anchor_y-thick)
		self.canvas.create_polygon(anchor_point, point1, point2, point3, 
								   fill=self.colors[1], outline=self.colors[0])
		self.eraser_tip1 = point1
		self.eraser_tip2 = point2
								   
	def draw_head(self, anchor, height, thick, slant, peak):
		# some of the grossest trig this world ever did see...
		(anchor_x, anchor_y) = anchor
		anchor_point = anchor
		point1 = (anchor_x-(thick*math.tan(slant))*0.25 +
				 (peak*math.cos(slant)), anchor_y-thick*0.25-
				  peak*math.sin(slant))
		point2 = (anchor_x-(thick*0.5*math.tan(slant)), anchor_y-thick*0.5)
		point3 = (anchor_x-(3*thick*math.tan(slant))*0.25 +
				 (peak*math.cos(slant)), anchor_y-3*thick*0.25-
				  peak*math.sin(slant))
		point4 = (anchor_x-(thick*math.tan(slant)), anchor_y-thick)
		point5 = (anchor_x-((0.5*thick)/math.cos(slant))*
				  (1.0/math.cos((math.pi/2)-slant)), anchor_y)
		self.canvas.create_polygon(anchor_point, point1, point2, point3, 
								   point4, point5, fill=self.colors[1], 
								   outline=self.colors[0], width=2)
		self.peak1 = point1
		self.trough = point2
		self.peak2 = point3
		
	def draw_lines(self, eraser, slant):
		eraser_height = eraser * math.tan(slant)
		edge1 = (self.eraser_tip1[0]-eraser, self.eraser_tip1[1]+eraser_height)
		edge2 = (self.eraser_tip2[0]-eraser, self.eraser_tip2[1]+eraser_height)
		self.canvas.create_line(edge1, edge2, fill=self.colors[0], width=2)
		mid_point = ((edge1[0]+edge2[0])/2.0, (edge1[1]+edge2[1])/2.0)
		self.canvas.create_line(mid_point, self.trough, fill=self.colors[0])
		quarter1 = ((edge1[0]+mid_point[0])/2.0, (edge1[1]+mid_point[1])/2.0)
		quarter2 = ((edge2[0]+mid_point[0])/2.0, (edge2[1]+mid_point[1])/2.0)
		self.canvas.create_line(quarter1, self.peak1, fill=self.colors[0])
		self.canvas.create_line(quarter2, self.peak2, fill=self.colors[0])
									
	def draw_pencil(self):
		left = (self.box_width/4.0)+(self.box_width/15)+self.left_border
		bottom = (self.box_height * 7 / 8.0) + self.top_border
		anchor = (left, bottom)
		height = self.box_height * 0.5
		thick = self.box_height * 0.28  # the vertical thickness of the pencil
		peak = self.box_height * 0.1  # height of triangles formed by the peaks
		eraser = self.box_width * 0.1 # width of the eraser
		slant = math.atan(2.0/3) # slant angle of the pencil
		self.draw_body(anchor, height, thick, slant)
		self.draw_head(anchor, height, thick, slant, peak)
		self.draw_lines(eraser, slant)

	def hand_shape(self, curve_height):
		self.left = (self.box_width/4.0)+(self.box_width/15)+self.left_border
		self.right = self.left + (self.box_width / 2.0)
		self.top = (self.box_height / 2.0) + self.top_border
		self.bottom = (self.box_height * 7 / 8.0) + self.top_border
		hand_curve_radius = self.box_height / 16.0
		in_right = self.right - hand_curve_radius
		in_bottom = self.bottom - hand_curve_radius
		mid_point = ((self.left + self.right) / 2.0, self.top - curve_height)
		self.canvas.create_polygon((self.left, self.top), (self.left, self.bottom),
		                           (in_right, self.bottom), (in_right, in_bottom),
		                           (self.right, in_bottom), 
		                           (self.right, self.top), (mid_point), 
		                           fill=self.colors[1], outline=self.colors[1])
		self.canvas.create_oval(in_right - hand_curve_radius,
								in_bottom - hand_curve_radius,
								in_right + hand_curve_radius,
								in_bottom + hand_curve_radius,
								fill=self.colors[1], outline=self.colors[1])
		self.thumb_radius = self.box_height / 13.0
		self.thumb_base_cx = self.left
		self.thumb_base_cy = self.bottom - self.thumb_radius
		self.canvas.create_oval(self.thumb_base_cx - self.thumb_radius, 
							    self.thumb_base_cy - self.thumb_radius,
							    self.thumb_base_cx + self.thumb_radius,
							    self.thumb_base_cy + self.thumb_radius,
							    fill=self.colors[1], outline=self.colors[1])
		self.finger_gap = self.box_width / 100.0
		self.knuckle_width = (self.right - self.left) / 4.0
		finger_cy = self.top
		self.finger_radius = (self.knuckle_width - self.finger_gap) / 2.0
		finger1_cx = self.left + self.finger_radius
		finger2_cx = (self.right - (2 * self.knuckle_width) - 
					  self.finger_radius - self.finger_gap / 2.0)
		finger3_cx = self.right - self.knuckle_width - self.finger_radius
		finger4_cx = self.right - self.finger_radius
		self.finger_cxs = [finger1_cx, finger2_cx, finger3_cx, finger4_cx]
		for cx in self.finger_cxs:
			self.canvas.create_oval(cx - self.finger_radius,
									finger_cy - self.finger_radius,
									cx + self.finger_radius,
									finger_cy + self.finger_radius,
									fill=self.colors[1], outline=self.colors[1])
	
	def draw_hand(self, mode, last_mode=None, state="on"):
		if state == "on":
			self.colors = self.on_colors
		else:
			self.colors = self.off_colors
		left, top = self.left_border, self.top_border
		right, bottom = left+self.box_width, top+self.box_height
		self.canvas.create_rectangle(left, top, right, bottom, 
									 fill = self.colors[0], 
									 outline = self.colors[1])
		if mode == "Navigation":
			self.nav_hand()
		elif mode == "Grab":
			self.grab_hand()
		elif mode == "Draw":
			self.draw_pencil()
		elif mode == "Shape":
			self.shape_hand()
		elif mode == "Leap Play":
			self.shape_hand()
		elif mode == None:
			self.draw_hand(last_mode, state="off")