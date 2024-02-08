import { FileList } from "./model";
import ExplorerService from "./service";
import { useEffect, useState } from "react";
import {
  Checkbox,
  CheckboxGroup,
  Divider,
  FlexboxGrid,
  Grid,
  IconButton,
  Panel,
  Row,
} from "rsuite";
import PlusIcon from "@rsuite/icons/Plus";
import PlayIcon from "@rsuite/icons/legacy/Play";

import "./explorer.scss";
import { ValueType } from "rsuite/esm/Checkbox";

interface IFcProps {
  files: string[];
  handleChanges: (selectedFiles: string[]) => void;
}

interface IFileItem {
  file: string;
}

function FileItem(props: IFileItem) {
  const path = props.file;
  const fileName = path.replace(/^.*[\\/]/, "");
  return (
    <>
      <Checkbox value={path}>{fileName}</Checkbox>
    </>
  );
}

function FilesContainer(props: IFcProps) {
  const files = props.files;
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);

  useEffect(() => {
    props.handleChanges(selectedFiles);
  }, [selectedFiles]);

  /**
   * Update the selected files.
   *
   * @param values selected files.
   */
  const handleFileSelected = (values: ValueType[]) => {
    setSelectedFiles(values.map((value) => value.toString()));
  };

  /**
   * Handles logic to select and unselect all the files.
   *
   * @param _ it is an unused variable.
   * @param checked whether the checkbox is selected.
   * @returns void
   */
  const handleCheckAll = (_: ValueType | undefined, checked: boolean) => {
    if (checked) {
      setSelectedFiles([...files]);
      return;
    }
    setSelectedFiles([]);
  };

  return (
    <>
      <Checkbox
        indeterminate={
          selectedFiles.length > 0 && selectedFiles.length < files.length
        }
        checked={selectedFiles.length === files.length}
        onChange={handleCheckAll}
      >
        Select All
      </Checkbox>
      <CheckboxGroup
        name="file-list"
        value={selectedFiles}
        onChange={handleFileSelected}
      >
        {files.map((file) => (
          <FileItem key={file} file={file} />
        ))}
      </CheckboxGroup>
    </>
  );
}

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
  const [fileListState, setFileList] = useState({ fileList: new FileList(null) });
  const showExplorer = async () => {
    const service = new ExplorerService();
    const response = (await service.fetchPdfs())!;
    setFileList({
      fileList: response,
    });
  };

  const updateSelectedFiles = (files: string[]) => {
    fileListState!.fileList.selectedFiles = files;
    setFileList({...fileListState});
    console.log(fileListState!.fileList.selectedFiles);
  };

  const memorisePdfs = () => {
    const service = new ExplorerService();
    service.parsePdfs(fileListState.fileList);
  }

  return (
    <div className="explorer-container">
      <Grid fluid>
        <Row>
          <FlexboxGrid justify="space-around">
            <IconButton
              onClick={showExplorer}
              size="lg"
              icon={<PlusIcon />}
              color="violet"
            >
              Select Files...
            </IconButton>
            <IconButton
              onClick={memorisePdfs}
              size="lg"
              icon={<PlayIcon />}
              color="violet"
              disabled={fileListState?.fileList.selectedFiles?.length === 0}
            >
              Memorise
            </IconButton>
          </FlexboxGrid>
        </Row>
        <Divider />
        {fileListState?.fileList.files && (
          <Row>
            <FlexboxGrid justify="center">
              <FlexboxGrid.Item colspan={22}>
                <div className="files-container">
                  <Panel header="Selected Files" shaded bordered>
                    <FilesContainer
                      files={fileListState.fileList.files}
                      handleChanges={updateSelectedFiles}
                    ></FilesContainer>
                  </Panel>
                </div>
              </FlexboxGrid.Item>
            </FlexboxGrid>
          </Row>
        )}
      </Grid>
    </div>
  );
}

export default Explorer;
