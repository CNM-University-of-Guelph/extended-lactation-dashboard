import LoginForm from "../components/LoginForm";
import "../styles/Login.css";

function Login() {
    return (
    <div className="login-page">
      <LoginForm route="/api/token/" method="login"/>
    </div>

  );
};

export default Login;