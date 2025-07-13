#!/usr/bin/env python3
"""
Sistema de Control por Voz con Identificación de Hablante
Permite ejecutar comandos específicos según la identidad del hablante identificado
"""

import speech_recognition as sr
import subprocess
import pyautogui
import os
import sys
import time
from pathlib import Path

# Agregar rutas del proyecto para poder importar el comparador
sys.path.append(os.path.dirname(__file__))

try:
    from audio_comparator_menu import AudioComparator
    COMPARATOR_AVAILABLE = True
except ImportError:
    print("⚠️  AudioComparator no disponible. Funcionando en modo básico.")
    COMPARATOR_AVAILABLE = False

class VoiceController:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000  # Ajustar según el ruido ambiental
        self.recognizer.dynamic_energy_threshold = True
        
        # Configurar sistema de permisos
        self.permisos = {
            "Hablante_1": [
                "abrir bloc de notas",
                "abrir notepad", 
                "abrir editor",
                "abrir navegador",
                "abrir chrome",
                "abrir explorador",
                "abrir archivos",
                "abrir calculadora",
                "abrir buscador"
            ],
            "Daniel": [
                "abrir calculadora",
                "abrir buscador"
            ],
            "Desconocido": []
        }
        
        # Inicializar audio comparator si está disponible
        if COMPARATOR_AVAILABLE:
            try:
                self.audio_comparator = AudioComparator()
                print("✅ Audio Comparator inicializado correctamente")
            except Exception as e:
                print(f"⚠️ Error inicializando Audio Comparator: {e}")
                self.audio_comparator = None
        else:
            self.audio_comparator = None
            print("⚠️ Audio Comparator no disponible")
        
        # Estado del usuario
        self.current_speaker = "Desconocido"
        self.authenticated = False
        
        # Control de escucha continua
        self.continuous_listening = False
        self.stop_listening = False
        
        # Procesos abiertos
        self.proceso_notepad = None
        
        # Saludo personalizado
        self.saludo = "¡Hola! Soy tu asistente de voz personalizado. ¿En qué puedo ayudarte hoy?"
        
        print("🎤 Sistema de Control por Voz inicializado")
        print(f"🔧 Usuarios configurados: {', '.join([k for k in self.permisos.keys() if k != 'Desconocido'])}")
        
        # Verificar dependencias críticas
        self.verificar_dependencias()

    def verificar_dependencias(self):
        """Verificar que las dependencias críticas estén instaladas"""
        dependencias = [
            "speech_recognition",
            "pyautogui"
        ]
        
        for dep in dependencias:
            try:
                __import__(dep)
            except ImportError:
                print(f"⚠️ Dependencia faltante: {dep}")
                print(f"   Instalar con: pip install {dep}")

    def identificar_hablante(self, duracion=3, auto_start=False):
        """Identificar al hablante actual usando grabación de voz
        
        Args:
            duracion (int): Duración de la grabación en segundos
            auto_start (bool): Si True, inicia automáticamente sin esperar Enter
        """
        if not COMPARATOR_AVAILABLE:
            print("❌ Sistema de identificación no disponible")
            return "Desconocido"
        
        print("\n🎤 IDENTIFICANDO HABLANTE...")
        print("=" * 50)
        print(f"⏱️  Habla durante {duracion} segundos para identificarte")
        print("🔊 Di algo como: 'Hola, soy [tu nombre]' o cuenta hasta 10")
        
        # Grabar audio para identificación
        recorded_file = self.audio_comparator.record_audio(duration=duracion, auto_start=auto_start)
        if not recorded_file:
            print("❌ Error en la grabación")
            return "Desconocido"
        
        # Referencias conocidas - usar las mismas que el audio_comparator
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
        
        # Verificar archivos disponibles
        available_references = {}
        for person, files in reference_files.items():
            available_files = [f for f in files if os.path.exists(f)]
            if available_files:
                available_references[person] = available_files
        
        if not available_references:
            print("❌ No se encontraron archivos de referencia")
            try:
                os.remove(recorded_file)
            except:
                pass
            return "Desconocido"
        
        # Comparar con personas conocidas usando el modelo ERes2Net (opción 2)
        results = {}
        model_choice = "2"  # Usar ERes2Net por defecto
        
        print("🔍 Comparando con hablantes conocidos...")
        
        for person, reference_files_list in available_references.items():
            print(f"   👤 Comparando con {person}...")
            person_scores = []
            
            for ref_file in reference_files_list[:2]:  # Solo 2 archivos para ser más rápido
                try:
                    # Usar el modelo cargado directamente para mejor control
                    score = self.audio_comparator.compare_with_model(model_choice, recorded_file, ref_file)
                    
                    if score is not None:
                        person_scores.append(score)
                        print(f"      🎯 {os.path.basename(ref_file)}: {score:.3f}")
                except Exception as e:
                    print(f"      ❌ Error con {ref_file}: {e}")
                    continue
            
            if person_scores:
                avg_score = sum(person_scores) / len(person_scores)
                results[person] = avg_score
                print(f"   📊 Promedio para {person}: {avg_score:.3f}")
        
        # Limpiar archivo temporal
        try:
            os.remove(recorded_file)
        except:
            pass
        
        # Determinar el hablante
        if results:
            best_person = max(results.items(), key=lambda x: x[1])
            best_speaker = best_person[0]
            best_score = best_person[1]
            
            # Threshold para aceptar identificación (usando los del modelo ERes2Net)
            threshold = 0.45  # Threshold medio del modelo ERes2Net
            
            if best_score > threshold:
                print(f"✅ Hablante identificado: {best_speaker} (confianza: {best_score:.3f})")
                print(f"📊 Todos los scores: {[(p, f'{s:.3f}') for p, s in sorted(results.items(), key=lambda x: x[1], reverse=True)]}")
                # Actualizar el estado del sistema
                self.current_speaker = best_speaker
                self.authenticated = True
                return best_speaker
            else:
                print(f"❓ Hablante no identificado claramente")
                print(f"📊 Mejor resultado: {best_speaker} con {best_score:.3f} (threshold: {threshold})")
                print(f"📊 Todos los scores: {[(p, f'{s:.3f}') for p, s in sorted(results.items(), key=lambda x: x[1], reverse=True)]}")
                # Resetear el estado del sistema
                self.current_speaker = "Desconocido"
                self.authenticated = False
                return "Desconocido"
        else:
            print("❌ No se pudo realizar la identificación")
            # Resetear el estado del sistema
            self.current_speaker = "Desconocido"
            self.authenticated = False
            return "Desconocido"

    def ejecutar_comando(self, comando):
        """Ejecutar comando si el hablante tiene permisos"""
        comando_original = comando
        comando = comando.lower()
        
        # Comandos que no requieren autenticación
        if "identificar hablante" in comando or "identificar" in comando:
            self.current_speaker = self.identificar_hablante()
            self.authenticated = True if self.current_speaker != "Desconocido" else False
            return
        
        if "estado sistema" in comando or "estado" in comando:
            self.mostrar_estado()
            return
        
        # Verificar autenticación
        if not self.authenticated or self.current_speaker is None:
            print("🚫 Debes identificarte primero. Di 'identificar hablante'")
            return
        
        # Verificar permisos usando el método correcto
        if not self.verificar_permisos(comando, self.current_speaker):
            print(f"🚫 {self.current_speaker} no tiene permisos para ejecutar: '{comando_original}'")
            print(f"📋 Comandos disponibles para {self.current_speaker}:")
            permisos = self.obtener_permisos(self.current_speaker)
            for cmd in permisos:
                print(f"   • {cmd}")
            return
        
        # Ejecutar comandos específicos
        if "abrir notepad" in comando or "abrir bloc de notas" in comando:
            try:
                self.proceso_notepad = subprocess.Popen(["notepad.exe"])
                print(f"✅ {self.current_speaker}: Bloc de notas abierto.")
            except Exception as e:
                print(f"❌ Error abriendo notepad: {e}")
                
        elif "saludar seguidores" in comando or "escribir saludo" in comando:
            try:
                pyautogui.write(self.saludo)
                print(f"✅ {self.current_speaker}: Saludo escrito.")
            except Exception as e:
                print(f"❌ Error escribiendo saludo: {e}")
                
        elif "cerrar notepad" in comando or "cerrar bloc de notas" in comando:
            if self.proceso_notepad:
                try:
                    self.proceso_notepad.terminate()
                    self.proceso_notepad = None
                    print(f"✅ {self.current_speaker}: Bloc de notas cerrado.")
                except Exception as e:
                    print(f"❌ Error cerrando notepad: {e}")
            else:
                print("⚠️  No hay ningún bloc de notas abierto por este sistema.")
                
        elif "salir" in comando:
            print(f"👋 {self.current_speaker}: Saliendo del asistente por voz.")
            if self.proceso_notepad:
                try:
                    self.proceso_notepad.terminate()
                except:
                    pass
            exit()
        else:
            print(f"🤔 Comando '{comando_original}' no reconocido.")

    def mostrar_estado(self):
        """Mostrar estado actual del sistema"""
        print("\n📊 ESTADO DEL SISTEMA")
        print("=" * 40)
        print(f"👤 Hablante actual: {self.current_speaker if self.current_speaker else 'No identificado'}")
        print(f"🔐 Autenticado: {'Sí' if self.authenticated else 'No'}")
        print(f"💻 Notepad abierto: {'Sí' if self.proceso_notepad else 'No'}")
        print(f"🎤 Reconocimiento: {'Activo' if COMPARATOR_AVAILABLE else 'Modo básico'}")
        
        if self.current_speaker and self.current_speaker in self.permisos:
            print(f"📋 Comandos disponibles:")
            for cmd in self.permisos[self.current_speaker]:
                print(f"   • {cmd}")
        print("=" * 40)

    def mostrar_ayuda(self):
        """Mostrar ayuda y comandos disponibles"""
        print("\n🎤 ASISTENTE DE VOZ CON IDENTIFICACIÓN DE HABLANTE")
        print("=" * 60)
        print("🔊 COMANDOS DISPONIBLES:")
        print()
        print("🎯 COMANDOS GENERALES:")
        print("   • 'identificar hablante' - Identificarte en el sistema")
        print("   • 'estado sistema' - Ver estado actual")
        print("   • 'salir' - Cerrar el asistente")
        print()
        print("👤 COMANDOS POR HABLANTE:")
        
        for hablante, comandos in self.permisos.items():
            if hablante != "Desconocido":
                print(f"\n🔹 {hablante}:")
                for cmd in comandos:
                    if cmd not in ["identificar hablante", "estado sistema"]:
                        print(f"   • '{cmd}'")
        
        print("\n📝 INSTRUCCIONES:")
        print("1. Di 'identificar hablante' para autenticarte")
        print("2. Habla claramente durante 3 segundos cuando se te solicite")
        print("3. Una vez identificado, puedes usar tus comandos permitidos")
        print("4. Di 'estado' para ver tu estado actual")
        print("5. Di 'salir' para cerrar el asistente")
        print("=" * 60)

    def escuchar_comandos(self):
        """Función principal para escuchar y procesar comandos de voz"""
        print("🎤 Iniciando sistema de control por voz...")
        
        # Mostrar ayuda inicial
        self.mostrar_ayuda()
        
        with sr.Microphone() as source:
            print("\n🎤 Ajustando al ruido ambiental...")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("✅ Listo para recibir comandos.")
            
            while True:
                try:
                    print("\n⏳ Escuchando comando...")
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    print("🔄 Procesando audio...")
                    comando = self.recognizer.recognize_google(audio, language="es-ES")
                    print(f"📣 Comando reconocido: '{comando}'")
                    
                    self.ejecutar_comando(comando)
                    
                except sr.WaitTimeoutError:
                    # No hay problema, solo continúa escuchando
                    pass
                except sr.UnknownValueError:
                    print("❌ No se entendió el audio. Intenta hablar más claro.")
                except sr.RequestError as e:
                    print(f"⚠️ Error al conectar con el servicio de reconocimiento: {e}")
                    print("🔄 Intentando continuar...")
                    time.sleep(2)
                except KeyboardInterrupt:
                    print("\n👋 Asistente interrumpido por el usuario.")
                    break
                except Exception as e:
                    print(f"😵 Error inesperado: {e}")
                    time.sleep(1)

    def mostrar_menu(self):
        """Mostrar el menú principal del sistema de control por voz"""
        print("\n" + "="*60)
        print("🎙️  SISTEMA DE CONTROL POR VOZ 🎙️")
        print("="*60)
        print("1. 🎯 Identificarse (Identificación de hablante)")
        print("2. 🎤 Comando por voz (requiere identificación previa)")
        print("3. 📊 Ver permisos actuales")
        print("4. 🔄 Configuración y pruebas")
        print("5. 📋 Ayuda - Lista de comandos disponibles")
        print("6. 🎧 Modo escucha continua")
        print("0. 🚪 Salir")
        print("="*60)
        
        if hasattr(self, 'current_speaker') and self.current_speaker != "Desconocido":
            print(f"👤 Usuario actual: {self.current_speaker}")
            permisos = self.obtener_permisos(self.current_speaker)
            print(f"🔑 Permisos: {', '.join(permisos) if permisos else 'Ninguno'}")
        else:
            print("👤 Usuario: No identificado")
        print("="*60)
    
    def ejecutar_menu(self):
        """Ejecutar el menú principal"""
        while True:
            self.mostrar_menu()
            
            try:
                opcion = input("\nSelecciona una opción (0-6): ").strip()
                
                if opcion == "0":
                    print("👋 ¡Hasta luego!")
                    break
                
                elif opcion == "1":
                    print("\n🎯 IDENTIFICACIÓN DE HABLANTE")
                    print("-" * 50)
                    
                    # Configurar duración de identificación
                    try:
                        duracion_input = input("⏱️  Duración de identificación en segundos (3-10, default: 3): ").strip()
                        duracion = int(duracion_input) if duracion_input else 3
                        duracion = max(3, min(duracion, 10))  # Entre 3 y 10 segundos
                    except ValueError:
                        duracion = 3
                    
                    # Realizar identificación
                    self.current_speaker = self.identificar_hablante(duracion)
                    
                    if self.current_speaker != "Desconocido":
                        permisos = self.obtener_permisos(self.current_speaker)
                        print(f"\n✅ Bienvenido/a {self.current_speaker}!")
                        print(f"🔑 Tienes acceso a: {', '.join(permisos) if permisos else 'Sin permisos especiales'}")
                    else:
                        print("\n❌ No se pudo identificar al hablante")
                        print("💡 Consejos:")
                        print("   - Habla claramente y sin ruido de fondo")
                        print("   - Asegúrate de que el micrófono funcione correctamente")
                        print("   - Intenta aumentar la duración de identificación")
                    
                    input("\nPresiona Enter para continuar...")
                
                elif opcion == "2":
                    if not hasattr(self, 'current_speaker') or self.current_speaker == "Desconocido":
                        print("\n❌ Debes identificarte primero (opción 1)")
                        input("Presiona Enter para continuar...")
                        continue
                    
                    print(f"\n🎤 COMANDO POR VOZ - Usuario: {self.current_speaker}")
                    print("-" * 50)
                    
                    # Configurar duración del comando
                    try:
                        duracion_input = input("⏱️  Duración del comando en segundos (3-10, default: 5): ").strip()
                        duracion = int(duracion_input) if duracion_input else 5
                        duracion = max(3, min(duracion, 10))
                    except ValueError:
                        duracion = 5
                    
                    # Ejecutar comando por voz
                    self.procesar_comando_voz(duracion)
                    input("\nPresiona Enter para continuar...")
                
                elif opcion == "3":
                    print("\n📊 PERMISOS DEL SISTEMA")
                    print("-" * 50)
                    
                    for usuario, permisos in self.permisos.items():
                        print(f"👤 {usuario}:")
                        if permisos:
                            for permiso in permisos:
                                print(f"   ✅ {permiso}")
                        else:
                            print("   ❌ Sin permisos")
                        print()
                    
                    if hasattr(self, 'current_speaker') and self.current_speaker != "Desconocido":
                        print(f"🔑 Tus permisos actuales ({self.current_speaker}):")
                        user_permisos = self.obtener_permisos(self.current_speaker)
                        if user_permisos:
                            for permiso in user_permisos:
                                print(f"   ✅ {permiso}")
                        else:
                            print("   ❌ Sin permisos")
                    
                    input("\nPresiona Enter para continuar...")
                
                elif opcion == "4":
                    print("\n🔄 CONFIGURACIÓN Y PRUEBAS")
                    print("-" * 50)
                    print("1. 🎙️  Configurar micrófono")
                    print("2. 🎯 Probar identificación")
                    print("3. 📊 Información del sistema")
                    print("4. 🔧 Diagnóstico de problemas")
                    print("0. Volver al menú principal")
                    
                    config_opcion = input("\nSelecciona una opción: ").strip()
                    
                    if config_opcion == "1":
                        self.configurar_microfono()
                    elif config_opcion == "2":
                        print("\n🧪 PRUEBA DE IDENTIFICACIÓN")
                        print("-" * 30)
                        test_speaker = self.identificar_hablante(5)
                        print(f"Resultado de la prueba: {test_speaker}")
                    elif config_opcion == "3":
                        self.mostrar_info_sistema()
                    elif config_opcion == "4":
                        self.diagnosticar_problemas()
                    
                    input("\nPresiona Enter para continuar...")
                
                elif opcion == "5":
                    self.mostrar_ayuda()
                    input("\nPresiona Enter para continuar...")
                
                elif opcion == "6":
                    if not hasattr(self, 'current_speaker') or self.current_speaker == "Desconocido":
                        print("\n❌ Debes identificarte primero (opción 1)")
                        input("Presiona Enter para continuar...")
                        continue
                    
                    print(f"\n🎧 MODO ESCUCHA CONTINUA - Usuario: {self.current_speaker}")
                    print("-" * 50)
                    print("🔊 El sistema ahora escuchará continuamente tus comandos")
                    print("🛑 Presiona Ctrl+C para salir del modo escucha")
                    print("📋 Comandos disponibles:")
                    
                    user_permisos = self.obtener_permisos(self.current_speaker)
                    if user_permisos:
                        for permiso in user_permisos:
                            print(f"   • {permiso}")
                    
                    input("\nPresiona Enter para iniciar el modo escucha...")
                    
                    try:
                        self.escuchar_comandos_continuo()
                    except KeyboardInterrupt:
                        print("\n🛑 Saliendo del modo escucha continua...")
                
                else:
                    print("❌ Opción no válida")
                    input("Presiona Enter para continuar...")
            
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("Presiona Enter para continuar...")

    def procesar_comando_voz(self, duracion=5):
        """Procesar un comando de voz único"""
        print(f"\n🎤 Grabando comando ({duracion} segundos)...")
        print("🔊 Habla claramente tu comando ahora...")
        
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                print("🔴 ¡GRABANDO!")
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=duracion)
                
                print("🔄 Procesando comando...")
                comando = self.recognizer.recognize_google(audio, language="es-ES")
                print(f"📣 Comando reconocido: '{comando}'")
                
                # Ejecutar comando
                self.ejecutar_comando_simple(comando)
                
        except sr.WaitTimeoutError:
            print("❌ No se detectó audio en el tiempo esperado")
        except sr.UnknownValueError:
            print("❌ No se entendió el audio. Intenta hablar más claro.")
        except sr.RequestError as e:
            print(f"⚠️ Error al conectar con el servicio de reconocimiento: {e}")
        except Exception as e:
            print(f"❌ Error procesando comando: {e}")

    def escuchar_comandos_continuo(self):
        """Escuchar comandos de forma continua"""
        print("\n🎧 Iniciando escucha continua...")
        
        # Reset del flag de parada
        self.stop_listening = False
        self.continuous_listening = True
        
        with sr.Microphone() as source:
            print("🎤 Ajustando al ruido ambiental...")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("✅ Listo para recibir comandos.")
            
            while not self.stop_listening:
                try:
                    print("\n⏳ Escuchando comando...")
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    # Verificar si se debe parar antes de procesar
                    if self.stop_listening:
                        break
                    
                    print("🔄 Procesando audio...")
                    comando = self.recognizer.recognize_google(audio, language="es-ES")
                    print(f"📣 Comando reconocido: '{comando}'")
                    
                    if "salir" in comando.lower() or "terminar" in comando.lower():
                        print("🛑 Saliendo del modo escucha continua...")
                        break
                    
                    # Verificar si se debe parar antes de ejecutar
                    if self.stop_listening:
                        break
                    
                    self.ejecutar_comando_simple(comando)
                    
                except sr.WaitTimeoutError:
                    # No hay problema, solo continúa escuchando
                    # Verificar si se debe parar durante el timeout
                    if self.stop_listening:
                        break
                    pass
                except sr.UnknownValueError:
                    if not self.stop_listening:
                        print("❌ No se entendió el audio. Intenta hablar más claro.")
                except sr.RequestError as e:
                    if not self.stop_listening:
                        print(f"⚠️ Error al conectar con el servicio de reconocimiento: {e}")
                        print("🔄 Intentando continuar...")
                        time.sleep(2)
                except KeyboardInterrupt:
                    print("\n👋 Saliendo del modo escucha...")
                    break
                except Exception as e:
                    if not self.stop_listening:
                        print(f"😵 Error inesperado: {e}")
                        time.sleep(1)
        
        # Limpiar estado
        self.continuous_listening = False
        self.stop_listening = False
        print("🔇 Escucha continua finalizada")

    def detener_escucha_continua(self):
        """Detener la escucha continua desde el exterior"""
        if self.continuous_listening:
            print("🛑 Señal de parada enviada...")
            self.stop_listening = True

    def ejecutar_comando_simple(self, comando):
        """Ejecutar comando simple sin autenticación (ya autenticado)"""
        comando_original = comando
        comando = comando.lower()
        
        # Verificar permisos
        if not self.verificar_permisos(comando, self.current_speaker):
            print(f"🚫 {self.current_speaker} no tiene permisos para: '{comando_original}'")
            return
        
        # Ejecutar comandos específicos
        if any(word in comando for word in ["bloc de notas", "notepad", "editor"]):
            try:
                subprocess.Popen(["notepad.exe"])
                print(f"✅ {self.current_speaker}: Bloc de notas abierto")
            except Exception as e:
                print(f"❌ Error abriendo bloc de notas: {e}")
                
        elif any(word in comando for word in ["navegador", "chrome", "browser"]):
            try:
                subprocess.Popen(["start", "chrome"], shell=True)
                print(f"✅ {self.current_speaker}: Navegador abierto")
            except Exception as e:
                print(f"❌ Error abriendo navegador: {e}")
                
        elif any(word in comando for word in ["explorador", "archivos", "explorer"]):
            try:
                subprocess.Popen(["explorer"])
                print(f"✅ {self.current_speaker}: Explorador abierto")
            except Exception as e:
                print(f"❌ Error abriendo explorador: {e}")
                
        elif any(word in comando for word in ["calculadora", "calc"]):
            try:
                subprocess.Popen(["calc"])
                print(f"✅ {self.current_speaker}: Calculadora abierta")
            except Exception as e:
                print(f"❌ Error abriendo calculadora: {e}")
                
        elif any(word in comando for word in ["buscar", "buscador"]):
            try:
                subprocess.Popen(["start", "ms-settings:search"], shell=True)
                print(f"✅ {self.current_speaker}: Buscador abierto")
            except Exception as e:
                print(f"❌ Error abriendo buscador: {e}")
                
        else:
            print(f"🤔 Comando '{comando_original}' no reconocido")
            print("💡 Comandos disponibles:")
            user_permisos = self.obtener_permisos(self.current_speaker)
            for permiso in user_permisos:
                print(f"   • {permiso}")

    def configurar_microfono(self):
        """Configurar y probar el micrófono"""
        print("\n🎙️  CONFIGURACIÓN DEL MICRÓFONO")
        print("-" * 40)
        
        try:
            import sounddevice as sd
            
            # Mostrar dispositivos disponibles
            print("📱 Dispositivos de audio disponibles:")
            devices = sd.query_devices()
            
            input_devices = []
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    input_devices.append((i, device))
                    print(f"   {i}: {device['name']} (Canales: {device['max_input_channels']})")
            
            if not input_devices:
                print("❌ No se encontraron dispositivos de entrada")
                return
            
            print(f"\n🎙️  Dispositivo actual: {sd.default.device}")
            
            # Probar grabación
            test_record = input("\n¿Hacer una grabación de prueba? (s/n): ").strip().lower()
            if test_record in ['s', 'si', 'sí', 'y', 'yes']:
                print("\n🧪 Grabación de prueba (3 segundos)...")
                test_file = self.audio_comparator.record_audio(duration=3)
                if test_file:
                    print("✅ Grabación de prueba exitosa")
                    try:
                        os.remove(test_file)
                    except:
                        pass
                else:
                    print("❌ Error en la grabación de prueba")
        
        except ImportError:
            print("❌ sounddevice no está instalado")
        except Exception as e:
            print(f"❌ Error configurando micrófono: {e}")

    def mostrar_info_sistema(self):
        """Mostrar información del sistema"""
        print("\n📊 INFORMACIÓN DEL SISTEMA")
        print("-" * 40)
        
        # Estado del comparador de audio
        if COMPARATOR_AVAILABLE:
            print("✅ Audio Comparator: Disponible")
            print(f"   🖥️  Dispositivo: {self.audio_comparator.device}")
            
            # Verificar modelos disponibles
            print("   📊 Modelos disponibles:")
            for key, model in self.audio_comparator.models_config.items():
                if model.get('use_original'):
                    print(f"      {key}. {model['name']} (Script Original)")
                elif 'model_paths' in model:
                    available = any(os.path.exists(path) for path in model['model_paths'])
                    status = "✅" if available else "❌"
                    print(f"      {key}. {model['name']} {status}")
        else:
            print("❌ Audio Comparator: No disponible")
        
        # Archivos de referencia
        print("\n📁 Archivos de referencia:")
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
            print(f"   👤 {person}: {status}")
        
        # Dependencias
        print("\n📦 Dependencias:")
        try:
            import speech_recognition
            print("   ✅ SpeechRecognition")
        except ImportError:
            print("   ❌ SpeechRecognition")
        
        try:
            import sounddevice
            print("   ✅ sounddevice")
        except ImportError:
            print("   ❌ sounddevice")
        
        try:
            import pyautogui
            print("   ✅ pyautogui")
        except ImportError:
            print("   ❌ pyautogui")

    def diagnosticar_problemas(self):
        """Diagnosticar problemas comunes"""
        print("\n🔧 DIAGNÓSTICO DE PROBLEMAS")
        print("-" * 40)
        
        print("🔍 Verificando sistema...")
        
        # 1. Verificar micrófono
        print("\n1. 🎙️  Verificando micrófono...")
        try:
            with sr.Microphone() as source:
                print("   ✅ Micrófono detectado")
        except Exception as e:
            print(f"   ❌ Error con micrófono: {e}")
        
        # 2. Verificar archivos de referencia
        print("\n2. 📁 Verificando archivos de referencia...")
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
            if available_files:
                print(f"   ✅ {person}: {len(available_files)} archivos disponibles")
            else:
                print(f"   ❌ {person}: No hay archivos disponibles")
        
        # 3. Verificar modelos
        print("\n3. 🤖 Verificando modelos...")
        if COMPARATOR_AVAILABLE:
            for key, model in self.audio_comparator.models_config.items():
                if model.get('use_original'):
                    print(f"   ✅ {model['name']}: Script original disponible")
                elif 'model_paths' in model:
                    available = any(os.path.exists(path) for path in model['model_paths'])
                    status = "✅" if available else "❌"
                    print(f"   {status} {model['name']}")
        else:
            print("   ❌ Audio Comparator no disponible")
        
        # 4. Verificar dependencias
        print("\n4. 📦 Verificando dependencias...")
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
                print(f"   ✅ {name}")
            except ImportError:
                print(f"   ❌ {name} no instalado")
        
        print("\n💡 SOLUCIONES COMUNES:")
        print("• Si falla el micrófono: Verificar permisos y conexión")
        print("• Si no hay archivos de referencia: Grabar nuevos audios")
        print("• Si falla la identificación: Verificar modelos y thresholds")
        print("• Si faltan dependencias: pip install -r requirements.txt")

    def obtener_permisos(self, hablante):
        """Obtener lista de permisos del hablante"""
        return self.permisos.get(hablante, [])

    def verificar_permisos(self, comando, hablante):
        """Verificar si el hablante tiene permisos para ejecutar el comando"""
        permisos = self.obtener_permisos(hablante)
        
        comando_lower = comando.lower()
        
        # Verificar cada permiso
        for permiso in permisos:
            permiso_lower = permiso.lower()
            
            # Verificar coincidencias flexibles
            if ("bloc" in permiso_lower or "notepad" in permiso_lower or "editor" in permiso_lower) and \
               ("bloc" in comando_lower or "notepad" in comando_lower or "editor" in comando_lower):
                return True
            elif ("navegador" in permiso_lower or "chrome" in permiso_lower) and \
                 ("navegador" in comando_lower or "chrome" in comando_lower or "browser" in comando_lower):
                return True
            elif ("explorador" in permiso_lower or "archivos" in permiso_lower) and \
                 ("explorador" in comando_lower or "archivos" in comando_lower or "explorer" in comando_lower):
                return True
            elif ("calculadora" in permiso_lower or "calc" in permiso_lower) and \
                 ("calculadora" in comando_lower or "calc" in comando_lower):
                return True
            elif ("buscar" in permiso_lower or "buscador" in permiso_lower) and \
                 ("buscar" in comando_lower or "buscador" in comando_lower):
                return True
        
        return False

    def mostrar_ayuda(self):
        """Mostrar ayuda del sistema"""
        print("\n📋 AYUDA - SISTEMA DE CONTROL POR VOZ")
        print("=" * 50)
        
        print("\n🎯 CÓMO USAR EL SISTEMA:")
        print("1. Primero debes identificarte con la opción 1")
        print("2. Luego puedes usar comandos de voz con la opción 2")
        print("3. Los comandos disponibles dependen de tus permisos")
        print("4. También puedes usar el modo escucha continua (opción 6)")
        
        print("\n🎤 COMANDOS DE VOZ DISPONIBLES:")
        print("📝 'abrir bloc de notas' / 'abrir notepad' / 'abrir editor'")
        print("🌐 'abrir navegador' / 'abrir chrome'")
        print("📁 'abrir explorador' / 'abrir archivos'")
        print("🔍 'abrir buscador' / 'buscar'")
        print("🖩 'abrir calculadora'")
        print("🛑 'salir' / 'terminar' (solo en modo escucha continua)")
        
        print("\n👥 PERMISOS POR USUARIO:")
        for usuario, permisos in self.permisos.items():
            print(f"👤 {usuario}:")
            if permisos:
                for permiso in permisos:
                    print(f"   ✅ {permiso}")
            else:
                print("   ❌ Sin permisos")
        
        print("\n💡 CONSEJOS:")
        print("• Habla claramente y sin ruido de fondo")
        print("• Asegúrate de que el micrófono funcione correctamente")
        print("• Si no te reconoce, aumenta la duración de identificación")
        print("• Los comandos son flexibles (puedes decir 'bloc de notas' o 'notepad')")
        print("• Usa la opción 4 para configurar y probar el sistema")
        
        print("\n🔧 SOLUCIÓN DE PROBLEMAS:")
        print("• Si no funciona la identificación: Verifica archivos de referencia")
        print("• Si no funciona el micrófono: Configura en la opción 4")
        print("• Si no se ejecutan comandos: Verifica permisos del usuario")
        print("• Si hay errores de audio: Instala dependencias faltantes")

    def mostrar_estado(self):
        """Mostrar estado actual del sistema"""
        print("\n📊 ESTADO DEL SISTEMA")
        print("=" * 40)
        print(f"👤 Hablante actual: {getattr(self, 'current_speaker', 'No identificado')}")
        print(f"🔐 Autenticado: {'Sí' if hasattr(self, 'current_speaker') and self.current_speaker != 'Desconocido' else 'No'}")
        print(f"🎤 Reconocimiento: {'Activo' if COMPARATOR_AVAILABLE else 'Modo básico'}")
        
        if hasattr(self, 'current_speaker') and self.current_speaker != "Desconocido":
            permisos = self.obtener_permisos(self.current_speaker)
            print(f"📋 Comandos disponibles:")
            if permisos:
                for permiso in permisos:
                    print(f"   • {permiso}")
            else:
                print("   • Sin permisos")
        print("=" * 40)

def main():
    """Función principal con menú mejorado"""
    try:
        controller = VoiceController()
        controller.ejecutar_menu()
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
