import os
import sys
import pathlib
import torch
import torchaudio
from pathlib import Path

# Añadir el directorio speakerlab al path
sys.path.insert(0, str(Path(__file__).parent / 'speakerlab'))

from speakerlab.process.processor import FBank
from speakerlab.utils.builder import dynamic_import
from modelscope.hub.snapshot_download import snapshot_download

def compare_two_audios(audio1_path, audio2_path):
    """
    Compara dos archivos de audio específicos usando el modelo ERes2Net
    """
    
    # Convertir a Path objects
    wav1 = Path(audio1_path)
    wav2 = Path(audio2_path)
    
    print(f"[INFO]: Comparando archivos:")
    print(f"  Archivo 1: {wav1}")
    print(f"  Archivo 2: {wav2}")
    
    # Verificar que los archivos existen
    if not wav1.exists():
        print(f"[ERROR]: No existe el archivo: {wav1}")
        return None
    if not wav2.exists():
        print(f"[ERROR]: No existe el archivo: {wav2}")
        return None
    
    # Configuración del modelo
    model_id = 'damo/speech_eres2net_base_sv_zh-cn_3dspeaker_16k'
    revision = 'v1.0.0'
    
    # Directorio base
    base_dir = Path(__file__).parent
    save_dir = base_dir / 'pretrained' / 'speech_eres2net_base_sv_zh-cn_3dspeaker_16k'
    save_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Descargar modelo (si no está ya descargado)
        print(f"[INFO]: Verificando modelo...")
        cache_dir = snapshot_download(
            model_id=model_id,
            cache_dir=str(save_dir),
            revision=revision,
        )
        cache_dir = Path(cache_dir)
        
        # Copiar archivos necesarios
        download_files = ['examples', 'eres2net_base_model.ckpt']
        for src in cache_dir.glob('*'):
            if any(df in src.name for df in download_files):
                dst = save_dir / src.name
                if not dst.exists():
                    try:
                        if src.is_dir():
                            import shutil
                            shutil.copytree(src, dst)
                        else:
                            import shutil
                            shutil.copy2(src, dst)
                    except (PermissionError, FileExistsError) as e:
                        print(f"[WARNING]: No se pudo copiar {src.name}: {e}")
        
        # Ruta del modelo preentrenado
        pretrained_model = save_dir / 'eres2net_base_model.ckpt'
        
        if not pretrained_model.exists():
            print(f"[ERROR]: No se encontró el archivo del modelo: {pretrained_model}")
            return None
        
        # Cargar modelo
        pretrained_state = torch.load(pretrained_model, map_location='cpu')
        
        # Configurar dispositivo
        if torch.cuda.is_available():
            print(f'[INFO]: Usando GPU para inferencia.')
            device = torch.device('cuda')
        else:
            print(f'[INFO]: Usando CPU para inferencia.')
            device = torch.device('cpu')
        
        # Configuración del modelo ERes2Net
        model_config = {
            'obj': 'speakerlab.models.eres2net.ERes2Net.ERes2Net',
            'args': {
                'feat_dim': 80,
                'embedding_size': 512,
                'pooling_func': 'TSTP',
                'two_emb_layer': False,
            }
        }
        
        # Crear modelo
        embedding_model = dynamic_import(model_config['obj'])(**model_config['args'])
        embedding_model.load_state_dict(pretrained_state)
        embedding_model.to(device)
        embedding_model.eval()
        
        # Función para cargar audio
        def load_wav(wav_file, obj_fs=16000):
            try:
                wav, fs = torchaudio.load(str(wav_file))
                if fs != obj_fs:
                    print(f'[WARNING]: Sample rate de {wav_file} es {fs}, resampling a {obj_fs}.')
                    wav = torchaudio.functional.resample(wav, fs, obj_fs)
                if wav.shape[0] > 1:
                    wav = wav[0, :].unsqueeze(0)
                return wav
            except Exception as e:
                print(f"[ERROR]: Error al cargar {wav_file}: {e}")
                return None
        
        # Extractor de características
        feature_extractor = FBank(80, sample_rate=16000, mean_nor=True)
        
        # Función para computar embedding
        def compute_embedding(wav_file):
            wav = load_wav(wav_file)
            if wav is None:
                return None
            
            try:
                feat = feature_extractor(wav).unsqueeze(0).to(device)
                with torch.no_grad():
                    embedding = embedding_model(feat)
                return embedding
            except Exception as e:
                print(f"[ERROR]: Error al computar embedding para {wav_file}: {e}")
                return None
        
        # Computar embeddings
        print(f"[INFO]: Computando embeddings...")
        
        emb1 = compute_embedding(wav1)
        emb2 = compute_embedding(wav2)
        
        if emb1 is None or emb2 is None:
            print(f"[ERROR]: No se pudieron computar los embeddings")
            return None
        
        # Calcular similitud coseno
        cos_sim = torch.nn.functional.cosine_similarity(emb1, emb2, dim=1)
        score = cos_sim.item()
        
        print(f"\n" + "="*50)
        print(f"RESULTADOS DE COMPARACIÓN")
        print(f"="*50)
        print(f"Archivo 1: {wav1.name}")
        print(f"Archivo 2: {wav2.name}")
        print(f"Similitud Coseno: {score:.4f}")
        
        # Interpretación del resultado
        if score > 0.5:
            print(f"Interpretación: MISMO HABLANTE (alta similitud)")
        elif score > 0.3:
            print(f"Interpretación: POSIBLEMENTE MISMO HABLANTE (similitud moderada)")
        else:
            print(f"Interpretación: HABLANTES DIFERENTES (baja similitud)")
        
        print(f"="*50)
        
        return score
        
    except Exception as e:
        print(f"[ERROR]: Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """
    Función principal que demuestra el uso del comparador
    """
    base_dir = Path(__file__).parent
    
    # Usar archivos de ejemplo del modelo preentrenado
    examples_dir = base_dir / "pretrained" / "speech_eres2net_base_sv_zh-cn_3dspeaker_16k" / "examples"
    
    print("=== COMPARACIÓN DE DIFERENTES HABLANTES ===")
    # Comparar diferentes hablantes
    audio1 = examples_dir / "speaker1_a_cn_16k.wav"
    audio2 = examples_dir / "speaker2_a_cn_16k.wav"
    score1 = compare_two_audios(audio1, audio2)
    
    print("\n=== COMPARACIÓN DEL MISMO HABLANTE ===")
    # Comparar mismo hablante
    audio3 = examples_dir / "speaker1_a_cn_16k.wav"
    audio4 = examples_dir / "speaker1_b_cn_16k.wav"
    score2 = compare_two_audios(audio3, audio4)
    
    if score1 is not None and score2 is not None:
        print(f"\n" + "="*60)
        print(f"RESUMEN DE COMPARACIONES")
        print(f"="*60)
        print(f"Hablantes diferentes: {score1:.4f}")
        print(f"Mismo hablante:       {score2:.4f}")
        print(f"Diferencia:           {score2 - score1:.4f}")
        print(f"="*60)

if __name__ == "__main__":
    main()
