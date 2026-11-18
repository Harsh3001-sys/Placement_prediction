import React from "react";
import { Briefcase, Info, Loader2 } from "lucide-react";
import type { SkillRequirementItem, SkillRoleSummary } from "../../types/placement";

interface RoleSelectorProps {
  roles: SkillRoleSummary[];
  selectedRoleId: string;
  onSelectRole: (roleId: string) => void;
  loading?: boolean;
  selectedRoleName?: string;
  skillCount?: number;
  coreSkillCount?: number;
  requirements?: SkillRequirementItem[];
}

export const RoleSelector: React.FC<RoleSelectorProps> = ({
  roles,
  selectedRoleId,
  onSelectRole,
  loading,
  selectedRoleName,
  skillCount,
  coreSkillCount,
  requirements = [],
}) => {
  const topSkills = [...requirements]
    .sort((a, b) => b.importance_weight - a.importance_weight)
    .slice(0, 4)
    .map((s) => s.skill_name);

  return (
    <div className="rounded-2xl border border-[#E4E1DA] bg-white p-6 shadow-xs space-y-4">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#EBF3F2] text-[#3D827C] border border-[#3D827C]/10">
            <Briefcase className="h-4.5 w-4.5" />
          </div>
          <div>
            <h2 className="font-heading text-base font-bold text-[#202B38]">Target Role</h2>
            <p className="text-xs text-[#738091]">Select a role to load benchmark skills and requirements</p>
          </div>
        </div>
        {loading && <Loader2 className="h-4 w-4 animate-spin text-[#C6A66B]" />}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 items-start">
        <div className="lg:col-span-1">
          <label className="block text-xs font-semibold text-[#202B38] mb-1.5">Choose target job role</label>
          <select
            value={selectedRoleId}
            onChange={(e) => onSelectRole(e.target.value)}
            className="w-full rounded-lg border border-[#E4E1DA] bg-white px-3 py-2.5 text-sm text-[#202B38] focus:border-[#3D827C] focus:ring-1 focus:ring-[#3D827C]"
          >
            <option value="">Select a role...</option>
            {roles.map((role) => (
              <option key={role.role_id} value={role.role_id}>
                {role.role_name}
              </option>
            ))}
          </select>
          <p className="mt-2 text-[11px] text-[#738091]">
            Requirements are synthetic illustrative benchmarks for this academic demo.
          </p>
        </div>

        <div className="lg:col-span-2 rounded-xl border border-[#E4E1DA] bg-[#FBF9F5] p-4">
          {selectedRoleId ? (
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="font-heading text-sm font-semibold text-[#202B38]">
                  {selectedRoleName || "Selected Role"}
                </h3>
                {typeof skillCount === "number" && (
                  <span className="rounded border border-[#E4E1DA] bg-white px-2 py-0.5 text-[10px] font-semibold text-[#738091]">
                    {skillCount} skills
                  </span>
                )}
                {typeof coreSkillCount === "number" && (
                  <span className="rounded border border-[#3D827C]/20 bg-[#EBF3F2] px-2 py-0.5 text-[10px] font-semibold text-[#3D827C]">
                    {coreSkillCount} core
                  </span>
                )}
              </div>
              <p className="text-xs text-[#738091] leading-relaxed flex items-start gap-1.5">
                <Info className="h-3.5 w-3.5 mt-0.5 text-[#9A7B3E] shrink-0" />
                <span>
                  Compare your current proficiency against role-specific benchmark skills to identify gaps, prioritize improvement,
                  and estimate weighted readiness (not placement probability).
                </span>
              </p>
              {topSkills.length > 0 && (
                <div className="pt-1">
                  <div className="text-[11px] font-semibold tracking-wider uppercase text-[#738091] mb-1.5">
                    High-importance focus areas
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {topSkills.map((s) => (
                      <span key={s} className="rounded-full border border-[#C6A66B]/25 bg-[#F7F3E9] px-2.5 py-1 text-[11px] font-medium text-[#9A7B3E]">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-xs text-[#738091]">Select a role to view its benchmark skill profile and start assessment.</div>
          )}
        </div>
      </div>
    </div>
  );
};
