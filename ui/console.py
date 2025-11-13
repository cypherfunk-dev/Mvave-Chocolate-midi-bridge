import customtkinter as ctk
from tkinter import scrolledtext

class ConsolePanel(ctk.CTkFrame):
    def __init__(self, parent, localization):
        super().__init__(parent)
        self.localization = localization
        self.build_ui()
    
    def build_ui(self):
        self.console = scrolledtext.ScrolledText(self, height=10, state="disabled", bg="#2b2b2b", fg="#D4DFC7")
        self.console.pack(fill="both", expand=True)
    
    def log(self, message):
        self.console.configure(state="normal")
        self.console.insert("end", message + "\n")
        self.console.configure(state="disabled")
        self.console.yview("end")