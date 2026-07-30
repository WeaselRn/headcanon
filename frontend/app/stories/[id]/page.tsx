import Link from "next/link";

export const metadata = {
  title: "Story — Headcanon",
  description: "View a story.",
};

interface Props {
  params: Promise<{ id: string }>;
}

export default async function StoryDetailPage({ params }: Props) {
  const { id } = await params;

  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-12">
      <p className="mb-4 text-sm text-zinc-500 dark:text-zinc-400">
        Story ID: <span className="font-mono">{id}</span>
      </p>
      <p className="text-zinc-600 dark:text-zinc-400">
        Story viewer will appear here once API integration is complete.
      </p>
      <Link
        href="/stories"
        className="mt-6 inline-block text-sm text-violet-600 hover:underline dark:text-violet-400"
      >
        ← Back to Library
      </Link>
    </div>
  );
}
