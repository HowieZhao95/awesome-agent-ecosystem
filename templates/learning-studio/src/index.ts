// biome-ignore-all lint/performance/noBarrelFile: This is the public library export surface.
export { FlashcardTemplate } from "./flashcard-template";
export { LearningTemplateProvider, type TemplateHost } from "./host";
export {
  InteractiveReportTemplate,
  ReportSectionBody,
} from "./interactive-report-template";
export { QuizTemplate } from "./quiz-template";
export type {
  Flashcards,
  InteractiveReport,
  LearningTemplateOutput,
  Quiz,
  ResolveAsset,
  StudyMemory,
} from "./types";
