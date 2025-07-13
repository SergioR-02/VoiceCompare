#!/usr/bin/env python3
"""
Menú integrado para comparar audios con diferentes modelos 3D-Speaker
"""

import os
import sys
import torch
import torchaudio
import numpy as np
from pathlib import Path
import subprocess
import re
import sounddevice as sd
import wave
import time
import threading

# Agregar rutas del proyecto
sys.path.append(os.path.join(os.path.dirname(__file__), 'speakerlab'))

from speakerlab.process.processor import FBank
from speakerlab.utils.builder import dynamic_import

class AudioComparator:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.feature_extractor = FBank(80, sample_rate=16000, mean_nor=True)
        
        # Configuraciones de modelos disponibles
        self.models_config = {
            "1": {
                "name": "CAM++ (Recomendado)",
                "description": "Más rápido y preciso para chino",
                "model_id": "iic/speech_campplus_sv_zh-cn_16k-common",
                "config": {
                    'obj': 'speakerlab.models.campplus.DTDNN.CAMPPlus',
                    'args': {
                        'feat_dim': 80,
                        'embedding_size': 192,
                    },
                },
                "model_paths": [
                    "pretrained/speech_campplus_sv_zh-cn_16k-common/campplus_cn_common.bin",
                    "pretrained/speech_campplus_sv_zh-cn_16k-common/pytorch_model.bin",
                ],
                "thresholds": [0.75, 0.65, 0.50, 0.35]
            },
            "2": {
                "name": "ERes2Net Base",
                "description": "Modelo robusto y confiable",
                "model_id": "iic/speech_eres2net_base_sv_zh-cn_3dspeaker_16k",
                "config": {
                    'obj': 'speakerlab.models.eres2net.ERes2Net.ERes2Net',
                    'args': {
                        'feat_dim': 80,
                        'embedding_size': 512,
                        'm_channels': 32,
                    },
                },
                "model_paths": [
                    "pretrained/speech_eres2net_base_sv_zh-cn_3dspeaker_16k/eres2net_base_model.ckpt",
                ],
                "thresholds": [0.70, 0.60, 0.45, 0.30]
            },
            "3": {
                "name": "Script Original (infer_sv.py)",
                "description": "Usar el script original del proyecto",
                "use_original": True
            }
        }

    def print_header(self):
        """Imprimir header del menú"""
        print("\n" + "="*60)
        print("🎤 COMPARADOR DE AUDIOS 3D-SPEAKER 🎤")
        print("="*60)
        print(f"💻 Dispositivo: {self.device}")
        total_audios = len(self.get_audio_files())
        print(f"🎵 Archivos de audio encontrados: {total_audios}")
        print("="*60)

    def get_audio_files(self):
        """Obtener todos los archivos de audio disponibles en la carpeta data"""
        audio_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg']
        audio_files = []
        
        # Buscar solo en el directorio data
        data_dir = 'data'
        
        if os.path.exists(data_dir):
            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in audio_extensions):
                        full_path = os.path.join(root, file)
                        # Filtrar archivos muy pequeños o temporales
                        if os.path.getsize(full_path) > 1000:  # Al menos 1KB
                            audio_files.append(full_path)
        
        return sorted(audio_files)

    def select_model(self):
        """Seleccionar modelo a usar"""
        print("\n📊 SELECCIONA EL MODELO:")
        print("-" * 40)
        
        for key, model in self.models_config.items():
            print(f"{key}. {model['name']}")
            print(f"   {model['description']}")
            if 'model_paths' in model:
                # Verificar si el modelo está disponible
                model_available = any(os.path.exists(path) for path in model['model_paths'])
                status = "✅ Disponible" if model_available else "❌ No encontrado"
                print(f"   {status}")
            
        print("\n4. 🔄 Comparar TODOS los audios (matriz de similitud)")
        print("5. 🎤 Grabación EN VIVO (comparar con archivos conocidos)")
        print("0. Salir")
        
        while True:
            try:
                choice = input("\nSelecciona una opción (0-5): ").strip()
                
                if choice == "0":
                    print("👋 ¡Hasta luego!")
                    sys.exit(0)
                elif choice == "4":
                    return "compare_all"
                elif choice == "5":
                    return "live_recording"
                elif choice in self.models_config:
                    return choice
                else:
                    print("❌ Opción inválida. Intenta de nuevo.")
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                sys.exit(0)

    def get_audio_info(self, audio_file):
        """Obtener información detallada del archivo de audio"""
        try:
            wav, fs = torchaudio.load(audio_file)
            duration = wav.shape[-1] / fs
            channels = wav.shape[0] if len(wav.shape) > 1 else 1
            file_size = os.path.getsize(audio_file) / 1024  # KB
            
            return {
                'duration': duration,
                'sample_rate': fs,
                'channels': channels,
                'file_size': file_size,
                'samples': wav.shape[-1]
            }
        except Exception as e:
            return None

    def select_audio_file(self, prompt_text):
        """Seleccionar archivo de audio"""
        audio_files = self.get_audio_files()
        
        if not audio_files:
            print("❌ No se encontraron archivos de audio")
            return None
        
        print(f"\n{prompt_text}")
        print("-" * 50)
        
        # Agrupar por directorio para mejor visualización
        files_by_dir = {}
        for file in audio_files:
            dir_name = os.path.dirname(file)
            if dir_name not in files_by_dir:
                files_by_dir[dir_name] = []
            files_by_dir[dir_name].append(file)
        
        file_index = 1
        index_to_file = {}
        
        for dir_name, files in files_by_dir.items():
            print(f"\n📁 {dir_name}:")
            for file in files:
                filename = os.path.basename(file)
                
                # Obtener información del audio
                audio_info = self.get_audio_info(file)
                if audio_info:
                    info_str = f"({audio_info['duration']:.1f}s, {audio_info['sample_rate']}Hz, {audio_info['file_size']:.1f}KB)"
                else:
                    info_str = f"({os.path.getsize(file) / 1024:.1f} KB)"
                
                print(f"  {file_index:2d}. {filename} {info_str}")
                index_to_file[file_index] = file
                file_index += 1
        
        print("\n  0. Volver al menú principal")
        print("  i. Mostrar información detallada de un archivo")
        
        while True:
            try:
                choice = input(f"\nSelecciona un archivo (1-{len(audio_files)}, i para info): ")
                
                if choice == "0":
                    return None
                elif choice.lower() == "i":
                    info_choice = input("Número del archivo para ver información: ")
                    try:
                        info_index = int(info_choice)
                        if info_index in index_to_file:
                            self.show_audio_info(index_to_file[info_index])
                        else:
                            print(f"❌ Número inválido")
                    except ValueError:
                        print("❌ Por favor, ingresa un número válido")
                    continue
                
                index = int(choice)
                if index in index_to_file:
                    return index_to_file[index]
                else:
                    print(f"❌ Por favor, ingresa un número entre 1 y {len(audio_files)}")
            except ValueError:
                print("❌ Por favor, ingresa un número válido")
            except KeyboardInterrupt:
                print("\n👋 Regresando al menú principal...")
                return None

    def show_audio_info(self, audio_file):
        """Mostrar información detallada del archivo de audio"""
        print(f"\n📄 INFORMACIÓN DEL ARCHIVO:")
        print("=" * 50)
        print(f"📁 Archivo: {os.path.basename(audio_file)}")
        print(f"📂 Ruta: {audio_file}")
        
        audio_info = self.get_audio_info(audio_file)
        if audio_info:
            print(f"⏱️  Duración: {audio_info['duration']:.2f} segundos")
            print(f"🔊 Frecuencia: {audio_info['sample_rate']} Hz")
            print(f"📻 Canales: {audio_info['channels']}")
            print(f"📊 Muestras: {audio_info['samples']:,}")
            print(f"💾 Tamaño: {audio_info['file_size']:.1f} KB")
            
            # Verificar si es adecuado para el modelo
            if audio_info['sample_rate'] != 16000:
                print(f"⚠️  Nota: El archivo será resampleado de {audio_info['sample_rate']}Hz a 16000Hz")
            
            if audio_info['duration'] < 1.0:
                print(f"⚠️  Advertencia: Archivo muy corto ({audio_info['duration']:.2f}s). Puede afectar la precisión.")
            elif audio_info['duration'] > 30.0:
                print(f"ℹ️  Información: Archivo largo ({audio_info['duration']:.2f}s). Solo se usará una porción.")
        else:
            print("❌ No se pudo leer la información del archivo")
        
        print("=" * 50)
        input("Presiona Enter para continuar...")

    def load_audio(self, wav_file, target_fs=16000):
        """Cargar y procesar archivo de audio"""
        wav, fs = torchaudio.load(wav_file)
        
        if fs != target_fs:
            print(f'[INFO]: Resampling {os.path.basename(wav_file)} from {fs} to {target_fs} Hz')
            wav = torchaudio.functional.resample(wav, fs, target_fs)
        
        if wav.shape[0] > 1:
            wav = wav[0, :].unsqueeze(0)
        
        return wav

    def extract_embedding(self, wav_file, model):
        """Extraer embedding de un archivo de audio"""
        wav = self.load_audio(wav_file)
        feat = self.feature_extractor(wav).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            embedding = model(feat).detach().squeeze(0).cpu().numpy()
        
        return embedding

    def cosine_similarity(self, emb1, emb2):
        """Calcular similitud coseno entre dos embeddings"""
        emb1_norm = emb1 / np.linalg.norm(emb1)
        emb2_norm = emb2 / np.linalg.norm(emb2)
        similarity = np.dot(emb1_norm, emb2_norm)
        return similarity

    def compare_with_original_script(self, model_choice, audio1, audio2):
        """Usar el script original infer_sv.py"""
        model_config = self.models_config[model_choice]
        script_path = Path("speakerlab") / "bin" / "infer_sv.py"
        
        cmd = [
            sys.executable,
            str(script_path),
            "--model_id", model_config["model_id"],
            "--wavs", audio1, audio2
        ]
        
        print(f"🔄 Ejecutando script original...")
        print(f"📊 Modelo: {model_config['name']}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
            
            # Buscar el score en la salida
            lines = result.stdout.split('\n')
            score = None
            
            for line in lines:
                if "The similarity score" in line:
                    match = re.search(r'(\d+\.\d+)', line)
                    if match:
                        score = float(match.group(1))
                        break
            
            if score is not None:
                print(f"\n📊 RESULTADOS:")
                print(f"🎯 Similitud coseno: {score:.4f}")
                
                # Interpretación usando thresholds del modelo
                thresholds = model_config.get("thresholds", [0.70, 0.60, 0.45, 0.30])
                self.interpret_results(score, thresholds, True)
                
                return score
            else:
                print("❌ No se pudo extraer el score de similitud")
                if result.stderr:
                    print(f"Error: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error ejecutando script original: {e}")
            return None

    def compare_with_model(self, model_choice, audio1, audio2):
        """Comparar usando modelo cargado directamente"""
        model_config = self.models_config[model_choice]
        
        print(f"🤖 Cargando modelo {model_config['name']}...")
        
        try:
            # Crear modelo
            model_class = dynamic_import(model_config['config']['obj'])
            model = model_class(**model_config['config']['args'])
            
            # Intentar cargar pesos preentrenados
            use_pretrained = False
            for model_path in model_config['model_paths']:
                if os.path.exists(model_path):
                    try:
                        print(f"📦 Cargando pesos desde {os.path.basename(model_path)}...")
                        checkpoint = torch.load(model_path, map_location='cpu', weights_only=True)
                        
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
                        print("✅ Modelo preentrenado cargado exitosamente")
                        break
                        
                    except Exception as e:
                        print(f"⚠️  Error cargando {model_path}: {e}")
                        continue
            
            if not use_pretrained:
                print("⚠️  Usando modelo sin entrenar (resultados no confiables)")
            
            model.to(self.device)
            model.eval()
            
            # Extraer embeddings
            print("🔄 Procesando audios...")
            embedding1 = self.extract_embedding(audio1, model)
            embedding2 = self.extract_embedding(audio2, model)
            
            # Calcular similitud
            similarity = self.cosine_similarity(embedding1, embedding2)
            
            print(f"\n📊 RESULTADOS:")
            print(f"🎯 Similitud coseno: {similarity:.4f}")
            print(f"📊 Embedding: {embedding1.shape[0]} dimensiones")
            
            # Interpretación
            thresholds = model_config.get("thresholds", [0.70, 0.60, 0.45, 0.30])
            self.interpret_results(similarity, thresholds, use_pretrained)
            
            return similarity
            
        except Exception as e:
            print(f"❌ Error con modelo {model_config['name']}: {e}")
            return None

    def interpret_results(self, similarity, thresholds, use_pretrained):
        """Interpretar resultados según thresholds"""
        if use_pretrained:
            if similarity > thresholds[0]:
                status = "🟢 MISMO LOCUTOR"
                confidence = "MUY ALTA CONFIANZA"
            elif similarity > thresholds[1]:
                status = "🟢 PROBABLEMENTE MISMO LOCUTOR"
                confidence = "ALTA CONFIANZA"
            elif similarity > thresholds[2]:
                status = "🟡 POSIBLEMENTE MISMO LOCUTOR"  
                confidence = "MEDIA CONFIANZA"
            elif similarity > thresholds[3]:
                status = "🟠 PROBABLEMENTE DIFERENTES"
                confidence = "BAJA SIMILITUD"
            else:
                status = "🔴 LOCUTORES DIFERENTES"
                confidence = "MUY BAJA SIMILITUD"
        else:
            status = "⚠️  RESULTADO NO CONFIABLE"
            confidence = "MODELO SIN ENTRENAR"
        
        print(f"🎯 Resultado: {status}")
        print(f"📈 Confianza: {confidence}")

    def compare_all_audios(self, model_choice):
        """Comparar todos los audios disponibles y crear matriz de similitud"""
        audio_files = self.get_audio_files()
        
        if len(audio_files) < 2:
            print("❌ Se necesitan al menos 2 archivos de audio")
            return
        
        if len(audio_files) > 10:
            print(f"⚠️  Se encontraron {len(audio_files)} archivos. Esto puede tomar mucho tiempo.")
            confirm = input("¿Continuar? (s/n): ").lower()
            if confirm not in ['s', 'si', 'sí', 'y', 'yes']:
                return
        
        model_config = self.models_config[model_choice]
        print(f"\n🔄 Comparando {len(audio_files)} archivos con {model_config['name']}...")
        
        # Cargar modelo
        try:
            model_class = dynamic_import(model_config['config']['obj'])
            model = model_class(**model_config['config']['args'])
            
            # Cargar pesos preentrenados
            use_pretrained = False
            for model_path in model_config['model_paths']:
                if os.path.exists(model_path):
                    try:
                        checkpoint = torch.load(model_path, map_location='cpu', weights_only=True)
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
                        break
                    except Exception as e:
                        continue
            
            model.to(self.device)
            model.eval()
            
            # Extraer embeddings de todos los archivos
            print("🔄 Extrayendo embeddings...")
            embeddings = {}
            file_names = []
            
            for i, audio_file in enumerate(audio_files):
                try:
                    print(f"   📄 Procesando {i+1}/{len(audio_files)}: {os.path.basename(audio_file)}")
                    embedding = self.extract_embedding(audio_file, model)
                    embeddings[audio_file] = embedding
                    file_names.append(os.path.basename(audio_file))
                except Exception as e:
                    print(f"   ❌ Error con {audio_file}: {e}")
                    continue
            
            if len(embeddings) < 2:
                print("❌ No se pudieron procesar suficientes archivos")
                return
            
            # Crear matriz de similitud
            print("\n📊 Calculando matriz de similitud...")
            similarity_matrix = np.zeros((len(embeddings), len(embeddings)))
            audio_list = list(embeddings.keys())
            
            for i, audio1 in enumerate(audio_list):
                for j, audio2 in enumerate(audio_list):
                    if i == j:
                        similarity_matrix[i, j] = 1.0
                    elif i < j:  # Solo calcular la mitad superior
                        similarity = self.cosine_similarity(embeddings[audio1], embeddings[audio2])
                        similarity_matrix[i, j] = similarity
                        similarity_matrix[j, i] = similarity  # Simetría
            
            # Mostrar resultados
            print("\n" + "="*80)
            print("📊 MATRIZ DE SIMILITUD")
            print("="*80)
            
            # Header con nombres de archivos
            header = "Archivo".ljust(20)
            for name in file_names:
                header += f"{name[:10]:<12}"
            print(header)
            print("-" * len(header))
            
            # Filas de la matriz
            for i, name in enumerate(file_names):
                row = f"{name[:18]:<20}"
                for j in range(len(file_names)):
                    score = similarity_matrix[i, j]
                    if i == j:
                        row += f"{'1.0000':<12}"
                    else:
                        row += f"{score:.4f}{'':6}"
                print(row)
            
            # Análisis de grupos
            print("\n📈 ANÁLISIS DE GRUPOS:")
            print("-" * 40)
            
            threshold = model_config.get("thresholds", [0.70, 0.60, 0.45, 0.30])[1]  # Usar segundo threshold
            high_similarity_pairs = []
            
            for i in range(len(audio_list)):
                for j in range(i+1, len(audio_list)):
                    if similarity_matrix[i, j] > threshold:
                        pair = (file_names[i], file_names[j], similarity_matrix[i, j])
                        high_similarity_pairs.append(pair)
            
            if high_similarity_pairs:
                print(f"🟢 Pares con alta similitud (> {threshold:.2f}):")
                for name1, name2, score in sorted(high_similarity_pairs, key=lambda x: x[2], reverse=True):
                    print(f"   {name1} ↔ {name2}: {score:.4f}")
            else:
                print(f"🔴 No se encontraron pares con alta similitud (> {threshold:.2f})")
            
            # Guardar resultados
            save_results = input("\n💾 ¿Guardar resultados en archivo? (s/n): ").lower()
            if save_results in ['s', 'si', 'sí', 'y', 'yes']:
                import csv
                import datetime
                
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"similarity_matrix_{model_choice}_{timestamp}.csv"
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Header
                    header_row = ['Archivo'] + file_names
                    writer.writerow(header_row)
                    
                    # Datos
                    for i, name in enumerate(file_names):
                        row = [name] + [f"{similarity_matrix[i, j]:.4f}" for j in range(len(file_names))]
                        writer.writerow(row)
                
                print(f"✅ Resultados guardados en: {filename}")
            
        except Exception as e:
            print(f"❌ Error en comparación masiva: {e}")
            import traceback
            traceback.print_exc()

    def record_audio(self, duration=5, sample_rate=16000, auto_start=False):
        """Grabar audio desde el micrófono
        
        Args:
            duration (int): Duración en segundos
            sample_rate (int): Frecuencia de muestreo
            auto_start (bool): Si True, inicia automáticamente sin esperar Enter
        """
        print(f"\n🎤 GRABACIÓN EN VIVO")
        print("=" * 50)
        print(f"⏱️  Duración: {duration} segundos")
        print(f"🔊 Frecuencia: {sample_rate} Hz")
        print("📱 Asegúrate de tener el micrófono conectado y funcionando")
        print("=" * 50)
        
        # Verificar dispositivos de audio disponibles
        try:
            devices = sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]
            
            if not input_devices:
                print("❌ No se encontraron dispositivos de entrada de audio")
                return None
            
            print(f"🎙️  Dispositivo de entrada: {sd.default.device[0] if sd.default.device[0] is not None else 'Default'}")
            
        except Exception as e:
            print(f"⚠️  Advertencia: No se pudo verificar dispositivos de audio: {e}")
        
        # Solo solicitar Enter si no es auto_start
        if not auto_start:
            input("\n🎤 Presiona Enter cuando estés listo para grabar...")
        else:
            print("\n🎤 Iniciando grabación automáticamente...")
            # Pequeña pausa para que el usuario se prepare
            time.sleep(1)
        
        print(f"\n🔴 ¡GRABANDO! Habla ahora por {duration} segundos...")
        
        # Contador visual
        def countdown():
            for i in range(duration, 0, -1):
                print(f"\r⏱️  Tiempo restante: {i} segundos", end="", flush=True)
                time.sleep(1)
            print(f"\r✅ Grabación completada!{' ' * 20}")
        
        try:
            # Iniciar contador en hilo separado
            countdown_thread = threading.Thread(target=countdown)
            countdown_thread.start()
            
            # Grabar audio
            recording = sd.rec(int(duration * sample_rate), 
                             samplerate=sample_rate, 
                             channels=1, 
                             dtype=np.float32)
            sd.wait()  # Esperar a que termine la grabación
            
            countdown_thread.join()
            
            # Verificar que la grabación no esté vacía
            if np.max(np.abs(recording)) < 0.001:
                print("⚠️  Advertencia: La grabación parece estar muy silenciosa")
                print("   Verifica que el micrófono esté funcionando correctamente")
            
            # Guardar temporalmente
            temp_filename = "temp_recording.wav"
            
            # Convertir a tensor de PyTorch para compatibilidad
            recording_tensor = torch.from_numpy(recording.T)  # Transponer para tener shape [channels, samples]
            torchaudio.save(temp_filename, recording_tensor, sample_rate)
            
            print(f"💾 Audio grabado y guardado temporalmente en: {temp_filename}")
            
            return temp_filename
            
        except Exception as e:
            print(f"❌ Error durante la grabación: {e}")
            return None

    def identify_speaker_live(self):
        """Función principal para identificación de locutor en vivo"""
        print("\n🎤 IDENTIFICACIÓN DE LOCUTOR EN VIVO")
        print("=" * 60)
        
        # Referencias conocidas (puedes modificar estos archivos según tus necesidades)
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
        
        # Verificar qué archivos de referencia existen
        available_references = {}
        for person, files in reference_files.items():
            available_files = [f for f in files if os.path.exists(f)]
            if available_files:
                available_references[person] = available_files
        
        if not available_references:
            print("❌ No se encontraron archivos de referencia")
            print("   Asegúrate de tener archivos en las carpetas:")
            for person, files in reference_files.items():
                print(f"   📁 {person}: {files[0][:20]}...")
            return
        
        print("👥 PERSONAS CONOCIDAS EN EL SISTEMA:")
        print("-" * 40)
        for person, files in available_references.items():
            print(f"👤 {person}: {len(files)} archivos de referencia")
        
        # Configurar grabación
        print(f"\n⚙️  CONFIGURACIÓN DE GRABACIÓN:")
        print("-" * 40)
        
        # Duración de grabación
        try:
            duration_input = input("⏱️  Duración de grabación en segundos (por defecto 5): ").strip()
            duration = int(duration_input) if duration_input else 5
            duration = max(2, min(duration, 30))  # Entre 2 y 30 segundos
        except ValueError:
            duration = 5
        
        # Seleccionar modelo
        print(f"\n📊 SELECCIONA EL MODELO PARA IDENTIFICACIÓN:")
        print("-" * 40)
        
        # Solo mostrar modelos que usen el script original para mayor confiabilidad
        available_models = {}
        for key, model in self.models_config.items():
            if model.get('use_original'):
                available_models[key] = model
                print(f"{key}. {model['name']} (Script Original)")
            elif 'model_paths' in model:
                model_available = any(os.path.exists(path) for path in model['model_paths'])
                if model_available:
                    available_models[key] = model
                    print(f"{key}. {model['name']} ✅")
        
        if not available_models:
            print("❌ No hay modelos disponibles")
            return
        
        model_choice = input(f"\nSelecciona modelo: ").strip()
        if model_choice not in available_models:
            print("❌ Selección inválida")
            return
        
        # Grabar audio
        recorded_file = self.record_audio(duration)
        if not recorded_file:
            return
        
        print(f"\n🔍 COMPARANDO CON PERSONAS CONOCIDAS...")
        print("=" * 60)
        
        # Comparar con cada persona
        results = {}
        
        for person, reference_files in available_references.items():
            print(f"\n👤 Comparando con {person}...")
            person_scores = []
            
            for ref_file in reference_files[:3]:  # Usar máximo 3 archivos por persona
                try:
                    print(f"   📄 Comparando con {os.path.basename(ref_file)}...")
                    
                    if self.models_config[model_choice].get('use_original'):
                        score = self.compare_with_original_script(model_choice, recorded_file, ref_file)
                    else:
                        score = self.compare_with_model(model_choice, recorded_file, ref_file)
                    
                    if score is not None:
                        person_scores.append(score)
                        print(f"     🎯 Similitud: {score:.4f}")
                    
                except Exception as e:
                    print(f"     ❌ Error: {e}")
                    continue
            
            if person_scores:
                avg_score = sum(person_scores) / len(person_scores)
                max_score = max(person_scores)
                results[person] = {
                    'avg_score': avg_score,
                    'max_score': max_score,
                    'scores': person_scores
                }
                print(f"   📊 Promedio: {avg_score:.4f}, Máximo: {max_score:.4f}")
        
        # Mostrar resultados finales
        print(f"\n🏆 RESULTADOS DE IDENTIFICACIÓN:")
        print("=" * 60)
        
        if not results:
            print("❌ No se pudieron realizar comparaciones")
            return
        
        # Ordenar por score promedio
        sorted_results = sorted(results.items(), key=lambda x: x[1]['avg_score'], reverse=True)
        
        best_match = sorted_results[0]
        best_person = best_match[0]
        best_avg_score = best_match[1]['avg_score']
        best_max_score = best_match[1]['max_score']
        
        print(f"🥇 MEJOR COINCIDENCIA: {best_person}")
        print(f"   📊 Score promedio: {best_avg_score:.4f}")
        print(f"   🎯 Score máximo: {best_max_score:.4f}")
        
        # Interpretar resultado
        model_config = self.models_config[model_choice]
        thresholds = model_config.get("thresholds", [0.70, 0.60, 0.45, 0.30])
        
        if best_avg_score > thresholds[0]:
            confidence = "🟢 MUY ALTA CONFIANZA - Es muy probable que sea esta persona"
        elif best_avg_score > thresholds[1]:
            confidence = "🟢 ALTA CONFIANZA - Probablemente es esta persona"
        elif best_avg_score > thresholds[2]:
            confidence = "🟡 CONFIANZA MEDIA - Podría ser esta persona"
        elif best_avg_score > thresholds[3]:
            confidence = "🟠 BAJA CONFIANZA - Similitud débil"
        else:
            confidence = "🔴 MUY BAJA CONFIANZA - Probablemente es una persona desconocida"
        
        print(f"   {confidence}")
        
        # Mostrar tabla completa de resultados
        print(f"\n📋 TABLA COMPLETA DE SIMILITUDES:")
        print("-" * 60)
        for person, data in sorted_results:
            print(f"👤 {person}:")
            print(f"   📊 Promedio: {data['avg_score']:.4f}")
            print(f"   🎯 Máximo: {data['max_score']:.4f}")
            print(f"   📈 Scores individuales: {[f'{s:.3f}' for s in data['scores']]}")
        
        # Limpiar archivo temporal
        try:
            os.remove(recorded_file)
            print(f"\n🗑️  Archivo temporal eliminado")
        except:
            pass
        
        print(f"\n✅ Identificación completada")
        input("Presiona Enter para continuar...")

    def run(self):
        """Ejecutar el menú principal"""
        while True:
            self.print_header()
            
            # Seleccionar modelo o acción
            choice = self.select_model()
            
            if choice == "compare_all":
                # Seleccionar modelo para comparación masiva
                print("\n📊 SELECCIONA EL MODELO PARA COMPARACIÓN MASIVA:")
                print("-" * 50)
                
                available_models = {}
                for key, model in self.models_config.items():
                    if not model.get('use_original'):  # Excluir script original para comparación masiva
                        model_available = any(os.path.exists(path) for path in model['model_paths'])
                        if model_available:
                            available_models[key] = model
                            print(f"{key}. {model['name']} ✅")
                        else:
                            print(f"{key}. {model['name']} ❌ (No disponible)")
                
                if not available_models:
                    print("❌ No hay modelos disponibles para comparación masiva")
                    input("Presiona Enter para continuar...")
                    continue
                
                model_choice = input(f"\nSelecciona modelo (1-{len(self.models_config)-1}): ").strip()
                
                if model_choice in available_models:
                    self.compare_all_audios(model_choice)
                else:
                    print("❌ Selección inválida")
                
                input("\nPresiona Enter para continuar...")
                continue
            
            elif choice == "live_recording":
                # Identificación en vivo
                self.identify_speaker_live()
                continue
            
            # Flujo normal para comparación de dos audios
            model_choice = choice
            
            # Seleccionar primer audio
            audio1 = self.select_audio_file("🎵 SELECCIONA EL PRIMER ARCHIVO DE AUDIO:")
            if not audio1:
                continue
            
            # Seleccionar segundo audio
            audio2 = self.select_audio_file("🎵 SELECCIONA EL SEGUNDO ARCHIVO DE AUDIO:")
            if not audio2:
                continue
            
            # Mostrar selección
            print("\n" + "="*60)
            print("📋 CONFIGURACIÓN SELECCIONADA:")
            print("="*60)
            print(f"🤖 Modelo: {self.models_config[model_choice]['name']}")
            print(f"🎵 Audio 1: {os.path.basename(audio1)}")
            print(f"🎵 Audio 2: {os.path.basename(audio2)}")
            print(f"🖥️  Dispositivo: {self.device}")
            print("="*60)
            
            # Confirmar ejecución
            confirm = input("\n¿Continuar con la comparación? (s/n): ").lower()
            if confirm not in ['s', 'si', 'sí', 'y', 'yes']:
                continue
            
            # Ejecutar comparación
            if self.models_config[model_choice].get('use_original'):
                score = self.compare_with_original_script(model_choice, audio1, audio2)
            else:
                score = self.compare_with_model(model_choice, audio1, audio2)
            
            if score is not None:
                print(f"\n✅ Comparación completada exitosamente")
            else:
                print(f"\n❌ Error en la comparación")
            
            # Preguntar si quiere hacer otra comparación
            print("\n" + "-"*60)
            another = input("¿Realizar otra comparación? (s/n): ").lower()
            if another not in ['s', 'si', 'sí', 'y', 'yes']:
                print("👋 ¡Hasta luego!")
                break

def main():
    try:
        comparator = AudioComparator()
        comparator.run()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
