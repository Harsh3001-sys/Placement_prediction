import React from "react";
import {
  ArrowRight,
  Sliders,
  Database,
  Cpu,
  TrendingUp,
  AlertCircle,
} from "lucide-react";
import type { PageView } from "../types/placement";
import { MetricCard } from "../components/MetricCard";

interface OverviewPageProps {
  onNavigate: (page: PageView) => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({ onNavigate }) => {
  return (
    <div className="space-y-10">
      {/* Editorial Hero Header */}
      <div className="relative overflow-hidden rounded-2xl border border-[#E4E1DA] bg-white p-8 sm:p-12 shadow-xs">
        <div className="max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 rounded-full border border-[#C6A66B]/30 bg-[#F7F3E9] px-3 py-1 text-xs font-semibold text-[#9A7B3E]">
            <span>ACADEMIC CAPSTONE PROJECT</span>
            <span>·</span>
            <span>LOGISTIC REGRESSION PIPELINE</span>
          </div>

          <h1 className="font-heading text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight text-[#202B38] leading-tight">
            Student Intelligence Platform
          </h1>

          <p className="text-base sm:text-lg leading-relaxed text-[#738091] font-sans">
            CareerLens is a unified supervised machine learning decision-support platform featuring two independent prediction systems: Student Placement Prediction and Student PPO Prediction. Each model uses its own artifacts, features, validation, and inference pipeline to provide transparent probabilistic outcomes.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-3">
            <button
              onClick={() => onNavigate("predictor")}
              className="inline-flex items-center gap-2.5 rounded-lg bg-[#101C2C] px-5 py-3 text-sm font-semibold text-white shadow-xs hover:bg-[#192B40] transition-colors"
            >
              <span>Placement Predictor</span>
              <ArrowRight className="h-4 w-4 text-[#C6A66B]" />
            </button>

            <button
              onClick={() => onNavigate("ppo-predictor")}
              className="inline-flex items-center gap-2 rounded-lg border border-[#E4E1DA] bg-white px-5 py-3 text-sm font-semibold text-[#202B38] hover:bg-[#F6F3ED] transition-colors"
            >
              <TrendingUp className="h-4 w-4 text-[#738091]" />
              <span>PPO Predictor</span>
            </button>

            <button
              onClick={() => onNavigate("model-insights")}
              className="inline-flex items-center gap-2 rounded-lg border border-[#E4E1DA] bg-white px-5 py-3 text-sm font-semibold text-[#202B38] hover:bg-[#F6F3ED] transition-colors"
            >
              <Sliders className="h-4 w-4 text-[#738091]" />
              <span>Model Insights</span>
            </button>
          </div>
        </div>
      </div>

      {/* 3-Step Compact Workflow Overview */}
      <div className="rounded-xl border border-[#E4E1DA] bg-white p-6 sm:p-8 shadow-xs">
        <div className="border-b border-[#E4E1DA] pb-4">
          <h2 className="font-heading text-lg font-bold text-[#202B38]">
            Inference Workflow Architecture
          </h2>
          <p className="text-xs text-[#738091]">
            How data flows from student input to deterministic model output
          </p>
        </div>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Step 1 */}
          <div className="relative rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="font-mono text-xs font-bold text-[#3D827C]">
                PHASE 01
              </span>
              <Database className="h-5 w-5 text-[#738091]" />
            </div>
            <h3 className="font-heading text-sm font-bold text-[#202B38]">
              Student Profile Specification
            </h3>
            <p className="mt-1.5 text-xs text-[#738091] leading-relaxed">
              13 parameters entered across academic scores (CGPA, SSC, HSC), experience indicators (internships, projects, certifications), and technical achievements.
            </p>
          </div>

          {/* Step 2 */}
          <div className="relative rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="font-mono text-xs font-bold text-[#3D827C]">
                PHASE 02
              </span>
              <Cpu className="h-5 w-5 text-[#738091]" />
            </div>
            <h3 className="font-heading text-sm font-bold text-[#202B38]">
              StandardScaler & ML Inference
            </h3>
            <p className="mt-1.5 text-xs text-[#738091] leading-relaxed">
              Input vector transformed by the pre-fitted scikit-learn pipeline using zero-mean unit-variance scaling, evaluated by the Logistic Regression classifier.
            </p>
          </div>

          {/* Step 3 */}
          <div className="relative rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="font-mono text-xs font-bold text-[#3D827C]">
                PHASE 03
              </span>
              <TrendingUp className="h-5 w-5 text-[#738091]" />
            </div>
            <h3 className="font-heading text-sm font-bold text-[#202B38]">
              Probabilistic Classification
            </h3>
            <p className="mt-1.5 text-xs text-[#738091] leading-relaxed">
              The model returns discrete predictions ("Placed" / "Not Placed") along with sigmoid probability estimates and individual metric breakdowns.
            </p>
          </div>
        </div>
      </div>

      {/* Model Performance Overview Grid */}
      <div>
        <div className="mb-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1">
          <div>
            <h2 className="font-heading text-lg font-bold text-[#202B38]">
              Test Evaluation Metrics
            </h2>
            <p className="text-xs text-[#738091]">
              Results recorded from the 20% stratified test split (2,000 samples)
            </p>
          </div>
          <span className="text-[11px] font-medium text-[#738091]">
            Algorithm: Logistic Regression (C=5, l2)
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          <MetricCard
            label="Test Accuracy"
            value="80.85%"
            subtext="1,617 of 2,000 correct"
            badge="Verified"
            badgeType="teal"
          />
          <MetricCard
            label="Precision"
            value="77.01%"
            subtext="Positive predictive value"
            badge="Placement"
            badgeType="neutral"
          />
          <MetricCard
            label="Recall"
            value="77.47%"
            subtext="True positive sensitivity"
            badge="Placed"
            badgeType="neutral"
          />
          <MetricCard
            label="F1-Score"
            value="77.24%"
            subtext="Harmonic mean of P & R"
            badge="Balanced"
            badgeType="neutral"
          />
          <MetricCard
            label="ROC-AUC"
            value="0.8840"
            subtext="Area under receiver curve"
            badge="High"
            badgeType="gold"
          />
        </div>
      </div>

      {/* Disclosure Notes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="rounded-xl border border-[#C6A66B]/30 bg-[#F7F3E9] p-6 text-xs text-[#202B38] shadow-xs">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-[#9A7B3E] shrink-0 mt-0.5" />
            <div className="space-y-1.5">
              <h3 className="font-heading text-sm font-bold text-[#9A7B3E]">
                Placement Model Note (Synthetic Features)
              </h3>
              <p className="leading-relaxed text-[#738091]">
                The placement dataset includes three synthetically generated features (LeetCode Problems Solved, Hackathon Wins, and Research Publications). Reported metrics reflect performance on the project’s evaluation dataset and are for academic demonstration.
              </p>
            </div>
          </div>
        </div>
        <div className="rounded-xl border border-[#C6A66B]/30 bg-[#F7F3E9] p-6 text-xs text-[#202B38] shadow-xs">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-[#9A7B3E] shrink-0 mt-0.5" />
            <div className="space-y-1.5">
              <h3 className="font-heading text-sm font-bold text-[#9A7B3E]">
                PPO Model Note (Synthetic Dataset)
              </h3>
              <p className="leading-relaxed text-[#738091]">
                The PPO Prediction model was trained and evaluated on synthetic PPO data. Predictions are indicative only and actual PPO decisions depend on company-specific evaluation criteria.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
