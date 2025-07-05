#!/usr/bin/env python3
"""
Script simple para comparar dos archivos de audio usando 3D-Speaker
Uso: python compare_audio.py archivo1.wav archivo2.wav
"""

import sys
import subprocess
import os
from pathlib import Path

def compare_audio_files(file1, file2, model_id="iic/speech_eres2net_base_sv_zh-cn_3dspeaker_16k"):
    """
    Compara dos archivos de audio usando el modelo 3D-Speaker
    
    Args:
        file1: Ruta del primer archivo de audio
        file2: Ruta del segundo archivo de audio
        model_id: ID del modelo a usar
    
    Returns:
        Score de similitud (float)
    """
    
    # Verificar que los archivos existen
    if not os.path.exists(file1):
        print(f"❌ Error: El archivo {file1} no existe.")
        return None
    
    if not os.path.exists(file2):
        print(f"❌ Error: El archivo {file2} no existe.")
        return None
    
    # Construir comando
    script_path = Path(__file__).parent / "speakerlab" / "bin" / "infer_sv.py"
    
    cmd = [
        sys.executable,
        str(script_path),
        "--model_id", model_id,
        "--wavs", file1, file2
    ]
    
    print(f"🔊 Comparando archivos de audio:")
    print(f"   📁 Archivo 1: {file1}")
    print(f"   📁 Archivo 2: {file2}")
    print(f"   🤖 Modelo: {model_id}")
    print(f"   ⏳ Procesando...")
    
    try:
        # Ejecutar comando
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        # Buscar el score en la salida
        lines = result.stdout.split('\n')
        score = None
        
        for line in lines:
            if "The similarity score" in line:
                # Extraer el score
                import re
                match = re.search(r'(\d+\.\d+)', line)
                if match:
                    score = float(match.group(1))
                    break
        
        if score is not None:
            print(f"\n📊 RESULTADO:")
            print(f"   🎯 Score de similitud: {score:.4f}")
            
            # Interpretación
            if score > 0.7:
                print(f"   ✅ Interpretación: MISMO HABLANTE (alta similitud)")
            elif score > 0.5:
                print(f"   ⚠️  Interpretación: PROBABLEMENTE MISMO HABLANTE (similitud moderada-alta)")
            elif score > 0.3:
                print(f"   ❓ Interpretación: POSIBLEMENTE MISMO HABLANTE (similitud moderada)")
            else:
                print(f"   ❌ Interpretación: HABLANTES DIFERENTES (baja similitud)")
                
            return score
        else:
            print(f"❌ Error: No se pudo extraer el score de similitud")
            print(f"Salida completa:\n{result.stdout}")
            if result.stderr:
                print(f"Errores:\n{result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error ejecutando la comparación: {e}")
        return None

def main():
    """Función principal"""
    if len(sys.argv) != 3:
        print("📝 Uso: python compare_audio.py archivo1.wav archivo2.wav")
        print("\n🔍 Ejemplos:")
        print("   python compare_audio.py data/daniel_2/audio_01.wav data/daniel_2/record_out.wav")
        print("   python compare_audio.py data/daniel_2/audio_01.wav data/hablante_1/hablante_1_01.wav")
        sys.exit(1)
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    
    print("🎵 Comparador de Audio 3D-Speaker")
    print("=" * 50)
    
    score = compare_audio_files(file1, file2)
    
    if score is not None:
        print(f"\n✅ Comparación completada exitosamente")
    else:
        print(f"\n❌ Error en la comparación")
        sys.exit(1)

if __name__ == "__main__":
    main()
