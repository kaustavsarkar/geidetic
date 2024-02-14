import { FileItemList } from "./model";
import SearchItem from "./search_item";

interface ISearchResultProp {
  searchItemList: FileItemList;
}

function SearchResult(props: ISearchResultProp) {
  const itemList = props.searchItemList;
  console.log(itemList);
  return (
    <>
      {itemList.searchItems.map((item) => {
        return <SearchItem key={item.filePath} searchItem={item}></SearchItem>;
      })}
    </>
  );
}

export default SearchResult;
