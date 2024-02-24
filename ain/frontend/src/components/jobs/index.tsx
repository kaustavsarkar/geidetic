import { Tabs, Placeholder } from "rsuite";
import InProgressJobs from "./in_progress";

const Jobs = () => {
  return (
    <>
      <Tabs defaultActiveKey="1" vertical appearance="subtle">
        <Tabs.Tab eventKey="1" title="In Progress">
          <InProgressJobs></InProgressJobs>
        </Tabs.Tab>
        <Tabs.Tab eventKey="2" title="Completed">
          <Placeholder.Paragraph graph="square" rows={5} />
        </Tabs.Tab>
        <Tabs.Tab eventKey="3" title="Failed">
          <Placeholder.Paragraph graph="circle" rows={5} />
        </Tabs.Tab>
      </Tabs>
    </>
  );
};

export default Jobs;
