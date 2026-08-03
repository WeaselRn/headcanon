"use client";

import React, { useEffect } from "react";
import { useParams } from "next/navigation";
import { useHeadcanon } from "@/lib/store";
import SceneView from "@/components/scene/SceneView";
import ErrorBoundary from "@/components/ui/ErrorBoundary";

export default function ExplorePage() {
  const params = useParams();
  const universeId = params?.id as string;
  const { loadUniverse } = useHeadcanon();

  useEffect(() => {
    if (universeId) {
      loadUniverse(universeId);
    }
  }, [universeId, loadUniverse]);

  return (
    <ErrorBoundary>
      <SceneView />
    </ErrorBoundary>
  );
}
