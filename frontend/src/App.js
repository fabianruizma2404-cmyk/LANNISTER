import React from "react";
import { HashRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Register from "./pages/Register";
import WhatsAppButton from "./components/WhatsAppButton.js";

const BACKEND_URL = "https://lannister-production.up.railway.app";

function PrivateRoute({ children }) {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/login" />;
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login backend={BACKEND_URL} />} />
        <Route path="/registro" element={<Register backend={BACKEND_URL} />} />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
      <WhatsAppButton />
    </Router>
  );
}
