import React, { useState, useEffect, useContext, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../Context/AuthContext';
import axios from 'axios';
import './Chatbot.css';

const Chatbot = () => {
    const { authenticated, logout, userId } = useContext(AuthContext);
    const navigate = useNavigate();

    const [message, setMessage] = useState('');
    const [chatHistory, setChatHistory] = useState([]);
    const [errorMsg, setErrorMsg] = useState(null);

    const sendInitialBotMessage = useCallback(async () => {
        try {
            const response = await axios.post(`http://localhost:8000/api/interact_with_chatbot/`, {
                user_input: "start",
                user_id: String(userId)
            });

            if (Array.isArray(response.data.response)) {
                const botMessages = response.data.response.map(botMsg => ({
                    content: botMsg,
                    sender: 'bot'
                }));
                setChatHistory(prev => [...prev, ...botMessages]);
            } else {
                console.error("Response from backend is not an array:", response.data.response);
            }
        } catch (error) {
            console.log('Error Details:', error.response);
            // handleError(error);
        }
    }, [userId]);

    useEffect(() => {
        const fetchChatHistory = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/chat/user/${userId}`);
                if (Array.isArray(response.data.messages)) {
                    setChatHistory(response.data.messages);
                    
                    // This condition ensures that if there's no previous chat history, a "start" message is sent.
                    if (response.data.messages.length === 0) {
                        sendInitialBotMessage();
                    }
                } else {
                    console.error("chatHistory is not an array:", response.data);
                }
            } catch (error) {
                console.error('Error fetching chat history:', error);
            }
        };

        fetchChatHistory();
    }, [userId, sendInitialBotMessage]);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const clearChatHistory = async () => {
        try {
            // If you want to clear the chat history on your backend, use the below request
            await axios.delete(`http://localhost:8000/clearChat/user/${userId}`);

            // Clear the chat history on frontend
            setChatHistory([]);
        } catch (error) {
            console.error('Error clearing chat history:', error);
        }
    };

    const sendUserMessage = async () => {
        if (!message.trim()) return;

        const userMessage = {
            content: message,
            sender: 'user'
        };

        setChatHistory(prev => [...prev, userMessage]);

        try {
            const response = await axios.post(`http://localhost:8000/api/interact_with_chatbot/`, {
                user_input: message,
                user_id: String(userId)
            });

            if (Array.isArray(response.data.response)) {
                const botMessages = response.data.response.map(botMsg => ({
                    content: botMsg,
                    sender: 'bot'
                }));
                setChatHistory(prev => [...prev, ...botMessages]);
            } else {
                console.error("Response from backend is not an array:", response.data.response);
            }

            setErrorMsg(null);
        } catch (error) {
            handleError(error);
        }

        setMessage('');
    };

    const handleError = (error) => {
        setErrorMsg('An error occurred while fetching a response from the chatbot. Please try again later.');
    }


    const deleteMessage = async (messageId) => {
        try {
            await axios.delete(`http://localhost:8000/chat/${userId}/${messageId}`);
            setChatHistory(prev => prev.filter(msg => msg.id !== messageId));
        } catch (error) {
            console.error('Error deleting message:', error);
        }
    };

    return (
        <div className="chat-container">
            <nav>
                <div className="nav-item">
                    {authenticated ? (
                        <button onClick={handleLogout} className="nav-link">Logout</button>
                    ) : (
                        <Link to="/login" className="nav-link">Login</Link>
                    )}
                </div>
                <div className="nav-item">
                    <Link to="/profile" className="nav-link">Profile</Link>
                </div>
            </nav>

            <div className="chat-input">
                <input 
                    type="text" 
                    value={message} 
                    onChange={(e) => setMessage(e.target.value)} 
                    placeholder="Type a message..."
                />
                <button onClick={sendUserMessage}>Send</button>
            </div>

            <div className="chat-box">
            {chatHistory.map((msg, index) => (
                    <div key={index} className={msg.sender}>
                        {msg.content}
                        {msg.sender === 'user' && msg.id && <button onClick={() => deleteMessage(msg.id)}>Delete</button>}
                    </div>
                ))}
                {chatHistory.length > 0 && <button onClick={clearChatHistory} className="clear-chat">Clear Chat</button>}
            </div>

            <div className="visualization">
                Visualization content goes here
            </div>

            {errorMsg && <p className="error-message">{errorMsg}</p>}
        </div>
    );
}

export default Chatbot;