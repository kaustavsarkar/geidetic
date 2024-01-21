export class FileList {
  private _files: string[];

  constructor(json: unknown) {
    /* @ts-expect-error since there is no type for json. */
    this._files = json.files;
  }

  public get files() {
    return this._files;
  }
}
