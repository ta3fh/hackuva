from Leap import *
from time import sleep

leap = Controller()

print "AWESOME MIDI CONTROLLER!"

sleep(1)

while True:
	frame = leap.frame()
	print "=== Got frame from Leap ==="
	i = 0
	for finger in frame.fingers:
		i += 1
		print "Finger %s: %s" % ( i, finger.tip_position )

	sleep(1)