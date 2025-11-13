import customtkinter as ctk
import os, sys
import json
from tkinter import filedialog

from utils.localization import Localization
from midi.manager import MidiManager
from midi.learning import LearningManager
from ui.midi_ports import MidiPortsPanel
from ui.controls_panel import ControlsPanel
from ui.console import ConsolePanel
from utils.file_utils import FileManager
from models.configuration import AppConfiguration
from models.switch import MidiSwitch
from config.settings import AppSettings

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



ctk.set_appearance_mode("dark")  # o "light" o "system"

# Ruta al tema personalizado (por ejemplo, themes/custom_theme.json)
theme_path = os.path.join(os.path.dirname(__file__), "..", "config", "custom_theme.json")
ctk.set_default_color_theme(theme_path)




class MidiBridgeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.styles = self.load_styles()


        self.title(self.styles["window"]["title"])
        self.geometry(self.styles["window"]["geometry"])
        self.iconbitmap(resource_path("assets/icon.ico"))  # importante: ruta válida al ícono

        
        # Inicializar componentes
        self.localization = Localization()
        self.midi_manager = MidiManager()
        self.learning_manager = LearningManager()
        self.file_manager = FileManager()
        self.settings = AppSettings()
        self.configuration = AppConfiguration()
        
        # Estado de la aplicación
        self.switches = {}
        self.is_connected = False
        
        self.build_ui()
        self.initialize_default_switches()
        self.load_configuration_auto()
    
    def build_ui(self):
        """Construye la interfaz principal"""
        # Frame principal
        main_frame = ctk.CTkFrame(self, corner_radius=2)
        main_frame.pack(fill="both", expand=True, padx=8, pady=8)  # Reducido padding

        # Título
        ctk.CTkLabel(main_frame, text=self.localization.t("app_title"), 
                    font=("Arial", 20, "bold")).pack(pady=8)

        # Panel de configuración
        self.config_frame = ctk.CTkFrame(main_frame, corner_radius=2)
        self.config_frame.pack(pady=8, padx=8, fill="x")
        self.build_configuration_panel()

        # Panel de controles MIDI - ¡PASAR LOS ESTILOS!
        self.controls_panel = ControlsPanel(
            self.config_frame, 
            self.localization, 
            self.on_learn_request, 
            self.on_delete_switch,
            self.styles  # ← ESTA LÍNEA FALTA
        )
        self.controls_panel.pack(fill="x", pady=5)

        # Botón agregar switch
        self.add_switch_btn = ctk.CTkButton(
            self.config_frame, 
            text=f"+ {self.localization.t('add_switch')}", 
            command=self.add_new_switch, 
            fg_color=self.styles["buttons"]["add_switch"]["fg_color"]  # ← De JSON
        )
        self.add_switch_btn.pack(pady=10)
        self.update_add_button_state()

        # Consola
        self.console_panel = ConsolePanel(main_frame, self.localization)
        self.console_panel.pack(fill="both", expand=True, pady=10, padx=10)




    def build_configuration_panel(self):
        """Construye el panel de configuración"""
        # Fila 1: Idioma - corner_radius mínimo
        row1_frame = ctk.CTkFrame(self.config_frame)
        row1_frame.pack(fill="x", pady=4)
        self.language_menu = ctk.CTkOptionMenu(
            row1_frame, 
            values=["es", "en"], 
            command=self.change_language,
            width=60,
            height=28,
            corner_radius=2
        )
        self.language_menu.set(self.localization.current_language)
        self.language_menu.pack(side="right", padx=6)

        # Fila 2: Puertos MIDI - INPUT IZQUIERDA, OUTPUT DERECHA
        row2_frame = ctk.CTkFrame(self.config_frame, corner_radius=2)
        row2_frame.pack(fill="x", pady=(20, 25))

        # MIDI INPUT - ALINEADO A LA IZQUIERDA
        input_container = ctk.CTkFrame(row2_frame, fg_color="transparent")
        input_container.pack(side="left", padx=6)
        
        ctk.CTkLabel(input_container, text=self.localization.t("input_midi")).pack(side="left", padx=(0, 6))
        self.input_menu = ctk.CTkOptionMenu(
            input_container, 
            values=self.get_input_ports(),
            width=180,
            height=28,
            corner_radius=2
        )
        self.input_menu.pack(side="left")

        # MIDI OUTPUT - ALINEADO A LA DERECHA
        output_container = ctk.CTkFrame(row2_frame, fg_color="transparent")
        output_container.pack(side="right", padx=6)
        
        ctk.CTkLabel(output_container, text=self.localization.t("output_midi")).pack(side="left", padx=(0, 6))
        self.output_menu = ctk.CTkOptionMenu(
            output_container, 
            values=self.get_output_ports(),
            width=180,
            height=28,
            corner_radius=2
        )
        self.output_menu.pack(side="left")

        # Fila 3: Botones CONECTAR/APRENDER - CENTRADOS
        row3_frame = ctk.CTkFrame(self.config_frame, corner_radius=2, fg_color="transparent")
        row3_frame.pack(fill="x", pady=4)
        
        # Contenedor interno para centrar botones
        button_container1 = ctk.CTkFrame(row3_frame, fg_color="transparent")
        button_container1.pack(expand=True, anchor="center")
        
        self.connect_btn = ctk.CTkButton(
            button_container1, 
            text=self.localization.t("connect"), 
            command=self.toggle_connection,
            width=120,
            height=32,
            corner_radius=4
        )
        self.connect_btn.pack(side="left", padx=6)

        self.learn_btn = ctk.CTkButton(
            button_container1, 
            text=self.localization.t("learn_controls"), 
            command=self.toggle_learning_mode,
            fg_color=self.styles["buttons"]["learn"]["inactive_fg_color"],
            state="disabled",
            width=120,
            height=32,
            corner_radius=4
        )
        self.learn_btn.pack(side="left", padx=6)

        # Fila 4: Botones GUARDAR/CARGAR - CENTRADOS
        row4_frame = ctk.CTkFrame(self.config_frame, corner_radius=2, fg_color="transparent")
        row4_frame.pack(fill="x", pady=25)
        
        # Contenedor interno para centrar botones
        button_container2 = ctk.CTkFrame(row4_frame, fg_color="transparent")
        button_container2.pack(expand=True, anchor="center")

        self.save_btn = ctk.CTkButton(
            button_container2, 
            text=self.localization.t("save_config"), 
            command=self.save_configuration,
            fg_color=self.styles["buttons"]["save"]["fg_color"],
            width=120,
            height=32,
            corner_radius=4
        )
        self.save_btn.pack(side="left", padx=6)

        self.load_btn = ctk.CTkButton(
            button_container2, 
            text=self.localization.t("load_config"), 
            command=self.load_configuration,
            fg_color=self.styles["buttons"]["load"]["fg_color"],
            width=120,
            height=32,
            corner_radius=4
        )
        self.load_btn.pack(side="left", padx=6)





    def get_input_ports(self):
        """Obtiene lista de puertos de entrada truncados"""
        return self.midi_manager.get_input_ports_truncated()

    def get_output_ports(self):
        """Obtiene lista de puertos de salida truncados"""
        return self.midi_manager.get_output_ports_truncated()

    def initialize_default_switches(self):
        """Inicializa los switches por defecto"""
        for i in range(self.settings.DEFAULT_SWITCHES):
            control_id = f"btn_{i}"
            switch = MidiSwitch(control_id, i + 1)
            self.switches[control_id] = switch
            self.controls_panel.add_switch(switch)

    def change_language(self, language):
        """Cambia el idioma de la aplicación - VERSIÓN OPTIMIZADA"""
        if language != self.localization.current_language:
            self.localization.current_language = language
            self.update_ui_texts()















    def load_styles(self):
        """Carga los estilos desde el archivo JSON"""
        try:
            styles_path = resource_path("config/styles.json")
            with open(styles_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error cargando estilos: {e}")
            return self.get_default_styles()

    def get_default_styles(self):
        """Proporciona estilos por defecto si no se puede cargar el JSON"""
        return {
            "window": {
                "title": "Bluetooth MIDI Bridge",
                "geometry": "800x750",
                "icon": "assets/icon.ico"
            },
            "buttons": {
                "connect": {
                    "connected_fg_color": "red",
                    "disconnected_fg_color": "green"
                },
                "learn": {
                    "active_fg_color": "red", 
                    "inactive_fg_color": "#FEF6C9"
                },
                "add_switch": {
                    "fg_color": "green"
                },
                "save": {
                    "fg_color": "green"
                },
                "load": {
                    "fg_color": "blue"
                }
            }
            # Puedes agregar más estilos por defecto aquí
        }




    def rebuild_ui(self):
        """Reconstruye completamente la interfaz"""
        # Guardar estado actual
        was_connected = self.is_connected
        
        # Reconstruir UI
        for widget in self.winfo_children():
            widget.destroy()
        
        self.build_ui()
        
        # Restaurar switches
        for control_id, switch in self.switches.items():
            self.controls_panel.add_switch(switch)
        
        # Restaurar estado de conexión
        if was_connected:
            self.connect_btn.configure(text=self.localization.t("disconnect"), fg_color="red")
            self.learn_btn.configure(
                state="normal",
                    fg_color=self.styles["buttons"]["learn"]["ready_fg_color"]
        )






    def on_learn_request(self, control_id, is_output=False):
        """Maneja solicitud de aprendizaje - VERSIÓN CORREGIDA"""
        self.console_panel.log(f"DEBUG: on_learn_request - control_id: {control_id}, is_output: {is_output}")
        
        if not self.is_connected:
            self.console_panel.log("Error: Primero debes conectar los puertos MIDI")
            return
        
        # Si ya estamos en modo aprendizaje para ESTE control, cancelarlo
        if (self.learning_manager.learning_mode and 
            self.learning_manager.learning_control_id == control_id):
            self.learning_manager.learning_control_id = None
            self.console_panel.log(f"Aprendizaje cancelado para {control_id}")
            self.update_learning_ui()
            return
        
        # Activar modo aprendizaje para este control específico
        self.learning_manager.learning_mode = True  # ← Asegurar que el modo global esté activo
        if is_output:
            self.learning_manager.start_learning_output(control_id)
            self.console_panel.log(f"DEBUG: learning_control_id establecido a: {control_id} (output)")
        else:
            self.learning_manager.start_learning_input(control_id)
            self.console_panel.log(f"DEBUG: learning_control_id establecido a: {control_id} (input)")
        
        self.update_learning_ui()








    def update_learning_ui(self):
        """Actualiza la UI según el estado de aprendizaje"""
        self.controls_panel.update_learning_ui(self.learning_manager)

    def on_delete_switch(self, control_id):
        """Maneja eliminación de switch"""
        if control_id in self.switches:
            # No permitir eliminar switches por defecto
            if self.switches[control_id].is_default:
                self.console_panel.log(f"No se pueden eliminar los primeros {self.settings.DEFAULT_SWITCHES} switches")
                return
            
            del self.switches[control_id]
            self.controls_panel.delete_switch(control_id)
            self.update_add_button_state()
            self.console_panel.log(f"Switch {control_id} eliminado")

    def on_mode_change(self, control_id, new_mode):
        """Maneja cambio de modo en un switch"""
        if control_id in self.switches:
            self.switches[control_id].mode_var.set(new_mode)

    def add_new_switch(self):
        """Agrega un nuevo switch"""
        if len(self.switches) >= self.settings.MAX_SWITCHES:
            self.console_panel.log(f"Límite máximo alcanzado: {self.settings.MAX_SWITCHES} switches")
            return
        
        # Encontrar próximo ID disponible
        existing_ids = [int(ctrl_id.split('_')[1]) for ctrl_id in self.switches.keys()]
        next_id = max(existing_ids) + 1 if existing_ids else self.settings.DEFAULT_SWITCHES
        
        control_id = f"btn_{next_id}"
        switch = MidiSwitch(control_id, next_id + 1)
        self.switches[control_id] = switch
        self.controls_panel.add_switch(switch)
        self.update_add_button_state()
        
        self.console_panel.log(f"Nuevo switch agregado: {control_id}")

    def update_add_button_state(self):
        """Actualiza estado del botón agregar"""
        if len(self.switches) >= self.settings.MAX_SWITCHES:
            self.add_switch_btn.configure(
                state="disabled", 
                text=f"{self.localization.t('limit_reached')} ({self.settings.MAX_SWITCHES})"
            )
        else:
            self.add_switch_btn.configure(
                state="normal", 
                text=f"+ {self.localization.t('add_switch')} ({len(self.switches)}/{self.settings.MAX_SWITCHES})"
            )

    def toggle_connection(self):
        """Conecta/desconecta puertos MIDI"""
        if not self.is_connected:
            self.connect_ports()
        else:
            self.disconnect_ports()




    def connect_ports(self):
        """Conecta a los puertos MIDI"""
        input_port = self.input_menu.get()
        output_port = self.output_menu.get()
        
        if self.midi_manager.connect_ports(input_port, output_port, self.on_midi_message):
            self.is_connected = True
            self.connect_btn.configure(
                text=self.localization.t("disconnect"), 
                fg_color=self.styles["buttons"]["connect"]["connected_fg_color"]
            )
            # CAMBIAR: Usar el mismo color que Load Config
            self.learn_btn.configure(
                state="normal",
                fg_color=self.styles["buttons"]["load"]["fg_color"]  # ← Mismo color que Load Config
            )
            self.console_panel.log(f"Conectado a {input_port} → {output_port}")
            return True
        else:
            self.console_panel.log("Error al conectar puertos MIDI")
            return False








    def disconnect_ports(self):
        """Desconecta los puertos MIDI"""
        self.midi_manager.disconnect_ports()
        self.is_connected = False
        self.connect_btn.configure(
            text=self.localization.t("connect"), 
            fg_color=self.styles["buttons"]["connect"]["disconnected_fg_color"]
        )
        # CAMBIAR: Volver al color original cuando está desconectado
        self.learn_btn.configure(
            state="disabled",
            fg_color=self.styles["buttons"]["learn"]["inactive_fg_color"]  # ← Color original deshabilitado
        )
        self.learning_manager.cancel_learning()
        self.console_panel.log("Puertos MIDI desconectados")







    def on_midi_message(self, msg):
        """Maneja mensajes MIDI entrantes"""
        if msg.type == "control_change":
            self.handle_cc_message(msg)

    def handle_cc_message(self, msg):
        """Maneja mensajes CC específicos"""
        control = msg.control
        value = msg.value
        
        self.console_panel.log(f"MIDI IN: CC{control} = {value}")
        
        # Modo aprendizaje
        if self.learning_manager.learning_mode and self.learning_manager.learning_control_id:
            self.handle_learning_message(control)
            return
        
        # Mapeo normal
        self.handle_normal_mapping(control, value)




    def handle_learning_message(self, control):
        """Maneja mensajes en modo aprendizaje"""
        control_id = self.learning_manager.learning_control_id
        
        if self.learning_manager.learning_cc_out:
            # Aprendiendo CC de salida
            if control_id in self.switches:
                self.switches[control_id].output_cc_var.set(str(control))
                self.console_panel.log(f"CC SALIDA para {control_id} asignado a CC{control}")
        else:
            # Aprendiendo CC de entrada
            if control_id in self.switches:
                self.switches[control_id].input_cc_var.set(str(control))
                self.console_panel.log(f"CC ENTRADA para {control_id} asignado a CC{control}")
        
        # RESET COMPLETO del modo aprendizaje
        self.learning_manager.learning_control_id = None
        self.learning_manager.learning_cc_out = False
        self.learning_manager.learning_mode = False

        # CAMBIAR: Usar el mismo color que Load Config
        self.learn_btn.configure(
            text=self.localization.t("learn_controls"), 
            fg_color=self.styles["buttons"]["load"]["fg_color"]  # ← Mismo color que Load Config
        )
        
        # ACTUALIZACIÓN COMPLETA DE LA UI
        self.controls_panel.refresh_all_switches()




    def handle_normal_mapping(self, control, value):
        """Maneja mapeo normal de CC - VERSIÓN OPTIMIZADA"""
        # Buscar switch
        matching_switch = None
        for switch in self.switches.values():
            try:
                input_cc_value = switch.input_cc_var.get()
                if (input_cc_value != self.localization.t("not_assigned") and 
                    int(input_cc_value) == control):
                    matching_switch = switch
                    break
            except ValueError:
                continue
    
        if not matching_switch:
            return
    
        mode = matching_switch.mode_var.get().lower()
        old_state = matching_switch.state
    
    # Lógica de estado
        if "toggle" in mode:
            # TOGGLE: Solo en press (valor > 0)
            if value > 0:
                matching_switch.state = not old_state
            else:
                return  # Ignorar release
        else:
            # MOMENTARY: Seguir valor
            matching_switch.state = value > 0
        
        # Solo enviar MIDI si el estado cambió
        if matching_switch.state != old_state:
            self.controls_panel.refresh_switch_ui(matching_switch.control_id)
            
            try:
                output_cc = int(matching_switch.output_cc_var.get())
                output_value = 127 if matching_switch.state else 0
                self.midi_manager.send_cc(output_cc, output_value)
                self.console_panel.log(f"MIDI OUT: CC{output_cc} = {output_value} ({'ON' if matching_switch.state else 'OFF'})")
            except ValueError:
                pass


    def update_ui_texts(self):
        """Actualiza solo los textos de la UI - VERSIÓN RÁPIDA"""
        # Botones principales
        self.connect_btn.configure(text=self.localization.t("connect") if not self.is_connected else self.localization.t("disconnect"))
        self.learn_btn.configure(text=self.localization.t("learn_controls"))
        self.save_btn.configure(text=self.localization.t("save_config"))
        self.load_btn.configure(text=self.localization.t("load_config"))
        self.add_switch_btn.configure(text=f"+ {self.localization.t('add_switch')}")
        
        # Labels de configuración
        for widget in self.config_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkLabel):
                        text = child.cget("text")
                        if text in ["Idioma:", "Language:"]:
                            child.configure(text=self.localization.t("language"))
                        elif text in ["Entrada MIDI:", "MIDI Input:"]:
                            child.configure(text=self.localization.t("input_midi"))
                        elif text in ["Salida MIDI:", "MIDI Output:"]:
                            child.configure(text=self.localization.t("output_midi"))
        
        # Actualizar controles (solo lo esencial)
        self.controls_panel.update_all_texts_fast()



    def toggle_learning_mode(self):
        """Activa/desactiva modo aprendizaje global - VERSIÓN CORREGIDA"""
        if not self.learning_manager.learning_mode:
            # ACTIVAR modo aprendizaje
            self.learning_manager.learning_mode = True
            self.learning_manager.learning_cc_out = False
            self.learning_manager.learning_control_id = None  # ← Asegurar que empiece sin control específico
            self.learn_btn.configure(
                text=self.localization.t("cancel_learn"), 
                fg_color=self.styles["buttons"]["learn"]["active_fg_color"]  # ← De JSON
            )
            self.console_panel.log(self.localization.t("learn_mode_active"))
            self.console_panel.log(self.localization.t("learn_instructions"))
            self.update_learning_ui()
        else:
            # DESACTIVAR modo aprendizaje COMPLETAMENTE
            self.cancel_learning_mode()



    def cancel_learning_mode(self):
        """Cancela el modo aprendizaje COMPLETAMENTE"""
        self.learning_manager.cancel_learning()
        self.learn_btn.configure(
            text=self.localization.t("learn_controls"), 
            fg_color=self.styles["buttons"]["learn"]["inactive_fg_color"]  # ← Color normal
        )
        self.console_panel.log("Modo aprendizaje cancelado")
        # Actualizar UI inmediatamente
        self.controls_panel.refresh_all_switches()





    def save_configuration(self):
        """Guarda la configuración actual"""
        config = {
            "language": self.localization.current_language,
            "input_port": self.input_menu.get(),
            "output_port": self.output_menu.get(),
            "switches": {}
        }
        
        for control_id, switch in self.switches.items():
            config["switches"][control_id] = {
                "input_cc": switch.input_cc_var.get(),
                "output_cc": switch.output_cc_var.get(),
                "mode": switch.mode_var.get(),
                "state": switch.state
            }
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title=self.localization.t("save_config"),
            initialfile=self.settings.DEFAULT_CONFIG_FILE
        )
        
        if file_path and self.file_manager.save_configuration(config, file_path):
            self.console_panel.log(f"{self.localization.t('config_saved')}: {file_path}")

    def load_configuration(self):
        """Carga configuración desde archivo"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title=self.localization.t("load_config"),
            initialfile=self.settings.DEFAULT_CONFIG_FILE
        )
        
        if file_path:
            self.load_config_from_file(file_path)

    def load_configuration_auto(self):
        """Carga configuración automáticamente al iniciar"""
        config_path = self.settings.DEFAULT_CONFIG_FILE
        if os.path.exists(config_path):
            self.load_config_from_file(config_path)

    def load_config_from_file(self, file_path):
        """Carga configuración desde archivo específico"""
        config = self.file_manager.load_configuration(file_path)
        if not config:
            self.console_panel.log("Error cargando configuración")
            return
        
        # Guardar estado de conexión
        was_connected = self.is_connected
        if was_connected:
            self.disconnect_ports()
        
        # Cargar configuración
        self.apply_configuration(config)
        
        # Reconectar si estaba conectado
        if was_connected:
            self.after(100, self.connect_ports)
        
        self.console_panel.log(f"{self.localization.t('config_loaded')}: {file_path}")

    def apply_configuration(self, config):
        """Aplica configuración cargada"""
        # Idioma
        if "language" in config and config["language"] != self.localization.current_language:
            self.localization.current_language = config["language"]
            self.rebuild_ui()
        
        # Puertos MIDI
        if "input_port" in config:
            self.input_menu.set(config["input_port"])
        if "output_port" in config:
            self.output_menu.set(config["output_port"])
        
        # Switches
        self.switches.clear()
        if "switches" in config:
            for control_id, switch_config in config["switches"].items():
                switch = MidiSwitch(control_id, int(control_id.split('_')[1]) + 1)
                switch.input_cc_var.set(switch_config.get("input_cc", self.localization.t("not_assigned")))
                switch.output_cc_var.set(switch_config.get("output_cc", str(10 + int(control_id.split('_')[1]))))
                switch.mode_var.set(switch_config.get("mode", "toggle"))
                switch.state = switch_config.get("state", False)
                self.switches[control_id] = switch
        
        # Actualizar UI
        self.controls_panel.clear_switches()
        for switch in self.switches.values():
            self.controls_panel.add_switch(switch)
        
        self.update_add_button_state()

    def __del__(self):
        """Destructor - asegura que los puertos MIDI se cierren"""
        if self.is_connected:
            self.midi_manager.disconnect_ports()