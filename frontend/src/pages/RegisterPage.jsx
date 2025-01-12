// src/pages/RegisterPage.jsx
import React from "react";
import RegisterForm from "../components/RegisterForm";
import { Link } from "react-router-dom";

const RegisterPage = ({ setUser }) => {
  return (
    <div>
      {/* Forward setUser to RegisterForm */}
      <RegisterForm setUser={setUser} />
      <div className="link-container">
        <p>Already have an account?</p>
        <Link to="/login">Sign In</Link>
      </div>
    </div>
  );
};

export default RegisterPage;
