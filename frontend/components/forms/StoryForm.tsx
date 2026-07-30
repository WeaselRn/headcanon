"use client";

import { useState } from "react";
import type { GenerationRequest } from "@/types/story";
import { STORY_MOODS } from "@/lib/constants";

const EMPTY: GenerationRequest = {
  universe: "",
  character_name: "",
  role: "",
  mood: "",
  prompt: "",
};

type Errors = Partial<Record<keyof GenerationRequest, string>>;

function validate(values: GenerationRequest): Errors {
  const errors: Errors = {};
  if (!values.universe.trim()) errors.universe = "Universe is required.";
  if (!values.character_name.trim())
    errors.character_name = "Character name is required.";
  if (!values.role.trim()) errors.role = "Role is required.";
  if (!values.mood) errors.mood = "Mood is required.";
  if (!values.prompt.trim()) errors.prompt = "Story prompt is required.";
  return errors;
}

export default function StoryForm() {
  const [values, setValues] = useState<GenerationRequest>(EMPTY);
  const [errors, setErrors] = useState<Errors>({});
  const [submitted, setSubmitted] = useState(false);

  function handleChange(
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) {
    const { name, value } = e.target;
    setValues((prev) => ({ ...prev, [name]: value }));
    if (errors[name as keyof GenerationRequest]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const errs = validate(values);
    if (Object.keys(errs).length > 0) {
      setErrors(errs);
      return;
    }
    setSubmitted(true);
  }

  if (submitted) {
    return (
      <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-6 text-center dark:border-emerald-800 dark:bg-emerald-950">
        <p className="font-medium text-emerald-700 dark:text-emerald-300">
          Story submitted! (API integration coming soon.)
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-6">
      <Field
        label="Universe"
        name="universe"
        type="text"
        placeholder="e.g. Harry Potter"
        value={values.universe}
        onChange={handleChange}
        error={errors.universe}
      />
      <Field
        label="Character Name"
        name="character_name"
        type="text"
        placeholder="e.g. Elias"
        value={values.character_name}
        onChange={handleChange}
        error={errors.character_name}
      />
      <Field
        label="Role"
        name="role"
        type="text"
        placeholder="e.g. Student"
        value={values.role}
        onChange={handleChange}
        error={errors.role}
      />

      <div className="flex flex-col gap-1">
        <label
          htmlFor="mood"
          className="text-sm font-medium text-zinc-700 dark:text-zinc-300"
        >
          Mood
        </label>
        <select
          id="mood"
          name="mood"
          value={values.mood}
          onChange={handleChange}
          className="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 focus:outline-none focus:ring-2 focus:ring-violet-500 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-50"
        >
          <option value="">Select a mood</option>
          {STORY_MOODS.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
        {errors.mood && (
          <p className="text-xs text-red-500">{errors.mood}</p>
        )}
      </div>

      <div className="flex flex-col gap-1">
        <label
          htmlFor="prompt"
          className="text-sm font-medium text-zinc-700 dark:text-zinc-300"
        >
          Story Prompt
        </label>
        <textarea
          id="prompt"
          name="prompt"
          rows={4}
          placeholder="The castle hides an ancient secret."
          value={values.prompt}
          onChange={handleChange}
          className="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 focus:outline-none focus:ring-2 focus:ring-violet-500 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-50"
        />
        {errors.prompt && (
          <p className="text-xs text-red-500">{errors.prompt}</p>
        )}
      </div>

      <button
        type="submit"
        className="w-full rounded-full bg-violet-600 px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-violet-500"
      >
        Generate Story
      </button>
    </form>
  );
}

interface FieldProps {
  label: string;
  name: string;
  type: string;
  placeholder: string;
  value: string;
  onChange: React.ChangeEventHandler<HTMLInputElement>;
  error?: string;
}

function Field({ label, name, type, placeholder, value, onChange, error }: FieldProps) {
  return (
    <div className="flex flex-col gap-1">
      <label
        htmlFor={name}
        className="text-sm font-medium text-zinc-700 dark:text-zinc-300"
      >
        {label}
      </label>
      <input
        id={name}
        name={name}
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        className="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 focus:outline-none focus:ring-2 focus:ring-violet-500 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-50"
      />
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}
