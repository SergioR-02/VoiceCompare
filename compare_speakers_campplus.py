#!/usr/bin/env python3
"""
Script para comparar audios usando CAM++ (MEJOR MODELO)
"""

import os
import sys
import torch
import torchaudio
import numpy as np
from pathlib import Path

# Agregar rutas del proyecto
sys.path.append(os.path.join(os.path.dirname(__file__), 'speakerlab'))

from speakerlab.process.processor import FBank
from speakerlab.utils.builder import dynamic_import

def load_audio(wav_file, target_fs=16000):
    """Cargar y procesar archivo de audio"""
    wav, fs = torchaudio.load(wav_file)
    
    if fs != target_fs:
        print(f'[INFO]: Resampling {wav_file} from {fs} to {target_fs} Hz')
        wav = torchaudio.functional.resample(wav, fs, target_fs)
    
    if wav.shape[0] > 1:
        wav = wav[0, :].unsqueeze(0)
    
    return wav

def extract_embedding(wav_file, model, feature_extractor, device):
    """Extraer embedding de un archivo de audio"""
    wav = load_audio(wav_file)
    feat = feature_extractor(wav).unsqueeze(0).to(device)
    
    with torch.no_grad():
        embedding = model(feat).detach().squeeze(0).cpu().numpy()
    
    return embedding

def cosine_similarity(emb1, emb2):
    """Calcular similitud coseno entre dos embeddings"""
    emb1_norm = emb1 / np.linalg.norm(emb1)
    emb2_norm = emb2 / np.linalg.norm(emb2)
    similarity = np.dot(emb1_norm, emb2_norm)
    return similarity

def main():
    if len(sys.argv) != 3:
        print("Uso: python compare_speakers_campplus.py audio1.wav audio2.wav")
        print("\nEjemplos:")
        print('  python compare_speakers_campplus.py "audio1.wav" "audio2.wav"')
        print('  python compare_speakers_campplus.py data/daniel_2/audio_01.wav data/hablante_1/hablante_1_01.wav')
        sys.exit(1)
    
    audio1_path = sys.argv[1]
    audio2_path = sys.argv[2]
    
    # Verificar archivos
    for audio_path in [audio1_path, audio2_path]:
        if not os.path.exists(audio_path):
            print(f"❌ Error: No se encuentra el archivo {audio_path}")
            sys.exit(1)
    
    print("🎤 COMPARADOR DE LOCUTORES 3D-SPEAKER (CAM++) 🎤")
    print("=" * 55)
    print(f"📁 Audio 1: {audio1_path}")
    print(f"📁 Audio 2: {audio2_path}")
    print("=" * 55)
    
    # Verificar que CAM++ esté disponible
    campplus_path = Path("speakerlab/models/campplus/DTDNN.py")
    if not campplus_path.exists():
        print("❌ CAM++ no encontrado.")
        print("   Ejecuta primero: python download_campplus.py")
        sys.exit(1)
    
    # Configurar dispositivo
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"🖥️  Dispositivo: {device}")
    
    # Configurar extractor de características
    feature_extractor = FBank(80, sample_rate=16000, mean_nor=True)
    
    # Configurar modelo CAM++
    model_config = {
        'obj': 'speakerlab.models.campplus.DTDNN.CAMPPlus',
        'args': {
            'feat_dim': 80,
            'embedding_size': 192,  # Tamaño correcto para el modelo preentrenado
        },
    }
    
    print("🤖 Cargando modelo CAM++...")
    try:
        model_class = dynamic_import(model_config['obj'])
        model = model_class(**model_config['args'])
        print("✅ Modelo CAM++ creado exitosamente")
    except Exception as e:
        print(f"❌ Error cargando CAM++: {e}")
        print("   Verifica que download_campplus.py se haya ejecutado correctamente")
        sys.exit(1)
    
    # Intentar cargar pesos preentrenados
    model_paths = [
        "pretrained/speech_campplus_sv_zh-cn_16k-common/campplus_cn_common.bin",
        "pretrained/speech_campplus_sv_zh-cn_16k-common/pytorch_model.bin",
        "pretrained/campplus_model.ckpt",
        "campplus_model.ckpt"
    ]
    
    use_pretrained = False
    for model_path in model_paths:
        if os.path.exists(model_path):
            try:
                print(f"📦 Cargando pesos preentrenados desde {model_path}...")
                checkpoint = torch.load(model_path, map_location='cpu', weights_only=True)
                
                # Intentar diferentes formas de cargar el checkpoint
                if isinstance(checkpoint, dict):
                    if 'model' in checkpoint:
                        model.load_state_dict(checkpoint['model'], strict=False)
                    elif 'state_dict' in checkpoint:
                        model.load_state_dict(checkpoint['state_dict'], strict=False)
                    else:
                        model.load_state_dict(checkpoint, strict=False)
                else:
                    model.load_state_dict(checkpoint, strict=False)
                
                use_pretrained = True
                print("✅ Modelo CAM++ preentrenado cargado exitosamente")
                break
                
            except Exception as e:
                print(f"⚠️  Error cargando pesos desde {model_path}: {e}")
                continue
    
    if not use_pretrained:
        print("⚠️  No se encontraron pesos preentrenados para CAM++")
        print("   Los resultados no serán confiables")
        print("   Descarga el modelo con: python speakerlab/bin/infer_sv.py --model_id iic/speech_campplus_sv_zh-cn_16k-common --wavs data/daniel_2/audio_01.wav")
    
    model.to(device)
    model.eval()
    
    print("\n🔄 Procesando archivos de audio...")
    
    try:
        # Extraer embeddings
        print("  🎵 Extrayendo embedding del primer audio...")
        embedding1 = extract_embedding(audio1_path, model, feature_extractor, device)
        print(f"  ✅ Embedding 1: {embedding1.shape}")
        
        print("  🎵 Extrayendo embedding del segundo audio...")
        embedding2 = extract_embedding(audio2_path, model, feature_extractor, device)
        print(f"  ✅ Embedding 2: {embedding2.shape}")
        
        # Calcular similitud
        similarity = cosine_similarity(embedding1, embedding2)
        
        print(f"\n📊 RESULTADOS FINALES")
        print(f"=" * 40)
        print(f"🎯 Similitud coseno: {similarity:.4f}")
        
        # Interpretación específica para CAM++
        if use_pretrained:
            if similarity > 0.75:
                status = "🟢 MISMO LOCUTOR"
                confidence = "MUY ALTA CONFIANZA"
                interpretation = "Es muy probable que sean el mismo locutor"
            elif similarity > 0.65:
                status = "🟢 PROBABLEMENTE MISMO LOCUTOR"
                confidence = "ALTA CONFIANZA"
                interpretation = "Es probable que sean el mismo locutor"
            elif similarity > 0.50:
                status = "🟡 POSIBLEMENTE MISMO LOCUTOR"  
                confidence = "MEDIA CONFIANZA"
                interpretation = "Podría ser el mismo locutor, revisar manualmente"
            elif similarity > 0.35:
                status = "🟠 PROBABLEMENTE DIFERENTES"
                confidence = "BAJA SIMILITUD"
                interpretation = "Probablemente son locutores diferentes"
            else:
                status = "🔴 LOCUTORES DIFERENTES"
                confidence = "MUY BAJA SIMILITUD"
                interpretation = "Es muy probable que sean locutores diferentes"
        else:
            status = "⚠️  RESULTADO NO CONFIABLE"
            confidence = "MODELO SIN ENTRENAR"
            interpretation = "Necesitas pesos preentrenados para resultados válidos"
        
        print(f"🎯 Resultado: {status}")
        print(f"📈 Confianza: {confidence}")
        print(f"📝 Interpretación: {interpretation}")
        
        print(f"\n🔧 Detalles técnicos:")
        print(f"   • Modelo: CAM++")
        print(f"   • Embedding: {embedding1.shape[0]} dimensiones")
        print(f"   • Preentrenado: {'✅ Sí' if use_pretrained else '❌ No'}")
        print(f"   • Dispositivo: {device}")
        
        if not use_pretrained:
            print(f"\n💡 Para obtener resultados confiables:")
            print(f"   1. Ejecuta: python speakerlab/bin/infer_sv.py --model_id iic/speech_campplus_sv_zh-cn_16k-common --wavs data/daniel_2/audio_01.wav")
            print(f"   2. Esto descargará el modelo preentrenado automáticamente")
        
    except Exception as e:
        print(f"❌ Error procesando archivos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
