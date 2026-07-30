import Link from "next/link";
import { BookOpen, Sparkles } from "lucide-react";

export default function HomePage() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-4 py-24 text-center">
      <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-violet-200 bg-violet-50 px-4 py-1.5 text-sm font-medium text-violet-700 dark:border-violet-800 dark:bg-violet-950 dark:text-violet-300">
        <Sparkles className="h-3.5 w-3.5" />
        Powered by Gemini
      </div>

      <h1 className="max-w-2xl text-4xl font-bold tracking-tight text-zinc-900 sm:text-6xl dark:text-zinc-50">
        Your story,{" "}
        <span className="text-violet-600 dark:text-violet-400">any universe</span>
      </h1>

      <p className="mt-6 max-w-xl text-lg leading-8 text-zinc-600 dark:text-zinc-400">
        Choose a universe, a character, a mood, and a prompt. Headcanon
        generates a personalised multimedia chapter — complete with storyboard
        images, narration, and ambience.
      </p>

      <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
        <Link
          href="/generate"
          className="inline-flex items-center gap-2 rounded-full bg-violet-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-violet-500"
        >
          <BookOpen className="h-4 w-4" />
          Create Your Story
        </Link>
        <Link
          href="/stories"
          className="rounded-full border border-zinc-300 px-6 py-3 text-sm font-semibold text-zinc-700 transition-colors hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
        >
          Browse Library
        </Link>
      </div>
    </div>
  );
}
