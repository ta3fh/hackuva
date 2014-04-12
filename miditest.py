import rtmidi_python as rtmidi
from time import sleep

midi_out = rtmidi.MidiOut()
for port_name in midi_out.ports:
    print port_name
midi_out.open_port(2)
midi_out.send_message([0x90, 50, 100]) # Note on
sleep(0.5)
midi_out.send_message([0x80, 50, 100]) # Note off

midi_out.send_message([0x90, 52, 100]) # Note on
sleep(0.5)
midi_out.send_message([0x80, 52, 100]) # Note off

midi_out.send_message([0x90, 54, 100]) # Note on
sleep(1)
midi_out.send_message([0x80, 54, 100]) # Note off