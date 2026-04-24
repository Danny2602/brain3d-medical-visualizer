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
            { name: 'logarithmic', label: 'Corrección Logarítmica', desc: 'Corrección no lineal de la iluminación.', params: { mode: 'logarithmic', factor: 1.2 } },
            { name: 'gamma', label: 'Corrección Gamma', desc: 'Corrección no lineal de la iluminación.', params: { mode: 'gamma', factor: 1.2 } },
            { name: 'clahe', label: 'Ecualización CLAHE', desc: 'Ajuste de contraste local adaptativo.', params: { clipLimit: 2.0, tileGridSize: [8, 8] } },
            { name: 'min_max', label: 'Normalización Min-Max', desc: 'Estira el rango dinámico al máximo posible, forzando la imagen a abarcar desde el tono más oscuro al más brillante.', params: {} },
            { name: 'global_hist_eq', label: 'Ecualización Global', desc: 'Aplica ecualización de histograma a toda la imagen para mejorar el contraste global.', params: {} },
            { name: 'local_statistical', label: 'Estadístico Local', desc: 'Mejora el contraste basándose en la media y desviación estándar de cada zona local.', params: {} },
            { name: 'fuzzy_logic', label: 'Fuzzy Logic', desc: 'Realce experto mediante lógica difusa Mamdani.', params: { mode: 'triangular' } },
        ]
    },
    edges: {
        label: 'Detección de Bordes',
        color: 'rose',
        items: [
            { name: 'canny_edges', label: 'Canny Edges', desc: 'Detecta los contornos de estructuras.', params: { low_threshold: 50, high_threshold: 150 } },
            { name: 'otsu_threshold', label: 'Umbral Otsu', desc: 'Binarización automática por intensidad.', params: {} },
        ]
    },
    detail: {
        label: 'Mejora de Detalles',
        color: 'cyan',
        items: [
            { name: 'tophat_morf', label: 'Top-Hat Morfológico', desc: 'Extrae detalles pequeños y brillantes suprimiendo el gradiente o variación lenta del fondo.', params: { kernel_size: 15 } },
            { name: 'unsharp_mask', label: 'Máscara de Desenfoque', desc: 'Aumenta la nitidez aparente restando una versión difuminada al original.', params: { ksize: 5 } },
            { name: 'laplacian', label: 'Laplaciano', desc: 'Resalta texturas y contornos calculando la segunda derivada espacial.', params: {} },
        ]
    },
    segmentacion: {
        label: 'Extracción de Máscara',
        color: 'cyan',
        items: [
            { name: 'morph_connect', label: 'Conexión Morfológica', desc: 'Une píxeles interconectados para formar regiones completas.', params: { kernel_size: 5 } },
        ]
    }
};

export const OPERATOR_TYPES = {
    logic: {
        label: 'Operaciones Lógicas',
        color: 'indigo',
        items: [
            { name: 'logic_or', label: 'Unión (OR)', desc: 'Suma dos máscaras (Input A + Input B).', params: {} },
            { name: 'logic_and', label: 'Intersección (AND)', desc: 'Mantiene solo el área común.', params: {} }
        ]
    },
    final: {
        label: 'Resultado Final',
        color: 'purple',
        items: [
            { name: 'mass_cleaning', label: 'Limpieza de Masa', desc: 'Limpia artefactos y extrae el tumor final.', params: { min_size_pct: 0.015 } },
            { name: 'mask_clipping', label: 'Recorte de Máscara', desc: 'Recorta la máscara de la imagen original.', params: { min_size_pct: 0.015 } },
        ]
    }
};
