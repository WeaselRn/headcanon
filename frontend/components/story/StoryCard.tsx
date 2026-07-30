import Image from "next/image";
import Link from "next/link";
import type { StoryCard as StoryCardType } from "@/types/story";

interface Props {
  story: StoryCardType;
}

export default function StoryCard({ story }: Props) {
  return (
    <Link
      href={`/stories/${story.story_id}`}
      className="group flex flex-col overflow-hidden rounded-xl border border-zinc-200 bg-white shadow-sm transition-shadow hover:shadow-md dark:border-zinc-800 dark:bg-zinc-900"
    >
      <div className="relative h-48 w-full overflow-hidden bg-zinc-100 dark:bg-zinc-800">
        <Image
          src={story.thumbnail || "/placeholder.png"}
          alt={story.title}
          fill
          className="object-cover transition-transform duration-300 group-hover:scale-105"
        />
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-zinc-900 line-clamp-2 dark:text-zinc-50">
          {story.title}
        </h3>
      </div>
    </Link>
  );
}
