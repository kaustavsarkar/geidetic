import { Input, InputGroup } from "rsuite";
import SearchIcon from "@rsuite/icons/Search";
import "./search-input.scss";

const iconStyle = {
  position: "absolute",
  top: "15px",
  left: "15px",
  zIndex: 100,
  color: "black",
} as React.CSSProperties;

function SearchInput() {
  return (
    <>
      <div className="search-input">
        <InputGroup inside className="search-input-grp">
          <SearchIcon
            className="search-icon"
            style={iconStyle}
          />
          <Input classPrefix="search-input" />
        </InputGroup>
      </div>
    </>
  );
}

export default SearchInput;
