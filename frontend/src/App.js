import React, { useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthContext } from './Context/AuthContext';
import AuthRoute from "./components/AuthRoute";
import Signup from './components/Signup';
import Login from './components/Login';
import Homepage from './components/Homepage';
import DefineFeatures from './components/DefineFeatures';
import ImportCSV from './components/ImportCSV';
import Chatbot from './components/Chatbot';
import './App.css';

const App = () => {
  const { authenticated, userId } = useContext(AuthContext);
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/signup" element={<Signup />} />
        <Route path="/login" element={<Login />} />
        <Route path="/import-csv" element={<AuthRoute><ImportCSV userId={userId} /></AuthRoute>} />
        <Route path="/define-features" element={<AuthRoute><DefineFeatures /></AuthRoute>} />
        <Route path="/user/:userId" element={<AuthRoute><Homepage /></AuthRoute>} />
        <Route path="/chatbot" element={<AuthRoute><Chatbot /></AuthRoute>} /> {/* New chatbot route */}
        <Route path="/" element={authenticated ? <Navigate to={`/user/${userId}`} /> : <Homepage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;