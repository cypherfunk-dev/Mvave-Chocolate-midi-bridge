import customtkinter as ctk
from models.switch import MidiSwitch

class ControlsPanel(ctk.CTkFrame):
    def __init__(self, parent, localization, on_learn_callback, on_delete_callback, styles):
        super().__init__(parent)
        self.localization = localization
        self.on_learn_callback = on_learn_callback
        self.on_delete_callback = on_delete_callback
        self.styles = styles  # ← Recibir estilos
        self.switch_frames = {}
        self.build_ui()  # ← Esto se queda igual, pero ahora styles está disponible
    
    def build_ui(self):
        """Construye la interfaz del panel de controles"""
        # Frame para contener los switches
        self.switches_container = ctk.CTkFrame(self, border_width=1, corner_radius=2)
        self.switches_container.pack(fill="x", pady=5)  

    def add_switch(self, switch):
        """Agrega un switch a la interfaz"""
        frame = ctk.CTkFrame(self.switches_container, border_width=1, corner_radius=2)
        frame.pack(pady=5, padx=10, fill="x")
        
        # Botón principal del switch
        btn = ctk.CTkButton(
            frame, 
            text=f"{self.localization.t('switch')} {switch.switch_number}", 
            fg_color=self.styles["switch_states"]["unassigned"],  # ← De JSON
            state="disabled",
            command=lambda sid=switch.control_id: self.on_learn_callback(sid, False)
        )
        btn.pack(side="left", padx=5, pady=5)
        
        # ✅ SELECTOR DE MODO (SOLO UNO) - CON TRADUCCIÓN
        mode_display_values = [self.localization.t("toggle"), self.localization.t("momentary")]
        mode_var = switch.mode_var

        def on_mode_change(new_display_value):
            # Convertir texto mostrado a valor interno
            if new_display_value == self.localization.t("toggle"):
                mode_var.set("toggle")
            elif new_display_value == self.localization.t("momentary"):
                mode_var.set("momentary")
        
        # Configurar valor inicial del display
        current_internal_value = mode_var.get()
        if current_internal_value == "toggle":
            current_display_value = self.localization.t("toggle")
        else:
            current_display_value = self.localization.t("momentary")
        
        mode_menu = ctk.CTkOptionMenu(
            frame, 
            values=mode_display_values,
            variable=ctk.StringVar(value=current_display_value),
            command=on_mode_change
        )
        mode_menu.pack(side="right", padx=5)
        
        # Campo CC Entrada
        ctk.CTkLabel(frame, text=self.localization.t("input_cc")).pack(side="left", padx=(10, 2))
        entry_cc = ctk.CTkEntry(frame, width=100, textvariable=switch.input_cc_var, state="readonly")
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
                fg_color=self.styles["buttons"]["delete"]["fg_color"],  # ← De JSON
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
        if control_id in self.switch_frames:
            elements = self.switch_frames[control_id]
            switch = elements['switch']
            
            input_cc_value = switch.input_cc_var.get()
            not_assigned_text = self.localization.t("not_assigned")
            
            # ✅ Verificar si es un número CC válido
            is_assigned = True
            try:
                cc_num = int(input_cc_value)
                if cc_num < 0 or cc_num > 127:
                    is_assigned = False
            except ValueError:
                if input_cc_value == not_assigned_text:
                    is_assigned = False
                else:
                    is_assigned = False
                    switch.input_cc_var.set(not_assigned_text)
            
            if not is_assigned:
                elements['button'].configure(
                    text=f"{self.localization.t('switch')} {switch.switch_number}",
                    fg_color=self.styles["switch_states"]["unassigned"],  # ← De JSON
                    state="disabled"
                )
            else:
                # Usar colores del JSON según el estado
                color = self.styles["switch_states"]["assigned_on"] if switch.state else self.styles["switch_states"]["assigned_off"]  # ← De JSON
                btn_text = f"CC{input_cc_value}→CC{switch.output_cc_var.get()}: {'ON' if switch.state else 'OFF'}"
                elements['button'].configure(
                    text=btn_text,
                    fg_color=color,
                    state="disabled"
                )










    def refresh_all_switches(self):
        """Actualiza todos los switches"""
        for control_id in self.switch_frames:
            self.refresh_switch_ui(control_id)
  
    def update_learning_ui(self, learning_manager):
        for control_id, elements in self.switch_frames.items():
            btn = elements['button']

            if learning_manager.learning_mode:
                btn.configure(state="normal")

                if (learning_manager.learning_control_id == control_id 
                    and learning_manager.learning_control_id is not None):
                    if learning_manager.learning_cc_out:
                        btn.configure(
                            text="¡Presiona CC salida!", 
                            fg_color=self.styles["learning_mode"]["waiting_button"]  # ← De JSON
                        )
                    else:
                        btn.configure(
                            text="¡Presiona control físico!", 
                            fg_color=self.styles["learning_mode"]["active_button"]  # ← De JSON
                        )
                else:
                    btn.configure(
                        text="Click para aprender", 
                        fg_color=self.styles["learning_mode"]["available_button"]  # ← De JSON
                    )
            else:
                btn.configure(state="disabled")
                self.refresh_switch_ui(control_id)





 

    def update_all_texts_fast(self):
        """Actualiza solo los textos esenciales - MÁXIMA VELOCIDAD"""
        for control_id, elements in self.switch_frames.items():
            switch = elements['switch']
            
            # Solo OptionMenu (lo más importante)
            mode_menu = elements['mode_menu']
            current_internal_value = switch.mode_var.get()
            new_values = [self.localization.t("toggle"), self.localization.t("momentary")]
            
            if current_internal_value == "toggle":
                current_display_value = self.localization.t("toggle")
            else:
                current_display_value = self.localization.t("momentary")
            
            mode_menu.configure(values=new_values)
            mode_menu.set(current_display_value)
            
            # Refrescar switch (actualiza el botón principal)
            self.refresh_switch_ui(control_id)