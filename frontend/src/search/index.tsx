import SearchInput from "./search-input";
import "./index.scss";

function Search() {
  return (
    <>
      <div className="search-container">
        <div>
          <div className="logo-container">
            <span className="logo">Ain-Legal AI</span>
          </div>
          <div className="input-container">
            <SearchInput></SearchInput>
          </div>
        </div>
      </div>
    </>
  );
}

export default Search;
