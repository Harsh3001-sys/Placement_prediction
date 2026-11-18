import React, { useMemo } from "react";
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
import type { SkillAnalysisResponse } from "../../types/placement";

interface SkillGapChartProps {
  analysis: SkillAnalysisResponse;
}

const COLORS = ["#3D827C", "#5A8A9A", "#C6A66B", "#101C2C", "#7C8A99", "#2F6F68", "#8C6E3D", "#4B5563"];

export const SkillGapChart: React.FC<SkillGapChartProps> = ({ analysis }) => {
  const comparisonData = useMemo(
    () =>
      [...analysis.skill_comparison]
        .sort((a, b) => b.importance_weight - a.importance_weight)
        .slice(0, 10)
        .map((s) => ({
          name: s.skill_name.length > 16 ? `${s.skill_name.slice(0, 16)}…` : s.skill_name,
          fullName: s.skill_name,
          Current: s.current_proficiency,
          Required: s.required_proficiency,
          Gap: s.gap,
        })),
    [analysis]
  );

  const gapData = useMemo(
    () =>
      [...analysis.skill_comparison]
        .filter((s) => s.gap > 0)
        .sort((a, b) => b.priority_score - a.priority_score)
        .slice(0, 10)
        .map((s) => ({
          name: s.skill_name.length > 16 ? `${s.skill_name.slice(0, 16)}…` : s.skill_name,
          fullName: s.skill_name,
          Gap: s.gap,
          classification: s.priority_classification,
        })),
    [analysis]
  );

  const categoryData = useMemo(() => {
    const map = new Map<string, { category: string; current: number; required: number; count: number }>();
    for (const s of analysis.skill_comparison) {
      const key = s.skill_category || "Other";
      if (!map.has(key)) map.set(key, { category: key, current: 0, required: 0, count: 0 });
      const item = map.get(key)!;
      item.current += s.current_proficiency;
      item.required += s.required_proficiency;
      item.count += 1;
    }
    return Array.from(map.values()).map((v) => ({
      category: v.category,
      "Avg Current": Number((v.current / v.count).toFixed(1)),
      "Avg Required": Number((v.required / v.count).toFixed(1)),
    }));
  }, [analysis]);

  const gapColor = (classification: string) => {
    if (classification === "Critical Gap") return "#B45309";
    if (classification === "Moderate Gap") return "#C6A66B";
    if (classification === "Minor Gap") return "#5A8A9A";
    return "#3D827C";
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <div className="rounded-2xl border border-[#E4E1DA] bg-white p-5 shadow-xs">
          <div className="mb-4">
            <h3 className="font-heading text-sm font-semibold text-[#202B38]">Current vs Required Proficiency</h3>
            <p className="text-[11px] text-[#738091] mt-0.5">Top skills by importance for the selected role (actual analysis values).</p>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonData} layout="vertical" margin={{ left: 10, right: 16, top: 4, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ECE9E2" />
                <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11, fill: "#738091" }} />
                <YAxis type="category" dataKey="name" width={110} tick={{ fontSize: 11, fill: "#202B38" }} />
                <Tooltip
                  formatter={(value: any, name: any) => [value, name]}
                  labelFormatter={(_, payload) => payload?.[0]?.payload?.fullName || ""}
                />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Bar dataKey="Required" fill="#CBD5E1" radius={[0, 4, 4, 0]} />
                <Bar dataKey="Current" fill="#3D827C" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-2xl border border-[#E4E1DA] bg-white p-5 shadow-xs">
          <div className="mb-4">
            <h3 className="font-heading text-sm font-semibold text-[#202B38]">Skill Gap Visualization</h3>
            <p className="text-[11px] text-[#738091] mt-0.5">Highest-priority gaps (gap = required - current, floored at 0).</p>
          </div>
          <div className="h-80">
            {gapData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={gapData} layout="vertical" margin={{ left: 10, right: 16, top: 4, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ECE9E2" />
                  <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11, fill: "#738091" }} />
                  <YAxis type="category" dataKey="name" width={110} tick={{ fontSize: 11, fill: "#202B38" }} />
                  <Tooltip labelFormatter={(_, payload) => payload?.[0]?.payload?.fullName || ""} />
                  <Bar dataKey="Gap" radius={[0, 4, 4, 0]}>
                    {gapData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={gapColor(entry.classification)} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-sm text-[#738091] border border-dashed border-[#E4E1DA] rounded-xl bg-[#FBF9F5]">
                No skill gaps detected for the provided assessment.
              </div>
            )}
          </div>
        </div>
      </div>

      {categoryData.length > 1 && (
        <div className="rounded-2xl border border-[#E4E1DA] bg-white p-5 shadow-xs">
          <div className="mb-4">
            <h3 className="font-heading text-sm font-semibold text-[#202B38]">Category-wise Skill Overview</h3>
            <p className="text-[11px] text-[#738091] mt-0.5">Average current vs required proficiency by skill category (from API analysis).</p>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData} margin={{ left: 8, right: 8, top: 8, bottom: 24 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ECE9E2" />
                <XAxis dataKey="category" tick={{ fontSize: 11, fill: "#738091" }} interval={0} angle={-15} textAnchor="end" height={50} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: "#738091" }} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Bar dataKey="Avg Required" fill={COLORS[2]} radius={[4, 4, 0, 0]} />
                <Bar dataKey="Avg Current" fill={COLORS[0]} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
};
