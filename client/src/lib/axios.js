import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
    baseURL: import.meta.env.API_URL || 'http://127.0.0.1:8000/api/', // Backend API URL
    withCredentials: false,
    // headers: { 'Content-Type': 'application/json' } // Removed to allow auto-detection for FormData
});

export default api