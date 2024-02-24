import { IngestionJob, JobStatus } from "./model";

const isLocal = import.meta.env.MODE === "development";

export default class JobService {
  _inProgress =
    JSON.parse(`{"jobs":[{"completedFiles":["/home/kaustav/work/ain/_1220.pdf", "/home/kaustav/work/ain/_1220.pdf"],"createdAt":"2024-02-21 02:26:02.903874","files":["/home/kaustav/work/ain/_1220.pdf"],"id":"753e7746-d032-11ee-a9de-ad2b0d6c2826","progress":1,"reason":null,"status":"IN_PROGRESS","updatedAt":"2024-02-21 02:30:59.693483"},{"completedFiles":["/home/kaustav/work/ain/_1220.pdf"],"createdAt":"2024-02-21 02:30:59.300428","files":["/home/kaustav/work/ain/_1220.pdf"],"id":"25e900f2-d033-11ee-a9de-ad2b0d6c2826","progress":100,"reason":null,"status":"IN_PROGRESS","updatedAt":"2024-02-21 02:30:59.937026"}]}
    `);
  _jobDetails = JSON.parse(
    `{"completedFiles":["/home/kaustav/work/ain/_1220.pdf", "/home/kaustav/work/ain/_1220.pdf"],"createdAt":"2024-02-21 02:26:02.903874","files":["/home/kaustav/work/ain/_1220.pdf"],"id":"753e7746-d032-11ee-a9de-ad2b0d6c2826","progress":1,"reason":null,"status":"IN_PROGRESS","updatedAt":"2024-02-21 02:30:59.693483"}`
  );
  inProgressJobs = async (): Promise<IngestionJob[]> => {
    if (isLocal) {
      const jobs: IngestionJob[] = [];
      for (const job of this._inProgress.jobs) {
        jobs.push(new IngestionJob(job));
      }
      return jobs;
    }

    try {
      const response = await fetch(`http://localhost:5000/jobs`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ status: JobStatus.IN_PROGRESS.toString() }),
      });

      if (response.ok) {
        const json = await response.json();
        const jobs: IngestionJob[] = [];
        for (const job of json.jobs) {
          jobs.push(new IngestionJob(job));
        }
        return jobs;
      }
    } catch (e) {
      console.log(e);
    }
    return [];
  };

  getJobDetails = async (id: string): Promise<IngestionJob> => {
    if (isLocal) {
      return new IngestionJob(this._jobDetails);
    }
    try {
      const response = await fetch(`http://localhost:5000/job`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ id: id }),
      });

      if (response.ok) {
        return new IngestionJob((await response.json()));
      }
    } catch (e) {
      console.log(e);
    }
    return new IngestionJob(null);
  };
}
