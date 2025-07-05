#!/usr/bin/env python3
"""
Script simple para comparar dos audios usando 3D-Speaker sin ModelScope
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
    
    # Resample si es necesario
    if fs != target_fs:
        print(f'[WARNING]: Resampling {wav_file} from {fs} to {target_fs} Hz')
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
        print("Uso: python compare_speakers_simple.py audio1.wav audio2.wav")
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
    
    print(f"Comparando:")
    print(f"  Audio 1: {audio1_path}")
    print(f"  Audio 2: {audio2_path}")
    
    # Configurar dispositivo
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Usando dispositivo: {device}")
    
    # Configurar extractor de características
    feature_extractor = FBank(80, sample_rate=16000, mean_nor=True)
    
    # Cargar modelo CAM++ (modelo más simple y rápido)
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
    
    # Inicializar modelo con pesos aleatorios (para prueba)
    # En producción necesitarías cargar pesos preentrenados
    model.to(device)
    model.eval()
    
    print("Extrayendo embeddings...")
    
    # Extraer embeddings
    try:
        embedding1 = extract_embedding(audio1_path, model, feature_extractor, device)
        print(f"  Embedding 1 extraído: shape {embedding1.shape}")
        
        embedding2 = extract_embedding(audio2_path, model, feature_extractor, device)
        print(f"  Embedding 2 extraído: shape {embedding2.shape}")
        
        # Calcular similitud
        similarity = cosine_similarity(embedding1, embedding2)
        
        print(f"\n--- RESULTADOS ---")
        print(f"Similitud coseno: {similarity:.4f}")
        
        if similarity > 0.7:
            print("🟢 ALTA probabilidad de ser el mismo locutor")
        elif similarity > 0.5:
            print("🟡 MEDIA probabilidad de ser el mismo locutor")
        else:
            print("🔴 BAJA probabilidad de ser el mismo locutor")
        
        print(f"\nNota: Este modelo usa pesos aleatorios.")
        print(f"Para resultados reales, necesitas pesos preentrenados.")
        
    except Exception as e:
        print(f"Error procesando archivos: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
