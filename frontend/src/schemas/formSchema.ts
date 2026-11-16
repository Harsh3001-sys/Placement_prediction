import { z } from "zod";

export const studentFormSchema = z.object({
  CGPA: z
    .number({ error: "CGPA must be a number" })
    .min(0, "CGPA cannot be negative")
    .max(10, "CGPA cannot exceed 10.0"),
  SSC_Marks: z
    .number({ error: "SSC Marks must be a number" })
    .min(0, "SSC percentage cannot be negative")
    .max(100, "SSC percentage cannot exceed 100%"),
  HSC_Marks: z
    .number({ error: "HSC Marks must be a number" })
    .min(0, "HSC percentage cannot be negative")
    .max(100, "HSC percentage cannot exceed 100%"),
  AptitudeTestScore: z
    .number({ error: "Aptitude Score must be a number" })
    .min(0, "Aptitude score cannot be negative")
    .max(100, "Aptitude score cannot exceed 100"),
  SoftSkillsRating: z
    .number({ error: "Soft Skills Rating must be a number" })
    .min(0, "Rating cannot be negative")
    .max(5, "Rating cannot exceed 5.0"),
  Internships: z
    .number({ error: "Internships must be an integer" })
    .int("Must be a whole number")
    .min(0, "Cannot be negative")
    .max(10, "Maximum limit is 10"),
  Projects: z
    .number({ error: "Projects must be an integer" })
    .int("Must be a whole number")
    .min(0, "Cannot be negative")
    .max(15, "Maximum limit is 15"),
  "Workshops/Certifications": z
    .number({ error: "Certifications must be an integer" })
    .int("Must be a whole number")
    .min(0, "Cannot be negative")
    .max(15, "Maximum limit is 15"),
  PlacementTraining: z.enum(["Yes", "No"], {
    error: "Please select Yes or No",
  }),
  ExtracurricularActivities: z.enum(["Yes", "No"], {
    error: "Please select Yes or No",
  }),
  LeetCode_Problems_Solved: z
    .number({ error: "LeetCode solved count must be an integer" })
    .int("Must be a whole number")
    .min(0, "Cannot be negative")
    .max(500, "Maximum range in project dataset is 500"),
  Hackathon_Wins: z
    .number({ error: "Hackathon wins must be an integer" })
    .int("Must be a whole number")
    .min(0, "Cannot be negative")
    .max(5, "Maximum range in project dataset is 5"),
  Publications: z
    .number({ error: "Publications must be an integer" })
    .int("Must be a whole number")
    .min(0, "Cannot be negative")
    .max(4, "Maximum range in project dataset is 4"),
});

export type StudentFormSchema = z.infer<typeof studentFormSchema>;

export const SAMPLE_PROFILES: Record<string, { label: string; description: string; data: StudentFormSchema }> = {
  highPotential: {
    label: "High-Potential Candidate",
    description: "Strong academic record, formal placement training, active extracurriculars, and multiple projects.",
    data: {
      CGPA: 8.75,
      SSC_Marks: 84.5,
      HSC_Marks: 82.0,
      AptitudeTestScore: 88.0,
      SoftSkillsRating: 4.6,
      Internships: 2,
      Projects: 3,
      "Workshops/Certifications": 2,
      PlacementTraining: "Yes",
      ExtracurricularActivities: "Yes",
      LeetCode_Problems_Solved: 310,
      Hackathon_Wins: 2,
      Publications: 1,
    },
  },
  balancedBenchmark: {
    label: "Balanced Average Profile",
    description: "Average academic metrics aligned closely with the dataset median values.",
    data: {
      CGPA: 7.7,
      SSC_Marks: 70.0,
      HSC_Marks: 73.0,
      AptitudeTestScore: 79.5,
      SoftSkillsRating: 4.3,
      Internships: 1,
      Projects: 2,
      "Workshops/Certifications": 1,
      PlacementTraining: "Yes",
      ExtracurricularActivities: "Yes",
      LeetCode_Problems_Solved: 250,
      Hackathon_Wins: 1,
      Publications: 0,
    },
  },
  developingProfile: {
    label: "Developing Candidate",
    description: "Lower baseline scores without formal placement preparation or extracurricular involvement.",
    data: {
      CGPA: 6.8,
      SSC_Marks: 60.0,
      HSC_Marks: 62.0,
      AptitudeTestScore: 63.0,
      SoftSkillsRating: 3.2,
      Internships: 0,
      Projects: 1,
      "Workshops/Certifications": 0,
      PlacementTraining: "No",
      ExtracurricularActivities: "No",
      LeetCode_Problems_Solved: 40,
      Hackathon_Wins: 0,
      Publications: 0,
    },
  },
};
