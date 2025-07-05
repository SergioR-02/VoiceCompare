#!/usr/bin/env python3
"""
Script para hacer comparaciones múltiples de archivos de audio
"""

import sys
import os
from pathlib import Path
import subprocess
import re

def get_audio_files(directory):
    """Obtiene todos los archivos de audio en un directorio"""
    audio_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg']
    audio_files = []
    
    for ext in audio_extensions:
        audio_files.extend(Path(directory).glob(f'**/*{ext}'))
    
    return sorted(audio_files)

def extract_score_from_output(output):
    """Extrae el score de similitud de la salida del comando"""
    lines = output.split('\n')
    for line in lines:
        if "The similarity score" in line:
            match = re.search(r'(\d+\.\d+)', line)
            if match:
                return float(match.group(1))
    return None

def compare_audio_files(file1, file2, model_id="iic/speech_eres2net_base_sv_zh-cn_3dspeaker_16k"):
    """Compara dos archivos de audio"""
    script_path = Path(__file__).parent / "speakerlab" / "bin" / "infer_sv.py"
    
    cmd = [
        sys.executable,
        str(script_path),
        "--model_id", model_id,
        "--wavs", str(file1), str(file2)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        return extract_score_from_output(result.stdout)
    except Exception as e:
        print(f"❌ Error comparando {file1} vs {file2}: {e}")
        return None

def main():
    """Función principal"""
    print("🎵 Comparador Múltiple de Audio 3D-Speaker")
    print("=" * 60)
    
    base_dir = Path("data")
    
    # Obtener archivos por directorio
    daniel_files = get_audio_files("data/daniel_2")
    hablante1_files = get_audio_files("data/hablante_1")
    
    print(f"📁 Archivos encontrados:")
    print(f"   Daniel: {len(daniel_files)} archivos")
    print(f"   Hablante_1: {len(hablante1_files)} archivos")
    
    comparisons = []
    
    # Comparaciones dentro del mismo hablante (Daniel)
    if len(daniel_files) >= 2:
        print(f"\n🔍 Comparando archivos de Daniel entre sí:")
        for i in range(min(3, len(daniel_files))):  # Limitar a 3 comparaciones
            for j in range(i+1, min(i+2, len(daniel_files))):
                file1 = daniel_files[i]
                file2 = daniel_files[j]
                print(f"   ⏳ {file1.name} vs {file2.name}")
                score = compare_audio_files(file1, file2)
                if score is not None:
                    comparisons.append({
                        'file1': file1.name,
                        'file2': file2.name,
                        'score': score,
                        'type': 'Mismo hablante (Daniel)'
                    })
    
    # Comparaciones dentro del mismo hablante (Hablante_1)
    if len(hablante1_files) >= 2:
        print(f"\n🔍 Comparando archivos de Hablante_1 entre sí:")
        for i in range(min(3, len(hablante1_files))):  # Limitar a 3 comparaciones
            for j in range(i+1, min(i+2, len(hablante1_files))):
                file1 = hablante1_files[i]
                file2 = hablante1_files[j]
                print(f"   ⏳ {file1.name} vs {file2.name}")
                score = compare_audio_files(file1, file2)
                if score is not None:
                    comparisons.append({
                        'file1': file1.name,
                        'file2': file2.name,
                        'score': score,
                        'type': 'Mismo hablante (Hablante_1)'
                    })
    
    # Comparaciones entre hablantes diferentes
    if daniel_files and hablante1_files:
        print(f"\n🔍 Comparando entre hablantes diferentes:")
        for i in range(min(3, len(daniel_files))):  # Limitar a 3 comparaciones
            for j in range(min(2, len(hablante1_files))):
                file1 = daniel_files[i]
                file2 = hablante1_files[j]
                print(f"   ⏳ {file1.name} vs {file2.name}")
                score = compare_audio_files(file1, file2)
                if score is not None:
                    comparisons.append({
                        'file1': file1.name,
                        'file2': file2.name,
                        'score': score,
                        'type': 'Hablantes diferentes'
                    })
    
    # Mostrar resumen
    if comparisons:
        print(f"\n📊 RESUMEN DE COMPARACIONES:")
        print(f"=" * 60)
        
        # Agrupar por tipo
        same_daniel = [c for c in comparisons if 'Daniel' in c['type']]
        same_hablante1 = [c for c in comparisons if 'Hablante_1' in c['type']]
        different = [c for c in comparisons if 'diferentes' in c['type']]
        
        for category, comps in [
            ("🔹 Mismo hablante (Daniel)", same_daniel),
            ("🔹 Mismo hablante (Hablante_1)", same_hablante1), 
            ("🔹 Hablantes diferentes", different)
        ]:
            if comps:
                print(f"\n{category}:")
                scores = [c['score'] for c in comps]
                avg_score = sum(scores) / len(scores)
                print(f"   📈 Score promedio: {avg_score:.4f}")
                print(f"   📊 Scores: {[f'{s:.3f}' for s in scores]}")
                
                for comp in comps:
                    interpretation = ""
                    if comp['score'] > 0.7:
                        interpretation = "✅ MISMO HABLANTE"
                    elif comp['score'] > 0.5:
                        interpretation = "⚠️ PROBABLEMENTE MISMO"
                    elif comp['score'] > 0.3:
                        interpretation = "❓ POSIBLEMENTE MISMO"
                    else:
                        interpretation = "❌ DIFERENTES"
                    
                    print(f"   • {comp['file1']} vs {comp['file2']}: {comp['score']:.4f} {interpretation}")
        
        # Estadísticas generales
        all_scores = [c['score'] for c in comparisons]
        print(f"\n📈 ESTADÍSTICAS GENERALES:")
        print(f"   • Total comparaciones: {len(comparisons)}")
        print(f"   • Score promedio: {sum(all_scores)/len(all_scores):.4f}")
        print(f"   • Score máximo: {max(all_scores):.4f}")
        print(f"   • Score mínimo: {min(all_scores):.4f}")
        
    else:
        print(f"\n❌ No se pudieron realizar comparaciones")

if __name__ == "__main__":
    main()
