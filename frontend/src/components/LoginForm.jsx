import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const LoginForm = ({ setUser }) => {
  const [emailOrUsername, setEmailOrUsername] = useState("");
  const [password, setPassword] = useState("");

  // Modal state for showing messages
  const [modal, setModal] = useState({
    open: false,
    message: "",
    onOk: null,
    type: "info",
  });

  const navigate = useNavigate();

  const closeModal = () => {
    setModal({ ...modal, open: false, message: "", onOk: null });
  };

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch(`${process.env.REACT_APP_USER_SERVICE_URL}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: emailOrUsername,
          password,
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        setModal({
          open: true,
          message: `Error: ${errData.detail || "Unable to login"}`,
          onOk: closeModal,
          type: "error",
        });
      } else {
        const data = await response.json();
        setModal({
          open: true,
          message: "Login successful! Press OK to confirm.",
          onOk: () => {
            closeModal();
            setUser({ userId: data.user_id, name: data.name });
            navigate("/dashboard");
          },
          type: "info",
        });
      }
    } catch ( error ) {
      console.error("Login error:", error);
      setModal({
        open: true,
        message: "An error occurred. Please try again.",
        onOk: closeModal,
        type: "error",
      });
    }
  };

  return (
    <div className="auth-container">
      <h2>Sign In</h2>
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
    </div>
  );
};

export default LoginForm;
