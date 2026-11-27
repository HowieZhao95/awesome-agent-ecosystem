// biome-ignore-all lint/suspicious/noArrayIndexKey: Generated table columns and rows have a fixed order.
"use client";

import { ArrowRight, Layers2, ListChecks } from "lucide-react";
import { useId, useRef, useState } from "react";
import { cn } from "./class-names";
import { FlashcardTemplate } from "./flashcard-template";
import { useTemplateHost } from "./host";
import { QuizTemplate } from "./quiz-template";
import type {
  Chapter,
  InteractiveReport,
  ResolveAsset,
  StudyMemory,
} from "./types";

export function ReportSectionBody({ section }: { section: Chapter }) {
  return (
    <div className="min-w-0 space-y-5">
      <p className="max-w-[65ch] whitespace-pre-line break-words text-[0.975rem] leading-[1.85]">
        {section.body}
      </p>
      {section.table && (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left text-sm leading-relaxed">
            <caption className="sr-only">{section.title}</caption>
            <thead>
              <tr className="border-surface-divider border-y bg-muted/40">
                {section.table.headers.map((header, i) => (
                  <th className="px-3 py-2.5 font-medium" key={i} scope="col">
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {section.table.rows.map((row, r) => (
                <tr
                  className="border-surface-divider border-b align-top"
                  key={r}
                >
                  {row.map((cell, c) => (
                    <td className="px-3 py-3" key={c}>
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export function InteractiveReportTemplate({
  output,
  memory,
  resolveAsset,
}: {
  output: InteractiveReport;
  memory: StudyMemory;
  resolveAsset: ResolveAsset;
}) {
  const { t, Button, LearningSelect } = useTemplateHost();
  const id = useId();
  const heading = useRef<HTMLHeadingElement>(null);
  const [index, setIndex] = useState(0);
  const labels = [
    ...output.sections.map((section) => section.title),
    ...output.embeds.map((activity) => activity.title),
  ];
  const chapter = output.sections[index];
  const embed = output.embeds[index - output.sections.length];

  function select(next: number) {
    setIndex(next);
    requestAnimationFrame(() => heading.current?.focus());
  }

  return (
    <div className="@container" data-template="interactive-report">
      <div className="grid @2xl:grid-cols-[10rem_minmax(0,1fr)] items-start @2xl:gap-10 gap-6">
        <nav aria-label={t("detail.contents")} className="min-w-0">
          <div className="relative @2xl:hidden">
            <label
              className="mb-1.5 block font-medium text-muted-foreground text-xs"
              htmlFor={`${id}select`}
            >
              {t("detail.contents")}
            </label>
            <LearningSelect
              id={`${id}select`}
              label={t("detail.contents")}
              lang={output.language}
              onValueChange={(value) => setIndex(Number(value))}
              options={labels.map((label, n) => ({ label, value: String(n) }))}
              value={String(index)}
            />
          </div>
          <div className="@2xl:block hidden">
            <p className="mb-3 font-medium text-muted-foreground text-xs">
              {t("detail.contents")}
            </p>
            <ol className="space-y-0.5">
              {labels.map((label, n) => {
                const item = output.embeds[n - output.sections.length];
                const Icon = item?.module === "quiz" ? ListChecks : Layers2;
                return (
                  <li key={n}>
                    {n === output.sections.length && (
                      <p className="mt-6 mb-2 font-medium text-muted-foreground text-xs">
                        {t("detail.practice")}
                      </p>
                    )}
                    <button
                      aria-controls={`${id}page`}
                      aria-current={n === index ? "page" : undefined}
                      aria-label={label}
                      className={cn(
                        "flex min-h-10 w-full items-start gap-2 rounded-lg px-2 py-2.5 text-left text-sm leading-snug focus-visible:outline-ring",
                        n === index
                          ? "bg-primary/[0.075] font-semibold text-primary"
                          : "text-muted-foreground hover:bg-muted/60 hover:text-foreground"
                      )}
                      lang={output.language}
                      onClick={() => select(n)}
                      type="button"
                    >
                      {item ? (
                        <Icon
                          aria-hidden="true"
                          className="mt-0.5 size-3.5 shrink-0"
                        />
                      ) : (
                        <span
                          aria-hidden="true"
                          className="w-4 shrink-0 text-xs tabular-nums opacity-75"
                        >
                          {n + 1}
                        </span>
                      )}
                      <span className="break-words">{label}</span>
                    </button>
                  </li>
                );
              })}
            </ol>
          </div>
        </nav>
        <section
          aria-labelledby={`${id}heading`}
          className="min-w-0"
          id={`${id}page`}
        >
          <h3
            className="mb-4 break-words font-serif @2xl:text-[1.8rem] text-2xl leading-tight tracking-tight outline-none"
            id={`${id}heading`}
            lang={output.language}
            ref={heading}
            tabIndex={-1}
          >
            {labels[index]}
          </h3>
          {chapter && (
            <div lang={output.language}>
              <ReportSectionBody section={chapter} />
            </div>
          )}
          {embed?.module === "flashcards" && (
            <FlashcardTemplate
              key={embed.id}
              memory={memory}
              output={embed}
              resolveAsset={resolveAsset}
            />
          )}
          {embed?.module === "quiz" && (
            <QuizTemplate
              key={embed.id}
              memory={memory}
              output={embed}
              resolveAsset={resolveAsset}
            />
          )}
          {chapter && index + 1 < labels.length && (
            <div className="mt-7 flex justify-end">
              <Button
                className="h-auto min-h-11 max-w-full whitespace-normal rounded-xl text-right"
                onClick={() => select(index + 1)}
                type="button"
                variant="ghost"
              >
                {labels[index + 1]}
                <ArrowRight aria-hidden="true" />
              </Button>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
