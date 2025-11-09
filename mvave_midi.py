# mwave_bridge.py
import mido
import time
import sys

# --- Configuración ---
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

def elegir_puerto(puertos, tipo):
    print(f"\nPuertos {tipo} disponibles:")
    for i, p in enumerate(puertos, 1):
        print(f"  {i}. {p}")
    try:
        eleccion = int(input(f"\nSelecciona el número del puerto {tipo}: "))
        return puertos[eleccion - 1]
    except (ValueError, IndexError):
        print("Selección inválida.")
        sys.exit(1)

# --- Listar puertos disponibles ---
inputs = mido.get_input_names()
outputs = mido.get_output_names()

if not inputs:
    print("No hay puertos de entrada MIDI disponibles.")
    sys.exit(1)
if not outputs:
    print("No hay puertos de salida MIDI disponibles.")
    sys.exit(1)

mwave_in = elegir_puerto(inputs, "de entrada")
virtual_out = elegir_puerto(outputs + [f"(crear {VIRTUAL_OUT_NAME})"], "de salida")

# --- Abrir puertos ---
print(f"\nUsando puerto de entrada: {mwave_in}")
try:
    inport = mido.open_input(mwave_in)
except Exception as e:
    print(f"No se pudo abrir el puerto de entrada: {e}")
    sys.exit(1)

if virtual_out.startswith("(crear"):
    try:
        outport = mido.open_output(VIRTUAL_OUT_NAME, virtual=True)
        print(f"Creado puerto virtual de salida: {VIRTUAL_OUT_NAME}")
    except Exception:
        print("No se pudo crear puerto virtual. Crea uno con loopMIDI e indícalo en VIRTUAL_OUT_NAME.")
        outport = None
else:
    outport = mido.open_output(virtual_out)
    print(f"Usando puerto de salida existente: {virtual_out}")

# --- Estados toggle ---
toggle_states = {4: False, 17: False, 18: False, 19: False}

print("\nBridge listo. Escuchando mensajes... (Ctrl+C para salir)\n")

# --- Bucle principal ---
try:
    for msg in inport:
        print(f"IN: {msg}")

        # --- Botones tipo toggle ---
        if msg.type == 'control_change' and msg.control in toggle_states:
            if msg.value == 127:  # Solo al presionar
                toggle_states[msg.control] = not toggle_states[msg.control]
                new_val = 127 if toggle_states[msg.control] else 0
                out = mido.Message('control_change', control=msg.control, value=new_val)
                if outport:
                    outport.send(out)
                print(f"> Toggle CC{msg.control} -> {'ON' if new_val == 127 else 'OFF'}")

        # --- Mapeo Pitchwheel ---
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

        # --- Reenvío normal ---
        elif outport and msg.type in ('note_on', 'note_off', 'control_change'):
            outport.send(msg)
            print("-> reenviado a Ableton:", msg)

except KeyboardInterrupt:
    print("\nCerrando puertos...")
    try: inport.close()
    except: pass
    try:
        if outport: outport.close()
    except: pass
    print("Adiós.")
