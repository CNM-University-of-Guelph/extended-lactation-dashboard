// Get the backend URL from environment variables
const WS_SCHEME = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const WS_BASE_URL = import.meta.env.VITE_API_URL?.replace(/^https?:\/\//, '');

export const createWebSocket = (path) => {
    // Use development URL if no API URL is provided
    const wsUrl = WS_BASE_URL 
        ? `${WS_SCHEME}//${WS_BASE_URL}${path}`
        : `ws://localhost:8000${path}`;
        
    console.log('Creating WebSocket connection to:', wsUrl);
    
    return new WebSocket(wsUrl);
}; 