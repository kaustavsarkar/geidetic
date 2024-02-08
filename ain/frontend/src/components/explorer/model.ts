export interface IFileList {
  files: string[];
  selectedFiles: string[];
}

export class FileList implements IFileList {
  private _files: string[];
  private _selectedFiles: string[];

  constructor(json: unknown | null) {
    /* @ts-expect-error since there is no type for json. */
    this._files = json?.files ?? null;
    console.log(this._files);
    this._selectedFiles = [];
  }

  public get files() {
    return this._files;
  }

  public get selectedFiles() {
    return this._selectedFiles;
  }

  public set selectedFiles(files: string[]) {
    this._selectedFiles = files;
  }

  public addSelectedFile(file: string) {
    this._selectedFiles.push(file);
  }

  public removeSelectedFile(file: string): boolean {
    if (this._selectedFiles.length === 0) {
      return false;
    }

    const index = this._selectedFiles.indexOf(file);
    if (index === -1) {
      return false;
    }

    this._selectedFiles.splice(index, -1);

    return true;
  }
}

export default FileList;
