import api from "@/lib/axios";

export const segmentacion = {
    postSegmentacion: async (image, data) => {
        const data2 = [];
        data.map((item) => {
            if (item.id !== 'none') {
                data2.push({
                    filter_name: item.name_api,
                    params: {

                    }
                });
            }
        })
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

