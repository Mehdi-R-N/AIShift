// Homepage.js
import React, { useState, useEffect, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { AuthContext } from '../Context/AuthContext';
import './Homepage.css';

const Homepage = () => {
  const { userId, authenticated, logout } = useContext(AuthContext);
  const [userName, setUserName] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/user/${userId}`);
        setUserName(response.data.name);
      } catch (error) {
        console.error(error);
      }
    };

    if (userId && authenticated) {
      fetchUser();
    } else {
      navigate('/login');
    }
  }, [userId, authenticated, navigate]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div>
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
      <div className="main-content">
        <h1>Welcome to My Web App, {userName}</h1>
        <Link to="/Dashboard" id="Dashboard" className="circle-button">Dashboard</Link>
        <Link to="/import-csv" id="import-csv" className="circle-button">Import CSV</Link>
        <Link to="/chatbot" id="chatbot" className="circle-button">Chatbot</Link> {/* Replaced Dashboard with Chatbot */}
      </div>
    </div>
  );
};

export default Homepage;