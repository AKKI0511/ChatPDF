import Form from "../components/Form";
import { useNavigate } from "react-router-dom";
import "../styles/Login.css"

function Login() {
    const navigate = useNavigate();

    const register = () => {
        navigate("/register");
    };
    return (
        <div className="login-container"> {/* Add the login-container class */}
            <Form route="/api/token/" method="login" />
            <div className="button-container"> {/* Add the button-container class */}
                <button className="form-btn" onClick={register}>Register</button>
            </div>
        </div>
    );
}

export default Login;
