import React, { useEffect, useState } from "react";
import { RefreshCw, Server, CheckCircle2, AlertCircle, Clock } from "lucide-react";
import { apiService } from "../services/api";
import type { HealthResponse, PPOHealthResponse } from "../types/placement";

type Status = "checking" | "healthy" | "degraded" | "offline";

const badge = (status: Status) => {
  if (status === "healthy") return "border-emerald-200 bg-emerald-50 text-emerald-800";
  if (status === "checking") return "border-amber-200 bg-amber-50 text-amber-800";
  if (status === "degraded") return "border-amber-200 bg-amber-50 text-amber-800";
  return "border-rose-200 bg-rose-50 text-rose-800";
};

export const ApiStatusPage: React.FC = () => {
  const [placement, setPlacement] = useState<HealthResponse | null>(null);
  const [ppo, setPpo] = useState<PPOHealthResponse | null>(null);
  const [placementStatus, setPlacementStatus] = useState<Status>("checking");
  const [ppoStatus, setPpoStatus] = useState<Status>("checking");
  const [loading, setLoading] = useState(false);

  const refresh = async () => {
    setLoading(true);
    setPlacementStatus("checking");
    setPpoStatus("checking");

    const [p1, p2] = await Promise.allSettled([apiService.getHealth(), apiService.getPPOHealth()]);

    if (p1.status === "fulfilled") {
      setPlacement(p1.value);
      setPlacementStatus(p1.value.status === "healthy" && p1.value.model_loaded ? "healthy" : "degraded");
    } else {
      setPlacement(null);
      setPlacementStatus("offline");
    }

    if (p2.status === "fulfilled") {
      setPpo(p2.value);
      setPpoStatus(p2.value.status === "healthy" && p2.value.model_loaded ? "healthy" : "degraded");
    } else {
      setPpo(null);
      setPpoStatus("offline");
    }

    setLoading(false);
  };

  useEffect(() => {
    refresh();
  }, []);

  const StatusIcon = ({ status }: { status: Status }) => {
    if (status === "checking") return <Clock className="h-4 w-4 animate-pulse" />;
    if (status === "healthy") return <CheckCircle2 className="h-4 w-4" />;
    return <AlertCircle className="h-4 w-4" />;
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 border-b border-[#E4E1DA] pb-5">
        <div>
          <h1 className="font-heading text-2xl sm:text-3xl font-bold tracking-tight text-[#202B38]">
            API Status
          </h1>
          <p className="mt-1 text-sm text-[#738091] max-w-3xl leading-relaxed">
            Independent health and readiness status for the Placement Prediction and PPO Prediction services.
          </p>
        </div>
        <button
          onClick={refresh}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-lg border border-[#E4E1DA] bg-white px-4 py-2 text-xs font-semibold text-[#202B38] hover:bg-[#F6F3ED] transition-colors disabled:opacity-60"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          Refresh Status
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-xl border border-[#E4E1DA] bg-white p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Server className="h-5 w-5 text-[#3D827C]" />
              <h2 className="font-heading text-lg font-bold text-[#202B38]">Placement Prediction API</h2>
            </div>
            <div className={`inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-medium ${badge(placementStatus)}`}>
              <StatusIcon status={placementStatus} />
              <span className="capitalize">{placementStatus}</span>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3">
              <span className="text-[#738091] block text-[11px]">Endpoint</span>
              <span className="font-semibold text-[#202B38]">GET /api/health</span>
            </div>
            <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3">
              <span className="text-[#738091] block text-[11px]">Model Loaded</span>
              <span className="font-semibold text-[#202B38]">{placement?.model_loaded ? "Yes" : placementStatus === "offline" ? "Unknown" : "No"}</span>
            </div>
            <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3">
              <span className="text-[#738091] block text-[11px]">Model</span>
              <span className="font-semibold text-[#202B38]">{placement?.model_name || "Placement Model"}</span>
            </div>
            <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3">
              <span className="text-[#738091] block text-[11px]">Features</span>
              <span className="font-semibold text-[#202B38]">{placement?.n_features ?? "—"}</span>
            </div>
          </div>
          <div className="text-[11px] text-[#738091]">
            Prediction endpoint: <code className="bg-[#F6F3ED] px-1.5 py-0.5 rounded border border-[#E4E1DA]">POST /api/predict</code>
          </div>
        </div>

        <div className="rounded-xl border border-[#E4E1DA] bg-white p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Server className="h-5 w-5 text-[#9A7B3E]" />
              <h2 className="font-heading text-lg font-bold text-[#202B38]">PPO Prediction API</h2>
            </div>
            <div className={`inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-xs font-medium ${badge(ppoStatus)}`}>
              <StatusIcon status={ppoStatus} />
              <span className="capitalize">{ppoStatus}</span>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3">
              <span className="text-[#738091] block text-[11px]">Endpoint</span>
              <span className="font-semibold text-[#202B38]">GET /api/ppo/health</span>
            </div>
            <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3">
              <span className="text-[#738091] block text-[11px]">Model Loaded</span>
              <span className="font-semibold text-[#202B38]">{ppo?.model_loaded ? "Yes" : ppoStatus === "offline" ? "Unknown" : "No"}</span>
            </div>
            <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3">
              <span className="text-[#738091] block text-[11px]">Features</span>
              <span className="font-semibold text-[#202B38]">{ppo?.n_features ?? "—"}</span>
            </div>
            <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3">
              <span className="text-[#738091] block text-[11px]">Threshold</span>
              <span className="font-semibold text-[#202B38]">{ppo?.threshold != null ? ppo.threshold.toFixed(2) : "—"}</span>
            </div>
          </div>
          {ppo?.load_error && (
            <div className="rounded-lg border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800">
              {ppo.load_error}
            </div>
          )}
          <div className="text-[11px] text-[#738091]">
            Prediction endpoint: <code className="bg-[#F6F3ED] px-1.5 py-0.5 rounded border border-[#E4E1DA]">POST /api/ppo/predict</code>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-[#E4E1DA] bg-[#FBF9F5] p-5 text-xs text-[#738091]">
        <strong className="text-[#202B38]">Isolation note:</strong> Placement and PPO services run with separate model artifacts, feature schemas, validation, and endpoints. One model being unavailable does not prevent the other from serving predictions.
      </div>
    </div>
  );
};
