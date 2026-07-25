export const FILTER_TYPES = {
    noise: {
        label: 'Reducción de Ruido',
        color: 'emerald',
        items: [
            { name: 'nl_means', label: 'NL-Means', desc: 'Elimina ruido preservando texturas finas.', params: { h_value: 10 } },
            { name: 'bilateral_filter', label: 'Filtro Bilateral', desc: 'Suaviza sin perder los bordes del tumor.', params: { diameter: 5, sigma_color: 50, sigma_space: 50 } },
            { name: 'gaussian_filter', label: 'Filtro Gaussiano', desc: 'Desenfoque suave para eliminar ruido gaussiano.', params: { kernel_size: 5 } },
        ]
    },
    contrast: {
        label: 'Iluminación y Contraste',
        color: 'amber',
        items: [
            { name: 'logarithmic', label: 'Corrección Logarítmica', desc: 'Realiza en la imagen una corrección logarítmica de la iluminación.', params: {} },
            { name: 'gamma', label: 'Corrección Gamma', desc: 'Realiza una corrección gamma, hace que la imagen sea más brillante o más oscura según el valor del factor.', params: { factor: 1.2 } },
            { name: 'clahe', label: 'Ecualización CLAHE', desc: 'Ajuste de contraste local adaptativo.', params: { clipLimit: 2.0, tileGridSize: [8, 8] } },
            { name: 'min_max', label: 'Normalización Min-Max', desc: 'Estira el rango de valores de la imagen al máximo posible, forzando la imagen a abarcar desde el tono más oscuro al más brillante.', params: {} },
            { name: 'global_hist_eq', label: 'Ecualización Global', desc: 'Aplica ecualización de histograma a toda la imagen para mejorar el contraste global.', params: {} },
            { name: 'local_statistical', label: 'Estadístico Local', desc: 'Mejora el contraste basándose en la media y desviación estándar de cada zona local.', params: { kernel_size: 15, k_factor: 2.0 } },
            { name: 'fuzzy_logic', label: 'Fuzzy Logic', desc: 'Realce experto mediante lógica difusa Mamdani.', params: { mode: 'triangular' } },
        ]
    },
    edges: {
        label: 'Detección de Bordes',
        color: 'rose',
        items: [
            { name: 'canny_edges', label: 'Canny Edges', desc: 'Detecta los contornos de estructuras.', params: { sigma: 0.33 } },
            { name: 'otsu_threshold', label: 'Umbral Otsu', desc: 'Binarización automática por intensidad.', params: {} },
            { name: 'multi_otsu_threshold', label: 'Umbral Otsu Múltiple', desc: 'Binarización automática por intensidad en múltiples niveles de gris.', params: { classes: 3 } },
        ]
    },
    detail: {
        label: 'Mejora de Detalles',
        color: 'cyan',
        items: [
            { name: 'tophat_morf', label: 'Top-Hat Morfológico', desc: 'Extrae detalles pequeños y brillantes suprimiendo el gradiente o variación lenta del fondo.', params: { kernel_size: 100 } },
            { name: 'unsharp_mask', label: 'Máscara de Desenfoque', desc: 'Aumenta la nitidez aparente restando una versión difuminada al original.', params: { sigma: 1.0 } },
            { name: 'laplacian', label: 'Laplaciano', desc: 'Resalta texturas y contornos calculando la segunda derivada espacial.', params: {} },
        ]
    },
    segmentacion: {
        label: 'Extracción de Máscara',
        color: 'cyan',
        items: [
            { name: 'morph_connect', label: 'Conexión Morfológica', desc: 'Une píxeles interconectados para formar regiones completas.', params: { kernel_size: 3 } },
            { name: 'morph_open', label: 'Apertura Morfológica', desc: 'Realiza una erosión y luego una dilatación.', params: { kernel_size: 3 } },
        ]
    },
    advanced_segmentation: {
        label: 'Segmentación Avanzada',
        color: 'blue',
        items: [
            { name: 'region_growing', label: 'Crecimiento de Regiones', desc: 'Realiza una segmentación de la imagen a travez de una semilla y una tolerancia.', params: { seed_x: 128, seed_y: 128, tolerance: 10 } },
            { name: 'skull_stripping', label: 'Eliminación de Cráneo', desc: 'Realiza una segmentación de la imagen eliminando el cráneo.', params: { erosion_iters: 5, dilation_iters: 5 } },
            { name: 'watershed', label: 'Búsqueda de Crestas', desc: 'Realiza una segmentación de la imagen a travez de una cresta.', params: {} },
        ]
    }

};

export const OPERATOR_TYPES = {
    logic: {
        label: 'Operaciones Lógicas',
        color: 'indigo',
        items: [
            { name: 'logic_or', label: 'Unión (OR)', desc: 'Suma dos máscaras (Input A + Input B).', params: {} },
            { name: 'logic_and', label: 'Intersección (AND)', desc: 'Mantiene solo el área común.', params: {} },
            { name: 'invert_not', label: 'Inversión (NOT)', desc: 'Invierte los valores de la máscara.', params: {} }
        ]
    },
    final: {
        label: 'Resultado Final',
        color: 'purple',
        items: [
            { name: 'mass_cleaning', label: 'Limpieza de Masa', desc: 'Limpia artefactos y extrae el tumor final.', params: { min_size_pct: 0.015 } },
            { name: 'mask_clipping', label: 'Recorte de Máscara', desc: 'Recorta la máscara de la imagen original.', params: {} },
        ]
    }
};


//Filtros para el formato dicom 
export const DICOM_FILTER_TYPES = {
    noise: {
        label: 'Reducción de Ruido (DICOM)',
        color: 'emerald',
        items: [
            { name: 'bilateral_filter', label: 'Filtro Bilateral', desc: 'Suaviza la imagen preservando bordes mediante filtrado bilateral en el espacio de color y coordenadas.', params: { diameter: 9, sigma_color: 0.05, sigma_space: 5.0 } },
            { name: 'gaussian_filter', label: 'Filtro Gaussiano', desc: 'Aplica desenfoque gaussiano suave para eliminar ruido de alta frecuencia sin perder estructura general.', params: { kernel_size: 5 } },
            { name: 'nl_means_filter', label: 'Filtro NL-Means', desc: 'Eliminación avanzada de ruido comparando parches similares en toda la imagen, preservando texturas finas.', params: { h: 0.1, patch_size: 7, patch_distance: 11 } },
        ]
    },
    contrast: {
        label: 'Iluminación y Contraste (DICOM)',
        color: 'amber',
        items: [
            { name: 'clahe_filter', label: 'Ecualización CLAHE', desc: 'Ajuste de contraste local adaptativo con límite de recorte. Mejora la visibilidad de estructuras en zonas oscuras sin sobreexponer las brillantes.', params: { clipLimit: 2.0, tileGridSize: [8, 8] } },
            { name: 'fuzzy_logic_filter', label: 'Lógica Difusa', desc: 'Realce experto de contraste mediante inferencia difusa Mamdani con funciones de membresía configurables (triangular, campana o sigmoide).', params: { mode: 'triangular', sigma: 0.15 } },
            { name: 'gamma_filter', label: 'Corrección Gamma', desc: 'Ajusta la luminosidad global mediante una curva de potencia. Valores < 1 aclaran la imagen, valores > 1 la oscurecen.', params: { gamma: 1.0 } },
            { name: 'global_hist_eq_filter', label: 'Ecualización Global', desc: 'Ecualización de histograma sobre toda la imagen para redistribuir uniformemente las intensidades y mejorar el contraste global.', params: {} },
            { name: 'local_statistical_filter', label: 'Estadístico Local', desc: 'Mejora el contraste local usando la media y desviación estándar de cada vecindad, iluminando zonas oscuras sin sobreexponer las brillantes.', params: { kernel_size: 15, k_factor: 2.0 } },
            { name: 'logarithmic_filter', label: 'Corrección Logarítmica', desc: 'Transformación logarítmica que comprime el rango dinámico, realzando detalles en zonas oscuras de la imagen DICOM.', params: { gain: 1.0 } },
            { name: 'min_max_filter', label: 'Normalización Min-Max', desc: 'Estira el rango de intensidades al intervalo deseado [alpha, beta], forzando la imagen a abarcar todo el espectro de tonos.', params: { alpha: 0.0, beta: 1.0 } },
        ]
    },
    edges: {
        label: 'Detección de Bordes (DICOM)',
        color: 'rose',
        items: [
            { name: 'canny_edges_filter', label: 'Canny Edges', desc: 'Detecta contornos anatómicos precisos mediante el algoritmo de Canny con umbrales de histéresis configurables.', params: { sigma: 1.0, low_threshold: 0.1, high_threshold: 0.2 } },
            { name: 'otsu_threshold_filter', label: 'Umbral Otsu', desc: 'Binarización automática calculando el umbral óptimo que minimiza la varianza intra-clase sobre valores físicos (HU).', params: {} },
            { name: 'multi_otsu_threshold_filter', label: 'Umbral Multi-Otsu', desc: 'Segmentación en múltiples clases anatómicas mediante umbrales Otsu sucesivos, ideal para separar tejidos por densidad.', params: { classes: 3 } },
        ]
    },
    detail: {
        label: 'Mejora de Detalles (DICOM)',
        color: 'cyan',
        items: [
            { name: 'laplacian_filter', label: 'Laplaciano', desc: 'Resalta texturas y contornos calculando la segunda derivada espacial (Laplaciano) de la imagen.', params: {} },
            { name: 'tophat_morf_filter', label: 'Top-Hat Morfológico', desc: 'Extrae estructuras brillantes pequeñas (calcificaciones, vasos) suprimiendo el fondo mediante transformada White Top-Hat.', params: { kernel_size: 5 } },
            { name: 'unsharp_mask_filter', label: 'Máscara de Enfoque', desc: 'Aumenta la nitidez aparente restando una versión desenfocada de la imagen original con radio y cantidad ajustables.', params: { radius: 1.0, amount: 1.0 } },
        ]
    },
    segmentacion: {
        label: 'Extracción de Máscara (DICOM)',
        color: 'teal',
        items: [
            { name: 'morph_erode_filter', label: 'Erosión Morfológica', desc: 'Reduce las regiones brillantes eliminando píxeles de los bordes. Útil para separar objetos unidos o eliminar ruido fino.', params: { kernel_size: 5, iterations: 1 } },
            { name: 'morph_dilate_filter', label: 'Dilatación Morfológica', desc: 'Expande las regiones brillantes añadiendo píxeles a los bordes. Útil para cerrar pequeños huecos y unir regiones cercanas.', params: { kernel_size: 5, iterations: 1 } },
            { name: 'morph_open_filter', label: 'Apertura Morfológica', desc: 'Erosión seguida de dilatación. Elimina ruido pequeño y protuberancias sin reducir significativamente el tamaño del objeto principal.', params: { kernel_size: 5, iterations: 1 } },
            { name: 'morph_connect_filter', label: 'Conexión Morfológica', desc: 'Closing morfológico que une áreas cercanas dilatando y luego erosionando, cerrando huecos dentro de estructuras anatómicas.', params: { kernel_size: 5, iterations: 1 } },
            { name: 'morph_gradient_filter', label: 'Gradiente Morfológico', desc: 'Calcula la diferencia entre dilatación y erosión para resaltar los bordes y contornos de las estructuras anatómicas.', params: { kernel_size: 3 } },
            { name: 'region_fill_filter', label: 'Relleno de Regiones', desc: 'Rellena agujeros oscuros dentro de estructuras anatómicas (ej. ventrículos tras detectar el cerebro completo).', params: {} },
        ]
    },
    advanced_segmentation: {
        label: 'Segmentación Avanzada (DICOM)',
        color: 'blue',
        items: [
            { name: 'region_growing_filter', label: 'Crecimiento de Regiones', desc: 'Segmentación por inundación (flood fill) a partir de una semilla, expandiéndose a píxeles vecinos dentro de la tolerancia especificada.', params: { seed_x: 128, seed_y: 128, tolerance: 0.05 } },
            { name: 'skull_stripping_filter', label: 'Eliminación de Cráneo', desc: 'Aísla la masa cerebral eliminando automáticamente el cráneo y fondo mediante binarización Otsu, closing y extracción del componente más grande.', params: {} },
            { name: 'watershed_filter', label: 'Segmentación Watershed', desc: 'Separa objetos unidos mediante el algoritmo de cuencas hidrográficas, usando la transformada de distancia y picos locales como marcadores.', params: { min_distance: 10 } },
        ]
    },
    final: {
        label: 'Resultado Final (DICOM)',
        color: 'purple',
        items: [
            { name: 'mass_cleaning_filter', label: 'Limpieza de Masa', desc: 'Elimina componentes conectados pequeños (artefactos, ruido macro) conservando solo las regiones con área mayor al mínimo especificado.', params: { min_area: 100 } },
            { name: 'mask_clipping_filter', label: 'Recorte por Máscara', desc: 'Recorta la imagen original usando una máscara precalculada de otro nodo, conservando solo los píxeles dentro de la región segmentada.', params: {} },
        ]
    }
};

export const DICOM_OPERATOR_TYPES = {
    logic: {
        label: 'Operaciones Lógicas (DICOM)',
        color: 'indigo',
        items: [
            { name: 'logic_or_filter', label: 'Unión (OR)', desc: 'Combina dos máscaras DICOM manteniendo los píxeles activos de ambas entradas (unión lógica).', params: {} },
            { name: 'logic_and_filter', label: 'Intersección (AND)', desc: 'Conserva únicamente los píxeles activos en ambas máscaras DICOM simultáneamente (intersección lógica).', params: {} },
            { name: 'invert_not_filter', label: 'Inversión (NOT)', desc: 'Invierte los valores de intensidad respetando la escala física: los píxeles claros se oscurecen y viceversa.', params: {} },
        ]
    }
};
