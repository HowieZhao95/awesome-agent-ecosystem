import type { Chapter, InteractiveReport, ResolveAsset, StudyMemory } from "./types";
export declare function ReportSectionBody({ section }: {
    section: Chapter;
}): import("react").JSX.Element;
export declare function InteractiveReportTemplate({ output, memory, resolveAsset, }: {
    output: InteractiveReport;
    memory: StudyMemory;
    resolveAsset: ResolveAsset;
}): import("react").JSX.Element;
