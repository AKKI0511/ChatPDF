// Register.js

import React from "react";
import { useNavigate } from "react-router-dom";
import Form from "../components/Form";
import "../styles/Register.css";

function Register() {
    const navigate = useNavigate();

    const login = () => {
        navigate("/login");
    };

    return (
        <div className="register-container">
            <div className="register-content">
                <h1>Register for ChatPDF</h1>
                <Form route="/api/chatbot/user/register/" method="register" />
                <div>
                    Already have an account? Click <button className="register-btn" onClick={login}>here</button> to Login!
                </div>
            </div>
        </div>
    );
}

export default Register;
