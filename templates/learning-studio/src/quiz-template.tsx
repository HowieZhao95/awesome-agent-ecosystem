// biome-ignore-all lint/suspicious/noArrayIndexKey: Answer choices retain their generated order.
"use client";

import {
  ArrowLeft,
  ArrowRight,
  Check,
  CheckCircle2,
  ChevronRight,
  Lightbulb,
  RotateCcw,
  X,
} from "lucide-react";
import { useId, useRef, useState } from "react";
import { cn } from "./class-names";
import { useTemplateHost } from "./host";
import { StudyProgress } from "./study-progress";
import type {
  Quiz,
  QuizAnswer,
  QuizProgress,
  ResolveAsset,
  StudyMemory,
} from "./types";

const blankAnswer: QuizAnswer = { choices: [], text: "" };
const newQuiz: QuizProgress = { index: 0, answers: {}, finished: false };
const spaces = /\s+/g;
function normalize(answer: string) {
  return answer.normalize("NFKC").trim().replace(spaces, " ").toLowerCase();
}

function AnswerField({
  id,
  language,
  question,
  answer,
  save,
}: {
  id: string;
  language: Quiz["language"];
  question: Quiz["questions"][number];
  answer: QuizAnswer;
  save: (value: QuizAnswer) => void;
}) {
  const { t, Label, Checkbox, RadioGroup, RadioGroupItem, Input, Textarea } =
    useTemplateHost();
  const checked = answer.result !== undefined;
  if ("options" in question) {
    const multiple = question.type === "multipleSelect";
    const choices = question.options.map((option, index) => {
      const selected = answer.choices.includes(index);
      const textId = `${id}-label-${index}`;
      return (
        <Label
          className={cn(
            "flex min-h-12 cursor-pointer items-center gap-3 rounded-xl border border-border-strong bg-card/55 px-4 py-3 font-normal text-sm leading-relaxed",
            !checked && "transition-colors hover:bg-muted/65",
            selected && "border-primary/45 bg-primary/[0.055]",
            checked && "cursor-default",
            checked && option.correct && "border-primary/55",
            checked && selected && !option.correct && "border-destructive/45"
          )}
          htmlFor={id + index}
          key={index}
        >
          {multiple ? (
            <Checkbox
              aria-labelledby={textId}
              checked={selected}
              disabled={checked}
              id={id + index}
              onCheckedChange={(value) =>
                save({
                  choices:
                    value === true
                      ? [...answer.choices, index]
                      : answer.choices.filter((choice) => choice !== index),
                  text: "",
                })
              }
            />
          ) : (
            <RadioGroupItem
              aria-labelledby={textId}
              disabled={checked}
              id={id + index}
              value={String(index)}
            />
          )}
          <span
            className="min-w-0 flex-1 break-words"
            id={textId}
            lang={language}
          >
            {option.label}
          </span>
          {checked && option.correct && (
            <Check
              aria-hidden="true"
              className="size-4 shrink-0 text-primary"
            />
          )}
          {checked && selected && !option.correct && (
            <X
              aria-hidden="true"
              className="size-4 shrink-0 text-destructive"
            />
          )}
        </Label>
      );
    });
    return multiple ? (
      <fieldset className="grid min-w-0 gap-2">
        <legend className="sr-only">{question.prompt}</legend>
        {choices}
      </fieldset>
    ) : (
      <RadioGroup
        aria-labelledby={`${id}question`}
        className="gap-2"
        disabled={checked}
        onValueChange={(value) => save({ choices: [Number(value)], text: "" })}
        value={answer.choices.length ? String(answer.choices[0]) : ""}
      >
        {choices}
      </RadioGroup>
    );
  }
  const field = {
    id: `${id}answer`,
    readOnly: checked,
    value: answer.text,
    onChange: (
      event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
    ) => save({ choices: [], text: event.target.value }),
  };
  return (
    <div className="space-y-2">
      <Label htmlFor={field.id}>{t("study.yourAnswer")}</Label>
      {question.type === "shortAnswer" ? (
        <Textarea {...field} className="min-h-24 rounded-xl" />
      ) : (
        <Input {...field} className="min-h-11 rounded-xl" />
      )}
    </div>
  );
}

export function QuizTemplate({
  output,
  resolveAsset,
  memory,
}: {
  output: Quiz;
  resolveAsset: ResolveAsset;
  memory: StudyMemory;
}) {
  const { t, Button, StudyImage } = useTemplateHost();
  const id = useId();
  const heading = useRef<HTMLHeadingElement>(null);
  const [progress, setProgress] = useState(
    () => memory.quizzes.get(output.id) ?? newQuiz
  );
  const [hintFor, setHintFor] = useState<string | null>(null);
  const { index, answers, finished } = progress;
  const question = output.questions[index];
  const answer = answers[question.id] ?? blankAnswer;
  const checked = answer.result !== undefined;
  const total = output.questions.length;
  const last = index === total - 1;

  function update(next: QuizProgress) {
    memory.quizzes.set(output.id, next);
    setProgress(next);
  }
  function navigate(next: QuizProgress) {
    update(next);
    setHintFor(null);
    requestAnimationFrame(() =>
      heading.current?.focus({ preventScroll: true })
    );
  }
  function save(next: QuizAnswer) {
    update({ ...progress, answers: { ...answers, [question.id]: next } });
  }
  function advance() {
    if (checked) {
      navigate(
        last
          ? { ...progress, finished: true }
          : { ...progress, index: index + 1 }
      );
      return;
    }
    const correct =
      "options" in question
        ? question.options.every(
            (option, i) => option.correct === answer.choices.includes(i)
          )
        : question.acceptedAnswers.some(
            (value) => normalize(value) === normalize(answer.text)
          );
    save({ ...answer, result: correct });
  }
  if (finished) {
    const correct = output.questions.filter(
      (item) => answers[item.id]?.result
    ).length;
    return (
      <section className="space-y-6" data-template="quiz">
        <h3
          className="font-serif text-3xl tracking-tight outline-none"
          ref={heading}
          tabIndex={-1}
        >
          {t("study.quizScore", { correct, total })}
        </h3>
        <div>
          <h4 className="border-surface-divider border-b pb-3 font-medium text-muted-foreground text-sm">
            {t("study.reviewAnswers")}
          </h4>
          <ul className="divide-y divide-surface-divider">
            {output.questions.map((item, position) => (
              <li key={item.id}>
                <button
                  aria-describedby={`${id}-result-${position}`}
                  aria-label={item.prompt}
                  className="flex min-h-12 w-full items-center gap-3 rounded-sm py-3 text-left text-sm hover:text-primary focus-visible:outline-ring"
                  onClick={() =>
                    navigate({ ...progress, index: position, finished: false })
                  }
                  type="button"
                >
                  {answers[item.id]?.result ? (
                    <CheckCircle2
                      aria-hidden="true"
                      className="size-4 shrink-0 text-primary"
                    />
                  ) : (
                    <X
                      aria-hidden="true"
                      className="size-4 shrink-0 text-destructive"
                    />
                  )}
                  <span className="sr-only" id={`${id}-result-${position}`}>
                    {t(
                      answers[item.id]?.result
                        ? "study.correct"
                        : "study.incorrect"
                    )}
                  </span>
                  <span className="min-w-0 flex-1" lang={output.language}>
                    {item.prompt}
                  </span>
                  <ChevronRight
                    aria-hidden="true"
                    className="size-4 text-muted-foreground"
                  />
                </button>
              </li>
            ))}
          </ul>
        </div>
        <Button
          className="min-h-11 rounded-xl"
          onClick={() => navigate(newQuiz)}
          type="button"
          variant="outline"
        >
          <RotateCcw />
          {t("study.retake")}
        </Button>
      </section>
    );
  }
  const empty =
    "options" in question ? !answer.choices.length : !answer.text.trim();
  let primaryLabel = "study.checkAnswer" as
    | "study.checkAnswer"
    | "study.seeResults"
    | "detail.nextQuestion";
  if (checked) {
    primaryLabel = last ? "study.seeResults" : "detail.nextQuestion";
  }
  return (
    <section className="min-w-0 space-y-5" data-template="quiz">
      <div className="flex min-h-9 items-center gap-4">
        <StudyProgress current={index + 1} total={total} />
        <span className="font-medium text-muted-foreground text-xs">
          {t(`options.${question.type}`)}
        </span>
      </div>
      <h3
        className="whitespace-pre-line break-words font-serif text-2xl leading-snug tracking-tight outline-none sm:text-[1.75rem]"
        id={`${id}question`}
        lang={output.language}
        ref={heading}
        tabIndex={-1}
      >
        {question.prompt}
      </h3>
      {question.image && (
        <StudyImage
          className="mx-0 max-h-36 rounded-xl"
          image={question.image}
          resolveAsset={resolveAsset}
        />
      )}
      <AnswerField
        answer={answer}
        id={id}
        language={output.language}
        question={question}
        save={save}
      />
      {question.hint && !checked && (
        <div>
          <Button
            aria-controls={`${id}hint`}
            aria-expanded={hintFor === question.id}
            className="min-h-10 rounded-lg px-1.5 text-muted-foreground"
            onClick={() =>
              setHintFor(hintFor === question.id ? null : question.id)
            }
            size="sm"
            type="button"
            variant="ghost"
          >
            <Lightbulb />
            {t("study.hint")}
          </Button>
          {hintFor === question.id && (
            <p
              className="mt-1 text-muted-foreground text-sm leading-relaxed"
              id={`${id}hint`}
              lang={output.language}
            >
              {question.hint}
            </p>
          )}
        </div>
      )}
      {checked && (
        <div
          aria-live="polite"
          className="space-y-1.5 border-primary/40 border-l-2 py-1 pl-4 text-sm"
        >
          <p
            className={cn(
              "font-semibold",
              answer.result ? "text-primary" : "text-destructive"
            )}
          >
            {t(answer.result ? "study.correct" : "study.incorrect")}
          </p>
          <p>
            {t("study.correctAnswer", {
              answer:
                "options" in question
                  ? question.options
                      .filter((option) => option.correct)
                      .map((option) => option.label)
                      .join(", ")
                  : question.acceptedAnswers.join(" / "),
            })}
          </p>
          <p
            className="text-muted-foreground leading-relaxed"
            lang={output.language}
          >
            {question.explanation}
          </p>
        </div>
      )}
      <div className="flex items-center justify-between gap-3 border-surface-divider border-t pt-4">
        <Button
          aria-label={t("detail.previousQuestion")}
          className="size-11 rounded-xl"
          disabled={index === 0}
          onClick={() => navigate({ ...progress, index: index - 1 })}
          size="icon"
          type="button"
          variant="ghost"
        >
          <ArrowLeft />
        </Button>
        <Button
          className="min-h-11 rounded-xl px-5"
          disabled={!checked && empty}
          onClick={advance}
          type="button"
        >
          {t(primaryLabel)}
          {checked && <ArrowRight />}
        </Button>
      </div>
    </section>
  );
}
