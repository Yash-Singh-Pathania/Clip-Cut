import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const LoginForm = ({ setUser }) => {
  const [emailOrUsername, setEmailOrUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: emailOrUsername,
          password,
        }),
      });

      // Handle response status
      if (!response.ok) {
        const errData = await response.json();
        alert(`Error: ${errData.detail || "Unable to login"}`);
        return; // Stop execution on error
      }

      // Handle success response
      const data = await response.json();
      alert("Login successful!");
      setUser({ userId: data.user_id, name: data.name }); // Save user info
      navigate("/dashboard"); // Redirect to the dashboard

    } catch (error) {
      console.error("Login error:", error); // Log for debugging
      alert("An error occurred. Please try again.");
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <label htmlFor="emailOrUsername">Email or Username</label>
      <input
        id="emailOrUsername"
        type="text"
        value={emailOrUsername}
        onChange={(e) => setEmailOrUsername(e.target.value)}
        required
      />

      <label htmlFor="password">Password</label>
      <input
        id="password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />

      <button type="submit">Sign In</button>
    </form>
  );
};

export default LoginForm;
