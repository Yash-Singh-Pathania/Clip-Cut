import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const RegisterForm = ({ setUser }) => {
  const [name, setName] = useState("");
  const [occupation, setOccupation] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // Modal state for showing messages
  const [modal, setModal] = useState({
    open: false,
    message: "",
    onOk: null,
    type: "info", // 'info' for success, 'error' for failure
  });

  const navigate = useNavigate();

  const closeModal = () => {
    setModal({ ...modal, open: false, message: "", onOk: null });
  };

  const handleRegister = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch(`${process.env.REACT_APP_USER_SERVICE_URL}/register`, {
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
        // Open modal with error message
        setModal({
          open: true,
          message: `Error: ${errData.detail || "Unable to register"}`,
          onOk: closeModal,
          type: "error",
        });
      } else {
        const data = await response.json();
        // On success, open modal with success message and navigate on OK
        setModal({
          open: true,
          message: "Registration successful! Press OK to confirm.",
          onOk: () => {
            closeModal();
            setUser({ userId: data.user_id, name: data.name });
            navigate("/dashboard");
          },
          type: "info",
        });
      }
    } catch (error) {
      setModal({
        open: true,
        message: "An error occurred. Please try again.",
        onOk: closeModal,
        type: "error",
      });
    }
  };

  return (
    <>
      {/* Wrap form in auth-container div so index.css rules apply */}
      <div className="auth-container">
        <h2>Register</h2>
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
          <select
            id="occupation"
            value={occupation}
            onChange={(e) => setOccupation(e.target.value)}
            required
          >
            <option value="">Select Occupation</option>
            <option value="working">Working</option>
            <option value="student">Student</option>
            <option value="other">Other</option>
          </select>

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

          <button type="submit">
            Register
          </button>
        </form>
      </div>

      {/* Modal */}
      {modal.open && (
        <div className="modal-overlay">
          <div className="modal-content">
            <p>{modal.message}</p>
            <div className="modal-buttons">
              <button onClick={modal.onOk}>OK</button>
              {modal.type !== "info" && (
                <button onClick={closeModal}>Close</button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default RegisterForm;
