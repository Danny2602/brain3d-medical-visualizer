export const FILTER_TYPES = {
    noise: {
        label: 'Reducción de Ruido',
        color: 'emerald',
        items: [
            { name: 'nl_means', label: 'NL-Means', desc: 'Elimina ruido preservando texturas finas.', params: { h_value: 10 } },
            { name: 'bilateral_filter', label: 'Bilateral', desc: 'Suaviza sin perder los bordes del tumor.', params: { diameter: 5, sigma_color: 50, sigma_space: 50 } },
            { name: 'gaussian_filter', label: 'Gaussian Blur', desc: 'Desenfoque suave para eliminar ruido gaussiano.', params: { kernel_size: 5 } },
            { name: 'median_blur', label: 'Filtro de Mediana', desc: 'Excelente para eliminar ruido de tipo sal y pimienta.', params: { kernel_size: 5 } }
        ]
    },
    contrast: {
        label: 'Realce y Contraste',
        color: 'amber',
        items: [
            { name: 'clahe', label: 'CLAHE', desc: 'Ajuste de contraste local adaptativo.', params: { clipLimit: 2.0, tileGridSize: [8, 8] } },
            { name: 'fuzzy_logic', label: 'Fuzzy Logic', desc: 'Realce experto mediante lógica difusa Mamdani.', params: { mode: 'triangular' } },
            { name: 'log_gamma', label: 'Log/Gamma', desc: 'Corrección no lineal de la iluminación.', params: { mode: 'gamma', factor: 1.2 } },
            { name: 'normalize', label: 'Normalización', desc: 'Escala los píxeles al rango óptimo 0-255.', params: {} },
            { name: 'hist_equalize', label: 'Ecualización', desc: 'Ajuste global del histograma de la imagen.', params: {} }
        ]
    },
    edges: {
        label: 'Segmentación',
        color: 'rose',
        items: [
            { name: 'canny_edges', label: 'Canny Edges', desc: 'Detecta los contornos de estructuras.', params: { low_threshold: 50, high_threshold: 150 } },
            { name: 'otsu_threshold', label: 'Otsu Threshold', desc: 'Binarización automática por intensidad.', params: {} },
            { name: 'adaptive_threshold', label: 'Umbral Adaptativo', desc: 'Binarización basada en regiones locales.', params: { blockSize: 11, C: 2 } }
        ]
    },
    detail: {
        label: 'Morfología',
        color: 'cyan',
        items: [
            { name: 'tophat_morf', label: 'Top-Hat', desc: 'Resalta objetos pequeños brillantes sobre fondo oscuro.', params: { kernel_size: 15 } },
            { name: 'morph_connect', label: 'Cierre Morfológico', desc: 'Une puntos cercanos y rellena huecos en la máscara.', params: { kernel_size: 5 } }
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
            { name: 'connect_comp', label: 'Connect Components', desc: 'Limpia artefactos y extrae el tumor final.', params: { min_size_pct: 0.015 } }
        ]
    }
};
