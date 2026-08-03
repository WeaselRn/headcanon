"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Import, FileText, Upload, Globe, Loader2, Sparkles } from "lucide-react";
import { importUniverse } from "@/lib/api";

export default function ImportPage() {
  const router = useRouter();
  const [sourceType, setSourceType] = useState<"text" | "pdf" | "epub" | "web">("text");
  const [textInput, setTextInput] = useState("");
  const [filePath, setFilePath] = useState("");
  const [urlInput, setUrlInput] = useState("");
  const [title, setTitle] = useState("");
  const [author, setAuthor] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await importUniverse({
        source_type: sourceType,
        text: sourceType === "text" ? textInput : undefined,
        file_path: sourceType === "pdf" || sourceType === "epub" ? filePath : undefined,
        url: sourceType === "web" ? urlInput : undefined,
        title: title.trim() || undefined,
        author: author.trim() || undefined,
      });

      router.push(`/universe/${res.universe_id}`);
    } catch (err: any) {
      console.error("Import failed:", err);
      setError(err?.response?.data?.detail || err.message || "Failed to import story.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-1 flex-col items-center justify-center p-6 lg:p-12 bg-slate-950 text-slate-100">
      <div className="w-full max-w-2xl rounded-2xl border border-slate-800 bg-slate-900/90 p-8 shadow-2xl backdrop-blur-md">
        <div className="flex items-center gap-3 border-b border-slate-800 pb-4 mb-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-950 text-purple-400 border border-purple-800/50">
            <Import className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-100">Import Story & Reconstruct Universe</h1>
            <p className="text-xs text-slate-400">
              Compile raw story sources into a persistent, living Headcanon universe.
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-6 rounded-lg bg-red-950/80 border border-red-800 p-3 text-xs text-red-200">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-6">
          {/* Source Type Selector */}
          <div className="flex flex-col gap-2">
            <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Source Format
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <button
                type="button"
                onClick={() => setSourceType("text")}
                className={`flex items-center justify-center gap-2 rounded-lg border py-2.5 px-3 text-xs font-semibold transition-colors ${
                  sourceType === "text"
                    ? "border-purple-500 bg-purple-950/60 text-purple-200"
                    : "border-slate-800 bg-slate-950 text-slate-400 hover:text-slate-200"
                }`}
              >
                <FileText className="h-4 w-4" /> Plain Text
              </button>

              <button
                type="button"
                onClick={() => setSourceType("pdf")}
                className={`flex items-center justify-center gap-2 rounded-lg border py-2.5 px-3 text-xs font-semibold transition-colors ${
                  sourceType === "pdf"
                    ? "border-purple-500 bg-purple-950/60 text-purple-200"
                    : "border-slate-800 bg-slate-950 text-slate-400 hover:text-slate-200"
                }`}
              >
                <Upload className="h-4 w-4" /> PDF Document
              </button>

              <button
                type="button"
                onClick={() => setSourceType("epub")}
                className={`flex items-center justify-center gap-2 rounded-lg border py-2.5 px-3 text-xs font-semibold transition-colors ${
                  sourceType === "epub"
                    ? "border-purple-500 bg-purple-950/60 text-purple-200"
                    : "border-slate-800 bg-slate-950 text-slate-400 hover:text-slate-200"
                }`}
              >
                <Upload className="h-4 w-4" /> EPUB eBook
              </button>

              <button
                type="button"
                onClick={() => setSourceType("web")}
                className={`flex items-center justify-center gap-2 rounded-lg border py-2.5 px-3 text-xs font-semibold transition-colors ${
                  sourceType === "web"
                    ? "border-purple-500 bg-purple-950/60 text-purple-200"
                    : "border-slate-800 bg-slate-950 text-slate-400 hover:text-slate-200"
                }`}
              >
                <Globe className="h-4 w-4" /> Web URL
              </button>
            </div>
          </div>

          {/* Dynamic Content Inputs */}
          {sourceType === "text" && (
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Story Text Content
              </label>
              <textarea
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="Paste story chapters or raw plain text here..."
                rows={8}
                required
                className="w-full rounded-xl border border-slate-700 bg-slate-950 p-4 text-sm text-slate-100 placeholder-slate-500 focus:border-purple-500 focus:outline-none"
              />
            </div>
          )}

          {(sourceType === "pdf" || sourceType === "epub") && (
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                File Path
              </label>
              <input
                type="text"
                value={filePath}
                onChange={(e) => setFilePath(e.target.value)}
                placeholder={`Enter absolute path to .${sourceType} file...`}
                required
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:border-purple-500 focus:outline-none"
              />
            </div>
          )}

          {sourceType === "web" && (
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Story Web Page URL
              </label>
              <input
                type="url"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="https://archiveofourown.org/works/... or Project Gutenberg URL"
                required
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:border-purple-500 focus:outline-none"
              />
            </div>
          )}

          {/* Title & Author Overrides */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Story Title (Optional)
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Harry Potter and the Philosopher's Stone"
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:border-purple-500 focus:outline-none"
              />
            </div>

            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Author Name (Optional)
              </label>
              <input
                type="text"
                value={author}
                onChange={(e) => setAuthor(e.target.value)}
                placeholder="e.g. J. K. Rowling"
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:border-purple-500 focus:outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-2 inline-flex items-center justify-center gap-2 rounded-xl bg-purple-600 px-6 py-3.5 text-sm font-semibold text-white hover:bg-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-colors shadow-xl disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Compiling Universe Pipeline...
              </>
            ) : (
              <>
                <Sparkles className="h-5 w-5 text-amber-400" />
                Reconstruct Universe
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
