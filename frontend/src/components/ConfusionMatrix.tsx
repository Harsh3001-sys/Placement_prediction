import React from "react";
import { Check, X, Info } from "lucide-react";
import type { ConfusionMatrixData } from "../types/placement";

interface ConfusionMatrixProps {
  data?: ConfusionMatrixData;
}

export const ConfusionMatrix: React.FC<ConfusionMatrixProps> = ({ data }) => {
  const tn = data?.true_negative ?? 967;
  const fp = data?.false_positive ?? 194;
  const fn = data?.false_negative ?? 189;
  const tp = data?.true_positive ?? 650;
  const total = tn + fp + fn + tp;

  return (
    <div className="rounded-xl border border-[#E4E1DA] bg-white p-6 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-[#E4E1DA] pb-4">
        <div>
          <h3 className="font-heading text-base font-semibold text-[#202B38]">
            Test Set Confusion Matrix
          </h3>
          <p className="text-xs text-[#738091]">
            Evaluation on N = {total.toLocaleString()} stratified test cases (80/20 train/test split)
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-[#738091]">
          <span className="flex items-center gap-1">
            <span className="h-2.5 w-2.5 rounded-sm bg-[#3D827C]/20 border border-[#3D827C]" />
            Correct (80.85%)
          </span>
          <span className="flex items-center gap-1 ml-2">
            <span className="h-2.5 w-2.5 rounded-sm bg-[#C6A66B]/20 border border-[#C6A66B]" />
            Misclassified (19.15%)
          </span>
        </div>
      </div>

      {/* Matrix Table */}
      <div className="mt-6 overflow-x-auto">
        <div className="min-w-[480px]">
          {/* Header columns */}
          <div className="grid grid-cols-12 gap-3 pb-2 text-center text-xs font-semibold text-[#738091]">
            <div className="col-span-3"></div>
            <div className="col-span-9 grid grid-cols-2 gap-3">
              <div className="rounded-md bg-[#F6F3ED] py-1.5 uppercase tracking-wider text-[11px] text-[#202B38]">
                Predicted: Not Placed
              </div>
              <div className="rounded-md bg-[#F6F3ED] py-1.5 uppercase tracking-wider text-[11px] text-[#202B38]">
                Predicted: Placed
              </div>
            </div>
          </div>

          {/* Row 1: Actual Not Placed */}
          <div className="grid grid-cols-12 gap-3 py-1.5 items-stretch">
            <div className="col-span-3 flex flex-col justify-center rounded-md bg-[#F6F3ED] px-3 py-2 text-left">
              <span className="text-xs font-semibold text-[#202B38]">
                Actual: Not Placed
              </span>
              <span className="text-[11px] text-[#738091]">
                Total: {(tn + fp).toLocaleString()} (58.05%)
              </span>
            </div>

            <div className="col-span-9 grid grid-cols-2 gap-3">
              {/* True Negative */}
              <div className="flex flex-col justify-between rounded-lg border border-[#3D827C]/30 bg-[#EBF3F2] p-4 text-left transition-all hover:border-[#3D827C]">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-[#3D827C]">
                    True Negative (TN)
                  </span>
                  <Check className="h-4 w-4 text-[#3D827C]" />
                </div>
                <div className="my-2">
                  <div className="font-heading text-2xl font-bold text-[#202B38]">
                    {tn.toLocaleString()}
                  </div>
                  <div className="text-[11px] text-[#738091]">
                    {((tn / (tn + fp)) * 100).toFixed(2)}% of actual NotPlaced
                  </div>
                </div>
                <div className="text-[10px] text-[#738091] border-t border-[#3D827C]/15 pt-1.5">
                  Specificity: 83.29%
                </div>
              </div>

              {/* False Positive */}
              <div className="flex flex-col justify-between rounded-lg border border-[#C6A66B]/30 bg-[#F7F3E9] p-4 text-left transition-all hover:border-[#C6A66B]">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-[#9A7B3E]">
                    False Positive (FP)
                  </span>
                  <X className="h-4 w-4 text-[#9A7B3E]" />
                </div>
                <div className="my-2">
                  <div className="font-heading text-2xl font-bold text-[#202B38]">
                    {fp.toLocaleString()}
                  </div>
                  <div className="text-[11px] text-[#738091]">
                    {((fp / (tn + fp)) * 100).toFixed(2)}% of actual NotPlaced
                  </div>
                </div>
                <div className="text-[10px] text-[#738091] border-t border-[#C6A66B]/15 pt-1.5">
                  Type I Error (False Alarm)
                </div>
              </div>
            </div>
          </div>

          {/* Row 2: Actual Placed */}
          <div className="grid grid-cols-12 gap-3 py-1.5 items-stretch">
            <div className="col-span-3 flex flex-col justify-center rounded-md bg-[#F6F3ED] px-3 py-2 text-left">
              <span className="text-xs font-semibold text-[#202B38]">
                Actual: Placed
              </span>
              <span className="text-[11px] text-[#738091]">
                Total: {(fn + tp).toLocaleString()} (41.95%)
              </span>
            </div>

            <div className="col-span-9 grid grid-cols-2 gap-3">
              {/* False Negative */}
              <div className="flex flex-col justify-between rounded-lg border border-[#C6A66B]/30 bg-[#F7F3E9] p-4 text-left transition-all hover:border-[#C6A66B]">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-[#9A7B3E]">
                    False Negative (FN)
                  </span>
                  <X className="h-4 w-4 text-[#9A7B3E]" />
                </div>
                <div className="my-2">
                  <div className="font-heading text-2xl font-bold text-[#202B38]">
                    {fn.toLocaleString()}
                  </div>
                  <div className="text-[11px] text-[#738091]">
                    {((fn / (fn + tp)) * 100).toFixed(2)}% of actual Placed
                  </div>
                </div>
                <div className="text-[10px] text-[#738091] border-t border-[#C6A66B]/15 pt-1.5">
                  Type II Error (Missed Placement)
                </div>
              </div>

              {/* True Positive */}
              <div className="flex flex-col justify-between rounded-lg border border-[#3D827C]/30 bg-[#EBF3F2] p-4 text-left transition-all hover:border-[#3D827C]">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-[#3D827C]">
                    True Positive (TP)
                  </span>
                  <Check className="h-4 w-4 text-[#3D827C]" />
                </div>
                <div className="my-2">
                  <div className="font-heading text-2xl font-bold text-[#202B38]">
                    {tp.toLocaleString()}
                  </div>
                  <div className="text-[11px] text-[#738091]">
                    {((tp / (fn + tp)) * 100).toFixed(2)}% of actual Placed
                  </div>
                </div>
                <div className="text-[10px] text-[#738091] border-t border-[#3D827C]/15 pt-1.5">
                  Recall: 77.47% · Precision: 77.01%
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Summary Note */}
      <div className="mt-5 flex items-start gap-2.5 rounded-lg border border-[#E4E1DA] bg-[#F6F3ED] p-3 text-xs text-[#738091]">
        <Info className="h-4 w-4 shrink-0 text-[#3D827C] mt-0.5" />
        <p className="leading-relaxed">
          The test split maintains class stratification matching the overall population (58% Not Placed / 42% Placed). The model correctly predicted 1,617 out of 2,000 cases, yielding an exact test accuracy of <strong>80.85%</strong> and balanced F1-score of <strong>77.24%</strong>.
        </p>
      </div>
    </div>
  );
};
