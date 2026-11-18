import React from "react";
import { CheckCircle2, Flag, TrendingUp } from "lucide-react";
import type { SkillRoadmapPhase } from "../../types/placement";

interface ImprovementRoadmapProps {
  roadmap: SkillRoadmapPhase[];
}

const phaseMeta: Record<string, { icon: React.ReactNode; badge: string }> = {
  immediate_focus: {
    icon: <Flag className="h-4 w-4 text-amber-700" />,
    badge: "bg-amber-50 text-amber-800 border-amber-200",
  },
  next_focus: {
    icon: <TrendingUp className="h-4 w-4 text-[#9A7B3E]" />,
    badge: "bg-[#F7F3E9] text-[#9A7B3E] border-[#C6A66B]/30",
  },
  maintain_strengths: {
    icon: <CheckCircle2 className="h-4 w-4 text-[#3D827C]" />,
    badge: "bg-[#EBF3F2] text-[#3D827C] border-[#3D827C]/20",
  },
};

export const ImprovementRoadmap: React.FC<ImprovementRoadmapProps> = ({ roadmap }) => {
  return (
    <div className="rounded-2xl border border-[#E4E1DA] bg-white p-6 shadow-xs space-y-4">
      <div>
        <h3 className="font-heading text-base font-semibold text-[#202B38]">Personalized Improvement Roadmap</h3>
        <p className="text-[11px] text-[#738091] mt-0.5">
          Rule-based guidance generated from your calculated gaps and role importance. This does not guarantee placement outcomes.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {roadmap.map((phase) => {
          const meta = phaseMeta[phase.phase] || phaseMeta.next_focus;
          return (
            <div key={phase.phase} className="rounded-xl border border-[#E4E1DA] bg-[#FBF9F5] p-4 flex flex-col">
              <div className="flex items-start justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white border border-[#E4E1DA]">
                    {meta.icon}
                  </div>
                  <h4 className="font-heading text-sm font-semibold text-[#202B38]">{phase.title}</h4>
                </div>
                <span className={`rounded border px-2 py-0.5 text-[10px] font-semibold ${meta.badge}`}>
                  {phase.skills.length} skill{phase.skills.length === 1 ? "" : "s"}
                </span>
              </div>
              <p className="text-[11px] text-[#738091] leading-relaxed mb-3">{phase.description}</p>

              <div className="space-y-2 flex-1">
                {phase.skills.length > 0 ? (
                  phase.skills.slice(0, 6).map((s) => (
                    <div key={s.skill_name} className="rounded-lg border border-[#E4E1DA] bg-white px-3 py-2">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-xs font-semibold text-[#202B38] truncate">{s.skill_name}</span>
                        <span className="text-[10px] text-[#738091] whitespace-nowrap">Gap {s.gap.toFixed(1)}</span>
                      </div>
                      <p className="mt-1 text-[10px] text-[#738091] leading-relaxed">{s.reason}</p>
                    </div>
                  ))
                ) : (
                  <div className="text-[11px] text-[#738091] border border-dashed border-[#E4E1DA] rounded-lg p-3 bg-white">
                    No skills currently in this phase based on your assessment.
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
