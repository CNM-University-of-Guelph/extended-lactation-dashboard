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
    const navigate = useNavigate();
    const { setUser } = useContext(UserContext)

    const name = method === "login" ? "Login" : "Register";

    const handleSubmit = async (e) => {
        setLoading(true);
        e.preventDefault();

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
            alert(error)
        } finally {
            setLoading(false)
        }
    };

    return (
        <form onSubmit={handleSubmit} className="login-form-container">
            <h1>{name}</h1>
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
                {name}
            </button>

            {/* Add link to registration page */}
            {method == "login" && (
                <p>
                    Don't have an account? <Link to="/register">Register here</Link>
                </p>
            )}
        </form>
    );
}

export default LoginForm