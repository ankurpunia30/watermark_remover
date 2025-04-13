import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ children }) {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    // Store the current path to redirect back after sign in
    localStorage.setItem('redirectAfterSignIn', window.location.pathname);
    return <Navigate to="/signin" replace />;
  }

  return children;
} 