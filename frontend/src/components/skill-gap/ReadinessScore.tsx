import React from "react";
import { AlertCircle, CheckCircle2, Target } from "lucide-react";
import type { SkillAnalysisResponse, SkillComparisonItem } from "../../types/placement";

interface ReadinessScoreProps {
  analysis: SkillAnalysisResponse;
}

function getTone(score: number) {
  if (score >= 75) return { label: "Strong Readiness", color: "#3D827C", bg: "bg-[#EBF3F2]", border: "border-[#3D827C]/20" };
  if (score >= 50) return { label: "Developing Readiness", color: "#9A7B3E", bg: "bg-[#F7F3E9]", border: "border-[#C6A66B]/30" };
  return { label: "Needs Focus", color: "#B45309", bg: "bg-amber-50", border: "border-amber-200" };
}

export const ReadinessScore: React.FC<ReadinessScoreProps> = ({ analysis }) => {
  const score = analysis.overall_readiness_score;
  const tone = getTone(score);
  const critical = analysis.summary.critical_gaps;
  const top = analysis.top_priority_skills.slice(0, 5);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div className={`rounded-2xl border ${tone.border} ${tone.bg} p-6 shadow-xs`}>
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="text-[11px] font-semibold tracking-wider uppercase text-[#738091]">Overall Role Readiness</div>
            <div className="mt-2 flex items-end gap-2">
              <div className="font-heading text-4xl font-extrabold text-[#202B38]">{score.toFixed(1)}</div>
              <div className="text-sm font-semibold text-[#738091] mb-1">/ 100</div>
            </div>
            <div className="mt-2 inline-flex items-center rounded-full border border-white/60 bg-white/70 px-2.5 py-1 text-[11px] font-semibold" style={{ color: tone.color }}>
              {tone.label}
            </div>
          </div>
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white border border-white/70 shadow-xs">
            <Target className="h-5 w-5" style={{ color: tone.color }} />
          </div>
        </div>

        <div className="mt-5">
          <div className="flex items-center justify-between text-[11px] text-[#738091] mb-1.5">
            <span>Weighted skill coverage</span>
            <span className="font-semibold text-[#202B38]">{score.toFixed(1)}%</span>
          </div>
          <div className="h-3 w-full rounded-full bg-white/80 border border-white/70 overflow-hidden p-0.5">
            <div
              className="h-full rounded-full transition-all duration-700"
              style={{ width: `${Math.max(0, Math.min(100, score))}%`, backgroundColor: tone.color }}
            />
          </div>
          <p className="mt-2 text-[11px] text-[#738091] leading-relaxed">
            {analysis.readiness_score_interpretation || "Weighted skill coverage against the selected role's benchmark requirements. Not a placement probability."}
          </p>
        </div>
      </div>

      <div className="rounded-2xl border border-[#E4E1DA] bg-white p-6 shadow-xs">
        <div className="flex items-center gap-2 mb-3">
          <CheckCircle2 className="h-4 w-4 text-[#3D827C]" />
          <h3 className="font-heading text-sm font-semibold text-[#202B38]">Strongest Skills</h3>
        </div>
        <div className="space-y-2">
          {analysis.strongest_skills.slice(0, 4).map((s: SkillComparisonItem) => (
            <div key={s.skill_id} className="flex items-center justify-between gap-3 rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] px-3 py-2">
              <div className="min-w-0">
                <div className="text-xs font-semibold text-[#202B38] truncate">{s.skill_name}</div>
                <div className="text-[10px] text-[#738091]">Gap {s.gap.toFixed(1)} · {s.priority_classification}</div>
              </div>
              <div className="text-right shrink-0">
                <div className="text-xs font-bold text-[#3D827C]">{s.current_proficiency}</div>
                <div className="text-[10px] text-[#738091]">/ {s.required_proficiency}</div>
              </div>
            </div>
          ))}
          {analysis.strongest_skills.length === 0 && <div className="text-xs text-[#738091]">No strengths identified yet.</div>}
        </div>
      </div>

      <div className="rounded-2xl border border-[#E4E1DA] bg-white p-6 shadow-xs">
        <div className="flex items-center gap-2 mb-3">
          <AlertCircle className="h-4 w-4 text-[#9A7B3E]" />
          <h3 className="font-heading text-sm font-semibold text-[#202B38]">Critical Gaps & Top 5</h3>
        </div>
        <div className="mb-3 rounded-lg border border-[#C6A66B]/20 bg-[#F7F3E9] px-3 py-2 text-xs text-[#9A7B3E]">
          <span className="font-semibold">{critical}</span> critical gap skill{critical === 1 ? "" : "s"} identified for this role.
        </div>
        <div className="space-y-2">
          {top.map((s, idx) => (
            <div key={s.skill_id} className="flex items-center gap-2.5 rounded-lg border border-[#E4E1DA] px-3 py-2">
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-[#101C2C] text-[10px] font-bold text-white">{idx + 1}</span>
              <div className="min-w-0 flex-1">
                <div className="text-xs font-semibold text-[#202B38] truncate">{s.skill_name}</div>
                <div className="text-[10px] text-[#738091]">{s.priority_classification} · gap {s.gap.toFixed(1)}</div>
              </div>
              <span className="text-[10px] font-semibold text-[#738091]">{(s.importance_weight * 100).toFixed(1)}%</span>
            </div>
          ))}
          {top.length === 0 && <div className="text-xs text-[#738091]">No priority gaps found. Great coverage!</div>}
        </div>
      </div>
    </div>
  );
};
