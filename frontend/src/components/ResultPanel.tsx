import React, { useState } from "react";
import {
  CheckCircle2,
  AlertCircle,
  RotateCcw,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  GraduationCap,
  Briefcase,
  Code2,
} from "lucide-react";
import type { PredictionResponse, StudentFormData } from "../types/placement";

interface ResultPanelProps {
  result: PredictionResponse;
  submittedProfile: StudentFormData;
  onReset: () => void;
}

export const ResultPanel: React.FC<ResultPanelProps> = ({
  result,
  submittedProfile,
  onReset,
}) => {
  const [showProfileDetails, setShowProfileDetails] = useState(false);
  const isPlaced = result.prediction === "Placed";
  const pPlacedPct = Math.round(result.placement_probability * 100);
  const pNotPlacedPct = Math.round(result.not_placed_probability * 100);

  return (
    <div className="space-y-6">
      {/* Primary Result Banner */}
      <div
        className={`rounded-2xl border p-6 sm:p-8 transition-all ${
          isPlaced
            ? "border-[#3D827C]/30 bg-[#EBF3F2]/60 shadow-xs"
            : "border-[#C6A66B]/30 bg-[#F7F3E9]/60 shadow-xs"
        }`}
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E4E1DA]/60 pb-6">
          <div className="flex items-center gap-3.5">
            <div
              className={`flex h-12 w-12 items-center justify-center rounded-xl border ${
                isPlaced
                  ? "border-[#3D827C]/30 bg-white text-[#3D827C]"
                  : "border-[#C6A66B]/40 bg-white text-[#9A7B3E]"
              }`}
            >
              {isPlaced ? (
                <CheckCircle2 className="h-6 w-6" />
              ) : (
                <AlertCircle className="h-6 w-6" />
              )}
            </div>

            <div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-semibold tracking-wider text-[#738091] uppercase">
                  Prediction Outcome
                </span>
                <span
                  className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${
                    isPlaced
                      ? "bg-[#3D827C] text-white"
                      : "bg-[#9A7B3E] text-white"
                  }`}
                >
                  {result.model}
                </span>
              </div>
              <h2 className="font-heading text-2xl sm:text-3xl font-bold tracking-tight text-[#202B38]">
                {result.prediction}
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onReset}
              className="inline-flex items-center gap-2 rounded-lg border border-[#E4E1DA] bg-white px-4 py-2 text-xs font-semibold text-[#202B38] shadow-xs hover:bg-[#F6F3ED] transition-colors"
            >
              <RotateCcw className="h-3.5 w-3.5 text-[#738091]" />
              Make Another Prediction
            </button>
          </div>
        </div>

        {/* Horizontal Probability Visualization */}
        <div className="mt-6">
          <div className="flex items-center justify-between text-xs font-semibold text-[#202B38] mb-2">
            <span className="flex items-center gap-1.5 text-[#3D827C]">
              <span className="h-2.5 w-2.5 rounded-full bg-[#3D827C]" />
              Placed Probability: {pPlacedPct}% ({(result.placement_probability * 100).toFixed(1)}%)
            </span>
            <span className="flex items-center gap-1.5 text-[#738091]">
              <span className="h-2.5 w-2.5 rounded-full bg-[#CBD5E1]" />
              Not Placed: {pNotPlacedPct}% ({(result.not_placed_probability * 100).toFixed(1)}%)
            </span>
          </div>

          {/* Dual Segment Progress Bar */}
          <div className="h-4 w-full overflow-hidden rounded-full bg-[#E4E1DA]/60 p-0.5 flex">
            <div
              className="h-full rounded-l-full bg-[#3D827C] transition-all duration-700 ease-out"
              style={{ width: `${Math.max(pPlacedPct, 3)}%` }}
              title={`Placement probability: ${pPlacedPct}%`}
            />
            <div
              className="h-full rounded-r-full bg-[#CBD5E1] transition-all duration-700 ease-out"
              style={{ width: `${Math.max(pNotPlacedPct, 3)}%` }}
              title={`Not placed probability: ${pNotPlacedPct}%`}
            />
          </div>

          <p className="mt-2 text-[11px] text-[#738091]">
            * Estimates generated via logistic sigmoid function over 13 standardized features. Probabilities reflect statistical class affiliation within the model distribution.
          </p>
        </div>

        {/* Responsible Disclaimer Box */}
        <div className="mt-6 flex items-start gap-2.5 rounded-lg border border-[#E4E1DA]/80 bg-white/70 p-3.5 text-xs text-[#738091]">
          <ShieldCheck className="h-4 w-4 shrink-0 text-[#3D827C] mt-0.5" />
          <p className="leading-relaxed">
            <strong>Academic Evaluation Notice:</strong> This prediction is a probabilistic academic assessment derived from a supervised machine learning model. It does not represent an actual campus recruitment decision or guaranteed employment offer.
          </p>
        </div>
      </div>

      {/* Submitted Profile Summary Panel */}
      <div className="rounded-xl border border-[#E4E1DA] bg-white p-6 shadow-xs">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-heading text-base font-semibold text-[#202B38]">
              Submitted Candidate Profile
            </h3>
            <p className="text-xs text-[#738091]">
              Overview of the 13 feature inputs provided for this evaluation
            </p>
          </div>

          <button
            onClick={() => setShowProfileDetails(!showProfileDetails)}
            className="flex items-center gap-1.5 rounded-md border border-[#E4E1DA] px-3 py-1.5 text-xs font-medium text-[#202B38] hover:bg-[#F6F3ED] transition-colors"
          >
            <span>{showProfileDetails ? "Collapse Details" : "Review Student Details"}</span>
            {showProfileDetails ? (
              <ChevronUp className="h-3.5 w-3.5 text-[#738091]" />
            ) : (
              <ChevronDown className="h-3.5 w-3.5 text-[#738091]" />
            )}
          </button>
        </div>

        {/* Compact Grid Summary */}
        <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="rounded-lg bg-[#F6F3ED] p-3">
            <span className="text-[#738091] block text-[11px]">CGPA</span>
            <span className="font-heading font-bold text-base text-[#202B38]">
              {submittedProfile.CGPA} / 10.0
            </span>
          </div>

          <div className="rounded-lg bg-[#F6F3ED] p-3">
            <span className="text-[#738091] block text-[11px]">Aptitude Test</span>
            <span className="font-heading font-bold text-base text-[#202B38]">
              {submittedProfile.AptitudeTestScore} / 100
            </span>
          </div>

          <div className="rounded-lg bg-[#F6F3ED] p-3">
            <span className="text-[#738091] block text-[11px]">Placement Training</span>
            <span
              className={`font-heading font-bold text-base ${
                submittedProfile.PlacementTraining === "Yes"
                  ? "text-[#3D827C]"
                  : "text-[#738091]"
              }`}
            >
              {submittedProfile.PlacementTraining}
            </span>
          </div>

          <div className="rounded-lg bg-[#F6F3ED] p-3">
            <span className="text-[#738091] block text-[11px]">Projects & Internships</span>
            <span className="font-heading font-bold text-base text-[#202B38]">
              {submittedProfile.Projects} Proj · {submittedProfile.Internships} Intern
            </span>
          </div>
        </div>

        {/* Expanded Detailed Breakdown */}
        {showProfileDetails && (
          <div className="mt-6 border-t border-[#E4E1DA] pt-6 space-y-5 animate-in fade-in-50 duration-200">
            {/* Academic section */}
            <div>
              <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-[#202B38]">
                <GraduationCap className="h-4 w-4 text-[#3D827C]" />
                Academic Background
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs">
                <div className="border border-[#E4E1DA] rounded-md p-2.5 bg-[#FBF9F5]">
                  <span className="text-[11px] text-[#738091] block">CGPA</span>
                  <span className="font-semibold text-[#202B38]">{submittedProfile.CGPA}</span>
                </div>
                <div className="border border-[#E4E1DA] rounded-md p-2.5 bg-[#FBF9F5]">
                  <span className="text-[11px] text-[#738091] block">SSC Marks (10th)</span>
                  <span className="font-semibold text-[#202B38]">{submittedProfile.SSC_Marks}%</span>
                </div>
                <div className="border border-[#E4E1DA] rounded-md p-2.5 bg-[#FBF9F5]">
                  <span className="text-[11px] text-[#738091] block">HSC Marks (12th)</span>
                  <span className="font-semibold text-[#202B38]">{submittedProfile.HSC_Marks}%</span>
                </div>
                <div className="border border-[#E4E1DA] rounded-md p-2.5 bg-[#FBF9F5]">
                  <span className="text-[11px] text-[#738091] block">Aptitude Score</span>
                  <span className="font-semibold text-[#202B38]">{submittedProfile.AptitudeTestScore} / 100</span>
                </div>
                <div className="border border-[#E4E1DA] rounded-md p-2.5 bg-[#FBF9F5]">
                  <span className="text-[11px] text-[#738091] block">Soft Skills Rating</span>
                  <span className="font-semibold text-[#202B38]">{submittedProfile.SoftSkillsRating} / 5.0</span>
                </div>
              </div>
            </div>

            {/* Preparation section */}
            <div>
              <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-[#202B38]">
                <Briefcase className="h-4 w-4 text-[#3D827C]" />
                Experience & Preparation
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs">
                <div className="border border-[#E4E1DA] rounded-md p-2.5 bg-[#FBF9F5]">
                  <span className="text-[11px] text-[#738091] block">Internships</span>
                  <span className="font-semibold text-[#202B38]">{submittedProfile.Internships}</span>
                </div>
                <div className="border border-[#E4E1DA] rounded-md p-2.5 bg-[#FBF9F5]">
                  <span className="text-[11px] text-[#738091] block">Projects</span>
                  <span className="font-semibold text-[#202B38]">{submittedProfile.Projects}</span>
                </div>
                <div className="border border-[#E4E1DA] rounded-md p-2.5 bg-[#FBF9F5]">
                  <span className="text-[11px] text-[#738091] block">Workshops/Certs</span>
                  <span className="font-semibold text-[#202B38]">{submittedProfile["Workshops/Certifications"]}</span>
                </div>
                <div className="border border-[#E4E1DA] rounded-md p-2.5 bg-[#FBF9F5]">
                  <span className="text-[11px] text-[#738091] block">Placement Training</span>
                  <span className="font-semibold text-[#202B38]">{submittedProfile.PlacementTraining}</span>
                </div>
                <div className="border border-[#E4E1DA] rounded-md p-2.5 bg-[#FBF9F5]">
                  <span className="text-[11px] text-[#738091] block">Extracurricular</span>
                  <span className="font-semibold text-[#202B38]">{submittedProfile.ExtracurricularActivities}</span>
                </div>
              </div>
            </div>

            {/* Technical section */}
            <div>
              <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-[#202B38]">
                <Code2 className="h-4 w-4 text-[#3D827C]" />
                Technical & Research (Synthetic in Dataset)
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                <div className="border border-[#E4E1DA] rounded-md p-2.5 bg-[#FBF9F5]">
                  <span className="text-[11px] text-[#738091] block">LeetCode Solved</span>
                  <span className="font-semibold text-[#202B38]">{submittedProfile.LeetCode_Problems_Solved}</span>
                </div>
                <div className="border border-[#E4E1DA] rounded-md p-2.5 bg-[#FBF9F5]">
                  <span className="text-[11px] text-[#738091] block">Hackathon Wins</span>
                  <span className="font-semibold text-[#202B38]">{submittedProfile.Hackathon_Wins}</span>
                </div>
                <div className="border border-[#E4E1DA] rounded-md p-2.5 bg-[#FBF9F5]">
                  <span className="text-[11px] text-[#738091] block">Publications</span>
                  <span className="font-semibold text-[#202B38]">{submittedProfile.Publications}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
