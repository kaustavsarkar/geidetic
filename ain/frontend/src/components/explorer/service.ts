import { FileList } from "./model";

export default class ExplorerService {
  /**
   * Sends a request to the server to allow the user to select pdfs for parsing.
   * @returns list of pdfs selected
   */
  fetchPdfs = async (): Promise<FileList | null> => {
    try {
      const response = await fetch(`http://localhost:5000/fetchPdfs`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        return new FileList(response.json);
      }
    } catch (e) {
      // Handle the error.
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
      const response = await fetch(`http://localhost:5000/parsePdfs`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        body: Object.keys(pdfs).length !== 0 ? JSON.stringify(pdfs) : null,
      });

      if (response.ok) {
        return;
      }
    } catch (e) {
      // Handle the error.
    }
    return;
  };
}
