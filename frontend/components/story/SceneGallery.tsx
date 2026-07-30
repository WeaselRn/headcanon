import Image from "next/image";
import type { Scene } from "@/types/scene";

interface Props {
  scenes: Scene[];
}

export default function SceneGallery({ scenes }: Props) {
  if (scenes.length === 0) {
    return (
      <p className="text-sm text-zinc-500 dark:text-zinc-400">No scenes yet.</p>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {scenes.map((scene) => (
        <div
          key={scene.scene_number}
          className="overflow-hidden rounded-lg border border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900"
        >
          <div className="relative h-48 w-full bg-zinc-100 dark:bg-zinc-800">
            <Image
              src={scene.image_url || "/placeholder.png"}
              alt={scene.title}
              fill
              className="object-cover"
            />
          </div>
          <div className="p-3">
            <p className="text-xs font-medium text-zinc-500 dark:text-zinc-400">
              Scene {scene.scene_number}
            </p>
            <p className="mt-0.5 text-sm font-semibold text-zinc-900 dark:text-zinc-50">
              {scene.title}
            </p>
            {scene.description && (
              <p className="mt-1 text-xs text-zinc-600 line-clamp-2 dark:text-zinc-400">
                {scene.description}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
