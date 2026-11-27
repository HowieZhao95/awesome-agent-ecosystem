export type TemplateImage = {
    storagePath: string;
    alt: string;
    mimeType: "image/png" | "image/jpeg" | "image/webp";
};
type Artifact = {
    id: string;
    title: string;
    language: string;
    sourceIds: string[];
    createdAt: string;
};
export type Flashcards = Artifact & {
    module: "flashcards";
    cards: {
        id: string;
        front: string;
        back: string;
        explanation?: string;
        image?: TemplateImage;
    }[];
};
type Question = {
    id: string;
    prompt: string;
    description?: string;
    explanation: string;
    hint?: string;
    image?: TemplateImage;
} & ({
    type: "multipleChoice" | "multipleSelect";
    options: {
        label: string;
        correct: boolean;
    }[];
} | {
    type: "fillInTheBlank" | "shortAnswer";
    acceptedAnswers: string[];
});
export type Quiz = Artifact & {
    module: "quiz";
    questions: Question[];
};
export type Chapter = {
    title: string;
    body: string;
    table?: {
        headers: string[];
        rows: string[][];
    };
};
export type InteractiveReport = Artifact & {
    module: "reports";
    format: "interactive";
    sections: Chapter[];
    embeds: (Flashcards | Quiz)[];
};
export type LearningTemplateOutput = InteractiveReport | Flashcards | Quiz;
export type ResolveAsset = (storagePath: string) => string;
export type FlashcardProgress = {
    order: number[];
    index: number;
    flipped: boolean;
    marks: Record<string, boolean>;
    reviewed: string[];
    finished: boolean;
};
export type QuizAnswer = {
    choices: number[];
    text: string;
    result?: boolean;
};
export type QuizProgress = {
    index: number;
    answers: Record<string, QuizAnswer>;
    finished: boolean;
};
export type StudyMemory = {
    cards: Map<string, FlashcardProgress>;
    quizzes: Map<string, QuizProgress>;
};
export {};
