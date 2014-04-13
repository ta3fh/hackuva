__author__ = 'csh7kd'

global x_min, x_max, y_min, y_max, z_min, z_max, pitch_min, pitch_max, roll_min, roll_max, yaw_min, yaw_max

x_min = -350
x_max = 350

y_min = 100
y_max = 350

z_min = -100
z_max = 100

pitch_min = -.8
pitch_max = .8

roll_min = -0.65
roll_max = 0.55

yaw_min = -0.3
yaw_max = 0.3

axis_min = 0
axis_max = 1000

scale_offsets = {
    "Major": [0,2,4,5,7,9,11],
    "Natural Minor": [0,2,3,5,7,8,10],
    "Harmonic Minor": [0,2,3,5,7,8,11],
    "Melodic Minor": [0,2,3,5,7,9,11],
    "Pentatonic Major": [0,2,4,7,9],
    "Penatonic Minor": [0,3,5,7,10],
    "Chromatic": range(0,12)
}

global velocity_default
velocity_default = 100

global noteoff, noteon, aftertouch, controller, patchchange, channelpressure, pitchbend, misc
noteoff = 0x80
noteon = 0x90
aftertouch = 0xA0
controller = 0xB0
patchchange = 0xC0
channelpressure = 0xD0
pitchbend = 0xE0
misc = 0xF0