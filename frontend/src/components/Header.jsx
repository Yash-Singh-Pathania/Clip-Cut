// src/components/Header.jsx
import React from "react";
import "./Header.css";

// Adjust the path based on where your logo.png is actually located
import clipCutLogo from "../logo/logo.png";

const Header = () => {
  return (
    <header className="main-header">
      <div className="logo-container">
        {/* If you *still* want the cloud emoji, keep it here:
            <span className="cloud-emoji" role="img" aria-label="cloud">☁️</span>
        */}
        
        {/* The PNG logo */}
        <img src={clipCutLogo} alt="ClipCut Logo" className="header-logo" />

        <div className="brand-text">
          <h1>ClipCut</h1>
          <p>One distributed frame at a time</p>
        </div>
      </div>
    </header>
  );
};

export default Header;
