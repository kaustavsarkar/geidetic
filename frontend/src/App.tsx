import "./App.css";
import Search from "./search";
import { Route, Routes } from "react-router-dom";
import Library from "./library";

function App() {
  return (
    <>
      <Routes>
        <Route path="/" Component={Search} />
        <Route path="/library" Component={Library} />
      </Routes>
    </>
  );
}

export default App;
