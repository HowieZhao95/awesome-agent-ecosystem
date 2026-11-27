// src/flashcard-template.tsx
import {
  ArrowLeft,
  ArrowRight,
  Check,
  CheckCheck,
  Ellipsis,
  Layers2,
  RotateCcw,
  RotateCw,
  Shuffle
} from "lucide-react";
import { useId, useRef, useState } from "react";

// src/host.tsx
import {
  createContext,
  useContext
} from "react";
var Context = createContext(null);
var LearningTemplateProvider = Context.Provider;
function useTemplateHost() {
  const host = useContext(Context);
  if (!host) {
    throw new Error("LearningTemplateProvider is required");
  }
  return host;
}

// src/study-progress.tsx
import { jsx, jsxs } from "react/jsx-runtime";
function StudyProgress({
  current,
  total
}) {
  const { t } = useTemplateHost();
  const label = t("viewer.position", { current, total });
  return /* @__PURE__ */ jsxs("div", { className: "flex min-w-0 flex-1 items-center gap-3", children: [
    /* @__PURE__ */ jsxs(
      "span",
      {
        "aria-hidden": "true",
        className: "shrink-0 font-medium text-xs tabular-nums",
        children: [
          current,
          " ",
          /* @__PURE__ */ jsx("span", { className: "px-0.5 text-muted-foreground", children: "/" }),
          " ",
          total
        ]
      }
    ),
    /* @__PURE__ */ jsx(
      "progress",
      {
        "aria-label": label,
        className: "h-1 max-w-44 flex-1 appearance-none overflow-hidden rounded-full bg-muted text-primary [&::-moz-progress-bar]:bg-primary [&::-webkit-progress-bar]:bg-muted [&::-webkit-progress-value]:rounded-full [&::-webkit-progress-value]:bg-primary",
        max: total,
        value: current
      }
    )
  ] });
}

// src/flashcard-template.tsx
import { jsx as jsx2, jsxs as jsxs2 } from "react/jsx-runtime";
function FlashcardTemplate({
  output,
  memory,
  resolveAsset
}) {
  const {
    t,
    Button,
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
    StudyImage
  } = useTemplateHost();
  const cardTextId = useId();
  const flipButton = useRef(null);
  const completeHeading = useRef(null);
  const all = output.cards.map((_, position) => position);
  const initial = {
    order: all,
    index: 0,
    flipped: false,
    marks: {},
    reviewed: [],
    finished: false
  };
  const [progress, setProgress] = useState(
    () => memory.cards.get(output.id) ?? initial
  );
  const { order, index, flipped, marks } = progress;
  const card = output.cards[order[index]];
  const missed = all.filter(
    (position) => marks[output.cards[position].id] === false
  );
  const known = Object.values(marks).filter(Boolean).length;
  const score = t("study.cardProgress", { known, missed: missed.length });
  function update(next) {
    memory.cards.set(output.id, next);
    setProgress(next);
  }
  function focusCard() {
    requestAnimationFrame(
      () => (flipButton.current ?? completeHeading.current)?.focus({
        preventScroll: true
      })
    );
  }
  function move(next) {
    update({ ...progress, index: next, flipped: false });
  }
  function mark(understood) {
    const reviewed = new Set(progress.reviewed);
    reviewed.add(card.id);
    const unreviewed = (position) => !reviewed.has(output.cards[position].id);
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
      flipped: false
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
    return /* @__PURE__ */ jsxs2(
      "section",
      {
        className: "space-y-5 py-8 text-center",
        "data-template": "flashcards",
        children: [
          /* @__PURE__ */ jsx2(
            CheckCheck,
            {
              "aria-hidden": "true",
              className: "mx-auto size-8 text-primary"
            }
          ),
          /* @__PURE__ */ jsx2(
            "h3",
            {
              className: "font-serif text-3xl outline-none",
              ref: completeHeading,
              tabIndex: -1,
              children: t("detail.roundComplete")
            }
          ),
          /* @__PURE__ */ jsx2("p", { "aria-live": "polite", className: "text-muted-foreground text-sm", children: score }),
          /* @__PURE__ */ jsxs2("div", { className: "flex flex-wrap justify-center gap-2", children: [
            missed.length > 0 && /* @__PURE__ */ jsx2(
              Button,
              {
                className: "min-h-11 rounded-xl",
                onClick: reviewMissed,
                type: "button",
                children: t("study.reviewMissed")
              }
            ),
            /* @__PURE__ */ jsx2(
              Button,
              {
                className: "min-h-11 rounded-xl",
                onClick: restart,
                type: "button",
                variant: "outline",
                children: t("study.restart")
              }
            )
          ] })
        ]
      }
    );
  }
  return /* @__PURE__ */ jsxs2(
    "section",
    {
      className: "@container min-w-0 space-y-3",
      "data-template": "flashcards",
      children: [
        /* @__PURE__ */ jsxs2("div", { className: "flex items-center gap-4", children: [
          /* @__PURE__ */ jsx2(StudyProgress, { current: index + 1, total: order.length }),
          /* @__PURE__ */ jsxs2(DropdownMenu, { children: [
            /* @__PURE__ */ jsx2(DropdownMenuTrigger, { asChild: true, children: /* @__PURE__ */ jsx2(
              Button,
              {
                "aria-label": t("detail.practiceOptions"),
                className: "size-11 rounded-xl",
                size: "icon",
                type: "button",
                variant: "ghost",
                children: /* @__PURE__ */ jsx2(Ellipsis, { "aria-hidden": "true" })
              }
            ) }),
            /* @__PURE__ */ jsxs2(DropdownMenuContent, { align: "end", children: [
              /* @__PURE__ */ jsxs2(DropdownMenuItem, { disabled: order.length < 2, onSelect: shuffle, children: [
                /* @__PURE__ */ jsx2(Shuffle, {}),
                t("study.shuffle")
              ] }),
              /* @__PURE__ */ jsxs2(DropdownMenuItem, { disabled: !missed.length, onSelect: reviewMissed, children: [
                /* @__PURE__ */ jsx2(Layers2, {}),
                t("study.reviewMissed")
              ] }),
              /* @__PURE__ */ jsxs2(DropdownMenuItem, { onSelect: restart, children: [
                /* @__PURE__ */ jsx2(RotateCcw, {}),
                t("study.restart")
              ] })
            ] })
          ] })
        ] }),
        /* @__PURE__ */ jsxs2("article", { className: "relative flex @md:min-h-72 min-h-64 flex-col justify-center rounded-2xl border border-border bg-card bg-linear-to-br from-primary/[0.045] to-transparent @md:px-10 px-6 py-16 shadow-xs", children: [
          /* @__PURE__ */ jsxs2("span", { className: "absolute top-5 @md:left-10 left-6 flex items-center gap-2 text-muted-foreground text-xs", children: [
            /* @__PURE__ */ jsx2(Layers2, { "aria-hidden": "true", className: "size-4 text-primary" }),
            t(flipped ? "study.answer" : "study.question")
          ] }),
          /* @__PURE__ */ jsxs2(
            "div",
            {
              "aria-live": "polite",
              className: "flex min-w-0 flex-wrap items-center gap-x-6 gap-y-4",
              id: cardTextId,
              lang: output.language,
              children: [
                /* @__PURE__ */ jsxs2("div", { className: "min-w-36 flex-1 space-y-3", children: [
                  /* @__PURE__ */ jsx2("p", { className: "break-words font-serif @md:text-3xl text-[1.55rem] leading-snug tracking-tight", children: flipped ? card.back : card.front }),
                  flipped && card.explanation && card.explanation !== card.back && /* @__PURE__ */ jsx2("p", { className: "max-w-prose whitespace-pre-line text-muted-foreground text-sm leading-relaxed", children: card.explanation })
                ] }),
                card.image && /* @__PURE__ */ jsx2(
                  StudyImage,
                  {
                    className: "m-0 h-auto max-h-28 @md:w-36 w-28 shrink-0 rounded-lg",
                    image: card.image,
                    resolveAsset
                  }
                )
              ]
            }
          ),
          /* @__PURE__ */ jsx2(
            "button",
            {
              "aria-describedby": cardTextId,
              "aria-label": t(flipped ? "study.showQuestion" : "study.showAnswer"),
              "aria-pressed": flipped,
              className: "group absolute inset-0 cursor-pointer rounded-2xl text-left outline-none focus-visible:ring-2 focus-visible:ring-ring",
              onClick: () => update({ ...progress, flipped: !flipped }),
              ref: flipButton,
              type: "button",
              children: /* @__PURE__ */ jsxs2("span", { className: "absolute bottom-5 @md:left-10 left-6 flex items-center gap-2 font-medium text-primary text-sm group-hover:underline", children: [
                /* @__PURE__ */ jsx2(RotateCw, { "aria-hidden": "true", className: "size-4" }),
                t(flipped ? "study.showQuestion" : "study.showAnswer")
              ] })
            }
          )
        ] }),
        /* @__PURE__ */ jsxs2("div", { className: "flex min-h-12 items-center justify-between gap-1", children: [
          /* @__PURE__ */ jsx2(
            Button,
            {
              "aria-label": t("detail.previousCard"),
              className: "size-11 rounded-xl",
              disabled: index === 0,
              onClick: () => move(index - 1),
              size: "icon",
              type: "button",
              variant: "ghost",
              children: /* @__PURE__ */ jsx2(ArrowLeft, {})
            }
          ),
          flipped ? /* @__PURE__ */ jsxs2("div", { className: "flex flex-wrap justify-center gap-2", children: [
            /* @__PURE__ */ jsxs2(
              Button,
              {
                className: "min-h-11 rounded-xl",
                onClick: () => mark(false),
                type: "button",
                variant: "outline",
                children: [
                  /* @__PURE__ */ jsx2(RotateCcw, {}),
                  t("study.missed")
                ]
              }
            ),
            /* @__PURE__ */ jsxs2(
              Button,
              {
                className: "min-h-11 rounded-xl",
                onClick: () => mark(true),
                type: "button",
                children: [
                  /* @__PURE__ */ jsx2(Check, {}),
                  t("study.known")
                ]
              }
            )
          ] }) : /* @__PURE__ */ jsx2(
            "p",
            {
              "aria-live": "polite",
              className: "text-center text-muted-foreground text-xs",
              children: score
            }
          ),
          /* @__PURE__ */ jsx2(
            Button,
            {
              "aria-label": t("detail.nextCard"),
              className: "size-11 rounded-xl",
              disabled: index === order.length - 1,
              onClick: () => move(index + 1),
              size: "icon",
              type: "button",
              variant: "ghost",
              children: /* @__PURE__ */ jsx2(ArrowRight, {})
            }
          )
        ] })
      ]
    }
  );
}

// src/interactive-report-template.tsx
import { ArrowRight as ArrowRight3, Layers2 as Layers22, ListChecks } from "lucide-react";
import { useId as useId3, useRef as useRef3, useState as useState3 } from "react";

// src/class-names.ts
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
function cn(...values) {
  return twMerge(clsx(values));
}

// src/quiz-template.tsx
import {
  ArrowLeft as ArrowLeft2,
  ArrowRight as ArrowRight2,
  Check as Check2,
  CheckCircle2,
  ChevronRight,
  Lightbulb,
  RotateCcw as RotateCcw2,
  X
} from "lucide-react";
import { useId as useId2, useRef as useRef2, useState as useState2 } from "react";
import { jsx as jsx3, jsxs as jsxs3 } from "react/jsx-runtime";
var blankAnswer = { choices: [], text: "" };
var newQuiz = { index: 0, answers: {}, finished: false };
var spaces = /\s+/g;
function normalize(answer) {
  return answer.normalize("NFKC").trim().replace(spaces, " ").toLowerCase();
}
function AnswerField({
  id,
  language,
  question,
  answer,
  save
}) {
  const { t, Label, Checkbox, RadioGroup, RadioGroupItem, Input, Textarea } = useTemplateHost();
  const checked = answer.result !== void 0;
  if ("options" in question) {
    const multiple = question.type === "multipleSelect";
    const choices = question.options.map((option, index) => {
      const selected = answer.choices.includes(index);
      const textId = `${id}-label-${index}`;
      return /* @__PURE__ */ jsxs3(
        Label,
        {
          className: cn(
            "flex min-h-12 cursor-pointer items-center gap-3 rounded-xl border border-border-strong bg-card/55 px-4 py-3 font-normal text-sm leading-relaxed",
            !checked && "transition-colors hover:bg-muted/65",
            selected && "border-primary/45 bg-primary/[0.055]",
            checked && "cursor-default",
            checked && option.correct && "border-primary/55",
            checked && selected && !option.correct && "border-destructive/45"
          ),
          htmlFor: id + index,
          children: [
            multiple ? /* @__PURE__ */ jsx3(
              Checkbox,
              {
                "aria-labelledby": textId,
                checked: selected,
                disabled: checked,
                id: id + index,
                onCheckedChange: (value) => save({
                  choices: value === true ? [...answer.choices, index] : answer.choices.filter((choice) => choice !== index),
                  text: ""
                })
              }
            ) : /* @__PURE__ */ jsx3(
              RadioGroupItem,
              {
                "aria-labelledby": textId,
                disabled: checked,
                id: id + index,
                value: String(index)
              }
            ),
            /* @__PURE__ */ jsx3(
              "span",
              {
                className: "min-w-0 flex-1 break-words",
                id: textId,
                lang: language,
                children: option.label
              }
            ),
            checked && option.correct && /* @__PURE__ */ jsx3(
              Check2,
              {
                "aria-hidden": "true",
                className: "size-4 shrink-0 text-primary"
              }
            ),
            checked && selected && !option.correct && /* @__PURE__ */ jsx3(
              X,
              {
                "aria-hidden": "true",
                className: "size-4 shrink-0 text-destructive"
              }
            )
          ]
        },
        index
      );
    });
    return multiple ? /* @__PURE__ */ jsxs3("fieldset", { className: "grid min-w-0 gap-2", children: [
      /* @__PURE__ */ jsx3("legend", { className: "sr-only", children: question.prompt }),
      choices
    ] }) : /* @__PURE__ */ jsx3(
      RadioGroup,
      {
        "aria-labelledby": `${id}question`,
        className: "gap-2",
        disabled: checked,
        onValueChange: (value) => save({ choices: [Number(value)], text: "" }),
        value: answer.choices.length ? String(answer.choices[0]) : "",
        children: choices
      }
    );
  }
  const field = {
    id: `${id}answer`,
    readOnly: checked,
    value: answer.text,
    onChange: (event) => save({ choices: [], text: event.target.value })
  };
  return /* @__PURE__ */ jsxs3("div", { className: "space-y-2", children: [
    /* @__PURE__ */ jsx3(Label, { htmlFor: field.id, children: t("study.yourAnswer") }),
    question.type === "shortAnswer" ? /* @__PURE__ */ jsx3(Textarea, { ...field, className: "min-h-24 rounded-xl" }) : /* @__PURE__ */ jsx3(Input, { ...field, className: "min-h-11 rounded-xl" })
  ] });
}
function QuizTemplate({
  output,
  resolveAsset,
  memory
}) {
  const { t, Button, StudyImage } = useTemplateHost();
  const id = useId2();
  const heading = useRef2(null);
  const [progress, setProgress] = useState2(
    () => memory.quizzes.get(output.id) ?? newQuiz
  );
  const [hintFor, setHintFor] = useState2(null);
  const { index, answers, finished } = progress;
  const question = output.questions[index];
  const answer = answers[question.id] ?? blankAnswer;
  const checked = answer.result !== void 0;
  const total = output.questions.length;
  const last = index === total - 1;
  function update(next) {
    memory.quizzes.set(output.id, next);
    setProgress(next);
  }
  function navigate(next) {
    update(next);
    setHintFor(null);
    requestAnimationFrame(
      () => heading.current?.focus({ preventScroll: true })
    );
  }
  function save(next) {
    update({ ...progress, answers: { ...answers, [question.id]: next } });
  }
  function advance() {
    if (checked) {
      navigate(
        last ? { ...progress, finished: true } : { ...progress, index: index + 1 }
      );
      return;
    }
    const correct = "options" in question ? question.options.every(
      (option, i) => option.correct === answer.choices.includes(i)
    ) : question.acceptedAnswers.some(
      (value) => normalize(value) === normalize(answer.text)
    );
    save({ ...answer, result: correct });
  }
  if (finished) {
    const correct = output.questions.filter(
      (item) => answers[item.id]?.result
    ).length;
    return /* @__PURE__ */ jsxs3("section", { className: "space-y-6", "data-template": "quiz", children: [
      /* @__PURE__ */ jsx3(
        "h3",
        {
          className: "font-serif text-3xl tracking-tight outline-none",
          ref: heading,
          tabIndex: -1,
          children: t("study.quizScore", { correct, total })
        }
      ),
      /* @__PURE__ */ jsxs3("div", { children: [
        /* @__PURE__ */ jsx3("h4", { className: "border-surface-divider border-b pb-3 font-medium text-muted-foreground text-sm", children: t("study.reviewAnswers") }),
        /* @__PURE__ */ jsx3("ul", { className: "divide-y divide-surface-divider", children: output.questions.map((item, position) => /* @__PURE__ */ jsx3("li", { children: /* @__PURE__ */ jsxs3(
          "button",
          {
            "aria-describedby": `${id}-result-${position}`,
            "aria-label": item.prompt,
            className: "flex min-h-12 w-full items-center gap-3 rounded-sm py-3 text-left text-sm hover:text-primary focus-visible:outline-ring",
            onClick: () => navigate({ ...progress, index: position, finished: false }),
            type: "button",
            children: [
              answers[item.id]?.result ? /* @__PURE__ */ jsx3(
                CheckCircle2,
                {
                  "aria-hidden": "true",
                  className: "size-4 shrink-0 text-primary"
                }
              ) : /* @__PURE__ */ jsx3(
                X,
                {
                  "aria-hidden": "true",
                  className: "size-4 shrink-0 text-destructive"
                }
              ),
              /* @__PURE__ */ jsx3("span", { className: "sr-only", id: `${id}-result-${position}`, children: t(
                answers[item.id]?.result ? "study.correct" : "study.incorrect"
              ) }),
              /* @__PURE__ */ jsx3("span", { className: "min-w-0 flex-1", lang: output.language, children: item.prompt }),
              /* @__PURE__ */ jsx3(
                ChevronRight,
                {
                  "aria-hidden": "true",
                  className: "size-4 text-muted-foreground"
                }
              )
            ]
          }
        ) }, item.id)) })
      ] }),
      /* @__PURE__ */ jsxs3(
        Button,
        {
          className: "min-h-11 rounded-xl",
          onClick: () => navigate(newQuiz),
          type: "button",
          variant: "outline",
          children: [
            /* @__PURE__ */ jsx3(RotateCcw2, {}),
            t("study.retake")
          ]
        }
      )
    ] });
  }
  const empty = "options" in question ? !answer.choices.length : !answer.text.trim();
  let primaryLabel = "study.checkAnswer";
  if (checked) {
    primaryLabel = last ? "study.seeResults" : "detail.nextQuestion";
  }
  return /* @__PURE__ */ jsxs3("section", { className: "min-w-0 space-y-5", "data-template": "quiz", children: [
    /* @__PURE__ */ jsxs3("div", { className: "flex min-h-9 items-center gap-4", children: [
      /* @__PURE__ */ jsx3(StudyProgress, { current: index + 1, total }),
      /* @__PURE__ */ jsx3("span", { className: "font-medium text-muted-foreground text-xs", children: t(`options.${question.type}`) })
    ] }),
    /* @__PURE__ */ jsx3(
      "h3",
      {
        className: "whitespace-pre-line break-words font-serif text-2xl leading-snug tracking-tight outline-none sm:text-[1.75rem]",
        id: `${id}question`,
        lang: output.language,
        ref: heading,
        tabIndex: -1,
        children: question.prompt
      }
    ),
    question.image && /* @__PURE__ */ jsx3(
      StudyImage,
      {
        className: "mx-0 max-h-36 rounded-xl",
        image: question.image,
        resolveAsset
      }
    ),
    /* @__PURE__ */ jsx3(
      AnswerField,
      {
        answer,
        id,
        language: output.language,
        question,
        save
      }
    ),
    question.hint && !checked && /* @__PURE__ */ jsxs3("div", { children: [
      /* @__PURE__ */ jsxs3(
        Button,
        {
          "aria-controls": `${id}hint`,
          "aria-expanded": hintFor === question.id,
          className: "min-h-10 rounded-lg px-1.5 text-muted-foreground",
          onClick: () => setHintFor(hintFor === question.id ? null : question.id),
          size: "sm",
          type: "button",
          variant: "ghost",
          children: [
            /* @__PURE__ */ jsx3(Lightbulb, {}),
            t("study.hint")
          ]
        }
      ),
      hintFor === question.id && /* @__PURE__ */ jsx3(
        "p",
        {
          className: "mt-1 text-muted-foreground text-sm leading-relaxed",
          id: `${id}hint`,
          lang: output.language,
          children: question.hint
        }
      )
    ] }),
    checked && /* @__PURE__ */ jsxs3(
      "div",
      {
        "aria-live": "polite",
        className: "space-y-1.5 border-primary/40 border-l-2 py-1 pl-4 text-sm",
        children: [
          /* @__PURE__ */ jsx3(
            "p",
            {
              className: cn(
                "font-semibold",
                answer.result ? "text-primary" : "text-destructive"
              ),
              children: t(answer.result ? "study.correct" : "study.incorrect")
            }
          ),
          /* @__PURE__ */ jsx3("p", { children: t("study.correctAnswer", {
            answer: "options" in question ? question.options.filter((option) => option.correct).map((option) => option.label).join(", ") : question.acceptedAnswers.join(" / ")
          }) }),
          /* @__PURE__ */ jsx3(
            "p",
            {
              className: "text-muted-foreground leading-relaxed",
              lang: output.language,
              children: question.explanation
            }
          )
        ]
      }
    ),
    /* @__PURE__ */ jsxs3("div", { className: "flex items-center justify-between gap-3 border-surface-divider border-t pt-4", children: [
      /* @__PURE__ */ jsx3(
        Button,
        {
          "aria-label": t("detail.previousQuestion"),
          className: "size-11 rounded-xl",
          disabled: index === 0,
          onClick: () => navigate({ ...progress, index: index - 1 }),
          size: "icon",
          type: "button",
          variant: "ghost",
          children: /* @__PURE__ */ jsx3(ArrowLeft2, {})
        }
      ),
      /* @__PURE__ */ jsxs3(
        Button,
        {
          className: "min-h-11 rounded-xl px-5",
          disabled: !checked && empty,
          onClick: advance,
          type: "button",
          children: [
            t(primaryLabel),
            checked && /* @__PURE__ */ jsx3(ArrowRight2, {})
          ]
        }
      )
    ] })
  ] });
}

// src/interactive-report-template.tsx
import { jsx as jsx4, jsxs as jsxs4 } from "react/jsx-runtime";
function ReportSectionBody({ section }) {
  return /* @__PURE__ */ jsxs4("div", { className: "min-w-0 space-y-5", children: [
    /* @__PURE__ */ jsx4("p", { className: "max-w-[65ch] whitespace-pre-line break-words text-[0.975rem] leading-[1.85]", children: section.body }),
    section.table && /* @__PURE__ */ jsx4("div", { className: "overflow-x-auto", children: /* @__PURE__ */ jsxs4("table", { className: "w-full border-collapse text-left text-sm leading-relaxed", children: [
      /* @__PURE__ */ jsx4("caption", { className: "sr-only", children: section.title }),
      /* @__PURE__ */ jsx4("thead", { children: /* @__PURE__ */ jsx4("tr", { className: "border-surface-divider border-y bg-muted/40", children: section.table.headers.map((header, i) => /* @__PURE__ */ jsx4("th", { className: "px-3 py-2.5 font-medium", scope: "col", children: header }, i)) }) }),
      /* @__PURE__ */ jsx4("tbody", { children: section.table.rows.map((row, r) => /* @__PURE__ */ jsx4(
        "tr",
        {
          className: "border-surface-divider border-b align-top",
          children: row.map((cell, c) => /* @__PURE__ */ jsx4("td", { className: "px-3 py-3", children: cell }, c))
        },
        r
      )) })
    ] }) })
  ] });
}
function InteractiveReportTemplate({
  output,
  memory,
  resolveAsset
}) {
  const { t, Button, LearningSelect } = useTemplateHost();
  const id = useId3();
  const heading = useRef3(null);
  const [index, setIndex] = useState3(0);
  const labels = [
    ...output.sections.map((section) => section.title),
    ...output.embeds.map((activity) => activity.title)
  ];
  const chapter = output.sections[index];
  const embed = output.embeds[index - output.sections.length];
  function select(next) {
    setIndex(next);
    requestAnimationFrame(() => heading.current?.focus());
  }
  return /* @__PURE__ */ jsx4("div", { className: "@container", "data-template": "interactive-report", children: /* @__PURE__ */ jsxs4("div", { className: "grid @2xl:grid-cols-[10rem_minmax(0,1fr)] items-start @2xl:gap-10 gap-6", children: [
    /* @__PURE__ */ jsxs4("nav", { "aria-label": t("detail.contents"), className: "min-w-0", children: [
      /* @__PURE__ */ jsxs4("div", { className: "relative @2xl:hidden", children: [
        /* @__PURE__ */ jsx4(
          "label",
          {
            className: "mb-1.5 block font-medium text-muted-foreground text-xs",
            htmlFor: `${id}select`,
            children: t("detail.contents")
          }
        ),
        /* @__PURE__ */ jsx4(
          LearningSelect,
          {
            id: `${id}select`,
            label: t("detail.contents"),
            lang: output.language,
            onValueChange: (value) => setIndex(Number(value)),
            options: labels.map((label, n) => ({ label, value: String(n) })),
            value: String(index)
          }
        )
      ] }),
      /* @__PURE__ */ jsxs4("div", { className: "@2xl:block hidden", children: [
        /* @__PURE__ */ jsx4("p", { className: "mb-3 font-medium text-muted-foreground text-xs", children: t("detail.contents") }),
        /* @__PURE__ */ jsx4("ol", { className: "space-y-0.5", children: labels.map((label, n) => {
          const item = output.embeds[n - output.sections.length];
          const Icon = item?.module === "quiz" ? ListChecks : Layers22;
          return /* @__PURE__ */ jsxs4("li", { children: [
            n === output.sections.length && /* @__PURE__ */ jsx4("p", { className: "mt-6 mb-2 font-medium text-muted-foreground text-xs", children: t("detail.practice") }),
            /* @__PURE__ */ jsxs4(
              "button",
              {
                "aria-controls": `${id}page`,
                "aria-current": n === index ? "page" : void 0,
                "aria-label": label,
                className: cn(
                  "flex min-h-10 w-full items-start gap-2 rounded-lg px-2 py-2.5 text-left text-sm leading-snug focus-visible:outline-ring",
                  n === index ? "bg-primary/[0.075] font-semibold text-primary" : "text-muted-foreground hover:bg-muted/60 hover:text-foreground"
                ),
                lang: output.language,
                onClick: () => select(n),
                type: "button",
                children: [
                  item ? /* @__PURE__ */ jsx4(
                    Icon,
                    {
                      "aria-hidden": "true",
                      className: "mt-0.5 size-3.5 shrink-0"
                    }
                  ) : /* @__PURE__ */ jsx4(
                    "span",
                    {
                      "aria-hidden": "true",
                      className: "w-4 shrink-0 text-xs tabular-nums opacity-75",
                      children: n + 1
                    }
                  ),
                  /* @__PURE__ */ jsx4("span", { className: "break-words", children: label })
                ]
              }
            )
          ] }, n);
        }) })
      ] })
    ] }),
    /* @__PURE__ */ jsxs4(
      "section",
      {
        "aria-labelledby": `${id}heading`,
        className: "min-w-0",
        id: `${id}page`,
        children: [
          /* @__PURE__ */ jsx4(
            "h3",
            {
              className: "mb-4 break-words font-serif @2xl:text-[1.8rem] text-2xl leading-tight tracking-tight outline-none",
              id: `${id}heading`,
              lang: output.language,
              ref: heading,
              tabIndex: -1,
              children: labels[index]
            }
          ),
          chapter && /* @__PURE__ */ jsx4("div", { lang: output.language, children: /* @__PURE__ */ jsx4(ReportSectionBody, { section: chapter }) }),
          embed?.module === "flashcards" && /* @__PURE__ */ jsx4(
            FlashcardTemplate,
            {
              memory,
              output: embed,
              resolveAsset
            },
            embed.id
          ),
          embed?.module === "quiz" && /* @__PURE__ */ jsx4(
            QuizTemplate,
            {
              memory,
              output: embed,
              resolveAsset
            },
            embed.id
          ),
          chapter && index + 1 < labels.length && /* @__PURE__ */ jsx4("div", { className: "mt-7 flex justify-end", children: /* @__PURE__ */ jsxs4(
            Button,
            {
              className: "h-auto min-h-11 max-w-full whitespace-normal rounded-xl text-right",
              onClick: () => select(index + 1),
              type: "button",
              variant: "ghost",
              children: [
                labels[index + 1],
                /* @__PURE__ */ jsx4(ArrowRight3, { "aria-hidden": "true" })
              ]
            }
          ) })
        ]
      }
    )
  ] }) });
}
export {
  FlashcardTemplate,
  InteractiveReportTemplate,
  LearningTemplateProvider,
  QuizTemplate,
  ReportSectionBody
};
