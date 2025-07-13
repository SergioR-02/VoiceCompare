# 🎤 Sistema de Control por Voz con Identificación de Hablante

Sistema avanzado de control por voz que identifica al hablante y ejecuta comandos según sus permisos asignados.

## 🚀 Características Principales

- **🎯 Identificación de Hablantes**: Usando modelos de deep learning (3D-Speaker)
- **🔐 Sistema de Permisos**: Comandos específicos por usuario
- **🎮 Doble Interfaz**: Gráfica moderna y línea de comandos
- **🎤 Reconocimiento de Voz**: Comandos en español
- **📊 Monitoreo en Tiempo Real**: Logs detallados con colores
- **⚙️ Configuración Avanzada**: Ajustes personalizables

## 📦 Instalación

### 1. Clonar el Repositorio
```bash
git clone https://github.com/usuario/voice-control-system.git
cd voice-control-system
```

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Verificar Archivos de Audio
Asegúrate de tener archivos de referencia en:
- `data/hablante_1/` - Archivos de Hablante_1
- `data/daniel_2/` - Archivos de Daniel

## 🎮 Uso del Sistema

### Inicio Rápido
```bash
python launcher.py
```

El launcher te permite elegir entre:
1. **📱 Interfaz Gráfica** (Recomendado)
2. **💻 Interfaz de Línea de Comandos**

### Interfaz Gráfica (GUI)
```bash
python voice_control_gui.py
```

**Características:**
- 🎨 Diseño moderno con tema oscuro
- 🎮 Controles visuales intuitivos
- 📊 Panel de estado en tiempo real
- 📝 Log con códigos de colores
- ⚙️ Ventanas de configuración
- 🧪 Herramientas de diagnóstico

### Interfaz de Línea de Comandos (CLI)
```bash
python voice_control.py
```

**Características:**
- 💻 Menú basado en texto
- 🔧 Ideal para usuarios avanzados
- 📊 Información detallada del sistema
- 🛠️ Herramientas de diagnóstico

## 👥 Sistema de Permisos

### Hablante_1 (Permisos Completos)
- ✅ Abrir bloc de notas
- ✅ Abrir navegador
- ✅ Abrir explorador de archivos
- ✅ Abrir calculadora
- ✅ Abrir buscador

### Daniel (Permisos Limitados)
- ✅ Abrir calculadora
- ✅ Abrir buscador

### Desconocido
- ❌ Sin permisos

## 🎤 Comandos de Voz Disponibles

### Aplicaciones
- `"abrir bloc de notas"` / `"abrir notepad"` / `"abrir editor"`
- `"abrir navegador"` / `"abrir chrome"`
- `"abrir explorador"` / `"abrir archivos"`
- `"abrir calculadora"`
- `"abrir buscador"` / `"buscar"`

### Control del Sistema
- `"salir"` / `"terminar"` (solo en modo escucha continua)

## 🔧 Configuración

### Ajustes Disponibles
- **⏱️ Duración de Identificación**: 2-10 segundos
- **⏱️ Duración de Comando**: 3-15 segundos
- **🎯 Threshold de Similitud**: 0.1-1.0
- **🎙️ Configuración de Micrófono**

### Archivos de Configuración
- `requirements.txt` - Dependencias del proyecto
- `launcher.py` - Selector de interfaz
- `voice_control.py` - Sistema principal CLI
- `voice_control_gui.py` - Interfaz gráfica
- `audio_comparator_menu.py` - Motor de comparación de audio

## 🛠️ Herramientas de Diagnóstico

### Pruebas Disponibles
1. **🎙️ Prueba de Micrófono**: Verifica funcionamiento del audio
2. **🎯 Prueba de Identificación**: Test de reconocimiento de voz
3. **🔧 Diagnóstico Completo**: Verificación integral del sistema
4. **📊 Estadísticas**: Métricas de uso y rendimiento

### Verificación de Dependencias
```bash
python -c "from launcher import check_dependencies; check_dependencies()"
```

## 📊 Estructura del Proyecto

```
voice-control-system/
├── 📄 launcher.py                 # Selector de interfaz
├── 📄 voice_control.py           # Sistema principal CLI
├── 📄 voice_control_gui.py       # Interfaz gráfica moderna
├── 📄 audio_comparator_menu.py   # Motor de audio
├── 📄 requirements.txt           # Dependencias
├── 📄 README.md                  # Documentación
├── 📁 data/                      # Archivos de audio
│   ├── 📁 hablante_1/
│   └── 📁 daniel_2/
├── 📁 pretrained/                # Modelos preentrenados
└── 📁 speakerlab/               # Framework 3D-Speaker
```

## 🐛 Solución de Problemas

### Problema: No se detecta el micrófono
**Solución:**
1. Verifica que el micrófono esté conectado
2. Revisa los permisos de audio en tu sistema
3. Ejecuta la prueba de micrófono en configuración

### Problema: No se identifica al hablante
**Soluciones:**
1. Verifica que existan archivos de referencia
2. Reduce el ruido de fondo
3. Habla más claramente
4. Aumenta la duración de identificación
5. Ajusta el threshold de similitud

### Problema: No se ejecutan comandos
**Soluciones:**
1. Verifica que estés identificado correctamente
2. Comprueba tus permisos en el panel correspondiente
3. Habla los comandos claramente
4. Usa las variaciones de comandos disponibles

### Problema: Errores de dependencias
**Solución:**
```bash
pip install --upgrade -r requirements.txt
```

## 🔄 Actualizaciones

### Versión Actual: 2.0
- ✅ Interfaz gráfica moderna
- ✅ Sistema de launcher
- ✅ Diagnóstico avanzado
- ✅ Configuración visual
- ✅ Logs con colores
- ✅ Documentación completa

### Próximas Funciones
- 🔄 Grabación de comandos personalizados
- 🔄 Estadísticas detalladas de uso
- 🔄 Múltiples idiomas
- 🔄 Integración con más aplicaciones
- 🔄 Modo de entrenamiento de voz

## 📞 Soporte

### Reportar Problemas
- Usa el diagnóstico integrado
- Revisa los logs generados
- Incluye información del sistema
- Describe los pasos para reproducir el error

### Contribuir
1. Fork del repositorio
2. Crear rama para nueva función
3. Implementar cambios
4. Añadir pruebas si es necesario
5. Crear pull request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- **3D-Speaker Framework**: Por el motor de identificación de hablantes
- **PyTorch Team**: Por el framework de deep learning
- **SpeechRecognition**: Por el reconocimiento de voz
- **Tkinter**: Por la interfaz gráfica

---

**🎤 ¡Disfruta controlando tu computadora con tu voz!**
