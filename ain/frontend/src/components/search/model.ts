export interface IFileItem {
  filePath: string;
  pages: string[];
}

export interface IFileItemList {
  searchItems: FileItem[];
}

export class FileItemList implements IFileItemList {
  private _searchItems: FileItem[] = [];

  constructor(json: unknown | null) {
    console.log(json);
    /* @ts-expect-error since there is no type for json. */
    const items = json?.searchItems ?? [];

    for (const item of items) {
      const searchItem = new FileItem(item);
      this._searchItems = this._searchItems.concat(searchItem);
    }
  }

  public get searchItems() {
    return this._searchItems;
  }
}

export class FileItem implements IFileItem {
  private _filePath: string;
  private _pages: string[];
  constructor(json: unknown | null) {
    /* @ts-expect-error since there is no type for json. */
    this._filePath = json?.filePath ?? null;
    /* @ts-expect-error since there is no type for json. */
    this._pages = json?.pages ?? [];
  }

  public get filePath() {
    return this._filePath;
  }

  public get pages() {
    return this._pages;
  }
}
