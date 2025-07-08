#!/usr/bin/env python3
"""
Script para limpiar archivos innecesarios del proyecto 3D-Speaker
Mantiene solo lo necesario para audio_comparator_menu.py y compare_multiple.py
"""

import os
import shutil
from pathlib import Path

def clean_project():
    """Eliminar archivos innecesarios"""
    
    # Archivos de scripts redundantes
    scripts_to_remove = [
        "compare_audio.py",
        "compare_speakers_advanced.py", 
        "compare_speakers_campplus.py",
        "compare_speakers_final.py",
        "compare_speakers_fixed.py",
        "compare_speakers_simple.py",
        "test_audio_files.py",
        "test_quick.py"
    ]
    
    # Scripts de entrenamiento en speakerlab/bin/
    training_scripts = [
        "speakerlab/bin/train_asd.py",
        "speakerlab/bin/train_para.py", 
        "speakerlab/bin/train_rdino.py",
        "speakerlab/bin/train_sdpn.py",
        "speakerlab/bin/extract_ssl.py",
        "speakerlab/bin/infer_diarization.py",
        "speakerlab/bin/infer_sv_ssl.py",
        "speakerlab/bin/infer_sv_batch.py",
        "speakerlab/bin/export_speaker_embedding_onnx.py"
    ]
    
    # Carpetas de modelos no utilizados
    model_dirs_to_remove = [
        "speakerlab/models/rdino",
        "speakerlab/models/sdpn", 
        "speakerlab/models/talknet",
        "speakerlab/models/xvector"
    ]
    
    # Utilidades no utilizadas
    utils_to_remove = [
        "speakerlab/utils/checkpoint.py",
        "speakerlab/utils/epoch.py",
        "speakerlab/utils/score_metrics.py", 
        "speakerlab/utils/utils_rdino.py",
        "speakerlab/process/augmentation.py",
        "speakerlab/process/cluster.py",
        "speakerlab/process/processor_para.py",
        "speakerlab/process/scheduler.py"
    ]
    
    # Carpetas completas a eliminar
    dirs_to_remove = [
        "speakerlab/loss"
    ]
    
    # Archivos de desarrollo
    dev_files = [
        ".pre-commit-config.yaml",
        ".gitignore"
    ]
    
    print("🧹 LIMPIANDO PROYECTO 3D-SPEAKER")
    print("=" * 50)
    
    total_removed = 0
    total_size_saved = 0
    
    # Eliminar scripts redundantes
    print("📄 Eliminando scripts redundantes...")
    for script in scripts_to_remove:
        if os.path.exists(script):
            size = os.path.getsize(script)
            os.remove(script)
            print(f"   ❌ {script} ({size/1024:.1f} KB)")
            total_removed += 1
            total_size_saved += size
    
    # Eliminar scripts de entrenamiento
    print("🏋️ Eliminando scripts de entrenamiento...")
    for script in training_scripts:
        if os.path.exists(script):
            size = os.path.getsize(script)
            os.remove(script)
            print(f"   ❌ {script} ({size/1024:.1f} KB)")
            total_removed += 1
            total_size_saved += size
    
    # Eliminar carpetas de modelos no utilizados
    print("🤖 Eliminando modelos no utilizados...")
    for model_dir in model_dirs_to_remove:
        if os.path.exists(model_dir):
            # Calcular tamaño de la carpeta
            dir_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                          for dirpath, dirnames, filenames in os.walk(model_dir)
                          for filename in filenames)
            
            shutil.rmtree(model_dir)
            print(f"   ❌ {model_dir}/ ({dir_size/1024/1024:.1f} MB)")
            total_removed += 1
            total_size_saved += dir_size
    
    # Eliminar utilidades no utilizadas
    print("🔧 Eliminando utilidades no utilizadas...")
    for util in utils_to_remove:
        if os.path.exists(util):
            size = os.path.getsize(util)
            os.remove(util)
            print(f"   ❌ {util} ({size/1024:.1f} KB)")
            total_removed += 1
            total_size_saved += size
    
    # Eliminar carpetas completas
    print("📁 Eliminando carpetas innecesarias...")
    for dir_path in dirs_to_remove:
        if os.path.exists(dir_path):
            # Calcular tamaño de la carpeta
            dir_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                          for dirpath, dirnames, filenames in os.walk(dir_path)
                          for filename in filenames)
            
            shutil.rmtree(dir_path)
            print(f"   ❌ {dir_path}/ ({dir_size/1024:.1f} KB)")
            total_removed += 1
            total_size_saved += dir_size
    
    # Eliminar archivos de desarrollo
    print("⚙️ Eliminando archivos de desarrollo...")
    for dev_file in dev_files:
        if os.path.exists(dev_file):
            size = os.path.getsize(dev_file)
            os.remove(dev_file)
            print(f"   ❌ {dev_file} ({size/1024:.1f} KB)")
            total_removed += 1
            total_size_saved += size
    
    # Limpiar carpetas __pycache__
    print("🗂️ Limpiando archivos cache...")
    cache_removed = 0
    for root, dirs, files in os.walk("speakerlab"):
        for dir_name in dirs[:]:  # Usar slice para modificar la lista mientras iteramos
            if dir_name == "__pycache__":
                cache_path = os.path.join(root, dir_name)
                # Calcular tamaño
                cache_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                              for dirpath, dirnames, filenames in os.walk(cache_path)
                              for filename in filenames)
                
                shutil.rmtree(cache_path)
                print(f"   ❌ {cache_path} ({cache_size/1024:.1f} KB)")
                cache_removed += 1
                total_size_saved += cache_size
                dirs.remove(dir_name)  # Evitar que os.walk entre en la carpeta eliminada
    
    print("\n" + "=" * 50)
    print("✅ LIMPIEZA COMPLETADA")
    print("=" * 50)
    print(f"📊 Archivos/carpetas eliminados: {total_removed + cache_removed}")
    print(f"💾 Espacio liberado: {total_size_saved/1024/1024:.1f} MB")
    
    print("\n✅ ARCHIVOS MANTENIDOS (esenciales):")
    print("   🎤 audio_comparator_menu.py")
    print("   🔄 compare_multiple.py")
    print("   📁 speakerlab/bin/infer_sv.py")
    print("   🤖 speakerlab/models/campplus/")
    print("   🤖 speakerlab/models/eres2net/")
    print("   🔧 speakerlab/process/processor.py")
    print("   🔧 speakerlab/utils/ (archivos esenciales)")
    print("   📊 data/ (archivos de audio)")
    print("   🏋️ pretrained/ (modelos preentrenados)")
    print("   📄 requirements.txt")
    print("   📚 README*.md")
    
    print("\n🎯 EL PROYECTO AHORA ESTÁ OPTIMIZADO PARA:")
    print("   • Comparación de audios con menú interactivo")
    print("   • Comparaciones múltiples por lotes")
    print("   • Modelos CAM++ y ERes2Net")
    print("   • Funcionalidad completa sin archivos innecesarios")

if __name__ == "__main__":
    print("⚠️  ADVERTENCIA: Este script eliminará archivos permanentemente")
    print("   Solo mantiene lo necesario para audio_comparator_menu.py y compare_multiple.py")
    
    confirm = input("\n¿Continuar con la limpieza? (escribe 'SI' para confirmar): ")
    
    if confirm == "SI":
        clean_project()
    else:
        print("❌ Operación cancelada")
