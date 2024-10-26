import { useContext, useState } from "react"
import api from "../api"
import { useNavigate, Link } from "react-router-dom"
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants"
import "../styles/LoginForm.css"
import LoadingIndicator from "./LoadingIndicator"
import { UserContext } from "../UserContext.jsx";

function LoginForm({ route, method }) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const navigate = useNavigate();
    const { setUser } = useContext(UserContext)

    const name = method === "login" ? "Login" : "Register";

    const handleSubmit = async (e) => {
        setLoading(true);
        setError("");
        e.preventDefault();

        if (!username) {
            setError("Username can't be empty.");
            setLoading(false);
            return;
        }
        if (!password) {
            setError("Password can't be empty.");
            setLoading(false);
            return;
        }

        try {
            const res = await api.post(route, { username, password })
            if (method === "login") {
                // Save JWT tokens to localStorage
                localStorage.setItem(ACCESS_TOKEN, res.data.access);
                localStorage.setItem(REFRESH_TOKEN, res.data.refresh);

                // Set the default Authorization header for future requests
                api.defaults.headers.common['Authorization'] = `Bearer ${res.data.access}`;

                // Fetch user info from backend
                const userRes = await api.get('/api/auth/user/');
                setUser(userRes.data);             
                localStorage.setItem('user', JSON.stringify(userRes.data));
                
                navigate("/")   // Navigate to Home after login
            } else {
                navigate("/login")  // After registration go to login page
            }
        } catch (error) {
            if (error.response) {
                if (error.response.status === 401) {
                    setError("Invalid username or password.");
                } else {
                    setError("Something went wrong. Please try again.");
                }
            } else if (error.request) {
                // Request was made but no response received
                setError("Server unreachable. Please check your network connection.");
            } else if (error.code === 'ECONNABORTED') {
                // Request timeout
                setError("Request timed out. Please try again.");
            } else {
                // Other errors
                setError("An unexpected error occurred. Please try again.");
            }
        } finally {
            setLoading(false)
        }
    };

    return (
        <form onSubmit={handleSubmit} className="login-form-container">
            <h1>Extended Lactation Dashboard</h1>
            {error && <div className="error-message">{error}</div>}
            <input
                className="login-form-input"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Username"
            />
            <input
                className="login-form-input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
            />
            {loading && <LoadingIndicator />}
            <button className="login-form-button" type="submit">
                Login
            </button>

            {/* Add link to registration page */}
            {method == "login" && (
                <p>
                    Don't have an account? <Link to="/register" className="register-link">Register here</Link>
                </p>
            )}
        </form>
    );
}

export default LoginForm
