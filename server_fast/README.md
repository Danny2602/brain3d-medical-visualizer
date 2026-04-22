# 🧠 Brain3D Medical Visualizer - Motor de Procesamiento (FastAPI)

¡Bienvenido al núcleo de Visión Computacional e Inteligencia Artificial del Proyecto Brain3D!

Este backend ha sido construido con una arquitectura **Ultramodular basada en Componentes (Nodos)**. A diferencia de un código tradicional monolítico, este sistema actúa como una "Caja de Legos". Permite que el Frontend (React) ensamble **Tuberías de Procesamiento Dinámicas (Pipelines)** mediante un sistema de Drag & Drop, decidiendo al vuelo el orden de los filtros y su intensidad matemática.

---

## 🏗️ Cómo funciona la Arquitectura (El Core)

Toda la "Magia Matemática" vive blindada dentro de la carpeta `processing/`. Esta carpeta es completamente ciega al Internet; no sabe qué es FastAPI ni qué es React, lo que la hace testeable y a prueba de errores.

### 1. El Molde (`base.py`)
Contiene la "Interface" principal llamada `BaseFilter`. Todo filtro creado en este sistema hereda obligatoriamente de este archivo.
**Regla de oro:** Todo filtro debe tener una función llamada `apply(self, img, history=None, **kwargs) -> np.ndarray`.

### 2. El Orquestador (`pipeline.py`)
Es el capataz de la fábrica. 
* Posee la Memoria RAM del proceso (`self.history`), guardando una copia fotográfica de cómo se veía el cerebro en el *"paso 1"*, *"paso 2"*, etc.
* Contiene el catálogo activo del sistema (`FILTERS_REGISTRY`). 
* Recibe el JSON plano que manda React, lee las instrucciones y llama a los archivos matemáticos correctos en el orden exacto.

### 3. Las Piezas de Lego (`filters/`)
Aquí viven las ecuaciones matemáticas separadas (OpenCV, Numpy). Están agrupadas metodológicamente en "Familias Médicas":
* 🧹 **noise_reduction:** Limpieza del sensor. (*NL-Means, Gaussian, Bilateral*)
* 🌑 **illumination_contrast:** Recuperación de detalles en zonas oscuras. (*CLAHE, Lógica Difusa, Min-Max, Estadístico Local*)
* 🔪 **edge_detection:** Descubrir la morfología pura. (*Canny, Thresholding de Otsu*)
* 🔍 **detail_enhancement:** Afilar estructuras orgánicas. (*Laplaciano, Top-Hat*)
* 🧠 **mask_extraction:** Aislamiento del tumor. (*Componentes Conexos, Morfología conectiva*)
* 🔀 **operations:** Fusiones de tiempo y espacio. (*Condicionales AND, OR para fusionar máscaras históricas*)

---

## 💻 El Puente con React (`main.py`)

El archivo `main.py` levanta un servidor de alta velocidad en FastAPI. 
Expone el endpoint `POST /process-image`. 
Este endpoint espera un **Formulario Multipart (FormData)** desde React que contenga dos cosas esenciales:

1. `image`: El archivo físico de la fotografía cerebral.
2. `flow_config_json`: Un archivo de texto en formato JSON dictando las instrucciones de ensamblaje.

### Ejemplo Exacto de lo que debe mandar React (`flow_config_json`):
```json
[
  {
    "filter_name": "nl_means",
    "params": { "h_value": 15 }
  },
  {
    "filter_name": "fuzzy_logic",
    "params": { "mode": "triangular", "width": 0.4 }
  },
  {
    "filter_name": "canny_edges",
    "params": { "low_threshold": 50, "high_threshold": 150 }
  },
  {
    "filter_name": "connect_comp",
    "params": { "original_layer_name": "fuzzy_logic", "return_mask_only": false }
  }
]
```
> **Explicación del JSON:** 
> 1. Limpiará el ruido.
> 2. Le dará un contraste brillante con Lógica Difusa.
> 3. Extraerá las líneas morfológicas (Bordes).
> 4. Extraerá el tejido buscando las masas blancas y recortará el resultado a color **sobre la capa antigua de lógica difusa** (memoria fotográfica).

---

## 🛠️ Cómo añadir un Nuevo Filtro al Sistema (Guía 3 Pasos)

Imagina que descubres una nueva fórmula matemática increíble con OpenCV y quieres agregarla al Drag & Drop:

### PASO 1: Crear el Archivo
Dirígete a la carpeta `processing/filters/...` que mejor represente el objetivo del filtro y crea un archivo nuevo. (Ej. `super_filtro.py`).

### PASO 2: Escribir la Matemática
Hereda de BaseFilter e invoca siempre `.astype(np.uint8)` al final para evitar corrupciones de video.
```python
import cv2
import numpy as np
from processing.base import BaseFilter

class SuperFiltro(BaseFilter):
    # Declaras las variables que tu FrontEnd podrá modificar mediante sliders (Ej. poder=10)
    def apply(self, img: np.ndarray, history: dict = None, poder: int = 10, **kwargs) -> np.ndarray:
        
        # --- Tu código de OpenCV aquí ---
        imagen_transformada = cv2.blur(img, (poder, poder))
        
        return imagen_transformada
```

### PASO 3: Registrar la Pieza en la Base de Datos Local
Ve al archivo maestro: `processing/pipeline.py`.
1. Impórtalo arriba: `from processing.filters...super_filtro import SuperFiltro`
2. Regístralo en el diccionario dándole un nombre comercial (El nombre exacto que React debe enviar en el JSON para invocarlo):
```python
FILTERS_REGISTRY = {
    "super_magia": SuperFiltro(),
}
```

¡Listo! Automáticamente ese filtro está en línea y puede ser llamado desde cualquier interfaz del mundo.

---

## 🚀 Despliegue Inmediato (Local)

Para encender el motor de IA en tu computadora, abre tu terminal y ejecuta:

```bash
# 1. Activar tu burbuja aislada (Si estás en Windows)
.\venv\Scripts\activate

# 2. Encender la turbina
fastapi dev main.py
# (O alternativamente: uvicorn main:app --reload)
```

👉 Entra a **http://127.0.0.1:8000/docs** para abrir Swagger UI y probar tus filtros a nivel backend enviándoles JSON manualmente.
