import React, { useState, useEffect, useRef } from 'react';
import { Button, Form, Alert, Container, Spinner } from 'react-bootstrap';
import BackButton from "../components/BackButton";
import "../styles/Createpdf.css";
import api from "../Api";
import aiImage from '../assets/ai_image_2.jpg';

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
                setConversation(conversations.reverse());
            })
            .catch(error => console.error('Error fetching conversations:', error));
    }, []);

    const handleInputChange = (e) => {
        setDescription(e.target.value);
        setError('');
    };

    const generatePdf = async () => {
        if (description.trim() === '') {
            setError('Description cannot be empty');
            return;
        }

        setLoading(true);
        setError('');

        // Add the user input to the conversation
        const newConversationEntry = { user: description, ai: 'loading' };
        setConversation(prev => [{ ...newConversationEntry }, ...prev]);
        setDescription('');

        try {
            const response = await api.post('/api/chatbot/generate-pdf/', { description });
            const pdfUrl = `${BASE_URL}${response.data.pdfUrl}`;
            const updatedConversationEntry = { ...newConversationEntry, ai: pdfUrl };
            setConversation(prev => {
                const updatedConversation = [...prev];
                updatedConversation[0] = updatedConversationEntry;
                return updatedConversation;
            });
        } catch (error) {
            console.error('Error:', error);
            setError('An error occurred while generating the PDF. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container className="pdf-generation-container mt-4">
            <BackButton /> {/* BackButton component */}
            <h2 className="text-center text-primary mb-4">Describe Your PDF</h2>
            <Form>
                <Form.Group controlId="description" className="textarea-container position-relative">
                    <div className='textarea-wrapper'>
                        <Form.Control
                            as="textarea"
                            ref={textareaRef}
                            className="description-textarea"
                            value={description}
                            onChange={handleInputChange}
                            placeholder="Enter description here..."
                            rows={2}
                        />
                        <Button
                            variant="primary"
                            className="textarea-button"
                            onClick={generatePdf}
                            disabled={loading}
                        >
                            {loading ? <Spinner as="span" animation="border" size="sm" /> : '↓'}
                        </Button>
                    </div>
                </Form.Group>
            </Form>
            {error && <Alert variant="danger" className="error-message">{error}</Alert>}
            <div className="conversation-history mt-4">
                {conversation.map((entry, index) => (
                    <div key={index} className="conversation-entry">
                        {entry.ai && (
                            <div className="ai-response">
                                <img src={aiImage} alt="AI" className="ai-avatar" />
                                <div className="pdf-preview">
                                    {entry.ai === 'loading' ? (
                                        <div className="loading-container">
                                            <div className="loader"></div>
                                        </div>
                                    ) : (
                                        <>
                                            <a href={entry.ai} target="_blank" rel="noopener noreferrer">View PDF</a>
                                            <a href={entry.ai} download>Download PDF</a>
                                        </>
                                    )}
                                </div>
                            </div>
                        )}
                        <div className="user-input">
                            {entry.user}
                        </div>
                    </div>
                ))}
            </div>
        </Container>
    );
}

export default CreatePDF;
