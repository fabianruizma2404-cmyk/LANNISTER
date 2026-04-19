import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";

import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Register from "./pages/Register";

const BACKEND_URL = "https://lannister-production.up.railway.app";

// 🔐 PROTEGER RUTA
function PrivateRoute({ children }) {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/login" />;
}

export default function App() {
  return (
    <Router>
      <Routes>

        {/* 🏠 HOME */}
        <Route path="/" element={<Home />} />

        {/* 🔐 LOGIN */}
        <Route path="/login" element={<Login backend={BACKEND_URL} />} />

        {/* 📝 REGISTER */}
        <Route path="/registro" element={<Register backend={BACKEND_URL} />} />

        {/* 📊 DASHBOARD PROTEGIDO */}
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }
        />

        {/* 🔁 REDIRECCIÓN POR DEFECTO */}
        <Route path="*" element={<Navigate to="/" />} />

      </Routes>
    </Router>
  );
}
