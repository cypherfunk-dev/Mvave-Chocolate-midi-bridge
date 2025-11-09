# Mvave MIDI Bridge

Este pequeño script convierte los mensajes del **Mvave Chocolate** (u otros controladores MIDI Bluetooth/USB) en eventos útiles para tu DAW.  
Permite mapear switches del pedal para controlar pistas, efectos o cualquier parámetro MIDI de forma más flexible.

---

## 🚀 Instalación y configuración

### 1. Instalar **loopMIDI**
- Descarga e instala **loopMIDI** desde [https://www.tobias-erichsen.de/software/loopmidi.html](https://www.tobias-erichsen.de/software/loopmidi.html)
- Ábrelo y crea un puerto nuevo llamado **`mvave_midi`** haciendo clic en el botón **`+`**.

---

### 2. Ejecutar **mvave_midi.exe**
- Abre el archivo `mvave_midi.exe` (puedes dejarlo en ejecución mientras usas tu DAW).
- Al iniciarse, el programa te pedirá seleccionar el puerto de entrada:
  - Si usas conexión **Bluetooth**, tu dispositivo aparecerá como `FootCtrl-bt`
  - Si usas **USB-C**, aparecerá como `USB-Midi`
- Luego, selecciona **`mvave_midi`** como puerto de salida.

---

### 3. Configurar tu DAW (ejemplo: Ableton Live)
1. Abre **Ableton Live**  
2. Ve a **Opciones → Configuración → Link, Tempo & MIDI**
3. En la sección **Puertos de entrada**, busca **`mvave_midi`**
4. Activa las opciones:
   - **Pista (Track)**
   - **Remoto (Remote)**
5. Listo. Tu pedal ahora puede controlar pistas, efectos o cualquier parámetro mapeado.

---

## 💡 Consejos
- Mantén **loopMIDI** y **mvave_midi.exe** abiertos antes de iniciar tu DAW.  
- Si cambias el nombre del puerto en loopMIDI, también debes seleccionarlo al ejecutar el programa.  
- Puedes usar cualquier otro pedal o dispositivo que envíe mensajes MIDI estándar.

---

## 🧠 Autor
Proyecto experimental desarrollado para conectar controladores MIDI Bluetooth con DAWs mediante Python y Mido.  
Inspirado por la necesidad de **controlar Ableton con los pies sin gastar cientos en hardware dedicado**.


---

## ⚙️ Dependencias (solo si ejecutas el script fuente)
- Python 3.10+
- `mido`
- `python-rtmidi`

Ejemplo de instalación en Windows:
```bash
mvave_midi/Scripts/activate
pip install -r requirements.txt
python mvave_midi.py


TODO: INTERFAZ GRAFICA, SELECCION CONTROL, MEJOR MANEJO DE EXCEPCIONES