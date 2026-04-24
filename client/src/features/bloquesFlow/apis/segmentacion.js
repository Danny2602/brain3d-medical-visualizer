import api from "@/lib/axios";

export const segmentacion = {
    /**
     * Envía la imagen y la configuración del pipeline al backend.
     * @param {File} image - Archivo de imagen MRI.
     * @param {Array} flowConfig - Estructura de nodos y conexiones.
     */
    postSegmentacion: async (image, flowConfig) => {
        try {
            const formData = new FormData();
            formData.append('image', image);
            formData.append('flow_config_json', JSON.stringify(flowConfig));

            const response = await api.post('/process-image-nodos', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return response.data;
        } catch (error) {
            console.error('Error en postSegmentacion:', error);
            throw error;
        }
    },
};
