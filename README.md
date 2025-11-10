# Mvave Chocolate MIDI Bridge

This small utility converts messages from the **Mvave Chocolate** (or any other Bluetooth/USB MIDI controller) into usable events for your DAW.  
It allows you to map pedal switches to control tracks, effects, or any MIDI-mappable parameter with greater flexibility.

---

## 🚀 Installation & Setup

### 1. Install **loopMIDI**
- Install **loopMIDI** from `loopMIDISetup.exe` or [https://www.tobias-erichsen.de/software/loopmidi.html](https://www.tobias-erichsen.de/software/loopmidi.html)
- Open it and create a new port named **`mvave_midi`** by clicking the **`+`** button.

![alt text](assets/image-1.png)


### 2. Install Sinco_Connector (for Bluetooth connectivity)
- Install `Sinco_Connector.exe`
- Open **Bt Midi connector** and click on **FootCtrl**

![alt text](assets/image.png)

---

### 3. Run **mvave_midi.exe**
- Launch the `mvave_midi.exe` file (keep it running while using your DAW).
- When started, the program will ask you to select the **input port**:
  - If you’re using **Bluetooth**, the device will appear as `FootCtrl-bt`
  - If you’re using **USB-C**, it will appear as `USB-Midi`
- Then, select **`mvave_midi`** as the **output port**.

---

### 4. Configure your DAW (example: Ableton Live)
1. Open **Ableton Live**  
2. Go to **Options → Preferences → Link, Tempo & MIDI**
3. Under **MIDI Ports**, find **`mvave_midi`**
4. Enable the following options:
   - **Track**
   - **Remote**
5. Done! Your pedal can now 

![alt text](assets/image-2.png)

---

## 💡 Tips
- Keep **loopMIDI** and **mvave_midi.exe** open before launching your DAW.  
- If you rename the port in loopMIDI, make sure to select the same name when running the program.  
- You can use any other pedal or controller that sends standard MIDI messages.

---

## 🧠 Author
Experimental project developed to bridge Bluetooth MIDI controllers with DAWs using Python and Mido.  
Inspired by the need to **control Ableton with your feet without spending hundreds on dedicated hardware**.
Also, CubeSuite (official software) is a little bit unstable.

---

## ⚙️ Dependencies (if running the Python source)
- Python 3.10+
- `mido`
- `python-rtmidi`
- `customtkinter`


Example setup on Windows:
```bash
mvave_midi/Scripts/activate
pip install -r requirements.txt
python mvave_midi.py
```
To build an executable 
```bash
pyinstaller --onefile --hidden-import=mido.backends.rtmidi --hidden-import=rtmidi --icon="assets/icon.ico"  mvave_midi.py
```
## TODO

* Add graphical interface
* Control selector
* Better exception handling
