import Image from "next/image";
import type { Scene } from "@/types/scene";

interface Props {
  scenes: Scene[];
}

export default function SceneGallery({ scenes }: Props) {
  if (scenes.length === 0) {
    return (
      <p className="text-sm text-slate-500">No scenes yet.</p>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {scenes.map((scene, idx) => (
        <div
          key={scene.scene_id || idx}
          className="overflow-hidden rounded-lg border border-slate-800 bg-slate-900"
        >
          <div className="relative h-48 w-full bg-slate-950">
            <Image
              src={scene.media?.illustration_url || "/placeholder.png"}
              alt={scene.location?.name || "Scene"}
              fill
              className="object-cover"
            />
          </div>
          <div className="p-3">
            <p className="text-xs font-medium text-slate-400">
              {scene.location?.name || `Scene ${idx + 1}`}
            </p>
            <p className="mt-1 text-xs text-slate-300 line-clamp-2">
              {scene.narration}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
