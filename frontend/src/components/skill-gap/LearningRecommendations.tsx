import React, { useMemo, useState } from "react";
import { ExternalLink, Filter, Sparkles } from "lucide-react";
import type { RecommendedSkillGroup, RecommendationSummary, SkillRecommendationPreferences } from "../../types/placement";

interface LearningRecommendationsProps {
  groups: RecommendedSkillGroup[];
  summary: RecommendationSummary;
  preferences?: SkillRecommendationPreferences;
  onPreferencesChange?: (prefs: SkillRecommendationPreferences) => void;
  onRefresh?: () => void;
  loading?: boolean;
}

const badge = (text: string, cls: string) => (
  <span className={`inline-flex items-center rounded border px-2 py-0.5 text-[10px] font-semibold ${cls}`}>{text}</span>
);

function difficultyClass(d: string) {
  if (d === "Beginner") return "bg-emerald-50 text-emerald-700 border-emerald-200";
  if (d === "Intermediate") return "bg-amber-50 text-amber-800 border-amber-200";
  return "bg-[#F7F3E9] text-[#9A7B3E] border-[#C6A66B]/30";
}

export const LearningRecommendations: React.FC<LearningRecommendationsProps> = ({
  groups,
  summary,
  preferences: _preferences,
  onPreferencesChange: _onPreferencesChange,
  onRefresh,
  loading,
}) => {
  const [freeOnly, setFreeOnly] = useState(false);
  const [difficulty, setDifficulty] = useState<string>("all");
  const [resourceType, setResourceType] = useState<string>("all");
  const [provider, setProvider] = useState<string>("all");

  const allResources = useMemo(() => groups.flatMap((g) => g.resources), [groups]);

  const providers = useMemo(() => {
    const set = new Set<string>();
    allResources.forEach((r) => set.add(r.provider));
    return Array.from(set).sort((a, b) => a.localeCompare(b));
  }, [allResources]);

  const resourceTypes = useMemo(() => {
    const set = new Set<string>();
    allResources.forEach((r) => set.add(r.resource_type));
    return Array.from(set).sort((a, b) => a.localeCompare(b));
  }, [allResources]);

  const filteredGroups = useMemo(() => {
    return groups
      .map((g) => {
        const resources = g.resources.filter((r) => {
          if (freeOnly && !r.is_free) return false;
          if (difficulty !== "all" && r.difficulty_level !== difficulty) return false;
          if (resourceType !== "all" && r.resource_type !== resourceType) return false;
          if (provider !== "all" && r.provider !== provider) return false;
          return true;
        });
        return { ...g, resources };
      })
      .filter((g) => g.resources.length > 0);
  }, [groups, freeOnly, difficulty, resourceType, provider]);

  const filteredCounts = useMemo(() => {
    const resources = filteredGroups.flatMap((g) => g.resources);
    return {
      resources: resources.length,
      skills: filteredGroups.length,
      free: resources.filter((r) => r.is_free).length,
      hours: Math.round(resources.reduce((sum, r) => sum + (Number(r.estimated_hours) || 0), 0) * 100) / 100,
    };
  }, [filteredGroups]);

  return (
    <div className="rounded-2xl border border-[#E4E1DA] bg-white p-6 shadow-xs space-y-5">
      <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4 border-b border-[#E4E1DA] pb-4">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#F7F3E9] text-[#9A7B3E] border border-[#C6A66B]/20 shrink-0">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-heading text-lg font-bold text-[#202B38]">Personalized Learning Recommendations</h3>
            <p className="text-xs text-[#738091] mt-0.5 max-w-3xl">
              Curated, explainable learning resources matched to your Phase 1 skill gaps and current proficiency. Recommendation scores are rule-based ranking signals (not placement probabilities or guarantees).
            </p>
          </div>
        </div>
        {onRefresh && (
          <button
            type="button"
            onClick={onRefresh}
            disabled={loading}
            className="inline-flex items-center justify-center rounded-lg border border-[#E4E1DA] bg-white px-3 py-2 text-xs font-semibold text-[#202B38] hover:bg-[#FBF9F5] disabled:opacity-60"
          >
            {loading ? "Refreshing..." : "Refresh Recommendations"}
          </button>
        )}
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="rounded-xl border border-[#E4E1DA] bg-[#FBF9F5] p-3">
          <div className="text-[10px] uppercase tracking-wider text-[#738091] font-semibold">Priority Skills Covered</div>
          <div className="font-heading text-xl font-bold text-[#202B38] mt-1">{summary.priority_skills_covered}</div>
        </div>
        <div className="rounded-xl border border-[#E4E1DA] bg-[#FBF9F5] p-3">
          <div className="text-[10px] uppercase tracking-wider text-[#738091] font-semibold">Recommended Resources</div>
          <div className="font-heading text-xl font-bold text-[#202B38] mt-1">{summary.total_recommended_resources}</div>
        </div>
        <div className="rounded-xl border border-[#E4E1DA] bg-[#FBF9F5] p-3">
          <div className="text-[10px] uppercase tracking-wider text-[#738091] font-semibold">Free Resources</div>
          <div className="font-heading text-xl font-bold text-[#202B38] mt-1">{summary.free_resources_recommended}</div>
        </div>
        <div className="rounded-xl border border-[#E4E1DA] bg-[#FBF9F5] p-3">
          <div className="text-[10px] uppercase tracking-wider text-[#738091] font-semibold">Estimated Hours</div>
          <div className="font-heading text-xl font-bold text-[#202B38] mt-1">{summary.estimated_total_learning_hours}</div>
          <div className="text-[10px] text-[#738091]">Actual resource totals</div>
        </div>
        <div className="rounded-xl border border-[#3D827C]/20 bg-[#EBF3F2] p-3 col-span-2 md:col-span-1">
          <div className="text-[10px] uppercase tracking-wider text-[#3D827C] font-semibold">Work On First</div>
          <div className="font-heading text-sm font-bold text-[#202B38] mt-1 leading-snug">{summary.top_skill_to_focus || "—"}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="rounded-xl border border-[#E4E1DA] bg-[#FBF9F5] p-4 space-y-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-[#202B38]">
          <Filter className="h-4 w-4 text-[#738091]" /> Filter recommendations
          <span className="text-[11px] font-normal text-[#738091]">(client-side filters on real recommendation data)</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <label className="flex items-center gap-2 text-sm text-[#202B38] bg-white border border-[#E4E1DA] rounded-lg px-3 py-2">
            <input type="checkbox" checked={freeOnly} onChange={(e) => setFreeOnly(e.target.checked)} className="accent-[#3D827C]" />
            Free resources only
          </label>
          <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)} className="rounded-lg border border-[#E4E1DA] bg-white px-3 py-2 text-sm text-[#202B38]">
            <option value="all">All difficulties</option>
            <option value="Beginner">Beginner</option>
            <option value="Intermediate">Intermediate</option>
            <option value="Advanced">Advanced</option>
          </select>
          <select value={resourceType} onChange={(e) => setResourceType(e.target.value)} className="rounded-lg border border-[#E4E1DA] bg-white px-3 py-2 text-sm text-[#202B38]">
            <option value="all">All resource types</option>
            {resourceTypes.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
          <select value={provider} onChange={(e) => setProvider(e.target.value)} className="rounded-lg border border-[#E4E1DA] bg-white px-3 py-2 text-sm text-[#202B38]">
            <option value="all">All providers</option>
            {providers.map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>
        <div className="text-[11px] text-[#738091]">
          Showing <strong className="text-[#202B38]">{filteredCounts.resources}</strong> resources across <strong className="text-[#202B38]">{filteredCounts.skills}</strong> skills ({filteredCounts.free} free, ~{filteredCounts.hours} hrs)
        </div>
      </div>

      {/* Grouped resources */}
      {filteredGroups.length === 0 ? (
        <div className="rounded-xl border border-dashed border-[#E4E1DA] bg-[#FBF9F5] p-6 text-center">
          <p className="text-sm font-medium text-[#202B38]">No recommendations match the selected filters.</p>
          <p className="text-xs text-[#738091] mt-1">Try adjusting filters to view more curated resources.</p>
        </div>
      ) : (
        <div className="space-y-5">
          {filteredGroups.map((group) => (
            <div key={group.skill_id} className="rounded-xl border border-[#E4E1DA] overflow-hidden">
              <div className="bg-[#FBF9F5] border-b border-[#E4E1DA] px-4 py-3 flex flex-wrap items-center justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <h4 className="font-heading text-sm font-semibold text-[#202B38]">{group.skill_name}</h4>
                    {badge(group.priority_classification, group.priority_classification === "Critical Gap" ? "bg-red-50 text-red-700 border-red-200" : group.priority_classification === "Moderate Gap" ? "bg-amber-50 text-amber-800 border-amber-200" : "bg-[#EBF3F2] text-[#3D827C] border-[#3D827C]/20")}
                  </div>
                  <p className="text-[11px] text-[#738091] mt-0.5">
                    Current {group.current_proficiency.toFixed(0)} / Required {group.required_proficiency.toFixed(0)} • Gap {group.gap.toFixed(1)}
                  </p>
                </div>
                <div className="text-[11px] text-[#738091]">{group.resources.length} resource{group.resources.length === 1 ? "" : "s"}</div>
              </div>
              <div className="p-4 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 bg-white">
                {group.resources.map((r) => (
                  <div key={r.resource_id} className="rounded-xl border border-[#E4E1DA] bg-[#FBF9F5] p-4 flex flex-col">
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <div className="flex flex-wrap gap-1.5 mb-2">
                          {badge(r.difficulty_level, difficultyClass(r.difficulty_level))}
                          {badge(r.resource_type, "bg-white text-[#738091] border-[#E4E1DA]")}
                          {badge(r.is_free ? "Free" : "Paid/Limited", r.is_free ? "bg-emerald-50 text-emerald-700 border-emerald-200" : "bg-slate-50 text-slate-600 border-slate-200")}
                        </div>
                        <h5 className="font-heading text-sm font-semibold text-[#202B38] leading-snug">{r.resource_title}</h5>
                        <p className="text-[11px] text-[#738091] mt-0.5">{r.provider}</p>
                      </div>
                      {typeof r.recommendation_score === "number" && (
                        <div className="shrink-0 text-right">
                          <div className="text-[10px] uppercase tracking-wider text-[#738091] font-semibold">Score</div>
                          <div className="font-mono text-sm font-bold text-[#202B38]">{r.recommendation_score.toFixed(1)}</div>
                        </div>
                      )}
                    </div>
                    <p className="text-[11px] text-[#738091] mt-2 leading-relaxed line-clamp-3">{r.description}</p>
                    <div className="mt-2 text-[11px] text-[#738091] flex flex-wrap gap-x-3 gap-y-1">
                      <span><strong className="text-[#202B38]">~{r.estimated_hours}</strong> hrs</span>
                      <span>Quality {r.quality_score}/100</span>
                      {r.prerequisites && r.prerequisites !== "None" && <span>Prereq: {r.prerequisites}</span>}
                    </div>
                    {r.why_recommended && r.why_recommended.length > 0 && (
                      <ul className="mt-2 space-y-1">
                        {r.why_recommended.slice(0, 2).map((reason, i) => (
                          <li key={i} className="text-[11px] text-[#202B38] leading-relaxed">• {reason}</li>
                        ))}
                      </ul>
                    )}
                    <div className="mt-auto pt-3">
                      <a
                        href={r.resource_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 rounded-lg bg-[#101C2C] px-3 py-2 text-xs font-semibold text-white hover:bg-[#192B40] transition-colors"
                      >
                        Open Resource <ExternalLink className="h-3.5 w-3.5" />
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};