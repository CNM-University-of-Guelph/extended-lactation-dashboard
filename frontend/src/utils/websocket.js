const WS_SCHEME = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const API_URL = import.meta.env.VITE_API_URL;

// Remove http:// or https:// and any trailing slash
const WS_BASE_URL = API_URL?.replace(/^https?:\/\//, '').replace(/\/$/, '');

export const createWebSocket = (path) => {
    if (!WS_BASE_URL) {
        throw new Error('VITE_API_URL environment variable is not set');
    }
    
    const wsUrl = `${WS_SCHEME}//${WS_BASE_URL}${path}`;
    
    // Log for debugging
    console.log('Creating WebSocket connection:');
    console.log('API URL:', API_URL);
    console.log('WS Base URL:', WS_BASE_URL);
    console.log('Final WebSocket URL:', wsUrl);
    
    return new WebSocket(wsUrl);
}; 