// src/components/RegisterForm.jsx
import React, { useState } from "react";

const RegisterForm = () => {
  const [name, setName] = useState("");
  const [occupation, setOccupation] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleRegister = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://127.0.0.1:8000/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          email,
          occupation,
          password,
        }),
      });

      if (!response.ok) {
        // For example, if a 4xx or 5xx response:
        const errData = await response.json();
        alert(`Error: ${errData.message || "Unable to register"}`);
      } else {
        const data = await response.json();
        alert(`Registration successful: ${data?.message || ""}`);
      }
    } catch (error) {
      alert("An error occurred. Please try again.");
    }
  };

  return (
    <form onSubmit={handleRegister}>
      <label htmlFor="name">Name</label>
      <input
        id="name"
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
      />

      <label htmlFor="occupation">Occupation</label>
      <input
        id="occupation"
        type="text"
        value={occupation}
        onChange={(e) => setOccupation(e.target.value)}
        required
      />

      <label htmlFor="email">Email</label>
      <input
        id="email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
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

      <button type="submit">Register</button>
    </form>
  );
};

export default RegisterForm;
