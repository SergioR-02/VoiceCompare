#!/usr/bin/env python3
"""
Script mejorado para comparar audios usando modelos preentrenados
"""

import os
import sys
import torch
import torchaudio
import numpy as np
import requests
from pathlib import Path

# Agregar rutas del proyecto
sys.path.append(os.path.join(os.path.dirname(__file__), 'speakerlab'))

from speakerlab.process.processor import FBank
from speakerlab.utils.builder import dynamic_import

def download_pretrained_model():
    """Descargar modelo preentrenado directamente desde Hugging Face"""
    model_url = "https://huggingface.co/iic/speech_campplus_sv_zh-cn_16k-common/resolve/main/pytorch_model.bin"
    model_path = "pretrained_model.bin"
    
    if not os.path.exists(model_path):
        print("Descargando modelo preentrenado...")
        try:
            response = requests.get(model_url, stream=True)
            response.raise_for_status()
            
            with open(model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("Modelo descargado exitosamente")
        except Exception as e:
            print(f"Error descargando modelo: {e}")
            return None
    
    return model_path

def load_audio(wav_file, target_fs=16000):
    """Cargar y procesar archivo de audio"""
    wav, fs = torchaudio.load(wav_file)
    
    # Resample si es necesario
    if fs != target_fs:
        print(f'[INFO]: Resampling {wav_file} from {fs} to {target_fs} Hz')
        wav = torchaudio.functional.resample(wav, fs, target_fs)
    
    # Convertir a mono si es estéreo
    if wav.shape[0] > 1:
        wav = wav[0, :].unsqueeze(0)
    
    return wav

def extract_embedding(wav_file, model, feature_extractor, device):
    """Extraer embedding de un archivo de audio"""
    # Cargar audio
    wav = load_audio(wav_file)
    
    # Extraer características
    feat = feature_extractor(wav).unsqueeze(0).to(device)
    
    # Extraer embedding
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
    # Verificar argumentos
    if len(sys.argv) != 3:
        print("Uso: python compare_speakers_advanced.py audio1.wav audio2.wav")
        sys.exit(1)
    
    audio1_path = sys.argv[1]
    audio2_path = sys.argv[2]
    
    # Verificar que los archivos existen
    if not os.path.exists(audio1_path):
        print(f"Error: No se encuentra el archivo {audio1_path}")
        sys.exit(1)
    
    if not os.path.exists(audio2_path):
        print(f"Error: No se encuentra el archivo {audio2_path}")
        sys.exit(1)
    
    print(f"🎤 COMPARADOR DE LOCUTORES 3D-SPEAKER 🎤")
    print(f"=" * 50)
    print(f"Audio 1: {audio1_path}")
    print(f"Audio 2: {audio2_path}")
    print(f"=" * 50)
    
    # Configurar dispositivo
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Dispositivo: {device}")
    
    # Configurar extractor de características
    feature_extractor = FBank(80, sample_rate=16000, mean_nor=True)
    
    # Configurar modelo CAM++
    model_config = {
        'obj': 'speakerlab.models.campplus.DTDNN.CAMPPlus',
        'args': {
            'feat_dim': 80,
            'embedding_size': 192,
        },
    }
    
    print("Cargando modelo CAM++...")
    model_class = dynamic_import(model_config['obj'])
    model = model_class(**model_config['args'])
    
    # Intentar descargar y cargar pesos preentrenados
    model_path = download_pretrained_model()
    use_pretrained = False
    
    if model_path and os.path.exists(model_path):
        try:
            print("Cargando pesos preentrenados...")
            state_dict = torch.load(model_path, map_location='cpu', weights_only=True)
            model.load_state_dict(state_dict, strict=False)
            use_pretrained = True
            print("✅ Pesos preentrenados cargados exitosamente")
        except Exception as e:
            print(f"⚠️  Error cargando pesos preentrenados: {e}")
            print("Usando modelo con pesos aleatorios...")
    else:
        print("⚠️  Usando modelo con pesos aleatorios (solo para prueba)")
    
    model.to(device)
    model.eval()
    
    print("\n🔄 Extrayendo embeddings...")
    
    # Extraer embeddings
    try:
        embedding1 = extract_embedding(audio1_path, model, feature_extractor, device)
        print(f"  ✅ Embedding 1: {embedding1.shape}")
        
        embedding2 = extract_embedding(audio2_path, model, feature_extractor, device)
        print(f"  ✅ Embedding 2: {embedding2.shape}")
        
        # Calcular similitud
        similarity = cosine_similarity(embedding1, embedding2)
        
        print(f"\n📊 RESULTADOS")
        print(f"=" * 30)
        print(f"Similitud coseno: {similarity:.4f}")
        
        # Interpretación de resultados
        if use_pretrained:
            # Thresholds para modelo preentrenado
            if similarity > 0.8:
                status = "🟢 MUY ALTA"
                interpretation = "Casi certeza de que es el mismo locutor"
            elif similarity > 0.7:
                status = "🟢 ALTA"
                interpretation = "Muy probable que sea el mismo locutor"
            elif similarity > 0.5:
                status = "🟡 MEDIA"
                interpretation = "Posiblemente el mismo locutor"
            elif similarity > 0.3:
                status = "🟠 BAJA"
                interpretation = "Probablemente locutores diferentes"
            else:
                status = "🔴 MUY BAJA"
                interpretation = "Casi certeza de que son locutores diferentes"
        else:
            # Para modelo con pesos aleatorios
            status = "⚠️  NO CONFIABLE"
            interpretation = "Resultados no válidos (modelo sin entrenar)"
        
        print(f"Probabilidad: {status}")
        print(f"Interpretación: {interpretation}")
        
        if not use_pretrained:
            print(f"\n⚠️  IMPORTANTE: Este resultado no es confiable")
            print(f"   El modelo no tiene pesos preentrenados.")
            print(f"   Para resultados reales, necesitas un modelo entrenado.")
        
        print(f"\n📝 Detalles técnicos:")
        print(f"   - Modelo: CAM++ (Context-Aware Masking)")
        print(f"   - Dimensión embedding: {embedding1.shape[0]}")
        print(f"   - Método: Similitud coseno")
        print(f"   - Modelo preentrenado: {'✅ Sí' if use_pretrained else '❌ No'}")
        
    except Exception as e:
        print(f"❌ Error procesando archivos: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
