import React from "react";
import {
  LayoutDashboard,
  Target,
  BarChart3,
  Server,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Clock,
  X,
  BriefcaseBusiness,
  BrainCircuit,
  Users,
} from "lucide-react";
import type { PageView } from "../types/placement";
import type { ConnectionStatus } from "../hooks/useApiHealth";

interface SidebarProps {
  currentPage: PageView;
  onPageChange: (page: PageView) => void;
  apiStatus: ConnectionStatus;
  onRefreshHealth: () => void;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentPage,
  onPageChange,
  apiStatus,
  onRefreshHealth,
  isOpenMobile,
  onCloseMobile,
}) => {
  const navItems = [
    {
      id: "overview" as PageView,
      label: "Overview",
      description: "Platform summary & workflow",
      icon: LayoutDashboard,
    },
    {
      id: "predictor" as PageView,
      label: "Placement Predictor",
      description: "13-Feature student inference",
      icon: Target,
    },
    {
      id: "ppo-predictor" as PageView,
      label: "PPO Predictor",
      description: "8-Feature internship evaluation",
      icon: BriefcaseBusiness,
    },
    {
      id: "skill-intelligence" as PageView,
      label: "Skill Intelligence",
      description: "Role readiness & skill gap analysis",
      icon: BrainCircuit,
    },
    {
      id: "student-segmentation" as PageView,
      label: "Student Segmentation",
      description: "Role-aware K-Means clusters",
      icon: Users,
    },
    {
      id: "model-insights" as PageView,
      label: "Model Insights",
      description: "Metrics & model transparency",
      icon: BarChart3,
    },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpenMobile && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-xs lg:hidden"
          onClick={onCloseMobile}
        />
      )}

      {/* Sidebar Shell */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 flex w-72 flex-col bg-[#101C2C] text-white transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 ${
          isOpenMobile ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Brand Header */}
        <div className="flex h-20 items-center justify-between border-b border-white/8 px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#192B40] border border-white/10 text-[#C6A66B]">
              <Target className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-heading text-lg font-bold tracking-tight text-white">
                  CareerLens
                </span>
                <span className="rounded bg-[#C6A66B]/20 px-1.5 py-0.5 text-[10px] font-semibold text-[#C6A66B]">
                  ML CP
                </span>
              </div>
              <p className="text-[11px] font-medium tracking-wider text-[#738091] uppercase">
                Placement Intelligence
              </p>
            </div>
          </div>

          <button
            onClick={onCloseMobile}
            className="rounded p-1.5 text-gray-400 hover:bg-white/10 lg:hidden"
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation Section */}
        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="mb-2 px-3 text-[11px] font-semibold tracking-wider text-[#738091] uppercase">
            Navigation
          </div>

          <nav className="space-y-1.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;

              return (
                <button
                  key={item.id}
                  onClick={() => {
                    onPageChange(item.id);
                    onCloseMobile();
                  }}
                  className={`group relative flex w-full items-center gap-3.5 rounded-lg px-3.5 py-3 text-left transition-all duration-150 ${
                    isActive
                      ? "bg-[#192B40] text-white font-medium shadow-xs"
                      : "text-gray-300 hover:bg-white/5 hover:text-white"
                  }`}
                >
                  {/* Subtle active left pill */}
                  {isActive && (
                    <span className="absolute left-0 top-2 bottom-2 w-1 rounded-r-md bg-[#3D827C]" />
                  )}

                  <Icon
                    className={`h-5 w-5 shrink-0 transition-colors ${
                      isActive
                        ? "text-[#3D827C]"
                        : "text-[#738091] group-hover:text-gray-200"
                    }`}
                  />

                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-medium tracking-tight">
                      {item.label}
                    </div>
                    <div className="text-[11px] text-[#738091] truncate">
                      {item.description}
                    </div>
                  </div>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Backend Status Section */}
        <div className="border-t border-white/8 p-4">
          <div className="rounded-lg bg-[#192B40]/70 p-3.5 border border-white/5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Server className="h-3.5 w-3.5 text-[#738091]" />
                <span className="text-[11px] font-semibold tracking-wider text-[#738091] uppercase">
                  Placement API
                </span>
              </div>
              <button
                onClick={onRefreshHealth}
                title="Ping placement backend service"
                className="rounded p-1 text-gray-400 hover:bg-white/10 hover:text-white transition-colors"
              >
                <RefreshCw
                  className={`h-3 w-3 ${
                    apiStatus === "checking" ? "animate-spin text-[#C6A66B]" : ""
                  }`}
                />
              </button>
            </div>

            <div className="mt-2.5 flex items-center gap-2">
              {apiStatus === "connected" && (
                <>
                  <span className="relative flex h-2 w-2">
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#3D827C] opacity-75"></span>
                    <span className="relative inline-flex h-2 w-2 rounded-full bg-[#3D827C]"></span>
                  </span>
                  <span className="text-xs font-medium text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3 inline" /> Placement API Connected
                  </span>
                </>
              )}

              {apiStatus === "checking" && (
                <>
                  <span className="h-2 w-2 rounded-full bg-[#C6A66B] animate-pulse" />
                  <span className="text-xs font-medium text-[#C6A66B] flex items-center gap-1">
                    <Clock className="h-3 w-3 inline" /> Checking...
                  </span>
                </>
              )}

              {apiStatus === "disconnected" && (
                <>
                  <span className="h-2 w-2 rounded-full bg-rose-400" />
                  <span className="text-xs font-medium text-rose-300 flex items-center gap-1">
                    <AlertCircle className="h-3 w-3 inline" /> Placement API Offline
                  </span>
                </>
              )}
            </div>

            <div className="mt-2 text-[10px] text-[#738091]">
              Service health details are available via backend API endpoints.
            </div>
          </div>

          <div className="mt-3 px-1 text-center text-[11px] text-[#738091]">
            CareerLens Â· Student Intelligence
          </div>
        </div>
      </aside>
    </>
  );
};

