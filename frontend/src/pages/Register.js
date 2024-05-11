import Form from "../components/Form";
import { useNavigate } from "react-router-dom";
import "../styles/Register.css"

function Register() {
    const navigate = useNavigate();

    const login = () => {
        navigate("/login");
    };
    return (
        <div className="register-container"> {/* Add the register-container class */}
            <div className="register-content"> {/* Add the register-content class */}
                <Form route="/api/chatbot/user/register/" method="register" />
            </div>
            <p className="register-link" onClick={login}>click here to Login!</p> {/* Add the register-link class */}
        </div>
    );
}

export default Register;
