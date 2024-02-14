class SearchItem():
    """Represents a search item for the search result of a search text. """

    def __init__(self, file_path: str, pages: 'list[str]'):
        self._file_path = file_path
        self._pages = pages

    @property
    def file_path(self) -> str:
        """Returns the file path."""
        return self._file_path

    def append_page(self, page_number: str):
        """Appends page number to the existing list."""
        self._pages.append(page_number)

    def to_json(self) -> 'dict[str, any]':
        """Creates a json object of the class"""
        return {
            'filePath': self._file_path,
            'pages': self._pages
        }


class SearchResult():
    """Represents the search result for a search string."""

    def __init__(self) -> None:
        self._search_items: 'list[SearchItem]' = []

    def add_search_item(self, item: SearchItem):
        """Adds a search item to an existing list."""
        self._search_items.append(item)

    @property
    def search_items(self) -> 'list[SearchItem]':
        """Returns the search items gathered."""
        return self._search_items

    def to_json(self) -> 'dict[str,list[dict[str,any]]]':
        """Convers the class to a json object."""
        my_dict: 'dict[str,list[dict[str,any]]]' = {}
        item_list_dict: 'list[dict[str:any]]' = []
        for item in self._search_items:
            item_list_dict.append(item.to_json())
        my_dict['searchItems'] = item_list_dict
        return my_dict
