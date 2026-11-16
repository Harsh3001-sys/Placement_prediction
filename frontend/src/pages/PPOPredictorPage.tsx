import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  ClipboardList,
  Loader2,
  RotateCcw,
  Send,
  Sparkles,
} from "lucide-react";
import { ppoFormSchema, PPO_SAMPLE_PROFILE } from "../schemas/ppoFormSchema";
import type { PPOFormSchema } from "../schemas/ppoFormSchema";
import { apiService, ApiClientError } from "../services/api";
import type { PPOFormData, PPOPredictionResponse } from "../types/placement";

const FIELD_CONFIG: Array<{
  name: keyof PPOFormSchema;
  label: string;
  range: string;
  placeholder: string;
  description: string;
  step?: string;
}> = [
  {
    name: "Technical_Evaluation",
    label: "Technical Evaluation",
    range: "1.0 – 10.0",
    placeholder: "e.g. 8.5",
    description: "Technical skill and evaluation score during internship",
    step: "0.1",
  },
  {
    name: "Task_Completion_Rate",
    label: "Task Completion Rate",
    range: "20.0 – 100.0",
    placeholder: "e.g. 90",
    description: "Percentage of assigned tasks completed",
    step: "0.1",
  },
  {
    name: "Attendance_Rate",
    label: "Attendance Rate",
    range: "51.5 – 100.0",
    placeholder: "e.g. 95",
    description: "Attendance consistency throughout internship",
    step: "0.1",
  },
  {
    name: "Communication_Score",
    label: "Communication Score",
    range: "3.6 – 10.0",
    placeholder: "e.g. 8.5",
    description: "Clarity and effectiveness of communication",
    step: "0.1",
  },
  {
    name: "Manager_Rating",
    label: "Manager Rating",
    range: "1.4 – 10.0",
    placeholder: "e.g. 9.0",
    description: "Overall manager evaluation rating",
    step: "0.1",
  },
  {
    name: "Code_Quality_Score",
    label: "Code Quality Score",
    range: "1.0 – 10.0",
    placeholder: "e.g. 8.8",
    description: "Quality, maintainability, and correctness of work output",
    step: "0.1",
  },
  {
    name: "Teamwork_Score",
    label: "Teamwork Score",
    range: "3.5 – 10.0",
    placeholder: "e.g. 8.2",
    description: "Collaboration and team contribution",
    step: "0.1",
  },
  {
    name: "Deadline_Adherence",
    label: "Deadline Adherence",
    range: "20.0 – 100.0",
    placeholder: "e.g. 90",
    description: "Percentage of deadlines met on time",
    step: "0.1",
  },
];

export const PPOPredictorPage: React.FC = () => {
  const [predictionResult, setPredictionResult] = useState<PPOPredictionResponse | null>(null);
  const [submittedData, setSubmittedData] = useState<PPOFormData | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [apiError, setApiError] = useState<{ message: string; details?: string[] } | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<PPOFormSchema>({
    resolver: zodResolver(ppoFormSchema),
    defaultValues: {
      Technical_Evaluation: "" as any,
      Task_Completion_Rate: "" as any,
      Attendance_Rate: "" as any,
      Communication_Score: "" as any,
      Manager_Rating: "" as any,
      Code_Quality_Score: "" as any,
      Teamwork_Score: "" as any,
      Deadline_Adherence: "" as any,
    },
  });

  const onSubmit = async (data: PPOFormSchema) => {
    setIsSubmitting(true);
    setApiError(null);
    try {
      const response = await apiService.predictPPO(data as PPOFormData);
      setPredictionResult(response);
      setSubmittedData(data as PPOFormData);
    } catch (err: any) {
      if (err instanceof ApiClientError) {
        setApiError({ message: err.message, details: err.details });
      } else {
        setApiError({ message: "An unexpected error occurred during PPO prediction." });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    reset({
      Technical_Evaluation: "" as any,
      Task_Completion_Rate: "" as any,
      Attendance_Rate: "" as any,
      Communication_Score: "" as any,
      Manager_Rating: "" as any,
      Code_Quality_Score: "" as any,
      Teamwork_Score: "" as any,
      Deadline_Adherence: "" as any,
    });
    setPredictionResult(null);
    setSubmittedData(null);
    setApiError(null);
  };

  const loadSample = () => {
    reset(PPO_SAMPLE_PROFILE);
    setApiError(null);
  };

  const ppoPct = predictionResult ? Math.round(predictionResult.ppo_probability * 1000) / 10 : 0;
  const noPpoPct = predictionResult ? Math.round(predictionResult.no_ppo_probability * 1000) / 10 : 0;

  return (
    <div className="space-y-8">
      <div className="border-b border-[#E4E1DA] pb-5">
        <h1 className="font-heading text-2xl sm:text-3xl font-bold tracking-tight text-[#202B38]">
          PPO Prediction
        </h1>
        <p className="mt-1 text-sm text-[#738091] max-w-3xl leading-relaxed">
          Evaluate internship performance indicators to estimate the likelihood of receiving a Pre-Placement Offer.
        </p>
      </div>

      {predictionResult && submittedData ? (
        <div className="space-y-6">
          <div
            className={`rounded-2xl border p-6 sm:p-8 shadow-xs ${
              predictionResult.prediction === 1
                ? "border-[#3D827C]/30 bg-[#EBF3F2]/60"
                : "border-[#C6A66B]/30 bg-[#F7F3E9]/60"
            }`}
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E4E1DA]/60 pb-6">
              <div className="flex items-center gap-3.5">
                <div
                  className={`flex h-12 w-12 items-center justify-center rounded-xl border bg-white ${
                    predictionResult.prediction === 1
                      ? "border-[#3D827C]/30 text-[#3D827C]"
                      : "border-[#C6A66B]/40 text-[#9A7B3E]"
                  }`}
                >
                  {predictionResult.prediction === 1 ? (
                    <CheckCircle2 className="h-6 w-6" />
                  ) : (
                    <Activity className="h-6 w-6" />
                  )}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-semibold tracking-wider text-[#738091] uppercase">
                      PPO Prediction Outcome
                    </span>
                    <span className="rounded-full px-2 py-0.5 text-[10px] font-semibold bg-[#101C2C] text-white">
                      Logistic Regression
                    </span>
                  </div>
                  <h2 className="font-heading text-2xl sm:text-3xl font-bold tracking-tight text-[#202B38]">
                    {predictionResult.prediction_label}
                  </h2>
                </div>
              </div>
              <button
                onClick={handleReset}
                className="inline-flex items-center gap-2 rounded-lg border border-[#E4E1DA] bg-white px-4 py-2 text-xs font-semibold text-[#202B38] hover:bg-[#F6F3ED] transition-colors"
              >
                <RotateCcw className="h-3.5 w-3.5 text-[#738091]" />
                Make Another Prediction
              </button>
            </div>

            <div className="mt-6">
              <div className="flex items-center justify-between text-xs font-semibold text-[#202B38] mb-2">
                <span className="flex items-center gap-1.5 text-[#3D827C]">
                  <span className="h-2.5 w-2.5 rounded-full bg-[#3D827C]" />
                  PPO Probability: {ppoPct}% ({(predictionResult.ppo_probability * 100).toFixed(1)}%)
                </span>
                <span className="flex items-center gap-1.5 text-[#738091]">
                  <span className="h-2.5 w-2.5 rounded-full bg-[#CBD5E1]" />
                  No PPO Probability: {noPpoPct}% ({(predictionResult.no_ppo_probability * 100).toFixed(1)}%)
                </span>
              </div>
              <div className="h-4 w-full overflow-hidden rounded-full bg-[#E4E1DA]/60 p-0.5 flex">
                <div
                  className="h-full rounded-l-full bg-[#3D827C] transition-all duration-700 ease-out"
                  style={{ width: `${Math.max(ppoPct, 3)}%` }}
                />
                <div
                  className="h-full rounded-r-full bg-[#CBD5E1] transition-all duration-700 ease-out"
                  style={{ width: `${Math.max(noPpoPct, 3)}%` }}
                />
              </div>
              <p className="mt-2 text-[11px] text-[#738091]">
                Classification threshold: {predictionResult.threshold.toFixed(2)}. Probabilities are produced by the PPO model for the submitted internship performance profile.
              </p>
            </div>

            <div className="mt-6 flex items-start gap-2.5 rounded-lg border border-[#E4E1DA]/80 bg-white/70 p-3.5 text-xs text-[#738091]">
              <AlertTriangle className="h-4 w-4 shrink-0 text-[#9A7B3E] mt-0.5" />
              <p className="leading-relaxed">
                This prediction is generated using a model trained on synthetic PPO data. Actual PPO decisions depend on company-specific evaluation criteria and cannot be guaranteed.
              </p>
            </div>
          </div>

          <div className="rounded-xl border border-[#E4E1DA] bg-white p-6 shadow-xs">
            <div className="flex items-center gap-2 mb-4">
              <ClipboardList className="h-4 w-4 text-[#3D827C]" />
              <h3 className="font-heading text-base font-semibold text-[#202B38]">
                Submitted Internship Evaluation Profile
              </h3>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              {FIELD_CONFIG.map((f) => (
                <div key={f.name} className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3">
                  <span className="text-[#738091] block text-[11px]">{f.label}</span>
                  <span className="font-heading font-bold text-base text-[#202B38]">
                    {submittedData[f.name]}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-xl border border-[#E4E1DA] bg-white p-4 shadow-xs">
            <div className="flex items-center gap-2 text-xs font-semibold text-[#738091] uppercase tracking-wider">
              <Sparkles className="h-4 w-4 text-[#C6A66B]" />
              <span>Quick fill</span>
            </div>
            <button
              type="button"
              onClick={loadSample}
              className="rounded-md border border-[#3D827C]/30 bg-[#EBF3F2] px-3 py-1.5 text-xs font-medium text-[#3D827C] hover:bg-[#3D827C]/15 transition-colors"
            >
              Load Sample Internship Profile
            </button>
          </div>

          <form
            onSubmit={handleSubmit(onSubmit)}
            className="rounded-2xl border border-[#E4E1DA] bg-white p-6 sm:p-8 shadow-xs space-y-6"
          >
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              {FIELD_CONFIG.map((f) => (
                <div key={f.name}>
                  <label className="block text-xs font-semibold text-[#202B38] mb-1">
                    {f.label} <span className="text-[#738091] font-normal">({f.range})</span>
                  </label>
                  <input
                    type="number"
                    step={f.step || "0.1"}
                    placeholder={f.placeholder}
                    {...register(f.name, { valueAsNumber: true })}
                    className={`w-full rounded-lg border px-3 py-2 text-sm text-[#202B38] placeholder-gray-400 bg-white transition-all focus:border-[#3D827C] focus:ring-1 focus:ring-[#3D827C] ${
                      errors[f.name] ? "border-rose-400 bg-rose-50/30" : "border-[#E4E1DA]"
                    }`}
                  />
                  <div className="mt-1 flex items-center justify-between gap-2 text-[11px] text-[#738091]">
                    <span>{f.description}</span>
                    {errors[f.name] && (
                      <span className="text-rose-600 font-medium">{errors[f.name]?.message as string}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {apiError && (
              <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800">
                <div className="flex items-center gap-2 font-semibold text-rose-900 mb-1">
                  <AlertTriangle className="h-4 w-4 text-rose-600" />
                  <span>{apiError.message}</span>
                </div>
                {apiError.details && apiError.details.length > 0 && (
                  <ul className="list-disc list-inside mt-2 space-y-0.5 text-rose-700">
                    {apiError.details.map((d, i) => (
                      <li key={i}>{d}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            <div className="border-t border-[#E4E1DA] pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
              <button
                type="button"
                onClick={handleReset}
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
                    <span>Evaluating PPO Likelihood...</span>
                  </>
                ) : (
                  <>
                    <span>Predict PPO Status</span>
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
