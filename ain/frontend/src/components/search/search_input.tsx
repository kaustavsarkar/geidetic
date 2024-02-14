import SearchIcon from "@rsuite/icons/Search";
import { KeyboardEvent, useState } from "react";
import { Input, InputGroup } from "rsuite";

interface ISearchInputProps {
  onSearch: (text: string) => void;
}

function SearchInput(props: ISearchInputProps) {
  const [inputString, setInputString] = useState("");

  const onInputChange = (value: string) => {
    setInputString(value);
  };

  const onPressEnter = (event: KeyboardEvent<HTMLInputElement>) => {
    const isEnter = event.key === "Enter";
    if (!isEnter) {
      return;
    }
    // Remove focus once the Enter key is pressed.
    (event.target as HTMLInputElement).blur();
    onSearch();
  };

  const onSearch = () => {
    if (!inputString) {
      return;
    }
    props.onSearch(inputString);
  };

  return (
    <>
      <InputGroup>
        <InputGroup.Addon>
          <SearchIcon></SearchIcon>
        </InputGroup.Addon>
        <Input
          size="lg"
          placeholder="Search"
          onKeyDownCapture={onPressEnter}
          onChange={onInputChange}
        ></Input>
        <InputGroup.Button onClick={onSearch}>Search</InputGroup.Button>
      </InputGroup>
    </>
  );
}

export default SearchInput;
