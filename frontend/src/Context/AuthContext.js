import { createContext, useState, useEffect, useCallback } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [authenticated, setAuthenticated] = useState(false);
  const [userId, setUserId] = useState(null);
  const [logoutTimer, setLogoutTimer] = useState(null);

  const logout = useCallback(() => {
    setAuthenticated(false);
    setUserId(null);
    localStorage.removeItem('userId'); // Remove user id from local storage
    localStorage.removeItem('token'); // Remove token from local storage
  }, []);

  const startLogoutTimer = useCallback(() => {
    // Set a new timer
    const timer = setTimeout(() => {
      logout();
    }, 10 * 60 * 1000); // 10 minutes

    setLogoutTimer(timer);
    return timer; // Return the timer so it can be cleared elsewhere
  }, [logout]);

  const handleUserActivity = useCallback(() => {
    clearTimeout(logoutTimer);
    startLogoutTimer();
  }, [startLogoutTimer, logoutTimer]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const id = localStorage.getItem('userId');
    if (token && id) {
      setAuthenticated(true);
      setUserId(id);
      startLogoutTimer(); // Start the logout timer when the user is authenticated
    }
  }, [startLogoutTimer]);

  useEffect(() => {
    // Set up event listeners for user activity
    window.addEventListener('mousemove', handleUserActivity);
    window.addEventListener('mousedown', handleUserActivity);
    window.addEventListener('keydown', handleUserActivity);
    window.addEventListener('scroll', handleUserActivity);

    // Clean up event listeners
    return () => {
      window.removeEventListener('mousemove', handleUserActivity);
      window.removeEventListener('mousedown', handleUserActivity);
      window.removeEventListener('keydown', handleUserActivity);
      window.removeEventListener('scroll', handleUserActivity);
    };
  }, [handleUserActivity]);

  const value = {
    authenticated,
    userId,
    login: (id) => {
      setAuthenticated(true);
      setUserId(id);
      localStorage.setItem('userId', id); // Save user id in local storage
      startLogoutTimer(); // Start the logout timer when the user logs in
    },
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
};
