# Learning Studio Templates

Learning Studio Templates provides three reusable, interactive HTML artifacts. Each accepts structured learning content and can also be rendered by a React host.

| Template | Contents |
| --- | --- |
| [Interactive report](templates/interactive-report/SKILL.md) | Navigable chapters, optional tables and embedded flashcards or quizzes. |
| [Flashcards](templates/flashcards/SKILL.md) | Card fronts and backs, recall marks, shuffle and missed-card practice. |
| [Quiz](templates/quiz/SKILL.md) | Four question types, hints, explanations, scoring and question-by-question review. |

## Open a template

Use Node 22 or newer. From the package directory run `npm install`, `npm run build` and `npm test`. Open any of the three HTML files in `dist/` in a browser. Each includes its own scripts and styles.

Replace the JSON in `<script type="application/json" id="learning-artifact">` with content matching that template’s schema. Escape literal less-than characters in embedded JSON as `\u003c`. Set the document’s `lang` for interface copy and set `language` on the artifact for authored content. The bundled interface supports Chinese, English, French, German, Japanese, Italian, Spanish and Portuguese. Supply any referenced images alongside the HTML.

## Use in a host

The package exports `InteractiveReportTemplate`, `FlashcardTemplate`, `QuizTemplate` and `LearningTemplateProvider`. Pass the host’s controls and translator to the provider. Each template accepts `output`, `memory` and `resolveAsset`. Keep the memory maps for the lifetime of the study session. Mount your host’s citations and file-opening actions beside the artifact. The standalone adapters are in [standalone/](standalone/).

The [manifest](manifest.json) records the version, stable resource IDs, schemas, examples and entry points. The course presentation uses the existing Agent resource’s pinned course-module template. [Course presentation resource](https://www.thusdesign.ai/agent#/resource/opendesign.html-ppt)

## License

The original template code is licensed under [MIT](LICENSE). The standalone distribution includes dependency notices in `dist/THIRD-PARTY-NOTICES.txt`. The course presentation is a reference to its separately maintained Agent resource.
