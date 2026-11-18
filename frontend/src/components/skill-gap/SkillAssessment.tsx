import React from "react";
import { SlidersHorizontal } from "lucide-react";
import type { SkillMetadataItem, SkillRequirementItem } from "../../types/placement";

interface SkillAssessmentProps {
  requirements: SkillRequirementItem[];
  metadataByKey: Record<string, SkillMetadataItem | undefined>;
  values: Record<string, number>;
  onChange: (skillName: string, value: number) => void;
  onAnalyze: () => void;
  analyzing?: boolean;
  disabled?: boolean;
}

export const SkillAssessment: React.FC<SkillAssessmentProps> = ({
  requirements,
  metadataByKey,
  values,
  onChange,
  onAnalyze,
  analyzing,
  disabled,
}) => {
  if (!requirements.length) return null;

  return (
    <div className="rounded-2xl border border-[#E4E1DA] bg-white p-6 shadow-xs space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#E4E1DA] pb-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#F7F3E9] text-[#9A7B3E] border border-[#C6A66B]/20">
            <SlidersHorizontal className="h-4.5 w-4.5" />
          </div>
          <div>
            <h2 className="font-heading text-base font-bold text-[#202B38]">Skill Assessment</h2>
            <p className="text-xs text-[#738091]">
              Set your current proficiency (0-100) for each role-relevant skill. Defaults are demo values only.
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={onAnalyze}
          disabled={disabled || analyzing}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-[#101C2C] px-5 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-[#192B40] transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {analyzing ? "Analyzing Skills..." : "Analyze My Skills"}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {requirements.map((skill) => {
          const meta =
            metadataByKey[skill.skill_id] ||
            metadataByKey[skill.skill_name.toLowerCase()];
          const value = values[skill.skill_name] ?? 0;
          return (
            <div
              key={skill.skill_id}
              className="rounded-xl border border-[#E4E1DA] bg-[#FBF9F5] p-4 space-y-3"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="text-sm font-semibold text-[#202B38]">{skill.skill_name}</h3>
                    {skill.is_core_skill && (
                      <span className="rounded border border-[#3D827C]/20 bg-[#EBF3F2] px-1.5 py-0.5 text-[10px] font-semibold text-[#3D827C]">
                        Core
                      </span>
                    )}
                    <span className="rounded border border-[#E4E1DA] bg-white px-1.5 py-0.5 text-[10px] text-[#738091]">
                      {skill.skill_category}
                    </span>
                  </div>
                  <p className="mt-1 text-[11px] leading-relaxed text-[#738091]">
                    {meta?.description || "Role-relevant skill used in the readiness benchmark comparison."}
                  </p>
                </div>
                <div className="shrink-0 text-right">
                  <div className="text-[10px] uppercase tracking-wider text-[#738091] font-semibold">Required</div>
                  <div className="font-heading text-lg font-bold text-[#202B38]">{skill.required_proficiency}</div>
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-[11px] text-[#738091]">
                  <label htmlFor={`skill-${skill.skill_id}`} className="font-medium text-[#202B38]">
                    Current proficiency
                  </label>
                  <span className="font-mono font-semibold text-[#202B38] bg-white border border-[#E4E1DA] rounded px-2 py-0.5">
                    {value}
                  </span>
                </div>
                <input
                  id={`skill-${skill.skill_id}`}
                  type="range"
                  min={0}
                  max={100}
                  step={1}
                  value={value}
                  onChange={(e) => onChange(skill.skill_name, Number(e.target.value))}
                  className="w-full accent-[#3D827C]"
                  aria-label={`${skill.skill_name} current proficiency`}
                />
                <div className="flex items-center justify-between text-[10px] text-[#738091]">
                  <span>Beginner (0)</span>
                  <span>Intermediate (50)</span>
                  <span>Advanced (100)</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
