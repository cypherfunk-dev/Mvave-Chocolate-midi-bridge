import time
import threading
from math import sin, pi
from ui.gradient_banner import GradientBanner

class AnimatedBanner:
    def __init__(self, banner_frame):
        self.banner_frame = banner_frame
        self.animating = False
        self.animation_thread = None
        
        # Colores base para la animación
        self.base_colors = [
            (43, 43, 43),    # #2B2B2B
            (126, 168, 190), # #7EA8BE  
            (194, 148, 138), # #C2948A
            (246, 240, 237)  # #F6F0ED
        ]
        
    def start_breathing_animation(self):
        """Inicia animación de respiración sutil"""
        self.animating = True
        self.animation_thread = threading.Thread(target=self._breathing_loop, daemon=True)
        self.animation_thread.start()
    
    def stop_animation(self):
        """Detiene la animación"""
        self.animating = False
        if self.animation_thread:
            self.animation_thread.join(timeout=1)
    
    def _breathing_loop(self):
        """Loop principal de animación de respiración"""
        duration = 8.0  # 8 segundos por ciclo completo
        start_time = time.time()
        
        while self.animating:
            try:
                elapsed = time.time() - start_time
                # Función seno suavizada para el efecto breathing
                t = (elapsed % duration) / duration
                breath_factor = (sin(t * 2 * pi - pi/2) + 1) / 2  # 0 a 1
                
                # Aplicar a los colores intermedios (no al primero ni último)
                animated_colors = [self.base_colors[0]]  # Mantener primer color fijo
                
                for i in range(1, len(self.base_colors)-1):
                    base_r, base_g, base_b = self.base_colors[i]
                    # Variación muy sutil (±5 en cada canal)
                    r = int(base_r + (breath_factor - 0.5) * 10)
                    g = int(base_g + (breath_factor - 0.5) * 10)
                    b = int(base_b + (breath_factor - 0.5) * 10)
                    animated_colors.append((r, g, b))
                
                animated_colors.append(self.base_colors[-1])  # Mantener último color fijo
                
                # Actualizar en el hilo principal
                self.banner_frame.after(0, self._update_banner_colors, animated_colors)
                
                time.sleep(0.05)  # 20 FPS
                
            except Exception as e:
                print(f"Error en animación: {e}")
                break
    
    def _update_banner_colors(self, colors):
        """Actualiza los colores del banner (ejecutar en main thread)"""
        if not self.animating:
            return
            
        try:
            # Aquí necesitarías recrear el gradiente con los nuevos colores
            # Esto depende de cómo implementes el gradiente
            width = self.banner_frame.winfo_width() or 800
            height = self.banner_frame.winfo_height() or 120
            
            gradient_image = GradientBanner.create_animated_gradient(width, height, colors)
            gradient_photo = ctk.CTkImage(gradient_image, size=(width, height))
            
            # Buscar y actualizar el label del gradiente
            for child in self.banner_frame.winfo_children():
                if hasattr(child, 'gradient_element'):
                    child.configure(image=gradient_photo)
                    break
                    
        except Exception as e:
            print(f"Error actualizando colores: {e}")


class ShiftingBanner(AnimatedBanner):
    def start_shifting_animation(self):
        """Inicia animación de desplazamiento de gradiente"""
        self.animating = True
        self.animation_thread = threading.Thread(target=self._shifting_loop, daemon=True)
        self.animation_thread.start()
    
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
    def start_wave_animation(self):
        """Inicia animación de ondas suaves"""
        self.animating = True
        self.animation_thread = threading.Thread(target=self._wave_loop, daemon=True)
        self.animation_thread.start()
    
    def _wave_loop(self):
        """Loop de animación de ondas"""
        duration = 6.0
        start_time = time.time()
        wave_speed = 0.5
        
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
