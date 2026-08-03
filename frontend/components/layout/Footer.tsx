import Link from "next/link";
import { Compass } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-slate-800 bg-slate-950">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6 text-xs text-slate-400">
        <div className="flex items-center gap-2 font-semibold text-slate-300">
          <Compass className="h-4 w-4 text-purple-400" />
          <span>Headcanon Engine</span>
        </div>
        <div className="flex items-center gap-6">
          <Link href="/library" className="hover:text-purple-300 transition-colors">
            Media Library
          </Link>
          <Link href="/settings" className="hover:text-purple-300 transition-colors">
            Settings
          </Link>
          <Link href="/import" className="hover:text-purple-300 transition-colors">
            Import Story
          </Link>
        </div>
      </div>
    </footer>
  );
}
