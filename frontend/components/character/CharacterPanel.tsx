"use client";

import React from "react";
import { Users } from "lucide-react";
import type { SceneCharacterSummary } from "@/types/scene";
import CharacterCard from "./CharacterCard";

interface CharacterPanelProps {
  characters: SceneCharacterSummary[];
  selectedCharacterId?: string | null;
  onSelectCharacter?: (characterId: string) => void;
  onTalkToCharacter?: (characterName: string) => void;
}

export default function CharacterPanel({
  characters,
  selectedCharacterId,
  onSelectCharacter,
  onTalkToCharacter,
}: CharacterPanelProps) {
  if (!characters || characters.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-6 text-center border border-dashed border-slate-800 rounded-xl bg-slate-900/30">
        <Users className="h-8 w-8 text-slate-600 mb-2" />
        <p className="text-xs text-slate-400">No other characters present in this location.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <Users className="h-3.5 w-3.5 text-purple-400" />
          Characters Present ({characters.length})
        </h3>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-3">
        {characters.map((char) => (
          <CharacterCard
            key={char.character_id}
            character={char}
            isSelected={selectedCharacterId === char.character_id}
            onSelect={() => onSelectCharacter?.(char.character_id)}
            onTalk={
              onTalkToCharacter ? () => onTalkToCharacter(char.name) : undefined
            }
          />
        ))}
      </div>
    </div>
  );
}
