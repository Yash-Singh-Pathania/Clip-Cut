// src/components/Header.jsx
import React from "react";
import "./Header.css";

import clipCutLogo from "../logo/logo.png";

const Header = () => {
  return (
    <header className="main-header">
      <div className="logo-container">
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
