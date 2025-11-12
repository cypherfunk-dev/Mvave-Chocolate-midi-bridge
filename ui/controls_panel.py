import customtkinter as ctk
from models.switch import MidiSwitch

class ControlsPanel(ctk.CTkFrame):
    def __init__(self, parent, localization, on_learn_callback, on_delete_callback):
        super().__init__(parent)
        self.localization = localization
        self.on_learn_callback = on_learn_callback
        self.on_delete_callback = on_delete_callback
        self.switch_frames = {}
        self.build_ui()
    
    def build_ui(self):
        """Construye la interfaz del panel de controles"""
        # Frame para contener los switches
        self.switches_container = ctk.CTkFrame(self)
        self.switches_container.pack(fill="x", pady=5)
    
    def add_switch(self, switch):
        """Agrega un switch a la interfaz"""
        frame = ctk.CTkFrame(self.switches_container)
        frame.pack(pady=5, padx=10, fill="x")
        
        # Botón principal del switch
        btn = ctk.CTkButton(
            frame, 
            text=f"{self.localization.t('switch')} {switch.switch_number}", 
            fg_color="gray",
            state="disabled"
        )
        btn.pack(side="left", padx=5, pady=5)
        
        # Selector de modo
        mode_menu = ctk.CTkOptionMenu(
            frame, 
            values=[self.localization.t("toggle"), self.localization.t("momentary")], 
            variable=switch.mode_var
        )
        mode_menu.pack(side="right", padx=5)
        
        # Campo CC Entrada
        ctk.CTkLabel(frame, text=self.localization.t("input_cc")).pack(side="left", padx=(10, 2))
        entry_cc = ctk.CTkEntry(frame, width=80, textvariable=switch.input_cc_var, state="readonly")
        entry_cc.pack(side="left", padx=5)
        
        # Campo CC Salida
        ctk.CTkLabel(frame, text=self.localization.t("output_cc")).pack(side="left", padx=(10, 2))
        entry_cc_out = ctk.CTkEntry(frame, width=80, textvariable=switch.output_cc_var)
        entry_cc_out.pack(side="left", padx=5)
        
        # Botón eliminar (solo para switches no por defecto)
        if not switch.is_default:
            delete_btn = ctk.CTkButton(
                frame, 
                text=self.localization.t("delete"), 
                width=60, 
                fg_color="red",
                command=lambda sid=switch.control_id: self.on_delete_callback(sid)
            )
            delete_btn.pack(side="left", padx=5)
        
        # Guardar referencia
        self.switch_frames[switch.control_id] = {
            'frame': frame,
            'button': btn,
            'mode_menu': mode_menu,
            'input_entry': entry_cc,
            'output_entry': entry_cc_out,
            'switch': switch
        }
        
        # Actualizar UI del switch
        self.refresh_switch_ui(switch.control_id)
    
    def delete_switch(self, control_id):
        """Elimina un switch de la interfaz"""
        if control_id in self.switch_frames:
            self.switch_frames[control_id]['frame'].destroy()
            del self.switch_frames[control_id]
    
    def clear_switches(self):
        """Limpia todos los switches de la interfaz"""
        # Destruir todos los frames de switches
        for control_id in list(self.switch_frames.keys()):
            self.switch_frames[control_id]['frame'].destroy()
        
        # Limpiar el diccionario
        self.switch_frames.clear()
        
        # Reconstruir el contenedor
        self.switches_container.destroy()
        self.switches_container = ctk.CTkFrame(self)
        self.switches_container.pack(fill="x", pady=5)
    
    def refresh_switch_ui(self, control_id):
        """Actualiza la UI de un switch específico"""
        if control_id in self.switch_frames:
            elements = self.switch_frames[control_id]
            switch = elements['switch']
            
            # Actualizar texto y color del botón según el estado
            if switch.input_cc_var.get() == self.localization.t("not_assigned"):
                elements['button'].configure(
                    text=f"{self.localization.t('switch')} {switch.switch_number}",
                    fg_color="gray"
                )
            else:
                color = "green" if switch.state else "red"
                btn_text = f"CC{switch.input_cc_var.get()}→CC{switch.output_cc_var.get()}: {'ON' if switch.state else 'OFF'}"
                elements['button'].configure(
                    text=btn_text,
                    fg_color=color
                )
    
    def refresh_all_switches(self):
        """Actualiza todos los switches"""
        for control_id in self.switch_frames:
            self.refresh_switch_ui(control_id)
    
    def update_learning_ui(self, learning_manager):
        """Actualiza la UI según el estado de aprendizaje"""
        for control_id, elements in self.switch_frames.items():
            if (learning_manager.learning_mode and 
                learning_manager.learning_control_id == control_id):
                
                if learning_manager.learning_cc_out:
                    elements['button'].configure(
                        text="¡Presiona CC salida!", 
                        fg_color="purple"
                    )
                else:
                    elements['button'].configure(
                        text="¡Presiona control físico!", 
                        fg_color="yellow"
                    )
            elif learning_manager.learning_mode:
                elements['button'].configure(
                    text="Aprender...", 
                    fg_color="orange"
                )
            else:
                self.refresh_switch_ui(control_id)