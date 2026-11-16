import React, { useState } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  GraduationCap,
  Briefcase,
  Code2,
  Sparkles,
  RotateCcw,
  Send,
  AlertTriangle,
  Loader2,
} from "lucide-react";
import {
  studentFormSchema,
  SAMPLE_PROFILES,
} from "../schemas/formSchema";
import type { StudentFormSchema } from "../schemas/formSchema";
import { apiService, ApiClientError, getApiBaseUrl, isLocalBackendUrl } from "../services/api";
import type { PredictionResponse, StudentFormData } from "../types/placement";
import { ResultPanel } from "../components/ResultPanel";
import type { ConnectionStatus } from "../hooks/useApiHealth";

interface PredictorPageProps {
  apiStatus: ConnectionStatus;
  onRefreshHealth: () => void;
}

export const PredictorPage: React.FC<PredictorPageProps> = ({
  apiStatus,
  onRefreshHealth,
}) => {
  const [predictionResult, setPredictionResult] = useState<PredictionResponse | null>(null);
  const [submittedData, setSubmittedData] = useState<StudentFormData | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<{ message: string; details?: string[] } | null>(null);

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors },
  } = useForm<StudentFormSchema>({
    resolver: zodResolver(studentFormSchema),
    defaultValues: {
      CGPA: "" as any,
      SSC_Marks: "" as any,
      HSC_Marks: "" as any,
      AptitudeTestScore: "" as any,
      SoftSkillsRating: "" as any,
      Internships: "" as any,
      Projects: "" as any,
      "Workshops/Certifications": "" as any,
      PlacementTraining: "No",
      ExtracurricularActivities: "No",
      LeetCode_Problems_Solved: "" as any,
      Hackathon_Wins: "" as any,
      Publications: "" as any,
    },
  });

  const onSubmit = async (data: StudentFormSchema) => {
    setIsSubmitting(true);
    setApiError(null);

    try {
      const response = await apiService.predictPlacement(data as StudentFormData);
      setPredictionResult(response);
      setSubmittedData(data as StudentFormData);
    } catch (err: any) {
      if (err instanceof ApiClientError) {
        setApiError({
          message: err.message,
          details: err.details,
        });
      } else {
        setApiError({
          message: "An unexpected error occurred during prediction. Please verify your connection.",
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleLoadSample = (profileKey: keyof typeof SAMPLE_PROFILES) => {
    const profile = SAMPLE_PROFILES[profileKey];
    if (profile) {
      reset(profile.data);
      setApiError(null);
    }
  };

  const handleResetForm = () => {
    reset({
      CGPA: "" as any,
      SSC_Marks: "" as any,
      HSC_Marks: "" as any,
      AptitudeTestScore: "" as any,
      SoftSkillsRating: "" as any,
      Internships: "" as any,
      Projects: "" as any,
      "Workshops/Certifications": "" as any,
      PlacementTraining: "No",
      ExtracurricularActivities: "No",
      LeetCode_Problems_Solved: "" as any,
      Hackathon_Wins: "" as any,
      Publications: "" as any,
    });
    setPredictionResult(null);
    setSubmittedData(null);
    setApiError(null);
  };

  return (
    <div className="space-y-8">
      {/* Editorial Header */}
      <div className="border-b border-[#E4E1DA] pb-5">
        <h1 className="font-heading text-2xl sm:text-3xl font-bold tracking-tight text-[#202B38]">
          Placement Predictor
        </h1>
        <p className="mt-1 text-sm text-[#738091] max-w-2xl leading-relaxed">
          Enter verified student credentials below. Inference is executed server-side via the fitted Logistic Regression pipeline with strict feature alignment.
        </p>
      </div>

      {/* Backend Alert if offline */}
      {apiStatus === "disconnected" && (() => {
        const apiBaseUrl = getApiBaseUrl();
        const localBackend = isLocalBackendUrl(apiBaseUrl);
        return (
          <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800 flex items-start justify-between gap-3 shadow-xs">
            <div className="flex items-start gap-2.5">
              <AlertTriangle className="h-4 w-4 text-rose-600 shrink-0 mt-0.5" />
              <div>
                <strong className="font-semibold block">Prediction Backend Unreachable</strong>
                <span>
                  Unable to reach the configured backend API
                  {apiBaseUrl ? (
                    <>
                      {" "}at <code>{apiBaseUrl}</code>
                    </>
                  ) : null}
                  .{" "}
                  {localBackend
                    ? "Start the local Flask backend (for example, run `python run.py` in the `backend/` directory) and try again."
                    : "The backend may be temporarily unavailable or waking up (Render free services can take up to a minute). Please wait a moment and retry."}
                </span>
              </div>
            </div>
            <button
              onClick={onRefreshHealth}
              className="shrink-0 rounded border border-rose-300 bg-white px-2.5 py-1 text-xs font-semibold text-rose-700 hover:bg-rose-100 transition-colors"
            >
              Retry Connection
            </button>
          </div>
        );
      })()}

      {/* Prediction Result Display (if available) */}
      {predictionResult && submittedData ? (
        <ResultPanel
          result={predictionResult}
          submittedProfile={submittedData}
          onReset={handleResetForm}
        />
      ) : (
        <div className="space-y-6">
          {/* Preset Sample Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-xl border border-[#E4E1DA] bg-white p-4 shadow-xs">
            <div className="flex items-center gap-2 text-xs font-semibold text-[#738091] uppercase tracking-wider">
              <Sparkles className="h-4 w-4 text-[#C6A66B]" />
              <span>Load Verified Profile Preset:</span>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={() => handleLoadSample("highPotential")}
                className="rounded-md border border-[#3D827C]/30 bg-[#EBF3F2] px-3 py-1.5 text-xs font-medium text-[#3D827C] hover:bg-[#3D827C]/15 transition-colors"
              >
                High-Potential Candidate
              </button>
              <button
                type="button"
                onClick={() => handleLoadSample("balancedBenchmark")}
                className="rounded-md border border-[#E4E1DA] bg-[#F6F3ED] px-3 py-1.5 text-xs font-medium text-[#202B38] hover:bg-[#ECE9E2] transition-colors"
              >
                Balanced Benchmark
              </button>
              <button
                type="button"
                onClick={() => handleLoadSample("developingProfile")}
                className="rounded-md border border-[#C6A66B]/30 bg-[#F7F3E9] px-3 py-1.5 text-xs font-medium text-[#9A7B3E] hover:bg-[#C6A66B]/20 transition-colors"
              >
                Developing Candidate
              </button>
            </div>
          </div>

          {/* Form Card */}
          <form
            onSubmit={handleSubmit(onSubmit)}
            className="rounded-2xl border border-[#E4E1DA] bg-white p-6 sm:p-8 shadow-xs space-y-8"
          >
            {/* Section 1: Academic Profile */}
            <div>
              <div className="flex items-center gap-2.5 border-b border-[#E4E1DA] pb-3 mb-5">
                <div className="flex h-7 w-7 items-center justify-center rounded-md bg-[#EBF3F2] text-[#3D827C]">
                  <GraduationCap className="h-4 w-4" />
                </div>
                <div>
                  <h2 className="font-heading text-base font-bold text-[#202B38]">
                    1. Academic Profile
                  </h2>
                  <p className="text-xs text-[#738091]">
                    Cumulative grade scores and standardized assessments
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                {/* CGPA */}
                <div>
                  <label className="block text-xs font-semibold text-[#202B38] mb-1">
                    CGPA <span className="text-[#738091] font-normal">(0.0 – 10.0)</span>
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    placeholder="e.g. 8.25"
                    {...register("CGPA", { valueAsNumber: true })}
                    className={`w-full rounded-lg border px-3 py-2 text-sm text-[#202B38] placeholder-gray-400 bg-white transition-all focus:border-[#3D827C] focus:ring-1 focus:ring-[#3D827C] ${
                      errors.CGPA ? "border-rose-400 bg-rose-50/30" : "border-[#E4E1DA]"
                    }`}
                  />
                  <div className="mt-1 flex items-center justify-between text-[11px] text-[#738091]">
                    <span>Training range: 6.5 – 9.1</span>
                    {errors.CGPA && (
                      <span className="text-rose-600 font-medium">{errors.CGPA.message}</span>
                    )}
                  </div>
                </div>

                {/* SSC Marks */}
                <div>
                  <label className="block text-xs font-semibold text-[#202B38] mb-1">
                    SSC Marks (10th) <span className="text-[#738091] font-normal">(0 – 100%)</span>
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    placeholder="e.g. 78.5"
                    {...register("SSC_Marks", { valueAsNumber: true })}
                    className={`w-full rounded-lg border px-3 py-2 text-sm text-[#202B38] placeholder-gray-400 bg-white transition-all focus:border-[#3D827C] focus:ring-1 focus:ring-[#3D827C] ${
                      errors.SSC_Marks ? "border-rose-400 bg-rose-50/30" : "border-[#E4E1DA]"
                    }`}
                  />
                  <div className="mt-1 flex items-center justify-between text-[11px] text-[#738091]">
                    <span>Training range: 55% – 90%</span>
                    {errors.SSC_Marks && (
                      <span className="text-rose-600 font-medium">{errors.SSC_Marks.message}</span>
                    )}
                  </div>
                </div>

                {/* HSC Marks */}
                <div>
                  <label className="block text-xs font-semibold text-[#202B38] mb-1">
                    HSC Marks (12th) <span className="text-[#738091] font-normal">(0 – 100%)</span>
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    placeholder="e.g. 80.0"
                    {...register("HSC_Marks", { valueAsNumber: true })}
                    className={`w-full rounded-lg border px-3 py-2 text-sm text-[#202B38] placeholder-gray-400 bg-white transition-all focus:border-[#3D827C] focus:ring-1 focus:ring-[#3D827C] ${
                      errors.HSC_Marks ? "border-rose-400 bg-rose-50/30" : "border-[#E4E1DA]"
                    }`}
                  />
                  <div className="mt-1 flex items-center justify-between text-[11px] text-[#738091]">
                    <span>Training range: 57% – 88%</span>
                    {errors.HSC_Marks && (
                      <span className="text-rose-600 font-medium">{errors.HSC_Marks.message}</span>
                    )}
                  </div>
                </div>

                {/* Aptitude Test Score */}
                <div>
                  <label className="block text-xs font-semibold text-[#202B38] mb-1">
                    Aptitude Test Score <span className="text-[#738091] font-normal">(0 – 100)</span>
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    placeholder="e.g. 85.0"
                    {...register("AptitudeTestScore", { valueAsNumber: true })}
                    className={`w-full rounded-lg border px-3 py-2 text-sm text-[#202B38] placeholder-gray-400 bg-white transition-all focus:border-[#3D827C] focus:ring-1 focus:ring-[#3D827C] ${
                      errors.AptitudeTestScore ? "border-rose-400 bg-rose-50/30" : "border-[#E4E1DA]"
                    }`}
                  />
                  <div className="mt-1 flex items-center justify-between text-[11px] text-[#738091]">
                    <span>Training range: 60 – 90</span>
                    {errors.AptitudeTestScore && (
                      <span className="text-rose-600 font-medium">{errors.AptitudeTestScore.message}</span>
                    )}
                  </div>
                </div>

                {/* Soft Skills Rating */}
                <div>
                  <label className="block text-xs font-semibold text-[#202B38] mb-1">
                    Soft Skills Rating <span className="text-[#738091] font-normal">(0.0 – 5.0)</span>
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    placeholder="e.g. 4.4"
                    {...register("SoftSkillsRating", { valueAsNumber: true })}
                    className={`w-full rounded-lg border px-3 py-2 text-sm text-[#202B38] placeholder-gray-400 bg-white transition-all focus:border-[#3D827C] focus:ring-1 focus:ring-[#3D827C] ${
                      errors.SoftSkillsRating ? "border-rose-400 bg-rose-50/30" : "border-[#E4E1DA]"
                    }`}
                  />
                  <div className="mt-1 flex items-center justify-between text-[11px] text-[#738091]">
                    <span>Training scale: 3.0 – 4.8</span>
                    {errors.SoftSkillsRating && (
                      <span className="text-rose-600 font-medium">{errors.SoftSkillsRating.message}</span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Section 2: Experience & Preparation */}
            <div>
              <div className="flex items-center gap-2.5 border-b border-[#E4E1DA] pb-3 mb-5">
                <div className="flex h-7 w-7 items-center justify-center rounded-md bg-[#EBF3F2] text-[#3D827C]">
                  <Briefcase className="h-4 w-4" />
                </div>
                <div>
                  <h2 className="font-heading text-base font-bold text-[#202B38]">
                    2. Experience & Preparation
                  </h2>
                  <p className="text-xs text-[#738091]">
                    Practical internships, projects, and campus placement activities
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                {/* Internships */}
                <div>
                  <label className="block text-xs font-semibold text-[#202B38] mb-1">
                    Internships Completed <span className="text-[#738091] font-normal">(0 – 10)</span>
                  </label>
                  <input
                    type="number"
                    placeholder="e.g. 1"
                    {...register("Internships", { valueAsNumber: true })}
                    className={`w-full rounded-lg border px-3 py-2 text-sm text-[#202B38] placeholder-gray-400 bg-white transition-all focus:border-[#3D827C] focus:ring-1 focus:ring-[#3D827C] ${
                      errors.Internships ? "border-rose-400 bg-rose-50/30" : "border-[#E4E1DA]"
                    }`}
                  />
                  <div className="mt-1 flex items-center justify-between text-[11px] text-[#738091]">
                    <span>Whole integer</span>
                    {errors.Internships && (
                      <span className="text-rose-600 font-medium">{errors.Internships.message}</span>
                    )}
                  </div>
                </div>

                {/* Projects */}
                <div>
                  <label className="block text-xs font-semibold text-[#202B38] mb-1">
                    Completed Projects <span className="text-[#738091] font-normal">(0 – 15)</span>
                  </label>
                  <input
                    type="number"
                    placeholder="e.g. 2"
                    {...register("Projects", { valueAsNumber: true })}
                    className={`w-full rounded-lg border px-3 py-2 text-sm text-[#202B38] placeholder-gray-400 bg-white transition-all focus:border-[#3D827C] focus:ring-1 focus:ring-[#3D827C] ${
                      errors.Projects ? "border-rose-400 bg-rose-50/30" : "border-[#E4E1DA]"
                    }`}
                  />
                  <div className="mt-1 flex items-center justify-between text-[11px] text-[#738091]">
                    <span>Course & portfolio projects</span>
                    {errors.Projects && (
                      <span className="text-rose-600 font-medium">{errors.Projects.message}</span>
                    )}
                  </div>
                </div>

                {/* Workshops/Certifications */}
                <div>
                  <label className="block text-xs font-semibold text-[#202B38] mb-1">
                    Workshops / Certifications <span className="text-[#738091] font-normal">(0 – 15)</span>
                  </label>
                  <input
                    type="number"
                    placeholder="e.g. 2"
                    {...register("Workshops/Certifications", { valueAsNumber: true })}
                    className={`w-full rounded-lg border px-3 py-2 text-sm text-[#202B38] placeholder-gray-400 bg-white transition-all focus:border-[#3D827C] focus:ring-1 focus:ring-[#3D827C] ${
                      errors["Workshops/Certifications"]
                        ? "border-rose-400 bg-rose-50/30"
                        : "border-[#E4E1DA]"
                    }`}
                  />
                  <div className="mt-1 flex items-center justify-between text-[11px] text-[#738091]">
                    <span>Industry credentials</span>
                    {errors["Workshops/Certifications"] && (
                      <span className="text-rose-600 font-medium">
                        {errors["Workshops/Certifications"].message}
                      </span>
                    )}
                  </div>
                </div>

                {/* Placement Training - Segmented Control */}
                <div>
                  <label className="block text-xs font-semibold text-[#202B38] mb-1">
                    Placement Training
                  </label>
                  <Controller
                    control={control}
                    name="PlacementTraining"
                    render={({ field }) => (
                      <div className="grid grid-cols-2 rounded-lg border border-[#E4E1DA] bg-[#F6F3ED] p-1">
                        <button
                          type="button"
                          onClick={() => field.onChange("Yes")}
                          className={`rounded-md py-1.5 text-xs font-semibold transition-all ${
                            field.value === "Yes"
                              ? "bg-white text-[#3D827C] shadow-xs"
                              : "text-[#738091] hover:text-[#202B38]"
                          }`}
                        >
                          Yes
                        </button>
                        <button
                          type="button"
                          onClick={() => field.onChange("No")}
                          className={`rounded-md py-1.5 text-xs font-semibold transition-all ${
                            field.value === "No"
                              ? "bg-white text-[#202B38] shadow-xs"
                              : "text-[#738091] hover:text-[#202B38]"
                          }`}
                        >
                          No
                        </button>
                      </div>
                    )}
                  />
                  <span className="mt-1 block text-[11px] text-[#738091]">
                    Formal institutional training
                  </span>
                </div>

                {/* Extracurricular Activities - Segmented Control */}
                <div>
                  <label className="block text-xs font-semibold text-[#202B38] mb-1">
                    Extracurricular Activities
                  </label>
                  <Controller
                    control={control}
                    name="ExtracurricularActivities"
                    render={({ field }) => (
                      <div className="grid grid-cols-2 rounded-lg border border-[#E4E1DA] bg-[#F6F3ED] p-1">
                        <button
                          type="button"
                          onClick={() => field.onChange("Yes")}
                          className={`rounded-md py-1.5 text-xs font-semibold transition-all ${
                            field.value === "Yes"
                              ? "bg-white text-[#3D827C] shadow-xs"
                              : "text-[#738091] hover:text-[#202B38]"
                          }`}
                        >
                          Yes
                        </button>
                        <button
                          type="button"
                          onClick={() => field.onChange("No")}
                          className={`rounded-md py-1.5 text-xs font-semibold transition-all ${
                            field.value === "No"
                              ? "bg-white text-[#202B38] shadow-xs"
                              : "text-[#738091] hover:text-[#202B38]"
                          }`}
                        >
                          No
                        </button>
                      </div>
                    )}
                  />
                  <span className="mt-1 block text-[11px] text-[#738091]">
                    Sports, cultural, leadership roles
                  </span>
                </div>
              </div>
            </div>

            {/* Section 3: Technical & Research Profile */}
            <div>
              <div className="flex items-center gap-2.5 border-b border-[#E4E1DA] pb-3 mb-5">
                <div className="flex h-7 w-7 items-center justify-center rounded-md bg-[#F7F3E9] text-[#9A7B3E]">
                  <Code2 className="h-4 w-4" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="font-heading text-base font-bold text-[#202B38]">
                      3. Technical and Research Profile
                    </h2>
                    <span className="rounded bg-[#F7F3E9] border border-[#C6A66B]/30 px-1.5 py-0.2 text-[10px] font-semibold text-[#9A7B3E]">
                      Synthetic Features in Dataset
                    </span>
                  </div>
                  <p className="text-xs text-[#738091]">
                    Competitive programming benchmarks, hackathon performance, and publications
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                {/* LeetCode Problems Solved */}
                <div>
                  <label className="block text-xs font-semibold text-[#202B38] mb-1">
                    LeetCode Problems Solved <span className="text-[#738091] font-normal">(0 – 500)</span>
                  </label>
                  <input
                    type="number"
                    placeholder="e.g. 240"
                    {...register("LeetCode_Problems_Solved", { valueAsNumber: true })}
                    className={`w-full rounded-lg border px-3 py-2 text-sm text-[#202B38] placeholder-gray-400 bg-white transition-all focus:border-[#3D827C] focus:ring-1 focus:ring-[#3D827C] ${
                      errors.LeetCode_Problems_Solved
                        ? "border-rose-400 bg-rose-50/30"
                        : "border-[#E4E1DA]"
                    }`}
                  />
                  <div className="mt-1 flex items-center justify-between text-[11px] text-[#738091]">
                    <span>Synthetic maximum: 500</span>
                    {errors.LeetCode_Problems_Solved && (
                      <span className="text-rose-600 font-medium">
                        {errors.LeetCode_Problems_Solved.message}
                      </span>
                    )}
                  </div>
                </div>

                {/* Hackathon Wins */}
                <div>
                  <label className="block text-xs font-semibold text-[#202B38] mb-1">
                    Hackathon Wins <span className="text-[#738091] font-normal">(0 – 5)</span>
                  </label>
                  <input
                    type="number"
                    placeholder="e.g. 1"
                    {...register("Hackathon_Wins", { valueAsNumber: true })}
                    className={`w-full rounded-lg border px-3 py-2 text-sm text-[#202B38] placeholder-gray-400 bg-white transition-all focus:border-[#3D827C] focus:ring-1 focus:ring-[#3D827C] ${
                      errors.Hackathon_Wins
                        ? "border-rose-400 bg-rose-50/30"
                        : "border-[#E4E1DA]"
                    }`}
                  />
                  <div className="mt-1 flex items-center justify-between text-[11px] text-[#738091]">
                    <span>Podium awards (0–5)</span>
                    {errors.Hackathon_Wins && (
                      <span className="text-rose-600 font-medium">
                        {errors.Hackathon_Wins.message}
                      </span>
                    )}
                  </div>
                </div>

                {/* Research Publications */}
                <div>
                  <label className="block text-xs font-semibold text-[#202B38] mb-1">
                    Research Publications <span className="text-[#738091] font-normal">(0 – 4)</span>
                  </label>
                  <input
                    type="number"
                    placeholder="e.g. 0"
                    {...register("Publications", { valueAsNumber: true })}
                    className={`w-full rounded-lg border px-3 py-2 text-sm text-[#202B38] placeholder-gray-400 bg-white transition-all focus:border-[#3D827C] focus:ring-1 focus:ring-[#3D827C] ${
                      errors.Publications ? "border-rose-400 bg-rose-50/30" : "border-[#E4E1DA]"
                    }`}
                  />
                  <div className="mt-1 flex items-center justify-between text-[11px] text-[#738091]">
                    <span>Peer-reviewed papers (0–4)</span>
                    {errors.Publications && (
                      <span className="text-rose-600 font-medium">
                        {errors.Publications.message}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Error Banner */}
            {apiError && (
              <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800">
                <div className="flex items-center gap-2 font-semibold text-rose-900 mb-1">
                  <AlertTriangle className="h-4 w-4 text-rose-600" />
                  <span>{apiError.message}</span>
                </div>
                {apiError.details && apiError.details.length > 0 && (
                  <ul className="list-disc list-inside mt-2 space-y-0.5 text-rose-700">
                    {apiError.details.map((detail, idx) => (
                      <li key={idx}>{detail}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            {/* Form Actions */}
            <div className="border-t border-[#E4E1DA] pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
              <button
                type="button"
                onClick={handleResetForm}
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-lg border border-[#E4E1DA] bg-white px-4 py-2.5 text-xs font-semibold text-[#738091] hover:bg-[#F6F3ED] hover:text-[#202B38] transition-colors"
              >
                <RotateCcw className="h-3.5 w-3.5" />
                Clear Form
              </button>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 rounded-lg bg-[#101C2C] px-7 py-3 text-sm font-semibold text-white shadow-xs hover:bg-[#192B40] transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin text-[#C6A66B]" />
                    <span>Executing ML Inference...</span>
                  </>
                ) : (
                  <>
                    <span>Generate Prediction</span>
                    <Send className="h-3.5 w-3.5 text-[#C6A66B]" />
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
