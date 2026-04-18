import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";

export default function App() {
  const token = localStorage.getItem("token");

  return (
    <BrowserRouter>
      <Routes>

        {/* 🏠 Landing */}
        <Route path="/" element={<Home />} />

        {/* 🔐 Auth */}
        <Route path="/login" element={<Login />} />
        <Route path="/registro" element={<Register />} />

        {/* 🔒 Protegido */}
        <Route
          path="/app"
          element={token ? <Dashboard /> : <Navigate to="/login" />}
        />

      </Routes>
    </BrowserRouter>
  );
}
