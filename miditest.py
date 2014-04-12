import rtmidi_python as rtmidi

midi_out = rtmidi.MidiOut()
for port_name in midi_out.ports:
    print port_name