import Form from "../components/Form";
import { useNavigate } from "react-router-dom";
import "../styles/Login.css"

function Login() {
    const navigate = useNavigate();

    const register = () => {
        navigate("/register");
    };
    return (
        <div className="login-container">
            <div className="login-content">
                <h1>Welcome to ChatPDF</h1>
                <Form route="/api/token/" method="login" />
                <div>
                    Don't have an account? <button className="register-btn" onClick={register}>Register</button>
                </div>
            </div>
        </div>
    );
}

export default Login;
