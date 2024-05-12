import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import './styles/App.css';
import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";
import NotFound from "./pages/NotFound";
import ProtectedRoute from "./components/ProtectedRoute";
import CreatePDF from "./pages/Createpdf";
import EditPDF from "./pages/Editpdf";

function Logout() {
  localStorage.clear();
  return <Navigate to="/login" />;
}

function RegisterAndLogout() {
  localStorage.clear();
  return <Register />;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/logout" element={<Logout />} />
        <Route path="/register" element={<RegisterAndLogout />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
        <Route
          path="/generate-pdf"
          element={
            <ProtectedRoute>
              <CreatePDF />
            </ProtectedRoute>
          }
        />
        <Route
          path="/edit-pdf"
          element={
            <ProtectedRoute>
              <EditPDF />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
