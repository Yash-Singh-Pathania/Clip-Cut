// src/pages/LoginPage.jsx
import React from "react";
import LoginForm from "../components/LoginForm";
import { Link, useNavigate } from "react-router-dom";

const LoginPage = ({ setUser }) => {
  const navigate = useNavigate();

  const handleTestLogin = () => {
    navigate("/dashboard");
  };

  return (
    <div>
      {/* Pass setUser to LoginForm */}
      <LoginForm setUser={setUser} />
      <br />

      <div className="link-container">
        <p>Don’t have an account?</p>
        <Link to="/register">Create one</Link>
      </div>
    </div>
  );
};

export default LoginPage;
