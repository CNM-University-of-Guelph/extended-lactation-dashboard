import { useNavigate, NavLink } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import "../styles/Navbar.css"

function Navbar() {
    const navigate = useNavigate();

    const handleLogout = () => {
        // Clear tokens from localStorage
        localStorage.removeItem(ACCESS_TOKEN);
        localStorage.removeItem(REFRESH_TOKEN);

        navigate("/login");
    };

    return (
        <header className="header">
            <nav>
                <ul className="nav-list">
                    <li>
                        <NavLink to="/" className={({ isActive }) => isActive ? "active-link" : ""}>
                            Home
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="/profile" className={({ isActive }) => isActive ? "active-link" : ""}>
                            Profile
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="/predictions" className={({ isActive }) => isActive ? "active-link" : ""}>
                            Predictions
                        </NavLink>
                    </li>
                    <li>
                        <NavLink to="/help" className={({ isActive }) => isActive ? "active-link" : ""}>
                            Help
                        </NavLink>
                    </li>
                </ul>
            </nav>
            <button onClick={handleLogout} className="logout-button">
                Logout
            </button>
        </header>
    );
}

export default Navbar;
