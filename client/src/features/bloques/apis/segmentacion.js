import api from "@/lib/axios";

export const segmentacion = {
    postSegmentacion: async (image, data) => {
        const data2 = [];
        data.forEach((item) => {
            if (item.id !== 'none') {
                // Recuperar los parámetros configurados visualmente (ej. por los Dropdowns)
                let parametrosDelBloque = item.params ? { ...item.params } : {};

                data2.push({
                    filter_name: item.name_api,
                    params: parametrosDelBloque
                });
            }
        });
        console.log(data2)
        try {
            const formData = new FormData();
            formData.append('image', image);
            formData.append('flow_config_json', JSON.stringify(data2));

            const response = await api.post('/process-image', formData)
            return response.data
        } catch (error) {
            console.error('Error al segmentar:', error)
            throw error
        }
    },
}

