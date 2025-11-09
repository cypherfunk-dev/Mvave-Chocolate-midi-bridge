# mwave_bridge.py
import mido
import time
import sys

# --- Configuration ---
SEARCH_KEYS = ["M-VAVE", "Chocolate", "FootCtrl-bt"]
VIRTUAL_OUT_NAME = "mwave_midi"
SEND_INITIAL_CONFIG = False
INITIAL_CONFIG = [
    {"type": "cc", "num": 20, "value": 127},
    {"type": "cc", "num": 21, "value": 127},
    {"type": "cc", "num": 22, "value": 127},
    {"type": "cc", "num": 23, "value": 127},
]
PITCH_MAP = {
    "button_a": {"min": -8192, "max": -4097, "note": 60},
    "button_b": {"min": -4096, "max": -1, "note": 61},
    "button_c": {"min": 0, "max": 4095, "note": 62},
    "button_d": {"min": 4096, "max": 8191, "note": 63},
}


def choose_port(ports, port_type):
    print(f"\nAvailable {port_type} ports:")
    for i, p in enumerate(ports, 1):
        print(f"  {i}. {p}")
    try:
        choice = int(input(f"\nSelect the {port_type} port number: "))
        return ports[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        sys.exit(1)


# --- List available ports ---
inputs = mido.get_input_names()
outputs = mido.get_output_names()

if not inputs:
    print("No MIDI input ports available.")
    sys.exit(1)
if not outputs:
    print("No MIDI output ports available.")
    sys.exit(1)

mwave_in = choose_port(inputs, "input")
virtual_out = choose_port(outputs + [f"(create {VIRTUAL_OUT_NAME})"], "output")

# --- Open ports ---
print(f"\nUsing input port: {mwave_in}")
try:
    inport = mido.open_input(mwave_in)
except Exception as e:
    print(f"Could not open input port: {e}")
    sys.exit(1)

if virtual_out.startswith("(create"):
    try:
        outport = mido.open_output(VIRTUAL_OUT_NAME, virtual=True)
        print(f"Created virtual output port: {VIRTUAL_OUT_NAME}")
    except Exception:
        print("Could not create virtual port. Create one manually with loopMIDI and set its name in VIRTUAL_OUT_NAME.")
        outport = None
else:
    outport = mido.open_output(virtual_out)
    print(f"Using existing output port: {virtual_out}")

# --- Toggle states ---
toggle_states = {4: False, 17: False, 18: False, 19: False}

print("\nBridge ready. Listening for messages... (Press Ctrl+C to exit)\n")

# --- Main loop ---
try:
    for msg in inport:
        print(f"IN: {msg}")

        # --- Toggle buttons ---
        if msg.type == 'control_change' and msg.control in toggle_states:
            if msg.value == 127:  # Only on press
                toggle_states[msg.control] = not toggle_states[msg.control]
                new_val = 127 if toggle_states[msg.control] else 0
                out = mido.Message('control_change', control=msg.control, value=new_val)
                if outport:
                    outport.send(out)
                print(f"> Toggle CC{msg.control} -> {'ON' if new_val == 127 else 'OFF'}")

        # --- Pitchwheel mapping ---
        elif msg.type == 'pitchwheel':
            pitch = msg.pitch
            sent = False
            for rng in PITCH_MAP.values():
                if rng["min"] <= pitch <= rng["max"]:
                    note = rng["note"]
                    out = mido.Message('note_on', note=note, velocity=127)
                    if outport:
                        outport.send(out)
                    print(f"> mapped pitch {pitch} -> NOTE {note}")
                    sent = True
                    break
            if not sent and outport:
                val = int(((pitch + 8192) / (8192 * 2)) * 127)
                cc_msg = mido.Message('control_change', control=40, value=max(0, min(127, val)))
                outport.send(cc_msg)
                print(f"> fallback: sent CC40={cc_msg.value}")

        # --- Normal forwarding ---
        elif outport and msg.type in ('note_on', 'note_off', 'control_change'):
            outport.send(msg)
            print("-> resending to Ableton:", msg)

except KeyboardInterrupt:
    print("\nClosing ports...")
    try:
        inport.close()
    except:
        pass
    try:
        if outport:
            outport.close()
    except:
        pass
    print("Goodbye.")
