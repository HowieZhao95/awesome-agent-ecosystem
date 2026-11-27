"use client";

import { useTemplateHost } from "./host";

export function StudyProgress({
  current,
  total,
}: {
  current: number;
  total: number;
}) {
  const { t } = useTemplateHost();
  const label = t("viewer.position", { current, total });
  return (
    <div className="flex min-w-0 flex-1 items-center gap-3">
      <span
        aria-hidden="true"
        className="shrink-0 font-medium text-xs tabular-nums"
      >
        {current} <span className="px-0.5 text-muted-foreground">/</span>{" "}
        {total}
      </span>
      <progress
        aria-label={label}
        className="h-1 max-w-44 flex-1 appearance-none overflow-hidden rounded-full bg-muted text-primary [&::-moz-progress-bar]:bg-primary [&::-webkit-progress-bar]:bg-muted [&::-webkit-progress-value]:rounded-full [&::-webkit-progress-value]:bg-primary"
        max={total}
        value={current}
      />
    </div>
  );
}
