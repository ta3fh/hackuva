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

class Baton:

    def __init__(self, maxHistory, hand, note="", velocity="", controller="y", aftertouch = "",
                 pitchbend = "", pressure = "" ):
        self.id = hand.id
        self.history = [hand]
        self.maxHistory = maxHistory
        self.config = [note, velocity, controller, aftertouch, pressure, pitchbend]
        self.scale = [50,53,55,57,60]
        self.scale += map(lambda x: x+12, self.scale)
        self.scale.append(self.scale[0]+24)

        print "created a new baton"

    def getVals(self):
        config = self.config
        ret = []
        for axis in config: #note, velocity, controller, aftertouch, pressure
            if config.index(axis) == 5:
                break
            if axis == "":
                ret.append(None)
            elif axis == "x":
                idx = int(map_range(self.getXValue(), constants.x_min, constants.x_max, 0, len(self.scale)-1))
                ret.append( self.scale[idx] )
            elif axis == "y":
                ret.append(int(map_range(self.getYValue(), constants.y_min, constants.y_max, 80, 127)))
            elif axis == "z":
                ret.append(int(map_range(self.getZValue(), constants.z_min, constants.z_max, 0, 127)))
            elif axis == "pitch":
                ret.append(int(map_range(self.getPitchValue(), constants.pitch_min, constants.pitch_max, 0, 127)))
            elif axis == "roll":
                ret.append(int(map_range(self.getRollValue(), constants.roll_min, constants.roll_max, 0, 127)))
            elif axis == "yaw":
                ret.append(int(map_range(self.getYawValue(), constants.yaw_min, constants.yaw_max, 0, 127)))

        if config[5] == "": #pitchbend because MSB and LSB
            ret.append(None)
        elif config[5] == "x":
            ret.append(int(map_range(self.getXValue(), constants.x_min, constants.x_max, 0x0, 0x7f)))
        elif config[5] == "y":
            ret.append(int(map_range(self.getYValue(), constants.y_min, constants.y_max, 0x0, 0x7f)))
        elif config[5] == "z":
            ret.append(int(map_range(self.getZValue(), constants.z_min, constants.z_max, 0x0, 0x7f)))
        elif config[5] == "pitch":
            ret.append(int(map_range(self.getPitchValue(), constants.pitch_min, constants.pitch_max, 0x0, 0x7f)))
        elif config[5] == "roll":
            ret.append(int(map_range(self.getRollValue(), constants.roll_min, constants.roll_max, 0x0, 0x7f)))
        elif config[5] == "yaw":
            ret.append(int(map_range(self.getYawValue(), constants.yaw_min, constants.yaw_max, 0x0, 0x7f)))

        return ret

    def generateMessages(self):
        messages = []
        vals = self.getVals()

        velocity = constants.velocity_default
        if vals[1] is not None:
            velocity = vals[1]

        #note and aftertouch
        if vals[0] is not None:
            messages.append([constants.noteon, vals[0], velocity])
            if vals[3] is not None:
                messages.append([constants.aftertouch, vals[0], vals[3]])

        #controller
        if vals[2] is not None:
            messages.append([constants.controller, 1, vals[2]]) #TODO: implement variable controller parameter

        #pressure
        if vals[4] is not None:
            messages.append([constants.channelpressure, vals[4]])

        #pitchbend
        if vals[5] is not None:
            hexy = hex(vals[5])
            msb = hexy[2:4]
            lsb = hexy[4:]
            messages.append([constants.pitchbend, int(lsb), int(msb)])
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
        self.midiPort = midiPort
        self.midiOut.open_port(midiPort)
        self.batons = []
        self.playing_notes = []
        self.smoothing = smoothing

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
                    print "Playing new note"
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
                    # STOP PLAYING NOTES!!!
                    print "Removed batons, %d remaining" % len(self.batons)

def main():
    # sleep(1)

    leap = Controller()

    player = Player(rtmidi.MidiOut(), 2, 50)

    playing_notes = []
    possible_notes = [50,52,54,55,57,59,61,62]
    possible_notes = map(lambda x: x+12,possible_notes)

    while True:
        frame = leap.frame()

        hands = []
        for hand in frame.hands:
            if True or hand.palm_position.z < 0:
                hands.append(hand)
        player.update(hands)

        player.sync()
        #sleep(1.0/10.0)

def map_range(num, min1, max1, min2, max2, clamp=True):
    percent = (num-min1)/(max1-min1)
    if clamp:
        percent = 0 if percent < 0 else percent
        percent = 1 if percent > 1 else percent
    return min2 + percent*(max2-min2)

main()