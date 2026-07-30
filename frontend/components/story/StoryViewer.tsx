import type { Story } from "@/types/story";
import { formatDate } from "@/lib/utils";
import SceneGallery from "./SceneGallery";

interface Props {
  story: Story;
}

export default function StoryViewer({ story }: Props) {
  return (
    <article className="mx-auto max-w-3xl space-y-8 py-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50">
          {story.title}
        </h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">
          {story.universe} &middot; {story.character_name} &middot;{" "}
          {story.mood} &middot;{" "}
          {formatDate(story.metadata.created_at)}
        </p>
      </header>

      <section>
        <div className="prose prose-zinc max-w-none dark:prose-invert">
          <p className="whitespace-pre-wrap leading-8 text-zinc-700 dark:text-zinc-300">
            {story.story}
          </p>
        </div>
      </section>

      <section>
        <h2 className="mb-4 text-xl font-semibold text-zinc-900 dark:text-zinc-50">
          Scenes
        </h2>
        <SceneGallery scenes={story.scenes} />
      </section>
    </article>
  );
}
