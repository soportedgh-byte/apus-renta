import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const AuthContext = createContext(null);

function decodeToken(token) {
  try {
    const payload = token.split('.')[1];
    return JSON.parse(atob(payload));
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('token');
      if (!storedToken) {
        setLoading(false);
        return;
      }

      const decoded = decodeToken(storedToken);
      if (!decoded || (decoded.exp && decoded.exp * 1000 < Date.now())) {
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        setToken(null);
        setLoading(false);
        return;
      }

      try {
        const { data } = await api.get('/auth/me');
        setUser(data.data || data);
        setToken(storedToken);
      } catch {
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = useCallback(async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    const result = response.data.data || response.data;

    // Backend returns: { user, accessToken, refreshToken }
    const accessToken = result.accessToken || result.token;
    const refreshTk = result.refreshToken;
    const userData = result.user;

    if (accessToken) {
      localStorage.setItem('token', accessToken);
    }
    if (refreshTk) {
      localStorage.setItem('refreshToken', refreshTk);
    }

    setToken(accessToken);
    setUser(userData);
    return userData;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    setToken(null);
    setUser(null);
    navigate('/login');
  }, [navigate]);

  const isAuthenticated = !!user && !!token;

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
