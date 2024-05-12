// BackButton.jsx

import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/BackButton.css";

function BackButton() {
    const navigate = useNavigate(); // Use useNavigate instead of useHistory

    const goBack = () => {
        navigate(-1); // Go back one step in history
    };

    return (
        <button className="back-button" onClick={goBack}>
            <span>&#8592;</span> {/* Unicode arrow symbol */}
        </button>
    );
}

export default BackButton;
