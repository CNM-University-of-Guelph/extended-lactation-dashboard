import { useNavigate, Link } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import "../styles/Header.css"

function Header() {
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
                        <Link to="/">Home</Link>
                    </li>
                    <li>
                        <Link to="/about">About</Link>
                    </li>
                    <li>
                        <Link to="/contact">Contact</Link>
                    </li>
                </ul>
            </nav>
            <button onClick={handleLogout} className="logout-button">
                Logout
            </button>
        </header>
    );
}

export default Header;
