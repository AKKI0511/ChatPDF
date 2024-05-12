// Home.js

import React from 'react';
import { Link } from 'react-router-dom';
import { FaFileAlt, FaEdit } from 'react-icons/fa';
import '../styles/Home.css';

function Home() {
    return (
        <div className="dashboard-container">
            <div className="logout-container">
                <Link to="/logout" className="logout-button">Logout</Link>
            </div>
            <h1>Welcome to ChatPDF</h1>
            <div className="cards-container">
                <Link to="/generate-pdf" className="card">
                    <div>
                        <FaFileAlt size={50} className='icon' /> {/* Icon representing PDF generation */}
                        <h2>Generate New PDF</h2>
                        <p>Create a new PDF based on text input</p>
                    </div>
                </Link>
                <Link to="/edit-pdf" className="card">
                    <div>
                        <FaEdit size={50} className='icon' /> {/* Icon representing PDF editing */}
                        <h2>Edit PDF</h2>
                        <p>Edit an existing PDF file</p>
                    </div>
                </Link>
            </div>
        </div>
    );
}

export default Home;
