import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const RegisterForm = ({ setUser }) => {
  const [name, setName] = useState("");
  const [occupation, setOccupation] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

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
        const errData = await response.json();
        alert(`Error: ${errData.detail || "Unable to register"}`);
      } else {
        const data = await response.json();
        alert("Registration successful!");
        setUser({ userId: data.user_id, name: data.name }); // Save user details
        navigate("/dashboard"); // Redirect to dashboard
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
