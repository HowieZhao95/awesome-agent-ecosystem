---
name: learning-interactive-report
description: Create an interactive interactive report from source material using the versioned Learning Studio HTML template.
---

# Interactive report

Render chapters, optional tables and embedded practice from one report. Preserve the section order and the supplied source IDs. A section needs a title and body. Use embeds for flashcards and quizzes.

1. Read [the output schema](schema.json) and [the example](example.json). Fill the content in the requested learning language and preserve the identifiers supplied by the host.
2. Start from the release file `dist/interactive-report.html`. Put the validated JSON in the `learning-artifact` data element. When writing an HTML file, escape literal `<` characters in serialized JSON as `\u003c`. The document language selects the interface language. The artifact language identifies the generated content.
3. Save the result in the project workspace. Relative media paths are resolved at display time. The host supplies its own source references and file-opening action.
4. Open the artifact, use its keyboard controls, and check the narrow layout. The interactive React source is [in the template package](../../src/interactive-report-template.tsx).
