import rtmidi_python as rtmidi
from time import sleep

midi_out = rtmidi.MidiOut()
for port_name in midi_out.ports:
    print port_name
midi_out.open_port(2)

while 1:
    sleep(.01)
    midi_out.send_message([0x90, 50, 100]) # Note on
