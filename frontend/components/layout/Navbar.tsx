import Link from "next/link";
import { Compass, Plus, Image as ImageIcon, Settings } from "lucide-react";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-6">
        <Link
          href="/"
          className="flex items-center gap-2 text-base font-bold text-slate-50 hover:text-purple-300 transition-colors"
        >
          <Compass className="h-5 w-5 text-purple-400" />
          <span>Headcanon</span>
        </Link>

        <nav className="flex items-center gap-6 text-xs font-semibold text-slate-300">
          <Link
            href="/library"
            className="flex items-center gap-1.5 transition-colors hover:text-purple-300"
          >
            <ImageIcon className="h-4 w-4 text-amber-400" />
            Media Library
          </Link>

          <Link
            href="/settings"
            className="flex items-center gap-1.5 transition-colors hover:text-purple-300"
          >
            <Settings className="h-4 w-4 text-slate-400" />
            Settings
          </Link>

          <Link
            href="/import"
            className="flex items-center gap-1.5 rounded-xl bg-purple-600 px-3.5 py-1.5 font-semibold text-white transition-colors hover:bg-purple-500 shadow-md"
          >
            <Plus className="h-4 w-4" />
            Import Universe
          </Link>
        </nav>
      </div>
    </header>
  );
}
