export class IngestionJob {
  private _id: string;
  private _status: JobStatus;
  private _reason: string;
  private _files: string[];
  private _completedFiles: string[];
  private _progress: number;
  private _createdAt: Date;
  private _updatedAt: Date;

  constructor(json: unknown | null) {
    console.log(json);
    /* @ts-expect-error since there is no type for json. */
    this._id = json?.id ?? "";
    /* @ts-expect-error since there is no type for json. */
    this._status = json?.status ?? JobStatus.UNDEFINED;
    /* @ts-expect-error since there is no type for json. */
    this._reason = json?.reason ?? "";
    /* @ts-expect-error since there is no type for json. */
    this._files = json?.files ?? [];
    /* @ts-expect-error since there is no type for json. */
    this._completedFiles = json?.completedFiles ?? [];
    /* @ts-expect-error since there is no type for json. */
    this._progress = json?.progress ?? 0;
    /* @ts-expect-error since there is no type for json. */
    this._createdAt = new Date(json?.createdAt) ?? null;
    /* @ts-expect-error since there is no type for json. */
    this._updatedAt = new Date(json?.updatedAt) ?? null;
    console.log(this);
  }

  public get id() {
    return this._id;
  }

  public get status() {
    return this._status;
  }

  public get reason() {
    return this._reason;
  }

  public get files() {
    return this._files;
  }

  public get completedFiles() {
    return this._completedFiles;
  }

  public get progress() {
    return this._progress;
  }

  public get createdAt() {
    return this._createdAt;
  }

  public get updatedAt() {
    return this._updatedAt;
  }
}

export enum JobStatus {
  STARTED = "STARTED",
  IN_PROGRESS = "IN_PROGRESS",
  FAILED = "FAILED",
  SUCCESS = "SUCCESS",
  UNDEFINED = "UNDEFINED",
}
