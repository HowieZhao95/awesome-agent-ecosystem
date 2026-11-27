"use client";

import {
  ArrowLeft,
  ArrowRight,
  Check,
  CheckCheck,
  Ellipsis,
  Layers2,
  RotateCcw,
  RotateCw,
  Shuffle,
} from "lucide-react";
import { useId, useRef, useState } from "react";
import { useTemplateHost } from "./host";
import { StudyProgress } from "./study-progress";
import type {
  FlashcardProgress,
  Flashcards,
  ResolveAsset,
  StudyMemory,
} from "./types";

export function FlashcardTemplate({
  output,
  memory,
  resolveAsset,
}: {
  output: Flashcards;
  memory: StudyMemory;
  resolveAsset: ResolveAsset;
}) {
  const {
    t,
    Button,
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
    StudyImage,
  } = useTemplateHost();
  const cardTextId = useId();
  const flipButton = useRef<HTMLButtonElement>(null);
  const completeHeading = useRef<HTMLHeadingElement>(null);
  const all = output.cards.map((_, position) => position);
  const initial = {
    order: all,
    index: 0,
    flipped: false,
    marks: {},
    reviewed: [],
    finished: false,
  };
  const [progress, setProgress] = useState<FlashcardProgress>(
    () => memory.cards.get(output.id) ?? initial
  );
  const { order, index, flipped, marks } = progress;
  const card = output.cards[order[index]];
  const missed = all.filter(
    (position) => marks[output.cards[position].id] === false
  );
  const known = Object.values(marks).filter(Boolean).length;
  const score = t("study.cardProgress", { known, missed: missed.length });

  function update(next: FlashcardProgress) {
    memory.cards.set(output.id, next);
    setProgress(next);
  }
  function focusCard() {
    requestAnimationFrame(() =>
      (flipButton.current ?? completeHeading.current)?.focus({
        preventScroll: true,
      })
    );
  }
  function move(next: number) {
    update({ ...progress, index: next, flipped: false });
  }
  function mark(understood: boolean) {
    const reviewed = new Set(progress.reviewed);
    reviewed.add(card.id);
    const unreviewed = (position: number) =>
      !reviewed.has(output.cards[position].id);
    let nextIndex = order.findIndex(
      (position, offset) => offset > index && unreviewed(position)
    );
    if (nextIndex < 0) {
      nextIndex = order.findIndex(unreviewed);
    }
    update({
      ...progress,
      marks: { ...marks, [card.id]: understood },
      reviewed: [...reviewed],
      index: nextIndex < 0 ? index : nextIndex,
      finished: nextIndex < 0,
      flipped: false,
    });
    focusCard();
  }
  function reviewMissed() {
    update({ ...initial, order: missed, marks });
    focusCard();
  }
  function restart() {
    update(initial);
    focusCard();
  }
  function shuffle() {
    const next = [...order];
    for (let cursor = next.length - 1; cursor > 0; cursor--) {
      const target = Math.floor(Math.random() * (cursor + 1));
      [next[cursor], next[target]] = [next[target], next[cursor]];
    }
    update({ ...progress, order: next, index: 0, flipped: false });
  }

  if (progress.finished) {
    return (
      <section
        className="space-y-5 py-8 text-center"
        data-template="flashcards"
      >
        <CheckCheck
          aria-hidden="true"
          className="mx-auto size-8 text-primary"
        />
        <h3
          className="font-serif text-3xl outline-none"
          ref={completeHeading}
          tabIndex={-1}
        >
          {t("detail.roundComplete")}
        </h3>
        <p aria-live="polite" className="text-muted-foreground text-sm">
          {score}
        </p>
        <div className="flex flex-wrap justify-center gap-2">
          {missed.length > 0 && (
            <Button
              className="min-h-11 rounded-xl"
              onClick={reviewMissed}
              type="button"
            >
              {t("study.reviewMissed")}
            </Button>
          )}
          <Button
            className="min-h-11 rounded-xl"
            onClick={restart}
            type="button"
            variant="outline"
          >
            {t("study.restart")}
          </Button>
        </div>
      </section>
    );
  }

  return (
    <section
      className="@container min-w-0 space-y-3"
      data-template="flashcards"
    >
      <div className="flex items-center gap-4">
        <StudyProgress current={index + 1} total={order.length} />
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              aria-label={t("detail.practiceOptions")}
              className="size-11 rounded-xl"
              size="icon"
              type="button"
              variant="ghost"
            >
              <Ellipsis aria-hidden="true" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem disabled={order.length < 2} onSelect={shuffle}>
              <Shuffle />
              {t("study.shuffle")}
            </DropdownMenuItem>
            <DropdownMenuItem disabled={!missed.length} onSelect={reviewMissed}>
              <Layers2 />
              {t("study.reviewMissed")}
            </DropdownMenuItem>
            <DropdownMenuItem onSelect={restart}>
              <RotateCcw />
              {t("study.restart")}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      <article className="relative flex @md:min-h-72 min-h-64 flex-col justify-center rounded-2xl border border-border bg-card bg-linear-to-br from-primary/[0.045] to-transparent @md:px-10 px-6 py-16 shadow-xs">
        <span className="absolute top-5 @md:left-10 left-6 flex items-center gap-2 text-muted-foreground text-xs">
          <Layers2 aria-hidden="true" className="size-4 text-primary" />
          {t(flipped ? "study.answer" : "study.question")}
        </span>
        <div
          aria-live="polite"
          className="flex min-w-0 flex-wrap items-center gap-x-6 gap-y-4"
          id={cardTextId}
          lang={output.language}
        >
          <div className="min-w-36 flex-1 space-y-3">
            <p className="break-words font-serif @md:text-3xl text-[1.55rem] leading-snug tracking-tight">
              {flipped ? card.back : card.front}
            </p>
            {flipped && card.explanation && card.explanation !== card.back && (
              <p className="max-w-prose whitespace-pre-line text-muted-foreground text-sm leading-relaxed">
                {card.explanation}
              </p>
            )}
          </div>
          {card.image && (
            <StudyImage
              className="m-0 h-auto max-h-28 @md:w-36 w-28 shrink-0 rounded-lg"
              image={card.image}
              resolveAsset={resolveAsset}
            />
          )}
        </div>
        <button
          aria-describedby={cardTextId}
          aria-label={t(flipped ? "study.showQuestion" : "study.showAnswer")}
          aria-pressed={flipped}
          className="group absolute inset-0 cursor-pointer rounded-2xl text-left outline-none focus-visible:ring-2 focus-visible:ring-ring"
          onClick={() => update({ ...progress, flipped: !flipped })}
          ref={flipButton}
          type="button"
        >
          <span className="absolute bottom-5 @md:left-10 left-6 flex items-center gap-2 font-medium text-primary text-sm group-hover:underline">
            <RotateCw aria-hidden="true" className="size-4" />
            {t(flipped ? "study.showQuestion" : "study.showAnswer")}
          </span>
        </button>
      </article>
      <div className="flex min-h-12 items-center justify-between gap-1">
        <Button
          aria-label={t("detail.previousCard")}
          className="size-11 rounded-xl"
          disabled={index === 0}
          onClick={() => move(index - 1)}
          size="icon"
          type="button"
          variant="ghost"
        >
          <ArrowLeft />
        </Button>
        {flipped ? (
          <div className="flex flex-wrap justify-center gap-2">
            <Button
              className="min-h-11 rounded-xl"
              onClick={() => mark(false)}
              type="button"
              variant="outline"
            >
              <RotateCcw />
              {t("study.missed")}
            </Button>
            <Button
              className="min-h-11 rounded-xl"
              onClick={() => mark(true)}
              type="button"
            >
              <Check />
              {t("study.known")}
            </Button>
          </div>
        ) : (
          <p
            aria-live="polite"
            className="text-center text-muted-foreground text-xs"
          >
            {score}
          </p>
        )}
        <Button
          aria-label={t("detail.nextCard")}
          className="size-11 rounded-xl"
          disabled={index === order.length - 1}
          onClick={() => move(index + 1)}
          size="icon"
          type="button"
          variant="ghost"
        >
          <ArrowRight />
        </Button>
      </div>
    </section>
  );
}
