import { useNavigate } from "react-router";
import { Button } from "rsuite";
import DirectoryIngest from "./dir-ingest";

function Library() {
  const navigate = useNavigate();
  return (
    <>
      <Button appearance="link" active onClick={() => navigate("/")}>
        Back
      </Button>
      <DirectoryIngest></DirectoryIngest>
    </>
  );
}

export default Library;
