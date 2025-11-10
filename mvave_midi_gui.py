import customtkinter as ctk
import mido
import threading
from tkinter import scrolledtext

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MidiBridgeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mvave MIDI Bridge")
        self.geometry("650x600")

        self.input_port = None
        self.output_port = None
        self.listening = False
        self.learning_mode = False
        self.learning_control_id = None

        self.toggle_state = {}
        self.buttons = {}
        self.modes = {}
        self.control_vars = {}

        self.build_ui()
    
    # ---------------- UI ----------------
    def build_ui(self):
        ctk.CTkLabel(self, text="Mvave MIDI Bridge", font=("Arial", 20, "bold")).pack(pady=10)

        # ----- Puertos -----
        ports_frame = ctk.CTkFrame(self)
        ports_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(ports_frame, text="Entrada MIDI:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.input_menu = ctk.CTkOptionMenu(ports_frame, values=mido.get_input_names())
        self.input_menu.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(ports_frame, text="Salida MIDI:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.output_menu = ctk.CTkOptionMenu(ports_frame, values=mido.get_output_names())
        self.output_menu.grid(row=1, column=1, padx=5, pady=5)

        self.connect_btn = ctk.CTkButton(ports_frame, text="Conectar", command=self.toggle_connection)
        self.connect_btn.grid(row=2, column=0, columnspan=2, pady=10)

        # ----- Botón de Aprendizaje -----
        self.learn_btn = ctk.CTkButton(ports_frame, text="Aprender Controles", 
                                      command=self.toggle_learning_mode,
                                      fg_color="orange", state="disabled")
        self.learn_btn.grid(row=3, column=0, columnspan=2, pady=5)

        # ----- Controles MIDI -----
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.pack(pady=10, padx=10, fill="x")
        self.build_controls()

        # ----- Consola -----
        ctk.CTkLabel(self, text="Consola de depuración:", anchor="w").pack(pady=(10, 0), padx=10, fill="x")
        self.console = scrolledtext.ScrolledText(self, height=10, state="disabled", bg="#111", fg="#0f0")
        self.console.pack(fill="both", expand=True, padx=10, pady=5)

    def log(self, msg):
        self.console.configure(state="normal")
        self.console.insert("end", msg + "\n")
        self.console.configure(state="disabled")
        self.console.yview("end")

    # ---------------- Controles ----------------
    def build_controls(self):
        for widget in self.controls_frame.winfo_children():
            widget.destroy()

        for i in range(4):
            frame = ctk.CTkFrame(self.controls_frame)
            frame.pack(pady=5, padx=10, fill="x")

            # Valor inicial CC (editable)
            var_cc = ctk.StringVar(value="No asignado")
            control_id = f"btn_{i}"

            # Botón principal con función de aprendizaje
            btn = ctk.CTkButton(frame, text=f"Botón {i+1}: {var_cc.get()}", fg_color="gray",
                                command=lambda cid=control_id: self.start_learning_for_control(cid))
            btn.pack(side="left", padx=5, pady=5)
            self.buttons[control_id] = btn
            self.toggle_state[control_id] = False
            self.control_vars[control_id] = var_cc

            # Selector de modo
            mode_var = ctk.StringVar(value="toggle")
            mode_menu = ctk.CTkOptionMenu(frame, values=["toggle", "momentary"], variable=mode_var)
            mode_menu.pack(side="right", padx=5)
            self.modes[control_id] = mode_var

            # Campo editable de número CC (ahora solo lectura durante aprendizaje)
            ctk.CTkLabel(frame, text="CC#:").pack(side="left", padx=(10, 2))
            entry_cc = ctk.CTkEntry(frame, width=80, textvariable=var_cc, state="readonly")
            entry_cc.pack(side="left", padx=5)

    def toggle_learning_mode(self):
        """Activa/desactiva el modo de aprendizaje global"""
        if not self.learning_mode:
            self.learning_mode = True
            self.learn_btn.configure(text="Cancelar Aprendizaje", fg_color="red")
            self.log("MODO APRENDIZAJE ACTIVADO")
            self.log("Haz clic en un botón de la interfaz y luego presiona el control físico que quieres asignar")
            
            # Cambiar todos los botones a modo aprendizaje
            for control_id, btn in self.buttons.items():
                btn.configure(text=f"Aprender...", fg_color="orange")
        else:
            self.cancel_learning_mode()

    def cancel_learning_mode(self):
        """Cancela el modo de aprendizaje"""
        self.learning_mode = False
        self.learning_control_id = None
        self.learn_btn.configure(text="Aprender Controles", fg_color="orange")
        self.refresh_all_buttons()
        self.log("Modo aprendizaje cancelado")

    def start_learning_for_control(self, control_id):
        """Inicia el aprendizaje para un control específico"""
        if not self.learning_mode:
            return
            
        self.learning_control_id = control_id
        self.buttons[control_id].configure(text="¡Presiona control físico!", fg_color="yellow")
        self.log(f"Esperando input MIDI para {control_id}...")

    def refresh_all_buttons(self):
        """Actualiza todos los botones con su estado actual"""
        for control_id, btn in self.buttons.items():
            cc_value = self.control_vars[control_id].get()
            state = self.toggle_state.get(control_id, False)
            if cc_value == "No asignado":
                btn.configure(text=f"Botón {control_id[-1]}: {cc_value}", 
                            fg_color="gray")
            else:
                color = "green" if state else "red"
                btn.configure(text=f"CC {cc_value}: {'ON' if state else 'OFF'}", 
                            fg_color=color)

    def refresh_button_label(self, control_id):
        """Actualiza el texto de un botón específico"""
        btn = self.buttons.get(control_id)
        if not btn:
            return
        cc_number = self.control_vars[control_id].get()
        state = self.toggle_state.get(control_id, False)
        
        if cc_number == "No asignado":
            btn.configure(text=f"Botón {control_id[-1]}: {cc_number}")
        else:
            color = "green" if state else "red"
            btn.configure(text=f"CC {cc_number}: {'ON' if state else 'OFF'}", 
                         fg_color=color)

    # ---------------- MIDI ----------------
    def toggle_connection(self):
        if not self.listening:
            try:
                in_name = self.input_menu.get()
                out_name = self.output_menu.get()
                self.input_port = mido.open_input(in_name)
                self.output_port = mido.open_output(out_name)
                self.connect_btn.configure(text="Desconectar", fg_color="red")
                self.learn_btn.configure(state="normal")
                self.listening = True
                threading.Thread(target=self.listen_midi, daemon=True).start()
                self.log(f"Conectado a {in_name} → {out_name}")
                self.log("Presiona 'Aprender Controles' para mapear tus botones físicos")
            except Exception as e:
                self.log(f"Error al conectar: {e}")
        else:
            self.disconnect_ports()

    def disconnect_ports(self):
        self.listening = False
        self.cancel_learning_mode()
        try:
            if self.input_port:
                self.input_port.close()
            if self.output_port:
                self.output_port.close()
            self.log("Puertos MIDI desconectados.")
        except Exception as e:
            self.log(f"Error al desconectar: {e}")
        self.connect_btn.configure(text="Conectar", fg_color="green")
        self.learn_btn.configure(state="disabled")

    def listen_midi(self):
        while self.listening:
            try:
                for msg in self.input_port.iter_pending():
                    if msg.type == "control_change":
                        self.handle_cc(msg)
            except Exception as e:
                self.log(f"Error en listen_midi: {e}")
                break
        self.log("Hilo MIDI detenido.")

    def handle_cc(self, msg):
        """Maneja mensajes CC entrantes del controlador MIDI"""
        control = msg.control
        value = msg.value
        
        self.log(f"MIDI IN: CC{control} = {value}")
        
        # Si estamos en modo aprendizaje, asignar el CC al control actual
        if self.learning_mode and self.learning_control_id:
            control_id = self.learning_control_id
            self.control_vars[control_id].set(str(control))
            self.learning_control_id = None
            self.log(f"✓ Control {control_id} asignado a CC{control}")
            self.refresh_button_label(control_id)
            
            # Verificar si todos los controles están asignados
            if all(cc.get() != "No asignado" for cc in self.control_vars.values()):
                self.log("✓ Todos los controles han sido asignados!")
                self.cancel_learning_mode()
            return
        
        # Buscar qué botón está mapeado a este número CC
        matching_control_id = None
        for control_id, cc_var in self.control_vars.items():
            try:
                if cc_var.get() != "No asignado" and int(cc_var.get()) == control:
                    matching_control_id = control_id
                    break
            except ValueError:
                continue
        
        if not matching_control_id:
            self.log(f"CC{control} no está mapeado a ningún botón")
            return

        mode = self.modes[matching_control_id].get()
        
        if mode == "momentary":
            # En modo momentary, el estado sigue el valor del mensaje
            state = value > 0
        else:
            # En modo toggle, alterna el estado cuando recibe cualquier valor > 0
            current_state = self.toggle_state.get(matching_control_id, False)
            state = not current_state if value > 0 else current_state

        self.toggle_state[matching_control_id] = state
        self.refresh_button_label(matching_control_id)
        self.log(f"Control {matching_control_id} (CC{control}) → {'ON' if state else 'OFF'}")

    def send_cc(self, control, value):
        if self.output_port:
            try:
                control_int = int(control)
                if 0 <= control_int <= 127 and 0 <= value <= 127:
                    msg = mido.Message("control_change", control=control_int, value=value)
                    self.output_port.send(msg)
                    self.log(f"MIDI OUT: CC{control_int} = {value}")
                else:
                    self.log(f"Valor CC inválido: {control_int}={value}")
            except ValueError:
                self.log(f"CC inválido: {control}")

    def on_button_click(self, control_id):
        """Maneja clics en los botones de la interfaz (cuando no están en modo aprendizaje)"""
        if self.learning_mode:
            self.start_learning_for_control(control_id)
            return
            
        cc_value = self.control_vars[control_id].get()
        if cc_value == "No asignado":
            self.log(f"Error: El control {control_id} no tiene asignado un número CC")
            return
            
        try:
            cc_number = int(cc_value)
        except ValueError:
            self.log(f"CC inválido para control {control_id}: {cc_value}")
            return

        mode = self.modes[control_id].get()
        
        if mode == "momentary":
            # Envía 127 y luego 0 después de 200ms
            self.send_cc(cc_number, 127)
            self.after(200, lambda: self.send_cc(cc_number, 0))
        else:
            # Modo toggle - alterna el estado
            current_state = self.toggle_state.get(control_id, False)
            new_state = not current_state
            
            self.toggle_state[control_id] = new_state
            self.refresh_button_label(control_id)
            self.send_cc(cc_number, 127 if new_state else 0)


if __name__ == "__main__":
    app = MidiBridgeApp()
    app.mainloop()