import { FlexboxGrid } from "rsuite";
import SearchInput from "./search_input";

import "./search.scss";
import SearchService from "./service";
import SearchResult from "./search_result";
import { useState } from "react";
import { FileItemList } from "./model";

function Search() {
  const [searchResult, setSearchResult] = useState({
    searchResult: new FileItemList(null),
  });
  const onSearch = async (text: string) => {
    const service = new SearchService();
    const result = await service.search(text);
    setSearchResult({
      searchResult: result!,
    });
  };
  return (
    <>
      <div className="search-container">
        <FlexboxGrid justify="center">
          <div className="search-input">
            <SearchInput onSearch={onSearch}></SearchInput>
          </div>
        </FlexboxGrid>
        {searchResult?.searchResult?.searchItems?.length > 0 ? (
          <SearchResult searchItemList={searchResult.searchResult}></SearchResult>
        ) : (
          <>There are not records to show</>
        )}
      </div>
    </>
  );
}

export default Search;
