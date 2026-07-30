import { useState, useCallback } from 'react';
import { iaQualityApi } from '../apis/iaQuality';

export function useIaQuality() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [selectedNodeIndex, setSelectedNodeIndex] = useState(null);

  const handleFileSelect = useCallback((file) => {
    if (!file) return;
    setSelectedFile(file);
    setError(null);
    setResult(null);
    setSelectedNodeIndex(null);
  }, []);

  const runAutoEnhance = useCallback(async () => {
    if (!selectedFile) {
      setError('Por favor selecciona o arrastra una imagen DICOM primero.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await iaQualityApi.autoEnhanceDicom(selectedFile);
      if (response.error) {
        setError(response.error);
        setResult(null);
      } else {
        setResult(response);
      }
    } catch (err) {
      setError(
        err.response?.data?.error || err.message || 'Error al conectar con el servidor de IA'
      );
    } finally {
      setLoading(false);
    }
  }, [selectedFile]);

  const resetState = useCallback(() => {
    setSelectedFile(null);
    setResult(null);
    setError(null);
    setSelectedNodeIndex(null);
  }, []);

  return {
    selectedFile, loading, result, error,
    selectedNodeIndex, setSelectedNodeIndex,
    handleFileSelect, runAutoEnhance, resetState,
  };
}
