import { z } from "zod";

export const ppoFormSchema = z.object({
  Technical_Evaluation: z
    .number({ error: "Technical Evaluation must be a number" })
    .min(1, "Must be at least 1.0")
    .max(10, "Must be at most 10.0"),
  Task_Completion_Rate: z
    .number({ error: "Task Completion Rate must be a number" })
    .min(20, "Must be at least 20.0")
    .max(100, "Must be at most 100.0"),
  Attendance_Rate: z
    .number({ error: "Attendance Rate must be a number" })
    .min(51.5, "Must be at least 51.5")
    .max(100, "Must be at most 100.0"),
  Communication_Score: z
    .number({ error: "Communication Score must be a number" })
    .min(3.6, "Must be at least 3.6")
    .max(10, "Must be at most 10.0"),
  Manager_Rating: z
    .number({ error: "Manager Rating must be a number" })
    .min(1.4, "Must be at least 1.4")
    .max(10, "Must be at most 10.0"),
  Code_Quality_Score: z
    .number({ error: "Code Quality Score must be a number" })
    .min(1, "Must be at least 1.0")
    .max(10, "Must be at most 10.0"),
  Teamwork_Score: z
    .number({ error: "Teamwork Score must be a number" })
    .min(3.5, "Must be at least 3.5")
    .max(10, "Must be at most 10.0"),
  Deadline_Adherence: z
    .number({ error: "Deadline Adherence must be a number" })
    .min(20, "Must be at least 20.0")
    .max(100, "Must be at most 100.0"),
});

export type PPOFormSchema = z.infer<typeof ppoFormSchema>;

export const PPO_SAMPLE_PROFILE: PPOFormSchema = {
  Technical_Evaluation: 8.5,
  Task_Completion_Rate: 90,
  Attendance_Rate: 95,
  Communication_Score: 8.5,
  Manager_Rating: 9.0,
  Code_Quality_Score: 8.8,
  Teamwork_Score: 8.2,
  Deadline_Adherence: 90,
};
