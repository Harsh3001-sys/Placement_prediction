import React from "react";
import { BookOpen, CheckCircle2, Flag, TrendingUp, Wrench, ExternalLink } from "lucide-react";
import type { LearningRoadmapStage } from "../../types/placement";

interface LearningRoadmapProps {
  roadmap: LearningRoadmapStage[];
}

const stageMeta: Record<string, { icon: React.ReactNode; badge: string; accent: string }> = {
  immediate_focus: {
    icon: <Flag className="h-4 w-4 text-red-700" />,
    badge: "bg-red-50 text-red-700 border-red-200",
    accent: "border-t-red-400",
  },
  skill_development: {
    icon: <TrendingUp className="h-4 w-4 text-amber-700" />,
    badge: "bg-amber-50 text-amber-800 border-amber-200",
    accent: "border-t-amber-400",
  },
  strengthening_skills: {
    icon: <Wrench className="h-4 w-4 text-[#3D827C]" />,
    badge: "bg-[#EBF3F2] text-[#3D827C] border-[#3D827C]/20",
    accent: "border-t-[#3D827C]",
  },
  maintain_strengths: {
    icon: <CheckCircle2 className="h-4 w-4 text-emerald-700" />,
    badge: "bg-emerald-50 text-emerald-700 border-emerald-200",
    accent: "border-t-emerald-400",
  },
};

export const LearningRoadmap: React.FC<LearningRoadmapProps> = ({ roadmap }) => {
  return (
    <div className="rounded-2xl border border-[#E4E1DA] bg-white p-6 shadow-xs space-y-4">
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#EBF3F2] text-[#3D827C] border border-[#3D827C]/20 shrink-0">
          <BookOpen className="h-5 w-5" />
        </div>
        <div>
          <h3 className="font-heading text-lg font-bold text-[#202B38]">Personalized Learning Roadmap</h3>
          <p className="text-[11px] text-[#738091] mt-0.5 max-w-3xl">
            4-stage learning sequence based on Phase 1 priorities and curated resource recommendations. Estimated hours reflect actual resource metadata and are not guaranteed completion times.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        {roadmap.map((stage, idx) => {
          const meta = stageMeta[stage.stage] || stageMeta.skill_development;
          return (
            <div key={stage.stage} className={`rounded-xl border border-[#E4E1DA] border-t-4 ${meta.accent} bg-[#FBF9F5] p-4 flex flex-col`}>
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="flex items-start gap-2.5">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white border border-[#E4E1DA] mt-0.5">
                    {meta.icon}
                  </div>
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-[10px] font-semibold text-[#738091] uppercase tracking-wider">Stage {idx + 1}</span>
                      <span className={`rounded border px-2 py-0.5 text-[10px] font-semibold ${meta.badge}`}>
                        {stage.skill_count} skill{stage.skill_count === 1 ? "" : "s"}
                      </span>
                    </div>
                    <h4 className="font-heading text-sm font-semibold text-[#202B38]">{stage.title}</h4>
                  </div>
                </div>
                <div className="text-right shrink-0">
                  <div className="text-[10px] uppercase tracking-wider text-[#738091] font-semibold">Est. Hours</div>
                  <div className="font-mono text-sm font-bold text-[#202B38]">{stage.estimated_stage_hours}</div>
                </div>
              </div>
              <p className="text-[11px] text-[#738091] leading-relaxed mb-3">{stage.description}</p>

              <div className="space-y-3 flex-1">
                {stage.skills.length > 0 ? (
                  stage.skills.map((skill) => (
                    <div key={skill.skill_id} className="rounded-lg border border-[#E4E1DA] bg-white p-3 space-y-2">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-sm font-semibold text-[#202B38]">{skill.skill_name}</span>
                            <span className="rounded border border-[#E4E1DA] bg-[#FBF9F5] px-1.5 py-0.5 text-[10px] text-[#738091]">{skill.priority}</span>
                          </div>
                          <p className="text-[10px] text-[#738091] mt-0.5">
                            Current {skill.current_proficiency.toFixed(0)} → Required {skill.required_proficiency.toFixed(0)} (Gap {skill.gap.toFixed(1)})
                          </p>
                        </div>
                        <span className="text-[10px] text-[#738091] whitespace-nowrap">~{skill.estimated_resource_hours} hrs</span>
                      </div>
                      <p className="text-[11px] text-[#738091] leading-relaxed">{skill.reason_for_prioritization}</p>

                      {skill.recommended_sequence.length > 0 ? (
                        <div className="space-y-1.5">
                          <div className="text-[10px] uppercase tracking-wider text-[#738091] font-semibold">Recommended sequence</div>
                          {skill.recommended_sequence.map((step) => {
                            const full = skill.recommended_resources.find((r) => r.resource_id === step.resource_id);
                            return (
                              <div key={step.resource_id} className="flex items-start gap-2 text-[11px]">
                                <span className="mt-0.5 inline-flex h-4 w-4 items-center justify-center rounded-full bg-[#101C2C] text-white text-[9px] font-bold shrink-0">{step.step}</span>
                                <div className="min-w-0 flex-1">
                                  <div className="text-[#202B38] font-medium leading-snug">{step.resource_title}</div>
                                  <div className="text-[#738091] flex flex-wrap items-center gap-x-2 gap-y-0.5">
                                    <span>{step.difficulty_level} • {step.resource_type}</span>
                                    {full && <span>~{full.estimated_hours} hrs</span>}
                                    {full?.resource_url && (
                                      <a href={full.resource_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-[#3D827C] hover:underline font-medium">
                                        Open <ExternalLink className="h-3 w-3" />
                                      </a>
                                    )}
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      ) : (
                        <div className="text-[11px] text-[#738091] border border-dashed border-[#E4E1DA] rounded p-2 bg-[#FBF9F5]">
                          No curated resources matched current filters/preferences for this skill. Try adjusting preferences.
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="text-[11px] text-[#738091] border border-dashed border-[#E4E1DA] rounded-lg p-3 bg-white">
                    No skills currently in this stage based on your assessment.
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