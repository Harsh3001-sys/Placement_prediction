import React, { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  Brain,
  Loader2,
  Sparkles,
  Target,
  Users,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { apiService, ApiClientError } from "../services/api";
import type {
  SegmentationClusterProfile,
  SegmentationClustersResponse,
  SegmentationOverviewResponse,
  SegmentationPredictResponse,
  SegmentationRoleSummary,
  SkillMetadataItem,
  SkillRequirementItem,
} from "../types/placement";
import { SkillAssessment } from "../components/skill-gap/SkillAssessment";

const CLUSTER_COLORS = ["#3D827C", "#C6A66B", "#5A8A9A", "#101C2C", "#7C8A99", "#8C6E3D", "#2F6F68", "#B45309"];

function fmt(n: any, digits = 2): string {
  const v = Number(n);
  if (!Number.isFinite(v)) return "—";
  return v.toFixed(digits);
}

function shortSkill(name: string): string {
  if (name === "Data Structures and Algorithms") return "DSA";
  if (name === "Object-Oriented Programming") return "OOP";
  if (name === "Git and GitHub") return "Git/GitHub";
  if (name === "Data Visualization") return "Data Viz";
  return name.length > 18 ? `${name.slice(0, 18)}…` : name;
}

function buildDefaultValues(requirements: SkillRequirementItem[]): Record<string, number> {
  const values: Record<string, number> = {};
  for (const skill of requirements) {
    const baseline = Math.round(skill.required_proficiency * 0.65);
    values[skill.skill_name] = Math.max(15, Math.min(90, baseline));
  }
  return values;
}

export const StudentSegmentationPage: React.FC = () => {
  const [roles, setRoles] = useState<SegmentationRoleSummary[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<string>("");
  const [overview, setOverview] = useState<SegmentationOverviewResponse | null>(null);
  const [clustersData, setClustersData] = useState<SegmentationClustersResponse | null>(null);

  const [requirements, setRequirements] = useState<SkillRequirementItem[]>([]);
  const [metadataByKey, setMetadataByKey] = useState<Record<string, SkillMetadataItem | undefined>>({});
  const [skillValues, setSkillValues] = useState<Record<string, number>>({});
  const [predictResult, setPredictResult] = useState<SegmentationPredictResponse | null>(null);

  const [loadingRoles, setLoadingRoles] = useState(true);
  const [loadingRoleData, setLoadingRoleData] = useState(false);
  const [predicting, setPredicting] = useState(false);
  const [pageError, setPageError] = useState<string | null>(null);
  const [roleDataError, setRoleDataError] = useState<string | null>(null);
  const [predictError, setPredictError] = useState<string | null>(null);

  const selectedRole = useMemo(() => roles.find((r) => r.role_id === selectedRoleId) || null, [roles, selectedRoleId]);
  const clusters = clustersData?.clusters || [];

  useEffect(() => {
    let mounted = true;
    (async () => {
      setLoadingRoles(true);
      setPageError(null);
      try {
        const [rolesRes, metadataRes] = await Promise.all([
          apiService.getSegmentationRoles(),
          apiService.getSkillMetadata(),
        ]);
        if (!mounted) return;
        const availableRoles = (rolesRes.roles || []).filter((r) => r.available);
        setRoles(availableRoles);
        const map: Record<string, SkillMetadataItem> = {};
        for (const item of metadataRes.skills || []) {
          map[item.skill_id] = item;
          map[item.skill_name.toLowerCase()] = item;
        }
        setMetadataByKey(map);
        if (availableRoles.length > 0) setSelectedRoleId(availableRoles[0].role_id);
      } catch (err: any) {
        if (!mounted) return;
        if (err instanceof ApiClientError) setPageError(err.message);
        else setPageError("Failed to load Student Segmentation data. Ensure segmentation models are trained and the backend is running.");
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
      setOverview(null);
      setClustersData(null);
      setRequirements([]);
      setSkillValues({});
      setPredictResult(null);
      setRoleDataError(null);
      return;
    }
    let mounted = true;
    (async () => {
      setLoadingRoleData(true);
      setRoleDataError(null);
      setPredictResult(null);
      setPredictError(null);
      try {
        const [ov, cl, reqRes] = await Promise.all([
          apiService.getSegmentationOverview(selectedRoleId),
          apiService.getSegmentationClusters(selectedRoleId),
          apiService.getSkillRequirements(selectedRoleId),
        ]);
        if (!mounted) return;
        setOverview(ov);
        setClustersData(cl);
        const reqs = reqRes.skills || [];
        setRequirements(reqs);
        setSkillValues(buildDefaultValues(reqs));
      } catch (err: any) {
        if (!mounted) return;
        setOverview(null);
        setClustersData(null);
        setRequirements([]);
        setSkillValues({});
        if (err instanceof ApiClientError) setRoleDataError(err.message);
        else setRoleDataError("Failed to load segmentation details for the selected role.");
      } finally {
        if (mounted) setLoadingRoleData(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, [selectedRoleId]);

  const distributionChartData = useMemo(() => {
    const dist =
      overview?.cluster_distribution ||
      clusters.map((c) => ({
        cluster_id: c.cluster_id,
        cluster_name: c.cluster_name,
        student_count: c.student_count,
        student_percentage: c.student_percentage,
      }));
    return dist.map((d, idx) => ({
      ...d,
      label: `C${d.cluster_id}`,
      fill: CLUSTER_COLORS[idx % CLUSTER_COLORS.length],
    }));
  }, [overview, clusters]);

  const comparisonChartData = useMemo(() => {
    if (!clusters.length) return [];
    const featureNames = Object.keys(clusters[0].average_proficiency_per_skill || {});
    return featureNames.map((skill) => {
      const row: Record<string, any> = { skill, skillShort: shortSkill(skill) };
      clusters.forEach((c) => {
        row[`Cluster ${c.cluster_id}`] = Number(c.average_proficiency_per_skill?.[skill] ?? 0);
      });
      return row;
    });
  }, [clusters]);

  const handleSkillChange = (skillName: string, value: number) => {
    const v = Math.max(0, Math.min(100, Math.round(value)));
    setSkillValues((prev) => ({ ...prev, [skillName]: v }));
  };

  const handlePredict = async () => {
    if (!selectedRoleId || requirements.length === 0) return;
    setPredicting(true);
    setPredictError(null);
    try {
      const skills: Record<string, number> = {};
      for (const req of requirements) skills[req.skill_name] = skillValues[req.skill_name] ?? 0;
      const res = await apiService.predictStudentSegment({ target_role: selectedRoleId, skills });
      setPredictResult(res);
    } catch (err: any) {
      setPredictResult(null);
      if (err instanceof ApiClientError) {
        const detail = err.details?.[0];
        setPredictError(detail ? `${err.message} ${detail}` : err.message);
      } else {
        setPredictError("Failed to predict student segment. Please try again.");
      }
    } finally {
      setPredicting(false);
    }
  };

  const resetAssessmentDefaults = () => {
    setSkillValues(buildDefaultValues(requirements));
    setPredictResult(null);
    setPredictError(null);
  };

  if (loadingRoles) {
    return (
      <div className="rounded-2xl border border-[#E4E1DA] bg-white p-10 shadow-xs flex flex-col items-center justify-center text-center">
        <Loader2 className="h-8 w-8 animate-spin text-[#3D827C] mb-3" />
        <h2 className="font-heading text-lg font-semibold text-[#202B38]">Loading Student Segmentation</h2>
        <p className="text-sm text-[#738091] mt-1">Fetching available segmentation roles and model metadata...</p>
      </div>
    );
  }

  if (pageError) {
    return (
      <div className="rounded-2xl border border-rose-200 bg-rose-50 p-6 shadow-xs">
        <div className="flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-rose-600 mt-0.5" />
          <div className="flex-1">
            <h2 className="font-heading text-lg font-semibold text-rose-900">Unable to load Student Segmentation</h2>
            <p className="text-sm text-rose-700 mt-1">{pageError}</p>
            <p className="text-xs text-rose-700 mt-2">
              If models are missing, run <code className="bg-rose-100 px-1 rounded">python backend/scripts/train_student_clusters.py</code> and refresh.
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (roles.length === 0) {
    return (
      <div className="rounded-2xl border border-amber-200 bg-amber-50 p-6 shadow-xs">
        <div className="flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-amber-600 mt-0.5" />
          <div>
            <h2 className="font-heading text-lg font-semibold text-amber-900">No segmentation models available</h2>
            <p className="text-sm text-amber-800 mt-1">Train role-aware K-Means models to enable this dashboard.</p>
            <p className="text-xs text-amber-800 mt-2">Run <code className="bg-amber-100 px-1 rounded">python backend/scripts/train_student_clusters.py</code>.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="border-b border-[#E4E1DA] pb-5">
        <div className="flex items-center gap-2 mb-2 flex-wrap">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-[#3D827C]/20 bg-[#EBF3F2] px-2.5 py-1 text-[10px] font-semibold tracking-wider text-[#3D827C] uppercase">
            <Users className="h-3 w-3" /> Student Segmentation
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-[#C6A66B]/30 bg-[#F7F3E9] px-2.5 py-1 text-[10px] font-semibold tracking-wider text-[#9A7B3E] uppercase">
            <Sparkles className="h-3 w-3" /> Unsupervised K-Means
          </span>
        </div>
        <h1 className="font-heading text-2xl sm:text-3xl font-bold tracking-tight text-[#202B38]">Student Segmentation</h1>
        <p className="mt-1 text-sm text-[#738091] max-w-3xl leading-relaxed">
          Discover role-aware groups of students with similar skill profiles using real K-Means clustering on synthetic student profiles.
          Cluster labels and descriptions are generated dynamically from learned centroids and Phase 1 role requirements. Cluster assignment is not a placement prediction.
        </p>
      </div>

      <div className="rounded-2xl border border-[#E4E1DA] bg-white p-6 shadow-xs space-y-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#EBF3F2] text-[#3D827C] border border-[#3D827C]/10">
            <Target className="h-4.5 w-4.5" />
          </div>
          <div>
            <h2 className="font-heading text-base font-bold text-[#202B38]">Target Role</h2>
            <p className="text-xs text-[#738091]">Select a role to view role-specific clusters and find your segment</p>
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 items-start">
          <div>
            <label className="block text-xs font-semibold text-[#202B38] mb-1.5">Role with trained segmentation model</label>
            <select
              value={selectedRoleId}
              onChange={(e) => setSelectedRoleId(e.target.value)}
              className="w-full rounded-lg border border-[#E4E1DA] bg-white px-3 py-2.5 text-sm text-[#202B38] focus:border-[#3D827C] focus:ring-1 focus:ring-[#3D827C]"
            >
              {roles.map((r) => (
                <option key={r.role_id} value={r.role_id}>
                  {r.role_name}
                </option>
              ))}
            </select>
            <p className="mt-2 text-[11px] text-[#738091]">Role-aware clustering uses only skills relevant to the selected role (Phase 1 mappings).</p>
          </div>
          <div className="lg:col-span-2 rounded-xl border border-[#E4E1DA] bg-[#FBF9F5] p-4">
            {selectedRole ? (
              <div className="space-y-1.5 text-xs text-[#738091]">
                <div className="font-semibold text-[#202B38] text-sm">{selectedRole.role_name}</div>
                <div>
                  Trained with {selectedRole.algorithm || "KMeans"} on {selectedRole.n_samples_trained ?? overview?.students_analyzed ?? "—"} synthetic profiles using {selectedRole.n_features ?? overview?.overall_clustering_summary?.n_features ?? "—"} role-relevant features.
                </div>
                <div>
                  Selected K: <span className="font-semibold text-[#202B38]">{selectedRole.selected_k ?? overview?.selected_k ?? "—"}</span>. Clusters and labels are learned from data (not hardcoded).
                </div>
              </div>
            ) : (
              <div className="text-xs text-[#738091]">Select a role to continue.</div>
            )}
          </div>
        </div>
      </div>

      {roleDataError && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800 flex items-start gap-2.5">
          <AlertTriangle className="h-4 w-4 text-rose-600 mt-0.5 shrink-0" />
          <div>
            <div className="font-semibold text-rose-900">Failed to load role segmentation data</div>
            <div className="mt-0.5">{roleDataError}</div>
          </div>
        </div>
      )}

      {loadingRoleData && (
        <div className="rounded-xl border border-[#E4E1DA] bg-white p-6 flex items-center gap-3 text-sm text-[#738091]">
          <Loader2 className="h-4 w-4 animate-spin text-[#3D827C]" />
          Loading segmentation overview, cluster profiles, and role skill requirements...
        </div>
      )}

      {!loadingRoleData && !roleDataError && overview && clustersData && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="rounded-xl border border-[#E4E1DA] bg-white p-4 shadow-xs">
              <div className="text-[11px] uppercase tracking-wider text-[#738091] font-semibold">Clusters</div>
              <div className="mt-1 font-heading text-2xl font-bold text-[#202B38]">{overview.n_clusters}</div>
              <div className="text-[11px] text-[#738091] mt-1">Discovered groups (selected K)</div>
            </div>
            <div className="rounded-xl border border-[#E4E1DA] bg-white p-4 shadow-xs">
              <div className="text-[11px] uppercase tracking-wider text-[#738091] font-semibold">Students Analyzed</div>
              <div className="mt-1 font-heading text-2xl font-bold text-[#202B38]">{overview.students_analyzed}</div>
              <div className="text-[11px] text-[#738091] mt-1">Synthetic profiles for this role</div>
            </div>
            <div className="rounded-xl border border-[#E4E1DA] bg-white p-4 shadow-xs">
              <div className="text-[11px] uppercase tracking-wider text-[#738091] font-semibold">Selected K</div>
              <div className="mt-1 font-heading text-2xl font-bold text-[#202B38]">{overview.selected_k}</div>
              <div className="text-[11px] text-[#738091] mt-1">Chosen via multi-metric evaluation</div>
            </div>
            <div className="rounded-xl border border-[#E4E1DA] bg-white p-4 shadow-xs">
              <div className="text-[11px] uppercase tracking-wider text-[#738091] font-semibold">Silhouette Score</div>
              <div className="mt-1 font-heading text-2xl font-bold text-[#202B38]">{fmt(overview.clustering_evaluation_metrics?.silhouette_score, 3)}</div>
              <div className="text-[11px] text-[#738091] mt-1">Higher is better (separation indicator)</div>
            </div>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
            <div className="rounded-2xl border border-[#E4E1DA] bg-white p-5 shadow-xs">
              <div className="mb-4 flex items-center justify-between gap-2">
                <div>
                  <h3 className="font-heading text-sm font-semibold text-[#202B38]">Cluster Distribution</h3>
                  <p className="text-[11px] text-[#738091] mt-0.5">Number and percentage of students in each discovered cluster.</p>
                </div>
                <BarChart3 className="h-4 w-4 text-[#3D827C]" />
              </div>
              <div className="h-72">
                {distributionChartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={distributionChartData} margin={{ left: 8, right: 8, top: 8, bottom: 8 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#ECE9E2" />
                      <XAxis dataKey="label" tick={{ fontSize: 11, fill: "#738091" }} />
                      <YAxis tick={{ fontSize: 11, fill: "#738091" }} allowDecimals={false} />
                      <Tooltip
                        formatter={(v: any, n: any, p: any) => [n === "student_count" ? `${v} students (${p?.payload?.student_percentage}%)` : v, n === "student_count" ? "Students" : n]}
                        labelFormatter={(l, payload) => payload?.[0]?.payload?.cluster_name || l}
                      />
                      <Bar dataKey="student_count" radius={[6, 6, 0, 0]}>
                        {distributionChartData.map((entry: any, idx: number) => (
                          <Cell key={`cd-${idx}`} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-sm text-[#738091] border border-dashed border-[#E4E1DA] rounded-xl bg-[#FBF9F5]">No distribution data available.</div>
                )}
              </div>
            </div>

            <div className="rounded-2xl border border-[#E4E1DA] bg-white p-5 shadow-xs">
              <div className="mb-4">
                <h3 className="font-heading text-sm font-semibold text-[#202B38]">Cluster Skill Comparison</h3>
                <p className="text-[11px] text-[#738091] mt-0.5">Average proficiency per role-relevant skill by cluster (real centroid means, original scale).</p>
              </div>
              <div className="h-72">
                {comparisonChartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={comparisonChartData} margin={{ left: 8, right: 8, top: 8, bottom: 28 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#ECE9E2" />
                      <XAxis dataKey="skillShort" interval={0} angle={-25} textAnchor="end" height={55} tick={{ fontSize: 10, fill: "#738091" }} />
                      <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: "#738091" }} />
                      <Tooltip labelFormatter={(_, payload) => payload?.[0]?.payload?.skill || ""} />
                      <Legend wrapperStyle={{ fontSize: 11 }} />
                      {clusters.map((c, idx) => (
                        <Bar key={c.cluster_id} dataKey={`Cluster ${c.cluster_id}`} fill={CLUSTER_COLORS[idx % CLUSTER_COLORS.length]} radius={[3, 3, 0, 0]} />
                      ))}
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center text-sm text-[#738091] border border-dashed border-[#E4E1DA] rounded-xl bg-[#FBF9F5]">No cluster comparison data available.</div>
                )}
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center gap-2 flex-wrap">
              <Brain className="h-5 w-5 text-[#3D827C]" />
              <h2 className="font-heading text-xl font-bold text-[#202B38]">Cluster Profiles</h2>
              <span className="text-xs text-[#738091]">Dynamic labels/descriptions from learned centroids and role requirements</span>
            </div>
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
              {clusters.map((c: SegmentationClusterProfile, idx: number) => (
                <div key={c.cluster_id} className="rounded-2xl border border-[#E4E1DA] bg-white p-5 shadow-xs space-y-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="inline-flex items-center justify-center h-6 min-w-6 px-2 rounded-full text-[11px] font-bold text-white" style={{ backgroundColor: CLUSTER_COLORS[idx % CLUSTER_COLORS.length] }}>
                          C{c.cluster_id}
                        </span>
                        <h3 className="font-heading text-base font-bold text-[#202B38]">{c.cluster_name}</h3>
                      </div>
                      <p className="mt-2 text-xs text-[#738091] leading-relaxed">{c.cluster_description}</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-2.5">
                      <div className="text-[10px] uppercase tracking-wider text-[#738091] font-semibold">Students</div>
                      <div className="font-heading text-lg font-bold text-[#202B38]">{c.student_count}</div>
                    </div>
                    <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-2.5">
                      <div className="text-[10px] uppercase tracking-wider text-[#738091] font-semibold">Share</div>
                      <div className="font-heading text-lg font-bold text-[#202B38]">{fmt(c.student_percentage, 1)}%</div>
                    </div>
                    <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-2.5">
                      <div className="text-[10px] uppercase tracking-wider text-[#738091] font-semibold">Avg Proficiency</div>
                      <div className="font-heading text-lg font-bold text-[#202B38]">{fmt(c.average_skill_proficiency, 1)}</div>
                    </div>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div className="rounded-xl border border-[#3D827C]/15 bg-[#F4FAF9] p-3">
                      <div className="text-[11px] font-semibold text-[#2D615D] mb-2">Strongest skills (vs role avg)</div>
                      <ul className="space-y-1.5">
                        {(c.strongest_skills || []).slice(0, 3).map((s, i) => (
                          <li key={i} className="text-xs text-[#202B38] flex items-center justify-between gap-2">
                            <span className="truncate">{s.skill_name}</span>
                            <span className="font-mono text-[11px] text-[#3D827C]">{fmt(s.cluster_average, 1)}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div className="rounded-xl border border-amber-200/60 bg-amber-50/50 p-3">
                      <div className="text-[11px] font-semibold text-[#9A7B3E] mb-2">Weakest skills (vs role avg)</div>
                      <ul className="space-y-1.5">
                        {(c.weakest_skills || []).slice(0, 3).map((s, i) => (
                          <li key={i} className="text-xs text-[#202B38] flex items-center justify-between gap-2">
                            <span className="truncate">{s.skill_name}</span>
                            <span className="font-mono text-[11px] text-[#9A7B3E]">{fmt(s.cluster_average, 1)}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {overview.clustering_evaluation_metrics && (
            <div className="rounded-2xl border border-[#E4E1DA] bg-[#FBF9F5] p-5 shadow-xs">
              <h3 className="font-heading text-sm font-semibold text-[#202B38] mb-3">Clustering Evaluation (Selected K = {overview.selected_k})</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                <div className="rounded-lg border border-[#E4E1DA] bg-white p-3"><div className="text-[#738091]">Silhouette (higher better)</div><div className="font-semibold text-[#202B38] mt-1">{fmt(overview.clustering_evaluation_metrics.silhouette_score, 4)}</div></div>
                <div className="rounded-lg border border-[#E4E1DA] bg-white p-3"><div className="text-[#738091]">Davies-Bouldin (lower better)</div><div className="font-semibold text-[#202B38] mt-1">{fmt(overview.clustering_evaluation_metrics.davies_bouldin_score, 4)}</div></div>
                <div className="rounded-lg border border-[#E4E1DA] bg-white p-3"><div className="text-[#738091]">Calinski-Harabasz (higher better)</div><div className="font-semibold text-[#202B38] mt-1">{fmt(overview.clustering_evaluation_metrics.calinski_harabasz_score, 4)}</div></div>
                <div className="rounded-lg border border-[#E4E1DA] bg-white p-3"><div className="text-[#738091]">WCSS / Inertia</div><div className="font-semibold text-[#202B38] mt-1">{fmt(overview.clustering_evaluation_metrics.wcss, 2)}</div></div>
              </div>
              {overview.k_selection?.rationale && <p className="mt-3 text-[11px] text-[#738091] leading-relaxed"><span className="font-semibold text-[#202B38]">K selection rationale: </span>{String(overview.k_selection.rationale)}</p>}
            </div>
          )}

          <div className="border-t border-[#E4E1DA] pt-6 space-y-4">
            <div className="flex items-center justify-between gap-3 flex-wrap">
              <div>
                <h2 className="font-heading text-xl font-bold text-[#202B38]">Find My Student Segment</h2>
                <p className="text-sm text-[#738091] mt-1">Enter your current role-relevant skill proficiencies to predict your closest K-Means cluster (no retraining; uses persisted role model/scaler).</p>
              </div>
              <button type="button" onClick={resetAssessmentDefaults} className="text-xs font-semibold text-[#3D827C] hover:text-[#326B66] underline decoration-[#3D827C]/30">Reset demo values</button>
            </div>

            {requirements.length > 0 ? (
              <SkillAssessment
                requirements={requirements}
                metadataByKey={metadataByKey}
                values={skillValues}
                onChange={handleSkillChange}
                onAnalyze={handlePredict}
                analyzing={predicting}
                disabled={requirements.length === 0}
              />
            ) : (
              <div className="rounded-xl border border-dashed border-[#E4E1DA] bg-[#FBF9F5] p-5 text-sm text-[#738091]">Role skill requirements unavailable for personal segmentation.</div>
            )}

            {predictError && (
              <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-xs text-rose-800 flex items-start gap-2.5">
                <AlertTriangle className="h-4 w-4 text-rose-600 mt-0.5 shrink-0" />
                <div>
                  <div className="font-semibold text-rose-900">Prediction failed</div>
                  <div className="mt-0.5">{predictError}</div>
                </div>
              </div>
            )}

            {predictResult && (
              <div className="space-y-4">
                <div className="rounded-2xl border border-[#3D827C]/20 bg-[#F4FAF9] p-5 shadow-xs">
                  <div className="flex items-start justify-between gap-3 flex-wrap">
                    <div>
                      <div className="text-[11px] uppercase tracking-wider text-[#2D615D] font-semibold">Predicted Segment</div>
                      <h3 className="font-heading text-xl font-bold text-[#202B38] mt-1">Cluster {predictResult.predicted_cluster_id}: {predictResult.cluster_name}</h3>
                      <p className="text-sm text-[#738091] mt-2 leading-relaxed">{predictResult.cluster_description}</p>
                    </div>
                    <div className="rounded-xl border border-[#3D827C]/20 bg-white px-4 py-3 text-center min-w-[140px]">
                      <div className="text-[10px] uppercase tracking-wider text-[#738091] font-semibold">Cluster avg proficiency</div>
                      <div className="font-heading text-2xl font-bold text-[#202B38]">{fmt((predictResult.cluster_characteristics as any)?.average_skill_proficiency, 1)}</div>
                    </div>
                  </div>
                  {predictResult.why_this_cluster && predictResult.why_this_cluster.length > 0 && (
                    <div className="mt-4 rounded-xl border border-[#E4E1DA] bg-white p-4">
                      <div className="text-xs font-semibold text-[#202B38] mb-2">Why you belong to this cluster</div>
                      <ul className="space-y-1.5 text-xs text-[#738091] list-disc list-inside">
                        {predictResult.why_this_cluster.map((r, i) => <li key={i}>{r}</li>)}
                      </ul>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <div className="rounded-2xl border border-[#E4E1DA] bg-white p-5 shadow-xs">
                    <h4 className="font-heading text-sm font-semibold text-[#202B38] mb-3">Your strongest skills (in this assessment)</h4>
                    <div className="space-y-2">
                      {(predictResult.student_strongest_skills || []).slice(0, 5).map((s: any, i: number) => (
                        <div key={i} className="flex items-center justify-between gap-3 rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] px-3 py-2 text-xs">
                          <span className="font-medium text-[#202B38] truncate">{s.skill_name}</span>
                          <span className="font-mono text-[#3D827C]">{fmt(s.student_proficiency, 1)} <span className="text-[#738091]">(cluster {fmt(s.cluster_average, 1)})</span></span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="rounded-2xl border border-[#E4E1DA] bg-white p-5 shadow-xs">
                    <h4 className="font-heading text-sm font-semibold text-[#202B38] mb-3">Your weakest skills (in this assessment)</h4>
                    <div className="space-y-2">
                      {(predictResult.student_weakest_skills || []).slice(0, 5).map((s: any, i: number) => (
                        <div key={i} className="flex items-center justify-between gap-3 rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] px-3 py-2 text-xs">
                          <span className="font-medium text-[#202B38] truncate">{s.skill_name}</span>
                          <span className="font-mono text-[#9A7B3E]">{fmt(s.student_proficiency, 1)} <span className="text-[#738091]">(cluster {fmt(s.cluster_average, 1)})</span></span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="rounded-2xl border border-[#E4E1DA] bg-white p-5 shadow-xs">
                  <h4 className="font-heading text-sm font-semibold text-[#202B38] mb-1">Comparison with Cluster Average</h4>
                  <p className="text-[11px] text-[#738091] mb-4">Differences highlight how your submitted profile deviates from your predicted cluster centroid (positive = above cluster average).</p>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={(predictResult.comparison_with_cluster || []).slice(0, 12)} layout="vertical" margin={{ left: 10, right: 20, top: 4, bottom: 4 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#ECE9E2" />
                        <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11, fill: "#738091" }} />
                        <YAxis type="category" dataKey="skill_name" width={140} tick={{ fontSize: 11, fill: "#202B38" }} tickFormatter={(v) => shortSkill(String(v))} />
                        <Tooltip formatter={(v: any, n: any) => [v, n === "student_proficiency" ? "You" : "Cluster Avg"]} labelFormatter={(l) => String(l)} />
                        <Legend wrapperStyle={{ fontSize: 11 }} />
                        <Bar dataKey="cluster_average" fill="#CBD5E1" radius={[0, 4, 4, 0]} name="Cluster Avg" />
                        <Bar dataKey="student_proficiency" fill="#3D827C" radius={[0, 4, 4, 0]} name="You" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-2">
                    {[...(predictResult.comparison_with_cluster || [])]
                      .sort((a, b) => Math.abs(Number(b.difference_from_cluster || 0)) - Math.abs(Number(a.difference_from_cluster || 0)))
                      .slice(0, 6)
                      .map((item, i) => {
                        const diff = Number(item.difference_from_cluster || 0);
                        const positive = diff >= 0;
                        return (
                          <div key={i} className={`rounded-lg border px-3 py-2 text-xs flex items-center justify-between gap-2 ${positive ? "border-[#3D827C]/20 bg-[#F4FAF9]" : "border-amber-200 bg-amber-50/60"}`}>
                            <span className="font-medium text-[#202B38] truncate">{item.skill_name}</span>
                            <span className={`font-mono font-semibold ${positive ? "text-[#3D827C]" : "text-[#9A7B3E]"}`}>{diff >= 0 ? "+" : ""}{fmt(diff, 1)} vs cluster</span>
                          </div>
                        );
                      })}
                  </div>
                </div>

                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                  <div className="rounded-2xl border border-[#E4E1DA] bg-white p-5 shadow-xs">
                    <h4 className="font-heading text-sm font-semibold text-[#202B38] mb-1">Personal Skill Gaps (Phase 1 Integration)</h4>
                    <p className="text-[11px] text-[#738091] mb-3">Computed from your submitted profile vs role benchmark requirements (rule-based, not placement probability).</p>
                    <div className="text-xs text-[#738091] mb-3">Readiness: <span className="font-semibold text-[#202B38]">{fmt(predictResult.personal_skill_gaps?.overall_readiness_score, 1)}</span> / 100</div>
                    <div className="space-y-2">
                      {((predictResult.personal_skill_gaps?.top_priority_skills as any[]) || []).slice(0, 5).map((s: any, i: number) => (
                        <div key={i} className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] px-3 py-2 text-xs">
                          <div className="flex items-center justify-between gap-2"><span className="font-semibold text-[#202B38]">{s.skill_name}</span><span className="text-[#9A7B3E] font-medium">{s.priority_classification}</span></div>
                          <div className="text-[#738091] mt-0.5">Gap {fmt(s.gap, 1)} (current {fmt(s.current_proficiency, 1)} / required {fmt(s.required_proficiency, 1)})</div>
                        </div>
                      ))}
                      {(!predictResult.personal_skill_gaps?.top_priority_skills || (predictResult.personal_skill_gaps.top_priority_skills as any[]).length === 0) && (
                        <div className="text-xs text-[#738091]">No priority personal gaps identified.</div>
                      )}
                    </div>
                  </div>
                  <div className="rounded-2xl border border-[#E4E1DA] bg-white p-5 shadow-xs">
                    <h4 className="font-heading text-sm font-semibold text-[#202B38] mb-1">Cluster-Level Weaknesses</h4>
                    <p className="text-[11px] text-[#738091] mb-3">Derived from the predicted cluster centroid profile for your role cohort (group pattern, not your individual assessment alone).</p>
                    <div className="space-y-2">
                      {((predictResult.cluster_level_weaknesses?.weakest_skills as any[]) || []).slice(0, 5).map((s: any, i: number) => (
                        <div key={i} className="flex items-center justify-between gap-3 rounded-lg border border-amber-200/60 bg-amber-50/40 px-3 py-2 text-xs">
                          <span className="font-medium text-[#202B38] truncate">{s.skill_name}</span>
                          <span className="font-mono text-[#9A7B3E]">{fmt(s.cluster_average, 1)} avg</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="rounded-2xl border border-[#E4E1DA] bg-white p-5 shadow-xs space-y-4">
                  <h4 className="font-heading text-sm font-semibold text-[#202B38]">Recommended Areas of Improvement & Learning Suggestions (Phase 2 Integration)</h4>
                  <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                    <div className="rounded-xl border border-[#E4E1DA] bg-[#FBF9F5] p-4">
                      <div className="text-xs font-semibold text-[#202B38] mb-1">Based on individual gaps</div>
                      <p className="text-[11px] text-[#738091] mb-3">Resources recommended by reusing the existing Phase 2 recommendation engine for your personal skill gaps.</p>
                      {(() => {
                        const groups = (predictResult.recommendations_based_on_individual_gaps as any)?.recommended_resources_by_skill || [];
                        if (!groups.length) return <div className="text-xs text-[#738091]">No individual-gap recommendations available.</div>;
                        return (
                          <div className="space-y-3">
                            {groups.slice(0, 3).map((g: any, gi: number) => (
                              <div key={gi} className="rounded-lg border border-[#E4E1DA] bg-white p-3">
                                <div className="text-xs font-semibold text-[#202B38]">{g.skill_name} <span className="text-[#738091] font-normal">({g.priority_classification || "Priority"})</span></div>
                                <ul className="mt-2 space-y-1.5">
                                  {(g.resources || []).slice(0, 2).map((r: any, ri: number) => (
                                    <li key={ri} className="text-[11px] text-[#738091]">
                                      <a href={r.resource_url} target="_blank" rel="noreferrer" className="text-[#3D827C] font-medium hover:underline">{r.resource_title}</a>
                                      <span> — {r.provider} · {r.difficulty_level} · {r.is_free ? "Free" : "Paid"}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            ))}
                          </div>
                        );
                      })()}
                    </div>
                    <div className="rounded-xl border border-[#E4E1DA] bg-[#FBF9F5] p-4">
                      <div className="text-xs font-semibold text-[#202B38] mb-1">Based on cluster patterns</div>
                      <p className="text-[11px] text-[#738091] mb-3">Resources suggested for weaknesses common in your predicted cluster (reusing existing Phase 2 dataset/engine; group-level guidance).</p>
                      {(() => {
                        const clusterRec = predictResult.recommendations_based_on_cluster_patterns as any;
                        const groups = clusterRec?.recommended_resources_by_skill || [];
                        const hints = clusterRec?.resource_suggestions_for_cluster_weaknesses?.suggested_resources || [];
                        if (!groups.length && !hints.length) return <div className="text-xs text-[#738091]">No cluster-pattern recommendations available.</div>;
                        return (
                          <div className="space-y-3">
                            {groups.slice(0, 2).map((g: any, gi: number) => (
                              <div key={gi} className="rounded-lg border border-[#E4E1DA] bg-white p-3">
                                <div className="text-xs font-semibold text-[#202B38]">{g.skill_name} <span className="text-[#738091] font-normal">(cluster pattern)</span></div>
                                <ul className="mt-2 space-y-1.5">
                                  {(g.resources || []).slice(0, 2).map((r: any, ri: number) => (
                                    <li key={ri} className="text-[11px] text-[#738091]">
                                      <a href={r.resource_url} target="_blank" rel="noreferrer" className="text-[#3D827C] font-medium hover:underline">{r.resource_title}</a>
                                      <span> — {r.provider} · {r.difficulty_level}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            ))}
                            {hints.length > 0 && (
                              <div className="rounded-lg border border-[#E4E1DA] bg-white p-3">
                                <div className="text-xs font-semibold text-[#202B38]">Cluster weakness resource hints</div>
                                <ul className="mt-2 space-y-1.5">
                                  {hints.slice(0, 4).map((r: any, ri: number) => (
                                    <li key={ri} className="text-[11px] text-[#738091]">
                                      <span className="font-medium text-[#202B38]">{r.skill_name}:</span>{" "}
                                      <a href={r.resource_url} target="_blank" rel="noreferrer" className="text-[#3D827C] hover:underline">{r.resource_title}</a>
                                      <span> ({r.provider})</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        );
                      })()}
                    </div>
                  </div>
                  {predictResult.integration_notes && (
                    <div className="rounded-lg border border-[#E4E1DA] bg-[#FBF9F5] p-3 text-[11px] text-[#738091] leading-relaxed">
                      <div><span className="font-semibold text-[#202B38]">Phase 1:</span> {String((predictResult.integration_notes as any).phase1 || "")}</div>
                      <div className="mt-1"><span className="font-semibold text-[#202B38]">Phase 2:</span> {String((predictResult.integration_notes as any).phase2 || "")}</div>
                      <div className="mt-1"><span className="font-semibold text-[#202B38]">Distinction:</span> {String((predictResult.integration_notes as any).distinction || "")}</div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {(overview.disclosure || clustersData.disclosure) && (
            <div className="rounded-xl border border-[#E4E1DA] bg-[#FBF9F5] p-4 text-xs text-[#738091] flex items-start gap-2.5">
              <AlertTriangle className="h-4 w-4 text-[#9A7B3E] mt-0.5 shrink-0" />
              <p className="leading-relaxed">{overview.disclosure || clustersData.disclosure}</p>
            </div>
          )}
        </>
      )}
    </div>
  );
};
