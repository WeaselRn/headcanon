import StoryForm from "@/components/forms/StoryForm";

export const metadata = {
  title: "Create Story — Headcanon",
  description: "Fill in the form to generate your personalised story.",
};

export default function GeneratePage() {
  return (
    <div className="mx-auto w-full max-w-xl px-4 py-12">
      <h1 className="mb-2 text-2xl font-bold text-zinc-900 dark:text-zinc-50">
        Create Your Story
      </h1>
      <p className="mb-8 text-sm text-zinc-500 dark:text-zinc-400">
        Choose a universe and shape your adventure.
      </p>
      <StoryForm />
    </div>
  );
}
