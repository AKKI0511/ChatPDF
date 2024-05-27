import BackButton from "../components/BackButton";
import React, { useState, useEffect, useRef } from 'react';
import "../styles/Createpdf.css";
import api from "../Api";

const BASE_URL = 'http://127.0.0.1:8000';

function CreatePDF() {
    const [description, setDescription] = useState('');
    const [conversation, setConversation] = useState([]);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const textareaRef = useRef(null);

    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
        }
    }, [description]);

    useEffect(() => {
        // Fetch existing conversations when the component mounts
        api.get('/api/chatbot/conversations/')
            .then(response => {
                const conversations = response.data.map(convo => {
                    return convo.pdfs.map(pdf => ({
                        user: pdf.description,
                        ai: `${BASE_URL}${pdf.pdf_url}`,
                    }));
                }).flat();
                setConversation(conversations);
            })
            .catch(error => console.error('Error fetching conversations:', error));
    }, []);

    const handleInputChange = (e) => {
        setDescription(e.target.value);
        setError('');
    };

    const generatePdf = () => {
        if (description.trim() === '') {
            setError('Description cannot be empty');
            return;
        }

        setLoading(true);
        setError('');

        // Add the user input to the conversation
        const newConversationEntry = { user: description, ai: '' };

        api.post('/api/chatbot/generate-pdf/', { description })
            .then(response => {
                setConversation(prev => [...prev, newConversationEntry]);
                setDescription('');        
                const updatedConversationEntry = { ...newConversationEntry, ai: `${BASE_URL}${response.data.pdfUrl}` };
                setConversation(prev => {
                    const updatedConversation = [...prev];
                    updatedConversation[updatedConversation.length - 1] = updatedConversationEntry;
                    return updatedConversation;
                });
                setLoading(false);
            })
            .catch(error => {
                console.error('Error:', error);
                setError('An error occurred while generating the PDF. Please try again.');
                setLoading(false);
            });
    };

    return (
        <div className="pdf-generation-container">
            <BackButton /> {/* BackButton component */}
            <h2>Describe Your PDF</h2>
            <textarea
                ref={textareaRef}
                className="description-textarea"
                value={description}
                onChange={handleInputChange}
                placeholder="Enter description here..."
            />
            {error && <div className="error-message">{error}</div>}
            <button onClick={generatePdf} disabled={loading}>
                {loading ? 'Generating PDF...' : 'Generate PDF'}
            </button>
            <div className="conversation-history">
                {conversation.map((entry, index) => (
                    <div key={index} className="conversation-entry">
                        <div className="user-input">
                            <strong>User:</strong> {entry.user}
                        </div>
                        {entry.ai && (
                            <div className="ai-response">
                                <strong>AI:</strong>
                                <div className="pdf-preview">
                                    <a href={entry.ai} download>Download PDF</a>
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default CreatePDF;
