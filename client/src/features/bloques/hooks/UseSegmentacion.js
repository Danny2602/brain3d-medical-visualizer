import { segmentacion } from "@/features/bloques/apis/segmentacion";
import { useState } from "react";

export const useSegmentacion = () => {
    const [segmentacionData, setSegmentacionData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const postSegmentacion = async (image, data) => {
        setLoading(true);
        setError(null);
        try {
            const response = await segmentacion.postSegmentacion(image, data);
            setSegmentacionData(response);
            return response;
        } catch (error) {
            setError(error);
            throw error;
        } finally {
            setLoading(false);
        }
    }
    return { postSegmentacion, segmentacionData, loading, error }
}