import { createRoot } from "react-dom/client";
import de from "../locales/de.json";
import en from "../locales/en.json";
import es from "../locales/es.json";
import fr from "../locales/fr.json";
import it from "../locales/it.json";
import ja from "../locales/ja.json";
import pt from "../locales/pt.json";
import zh from "../locales/zh.json";
import {
  FlashcardTemplate,
  InteractiveReportTemplate,
  type LearningTemplateOutput,
  LearningTemplateProvider,
  QuizTemplate,
  type StudyMemory,
} from "../src/index";
import controls from "./controls";

const dictionaries: Record<string, Record<string, string>> = {
  en,
  zh,
  de,
  es,
  fr,
  it,
  ja,
  pt,
};
const language = document.documentElement.lang.split("-")[0];
const messages = dictionaries[language] ?? en;
const placeholder = /\{(\w+)\}/g;
const t = (key: string, values: Record<string, string | number> = {}) =>
  (messages[key] ?? key).replace(placeholder, (original, name: string) =>
    String(values[name] ?? original)
  );
const memory: StudyMemory = { cards: new Map(), quizzes: new Map() };
const resolveAsset = (path: string) => new URL(path, document.baseURI).href;
const element = document.getElementById("learning-artifact");
const container = document.getElementById("learning-root");
if (!(element && container)) {
  throw new Error("Missing learning artifact or mount point");
}
const output: LearningTemplateOutput = JSON.parse(element.textContent ?? "");
if (!["reports", "flashcards", "quiz"].includes(output.module)) {
  throw new Error("Unsupported learning artifact");
}
const shared = { resolveAsset, memory };
function renderContent(data: LearningTemplateOutput) {
  switch (data.module) {
    case "reports":
      return <InteractiveReportTemplate {...shared} output={data} />;
    case "flashcards":
      return <FlashcardTemplate {...shared} output={data} />;
    case "quiz":
      return <QuizTemplate {...shared} output={data} />;
    default:
      throw new Error("Unsupported learning artifact");
  }
}
document.title = output.title;
createRoot(container).render(
  <LearningTemplateProvider value={{ ...controls, t }}>
    <article className={articleClass(output.module)}>
      <header className="mb-7 space-y-3 border-surface-divider border-b pb-6">
        <p className="font-medium text-muted-foreground text-sm">
          {t(`modules.${output.module}.name`)}
        </p>
        <h1
          className="break-words font-serif text-3xl sm:text-4xl"
          lang={output.language}
        >
          {output.title}
        </h1>
      </header>
      {renderContent(output)}
    </article>
  </LearningTemplateProvider>
);

function articleClass(module: LearningTemplateOutput["module"]) {
  return module === "reports"
    ? "mx-auto max-w-[60rem] px-5 py-8 sm:p-10"
    : "mx-auto max-w-[44rem] px-5 py-8 sm:p-10";
}
