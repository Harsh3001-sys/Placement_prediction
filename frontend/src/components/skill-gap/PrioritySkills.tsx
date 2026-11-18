import React from "react";
import { ArrowUpRight, Info } from "lucide-react";
import type { SkillComparisonItem } from "../../types/placement";

interface PrioritySkillsProps {
  skills: SkillComparisonItem[];
}

const badgeClass = (classification: string) => {
  if (classification === "Critical Gap") return "bg-amber-50 text-amber-800 border-amber-200";
  if (classification === "Moderate Gap") return "bg-[#F7F3E9] text-[#9A7B3E] border-[#C6A66B]/30";
  if (classification === "Minor Gap") return "bg-slate-50 text-slate-700 border-slate-200";
  return "bg-[#EBF3F2] text-[#3D827C] border-[#3D827C]/20";
};

export const PrioritySkills: React.FC<PrioritySkillsProps> = ({ skills }) => {
  if (!skills.length) return null;

  return (
    <div className="rounded-2xl border border-[#E4E1DA] bg-white p-6 shadow-xs">
      <div className="flex items-center justify-between gap-3 mb-4">
        <div>
          <h3 className="font-heading text-base font-semibold text-[#202B38]">Priority Skills to Improve</h3>
          <p className="text-[11px] text-[#738091] mt-0.5">
            Ordered by weighted priority (gap and importance). Focus on higher-priority skills first.
          </p>
        </div>
        <span className="text-[11px] font-semibold text-[#738091]">Top {Math.min(5, skills.length)}</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        {skills.slice(0, 5).map((skill, idx) => (
          <div key={skill.skill_id} className="rounded-xl border border-[#E4E1DA] bg-[#FBF9F5] p-4 space-y-3">
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-2 min-w-0">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-[#101C2C] text-xs font-bold text-white shrink-0">
                  {idx + 1}
                </span>
                <div className="min-w-0">
                  <div className="text-sm font-semibold text-[#202B38] truncate">{skill.skill_name}</div>
                  <div className="text-[10px] text-[#738091]">{skill.skill_category}{skill.is_core_skill ? " · Core skill" : ""}</div>
                </div>
              </div>
              <span className={`rounded border px-2 py-0.5 text-[10px] font-semibold ${badgeClass(skill.priority_classification)}`}>
                {skill.priority_classification}
              </span>
            </div>

            <div className="grid grid-cols-4 gap-2 text-center">
              <div className="rounded-lg border border-[#E4E1DA] bg-white px-2 py-2">
                <div className="text-[10px] text-[#738091]">Current</div>
                <div className="text-sm font-bold text-[#202B38]">{skill.current_proficiency}</div>
              </div>
              <div className="rounded-lg border border-[#E4E1DA] bg-white px-2 py-2">
                <div className="text-[10px] text-[#738091]">Required</div>
                <div className="text-sm font-bold text-[#202B38]">{skill.required_proficiency}</div>
              </div>
              <div className="rounded-lg border border-[#E4E1DA] bg-white px-2 py-2">
                <div className="text-[10px] text-[#738091]">Gap</div>
                <div className="text-sm font-bold text-[#9A7B3E]">{skill.gap.toFixed(1)}</div>
              </div>
              <div className="rounded-lg border border-[#E4E1DA] bg-white px-2 py-2">
                <div className="text-[10px] text-[#738091]">Importance</div>
                <div className="text-sm font-bold text-[#3D827C]">{(skill.importance_weight * 100).toFixed(1)}%</div>
              </div>
            </div>

            <div className="space-y-1.5 text-[11px] text-[#738091] leading-relaxed">
              <p className="flex items-start gap-1.5">
                <Info className="h-3.5 w-3.5 mt-0.5 text-[#C6A66B] shrink-0" />
                <span><span className="font-semibold text-[#202B38]">Why it matters:</span> {skill.why_it_matters} {skill.description}</span>
              </p>
              <p className="flex items-start gap-1.5">
                <ArrowUpRight className="h-3.5 w-3.5 mt-0.5 text-[#3D827C] shrink-0" />
                <span><span className="font-semibold text-[#202B38]">Suggestion:</span> {skill.improvement_suggestion}</span>
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
