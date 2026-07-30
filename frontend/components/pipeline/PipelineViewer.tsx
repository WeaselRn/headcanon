"use client";

import { motion } from "framer-motion";
import { CheckCircle, Circle, Loader2 } from "lucide-react";

const PIPELINE_STAGES = [
  "Generate Story",
  "Split Scenes",
  "Generate Images",
  "Generate Narration",
  "Generate Music",
  "Upload Assets",
  "Generate Manifest",
] as const;

type Stage = (typeof PIPELINE_STAGES)[number];

type StageStatus = "pending" | "active" | "done";

interface Props {
  activeStage?: Stage;
  completedStages?: Stage[];
}

function getStatus(
  stage: Stage,
  active?: Stage,
  completed?: Stage[]
): StageStatus {
  if (completed?.includes(stage)) return "done";
  if (active === stage) return "active";
  return "pending";
}

export default function PipelineViewer({
  activeStage,
  completedStages = [],
}: Props) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
      <h2 className="mb-4 text-base font-semibold text-zinc-900 dark:text-zinc-50">
        Pipeline Progress
      </h2>
      <ol className="space-y-3">
        {PIPELINE_STAGES.map((stage, idx) => {
          const status = getStatus(stage, activeStage, completedStages);
          return (
            <motion.li
              key={stage}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="flex items-center gap-3"
            >
              {status === "done" && (
                <CheckCircle className="h-4 w-4 shrink-0 text-emerald-500" />
              )}
              {status === "active" && (
                <Loader2 className="h-4 w-4 shrink-0 animate-spin text-violet-500" />
              )}
              {status === "pending" && (
                <Circle className="h-4 w-4 shrink-0 text-zinc-300 dark:text-zinc-600" />
              )}
              <span
                className={
                  status === "active"
                    ? "text-sm font-medium text-zinc-900 dark:text-zinc-50"
                    : status === "done"
                      ? "text-sm text-zinc-500 line-through dark:text-zinc-500"
                      : "text-sm text-zinc-400 dark:text-zinc-600"
                }
              >
                {stage}
              </span>
            </motion.li>
          );
        })}
      </ol>
    </div>
  );
}
