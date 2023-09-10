import SearchInput from "./search-input";
import "./index.scss";
import { Button, ButtonToolbar } from "rsuite";
import { useNavigate } from "react-router-dom";

function Search() {
  const navigate = useNavigate();

  return (
    <>
      <div className="search-container">
        <div className="search-box">
          <div className="logo-container">
            <span className="logo">Ain-Legal AI</span>
          </div>
          <div className="input-container">
            <SearchInput></SearchInput>
          </div>
          <div className="button-container">
            <ButtonToolbar>
              <Button
                color="cyan"
                appearance="primary"
                onClick={() => navigate("/library")}
              >
                My Library
              </Button>
            </ButtonToolbar>
          </div>
        </div>
      </div>
    </>
  );
}

export default Search;
