#!/usr/bin/env python3
"""
Launcher para el Sistema de Control por Voz
Permite elegir entre interfaz de línea de comandos o interfaz gráfica
"""

import sys
import os

def show_launcher_menu():
    """Mostrar menú de selección de interfaz"""
    print("\n" + "="*60)
    print("🎤 SISTEMA DE CONTROL POR VOZ")
    print("="*60)
    print("Selecciona el tipo de interfaz:")
    print()
    print("1. 📱 Interfaz Gráfica (Recomendado)")
    print("   - Diseño moderno y fácil de usar")
    print("   - Controles visuales intuitivos")
    print("   - Log en tiempo real con colores")
    print("   - Ventanas de configuración y ayuda")
    print()
    print("2. 💻 Interfaz de Línea de Comandos")
    print("   - Menú basado en texto")
    print("   - Ideal para usuarios avanzados")
    print("   - Menor uso de recursos")
    print("   - Compatible con terminals remotos")
    print()
    print("0. 🚪 Salir")
    print("="*60)

def launch_gui():
    """Lanzar interfaz gráfica"""
    try:
        print("🚀 Iniciando interfaz gráfica...")
        from voice_control_gui import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"❌ Error importando interfaz gráfica: {e}")
        print("💡 Asegúrate de tener tkinter instalado")
        print("   En Ubuntu/Debian: sudo apt-get install python3-tk")
        print("   En Windows: tkinter viene incluido con Python")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando interfaz gráfica: {e}")
        return False
    return True

def launch_cli():
    """Lanzar interfaz de línea de comandos"""
    try:
        print("🚀 Iniciando interfaz de línea de comandos...")
        from voice_control import main as cli_main
        cli_main()
    except ImportError as e:
        print(f"❌ Error importando interfaz CLI: {e}")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando interfaz CLI: {e}")
        return False
    return True

def check_dependencies():
    """Verificar dependencias básicas"""
    print("🔍 Verificando dependencias...")
    
    dependencies = {
        'speech_recognition': 'Reconocimiento de voz',
        'pyautogui': 'Automatización de aplicaciones',
        'torch': 'Framework de machine learning',
        'torchaudio': 'Procesamiento de audio'
    }
    
    missing = []
    for dep, desc in dependencies.items():
        try:
            __import__(dep)
            print(f"✅ {desc}")
        except ImportError:
            print(f"❌ {desc} (faltante: {dep})")
            missing.append(dep)
    
    if missing:
        print(f"\n⚠️  Dependencias faltantes: {', '.join(missing)}")
        print("💡 Instalar con: pip install -r requirements.txt")
        return False
    
    print("✅ Todas las dependencias están disponibles")
    return True

def main():
    """Función principal del launcher"""
    try:
        print("🎤 Iniciando Sistema de Control por Voz...")
        
        # Verificar dependencias
        if not check_dependencies():
            print("\n❌ No se pueden iniciar las interfaces sin las dependencias necesarias")
            input("Presiona Enter para salir...")
            return
        
        while True:
            show_launcher_menu()
            
            try:
                choice = input("\nSelecciona una opción (0-2): ").strip()
                
                if choice == "0":
                    print("👋 ¡Hasta luego!")
                    break
                
                elif choice == "1":
                    print()
                    if launch_gui():
                        break  # La GUI se encarga del resto
                    else:
                        print("\n❌ No se pudo iniciar la interfaz gráfica")
                        fallback = input("¿Quieres usar la interfaz de línea de comandos? (s/n): ").strip().lower()
                        if fallback in ['s', 'si', 'sí', 'y', 'yes']:
                            print()
                            if launch_cli():
                                break
                        input("Presiona Enter para continuar...")
                
                elif choice == "2":
                    print()
                    if launch_cli():
                        break  # La CLI se encarga del resto
                    else:
                        print("\n❌ No se pudo iniciar la interfaz de línea de comandos")
                        input("Presiona Enter para continuar...")
                
                else:
                    print("❌ Opción no válida")
                    input("Presiona Enter para continuar...")
            
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("Presiona Enter para continuar...")
    
    except Exception as e:
        print(f"❌ Error fatal en launcher: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
