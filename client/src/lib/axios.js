import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL, // Backend API URL
    withCredentials: false,
    // headers: { 'Content-Type': 'application/json' } // Removed to allow auto-detection for FormData
});

export default api