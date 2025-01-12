// src/App.js
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import React, { useState } from "react";
import Header from "./components/Header";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";

function App() {
  const [user, setUser] = useState(null);

  return (
    <Router>
      <Header />
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />

        {/* Pass setUser to LoginPage */}
        <Route path="/login" element={<LoginPage setUser={setUser} />} />

        {/* Pass setUser to RegisterPage */}
        <Route path="/register" element={<RegisterPage setUser={setUser} />} />

        {/* Pass user to DashboardPage */}
        <Route
          path="/dashboard"
          element={user ? <DashboardPage user={user} /> : <Navigate to="/login" />}
        />
      </Routes>
    </Router>
  );
}

export default App;
