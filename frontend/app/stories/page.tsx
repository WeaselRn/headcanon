import type { StoryCard } from "@/types/story";
import StoryCardComponent from "@/components/story/StoryCard";

export const metadata = {
  title: "Story Library — Headcanon",
  description: "Browse all of your saved stories.",
};

const PLACEHOLDER_STORIES: StoryCard[] = [];

export default function StoriesPage() {
  const stories = PLACEHOLDER_STORIES;

  return (
    <div className="mx-auto w-full max-w-6xl px-4 py-12">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-50">
          Story Library
        </h1>
      </div>

      {stories.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-zinc-300 py-24 text-center dark:border-zinc-700">
          <p className="text-zinc-500 dark:text-zinc-400">No stories yet.</p>
          <a
            href="/generate"
            className="mt-4 text-sm font-medium text-violet-600 hover:underline dark:text-violet-400"
          >
            Create your first story →
          </a>
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {stories.map((s) => (
            <StoryCardComponent key={s.story_id} story={s} />
          ))}
        </div>
      )}
    </div>
  );
}
