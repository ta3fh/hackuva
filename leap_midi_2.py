from Leap import *
import rtmidi_python as rtmidi
from time import sleep

def main():
    print "AWESOME MIDI CONTROLLER!"

    sleep(1)

    leap = Controller()
    midi_out = rtmidi.MidiOut()
    midi_out.open_port(2)

    playing_notes = []
    possible_notes = [50,52,54,55,57,59,61,62,64,66,67,69,71,73,74 ]
    possible_notes = map(lambda x: x+12,possible_notes)

    for port_name in midi_out.ports:
        print port_name

    while True:
        frame = leap.frame()
        new_notes = [] # ONLY new notes
        continuing_notes = [] # ONLY continuing notes
        # for each finger
        for finger in frame.fingers:
            # calculate note
            note = int(map_range(finger.tip_position.x, -200, 200, 0, 14))
            note = possible_notes[note]
            # add to array (no duplicates)
            if note in playing_notes and note not in continuing_notes:
                continuing_notes.append(note)
            elif note not in playing_notes and note not in new_notes:
                new_notes.append(note)
        # remove non-continuing notes
        for old in playing_notes:
            if old not in continuing_notes:
                playing_notes.remove(old)
                stop_note(midi_out,old)
        # PLAY NEW NOTES
        for note in new_notes:
            start_note(midi_out,note)
            playing_notes.append(note)
        # PLEASE DELAY OH GOD
        # sleep(1)

# FUNCTIONS!!!!

def stop_note(out,note,velocity=80):
    out.send_message([0x81, note, velocity])

def start_note(out,note,velocity=80):
    out.send_message([0x91, note, velocity])

def map_range(num, min1, max1, min2, max2, clamp=True):
    percent = (num-min1)/(max1-min1)
    if clamp:
        percent = 0 if percent < 0 else percent
        percent = 1 if percent > 1 else percent
    return min2 + percent*(max2-min2)

main() # MOTHERF*CKER