import { useEffect, useState } from "react";
import { Loader, Panel, Progress } from "rsuite";
import JobService from "./service";
import { IngestionJob } from "./model";

interface InProgressJobProps {
  job: IngestionJob;
}

const InProgressJob = (props: InProgressJobProps) => {
  const [job, setJob] = useState({ job: props.job });
  useEffect(() => {
    const interval = setInterval(() => {
      const service = new JobService();
      service.getJobDetails(job.job.id).then((job) => {
        setJob({ job: job });
      });
    }, 10000);
    return () => {
      clearInterval(interval);
    };
  });
  return (
    <>
      <Progress.Line percent={job.job.progress} strokeColor="#ffc107" />
      <Panel header="Selected Files">
        {job.job.files.map((file) => (
          <div>{file}</div>
        ))}
      </Panel>
      <Panel header="Completed Files">
        {job.job.completedFiles.map((file) => (
          <div>{file}</div>
        ))}
      </Panel>
    </>
  );
};

const InProgressJobs = () => {
  const [jobs, setJobs] = useState<IngestionJob[] | null>([]);
  useEffect(() => {
    const service = new JobService();
    service.inProgressJobs().then((jobs) => {
      console.log(typeof jobs[0].createdAt);
      jobs.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
      console.log(jobs);
      setJobs(jobs);
    });
    console.log("initialised in porgress jobs");
  }, []);
  return (
    <>
      {jobs === null ? (
        <Loader content="Checking..."></Loader>
      ) : (
        jobs.map((job) => <InProgressJob key={job.id} job={job} />)
      )}
    </>
  );
};

export default InProgressJobs;
