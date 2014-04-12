from Leap import *
import rtmidi_python as rtmidi
from time import sleep
import constants

class Note:

    def __init__(self, midiVal, velocity=100, channel=0):
        self.midiVal = midiVal
        self.velocity = velocity
        self.channel = channel

    def __eq__(self,other):
        return self.midiVal == other.midiVal

class Axis:
    def __init__(self, min, max, param):
        self.min = min
        self.max = max
        self.param = param

    def __eq__(self, other):
        return self.param == other.param #will only ever be called on active axes to avoid empty strings matching

class Baton:

    # def __init__(self, maxHistory, hand):
    #     self.id = hand.id
    #     self.history = [hand]
    #     self.maxHistory = maxHistory

    def __init__(self, maxHistory, hand, yParam="velocity", zParam="", rollParam="", pitchParam="", yawParam=""):
        self.id = hand.id
        self.history = [hand]
        self.maxHistory = maxHistory

        #Axes array has indices 0:x, 1:y, 2:z, 3:roll, 4:pitch, 5:yaw
        self.axes = []
        self.axes.append(Axis(constants.x_min, constants.x_max, "note")) #hard coded note value on x axis for now
        self.axes.append(Axis(constants.y_min, constants.y_max, yParam))
        self.axes.append(Axis(constants.z_min, constants.z_max, zParam))
        self.axes.append(Axis(constants.roll_min, constants.roll_max, rollParam))
        self.axes.append(Axis(constants.pitch_min, constants.pitch_max, pitchParam))
        self.axes.append(Axis(constants.yaw_min, constants.yaw_max, yawParam))
        print "created a new baton"

    #returns Axis assigned to given midi parameter
    def getAxisByAttr(self, attr):
        for axis in self.axes:
            if axis.param == attr:
                return axis
        return None #shouldn't happen, hopefully

    #returns the current LeapMotion value for an axis by calling the appropriate smoothing method for that axis
    def getAxisValue(self, axis):
        if axis == self.axes[0]:
            return self.getXValue()
        if axis == self.axes[1]:
            return self.getYValue()
        if axis == self.axes[2]:
            return self.getZValue()
        if axis == self.axes[3]:
            return self.getRollValue()
        if axis == self.axes[4]:
            return self.getPitchValue()
        if axis == self.axes[5]:
            return self.getYawValue()

    #gets all active axes, hard coded minus x axis and velocity axis
    def activeAxes(self):
        active = []
        for axis in self.axes:
            if axis.param != "" and axis.param != "velocity": #hard coded exclude velocity
                active.append(axis)
        active.pop(0) #hard coded remove x axis
        return active

    #returns a list of midi messages to player for the 'extra' axes currently assigned to a midi parameter
    def getMessages(self):
        messages = []
        for axis in self.activeAxes():
            messages.append(self.generateMessage(axis))

        print "messages: " + messages
        return messages

    #generates a midi message for an 'extra' axis to send to the player
    def generateMessage(self, axis):
        commands = {
            #'aftertouch' : 0xA0,
            'controller': 0xB0,
            #'patchchange': 0xC0,
            'channelpressure': 0xD0,
            'pitchbend': 0xE0,
            #'misc': 0xF0,
        }
        key = axis.param
        param1 = -1
        param2 = -1
        if axis.param.find("_") != -1:
            param1 = int(key[axis.param.find("_") + 1:])
            key = key[:axis.param.find("_")] #strip param so hex command remains
        if key == 'pitchbend': #need to implement MSB and LSB as two params
            pass
        elif param1 == -1: #first message param is axis value if not supplied in axis param
            param1 = int(map_range(self.getAxisValue(axis), axis.min, axis.max, 0, 127))
        else: #else second message param is axis value, because first message param was supplied on axis assignment
            param2 = int(map_range(self.getAxisValue(axis), axis.min, axis.max, 0, 124))
        command = int(commands[key] + (self.getChannel() - 1)) #apply channel to command hex
        print "MESSAGE GENERATED: " + str([command, param1, param2])
        return [command, param1, param2]



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
        return True


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

    def getNote(self, velocity=100):
        midiVal = int(map_range(self.getXValue(), constants.x_min, constants.x_max, 60, 72))
        velocity = int(map_range(self.getYValue(), constants.y_min, constants.y_max, 0, 127))
        #print "VELOCITY: " + str(map_range(self.getAxisValue(self.getAxisByAttr("velocity")), 100, 500, 0, 127))
        #velocity = int(map_range(self.getAxisValue(self.getAxisByAttr("velocity")), 100, 500, 0, 127))
        return Note(midiVal, velocity, int(self.getChannel()))


class Player:

    def __init__(self, midiOut, midiPort, smoothing=5):
        self.midiOut = midiOut
        self.midiPort = midiPort
        self.midiOut.open_port(midiPort)
        self.batons = []
        self.playing_notes = []
        self.smoothing = smoothing

    def sync(self): #handles midi messages from baton's parameters
        batons = self.batons
        notes = []
        for baton in batons:
            if len(baton.history) is not 0:
                notes.append(baton.getNote())
                #for message in baton.getMessages():
                    #self.midiOut.send_message(message)
        print notes
        for note in notes:
            if note not in self.playing_notes:
                print "playing new note!"
                self.playNote(note)
        for note in self.playing_notes:
            if note not in notes:
                self.stopNote(note)

    def playNote(self, note):
        playing_notes = self.playing_notes
        if note not in playing_notes:
            playing_notes.append(note)
            if note.channel > 0:
                #self.midiOut.send_message([0x90 + (note.channel - 1), note.midiVal, note.velocity])
                self.midiOut.send_message([0x90, note.midiVal, note.velocity])

    def stopNote(self, note):
        playing_notes = self.playing_notes
        if note in playing_notes:
            playing_notes.remove(note)
            if note.channel > 0:
                #self.midiOut.send_message([0x80 + (note.channel - 1), note.midiVal, note.velocity])
                self.midiOut.send_message([0x80, note.midiVal, note.velocity])

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


def main():

    sleep(1)

    leap = Controller()

    player = Player(rtmidi.MidiOut(), 2, 100)

    playing_notes = []
    possible_notes = [50,52,54,55,57,59,61,62]
    possible_notes = map(lambda x: x+12,possible_notes)

    while True:
        frame = leap.frame()

        hands = []
        for hand in frame.hands:
            hands.append(hand)
        player.update(hands)

        player.sync()
        sleep(1)

def map_range(num, min1, max1, min2, max2, clamp=True):
    percent = (num-min1)/(max1-min1)
    if clamp:
        percent = 0 if percent < 0 else percent
        percent = 1 if percent > 1 else percent
    return min2 + percent*(max2-min2)

main()