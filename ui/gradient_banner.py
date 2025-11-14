import customtkinter as ctk
from PIL import Image, ImageDraw
import time
from math import sin, pi
import threading

class GradientCreator:
    """Clase estática para crear gradientes"""
    
    @staticmethod
    def create_gradient_banner(width, height, colors=None):
        """Crea una imagen de gradiente para el banner"""
        if colors is None:
            colors = [
                (43, 43, 43),    # #2B2B2B
                (126, 168, 190), # #7EA8BE  
                (194, 148, 138), # #C2948A
                (246, 240, 237)  # #F6F0ED
            ]
        
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        for x in range(width):
            pos = x / (width - 1) if width > 1 else 0
            
            if len(colors) == 1:
                r, g, b = colors[0]
            elif len(colors) == 2:
                r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * pos)
                g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * pos)
                b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * pos)
            else:
                # Interpolación para múltiples colores
                segment = 1.0 / (len(colors) - 1)
                color_index = int(pos / segment)
                color_index = min(color_index, len(colors) - 2)
                
                local_pos = (pos - color_index * segment) / segment
                r = int(colors[color_index][0] + (colors[color_index+1][0] - colors[color_index][0]) * local_pos)
                g = int(colors[color_index][1] + (colors[color_index+1][1] - colors[color_index][1]) * local_pos)
                b = int(colors[color_index][2] + (colors[color_index+1][2] - colors[color_index][2]) * local_pos)
            
            draw.line([(x, 0), (x, height)], fill=(r, g, b))
        
        return image

class AnimatedBanner:
    """Clase base para banners animados"""
    
    def __init__(self, banner_frame):
        self.banner_frame = banner_frame
        self.animating = False
        self.animation_thread = None
        self.gradient_label = None
        
        # Colores base para la animación
        self.base_colors = [
            (43, 43, 43),    # #2B2B2B
            (126, 168, 190), # #7EA8BE  
            (194, 148, 138), # #C2948A
            (246, 240, 237)  # #F6F0ED
        ]
    
    def set_gradient_label(self, gradient_label):
        """Establece la referencia al label del gradiente"""
        self.gradient_label = gradient_label
    
    def _update_banner_colors(self, colors):
        """Actualiza los colores del banner (ejecutar en main thread)"""
        if not self.animating or not self.gradient_label:
            return
            
        try:
            width = self.banner_frame.winfo_width() or 800
            height = self.banner_frame.winfo_height() or 120
            
            gradient_image = GradientCreator.create_gradient_banner(width, height, colors)
            gradient_photo = ctk.CTkImage(gradient_image, size=(width, height))
            
            self.gradient_label.configure(image=gradient_photo)
                    
        except Exception as e:
            print(f"Error actualizando colores: {e}")

class BreathingBanner(AnimatedBanner):
    """Banner con efecto de respiración sutil"""
    
    def start_animation(self):
        """Inicia animación de respiración sutil"""
        print("🎬 Iniciando animación de respiración...")

        self.animating = True
        self.animation_thread = threading.Thread(target=self._breathing_loop, daemon=True)
        self.animation_thread.start()
        print("✅ Hilo de animación iniciado")

    
    def stop_animation(self):
        """Detiene la animación"""
        self.animating = False
        if self.animation_thread:
            self.animation_thread.join(timeout=1)

    def _breathing_loop(self):
        """Loop principal de animación de respiración - VERSIÓN MÁS VISIBLE"""
        duration = 4.0  # Más rápido
        start_time = time.time()
        
        while self.animating:
            try:
                elapsed = time.time() - start_time
                t = (elapsed % duration) / duration
                breath_factor = (sin(t * 2 * pi - pi/2) + 1) / 2
                
                # Variación MÁS PRONUNCIADA para testing (±20 en cada canal)
                animated_colors = [self.base_colors[0]]
                
                for i in range(1, len(self.base_colors)-1):
                    base_r, base_g, base_b = self.base_colors[i]
                    r = int(base_r + (breath_factor - 0.5) * 40)  # ← Más pronunciado
                    g = int(base_g + (breath_factor - 0.5) * 40)
                    b = int(base_b + (breath_factor - 0.5) * 40)
                    animated_colors.append((r, g, b))
                
                animated_colors.append(self.base_colors[-1])
                
                self.banner_frame.after(0, self._update_banner_colors, animated_colors)
                time.sleep(0.05)
                
            except Exception as e:
                print(f"Error en animación: {e}")
                break


class ShiftingBanner(AnimatedBanner):
    """Banner con efecto de desplazamiento de gradiente"""
    
    def start_animation(self):
        """Inicia animación de desplazamiento de gradiente"""
        self.animating = True
        self.animation_thread = threading.Thread(target=self._shifting_loop, daemon=True)
        self.animation_thread.start()
    
    def stop_animation(self):
        """Detiene la animación"""
        self.animating = False
        if self.animation_thread:
            self.animation_thread.join(timeout=1)
    
    def _shifting_loop(self):
        """Loop de desplazamiento de gradiente"""
        duration = 12.0  # Más lento
        start_time = time.time()
        
        while self.animating:
            try:
                elapsed = time.time() - start_time
                t = (elapsed % duration) / duration
                
                # Crear array de colores desplazados
                shift_amount = int(t * len(self.base_colors))
                shifted_colors = self.base_colors[shift_amount:] + self.base_colors[:shift_amount]
                
                self.banner_frame.after(0, self._update_banner_colors, shifted_colors)
                time.sleep(0.1)  # 10 FPS - más lento para desplazamiento
                
            except Exception as e:
                print(f"Error en animación de desplazamiento: {e}")
                break

class WaveBanner(AnimatedBanner):
    """Banner con efecto de ondas suaves"""
    
    def start_animation(self):
        """Inicia animación de ondas suaves"""
        self.animating = True
        self.animation_thread = threading.Thread(target=self._wave_loop, daemon=True)
        self.animation_thread.start()
    
    def stop_animation(self):
        """Detiene la animación"""
        self.animating = False
        if self.animation_thread:
            self.animation_thread.join(timeout=1)
    
    def _wave_loop(self):
        """Loop de animación de ondas"""
        duration = 6.0
        start_time = time.time()
        
        while self.animating:
            try:
                elapsed = time.time() - start_time
                t = (elapsed % duration) / duration
                
                animated_colors = []
                for i, base_color in enumerate(self.base_colors):
                    base_r, base_g, base_b = base_color
                    
                    # Cada color tiene un desfase diferente
                    phase = i * 0.3
                    wave = sin((t + phase) * 2 * pi) * 0.3 + 0.7  # 0.4 a 1.0
                    
                    # Aplicar variación más pronunciada a colores intermedios
                    if 0 < i < len(self.base_colors) - 1:
                        r = int(base_r * wave)
                        g = int(base_g * wave) 
                        b = int(base_b * wave)
                    else:
                        # Colores de los extremos menos afectados
                        r = int(base_r * (wave * 0.3 + 0.7))
                        g = int(base_g * (wave * 0.3 + 0.7))
                        b = int(base_b * (wave * 0.3 + 0.7))
                    
                    animated_colors.append((r, g, b))
                
                self.banner_frame.after(0, self._update_banner_colors, animated_colors)
                time.sleep(0.04)  # 25 FPS
                
            except Exception as e:
                print(f"Error en animación de ondas: {e}")
                break

# Función de conveniencia para crear banners
def create_animated_banner(parent, animation_type="breathing"):
    """Crea un banner animado listo para usar - VERSIÓN CORREGIDA"""
    banner_frame = ctk.CTkFrame(parent, height=120, corner_radius=0)
    banner_frame.pack(fill="x", padx=0, pady=0)
    banner_frame.pack_propagate(False)
    
    # Variable para almacenar la referencia al CTkImage
    gradient_photo_ref = None
    
    def create_gradient_image(width, height, colors=None):
        """Función auxiliar para crear la imagen de gradiente"""
        nonlocal gradient_photo_ref
        gradient_image = GradientCreator.create_gradient_banner(width, height, colors)
        gradient_photo = ctk.CTkImage(gradient_image, size=(width, height))
        gradient_photo_ref = gradient_photo  # Mantener referencia
        return gradient_photo
    
    # Crear gradiente inicial
    initial_photo = create_gradient_image(800, 120)
    
    # Label con gradiente
    gradient_label = ctk.CTkLabel(
        banner_frame,
        image=initial_photo,
        text="",
        corner_radius=0
    )
    gradient_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    # Título
    title_label = ctk.CTkLabel(
        banner_frame,
        text="BLUETOOTH MIDI BRIDGE",
        font=("Arial", 28, "bold"),
        text_color="#F6F0ED",
        bg_color="transparent"
    )
    title_label.pack(side="left", padx=30, pady=20)
    
    # Crear animación
    if animation_type == "breathing":
        animated_banner = BreathingBanner(banner_frame)
    elif animation_type == "shifting":
        animated_banner = ShiftingBanner(banner_frame)
    elif animation_type == "wave":
        animated_banner = WaveBanner(banner_frame)
    else:
        animated_banner = BreathingBanner(banner_frame)
    
    # Sobrescribir el método _update_banner_colors para usar nuestra función
    original_update = animated_banner._update_banner_colors
    
    def custom_update(colors):
        try:
            width = banner_frame.winfo_width() or 800
            height = banner_frame.winfo_height() or 120
            new_photo = create_gradient_image(width, height, colors)
            gradient_label.configure(image=new_photo)
        except Exception as e:
            print(f"Error en actualización: {e}")
    
    animated_banner._update_banner_colors = custom_update
    animated_banner.set_gradient_label(gradient_label)
    
    # Iniciar animación
    def start_anim():
        try:
            print("🎬 Iniciando animación...")
            animated_banner.start_animation()
            print("✅ Animación iniciada")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    parent.after(1500, start_anim)
    
    return banner_frame, animated_banner

class GradientBanner:
    """Alias para GradientCreator para mantener compatibilidad"""
    
    @staticmethod
    def create_gradient_banner(width, height, colors=None):
        return GradientCreator.create_gradient_banner(width, height, colors)
    
    @staticmethod
    def create_animated_gradient(width, height, colors):
        return GradientCreator.create_gradient_banner(width, height, colors)