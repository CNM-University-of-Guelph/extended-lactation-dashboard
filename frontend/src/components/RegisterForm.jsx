import { useState } from "react"
import zxcvbn from "zxcvbn";
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
    const [passwordStrengthScore, setPasswordStrengthScore] = useState(0);

    const navigate = useNavigate();

    const evaluatePasswordStrength = (password) => {
        if (!password) {
            return { score: 0 }; // No password input
        }
        const evaluation = zxcvbn(password);
        return evaluation;
    };

    const handlePasswordChange = (e) => {
        const newPassword = e.target.value;
        setPassword(newPassword);

        // Evaluate password strength using zxcvbn and update score
        const evaluation = evaluatePasswordStrength(newPassword);
        setPasswordStrengthScore(evaluation.score);
    };

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

        const userData = { 
            username, 
            email, 
            password,
            confirmPassword  
        };

        console.log('Sending registration data:', userData);

        try {
            const res = await api.post(route, userData);
            console.log('Registration response:', res.data);
            navigate("/login")

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

    const getPasswordStrengthLabel = (score) => {
        switch (score) {
            case 0:
                return "Very Weak";
            case 1:
                return "Weak";
            case 2:
                return "Fair";
            case 3:
                return "Good";
            case 4:
                return "Strong";
            default:
                return "";
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
                onChange={handlePasswordChange}
                placeholder="Password"
                required
            />

            {password && (
                <div className={`password-strength strength-${passwordStrengthScore}`}>
                    <p>Password Strength: {getPasswordStrengthLabel(passwordStrengthScore)}</p>
                    <div className="strength-bar">
                        <div
                            className="strength-bar-fill"
                            style={{
                                width: `${(passwordStrengthScore + 1) * 20}%`,
                                backgroundColor: passwordStrengthScore === 4 ? "#4caf50" : passwordStrengthScore === 3 ? "#ffc107" : "#f44336"
                            }}
                        ></div>
                    </div>
                </div>
            )}

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
                    Already have an account? <Link to="/login" className="login-link">Login here</Link>
                </p>
            )}
        </form>
    );
}

export default RegisterForm;
