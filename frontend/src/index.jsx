// frontend/src/index.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
// import './index.css'; // Assuming you have a global CSS file if needed

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);