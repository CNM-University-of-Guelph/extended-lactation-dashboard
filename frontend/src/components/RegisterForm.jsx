import { useState } from "react"
import api from "../api"
import { useNavigate, Link } from "react-router-dom"
import "../styles/RegisterForm.css"
import LoadingIndicator from "./LoadingIndicator"

function RegisterForm({ route, method }) {
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        setLoading(true);
        e.preventDefault();
        // Clear previous errors
        setError("");

        if (password !== confirmPassword) {
            setError("Passwords do not match!");
            setLoading(false);
            return;
        }

        try {
            const res = await api.post(route, { 
                username, 
                email, 
                password,
                confirmPassword
            });
            alert("User registered successfully!")
            navigate("/login")

        } catch (error) {
            alert(error)
        } finally {
            setLoading(false)
        }
    };

    return (
        <form onSubmit={handleSubmit} className="register-form-container">
            <h1>Register</h1>
            <input
                className="register-form-input"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Username"
                required
            />
            <input
                className="register-form-input"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email"
                required
            />
            <input
                className="register-form-input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                required
            />
            <input
                className="register-form-input"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)} 
                placeholder="Confirm Password"
                required
            />
            {loading && <LoadingIndicator />}
            <button className="register-form-button" type="submit">
                Register
            </button>

            {method == "register" && (
                <p>
                    Already have an account? <Link to="/login">Login here</Link>
                </p>
            )}
        </form>
    );
}

export default RegisterForm;