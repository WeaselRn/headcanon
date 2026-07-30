import Link from "next/link";
import { BookOpen } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-6 text-sm text-zinc-500 dark:text-zinc-400">
        <div className="flex items-center gap-2">
          <BookOpen className="h-4 w-4" />
          <span>Headcanon</span>
        </div>
        <div className="flex items-center gap-6">
          <Link href="/stories" className="hover:text-zinc-900 dark:hover:text-zinc-50">
            Library
          </Link>
          <Link href="/generate" className="hover:text-zinc-900 dark:hover:text-zinc-50">
            Create
          </Link>
        </div>
      </div>
    </footer>
  );
}
