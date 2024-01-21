import { Routes, Route } from "react-router-dom";
import "./App.css";
import "./components/explorer/index";
import Explorer from "./components/explorer/index";
import SideNavBar from "./components/navbar";

function App() {
  return (
    <>
      <div>
        <SideNavBar expanded={true}></SideNavBar>
        <div>
          <Routes>
            <Route path="/" element={<Explorer></Explorer>}></Route>
            <Route path="/explorer" element={<Explorer></Explorer>}></Route>
          </Routes>
        </div>
      </div>
    </>
  );
}

export default App;
