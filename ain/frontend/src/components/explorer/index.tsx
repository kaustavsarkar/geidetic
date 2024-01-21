import { Button } from "rsuite";

/**
 * The Explorer componnet selects and parses the files.
 *
 * For parsing the pdfs, they are required to be selected first. This would help in
 * determining any duplicates amd remove them, also allow folks to update their selection,
 * if required.
 *
 * Once the selection is finalised, there needs to be nother service which shall be sending the
 * list of selected and finalised PDFs to the server to start processing.
 *
 *
 * @returns a react component
 */
function Explorer() {
  const showExplorer = async () => {
    const response = await fetch(`http://localhost:5000/list`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    response.json();
  };
  return (
    <>
      <Button onClick={showExplorer}>Select Files...</Button>
    </>
  );
}

export default Explorer;
