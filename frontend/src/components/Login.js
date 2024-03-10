import React, { useState, useContext } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../Context/AuthContext';

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const { login } = useContext(AuthContext);

  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      const response = await axios.post("http://localhost:8000/api/login",
        new URLSearchParams({ username: email, password }),
        { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
      );

      console.log(response.data);
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('userId', response.data.id); // Store user id in local storage
      login(response.data.id); // Call the login function with user id
      navigate('/');

    } catch (error) {
      console.error(error);
      if (error.response) {
        console.log(error.response.data);
        console.log(error.response.status);
        console.log(error.response.headers);
        if (error.response.data.detail) {
          console.log("Error details: ");
          error.response.data.detail.forEach((err, index) => {
            console.log(`Error ${index + 1}: `, err);
          });
        }
      } else if (error.request) {
        console.log(error.request);
      } else {
        console.log('Error', error.message);
      }
      setErrorMessage("An error occurred while trying to log in.");
    }
  }

  return (
    <div>
      {errorMessage && <p>{errorMessage}</p>}
      <form onSubmit={handleSubmit}>
        <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
        <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required />
        <button type="submit">Log In</button>
      </form>
    </div>
  );
}

export default Login;
