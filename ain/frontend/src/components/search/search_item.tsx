import { FileItem } from "./model";
import { Accordion, Stack, Avatar, Button, Grid, Row, Col } from "rsuite";
import PdfImage from "../../assets/pdf.png";
import SearchService from "./service";

interface ISearchItemProp {
  searchItem: FileItem;
}

interface IHeaderProp {
  title: string;
  subtitle: string;
}

interface IPageProp {
  pageNumber: string;
  filePath: string;
}

const Header = (props: IHeaderProp) => {
  const { title, subtitle } = props;
  return (
    <Stack spacing={10} alignItems="flex-start">
      <Avatar src={PdfImage} alt={title} />
      <Stack spacing={2} direction="column" alignItems="flex-start">
        <div>{title}</div>
        <div style={{ color: "var(--rs-text-secondary)", fontSize: 12 }}>
          {subtitle}
        </div>
      </Stack>
    </Stack>
  );
};

const Page = (props: IPageProp) => {
  // const [showModal, setShowModal] = useState<boolean>(false);
  const onPageClick = () => {
    console.log("open pdf");
    const service = new SearchService();
    service.open(props.filePath, props.pageNumber);
  };
  return (
    <>
      <Col xs={2}>
        <Button onClick={onPageClick}>{props.pageNumber}</Button>
        <br />
      </Col>
    </>
  );
};

function SearchItem(props: ISearchItemProp) {
  const pathSplitArr = props.searchItem.filePath.split("/");
  const fileName = pathSplitArr[pathSplitArr.length - 1];
  const dir = props.searchItem.filePath.substring(
    0,
    props.searchItem.filePath.lastIndexOf("/")
  );
  return (
    <>
      <Accordion bordered defaultActiveKey={1}>
        <Accordion.Panel
          header={<Header title={fileName} subtitle={dir}></Header>}
        >
          <Grid fluid>
            <Row gutter={16}>
              {props.searchItem.pages.map((pageNumber) => (
                <Page
                  key={pageNumber}
                  pageNumber={pageNumber}
                  filePath={props.searchItem.filePath}
                ></Page>
              ))}
            </Row>
          </Grid>
        </Accordion.Panel>
      </Accordion>
    </>
  );
}

export default SearchItem;
