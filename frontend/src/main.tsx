import React from "react";
import { createRoot } from "react-dom/client";
import "./style.css";
import App from "./App";
import { HashRouter } from "react-router-dom";
import 'rsuite/dist/rsuite.min.css';

const container = document.getElementById("root");

const root = createRoot(container!);

root.render(
  <HashRouter>
    <React.StrictMode>
      <App />
    </React.StrictMode>
  </HashRouter>
);
