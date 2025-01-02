// src/pages/LoginPage.jsx
import React from "react";
import LoginForm from "../components/LoginForm";
import { Link } from "react-router-dom";

const LoginPage = () => {
  return (
    <div className="auth-container">
      <h2>Sign In</h2>
      <LoginForm />
      <div className="link-container">
        <p>Don’t have an account?</p>
        <Link to="/register">Create one</Link>
      </div>
    </div>
  );
};

export default LoginPage;
