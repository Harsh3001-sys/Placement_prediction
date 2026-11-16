import React, { useEffect, useState } from "react";
import { ShieldAlert, HelpCircle, AlertTriangle } from "lucide-react";
import { MetricCard } from "../components/MetricCard";
import { ConfusionMatrix } from "../components/ConfusionMatrix";
import { RocCurveChart } from "../components/RocCurveChart";
import { FeatureImportanceChart } from "../components/FeatureImportanceChart";
import { apiService } from "../services/api";
import type { ModelInfoResponse, PPOModelInfoResponse } from "../types/placement";

const PPO_COEFFICIENTS: Record<string, number> = {
  Technical_Evaluation: 0.712782,
  Task_Completion_Rate: 0.542007,
  Manager_Rating: 0.461836,
  Code_Quality_Score: 0.296444,
  Communication_Score: 0.2101,
  Deadline_Adherence: 0.162467,
  Attendance_Rate: 0.149356,
  Teamwork_Score: 0.1201,
};

const PPO_EVAL = {
  test_accuracy: 0.8229,
  precision: 0.8644,
  recall: 0.8916,
  f1_score: 0.8778,
  roc_auc: 0.8852,
};

export const ModelInsightsPage: React.FC = () => {
  const [modelInfo, setModelInfo] = useState<ModelInfoResponse | null>(null);
  const [ppoInfo, setPpoInfo] = useState<PPOModelInfoResponse | null>(null);

  useEffect(() => {
    apiService.getModelInfo().then(setModelInfo).catch(() => {});
    apiService.getPPOModelInfo().then(setPpoInfo).catch(() => {});
  }, []);

  const ppoCoeffs = ppoInfo?.coefficients || PPO_COEFFICIENTS;
  const ppoEval = ppoInfo?.evaluation || PPO_EVAL;

  return (
    <div className="space-y-10">
      <div className="border-b border-[#E4E1DA] pb-5">
        <div className="inline-flex items-center gap-2 rounded-full border border-[#3D827C]/30 bg-[#EBF3F2] px-3 py-1 text-xs font-semibold text-[#3D827C] mb-2">
          <span>MODEL TRANSPARENCY & VALIDATION</span>
        </div>
        <h1 className="font-heading text-2xl sm:text-3xl font-bold tracking-tight text-[#202B38]">
          Model Architecture & Empirical Insights
        </h1>
        <p className="mt-1 text-sm text-[#738091] max-w-3xl leading-relaxed">
          Independent technical documentation for both prediction systems: Student Placement Prediction and Student PPO Prediction.
        </p>
      </div>

      {/* Placement Prediction Model */}
      <section className="space-y-6">
        <div className="rounded-xl border border-[#E4E1DA] bg-white p-6 sm:p-8 shadow-xs">
          <div className="border-b border-[#E4E1DA] pb-4 mb-6 flex items-start justify-between gap-4">
            <div>
              <h2 className="font-heading text-xl font-bold text-[#202B38]">Placement Prediction Model</h2>
              <p className="text-xs text-[#738091] mt-1">
                Existing student placement likelihood model (preserved). Serialized scikit-learn pipeline with standardized features.
              </p>
            </div>
            <span className="rounded-full border border-[#3D827C]/30 bg-[#EBF3F2] px-2.5 py-1 text-[11px] font-semibold text-[#3D827C]">
              Independent System
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 text-xs mb-6">
            <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3.5">
              <span className="text-[#738091] block text-[11px] uppercase tracking-wider font-semibold">Algorithm</span>
              <span className="font-bold text-[#202B38] mt-1 block">Logistic Regression</span>
              <span className="text-[10px] text-[#738091]">liblinear solver</span>
            </div>
            <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3.5">
              <span className="text-[#738091] block text-[11px] uppercase tracking-wider font-semibold">Preprocessing</span>
              <span className="font-bold text-[#202B38] mt-1 block">StandardScaler</span>
              <span className="text-[10px] text-[#738091]">Pipeline step</span>
            </div>
            <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3.5">
              <span className="text-[#738091] block text-[11px] uppercase tracking-wider font-semibold">Dataset Size</span>
              <span className="font-bold text-[#202B38] mt-1 block">10,000 Rows</span>
              <span className="text-[10px] text-[#738091]">Institutional CP</span>
            </div>
            <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3.5">
              <span className="text-[#738091] block text-[11px] uppercase tracking-wider font-semibold">Train / Test Split</span>
              <span className="font-bold text-[#202B38] mt-1 block">80 / 20 Stratified</span>
              <span className="text-[10px] text-[#738091]">8,000 / 2,000</span>
            </div>
            <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3.5">
              <span className="text-[#738091] block text-[11px] uppercase tracking-wider font-semibold">Regularization</span>
              <span className="font-bold text-[#202B38] mt-1 block">L2 (C = 5.0)</span>
              <span className="text-[10px] text-[#738091]">max_iter = 3000</span>
            </div>
            <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3.5">
              <span className="text-[#738091] block text-[11px] uppercase tracking-wider font-semibold">Input Vector</span>
              <span className="font-bold text-[#202B38] mt-1 block">13 Features</span>
              <span className="text-[10px] text-[#738091]">10 real + 3 synthetic</span>
            </div>
          </div>

          <div className="mb-4">
            <h3 className="font-heading text-lg font-bold text-[#202B38]">Test Set Evaluation Summary</h3>
            <p className="text-xs text-[#738091]">Recorded performance on the 2,000 held-out student records</p>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            <MetricCard label="Test Accuracy" value="80.85%" subtext="1,617 of 2,000 correct decisions" badge="Primary" badgeType="teal" />
            <MetricCard label="Precision" value="77.01%" subtext="650 / 844 predicted Placed" badge="P(Placed|Pred)" badgeType="neutral" />
            <MetricCard label="Recall (Sensitivity)" value="77.47%" subtext="650 / 839 actual Placed" badge="True Pos Rate" badgeType="neutral" />
            <MetricCard label="F1-Score" value="77.24%" subtext="Balanced harmonic mean" badge="Balance" badgeType="neutral" />
            <MetricCard label="ROC-AUC" value="0.8840" subtext="Area under ROC curve" badge="Excellent" badgeType="gold" />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
          <ConfusionMatrix data={modelInfo?.evaluation?.confusion_matrix} />
          <RocCurveChart points={modelInfo?.roc_curve} auc={modelInfo?.evaluation?.roc_auc ?? 0.884} />
        </div>
        <FeatureImportanceChart coefficients={modelInfo?.coefficients} />
      </section>

      {/* PPO Prediction Model */}
      <section className="space-y-6">
        <div className="rounded-xl border border-[#E4E1DA] bg-white p-6 sm:p-8 shadow-xs">
          <div className="border-b border-[#E4E1DA] pb-4 mb-6 flex items-start justify-between gap-4">
            <div>
              <h2 className="font-heading text-xl font-bold text-[#202B38]">PPO Prediction Model</h2>
              <p className="text-xs text-[#738091] mt-1">
                Independent internship-performance model predicting Pre-Placement Offer likelihood.
              </p>
            </div>
            <span className="rounded-full border border-[#C6A66B]/30 bg-[#F7F3E9] px-2.5 py-1 text-[11px] font-semibold text-[#9A7B3E]">
              Synthetic Dataset Evaluation
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 text-xs mb-6">
            <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3.5">
              <span className="text-[#738091] block text-[11px] uppercase tracking-wider font-semibold">Algorithm</span>
              <span className="font-bold text-[#202B38] mt-1 block">Logistic Regression</span>
              <span className="text-[10px] text-[#738091]">Serialized pipeline</span>
            </div>
            <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3.5">
              <span className="text-[#738091] block text-[11px] uppercase tracking-wider font-semibold">Input Features</span>
              <span className="font-bold text-[#202B38] mt-1 block">8 Features</span>
              <span className="text-[10px] text-[#738091]">Internship indicators</span>
            </div>
            <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3.5">
              <span className="text-[#738091] block text-[11px] uppercase tracking-wider font-semibold">Dataset Records</span>
              <span className="font-bold text-[#202B38] mt-1 block">8,017</span>
              <span className="text-[10px] text-[#738091]">Synthetic PPO Dataset V3</span>
            </div>
            <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3.5">
              <span className="text-[#738091] block text-[11px] uppercase tracking-wider font-semibold">Threshold</span>
              <span className="font-bold text-[#202B38] mt-1 block">0.50</span>
              <span className="text-[10px] text-[#738091]">PPO likelihood cutoff</span>
            </div>
            <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3.5">
              <span className="text-[#738091] block text-[11px] uppercase tracking-wider font-semibold">Balanced Accuracy</span>
              <span className="font-bold text-[#202B38] mt-1 block">77.19%</span>
              <span className="text-[10px] text-[#738091]">Synthetic test set</span>
            </div>
            <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3.5">
              <span className="text-[#738091] block text-[11px] uppercase tracking-wider font-semibold">Status</span>
              <span className="font-bold text-[#202B38] mt-1 block">{ppoInfo?.is_loaded === false ? "Degraded" : "Ready"}</span>
              <span className="text-[10px] text-[#738091]">Independent endpoint</span>
            </div>
          </div>

          <div className="mb-4">
            <h3 className="font-heading text-lg font-bold text-[#202B38]">Synthetic Test Evaluation Summary</h3>
            <p className="text-xs text-[#738091]">Metrics reported on the PPO model's synthetic evaluation dataset</p>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
            <MetricCard label="Test Accuracy" value={`${(ppoEval.test_accuracy * 100).toFixed(2)}%`} subtext="Synthetic PPO test evaluation" badge="Synthetic" badgeType="teal" />
            <MetricCard label="Precision" value={`${(ppoEval.precision * 100).toFixed(2)}%`} subtext="Positive predictive value" badge="P(PPO|Pred)" badgeType="neutral" />
            <MetricCard label="Recall" value={`${(ppoEval.recall * 100).toFixed(2)}%`} subtext="True positive sensitivity" badge="Sensitivity" badgeType="neutral" />
            <MetricCard label="F1-score" value={`${(ppoEval.f1_score * 100).toFixed(2)}%`} subtext="Harmonic mean of P & R" badge="Balance" badgeType="neutral" />
            <MetricCard label="ROC-AUC" value={ppoEval.roc_auc.toFixed(4)} subtext="Area under ROC curve" badge="High" badgeType="gold" />
          </div>

          <div className="mt-6 flex items-start gap-3 rounded-lg border border-[#C6A66B]/30 bg-[#F7F3E9] p-4 text-xs text-[#202B38]">
            <AlertTriangle className="h-4 w-4 shrink-0 text-[#9A7B3E] mt-0.5" />
            <p className="leading-relaxed text-[#738091]">
              <strong className="text-[#9A7B3E]">Synthetic-dataset disclosure:</strong> This model was trained and evaluated on synthetic PPO data. Do not interpret these metrics as verified real-world company PPO prediction performance.
            </p>
          </div>
        </div>

        <div className="rounded-xl border border-[#E4E1DA] bg-white p-6 shadow-xs">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-[#E4E1DA] pb-4">
            <div>
              <h3 className="font-heading text-base font-semibold text-[#202B38]">
                PPO Feature Importance (Logistic Regression Coefficients)
              </h3>
              <p className="text-xs text-[#738091] mt-0.5">
                Model coefficients from the trained PPO classifier (synthetic-dataset evaluation)
              </p>
            </div>
            <div className="text-xs text-[#738091]">Higher positive weight indicates stronger contribution toward PPO likelihood</div>
          </div>

          <div className="mt-5 space-y-3">
            {Object.entries(ppoCoeffs)
              .sort((a, b) => b[1] - a[1])
              .map(([key, coef]) => {
                const maxAbs = Math.max(...Object.values(ppoCoeffs).map((v) => Math.abs(v)), 0.8);
                const widthPct = (Math.abs(coef) / maxAbs) * 100;
                return (
                  <div key={key} className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 rounded-lg border border-[#F6F3ED] bg-[#FBF9F5] p-2.5 text-xs">
                    <div className="w-full sm:w-64 font-medium text-[#202B38]">{key.replace(/_/g, " ")}</div>
                    <div className="flex-1 flex items-center gap-3">
                      <div className="relative h-2 w-full overflow-hidden rounded-full bg-[#E4E1DA]/60">
                        <div className="h-full rounded-full bg-[#3D827C]" style={{ width: `${Math.max(widthPct, 3)}%` }} />
                      </div>
                      <div className="w-20 text-right font-mono font-semibold text-[11px] text-[#3D827C]">
                        {coef >= 0 ? `+${coef.toFixed(6)}` : coef.toFixed(6)}
                      </div>
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      </section>

      {/* General glossary / limitations kept brief */}
      <div className="rounded-xl border border-[#E4E1DA] bg-white p-6 sm:p-8 shadow-xs">
        <div className="flex items-center gap-2 border-b border-[#E4E1DA] pb-4 mb-4">
          <HelpCircle className="h-5 w-5 text-[#3D827C]" />
          <div>
            <h2 className="font-heading text-base font-bold text-[#202B38]">Independent Model Isolation</h2>
            <p className="text-xs text-[#738091]">Both prediction systems operate separately within the same platform</p>
          </div>
        </div>
        <ul className="text-xs text-[#738091] space-y-2 list-disc list-inside">
          <li>Placement and PPO models use separate artifacts, feature schemas, preprocessing pipelines, services, and API endpoints.</li>
          <li>Placement predictions never call PPO logic, and PPO predictions never call placement logic.</li>
          <li>Each model has independent validation and health reporting so one model can remain available if the other is unavailable.</li>
        </ul>
      </div>

      <div className="rounded-xl border border-[#C6A66B]/30 bg-[#F7F3E9] p-6 sm:p-8 text-xs text-[#202B38] shadow-xs">
        <div className="flex items-start gap-3.5">
          <ShieldAlert className="h-6 w-6 text-[#9A7B3E] shrink-0 mt-0.5" />
          <div className="space-y-2">
            <h3 className="font-heading text-base font-bold text-[#9A7B3E]">Responsible Use</h3>
            <p className="text-[#738091] leading-relaxed">
              Placement and PPO outputs are statistical decision-support estimates, not guarantees. PPO predictions are based on synthetic training data and should be used only as indicative guidance in the context of internship performance evaluation.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
