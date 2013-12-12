
from random import randint
import shelve

class Patches:
	def __init__(self):
		self.saved_patches = {}
		self.Default = [ ["on", [0.02, 1.0, 0.6, 0.8, 0.8], [0.0, 1.0/24, 1.0], 16, 
				[1] + [0] * 31],#[1.0 * (2.0 ** (-i/2.0)) for i in xrange(32)]],
			["off", [0.3, 1.0, 0.0, 1.0, 0.0], [0.0, 1.0/24, 0.0], 16, 
				[1] + [0] * 31],
			["off", [0.3, 1.0, 0.0, 1.0, 0.0], [0.0, 1.0/24, 0.0], 16, 
				[1] + [0] * 31],
			["off", [0.3, 1.0, 0.0, 1.0, 0.0], [0.0, 1.0/24, 0.0], 16, 
				[1] + [0] * 31] ]
		self.Random = [ ["on", 
		   [self.decimal() for i in range(5)],
		   [self.decimal() for i in range(3)],
		   16 + (16 * randint(0, 1)),
		   [self.decimal(3) for i in range(32)]],
		   
		   [self.on_off(),
		   [self.decimal() for i in range(5)],
		   [self.decimal() for i in range(3)],
		   16 + (16 * randint(0, 1)),
		   [decimal(3) for i in range(32)]],
		   
		   [self.on_off(),
		   [self.decimal() for i in range(5)],
		   [self.decimal() for i in range(3)],
		   16 + (16 * randint(0, 1)),
		   [self.decimal(3) for i in range(32)]],
		   
		   [self.on_off(),
		   [self.decimal() for i in range(5)],
		   [self.decimal() for i in range(3)],
		   16 + (16 * randint(0, 1)),
		   [self.decimal(3) for i in range(32)]] ]
		self.save_patch('Default', self.Default)
		self.save_patch('Random', self.Random)
		
	def get_keys(self):
		self.saved_patches = shelve.open('patches.db')
		keys = self.saved_patches.keys()
		self.saved_patches.close()
		return keys
			
	def save_patch(self, patch_name, patch):
		self.saved_patches = shelve.open('patches.db')
		self.saved_patches[patch_name] = patch
		self.saved_patches.close()
		
	def load_patch(self, patch_name):
		self.saved_patches = shelve.open('patches.db')
		patch = self.saved_patches[patch_name]
		self.saved_patches.close()
		return patch
		
	def decimal(self, places=2):
		denominator = randint(0, 10**places + 1)
		dec = (1.0 / 10**places) * denominator
		return dec
	
	def on_off(self):
		state = ["off", "on"]
		i = randint(0, 1)
		return state[i]


Default = [ ["on", [0.02, 1.0, 0.6, 0.8, 0.8], [0.0, 1.0/24, 1.0], 16, 
				[1] + [0] * 31],#[1.0 * (2.0 ** (-i/2.0)) for i in xrange(32)]],
			["off", [0.3, 1.0, 0.0, 1.0, 0.0], [0.0, 1.0/24, 0.0], 16, 
				[1] + [0] * 31],
			["off", [0.3, 1.0, 0.0, 1.0, 0.0], [0.0, 1.0/24, 0.0], 16, 
				[1] + [0] * 31],
			["off", [0.3, 1.0, 0.0, 1.0, 0.0], [0.0, 1.0/24, 0.0], 16, 
				[1] + [0] * 31]
			]
				
def decimal(self, places=2):
	denominator = randint(0, 10**places + 1)
	dec = (1.0 / 10**places) * denominator
	return dec
	
def on_off(self):
	state = ["off", "on"]
	i = randint(0, 1)
	return state[i]
	
"""	
Random = [ ["on", 
		   [decimal() for i in range(5)],
		   [decimal() for i in range(3)],
		   16 + (16 * randint(0, 1)),
		   [decimal(3) for i in range(32)]],
		   
		   [on_off(),
		   [decimal() for i in range(5)],
		   [decimal() for i in range(3)],
		   16 + (16 * randint(0, 1)),
		   [decimal(3) for i in range(32)]],
		   
		   [on_off(),
		   [decimal() for i in range(5)],
		   [decimal() for i in range(3)],
		   16 + (16 * randint(0, 1)),
		   [decimal(3) for i in range(32)]],
		   
		   [on_off(),
		   [decimal() for i in range(5)],
		   [decimal() for i in range(3)],
		   16 + (16 * randint(0, 1)),
		   [decimal(3) for i in range(32)]]
		  ]
		  
saved_patches = { "Default" : Default,
				  "Random" : Random 
				}

"""
				
ATTACK_TIME = {'title' : 'Attack Time', 'msg' : """\
The time needed to travel from 
the inital value to the peak 
value."""
}

PEAK = {'title' : 'Peak Amplitude', 'msg' : """\
The amplitude reached at the end 
of the attack time."""
}

DECAY_TIME = {'title' : 'Decay Time', 'msg' : """\
The time needed to travel from 
the peak value to the sustain 
value."""
}

SUSTAIN_HEIGHT = {'title' : 'Sustain Height', 'msg' : """\
The amplitude reached at the end 
of the decay stage, at which the 
note sustains for as long as it 
is on.
"""
}

RELEASE_TIME = {'title' : 'Release Time', 'msg' : """\
The time needed to travel from 
the sustain amplitude to zero."""
}

FINE = {'title' : 'Fine', 'msg' : """\
Changes the tuning of the 
fundamental pitch by millioctaves
(equally-spaced thousandths of an
octave)."""
}

COARSE = {'title' : 'Coarse', 'msg' : """\
Multiplies the fundamental harmonic 
by an integer."""
}

LEVEL = {'title' : 'Level', 'msg' : "Overall amplitude for this oscillator."
}

MORE_WAVEFORMS = {'title' : 'More Waveforms', 'msg' : 'some more waveforms.'}

EFFECTS = {'title' : 'Effects', 'msg' : 'This page ain\'t done yet.'}

WAVEFORM_EDITOR = {'title' : 'Waveform Editor', 'msg' : """\
Each bar represents a multiple of 
the fundamental frequency 
(otherwise known as partials or 
harmonics), with the first bar 
being the fundamental pitch. The
height of each bar represents the 
amplitude of that partial. Up to 32
partials are available for each 
oscillator."""
}

OSCILLATOR_1 = {'title' : 'Oscillator 1', 'msg' : "This oscillator is on"}
OSCILLATOR_2 = {'title' : 'Oscillator 2', 'msg' : "This oscillator is off"}
OSCILLATOR_3 = {'title' : 'Oscillator 3', 'msg' : "This oscillator is off"}
OSCILLATOR_4 = {'title' : 'Oscillator 4', 'msg' : "This oscillator is off"}

CELL_TO_TEXT = { (0, 0) : OSCILLATOR_1, (0, 1) : OSCILLATOR_2, 
				 (0, 2) : OSCILLATOR_3, (0, 3) : OSCILLATOR_3,
				 (0, 4) : EFFECTS, (1, 1) : MORE_WAVEFORMS,
				 (1, 0) : WAVEFORM_EDITOR, (2, 0) : ATTACK_TIME,
				 (2, 1) : PEAK, (2, 2) : DECAY_TIME, (2, 3) : SUSTAIN_HEIGHT, 
				 (2, 4) : RELEASE_TIME, (2, 5) : FINE, (2, 6) : COARSE, 
				 (2, 7) : LEVEL
				 }




		  