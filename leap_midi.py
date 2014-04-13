from Leap import *
import rtmidi_python as rtmidi
from time import sleep
import constants

from threading import Thread

from constants import axis_min, axis_max


note = "x"
velocity = "z"
controller1 = "yaw"
controller2 = "y"
controller3 = "pitch"
controller4 = "roll"
ctrlPort1 = 1
ctrlPort2 = 7
ctrlPort3 = 11
ctrlPort4 = 16

scale_notes = None

range_note = [50, 70] #TODO: implement note schemas
range_velocity = [0, 127]
range_controller1 = [0, 127]
range_controller2 = [0, 127]
range_controller3 = [0, 127]
range_controller4 = [0, 127]

def setAxis_note(axis):
    global note
    note = axis

def setAxis_velocity(axis):
    global velocity
    velocity = axis

def setAxis_controller1(axis):
    global controller1
    controller1 = axis

def setAxis_controller2(axis):
    global controller2
    controller2 = axis

def setAxis_controller3(axis):
    global controller3
    controller3 = axis

def setAxis_controller4(axis):
    global controller4
    controller4 = axis

def setCtrlPort1(axis):
    global ctrlPort1
    ctrlPort1 = axis

def setCtrlPort2(axis):
    global ctrlPort2
    ctrlPort2 = axis

def setCtrlPort3(axis):
    global ctrlPort3
    ctrlPort3 = axis

def setCtrlPort4(axis):
    global ctrlPort4
    ctrlPort4 = axis

def map_range(num, min1, max1, min2, max2, clamp=True):
    percent = (num-min1)/(max1-min1)
    if clamp:
        percent = 0 if percent < 0 else percent
        percent = 1 if percent > 1 else percent
    return min2 + percent*(max2-min2)

class Baton:

    def __init__(self, maxHistory, hand):
        self.id = hand.id
        self.history = [hand]
        self.maxHistory = maxHistory
        self.config = [note, velocity, controller1, controller2, controller3, controller4]

        #TODO: make note scaling GUI side
        self.scale = [50,53,55,57,60]
        self.scale += map(lambda x: x+12, self.scale)
        self.scale.append(self.scale[0]+24)

        # print "created a new baton"

    def getVals(self): # FLOAT values from 0-1000, or axis_min to axis_max
        config = self.config
        ret = []
        for axis in config: #note, velocity, controller1, controller2, controller3, controller4
            if axis == "":
                ret.append(None)
            elif axis == "x":
                ret.append(map_range(self.getXValue(), constants.x_min, constants.x_max, constants.axis_min, constants.axis_max))
            elif axis == "y":
                ret.append(map_range(self.getYValue(), constants.y_min, constants.y_max, constants.axis_min, constants.axis_max))
            elif axis == "z":
                ret.append(map_range(self.getZValue(), constants.z_min, constants.z_max, constants.axis_max, constants.axis_min))
                                            #we  want away from body to be greater value
            elif axis == "pitch":
                ret.append(map_range(self.getPitchValue(), constants.pitch_min, constants.pitch_max, constants.axis_min, constants.axis_max))
            elif axis == "roll":
                ret.append(map_range(self.getRollValue(), constants.roll_min, constants.roll_max, constants.axis_max, constants.axis_min))  #backwards because
                                            #right hand is more intuitive to twist positive the opposite way we didn't ask for this life
            elif axis == "yaw":
                ret.append(map_range(self.getYawValue(), constants.yaw_min, constants.yaw_max, constants.axis_min, constants.axis_max))

        return ret

    def generateMessages(self):
        messages = []
        vals = self.getVals()

        velocity = constants.velocity_default
        if vals[1] is not None:
            global range_velocity
            velocity = int(map_range(vals[1],constants.axis_min,constants.axis_max,range_velocity[0],range_velocity[1]))

        #note (and velocity)
        # TODO note and velocity scaling, etc
        if vals[0] is not None:
            global range_note
            note = None
            scale_notes = globals()["scale_notes"]
            if scale_notes is None:
                note = int(map_range(vals[0],axis_min,axis_max,range_note[0],range_note[1]))
            else:
                note_idx = int(map_range(vals[0],axis_min,axis_max,0,len(scale_notes)))
                note = scale_notes[note_idx]
            messages.append([constants.noteon, note, velocity])

        #controllers 1-4
        if vals[2] is not None:
            global range_controller1
            val = int(map_range(vals[2],axis_min,axis_max,range_controller1[0],range_controller1[1]))
            messages.append([constants.controller, ctrlPort1, val])
        if vals[3] is not None:
            global range_controller2
            val = int(map_range(vals[3],axis_min,axis_max,range_controller2[0],range_controller2[1]))
            messages.append([constants.controller, ctrlPort2, val])
        if vals[4] is not None:
            global range_controller3
            val = int(map_range(vals[4],axis_min,axis_max,range_controller3[0],range_controller3[1]))
            messages.append([constants.controller, ctrlPort3, val])
        if vals[5] is not None:
            global range_controller4
            val = int(map_range(vals[5],axis_min,axis_max,range_controller4[0],range_controller4[1]))
            messages.append([constants.controller, ctrlPort4, val])

        return messages



    def getAxis(self, key):
        return {
            'y': self.getYValue(),
            'z': self.getZValue(),
            'roll': self.getRollValue(),
            'pitch': self.getPitchValue(),
            'yaw': self.getYawValue(),
        }[key]

    def setMaxHistory(self, maxHistory):
        self.maxHistory = maxHistory

    def getId(self):
        return self.id

    def update(self, hand):
        history = self.history
        if hand is None:
            if len(history) > 0:
                history.pop(0)
            else:
                return False
        else:
            history.append(hand)
        while len(history) > self.maxHistory:
            history.pop(0)
        #print len(history)
        return True


    def getFingerValue(self):
        history = self.history
        total = 0
        for h in history:
            total += len(h.fingers)
        if len(history) is not 0:
            return int(float(total)/float(len(history)))
        else:
            return 0

    def getXValue(self):
        history = self.history
        total = 0
        for h in history:
            total += h.palm_position.x
        return float(total)/float(len(history))

    def getYValue(self):
        history = self.history
        total = 0
        for h in history:
            total += h.palm_position.y
        return float(total)/float(len(history))

    def getZValue(self):
        history = self.history
        total = 0
        for h in history:
            total += h.palm_position.z
        return float(total)/float(len(history))

    def getRollValue(self):
        history = self.history
        total = 0
        for h in history:
            total += h.palm_normal.roll
        return float(total)/float(len(history))

    def getPitchValue(self):
        history = self.history
        total = 0
        for h in history:
            total += h.direction.pitch
        return float(total)/float(len(history))

    def getYawValue(self):
        history = self.history
        total = 0
        for h in history:
            total += h.direction.yaw
        return float(total)/float(len(history))

    def getChannel(self):
        return 0 #hard coded for now
        # history = self.history
        # total = 0
        # for h in history:
        #     total += len(h.fingers)
        # return float(total +0.5)/float(len(history))

    def flushHistory(self):
        self.history = []



class Player:

    def __init__(self, midiOut, midiPort, smoothing=5):
        self.midiOut = midiOut
        self.midiPort = None
        self.switchPort(midiPort)
        self.batons = []
        self.playing_notes = []
        self.smoothing = smoothing

    def switchPort(self, new_port):
        if self.midiPort is not None:
            self.midiOut.close_port()
        self.midiOut.open_port(new_port)
        self.midiPort = new_port

    def sync(self): #handles midi messages from baton's parameters
        batons = self.batons
        messages = []
        for baton in batons:
            # print baton.getFingerValue()
            if baton.getFingerValue() < 1:
                continue
            if len(baton.history) is not 0:
                messages = baton.generateMessages()
        notesNow = []
        for message in messages:
            if message[0] != constants.noteon:
                #if message[0] == constants.controller:
                #    print "Setting controller to %d." % message[1]
                self.midiOut.send_message(message) #send message if not a note
            else:
                notesNow.append(message[1])
                if message[1] not in self.playing_notes: #it is a note
                    # print "Playing new note"
                    self.playing_notes.append(message[1])
                    self.midiOut.send_message(message)
                else: #note already playing
                    pass
        for note in self.playing_notes: #handle note offs
            if note not in notesNow:
                self.midiOut.send_message([constants.noteoff, note, 100])
                self.playing_notes.remove(note)

    def playNote(self, note):
        playing_notes = self.playing_notes
        if note not in playing_notes:
            playing_notes.append(note)
            #if note.channel > 0:
            #self.midiOut.send_message([0x90 + (note.channel - 1), note.midiVal, note.velocity])
            self.midiOut.send_message([0x90, note.midiVal, note.velocity])

    def stopNote(self, note):
        playing_notes = self.playing_notes
        if note in playing_notes:
            playing_notes.remove(note)
            #if note.channel > 0:
            #self.midiOut.send_message([0x80 + (note.channel - 1), note.midiVal, note.velocity])
            self.midiOut.send_message([0x80, note, 100])

    # def controlChange(self, controller, value):
    #     self.midiOut.send_message([0xB0 + ( - 1)


    def stopAll(self):
        playing_notes = self.playing_notes
        for note in playing_notes:
            self.stopNote(note)

    def flushNotes(self):
        self.stopAll()
        self.playing_notes = []

    def update(self, hands): #handles how many batons (hands) are currently used
        found_batons = []
        for hand in hands:
            tracked = False
            for baton in self.batons:
                if baton.getId() == hand.id:
                    baton.update(hand)
                    found_batons.append(baton)
                    tracked = True
                    break
            if not tracked:
                self.batons.append(Baton(self.smoothing, hand))
        for baton in self.batons:
            if baton not in found_batons:
                if not baton.update(None):
                    self.batons.remove(baton)
                    # STOP PLAYING NOTES!!!
                    # print "Removed batons, %d remaining" % len(self.batons)

class LeapMusicApp(Thread):

    def __init__(self, out=None):
        super(LeapMusicApp, self).__init__()
        self.out = out
        if self.out is None:
            self.out = 0

        self.player = Player(rtmidi.MidiOut(), self.out, 50)


    def set_out(self,x):
        self.player.switchPort(x)

    def run(self):
        leap = Controller()
        self.done = False


        player = self.player

        playing_notes = []
        possible_notes = [50,52,54,55,57,59,61,62]
        possible_notes = map(lambda x: x+12,possible_notes)

        while not self.done:
            frame = leap.frame()

            hands = []
            for hand in frame.hands:
                if True or hand.palm_position.z < 0:
                    hands.append(hand)
            player.update(hands)

            player.sync()

        self.player.flushNotes()


if __name__ ==  "__main__":
    LeapMusicApp().run()