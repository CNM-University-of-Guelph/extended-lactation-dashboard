import axios from "axios"
import { ACCESS_TOKEN } from "./constants"

// Add this for debugging
console.log('API Base URL:', import.meta.env.VITE_API_URL)

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL?.replace(/\/$/, ''),  // Remove trailing slash
})

api.interceptors.request.use(
    (config) => {
        console.log('Full request URL:', `${config.baseURL}${config.url}`)
        const token = localStorage.getItem(ACCESS_TOKEN);
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Now we use this api object that will automatically add the authorization token
export default api