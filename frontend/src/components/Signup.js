import React, { useState } from 'react';
import axios from 'axios';

const Signup = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [repeatPassword, setRepeatPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [signupSuccess, setSignupSuccess] = useState(false); 
  const [errorMessage, setErrorMessage] = useState(""); 

  const isValidEmail = (email) => {
    const regex = /^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]{2,7}$/;
    return regex.test(email);
  }

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!isValidEmail(email)) {
      setErrorMessage("Please enter a valid email.");
      return;
    }

    if (password !== repeatPassword) {
      setErrorMessage("Passwords do not match!");
      return;
    }

    const newUser = {
        email,
        password,
        repeat_password: password,
        first_name: firstName,
        last_name: lastName,
        company_name: companyName
    };

    try {
        const response = await axios.post("http://localhost:8000/api/signup", newUser);
        console.log(response.data);
        setSignupSuccess(true); 
        setErrorMessage(""); // Clear any previous error messages
    } catch (err) {
        console.error(err);
        if (err.response) {
            // client received an error response (5xx, 4xx)
            setErrorMessage(err.response.data.detail);
        } else if (err.request) {
            // client never received a response, or request never left
            setErrorMessage("Network error. Please try again.");
        } else {
            // anything else
            setErrorMessage("An error occurred. Please try again.");
        }
    }
};

  return (
    <div>
      {errorMessage && <p>{errorMessage}</p>} 
      {signupSuccess ? <p>Your account has been created successfully!</p> : null} 
      <form onSubmit={handleSubmit}>
        <input type="text" placeholder="First Name" value={firstName} onChange={e => setFirstName(e.target.value)} required />
        <input type="text" placeholder="Last Name" value={lastName} onChange={e => setLastName(e.target.value)} required />
        <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
        <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required />
        <input type="password" placeholder="Repeat Password" value={repeatPassword} onChange={e => setRepeatPassword(e.target.value)} required />
        <input type="text" placeholder="Company Name" value={companyName} onChange={e => setCompanyName(e.target.value)} required />
        <button type="submit">Sign Up</button>
      </form>
    </div>
  );
}

export default Signup;
