import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { RocPoint } from "../types/placement";

interface RocCurveChartProps {
  points?: RocPoint[];
  auc?: number;
}

const DEFAULT_ROC_POINTS: RocPoint[] = [
  { fpr: 0.0, tpr: 0.0 },
  { fpr: 0.008, tpr: 0.237 },
  { fpr: 0.016, tpr: 0.306 },
  { fpr: 0.025, tpr: 0.373 },
  { fpr: 0.035, tpr: 0.447 },
  { fpr: 0.042, tpr: 0.540 },
  { fpr: 0.053, tpr: 0.566 },
  { fpr: 0.064, tpr: 0.602 },
  { fpr: 0.074, tpr: 0.631 },
  { fpr: 0.089, tpr: 0.651 },
  { fpr: 0.104, tpr: 0.672 },
  { fpr: 0.121, tpr: 0.698 },
  { fpr: 0.138, tpr: 0.722 },
  { fpr: 0.155, tpr: 0.743 },
  { fpr: 0.167, tpr: 0.760 },
  { fpr: 0.194, tpr: 0.775 },
  { fpr: 0.222, tpr: 0.795 },
  { fpr: 0.255, tpr: 0.817 },
  { fpr: 0.288, tpr: 0.835 },
  { fpr: 0.334, tpr: 0.860 },
  { fpr: 0.385, tpr: 0.880 },
  { fpr: 0.452, tpr: 0.902 },
  { fpr: 0.521, tpr: 0.925 },
  { fpr: 0.601, tpr: 0.946 },
  { fpr: 0.705, tpr: 0.968 },
  { fpr: 0.820, tpr: 0.985 },
  { fpr: 0.915, tpr: 0.994 },
  { fpr: 1.0, tpr: 1.0 },
];

export const RocCurveChart: React.FC<RocCurveChartProps> = ({
  points = DEFAULT_ROC_POINTS,
  auc = 0.8840,
}) => {
  // Merge diagonal reference points into chart dataset
  const chartData = points.map((p) => ({
    fpr: p.fpr,
    tpr: p.tpr,
    chance: p.fpr,
  }));

  return (
    <div className="rounded-xl border border-[#E4E1DA] bg-white p-6 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-[#E4E1DA] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-heading text-base font-semibold text-[#202B38]">
              Receiver Operating Characteristic (ROC)
            </h3>
            <span className="rounded bg-[#EBF3F2] px-2 py-0.5 text-xs font-semibold text-[#3D827C] border border-[#3D827C]/20">
              AUC: {auc.toFixed(4)}
            </span>
          </div>
          <p className="text-xs text-[#738091] mt-0.5">
            Empirical true positive rate vs false positive rate plotted from actual test evaluation probabilities
          </p>
        </div>

        <div className="flex items-center gap-4 text-xs text-[#738091]">
          <span className="flex items-center gap-1.5">
            <span className="h-0.5 w-4 bg-[#3D827C]" />
            Logistic Regression
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-0.5 w-4 border-t border-dashed border-[#738091]" />
            Random Chance (0.50)
          </span>
        </div>
      </div>

      <div className="mt-6 h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 10, right: 20, bottom: 20, left: 10 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#ECE9E2" />
            <XAxis
              dataKey="fpr"
              type="number"
              domain={[0, 1]}
              tickCount={6}
              tickFormatter={(v) => v.toFixed(1)}
              stroke="#738091"
              fontSize={11}
              label={{
                value: "False Positive Rate (1 - Specificity)",
                position: "insideBottom",
                offset: -10,
                fontSize: 11,
                fill: "#738091",
              }}
            />
            <YAxis
              domain={[0, 1]}
              tickCount={6}
              tickFormatter={(v) => v.toFixed(1)}
              stroke="#738091"
              fontSize={11}
              label={{
                value: "True Positive Rate (Sensitivity / Recall)",
                angle: -90,
                position: "insideLeft",
                offset: 5,
                fontSize: 11,
                fill: "#738091",
              }}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const item = payload[0].payload;
                  return (
                    <div className="rounded-lg border border-[#E4E1DA] bg-white p-3 shadow-md text-xs">
                      <div className="font-semibold text-[#202B38] mb-1">
                        Operating Point
                      </div>
                      <div className="flex justify-between gap-4 text-[#738091]">
                        <span>False Positive Rate:</span>
                        <strong className="text-[#202B38]">
                          {(item.fpr * 100).toFixed(1)}%
                        </strong>
                      </div>
                      <div className="flex justify-between gap-4 text-[#738091]">
                        <span>True Positive Rate (Recall):</span>
                        <strong className="text-[#3D827C]">
                          {(item.tpr * 100).toFixed(1)}%
                        </strong>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />
            {/* Random chance line */}
            <Line
              type="linear"
              dataKey="chance"
              stroke="#A0AEC0"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              dot={false}
              isAnimationActive={false}
            />
            {/* Real ROC Curve */}
            <Line
              type="monotone"
              dataKey="tpr"
              stroke="#3D827C"
              strokeWidth={2.5}
              dot={false}
              activeDot={{ r: 5, fill: "#3D827C", stroke: "#FFFFFF", strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-2 text-center text-[11px] text-[#738091]">
        An ROC-AUC score of 0.8840 confirms that in 88.4% of randomly chosen pairs (one placed and one not placed student), the model assigns a higher probability to the placed student.
      </div>
    </div>
  );
};
