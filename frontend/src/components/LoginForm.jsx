// src/components/LoginForm.jsx
import React, { useState } from "react";

const LoginForm = () => {
  const [emailOrUsername, setEmailOrUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: emailOrUsername,
          password,
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        alert(`Error: ${errData.message || "Unable to login"}`);
      } else {
        const data = await response.json();
        alert(`Login successful: ${data?.message || ""}`);
      }
    } catch (error) {
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
