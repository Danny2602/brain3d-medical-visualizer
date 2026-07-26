import axios from 'axios';

// creacion de la instacia de axios 
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL, // Backend API URL
    withCredentials: false,
    // headers: { 'Content-Type': 'application/json' } // Removed to allow auto-detection for FormData
});

export default api