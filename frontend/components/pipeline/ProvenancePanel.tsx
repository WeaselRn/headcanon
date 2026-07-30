import type { Provenance } from "@/types/metadata";
import { formatDate } from "@/lib/utils";

interface Props {
  provenance: Provenance;
}

export default function ProvenancePanel({ provenance }: Props) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
      <h2 className="mb-4 text-base font-semibold text-zinc-900 dark:text-zinc-50">
        Provenance
      </h2>
      <dl className="space-y-2 text-sm">
        <div className="flex justify-between">
          <dt className="text-zinc-500 dark:text-zinc-400">Execution ID</dt>
          <dd className="font-mono text-xs text-zinc-700 dark:text-zinc-300">
            {provenance.execution_id}
          </dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-zinc-500 dark:text-zinc-400">Pipeline</dt>
          <dd className="text-zinc-700 dark:text-zinc-300">
            {provenance.pipeline_version}
          </dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-zinc-500 dark:text-zinc-400">Started</dt>
          <dd className="text-zinc-700 dark:text-zinc-300">
            {formatDate(provenance.started_at)}
          </dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-zinc-500 dark:text-zinc-400">Completed</dt>
          <dd className="text-zinc-700 dark:text-zinc-300">
            {formatDate(provenance.completed_at)}
          </dd>
        </div>
        <div>
          <dt className="mb-1 text-zinc-500 dark:text-zinc-400">Models</dt>
          <dd className="flex flex-wrap gap-1">
            {provenance.models_used.map((m) => (
              <span
                key={m}
                className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"
              >
                {m}
              </span>
            ))}
          </dd>
        </div>
        <div>
          <dt className="mb-1 text-zinc-500 dark:text-zinc-400">Assets</dt>
          <dd className="flex flex-wrap gap-1">
            {provenance.assets_generated.map((a) => (
              <span
                key={a}
                className="rounded-full bg-zinc-100 px-2 py-0.5 font-mono text-xs text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300"
              >
                {a}
              </span>
            ))}
          </dd>
        </div>
      </dl>
    </div>
  );
}
