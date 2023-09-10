import "./App.css";
import Search from "./search";
import { Route, Routes } from "react-router-dom";

function App() {
  return (
      <>
        <Routes>
          <Route path="/" Component={Search} />
        </Routes>
      </>
  );
}

export default App;
