import React from "react";
import { Menu, Activity, Sparkles, Terminal } from "lucide-react";
import type { PageView } from "../types/placement";
import type { ConnectionStatus } from "../hooks/useApiHealth";

interface TopNavProps {
  currentPage: PageView;
  apiStatus: ConnectionStatus;
  onOpenMobile: () => void;
}

const PAGE_TITLES: Record<PageView, { title: string; subtitle: string }> = {
  overview: {
    title: "System Overview",
    subtitle: "Unified student intelligence platform overview",
  },
  predictor: {
    title: "Placement Predictor",
    subtitle: "Inference across 13 multidimensional student features",
  },
  "ppo-predictor": {
    title: "PPO Predictor",
    subtitle: "Internship performance evaluation for PPO likelihood",
  },
  "skill-intelligence": {
    title: "Skill Intelligence",
    subtitle: "Role-based skill gap analysis, readiness, and improvement roadmap",
  },
  "student-segmentation": {
    title: "Student Segmentation",
    subtitle: "Role-aware K-Means clustering insights and personal segment analysis",
  },
  "model-insights": {
    title: "Model Insights & Transparency",
    subtitle: "Independent metrics and transparency for both ML models",
  },
};

export const TopNav: React.FC<TopNavProps> = ({
  currentPage,
  apiStatus,
  onOpenMobile,
}) => {
  const current = PAGE_TITLES[currentPage];

  return (
    <header className="sticky top-0 z-30 flex h-20 w-full items-center justify-between border-b border-[#E4E1DA] bg-white/95 px-6 backdrop-blur-sm">
      {/* Left: Mobile trigger & breadcrumb */}
      <div className="flex items-center gap-4">
        <button
          onClick={onOpenMobile}
          className="rounded-md border border-[#E4E1DA] p-2 text-[#738091] hover:bg-[#F6F3ED] hover:text-[#202B38] lg:hidden"
          aria-label="Open navigation"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div>
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-semibold tracking-wider text-[#738091] uppercase">
              CareerLens
            </span>
            <span className="text-gray-300">/</span>
            <span className="text-xs font-medium text-[#3D827C]">
              {current.title}
            </span>
          </div>
          <h1 className="text-lg font-semibold tracking-tight text-[#202B38]">
            {current.title}
          </h1>
        </div>
      </div>

      {/* Right: Project Badges & Status */}
      <div className="flex items-center gap-3">
        {/* ML Project Label */}
        <div className="hidden sm:flex items-center gap-2 rounded-md border border-[#E4E1DA] bg-[#F6F3ED] px-3 py-1.5 text-xs text-[#202B38]">
          <Terminal className="h-3.5 w-3.5 text-[#3D827C]" />
          <span className="font-semibold tracking-wide text-[11px] uppercase">
            ML PROJECT
          </span>
          <span className="text-[#738091]">Â·</span>
          <span className="text-[#738091]">LogReg Pipeline</span>
        </div>

        {/* Live Connectivity Badge */}
        <div
          className={`flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-medium ${
            apiStatus === "connected"
              ? "border-emerald-200 bg-emerald-50 text-emerald-800"
              : apiStatus === "checking"
              ? "border-amber-200 bg-amber-50 text-amber-800"
              : "border-rose-200 bg-rose-50 text-rose-800"
          }`}
        >
          <Activity
            className={`h-3.5 w-3.5 ${
              apiStatus === "connected"
                ? "text-emerald-600 animate-pulse"
                : apiStatus === "checking"
                ? "text-amber-600 animate-spin"
                : "text-rose-600"
            }`}
          />
          <span className="hidden md:inline">
            {apiStatus === "connected"
              ? "API Connected"
              : apiStatus === "checking"
              ? "Pinging Backend"
              : "Backend Offline"}
          </span>
        </div>

        {/* Academic Identity Pill */}
        <div className="hidden lg:flex items-center gap-2 border-l border-[#E4E1DA] pl-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#101C2C] text-[#C6A66B]">
            <Sparkles className="h-4 w-4" />
          </div>
          <div className="text-left text-xs leading-tight">
            <div className="font-semibold text-[#202B38]">Academic Demo</div>
            <div className="text-[11px] text-[#738091]">scikit-learn 1.6+</div>
          </div>
        </div>
      </div>
    </header>
  );
};

