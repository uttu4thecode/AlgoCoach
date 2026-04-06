import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import { isLoggedIn } from './services/authService';

function ProtectedRoute({ children }) {
  return isLoggedIn() ? children : <Navigate replace to="/login" />;
}

function PublicRoute({ children }) {
  return isLoggedIn() ? <Navigate replace to="/" /> : children;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          }
        />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate replace to={isLoggedIn() ? '/' : '/login'} />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
