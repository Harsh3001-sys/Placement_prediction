import React from "react";
import { AlertCircle, ArrowUpRight, ArrowDownRight } from "lucide-react";

interface FeatureImportanceChartProps {
  coefficients?: Record<string, number>;
}

const DEFAULT_COEFFICIENTS: Record<string, { coef: number; label: string; synthetic?: boolean; category: string }> = {
  AptitudeTestScore: {
    coef: 0.6137,
    label: "Aptitude Test Score",
    category: "Academic",
  },
  PlacementTraining: {
    coef: 0.3917,
    label: "Placement Training",
    category: "Preparation",
  },
  ExtracurricularActivities: {
    coef: 0.3682,
    label: "Extracurricular Activities",
    category: "Experience",
  },
  SSC_Marks: {
    coef: 0.2813,
    label: "SSC Marks (10th)",
    category: "Academic",
  },
  Projects: {
    coef: 0.2638,
    label: "Completed Projects",
    category: "Experience",
  },
  SoftSkillsRating: {
    coef: 0.2635,
    label: "Soft Skills Rating",
    category: "Academic",
  },
  CGPA: {
    coef: 0.2563,
    label: "CGPA",
    category: "Academic",
  },
  HSC_Marks: {
    coef: 0.222,
    label: "HSC Marks (12th)",
    category: "Academic",
  },
  "Workshops/Certifications": {
    coef: 0.0968,
    label: "Workshops & Certifications",
    category: "Preparation",
  },
  Publications: {
    coef: 0.0407,
    label: "Research Publications",
    synthetic: true,
    category: "Technical & Research",
  },
  Internships: {
    coef: -0.0102,
    label: "Internships Count",
    category: "Experience",
  },
  LeetCode_Problems_Solved: {
    coef: -0.0143,
    label: "LeetCode Problems Solved",
    synthetic: true,
    category: "Technical & Research",
  },
  Hackathon_Wins: {
    coef: -0.0408,
    label: "Hackathon Wins",
    synthetic: true,
    category: "Technical & Research",
  },
};

export const FeatureImportanceChart: React.FC<FeatureImportanceChartProps> = ({
  coefficients,
}) => {
  // Sort by absolute magnitude or coefficient value descending
  const items = Object.entries(DEFAULT_COEFFICIENTS)
    .map(([key, def]) => {
      const actualCoef =
        coefficients && coefficients[key] !== undefined
          ? coefficients[key]
          : def.coef;
      return {
        key,
        coef: actualCoef,
        label: def.label,
        synthetic: !!def.synthetic,
        category: def.category,
      };
    })
    .sort((a, b) => b.coef - a.coef);

  const maxAbs = Math.max(...items.map((i) => Math.abs(i.coef)), 0.65);

  return (
    <div className="rounded-xl border border-[#E4E1DA] bg-white p-6 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-[#E4E1DA] pb-4">
        <div>
          <h3 className="font-heading text-base font-semibold text-[#202B38]">
            Standardized Logistic Regression Coefficients
          </h3>
          <p className="text-xs text-[#738091] mt-0.5">
            Feature weights learned after StandardScaler transformation (Log-Odds Impact)
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="flex items-center gap-1 text-[#3D827C]">
            <span className="h-2.5 w-2.5 rounded-sm bg-[#3D827C]" />
            Positive (+ Odds)
          </span>
          <span className="flex items-center gap-1 text-[#C6A66B] ml-2">
            <span className="h-2.5 w-2.5 rounded-sm bg-[#C6A66B]" />
            Synthetic Feature
          </span>
        </div>
      </div>

      <div className="mt-5 space-y-3">
        {items.map((item) => {
          const isPositive = item.coef >= 0;
          const widthPct = (Math.abs(item.coef) / maxAbs) * 100;

          return (
            <div
              key={item.key}
              className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 rounded-lg border border-[#F6F3ED] bg-[#FBF9F5] p-2.5 text-xs transition-all hover:border-[#E4E1DA]"
            >
              {/* Feature Name & Badges */}
              <div className="w-full sm:w-64 flex items-center justify-between sm:justify-start gap-2">
                <span className="font-medium text-[#202B38]">
                  {item.label}
                </span>
                {item.synthetic && (
                  <span className="rounded bg-[#F7F3E9] border border-[#C6A66B]/30 px-1.5 py-0.5 text-[10px] font-semibold text-[#9A7B3E]">
                    Synthetic
                  </span>
                )}
              </div>

              {/* Visual Relative Bar */}
              <div className="flex-1 flex items-center gap-3">
                <div className="relative h-2 w-full overflow-hidden rounded-full bg-[#E4E1DA]/60">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      item.synthetic
                        ? "bg-[#C6A66B]"
                        : isPositive
                        ? "bg-[#3D827C]"
                        : "bg-slate-500"
                    }`}
                    style={{ width: `${Math.max(widthPct, 3)}%` }}
                  />
                </div>

                {/* Numerical Weight */}
                <div className="w-16 text-right font-mono font-semibold text-[11px] flex items-center justify-end gap-0.5">
                  {isPositive ? (
                    <ArrowUpRight className="h-3 w-3 text-[#3D827C]" />
                  ) : (
                    <ArrowDownRight className="h-3 w-3 text-slate-500" />
                  )}
                  <span
                    className={
                      isPositive ? "text-[#3D827C]" : "text-slate-600"
                    }
                  >
                    {item.coef > 0 ? `+${item.coef.toFixed(4)}` : item.coef.toFixed(4)}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Synthetic Feature Disclosure */}
      <div className="mt-6 flex items-start gap-3 rounded-lg border border-[#C6A66B]/25 bg-[#F7F3E9]/80 p-4 text-xs text-[#202B38]">
        <AlertCircle className="h-4 w-4 shrink-0 text-[#9A7B3E] mt-0.5" />
        <div className="space-y-1">
          <div className="font-semibold text-[#9A7B3E]">
            Synthetic Feature Disclosure & Regularization Analysis
          </div>
          <p className="leading-relaxed text-[#738091]">
            The 3 features <strong>LeetCode Problems Solved</strong>, <strong>Hackathon Wins</strong>, and <strong>Publications</strong> were synthetically generated for this academic dataset. Notice that the fitted Logistic Regression model assigned them weights close to zero (between -0.04 and +0.04). This clearly demonstrates how <em>L2 regularization</em> and linear optimization guard against spurious correlation when non-informative variables are added.
          </p>
        </div>
      </div>
    </div>
  );
};
