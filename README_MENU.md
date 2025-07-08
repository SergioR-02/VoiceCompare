# 🎤 Comparador de Audios 3D-Speaker - Guía del Menú

## 📋 Descripción

El menú integrado (`audio_comparator_menu.py`) proporciona una interfaz interactiva para comparar audios usando los modelos 3D-Speaker. Es la forma más fácil y completa de usar el sistema.

## 🚀 Cómo usar

### Ejecutar el menú
```powershell
python audio_comparator_menu.py
```

## 🔧 Funcionalidades

### 1. 📊 Selección de Modelo
- **CAM++ (Recomendado)**: Más rápido y preciso para idioma chino
- **ERes2Net Base**: Modelo robusto y confiable
- **Script Original**: Usar el script original del proyecto
- **Comparación Masiva**: Comparar todos los audios disponibles

### 2. 🎵 Selección de Audios
- Muestra todos los archivos de audio disponibles organizados por carpetas
- Información detallada: duración, frecuencia, tamaño
- Opción para ver información completa de cualquier archivo
- Filtrado automático de archivos válidos

### 3. 📈 Análisis de Resultados
- **Similitud coseno**: Valor numérico de 0 a 1
- **Interpretación automática**: Estado basado en thresholds
- **Niveles de confianza**: Desde "Muy Alta" hasta "Muy Baja"
- **Indicadores visuales**: Emojis para fácil interpretación

### 4. 🔄 Comparación Masiva
- Crea matriz de similitud entre todos los audios
- Identifica grupos de alta similitud
- Exporta resultados a CSV
- Análisis automático de clusters

## 📊 Interpretación de Resultados

### Escala de Similitud (CAM++)
- **> 0.75**: 🟢 MISMO LOCUTOR (Muy Alta Confianza)
- **> 0.65**: 🟢 PROBABLEMENTE MISMO LOCUTOR (Alta Confianza)
- **> 0.50**: 🟡 POSIBLEMENTE MISMO LOCUTOR (Media Confianza)
- **> 0.35**: 🟠 PROBABLEMENTE DIFERENTES (Baja Similitud)
- **≤ 0.35**: 🔴 LOCUTORES DIFERENTES (Muy Baja Similitud)

### Escala de Similitud (ERes2Net)
- **> 0.70**: 🟢 MISMO LOCUTOR (Muy Alta Confianza)
- **> 0.60**: 🟢 PROBABLEMENTE MISMO LOCUTOR (Alta Confianza)
- **> 0.45**: 🟡 POSIBLEMENTE MISMO LOCUTOR (Media Confianza)
- **> 0.30**: 🟠 PROBABLEMENTE DIFERENTES (Baja Similitud)
- **≤ 0.30**: 🔴 LOCUTORES DIFERENTES (Muy Baja Similitud)

## 💡 Consejos de Uso

### 🎯 Para mejores resultados:
1. **Duración**: Archivos de 3-10 segundos son ideales
2. **Calidad**: Audio limpio sin ruido de fondo
3. **Formato**: WAV 16kHz mono recomendado
4. **Contenido**: Evitar música, usar solo voz

### ⚠️ Limitaciones:
- Archivos muy cortos (<1s) pueden ser imprecisos
- Ruido de fondo afecta la precisión
- Diferentes idiomas pueden afectar CAM++
- Modelos sin entrenar no son confiables

## 📁 Estructura de Archivos

```
📂 Archivos de audio detectados automáticamente en:
├── 📁 data/
│   ├── 📁 daniel_2/
│   └── 📁 hablante_1/
├── 📁 pretrained/examples/
└── 📁 otros directorios con .wav, .mp3, .flac
```

## 🔧 Características Avanzadas

### 📊 Matriz de Similitud
- Compara todos los audios entre sí
- Genera archivo CSV con resultados
- Identifica automáticamente grupos similares
- Análisis visual de relaciones

### 💾 Exportar Resultados
- Formato CSV compatible con Excel
- Timestamp automático en nombres
- Estructura organizada para análisis

### 🖥️ Información del Sistema
- Detección automática de GPU/CPU
- Conteo de archivos disponibles
- Verificación de modelos instalados

## 🚨 Solución de Problemas

### Modelo no encontrado
```
❌ No encontrado
```
**Solución**: Verificar que los archivos del modelo estén en `pretrained/`

### Error de carga de audio
```
❌ Error con archivo.wav: ...
```
**Solución**: Verificar formato del archivo (usar WAV 16kHz si es posible)

### Memoria insuficiente
```
RuntimeError: CUDA out of memory
```
**Solución**: Usar CPU en lugar de GPU, o procesar menos archivos

## 📈 Ejemplos de Uso

### Comparación Simple
1. Ejecutar: `python audio_comparator_menu.py`
2. Seleccionar modelo: `1` (CAM++)
3. Elegir primer audio: `1`
4. Elegir segundo audio: `2`
5. Confirmar: `s`

### Análisis Masivo
1. Ejecutar menú
2. Seleccionar: `4` (Comparar TODOS)
3. Elegir modelo: `1` (CAM++)
4. Esperar procesamiento
5. Guardar CSV: `s`

## 📞 Soporte

Si encuentras problemas:
1. Verificar que las dependencias estén instaladas
2. Comprobar que los modelos estén descargados
3. Verificar formato de archivos de audio
4. Revisar mensajes de error para diagnóstico

---
*Creado para facilitar el uso del proyecto 3D-Speaker con una interfaz amigable*
