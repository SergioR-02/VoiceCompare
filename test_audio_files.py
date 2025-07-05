import os
import pathlib
import torchaudio

# Verificar archivos de audio
audio_files = [
    r"d:\Documentos\Programacion\Python\3D-Speaker-main\record_out",
    r"d:\Documentos\Programacion\Python\3D-Speaker-main\record_out.wav",
    r"d:\Documentos\Programacion\Python\3D-Speaker-main\record_out.mp3",
    r"d:\Documentos\Programacion\Python\3D-Speaker-main\record_out.flac",
    r"d:\Documentos\Programacion\Python\3D-Speaker-main\record_out.m4a",
    r"d:\Documentos\Programacion\Python\3D-Speaker-main\record_out.ogg",
]

print("Verificando archivos de audio en el directorio...")
base_dir = pathlib.Path(r"d:\Documentos\Programacion\Python\3D-Speaker-main")

# Buscar archivos de audio
audio_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg', '.aac']
found_files = []

for ext in audio_extensions:
    for file in base_dir.glob(f"*{ext}"):
        found_files.append(file)
        print(f"Encontrado: {file}")

# Verificar archivos específicos
for file_path in audio_files:
    if os.path.exists(file_path):
        print(f"✓ Existe: {file_path}")
        try:
            info = torchaudio.info(file_path)
            print(f"  - Duración: {info.num_frames / info.sample_rate:.2f} segundos")
            print(f"  - Sample rate: {info.sample_rate} Hz")
            print(f"  - Canales: {info.num_channels}")
        except Exception as e:
            print(f"  - Error al leer: {e}")
    else:
        print(f"✗ No existe: {file_path}")

if not found_files:
    print("\nNo se encontraron archivos de audio en el directorio principal.")
    print("Buscando en subdirectorios...")
    
    # Buscar en subdirectorios
    for ext in audio_extensions:
        for file in base_dir.rglob(f"*{ext}"):
            found_files.append(file)
            print(f"Encontrado en subdirectorio: {file}")

print(f"\nTotal de archivos de audio encontrados: {len(found_files)}")
