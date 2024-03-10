import { Navigate } from 'react-router-dom';
import { useContext } from 'react';
import { AuthContext } from '../Context/AuthContext';

const AuthRoute = ({ children }) => {
  const { authenticated, userId } = useContext(AuthContext);

  return (authenticated && userId) ? children : <Navigate replace to="/login" />;
};

export default AuthRoute;
