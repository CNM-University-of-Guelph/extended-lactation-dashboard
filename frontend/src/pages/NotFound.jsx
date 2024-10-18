import Navbar from "../components/Navbar";
import "../styles/NotFound.css"

function NotFound() {
    return (
      <div>
        <Navbar />
        <div className="not-found-container">
          <h1 className="not-found-header">404 Not Found</h1>
          <p className="not-found-message">
            Oops! The page you are looking for doesn't exist.
          </p>
          <button
            className="not-found-button"
            onClick={() => window.location.href = "/"} // Redirect to home
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

export default NotFound;
