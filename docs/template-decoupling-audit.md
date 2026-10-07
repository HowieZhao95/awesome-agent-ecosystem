# OpenDesign 模板与设计系统边界审计

审计对象是固定 upstream snapshot `53231d40b778d88eba23f35547bf99485d3ae9fc`（归档 SHA-256 `edd9b2cf8f37f18bb26e070739a00149124adb3758572ae3bb4bc05e8816aba5`）。本报告只记录证据和建议，不复制上游正文。

## 结论

当前目录结构已经有独立的设计系统包，也有可复用的框架 seed、布局片段和示例；但 Skill/示例 prompt 把内容框架与视觉身份重新绑在一起。实施重点应是给模板定义稳定的框架身份，把风格约束从模板身份与示例指令中移出，让设计系统作为独立输入。七个现有模板候选覆盖 prototype、deck、dashboard、3D 展示、motion graphics、document、social carousel；按框架证据严格审查时，其中多个目前只有 Skill 和示例，尚不足以证明是可复用内容/代码框架。

## 当前 7 个目录记录

当前七个模板候选的上游记录如下。设计系统是另一类独立资产，不计入七模板：

| 路径 | 证据与分类 | 风格耦合情况 |
|---|---|---|
| `plugins/_official/examples/web-prototype/SKILL.md` | **可确认框架。** 对应 `design-templates/web-prototype/` 有 `assets/template.html`、`references/layouts.md`、检查清单和 example。正文要求从 seed/layout 组装。 | Skill 要求读取当前 `DESIGN.md` 并映射到 seed 的六个根变量，表明框架可接收 DS；但 `example_prompt` 仍要求保留模板 visual signature，需删除/改写此冲突指令。 |
| `plugins/_official/examples/html-ppt-pitch-deck/SKILL.md` | **独立框架证据不成立；应并入 deck 框架的内容配方。** 对应目录只有 Skill 和 example；正文明确路由到 `design-templates/html-ppt/SKILL.md` master 与共享 pitch-deck 模板。真正代码框架在 `design-templates/html-ppt/`，含 224 个支持文件、theme/runtime/layout。 | Deck 框架可选择 36 个 themes；pitch 配方限定募资叙事并要求确切 pitch-deck visual identity，应把业务内容配方与风格选择分开。 |
| `plugins/_official/examples/live-dashboard/SKILL.md` | **可确认框架。** 对应 `design-templates/live-dashboard/` 有 template、组件/布局/connector references、checklist 和 example。 | 正文要求按 active DESIGN 确定视觉方向、组件可 re-skin；当前 Notion 示例把具体业务场景和 connector 写入 prompt，应保留为配方而非框架身份。 |
| `plugins/_official/examples/motion-frames/SKILL.md` | **独立框架证据不成立；暂列专用 Skill/效果示例。** 对应 `design-templates/motion-frames/` 只有 Skill 和 example，没有 seed、布局库或共享 motion code framework。 | 它规定单幅构图与循环动画并展示视觉效果；证据不足以将任意 DS 套到可复用运动框架上。 |
| `plugins/_official/examples/docs-page/SKILL.md` | **独立框架证据不成立；暂列页面配方/示例。** 对应 `design-templates/docs-page/` 只有 Skill 和 example，没有可引用 seed/reference。 | 左导航、文章、右目录是清楚的页面结构，但结构描述加单个固定 example 还没有成为可复用代码框架。 |
| `plugins/_official/examples/social-carousel/SKILL.md` | **独立框架证据不成立；暂列产物配方/示例。** 对应 `design-templates/social-carousel/` 只有 Skill 和 example。 | 三张 1080 方图、跨卡标题、品牌标记、序号、caption 等定义了序列内容规则；没有 reusable seed/support files 证明可换风格框架。 |
| `plugins/_official/examples/mockup-device-3d/SKILL.md` | **独立框架证据不成立；暂列 3D showcase 配方/示例。** Skill 明确规定 iPhone/MacBook 场景、CSS transform、玻璃高光、地面反射及 single-file HTML，但对应目录仅有 Skill 和 `example.html`，未找到 scene seed、组件库或辅助代码。 | 视觉身份被写死为设备模型与玻璃/反射效果；其中屏幕内容应可由用户数据替换，但这还不足以证明具备可换 DS 的通用 3D 框架。 |

设计系统独立证据：`design-systems/agentic/manifest.json`、`DESIGN.md`、`tokens.css` 三件套齐全；其 system artifacts 含 deck、email、form、landing、newsletter、poster，表明 DS 本身跨多种产物复用。它是独立登记，不是第八个模板。

补充：`design-templates/image-poster/SKILL.md` 描述图像生成流程并输出 PNG/JPEG，应登记为任务 Skill，不因路径在 design-templates 就算作代码/内容模板。

## 114 个 design-templates 条目

快照中精确找到 114 个 `design-templates/<slug>/SKILL.md`。逐个核对目录下的实体文件清单，并阅读代表性 Skill 中对 seed、master skill、共享 runtime、示例和任务目标的引用。路径数量不等于模板数量。结构化分组和 114 个完整 slug 清单见 JSON evidence；以下给出审查结论及可复核的物证类别。

**16 个有独立复用框架物证的候选**：`flowai-live-dashboard-template`、`github-dashboard`、`guizang-ppt`、`html-ppt`、`ib-pitch-book`、`live-artifact`、`live-dashboard`、`mobile-app`、`open-design-landing`、`open-design-landing-deck`、`replit-deck`、`simple-deck`、`social-media-matrix-tracker-template`、`trading-analysis-dashboard-template`、`waitlist-page`、`web-prototype`。证据包括实体 `assets/template.html` 和 layouts/components/checklist references（例如 `simple-deck`、`live-dashboard`、`waitlist-page`）、完整 deck runtime/assets 的 `html-ppt`、带 schema + compose script 的 `open-design-landing-deck`，或多套可实例化 `assets/templates/*/template.html` 的 `live-artifact`。这些是框架候选，仍需逐个确认是否已有 DS 输入契约；不要把所有候选直接标为已解耦。

**37 个应依附主框架的风格入口**：3 个 `web-prototype-taste-*` 包含视觉取向描述和单一 `example.html`，没有自己的 seed/reference；32 个 `html-ppt-zhangzara-*` 包含 `template.json` 与单一 example/license；`html-ppt-taste-brutalist`、`html-ppt-taste-editorial` 是同类 deck 视觉入口。实际文件和 Skill 描述支持其作为 prototype/deck 的风格预设或示例，不足以支持独立模板 ID。

**13 个 deck 内容/效果入口**：`html-ppt-course-module`、`html-ppt-graphify-dark-graph`、`html-ppt-hermes-cyber-terminal`、`html-ppt-knowledge-arch-blueprint`、`html-ppt-obsidian-claude-gradient`、`html-ppt-pitch-deck`、`html-ppt-presenter-mode-reveal`、`html-ppt-product-launch`、`html-ppt-tech-sharing`、`html-ppt-testing-safety-alert`、`html-ppt-weekly-report`、`html-ppt-xhs-pastel-card`、`html-ppt-xhs-white-editorial`。这些目录自身是 Skill + example；Skill/引用路由到 `html-ppt` master。pitch deck 同时带融资内容要求和指定视觉身份，属于需要拆分的内容配方。

**48 个目前未证明有独立框架的任务 Skill 或单产物示例**：`audio-jingle`、`blog-post`、`clinical-case-report`、`contact-widget`、`critique`、`dashboard`、`dating-web`、`dcf-valuation`、`digital-eguide`、`docs-page`、`email-marketing`、`eng-runbook`、`finance-report`、`gamified-app`、`hr-onboarding`、`hyperframes`、`image-poster`、`invoice`、`kami-deck`、`kami-landing`、`kanban-board`、`last30days`、`magazine-poster`、`meeting-notes`、`mobile-onboarding`、`motion-frames`、`orbit-general`、`orbit-github`、`orbit-gmail`、`orbit-linear`、`orbit-notion`、`pm-spec`、`pricing-page`、`saas-landing`、`social-carousel`、`social-media-dashboard`、`sprite-animation`、`team-okrs`、`tweaks`、`video-shortform`、`webgl-experience`、`weekly-update`、`wireframe-annotated`、`wireframe-greybox`、`wireframe-mobile-flow`、`wireframe-sketch`、`worker-visualizer`、`x-research`。其中也有任务辅助文件（如 `last30days` 的 Python 收集工具、`hyperframes` 的 motion references）或具体页面说明；这类内容可作为 Skill 或经补充成为模板，但当前没有证据支持每个条目已经是自含、可换 DS 的内容/代码框架。下一轮应按用户价值逐个复核，不能把“未证明”误写成“无价值”。

这四组数量为 16 + 37 + 13 + 48 = 114。分类依据是包内支持文件与 Skill 正文引用，而非 slug 名称；这是当前边界决策，不是 114 项迁移授权。

## 设计系统核对

`design-systems/README.md` 声明标准包为 `manifest.json + DESIGN.md + tokens.css`，并要求 manifest 稳定记录元数据、来源和路径；`DESIGN.md` 是 agent 设计正文，`tokens.css` 是编译后的语义 tokens。按文件内容与 JSON 字段逐项核对：快照有 153 个一级目录，其中 `_schema` 是 schema 目录；其余 152 个均具有三件套，152 份 manifest 都是有效 JSON，slug 与 `manifest.id` 相同，声明的 design/tokens 路径分别是 `DESIGN.md` 和 `tokens.css`。README 的“151 packages”落后实际文件清单一项，应在后续维护时修正文档数字。

同一 README 说明设计上下文会被注入 agent prompt；Web Prototype 和 Live Dashboard 的 Skill 正文都明确消费 active `DESIGN.md`。这证明当前上游已有单套框架应用 DS 的技术路径，但 `example_prompt` 及若干 catalog 描述仍把“模板视觉签名”视为模板本身，语义边界还未完成。

## 建议的最小实施

1. 将模板记录定义为可复用内容与代码框架：`SKILL.md`、seed/代码、示例、辅助文件；其身份字段描述产物结构、行为和内容槽，不描述 palette/font/品牌风格。
2. 设计系统独立登记，保留 `manifest.json + DESIGN.md + tokens.css` 核心；模板明确读取当前 DS，并把 semantic token 映射到框架定义的 token slots。用户未指定 DS 时，框架可给出默认值，但默认值不能变成模板身份。
3. 将 taste/品牌类 entry point 降为设计系统或风格 preset；将 pitch fundraising、Notion dashboard 一类业务内容 prompt 留作可选配方/示例。换 DS 不创建新模板 ID。
4. 七类使用统一枚举：prototype、deck、3D、dashboard、motion graphics、document、custom。以产物用途/交互形态分类，不按 HTML/PPT 等实现文件扩展名分类。当前 3D 类应标记缺框架证据，等待真正可复用 Three.js/WebGPU scene framework。
5. 暂不实施 114 项批量重命名、迁移，也不改 editor/runtime/kernel。先对本次 7 个候选逐个记录分类、seed/reference/example 文件、DS consumption contract 和 style-boundary 决策；其中目前只有 Web Prototype 与 Live Dashboard 已确认实体 seed/reference 框架。

## 证据文件

结构化路径、哈希、上游快照标识、核对计数和摘录索引见同目录 `evidence/2026-10-07-template-decoupling-audit.json`。
