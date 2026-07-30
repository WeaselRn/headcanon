import Link from "next/link";

export const metadata = {
  title: "Page Not Found — Headcanon",
};

export default function NotFound() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-4 py-24 text-center">
      <p className="text-6xl font-bold text-zinc-200 dark:text-zinc-800">404</p>
      <h2 className="mt-4 text-xl font-semibold text-zinc-900 dark:text-zinc-50">
        Page not found
      </h2>
      <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
        The page you&apos;re looking for doesn&apos;t exist.
      </p>
      <Link
        href="/"
        className="mt-6 rounded-full bg-violet-600 px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-violet-700"
      >
        Go Home
      </Link>
    </div>
  );
}
