import React from "react";

interface MetricCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  badge?: string;
  badgeType?: "teal" | "gold" | "neutral";
  icon?: React.ReactNode;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subtext,
  badge,
  badgeType = "neutral",
  icon,
}) => {
  const badgeClasses = {
    teal: "bg-[#EBF3F2] text-[#3D827C] border-[#3D827C]/20",
    gold: "bg-[#F7F3E9] text-[#9A7B3E] border-[#C6A66B]/30",
    neutral: "bg-[#F6F3ED] text-[#738091] border-[#E4E1DA]",
  }[badgeType];

  return (
    <div className="relative flex flex-col justify-between rounded-xl border border-[#E4E1DA] bg-white p-5 shadow-xs transition-all hover:border-[#738091]/30">
      <div className="flex items-start justify-between gap-3">
        <span className="text-xs font-semibold tracking-wider text-[#738091] uppercase">
          {label}
        </span>
        <div className="flex items-center gap-2">
          {badge && (
            <span
              className={`rounded border px-2 py-0.5 text-[10px] font-semibold tracking-wide ${badgeClasses}`}
            >
              {badge}
            </span>
          )}
          {icon && <div className="text-[#738091]">{icon}</div>}
        </div>
      </div>

      <div className="mt-3">
        <div className="font-heading text-3xl font-bold tracking-tight text-[#202B38]">
          {value}
        </div>
        {subtext && (
          <p className="mt-1 text-xs leading-relaxed text-[#738091]">
            {subtext}
          </p>
        )}
      </div>
    </div>
  );
};
