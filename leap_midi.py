from Leap import *
import rtmidi_python as rtmidi
from time import sleep

def main():
    print "AWESOME MIDI CONTROLLER!"

    sleep(1)

    leap = Controller()
    midi_out = rtmidi.MidiOut()
    midi_out.open_port(2)

    last_note = None

    while True:
        frame = leap.frame()
        fingers = frame.fingers
        if fingers.is_empty and last_note is not None:
            stop_note(midi_out,last_note)
        else:
            f = fingers.frontmost
            note = int(map_range(f.tip_position.y, 0, 512, 50, 70))
            if last_note == note:
                pass
            else:
                if last_note is not None:
                    stop_note(midi_out,last_note)
                start_note(midi_out,note)
                last_note = note


# FUNCTIONS!!!!

def stop_note(out,note,velocity=100):
    out.send_message([0x80, note, velocity])

def start_note(out,note,velocity=100):
    out.send_message([0x90, note, velocity])

def map_range(num, min1, max1, min2, max2, clamp=True):
    percent = (num-min1)/(max1-min1)
    if clamp:
        percent = 0 if percent < 0 else percent
        percent = 1 if percent > 1 else percent
    return min2 + percent*(max2-min2)

main() # MOTHERF*CKER