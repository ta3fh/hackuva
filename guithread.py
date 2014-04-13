from threading import *
from time import sleep

class RunningThread(Thread):

	def run(self):
		for i in range(10):
			print "Running %d" % (i+1)
			sleep(1)

for i in range(10):
	RunningThread().start()