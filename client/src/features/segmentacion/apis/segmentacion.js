import api from "@/lib/axios";

export const segmentacion = {
    postSegementacion: async (image) => {
        const response = await api.post('/segmentacion/', image);
        return response.data;

    },

    postSegementacionFourier: async (image) => {
        const response = await api.post('/fourier/', image);
        return response.data;
    }
}