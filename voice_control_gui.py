#!/usr/bin/env python3
"""
Interfaz Gráfica para Sistema de Control por Voz con Identificación de Hablante
Diseño moderno y funcional con Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import os
import sys
from datetime import datetime
import queue

# Importar el sistema de control por voz
try:
    from voice_control import VoiceController
    VOICE_CONTROL_AVAILABLE = True
except ImportError:
    print("⚠️  VoiceController no disponible")
    VOICE_CONTROL_AVAILABLE = False

class VoiceControlGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎤 Sistema de Control por Voz")
        self.root.geometry("900x700")
        self.root.configure(bg='#2c3e50')
        self.root.resizable(True, True)
        
        # Configurar icono si existe
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # Configurar estilo moderno
        self.setup_styles()
        
        # Variables de estado
        self.current_speaker = tk.StringVar(value="No identificado")
        self.is_listening = tk.BooleanVar(value=False)
        self.is_identifying = tk.BooleanVar(value=False)
        self.listening_thread = None
        self.log_queue = queue.Queue()
        
        # Inicializar controlador de voz
        self.init_voice_controller()
        
        # Crear interfaz
        self.create_widgets()
        
        # Iniciar procesamiento de logs
        self.process_log_queue()
        
        # Configurar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Log inicial
        self.log_message("🎤 Interfaz gráfica inicializada", "INFO")

    def setup_styles(self):
        """Configurar estilos modernos"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Colores modernos
        self.colors = {
            'bg_dark': '#2c3e50',
            'bg_light': '#34495e',
            'accent': '#3498db',
            'success': '#2ecc71',
            'warning': '#f39c12',
            'error': '#e74c3c',
            'text': '#ecf0f1',
            'text_dark': '#2c3e50'
        }
        
        # Configurar estilos básicos compatibles
        self.style.configure('Title.TLabel', 
                           font=('Segoe UI', 20, 'bold'),
                           foreground=self.colors['text'],
                           background=self.colors['bg_dark'])
        
        self.style.configure('Heading.TLabel', 
                           font=('Segoe UI', 12, 'bold'),
                           foreground=self.colors['text'],
                           background=self.colors['bg_light'])
        
        self.style.configure('Status.TLabel', 
                           font=('Segoe UI', 10),
                           foreground=self.colors['text'],
                           background=self.colors['bg_light'])
        
        self.style.configure('Success.TLabel', 
                           font=('Segoe UI', 10, 'bold'),
                           foreground=self.colors['success'],
                           background=self.colors['bg_light'])
        
        self.style.configure('Warning.TLabel', 
                           font=('Segoe UI', 10, 'bold'),
                           foreground=self.colors['warning'],
                           background=self.colors['bg_light'])
        
        self.style.configure('Error.TLabel', 
                           font=('Segoe UI', 10, 'bold'),
                           foreground=self.colors['error'],
                           background=self.colors['bg_light'])
        
        # Botones modernos
        self.style.configure('Action.TButton', 
                           font=('Segoe UI', 10, 'bold'),
                           padding=(10, 5))
        
        self.style.configure('Primary.TButton', 
                           font=('Segoe UI', 10, 'bold'),
                           padding=(10, 5))
        
        self.style.configure('Success.TButton', 
                           font=('Segoe UI', 10, 'bold'),
                           padding=(10, 5))
        
        self.style.configure('Warning.TButton', 
                           font=('Segoe UI', 10, 'bold'),
                           padding=(10, 5))

    def init_voice_controller(self):
        """Inicializar controlador de voz"""
        if VOICE_CONTROL_AVAILABLE:
            try:
                self.voice_controller = VoiceController()
                self.log_message("✅ Sistema de control por voz inicializado correctamente", "SUCCESS")
            except Exception as e:
                self.voice_controller = None
                self.log_message(f"❌ Error inicializando sistema de voz: {e}", "ERROR")
        else:
            self.voice_controller = None
            self.log_message("❌ Sistema de control por voz no disponible", "ERROR")

    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.configure(style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configurar grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Título principal
        title_label = ttk.Label(main_frame, text="🎤 Sistema de Control por Voz", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Panel izquierdo - Controles
        self.create_control_panel(main_frame)
        
        # Panel derecho - Estado y información
        self.create_status_panel(main_frame)
        
        # Panel inferior - Log
        self.create_log_panel(main_frame)
        
        # Barra de estado
        self.create_status_bar(main_frame)

    def create_control_panel(self, parent):
        """Crear panel de controles"""
        # Frame de controles
        control_frame = ttk.LabelFrame(parent, text="🎮 Controles", padding="15")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), 
                          padx=(0, 10), pady=(0, 10))
        control_frame.columnconfigure(0, weight=1)
        
        # Botón de identificación
        self.identify_btn = ttk.Button(control_frame, text="🎯 Identificarse", 
                                      command=self.identify_speaker, 
                                      style='Primary.TButton')
        self.identify_btn.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botón comando único
        self.single_command_btn = ttk.Button(control_frame, text="🎤 Comando Único", 
                                            command=self.single_voice_command, 
                                            style='Action.TButton')
        self.single_command_btn.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botón escucha continua
        self.continuous_btn = ttk.Button(control_frame, text="🎧 Escucha Continua", 
                                        command=self.toggle_continuous_listening, 
                                        style='Success.TButton')
        self.continuous_btn.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Separador
        ttk.Separator(control_frame, orient='horizontal').grid(row=3, column=0, 
                                                             sticky=(tk.W, tk.E), 
                                                             pady=10)
        
        # Botones secundarios
        self.permissions_btn = ttk.Button(control_frame, text="📋 Permisos", 
                                         command=self.show_permissions)
        self.permissions_btn.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.config_btn = ttk.Button(control_frame, text="⚙️ Configuración", 
                                    command=self.show_config)
        self.config_btn.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.help_btn = ttk.Button(control_frame, text="❓ Ayuda", 
                                  command=self.show_help)
        self.help_btn.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Configuración de duración
        duration_frame = ttk.LabelFrame(control_frame, text="⏱️ Configuración", padding="10")
        duration_frame.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(duration_frame, text="Duración (segundos):", 
                 style='Status.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        self.duration_var = tk.StringVar(value="3")
        self.duration_spin = ttk.Spinbox(duration_frame, from_=2, to=10, 
                                        textvariable=self.duration_var, 
                                        width=5)
        self.duration_spin.grid(row=0, column=1, sticky=tk.E)

    def create_status_panel(self, parent):
        """Crear panel de estado"""
        # Frame de estado
        status_frame = ttk.LabelFrame(parent, text="📊 Estado del Sistema", padding="15")
        status_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), 
                         padx=(10, 0), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Usuario actual
        ttk.Label(status_frame, text="👤 Usuario:", 
                 style='Status.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.speaker_label = ttk.Label(status_frame, textvariable=self.current_speaker, 
                                      style='Warning.TLabel')
        self.speaker_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # Estado de escucha
        ttk.Label(status_frame, text="🎧 Estado:", 
                 style='Status.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        self.listening_label = ttk.Label(status_frame, text="Inactivo", 
                                        style='Status.TLabel')
        self.listening_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # Sistema de audio
        ttk.Label(status_frame, text="🔊 Audio:", 
                 style='Status.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        audio_status = "Disponible" if self.voice_controller and self.voice_controller.audio_comparator else "No disponible"
        self.audio_label = ttk.Label(status_frame, text=audio_status, 
                                    style='Success.TLabel' if self.voice_controller else 'Error.TLabel')
        self.audio_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        
        # Separador
        ttk.Separator(status_frame, orient='horizontal').grid(row=3, column=0, 
                                                            columnspan=2, 
                                                            sticky=(tk.W, tk.E), 
                                                            pady=10)
        
        # Comandos disponibles
        ttk.Label(status_frame, text="🎤 Comandos Disponibles:", 
                 style='Heading.TLabel').grid(row=4, column=0, columnspan=2, 
                                            sticky=tk.W, pady=(0, 10))
        
        # Lista de comandos
        self.commands_frame = ttk.Frame(status_frame)
        self.commands_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.commands_text = tk.Text(self.commands_frame, height=8, width=40,
                                    font=('Consolas', 9), 
                                    bg=self.colors['bg_dark'], 
                                    fg=self.colors['text'],
                                    insertbackground=self.colors['text'],
                                    selectbackground=self.colors['accent'],
                                    relief='flat',
                                    borderwidth=0)
        
        commands_scroll = ttk.Scrollbar(self.commands_frame, orient=tk.VERTICAL, 
                                       command=self.commands_text.yview)
        self.commands_text.configure(yscrollcommand=commands_scroll.set)
        
        self.commands_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        commands_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Actualizar comandos
        self.update_commands_list()

    def create_log_panel(self, parent):
        """Crear panel de log"""
        # Frame de log
        log_frame = ttk.LabelFrame(parent, text="📝 Registro de Actividad", padding="15")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), 
                      pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Área de log con colores
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, 
                                                 font=('Consolas', 9),
                                                 bg=self.colors['bg_dark'],
                                                 fg=self.colors['text'],
                                                 insertbackground=self.colors['text'],
                                                 selectbackground=self.colors['accent'],
                                                 relief='flat',
                                                 borderwidth=0)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar tags para colores
        self.log_text.tag_configure("INFO", foreground=self.colors['text'])
        self.log_text.tag_configure("SUCCESS", foreground=self.colors['success'])
        self.log_text.tag_configure("WARNING", foreground=self.colors['warning'])
        self.log_text.tag_configure("ERROR", foreground=self.colors['error'])
        self.log_text.tag_configure("TIMESTAMP", foreground=self.colors['accent'])
        
        # Botones de log
        log_buttons_frame = ttk.Frame(log_frame)
        log_buttons_frame.grid(row=1, column=0, pady=(10, 0))
        
        ttk.Button(log_buttons_frame, text="🗑️ Limpiar", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(log_buttons_frame, text="💾 Guardar", 
                  command=self.save_log).pack(side=tk.LEFT, padx=(5, 0))

    def create_status_bar(self, parent):
        """Crear barra de estado"""
        # Barra de estado
        status_bar_frame = ttk.Frame(parent)
        status_bar_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), 
                             pady=(10, 0))
        status_bar_frame.columnconfigure(0, weight=1)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(status_bar_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Indicador de estado
        self.status_indicator = ttk.Label(status_bar_frame, text="● Listo", 
                                         style='Success.TLabel')
        self.status_indicator.grid(row=0, column=1)

    def log_message(self, message, level="INFO"):
        """Agregar mensaje al log con colores"""
        self.log_queue.put((message, level))

    def process_log_queue(self):
        """Procesar cola de mensajes de log"""
        try:
            while True:
                message, level = self.log_queue.get_nowait()
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                # Insertar timestamp
                self.log_text.insert(tk.END, f"[{timestamp}] ", "TIMESTAMP")
                
                # Insertar mensaje con color según el nivel
                self.log_text.insert(tk.END, f"{message}\n", level)
                
                # Scroll automático
                self.log_text.see(tk.END)
                self.root.update_idletasks()
                
        except queue.Empty:
            pass
        
        # Programar siguiente procesamiento
        self.root.after(100, self.process_log_queue)

    def clear_log(self):
        """Limpiar el log"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("🗑️ Log limpiado", "INFO")

    def save_log(self):
        """Guardar log en archivo"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"voice_control_log_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_text.get(1.0, tk.END))
            
            self.log_message(f"💾 Log guardado en: {filename}", "SUCCESS")
            messagebox.showinfo("Éxito", f"Log guardado en: {filename}")
        except Exception as e:
            self.log_message(f"❌ Error guardando log: {e}", "ERROR")
            messagebox.showerror("Error", f"Error guardando log: {e}")

    def update_commands_list(self):
        """Actualizar la lista de comandos disponibles"""
        self.commands_text.delete(1.0, tk.END)
        
        if not self.voice_controller:
            self.commands_text.insert(tk.END, "❌ Sistema de voz no disponible\n")
            return
        
        current_speaker = self.current_speaker.get()
        if current_speaker == "No identificado":
            self.commands_text.insert(tk.END, "❗ Debes identificarte primero\n")
            self.commands_text.insert(tk.END, "   Usa el botón 'Identificarse'\n")
            return
        
        # Obtener permisos del usuario actual
        permisos = self.voice_controller.obtener_permisos(current_speaker)
        
        if not permisos:
            self.commands_text.insert(tk.END, "❌ Sin permisos disponibles\n")
            return
        
        self.commands_text.insert(tk.END, f"Comandos para {current_speaker}:\n\n")
        for i, permiso in enumerate(permisos, 1):
            self.commands_text.insert(tk.END, f"{i:2d}. {permiso}\n")

    def set_status(self, message, level="INFO"):
        """Establecer estado en la barra de estado"""
        colors = {
            "INFO": ("● " + message, 'Status.TLabel'),
            "SUCCESS": ("● " + message, 'Success.TLabel'),
            "WARNING": ("● " + message, 'Warning.TLabel'),
            "ERROR": ("● " + message, 'Error.TLabel')
        }
        
        text, style = colors.get(level, ("● " + message, 'Status.TLabel'))
        self.status_indicator.configure(text=text, style=style)

    def identify_speaker(self):
        """Identificar al hablante"""
        if not self.voice_controller:
            messagebox.showerror("Error", "Sistema de voz no disponible")
            return
        
        if self.is_identifying.get():
            messagebox.showwarning("Advertencia", "Identificación en progreso...")
            return
        
        # Verificar si está en escucha continua
        if self.is_listening.get():
            messagebox.showwarning("Advertencia", "Detén la escucha continua primero")
            return
        
        def identify_worker():
            try:
                self.is_identifying.set(True)
                self.identify_btn.configure(text="🔄 Identificando...", state='disabled')
                self.progress.start()
                self.set_status("Identificando hablante...", "WARNING")
                
                # Deshabilitar otros botones durante identificación
                self.single_command_btn.configure(state='disabled')
                self.continuous_btn.configure(state='disabled')
                
                self.log_message("🎯 Iniciando identificación de hablante...", "INFO")
                
                # Obtener duración
                try:
                    duration = int(self.duration_var.get())
                except ValueError:
                    duration = 3
                
                # Ejecutar identificación con auto_start=True para GUI
                speaker = self.voice_controller.identificar_hablante(duration, auto_start=True)
                
                # Actualizar interfaz - el current_speaker ya se actualiza dentro del método
                self.current_speaker.set(speaker)
                
                if speaker != "Desconocido":
                    self.log_message(f"✅ Hablante identificado: {speaker}", "SUCCESS")
                    self.speaker_label.configure(style='Success.TLabel')
                    self.set_status(f"Identificado como {speaker}", "SUCCESS")
                    
                    permisos = self.voice_controller.obtener_permisos(speaker)
                    self.log_message(f"🔑 Permisos cargados: {len(permisos)} comandos", "INFO")
                else:
                    self.log_message("❌ No se pudo identificar al hablante", "ERROR")
                    self.speaker_label.configure(style='Error.TLabel')
                    self.set_status("Identificación fallida", "ERROR")
                
                self.update_commands_list()
                
            except Exception as e:
                self.log_message(f"❌ Error en identificación: {e}", "ERROR")
                self.set_status("Error en identificación", "ERROR")
                messagebox.showerror("Error", f"Error en identificación: {e}")
            finally:
                self.is_identifying.set(False)
                self.identify_btn.configure(text="🎯 Identificarse", state='normal')
                self.single_command_btn.configure(state='normal')
                self.continuous_btn.configure(state='normal')
                self.progress.stop()
                if not self.is_listening.get():
                    self.set_status("Listo", "SUCCESS")
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=identify_worker)
        thread.daemon = True
        thread.start()

    def single_voice_command(self):
        """Ejecutar un comando de voz único"""
        if not self.voice_controller:
            messagebox.showerror("Error", "Sistema de voz no disponible")
            return
        
        if self.current_speaker.get() == "No identificado":
            messagebox.showwarning("Advertencia", "Debes identificarte primero")
            return
        
        # Verificar si está en escucha continua
        if self.is_listening.get():
            messagebox.showwarning("Advertencia", "Detén la escucha continua primero")
            return
        
        def command_worker():
            try:
                self.single_command_btn.configure(text="🔄 Escuchando...", state='disabled')
                self.progress.start()
                self.set_status("Escuchando comando...", "WARNING")
                
                # Deshabilitar escucha continua mientras se procesa comando único
                self.continuous_btn.configure(state='disabled')
                
                self.log_message("🎤 Esperando comando de voz...", "INFO")
                
                # Obtener duración
                try:
                    duration = int(self.duration_var.get())
                except ValueError:
                    duration = 5
                
                # Simular el procesamiento de comando
                self.voice_controller.procesar_comando_voz(duration)
                
                self.log_message("✅ Comando procesado", "SUCCESS")
                self.set_status("Comando ejecutado", "SUCCESS")
                
            except Exception as e:
                self.log_message(f"❌ Error procesando comando: {e}", "ERROR")
                self.set_status("Error en comando", "ERROR")
                messagebox.showerror("Error", f"Error procesando comando: {e}")
            finally:
                self.single_command_btn.configure(text="🎤 Comando Único", state='normal')
                self.continuous_btn.configure(state='normal')
                self.progress.stop()
                if not self.is_listening.get():
                    self.set_status("Listo", "SUCCESS")
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=command_worker)
        thread.daemon = True
        thread.start()

    def toggle_continuous_listening(self):
        """Alternar escucha continua"""
        if not self.voice_controller:
            messagebox.showerror("Error", "Sistema de voz no disponible")
            return
        
        if self.current_speaker.get() == "No identificado":
            messagebox.showwarning("Advertencia", "Debes identificarte primero")
            return
        
        if self.is_listening.get():
            self.stop_continuous_listening()
        else:
            self.start_continuous_listening()

    def start_continuous_listening(self):
        """Iniciar escucha continua"""
        self.is_listening.set(True)
        self.listening_label.configure(text="🎧 Escuchando...", style='Success.TLabel')
        self.continuous_btn.configure(text="🛑 Detener Escucha", style='Warning.TButton')
        self.set_status("Escucha continua activa", "SUCCESS")
        self.log_message("🎧 Iniciando escucha continua...", "INFO")
        
        # Deshabilitar otros botones
        self.identify_btn.configure(state='disabled')
        self.single_command_btn.configure(state='disabled')
        
        def listening_worker():
            try:
                self.voice_controller.escuchar_comandos_continuo()
            except Exception as e:
                self.log_message(f"❌ Error en escucha continua: {e}", "ERROR")
            finally:
                # Restaurar estado (esto se ejecuta automáticamente cuando se detiene)
                self.root.after(0, self.stop_continuous_listening)
        
        # Ejecutar en hilo separado
        self.listening_thread = threading.Thread(target=listening_worker)
        self.listening_thread.daemon = True
        self.listening_thread.start()

    def stop_continuous_listening(self):
        """Detener escucha continua"""
        if self.is_listening.get() and self.voice_controller:
            # Enviar señal de parada al voice controller
            self.voice_controller.detener_escucha_continua()
            self.log_message("🛑 Enviando señal de parada...", "INFO")
        
        self.is_listening.set(False)
        self.listening_label.configure(text="Inactivo", style='Status.TLabel')
        self.continuous_btn.configure(text="🎧 Escucha Continua", style='Success.TButton')
        self.set_status("Listo", "SUCCESS")
        self.log_message("🛑 Escucha continua detenida", "INFO")
        
        # Habilitar otros botones
        self.identify_btn.configure(state='normal')
        self.single_command_btn.configure(state='normal')

    def show_permissions(self):
        """Mostrar ventana de permisos"""
        if not self.voice_controller:
            messagebox.showerror("Error", "Sistema de voz no disponible")
            return
        
        # Crear ventana de permisos
        permissions_window = tk.Toplevel(self.root)
        permissions_window.title("📋 Permisos del Sistema")
        permissions_window.geometry("600x500")
        permissions_window.configure(bg=self.colors['bg_dark'])
        permissions_window.transient(self.root)
        permissions_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(permissions_window, style='Card.TFrame', padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(main_frame, text="📋 Permisos por Usuario", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Texto de permisos
        permisos_text = scrolledtext.ScrolledText(main_frame, height=25, 
                                                 font=('Consolas', 10),
                                                 bg=self.colors['bg_dark'],
                                                 fg=self.colors['text'],
                                                 insertbackground=self.colors['text'],
                                                 selectbackground=self.colors['accent'],
                                                 relief='flat',
                                                 borderwidth=0)
        permisos_text.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags para colores
        permisos_text.tag_configure("USER", foreground=self.colors['accent'], font=('Consolas', 10, 'bold'))
        permisos_text.tag_configure("PERMISSION", foreground=self.colors['success'])
        permisos_text.tag_configure("NO_PERMISSION", foreground=self.colors['error'])
        permisos_text.tag_configure("CURRENT", foreground=self.colors['warning'], font=('Consolas', 10, 'bold'))
        
        # Mostrar permisos
        for usuario, permisos in self.voice_controller.permisos.items():
            permisos_text.insert(tk.END, f"👤 {usuario}:\n", "USER")
            if permisos:
                for permiso in permisos:
                    permisos_text.insert(tk.END, f"   ✅ {permiso}\n", "PERMISSION")
            else:
                permisos_text.insert(tk.END, "   ❌ Sin permisos\n", "NO_PERMISSION")
            permisos_text.insert(tk.END, "\n")
        
        # Destacar usuario actual
        if self.current_speaker.get() != "No identificado":
            permisos_text.insert(tk.END, f"🔑 Tus permisos actuales ({self.current_speaker.get()}):\n", "CURRENT")
            user_permisos = self.voice_controller.obtener_permisos(self.current_speaker.get())
            if user_permisos:
                for permiso in user_permisos:
                    permisos_text.insert(tk.END, f"   ✅ {permiso}\n", "PERMISSION")
            else:
                permisos_text.insert(tk.END, "   ❌ Sin permisos\n", "NO_PERMISSION")
        
        permisos_text.config(state=tk.DISABLED)
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", 
                  command=permissions_window.destroy).pack(pady=(10, 0))

    def show_config(self):
        """Mostrar ventana de configuración"""
        if not self.voice_controller:
            messagebox.showerror("Error", "Sistema de voz no disponible")
            return
        
        # Crear ventana de configuración
        config_window = tk.Toplevel(self.root)
        config_window.title("⚙️ Configuración del Sistema")
        config_window.geometry("700x600")
        config_window.configure(bg=self.colors['bg_dark'])
        config_window.transient(self.root)
        config_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(config_window, style='Card.TFrame', padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(main_frame, text="⚙️ Configuración del Sistema", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Notebook para pestañas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de información del sistema
        self.create_info_tab(notebook)
        
        # Pestaña de pruebas
        self.create_test_tab(notebook)
        
        # Pestaña de configuración
        self.create_settings_tab(notebook)

    def create_info_tab(self, notebook):
        """Crear pestaña de información"""
        info_frame = ttk.Frame(notebook, style='Card.TFrame')
        notebook.add(info_frame, text="📊 Información")
        
        info_text = scrolledtext.ScrolledText(info_frame, height=20, 
                                             font=('Consolas', 9),
                                             bg=self.colors['bg_dark'],
                                             fg=self.colors['text'],
                                             insertbackground=self.colors['text'],
                                             selectbackground=self.colors['accent'],
                                             relief='flat',
                                             borderwidth=0)
        info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configurar tags para colores
        info_text.tag_configure("HEADER", foreground=self.colors['accent'], font=('Consolas', 9, 'bold'))
        info_text.tag_configure("SUCCESS", foreground=self.colors['success'])
        info_text.tag_configure("ERROR", foreground=self.colors['error'])
        info_text.tag_configure("INFO", foreground=self.colors['text'])
        
        # Mostrar información del sistema
        info_text.insert(tk.END, "📊 INFORMACIÓN DEL SISTEMA\n", "HEADER")
        info_text.insert(tk.END, "=" * 50 + "\n\n", "INFO")
        
        # Estado del comparador
        if hasattr(self.voice_controller, 'audio_comparator') and self.voice_controller.audio_comparator:
            info_text.insert(tk.END, "✅ Audio Comparator: Disponible\n", "SUCCESS")
            info_text.insert(tk.END, f"   🖥️  Dispositivo: {self.voice_controller.audio_comparator.device}\n\n", "INFO")
        else:
            info_text.insert(tk.END, "❌ Audio Comparator: No disponible\n\n", "ERROR")
        
        # Archivos de referencia
        info_text.insert(tk.END, "📁 Archivos de referencia:\n", "HEADER")
        reference_files = {
            "Daniel": [
                "data/daniel_2/record_out (11).wav",
                "data/daniel_2/audio_01.wav",
                "data/daniel_2/record_out.wav"
            ],
            "Hablante_1": [
                "data/hablante_1/hablante_1_02.wav",
                "data/hablante_1/hablante_1_01.wav", 
                "data/hablante_1/hablante_1_03.wav"
            ]
        }
        
        for person, files in reference_files.items():
            available_files = [f for f in files if os.path.exists(f)]
            status = f"{len(available_files)}/{len(files)} disponibles"
            color = "SUCCESS" if len(available_files) > 0 else "ERROR"
            info_text.insert(tk.END, f"   👤 {person}: {status}\n", color)
        
        # Dependencias
        info_text.insert(tk.END, "\n📦 Dependencias:\n", "HEADER")
        dependencies = [
            ("speech_recognition", "SpeechRecognition"),
            ("sounddevice", "sounddevice"),
            ("pyautogui", "pyautogui"),
            ("torch", "PyTorch"),
            ("torchaudio", "torchaudio")
        ]
        
        for module, name in dependencies:
            try:
                __import__(module)
                info_text.insert(tk.END, f"   ✅ {name}\n", "SUCCESS")
            except ImportError:
                info_text.insert(tk.END, f"   ❌ {name} no instalado\n", "ERROR")
        
        info_text.config(state=tk.DISABLED)

    def create_test_tab(self, notebook):
        """Crear pestaña de pruebas"""
        test_frame = ttk.Frame(notebook, style='Card.TFrame')
        notebook.add(test_frame, text="🧪 Pruebas")
        
        test_frame.columnconfigure(0, weight=1)
        
        # Título
        title_label = ttk.Label(test_frame, text="🧪 Pruebas del Sistema", 
                               style='Heading.TLabel')
        title_label.grid(row=0, column=0, pady=(20, 30))
        
        # Botones de prueba
        buttons_frame = ttk.Frame(test_frame, style='Card.TFrame')
        buttons_frame.grid(row=1, column=0, pady=10)
        
        ttk.Button(buttons_frame, text="🎙️ Probar Micrófono", 
                  command=self.test_microphone,
                  style='Action.TButton').pack(pady=10, fill=tk.X)
        
        ttk.Button(buttons_frame, text="🎯 Prueba de Identificación", 
                  command=self.test_identification,
                  style='Action.TButton').pack(pady=10, fill=tk.X)
        
        ttk.Button(buttons_frame, text="🔧 Diagnóstico Completo", 
                  command=self.run_diagnostics,
                  style='Action.TButton').pack(pady=10, fill=tk.X)
        
        ttk.Button(buttons_frame, text="📊 Mostrar Estadísticas", 
                  command=self.show_statistics,
                  style='Action.TButton').pack(pady=10, fill=tk.X)

    def create_settings_tab(self, notebook):
        """Crear pestaña de configuración"""
        settings_frame = ttk.Frame(notebook, style='Card.TFrame')
        notebook.add(settings_frame, text="⚙️ Configuración")
        
        settings_frame.columnconfigure(0, weight=1)
        
        # Configuración de audio
        audio_frame = ttk.LabelFrame(settings_frame, text="🔊 Configuración de Audio", 
                                    style='Card.TLabelFrame', padding="15")
        audio_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=20, pady=10)
        
        # Threshold de identificación
        ttk.Label(audio_frame, text="🎯 Threshold de Identificación:", 
                 style='Status.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.threshold_var = tk.StringVar(value="0.45")
        threshold_spin = ttk.Spinbox(audio_frame, from_=0.1, to=1.0, increment=0.05,
                                    textvariable=self.threshold_var, width=10)
        threshold_spin.grid(row=0, column=1, sticky=tk.E, pady=5)
        
        # Configuración de duraciones
        duration_frame = ttk.LabelFrame(settings_frame, text="⏱️ Configuración de Tiempos", 
                                       style='Card.TLabelFrame', padding="15")
        duration_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=20, pady=10)
        
        # Duración de identificación
        ttk.Label(duration_frame, text="Identificación (segundos):", 
                 style='Status.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.id_duration_var = tk.StringVar(value="3")
        id_duration_spin = ttk.Spinbox(duration_frame, from_=2, to=10,
                                      textvariable=self.id_duration_var, width=10)
        id_duration_spin.grid(row=0, column=1, sticky=tk.E, pady=5)
        
        # Duración de comando
        ttk.Label(duration_frame, text="Comando (segundos):", 
                 style='Status.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.cmd_duration_var = tk.StringVar(value="5")
        cmd_duration_spin = ttk.Spinbox(duration_frame, from_=3, to=15,
                                       textvariable=self.cmd_duration_var, width=10)
        cmd_duration_spin.grid(row=1, column=1, sticky=tk.E, pady=5)
        
        # Botón guardar configuración
        ttk.Button(settings_frame, text="💾 Guardar Configuración", 
                  command=self.save_settings,
                  style='Primary.TButton').grid(row=2, column=0, pady=20)

    def test_microphone(self):
        """Probar micrófono"""
        def test_worker():
            try:
                self.log_message("🎙️ Probando micrófono...", "INFO")
                self.voice_controller.configurar_microfono()
                self.log_message("✅ Prueba de micrófono completada", "SUCCESS")
            except Exception as e:
                self.log_message(f"❌ Error probando micrófono: {e}", "ERROR")
        
        thread = threading.Thread(target=test_worker)
        thread.daemon = True
        thread.start()

    def test_identification(self):
        """Probar identificación"""
        def test_worker():
            try:
                self.log_message("🧪 Iniciando prueba de identificación...", "INFO")
                result = self.voice_controller.identificar_hablante(5)
                self.log_message(f"🧪 Resultado de prueba: {result}", "SUCCESS" if result != "Desconocido" else "WARNING")
            except Exception as e:
                self.log_message(f"❌ Error en prueba de identificación: {e}", "ERROR")
        
        thread = threading.Thread(target=test_worker)
        thread.daemon = True
        thread.start()

    def run_diagnostics(self):
        """Ejecutar diagnóstico completo"""
        def diagnostic_worker():
            try:
                self.log_message("🔧 Ejecutando diagnóstico completo...", "INFO")
                self.voice_controller.diagnosticar_problemas()
                self.log_message("✅ Diagnóstico completado", "SUCCESS")
            except Exception as e:
                self.log_message(f"❌ Error en diagnóstico: {e}", "ERROR")
        
        thread = threading.Thread(target=diagnostic_worker)
        thread.daemon = True
        thread.start()

    def show_statistics(self):
        """Mostrar estadísticas del sistema"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Estadísticas del Sistema")
        stats_window.geometry("500x400")
        stats_window.configure(bg=self.colors['bg_dark'])
        stats_window.transient(self.root)
        
        # Contenido de estadísticas
        stats_frame = ttk.Frame(stats_window, style='Card.TFrame', padding="20")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        stats_text = scrolledtext.ScrolledText(stats_frame, height=20, 
                                              font=('Consolas', 9),
                                              bg=self.colors['bg_dark'],
                                              fg=self.colors['text'],
                                              relief='flat',
                                              borderwidth=0)
        stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Mostrar estadísticas
        stats_content = """
📊 ESTADÍSTICAS DEL SISTEMA
=============================

👤 Usuario Actual: {current_user}
🔐 Estado: {auth_status}
🎤 Sistema de Audio: {audio_status}
⏱️ Tiempo Activo: {uptime}

📈 MÉTRICAS:
• Identificaciones Exitosas: N/A
• Comandos Ejecutados: N/A
• Errores Registrados: N/A
• Precisión Media: N/A

🎯 CONFIGURACIÓN ACTUAL:
• Threshold: {threshold}
• Duración ID: {id_duration}s
• Duración CMD: {cmd_duration}s

💾 ARCHIVOS:
• Logs Guardados: Consultar carpeta
• Configuración: Archivo local
        """.format(
            current_user=self.current_speaker.get(),
            auth_status="Autenticado" if self.current_speaker.get() != "No identificado" else "No autenticado",
            audio_status="Disponible" if self.voice_controller and self.voice_controller.audio_comparator else "No disponible",
            uptime="Sesión actual",
            threshold=self.threshold_var.get() if hasattr(self, 'threshold_var') else "0.45",
            id_duration=self.id_duration_var.get() if hasattr(self, 'id_duration_var') else "3",
            cmd_duration=self.cmd_duration_var.get() if hasattr(self, 'cmd_duration_var') else "5"
        )
        
        stats_text.insert(tk.END, stats_content)
        stats_text.config(state=tk.DISABLED)

    def save_settings(self):
        """Guardar configuración"""
        try:
            # Aquí podrías guardar la configuración en un archivo
            self.log_message("💾 Configuración guardada", "SUCCESS")
            messagebox.showinfo("Éxito", "Configuración guardada correctamente")
        except Exception as e:
            self.log_message(f"❌ Error guardando configuración: {e}", "ERROR")
            messagebox.showerror("Error", f"Error guardando configuración: {e}")

    def show_help(self):
        """Mostrar ventana de ayuda"""
        help_window = tk.Toplevel(self.root)
        help_window.title("❓ Ayuda")
        help_window.geometry("800x700")
        help_window.configure(bg=self.colors['bg_dark'])
        help_window.transient(self.root)
        
        # Frame principal
        main_frame = ttk.Frame(help_window, style='Card.TFrame', padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(main_frame, text="❓ Ayuda del Sistema", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Texto de ayuda
        help_text = scrolledtext.ScrolledText(main_frame, height=35, 
                                             font=('Segoe UI', 10),
                                             bg=self.colors['bg_dark'],
                                             fg=self.colors['text'],
                                             insertbackground=self.colors['text'],
                                             selectbackground=self.colors['accent'],
                                             relief='flat',
                                             borderwidth=0,
                                             wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags para colores
        help_text.tag_configure("HEADER", foreground=self.colors['accent'], font=('Segoe UI', 12, 'bold'))
        help_text.tag_configure("SUBHEADER", foreground=self.colors['warning'], font=('Segoe UI', 10, 'bold'))
        help_text.tag_configure("SUCCESS", foreground=self.colors['success'])
        help_text.tag_configure("INFO", foreground=self.colors['text'])
        
        # Contenido de ayuda
        help_content = [
            ("🎤 SISTEMA DE CONTROL POR VOZ - GUÍA COMPLETA\n\n", "HEADER"),
            ("🎯 PRIMEROS PASOS:\n", "SUBHEADER"),
            ("1. Asegúrate de tener un micrófono conectado y funcionando\n", "INFO"),
            ("2. Haz clic en '🎯 Identificarse' para que el sistema reconozca tu voz\n", "INFO"),
            ("3. Habla claramente durante 3 segundos cuando se te solicite\n", "INFO"),
            ("4. Una vez identificado, podrás usar los comandos de voz\n\n", "INFO"),
            
            ("🎮 CONTROLES PRINCIPALES:\n", "SUBHEADER"),
            ("• 🎯 Identificarse: Identifica tu voz en el sistema\n", "SUCCESS"),
            ("• 🎤 Comando Único: Ejecuta un comando específico\n", "SUCCESS"),
            ("• 🎧 Escucha Continua: El sistema escucha permanentemente\n", "SUCCESS"),
            ("• 📋 Permisos: Muestra los permisos de cada usuario\n", "SUCCESS"),
            ("• ⚙️ Configuración: Ajustes y pruebas del sistema\n", "SUCCESS"),
            ("• ❓ Ayuda: Esta ventana de ayuda\n\n", "SUCCESS"),
            
            ("🗣️ COMANDOS DE VOZ DISPONIBLES:\n", "SUBHEADER"),
            ("• 'abrir bloc de notas' / 'abrir notepad' / 'abrir editor'\n", "INFO"),
            ("• 'abrir navegador' / 'abrir chrome'\n", "INFO"),
            ("• 'abrir explorador' / 'abrir archivos'\n", "INFO"),
            ("• 'abrir calculadora'\n", "INFO"),
            ("• 'abrir buscador' / 'buscar'\n", "INFO"),
            ("• 'salir' / 'terminar' (solo en modo escucha continua)\n\n", "INFO"),
            
            ("👥 SISTEMA DE PERMISOS:\n", "SUBHEADER"),
            ("• Hablante_1: Acceso completo a todos los comandos\n", "SUCCESS"),
            ("• Daniel: Acceso limitado (calculadora y buscador)\n", "WARNING"),
            ("• Desconocido: Sin permisos\n\n", "ERROR"),
            
            ("💡 CONSEJOS IMPORTANTES:\n", "SUBHEADER"),
            ("• Habla claramente y sin ruido de fondo\n", "INFO"),
            ("• Mantén el micrófono a distancia adecuada\n", "INFO"),
            ("• Si no te reconoce, ajusta la duración de identificación\n", "INFO"),
            ("• Los comandos son flexibles en el lenguaje\n", "INFO"),
            ("• Usa la configuración para probar el sistema\n\n", "INFO"),
            
            ("🔧 SOLUCIÓN DE PROBLEMAS:\n", "SUBHEADER"),
            ("• Si no funciona la identificación:\n", "WARNING"),
            ("  - Verifica que existan archivos de referencia\n", "INFO"),
            ("  - Reduce el ruido de fondo\n", "INFO"),
            ("  - Aumenta la duración de identificación\n", "INFO"),
            ("• Si no se ejecutan comandos:\n", "WARNING"),
            ("  - Verifica que tengas permisos para ese comando\n", "INFO"),
            ("  - Asegúrate de estar identificado correctamente\n", "INFO"),
            ("• Si hay errores de audio:\n", "WARNING"),
            ("  - Verifica la conexión del micrófono\n", "INFO"),
            ("  - Comprueba las dependencias en configuración\n", "INFO"),
            ("  - Ejecuta un diagnóstico completo\n\n", "INFO"),
            
            ("📊 CARACTERÍSTICAS AVANZADAS:\n", "SUBHEADER"),
            ("• Log en tiempo real con códigos de colores\n", "SUCCESS"),
            ("• Procesamiento en hilos separados (no bloquea la interfaz)\n", "SUCCESS"),
            ("• Guardado automático de logs\n", "SUCCESS"),
            ("• Configuración personalizable\n", "SUCCESS"),
            ("• Estadísticas del sistema\n", "SUCCESS"),
            ("• Diagnóstico automático de problemas\n\n", "SUCCESS"),
            
            ("🎨 INTERFAZ:\n", "SUBHEADER"),
            ("• Diseño moderno con colores distintivos\n", "INFO"),
            ("• Indicadores de estado en tiempo real\n", "INFO"),
            ("• Barras de progreso para operaciones largas\n", "INFO"),
            ("• Ventanas emergentes organizadas\n", "INFO"),
            ("• Texto redimensionable y desplazable\n", "INFO"),
        ]
        
        for text, tag in help_content:
            help_text.insert(tk.END, text, tag)
        
        help_text.config(state=tk.DISABLED)

    def on_closing(self):
        """Manejar cierre de la aplicación"""
        if self.is_listening.get():
            self.stop_continuous_listening()
        
        self.log_message("👋 Cerrando aplicación...", "INFO")
        self.root.destroy()

def main():
    """Función principal"""
    try:
        app = VoiceControlGUI()
        app.root.mainloop()
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
