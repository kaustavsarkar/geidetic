import { Routes, Route } from "react-router-dom";
import "./App.css";
import "./components/explorer/index";
import Explorer from "./components/explorer/index";
import SideNavBar from "./components/navbar";
import Search from "./components/search";
import Jobs from "./components/jobs";

function App() {
  return (
    <>
      <div className="app">
        <SideNavBar></SideNavBar>
        <div className="app-content">
          <Routes>
            <Route path="/" element={<Search></Search>}></Route>
            <Route path="/explorer" element={<Explorer></Explorer>}></Route>
            <Route path="/jobs" element={<Jobs></Jobs>}></Route>
          </Routes>
        </div>
      </div>
    </>
  );
}

export default App;
