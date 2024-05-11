import { Navigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import api from '../Api';
import { ACCESS_TOKEN, REFRESH_TOKEN } from '../constants';
import { useState, useEffect } from 'react';

function ProtectedRoute({ children }) {
    const [isAuthorized, setIsAuthorized] = useState(null);

    useEffect(() => {
        auth().catch(() => setIsAuthorized(false)); // Added semicolon
    }, []);

    const refreshToken = async () => {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN);
        try {
            const res = await api.post("/api/token/refresh/", {
                refresh: refreshToken,
            });
            if (res.status === 200) {
                localStorage.setItem(ACCESS_TOKEN, res.data.access);
                setIsAuthorized(true);
            } else {
                setIsAuthorized(false);
            }
        } catch (error) {
            console.log(error);
            setIsAuthorized(false);
        }
    };
    const auth = async () => {
        const token = localStorage.getItem(ACCESS_TOKEN);
        if (!token) {
            setIsAuthorized(false);
            return;
        }
        const decoded = jwtDecode(token); // Fixed 'jwt-decode' to 'jwtDecode'
        const tokenExpiration = decoded.exp;
        const now = Date.now() / 1000;  /* milisecond to second */
        if (tokenExpiration >= now) {
            setIsAuthorized(true);
        } else {
            await refreshToken();
        }
    };

    if (isAuthorized == null) {
        return <div>Loading...</div>;
    }
    return isAuthorized ? children : <Navigate to='/login' />;
}

export default ProtectedRoute;
