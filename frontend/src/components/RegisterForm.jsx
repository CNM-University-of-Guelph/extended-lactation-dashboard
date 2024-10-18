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

    const [error, setError] = useState(""); // General error message
    const [usernameError, setUsernameError] = useState(""); // Specific username error
    const [emailError, setEmailError] = useState(""); // Specific email error
    const [passwordError, setPasswordError] = useState(""); // Password mismatch error


    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        setUsernameError(""); 
        setEmailError(""); 
        setPasswordError("");

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

        // } catch (error) {
        //     alert(error)
        // } finally {
        //     setLoading(false)
        // }

        } catch (error) {
            // Handle specific backend errors
            if (error.response && error.response.data) {
                const errData = error.response.data;
                
                // Check for specific errors returned from the server
                if (errData.username) {
                    setUsernameError(errData.username); // Set username error message
                }
                if (errData.email) {
                    setEmailError(errData.email); // Set email error message
                }
                if (errData.non_field_errors) {
                    setError(errData.non_field_errors[0]); // General error message
                }
            } else {
                setError("An unexpected error occurred. Please try again.");
            }
        } finally {
            setLoading(false);
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
            {usernameError && <p className="error-message">{usernameError}</p>} {/* Display username error */}

            <input
                className="register-form-input"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email"
                required
            />
            {emailError && <p className="error-message">{emailError}</p>} {/* Display email error */}

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
            {passwordError && <p className="error-message">{passwordError}</p>} {/* Display password mismatch error */}

            {error && <p className="error-message">{error}</p>} {/* Display general error */}

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
