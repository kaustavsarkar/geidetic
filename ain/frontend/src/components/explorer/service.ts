import { FileList, IFileList } from "./model";

const isLocal = import.meta.env.MODE === "development";

export default class ExplorerService {
  _files = (): IFileList =>
    JSON.parse(
      ` {"files":["/home/kaustav/work/ain/view-bill.pdf","/home/kaustav/work/ain/legal_gk.pdf","/home/kaustav/work/ain/lexpedia.pdf","/home/kaustav/work/ain/judicial.pdf"]}`
    );
  /**
   * Sends a request to the server to allow the user to select pdfs for parsing.
   * @returns list of pdfs selected
   */
  fetchPdfs = async (): Promise<FileList | null> => {
    if (isLocal) {
      return new FileList(this._files());
    }
    try {
      const response = await fetch(`http://localhost:5000/fetchPdfs`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        return new FileList(await response.json());
      }
    } catch (e) {
      console.log(e);
    }
    return null;
  };

  /**
   * Sends a list of PDFs to the server which need to be parsed.
   * @param pdfs a list of pdfs which need to be parsed.
   * @returns whether the server processed the request successfully.
   */
  parsePdfs = async (pdfs: FileList): Promise<void> => {
    try {
      const response = await fetch(`http://localhost:5000/indexpdfs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body:
          Object.keys(pdfs).length !== 0
            ? JSON.stringify({ selectedFiles: pdfs.selectedFiles })
            : null,
      });

      if (response.ok) {
        return;
      }
    } catch (e) {
      // Handle the error.
    }
    return;
  };

  /**
   * Fetches the path if a pdf with same name was parsed.
   * @param pdfName name of the pdf
   * @returns path of the pdf previously parsed
   */
  getFilePath = async (pdfName: string): Promise<string> => {
    if (isLocal) {
      await sleep(2000);
      return "random_path";
    }
    try {
      const response = await fetch("http://localhost:5000/pdfpath", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ pdfName: pdfName }),
      });

      if (response.ok) {
        return (await response.json())["path"];
      }
    } catch (e) {
      // Handle the error.
    }
    return "";
  };
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
