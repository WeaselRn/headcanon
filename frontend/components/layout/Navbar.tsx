import Link from "next/link";
import { BookOpen } from "lucide-react";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-zinc-200 bg-white/80 backdrop-blur-md dark:border-zinc-800 dark:bg-zinc-950/80">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
        <Link
          href="/"
          className="flex items-center gap-2 font-semibold text-zinc-900 dark:text-zinc-50"
        >
          <BookOpen className="h-5 w-5" />
          <span>Headcanon</span>
        </Link>

        <nav className="flex items-center gap-6 text-sm font-medium text-zinc-600 dark:text-zinc-400">
          <Link
            href="/stories"
            className="transition-colors hover:text-zinc-900 dark:hover:text-zinc-50"
          >
            Library
          </Link>
          <Link
            href="/generate"
            className="rounded-full bg-zinc-900 px-4 py-1.5 text-white transition-colors hover:bg-zinc-700 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200"
          >
            Create Story
          </Link>
        </nav>
      </div>
    </header>
  );
}
