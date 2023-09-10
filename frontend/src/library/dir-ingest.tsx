import { Button } from "rsuite";
import { ProcessDirectory, ReadProcessedDirs } from "../../wailsjs/go/main/App";

function DirectoryIngest() {
  const selectDirectory = async () => {
    try {
      await ProcessDirectory();
    } catch (e) {
      console.log(e);
    }
  };

  const printDirectory = async () => {
    try {
      const dirs = await ReadProcessedDirs();
      console.log(dirs);
    } catch (e) {
      console.log(e);
    }
  };

  return (
    <>
      <Button onClick={selectDirectory}>Select PDFs</Button>
      <Button onClick={printDirectory}>Print PDFs</Button>
    </>
  );
}

export default DirectoryIngest;
