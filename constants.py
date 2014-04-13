__author__ = 'csh7kd'

global x_min, x_max, y_min, y_max, z_min, z_max, pitch_min, pitch_max, roll_min, roll_max, yaw_min, yaw_max
x_min = -350
x_max = 350
y_min = 100
y_max = 350
z_min = -100
z_max = 100
pitch_min = -90
pitch_max = 90
#roll_min = -90
#roll_max = 90

roll_min = -0.65
roll_max = 0.55

yaw_min = -90
yaw_max = 90

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