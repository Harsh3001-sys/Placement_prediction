import React, { useEffect, useMemo, useState } from "react";
import { AlertTriangle, BarChart3, Loader2, RefreshCw, Sparkles } from "lucide-react";
import { apiService, ApiClientError } from "../services/api";
import type {
  SkillAnalysisResponse,
  SkillMetadataItem,
  SkillRecommendResponse,
  SkillRequirementItem,
  SkillRoleSummary,
} from "../types/placement";
import { RoleSelector } from "../components/skill-gap/RoleSelector";
import { SkillAssessment } from "../components/skill-gap/SkillAssessment";
import { ReadinessScore } from "../components/skill-gap/ReadinessScore";
import { SkillGapChart } from "../components/skill-gap/SkillGapChart";
import { PrioritySkills } from "../components/skill-gap/PrioritySkills";
import { ImprovementRoadmap } from "../components/skill-gap/ImprovementRoadmap";
import { LearningRecommendations } from "../components/skill-gap/LearningRecommendations";
import { LearningRoadmap } from "../components/skill-gap/LearningRoadmap";

function buildDefaultValues(requirements: SkillRequirementItem[]): Record<string, number> {
  const values: Record<string, number> = {};
  for (const skill of requirements) {
    // Sensible demo defaults (not verified assessments), varied relative to requirement
    const baseline = Math.round(skill.required_proficiency * 0.65);
    values[skill.skill_name] = Math.max(15, Math.min(90, baseline));
  }
  return values;
}

export const SkillIntelligencePage: React.FC = () => {
  const [roles, setRoles] = useState<SkillRoleSummary[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<string>("");
  const [selectedRoleName, setSelectedRoleName] = useState<string>("");
  const [requirements, setRequirements] = useState<SkillRequirementItem[]>([]);
  const [metadataByKey, setMetadataByKey] = useState<Record<string, SkillMetadataItem | undefined>>({});
  const [skillValues, setSkillValues] = useState<Record<string, number>>({});
  const [analysis, setAnalysis] = useState<SkillAnalysisResponse | null>(null);
  const [recommendation, setRecommendation] = useState<SkillRecommendResponse | null>(null);

  const [loadingRoles, setLoadingRoles] = useState(true);
  const [loadingRoleData, setLoadingRoleData] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [recommending, setRecommending] = useState(false);
  const [pageError, setPageError] = useState<string | null>(null);
  const [roleError, setRoleError] = useState<string | null>(null);
  const [analyzeError, setAnalyzeError] = useState<{ message: string; details?: string[] } | null>(null);
  const [recommendError, setRecommendError] = useState<string | null>(null);

  const selectedRoleSummary = useMemo(
    () => roles.find((r) => r.role_id === selectedRoleId),
    [roles, selectedRoleId]
  );

  useEffect(() => {
    let mounted = true;
    (async () => {
      setLoadingRoles(true);
      setPageError(null);
      try {
        const [rolesRes, metadataRes] = await Promise.all([
          apiService.getSkillRoles(),
          apiService.getSkillMetadata(),
        ]);
        if (!mounted) return;
        const loadedRoles = rolesRes.roles || [];
        setRoles(loadedRoles);

        const map: Record<string, SkillMetadataItem> = {};
        for (const item of metadataRes.skills || []) {
          map[item.skill_id] = item;
          map[item.skill_name.toLowerCase()] = item;
        }
        setMetadataByKey(map);

        // Auto-select first role for better UX
        if (loadedRoles.length > 0) {
          setSelectedRoleId(loadedRoles[0].role_id);
        }
      } catch (err: any) {
        if (!mounted) return;
        if (err instanceof ApiClientError) setPageError(err.message);
        else setPageError("Failed to load Skill Intelligence data. Please try again.");
      } finally {
        if (mounted) setLoadingRoles(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (!selectedRoleId) {
      setRequirements([]);
      setSkillValues({});
      setSelectedRoleName("");
      setAnalysis(null);
      setRecommendation(null);
      setRecommendError(null);
      return;
    }

    let mounted = true;
    (async () => {
      setLoadingRoleData(true);
      setRoleError(null);
      setAnalyzeError(null);
      setRecommendError(null);
      setAnalysis(null);
      setRecommendation(null);
      try {
        const reqRes = await apiService.getSkillRequirements(selectedRoleId);
        if (!mounted) return;
        const reqs = reqRes.skills || [];
        setRequirements(reqs);
        setSelectedRoleName(reqRes.role_name || selectedRoleSummary?.role_name || selectedRoleId);
        setSkillValues(buildDefaultValues(reqs));
      } catch (err: any) {
        if (!mounted) return;
        setRequirements([]);
        setSkillValues({});
        if (err instanceof ApiClientError) setRoleError(err.message);
        else setRoleError("Failed to load role requirements.");
      } finally {
        if (mounted) setLoadingRoleData(false);
      }
    })();

    return () => {
      mounted = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedRoleId]);

  const handleSkillChange = (skillName: string, value: number) => {
    const v = Math.max(0, Math.min(100, Math.round(value)));
    setSkillValues((prev) => ({ ...prev, [skillName]: v }));
  };

  const buildPayloadSkills = () => {
    const payloadSkills: Record<string, number> = {};
    for (const req of requirements) {
      payloadSkills[req.skill_name] = skillValues[req.skill_name] ?? 0;
    }
    return payloadSkills;
  };

  const fetchRecommendations = async (targetRole: string, skills: Record<string, number>) => {
    setRecommending(true);
    setRecommendError(null);
    try {
      const rec = await apiService.recommendSkills({
        target_role: targetRole,
        skills,
        preferences: { difficulty_preference: "adaptive", free_only: false, preferred_types: [] },
      });
      setRecommendation(rec);
    } catch (err: any) {
      setRecommendation(null);
      if (err instanceof ApiClientError) {
        const detail = err.details?.[0];
        setRecommendError(detail ? `${err.message} ${detail}` : err.message);
      } else {
        setRecommendError("Failed to generate learning recommendations. Please try again.");
      }
    } finally {
      setRecommending(false);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedRoleId || requirements.length === 0) return;
    const payloadSkills = buildPayloadSkills();
    setAnalyzing(true);
    setAnalyzeError(null);
    setRecommendError(null);
    setRecommendation(null);
    try {
      const [analysisRes, recRes] = await Promise.allSettled([
        apiService.analyzeSkillGap({ target_role: selectedRoleId, skills: payloadSkills }),
        apiService.recommendSkills({
          target_role: selectedRoleId,
          skills: payloadSkills,
          preferences: { difficulty_preference: "adaptive", free_only: false, preferred_types: [] },
        }),
      ]);

      if (analysisRes.status === "fulfilled") {
        setAnalysis(analysisRes.value);
      } else {
        setAnalysis(null);
        const err = analysisRes.reason;
        if (err instanceof ApiClientError) {
          setAnalyzeError({ message: err.message, details: err.details });
        } else {
          setAnalyzeError({ message: "Failed to analyze skills. Please try again." });
        }
      }

      if (recRes.status === "fulfilled") {
        setRecommendation(recRes.value);
      } else {
        setRecommendation(null);
        const err = recRes.reason;
        if (err instanceof ApiClientError) {
          const detail = err.details?.[0];
          setRecommendError(detail ? `${err.message} ${detail}` : err.message);
        } else {
          setRecommendError("Failed to generate learning recommendations. Please try again.");
        }
      }
    } finally {
      setAnalyzing(false);
    }
  };

  const resetAssessmentDefaults = () => {
    setSkillValues(buildDefaultValues(requirements));
    setAnalysis(null);
    setAnalyzeError(null);
    setRecommendation(null);
    setRecommendError(null);
  };

  const handleRetryRecommendations = async () => {
    if (!selectedRoleId || requirements.length === 0) return;
    await fetchRecommendations(selectedRoleId, buildPayloadSkills());
  };

  if (loadingRoles) {
    return (
      <div className="rounded-2xl border border-[#E4E1DA] bg-white p-10 shadow-xs flex flex-col items-center justify-center text-center">
        <Loader2 className="h-8 w-8 animate-spin text-[#3D827C] mb-3" />
        <h2 className="font-heading text-lg font-semibold text-[#202B38]">Loading Skill Intelligence</h2>
        <p className="text-sm text-[#738091] mt-1">Fetching role benchmarks and skill metadata...</p>
      </div>
    );
  }

  if (pageError) {
    return (
      <div className="rounded-2xl border border-rose-200 bg-rose-50 p-6 shadow-xs">
        <div className="flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-rose-600 mt-0.5" />
          <div className="flex-1">
            <h2 className="font-heading text-lg font-semibold text-rose-900">Unable to load Skill Intelligence</h2>
            <p className="text-sm text-rose-700 mt-1">{pageError}</p>
            <button
              type="button"
              onClick={() => window.location.reload()}
              className="mt-4 inline-flex items-center gap-2 rounded-lg border border-rose-300 bg-white px-3 py-2 text-xs font-semibold text-rose-700 hover:bg-rose-100"
            >
              <RefreshCw className="h-3.5 w-3.5" /> Reload Page
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="border-b border-[#E4E1DA] pb-5">
        <div className="flex items-center gap-2 mb-2">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-[#C6A66B]/30 bg-[#F7F3E9] px-2.5 py-1 text-[10px] font-semibold tracking-wider text-[#9A7B3E] uppercase">
            <Sparkles className="h-3 w-3" /> Skill Intelligence
          </span>
          <span className="inline-flex items-center rounded-full border border-[#3D827C]/20 bg-[#EBF3F2] px-2.5 py-1 text-[10px] font-semibold tracking-wider text-[#3D827C] uppercase">
            Rule-based & Explainable
          </span>
        </div>
        <h1 className="font-heading text-2xl sm:text-3xl font-bold tracking-tight text-[#202B38]">
          Skill Intelligence
        </h1>
        <p className="mt-1 text-sm text-[#738091] max-w-3xl leading-relaxed">
          Compare your current skill proficiency against synthetic illustrative role benchmarks to identify gaps,
          prioritize improvements, estimate role readiness, and receive personalized learning recommendations with a
          structured roadmap. Readiness and recommendation scores are explainable decision-support signals, not placement
          probabilities.
        </p>
      </div>

      <RoleSelector
        roles={roles}
        selectedRoleId={selectedRoleId}
        onSelectRole={setSelectedRoleId}
        loading={loadingRoleData}
        selectedRoleName={selectedRoleName}
        skillCount={selectedRoleSummary?.skill_count ?? requirements.length}
        coreSkillCount={selectedRoleSummary?.core_skill_count}
        requirements={requirements}
      />

      {roleError && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800 flex items-start gap-2.5">
          <AlertTriangle className="h-4 w-4 text-rose-600 mt-0.5 shrink-0" />
          <div>
            <div className="font-semibold text-rose-900">Failed to load role requirements</div>
            <div className="mt-0.5">{roleError}</div>
          </div>
        </div>
      )}

      {loadingRoleData && (
        <div className="rounded-xl border border-[#E4E1DA] bg-white p-6 flex items-center gap-3 text-sm text-[#738091]">
          <Loader2 className="h-4 w-4 animate-spin text-[#3D827C]" />
          Loading role requirements and assessment sliders...
        </div>
      )}

      {!loadingRoleData && !roleError && selectedRoleId && requirements.length > 0 && (
        <>
          <div className="flex items-center justify-between gap-3">
            <div className="text-[11px] text-[#738091]">
              Demo defaults prefilled for quick testing. Adjust sliders to reflect your current self-assessed proficiency.
            </div>
            <button
              type="button"
              onClick={resetAssessmentDefaults}
              className="text-xs font-semibold text-[#3D827C] hover:text-[#326B66] underline decoration-[#3D827C]/30"
            >
              Reset demo values
            </button>
          </div>

          <SkillAssessment
            requirements={requirements}
            metadataByKey={metadataByKey}
            values={skillValues}
            onChange={handleSkillChange}
            onAnalyze={handleAnalyze}
            analyzing={analyzing}
            disabled={requirements.length === 0}
          />
        </>
      )}

      {analyzeError && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800">
          <div className="flex items-center gap-2 font-semibold text-rose-900 mb-1">
            <AlertTriangle className="h-4 w-4 text-rose-600" />
            <span>{analyzeError.message}</span>
          </div>
          {analyzeError.details && analyzeError.details.length > 0 && (
            <ul className="list-disc list-inside mt-2 space-y-0.5 text-rose-700">
              {analyzeError.details.map((d, i) => (
                <li key={i}>{d}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {analysis && (
        <div className="space-y-6">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-[#3D827C]" />
            <h2 className="font-heading text-xl font-bold text-[#202B38]">Analysis Results</h2>
            <span className="text-xs text-[#738091]">for {analysis.role_name}</span>
          </div>

          <ReadinessScore analysis={analysis} />
          <SkillGapChart analysis={analysis} />
          <PrioritySkills skills={analysis.top_priority_skills} />
          <ImprovementRoadmap roadmap={analysis.improvement_roadmap} />

          {analysis.disclaimer && (
            <div className="rounded-xl border border-[#E4E1DA] bg-[#FBF9F5] p-4 text-xs text-[#738091] flex items-start gap-2.5">
              <AlertTriangle className="h-4 w-4 text-[#9A7B3E] mt-0.5 shrink-0" />
              <p className="leading-relaxed">{analysis.disclaimer}</p>
            </div>
          )}

          {/* Phase 2: Personalized Learning Recommendations */}
          <div className="space-y-4 pt-2">
            {recommending && !recommendation && (
              <div className="rounded-2xl border border-[#E4E1DA] bg-white p-8 flex items-center justify-center gap-3 text-[#738091]">
                <Loader2 className="h-5 w-5 animate-spin text-[#3D827C]" />
                <span className="text-sm">Generating personalized learning recommendations and 4-stage roadmap...</span>
              </div>
            )}

            {recommendError && (
              <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="h-5 w-5 text-rose-600 mt-0.5 shrink-0" />
                  <div>
                    <h4 className="font-heading text-sm font-semibold text-rose-900">Recommendations unavailable</h4>
                    <p className="text-sm text-rose-700 mt-0.5">{recommendError}</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleRetryRecommendations}
                  disabled={recommending}
                  className="inline-flex items-center gap-2 rounded-lg border border-rose-300 bg-white px-3 py-2 text-xs font-semibold text-rose-700 hover:bg-rose-100 self-start sm:self-auto disabled:opacity-60"
                >
                  <RefreshCw className={`h-3.5 w-3.5 ${recommending ? "animate-spin" : ""}`} /> {recommending ? "Retrying..." : "Retry"}
                </button>
              </div>
            )}

            {recommendation && (
              <>
                {recommendation.dataset_disclosure?.learning_resources && (
                  <div className="rounded-xl border border-[#3D827C]/20 bg-[#EBF3F2] px-4 py-3 text-[11px] text-[#2D615D] leading-relaxed">
                    <span className="font-semibold">Curated resource disclosure:</span>{" "}
                    {recommendation.dataset_disclosure.learning_resources}{" "}
                    {recommendation.dataset_disclosure.recommendation_scores
                      ? recommendation.dataset_disclosure.recommendation_scores
                      : ""}
                  </div>
                )}
                <LearningRecommendations
                  groups={recommendation.recommended_resources_by_skill}
                  summary={recommendation.recommendation_summary}
                  preferences={recommendation.preferences_applied}
                  onRefresh={handleRetryRecommendations}
                  loading={recommending}
                />
                <LearningRoadmap roadmap={recommendation.learning_roadmap} />
              </>
            )}

            {!recommending && !recommendation && !recommendError && (
              <div className="rounded-xl border border-dashed border-[#E4E1DA] bg-[#FBF9F5] p-5 text-sm text-[#738091]">
                Personalized learning recommendations and a 4-stage roadmap will appear here after analysis.
              </div>
            )}
          </div>
        </div>
      )}

      {!analysis && !loadingRoleData && selectedRoleId && requirements.length > 0 && !analyzeError && (
        <div className="rounded-xl border border-dashed border-[#E4E1DA] bg-white p-8 text-center">
          <div className="font-heading text-base font-semibold text-[#202B38]">Ready to analyze</div>
          <p className="mt-1 text-sm text-[#738091]">
            Adjust the sliders above and click <span className="font-semibold text-[#202B38]">Analyze My Skills</span> to
            generate your readiness score, gap charts, priority skills, improvement roadmap, and personalized learning recommendations.
          </p>
        </div>
      )}
    </div>
  );
};
