import api from "@/lib/axios";

export const iaQualityApi = {
  /**
   * Envía una imagen DICOM para pre-procesamiento optimizado con IA.
   * La IA gestiona automáticamente el ID de serie, caché y número de pruebas.
   * @param {File} imageFile - Archivo DICOM (.dcm o binario DICOM).
   */
  autoEnhanceDicom: async (imageFile) => {
    try {
      const formData = new FormData();
      formData.append("image", imageFile);

      const response = await api.post("/ai/dicom/auto-enhance", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return response.data;
    } catch (error) {
      console.error("Error en autoEnhanceDicom:", error);
      throw error;
    }
  },

  /** Obtiene las estrategias radiológicas predeterminadas. */
  getPresets: async () => {
    try {
      const response = await api.get("/ai/dicom/presets");
      return response.data;
    } catch (error) {
      console.error("Error al obtener presets:", error);
      throw error;
    }
  },
};