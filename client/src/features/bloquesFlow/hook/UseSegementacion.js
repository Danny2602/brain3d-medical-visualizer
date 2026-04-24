import { useState } from 'react';
import { segmentacion } from '../apis/segmentacion';

export const useSegmentacion = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [data, setData] = useState(null);

    const ejecutarProcesamiento = async (imageFile, flowConfig) => {
        // Validaciones previas
        if (!imageFile) {
            setError("Falta la imagen de origen.");
            return null;
        }
        if (!flowConfig || flowConfig.length === 0) {
            setError("El pipeline está vacío.");
            return null;
        }

        setLoading(true);
        setError(null);

        try {
            const result = await segmentacion.postSegmentacion(imageFile, flowConfig);
            setData(result);
            return result;
        } catch (err) {
            const mensajeError = err.response?.data?.detail || "Error al procesar la imagen en el servidor.";
            setError(mensajeError);
            return null;
        } finally {
            setLoading(false);
        }
    };

    const limpiarEstado = () => {
        setData(null);
        setError(null);
        setLoading(false);
    };

    return {
        ejecutarProcesamiento,
        loading,
        error,
        data,
        limpiarEstado
    };
};
