import RegisterForm from "../components/RegisterForm";
import "../styles/Register.css";

function Register() {
    return (
        <div className="register-page">
          <RegisterForm route="/api/user/register/" method="register"/>
        </div>

  );
};

export default Register;