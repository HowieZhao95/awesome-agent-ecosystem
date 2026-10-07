# Template and Design System Separation Implementation Plan

**Goal:** 按用户最新裁定把模板登记为可复用内容与代码框架，七类不变；设计系统独立登记 manifest.json、DESIGN.md、tokens.css；框架身份不随视觉风格变化。

**Architecture:** 修订分类/契约正本，以最小可选资源 profile 登记真实文件角色。公共 UI 分别展示框架文件、参考示例与独立设计系统文件；候选的上游耦合情况明确说明，不把静态示例渲染成功当成模板已经解耦。保持公共目录、账号安装与 OMP 边界。

**Tech Stack:** 现有 YAML/Python validator + TypeScript/React/Vite 公共包；TDD 和 ego-browser 页面检查。

## 用户裁定与工作关卡

用户于 2026-10-07 明确：模板是一套内容与代码框架，包含 SKILL.md、示例、辅助文件；模板分类沿用七类；设计系统核心 manifest.json + DESIGN.md + tokens.css；模板与风格解耦。随后要求“按照这个方向和决定来实施”。本裁定修订先前冻结定义中的相关内容，不批准单项许可/使用状态或发布。

当前 repo `/Users/howiez/Downloads/awesome-agent-ecosystem`、main、基线 ad3ec20，启动时工作区干净；复用当前目录，myApps 不修改，不创建 worktree。主会话协调/正本数据/最终审核，Luna 各自独占文件范围。运行中的 3001 预览只在确认归属后重启；3000 不触碰。

## 公共字段（最小数据扩展）

非适用类别省略可选字段，保留 schema_version=3 的旧记录读取；新增记录和本次七条模板使用以下 profile。未知文件不得伪造为已存在。

- `template`: `{files: [{role: instructions/framework/example/support, path, url}], style: {policy: external-design-system, upstream_status: independent/mixed/unknown, note}}`。文件 path 相对上游仓库，固定 url/ref 与该资源证据对应；示例内的视觉样式只作示范，不属于框架身份。`mixed` 为上游待拆分候选，不能标为模板已解耦/usable。
- `design_system`: `{files: [{role: manifest/rules/tokens-css/example/support, path, url}]}`。三个核心角色可查明则登记；单文档参考可以不完整，仍明确缺口；不能以文件名或仓库 owner 推导许可和作者。

不增加模板绑定 design_system_id、主题变体资源身份、安装版本体系或样式执行器。选择/应用设计系统留在宿主的已有应用能力，本目录只提供独立浏览和真实文件入口。

## Task 1: 固定上游审计（Luna readonly）

Files: `docs/template-decoupling-audit.md`, `docs/evidence/2026-10-07-template-decoupling-audit.json`。
1. 从实际归档读取七条资源的 instructions/framework/example/support；检查约束、seed 与样式耦合。
2. 114 个入口按内容核对框架、风格衍生与任务方法，输出可复核的清单，不把114当模板种类/独立资产数。
3. 检查上游设计系统核心三文件和 manifest 映射，不推导可用或许可证。

## Task 2: 契约与校验（Luna）

Files: `src/contracts.ts`, `scripts/validate.py`, `scripts/build.py`, `tests/test_template_profiles.py`, `tests/template-profiles.test.ts`。
1. 写 profile 正确/角色混用/风格绑定/缺文件/usable 耦合模板/设计系统三核心门槛测试并观察失败。
2. 实现最小字段校验，可接受旧候选记录没有 profile；profile 与类别相符，固定引用、路径和角色检查与原规则共用。
3. usable 模板要求 framework 与 instructions/example/support 文件及 independent 上游边界；usable design-systems 要三核心，不影响普通 Skill 等门槛。
4. 类型与完整 JSON/兼容 site-data 投影保留 profile，README 按分类正本说明框架和独立系统，不复制定义。
5. 不碰 data/UI，不构建共享产物、不提交。

## Task 3: 公共 UI（Luna）

Files: `src/ui/**`, `tests/ui.test.ts`。
1. 测试框架入口与示例分开展示，待拆分上游不显示为已解耦；设计系统核心三文件展示；不出现绑定风格的假状态。
2. 读取 profile 展示文件角色及来源；模板主区优先框架/操作指南，预览命名为参考示例；明确风格由独立设计系统提供。
3. 列表可区别模板框架与视觉系统，不生成主题变体身份；既有类别导航/搜索/详情/宿主接口保持。
4. 不碰数据/契约/生成器，不构建共享产物、不提交。

## Task 4: 正本和目录重整（root）

Files: `data/categories.yaml`, `data/resources.yaml`, `data/sources.yaml`（如真实新增引用需覆盖）, `docs/architecture.md`, `CONTRIBUTING.md`, `MAINTENANCE.md`。
1. 修订定义、模板身份与风格独立、设计系统核心文件门槛；历史冻结记录不抹除，明确最新裁定。
2. 将真实审计文件角色应用当前模板/系统；实际框架不足或耦合保持 candidate/reference，不能仅改名声称解耦实现。
3. 路径与作者/许可/实测不自动晋级。框架用途差异保留，只有风格不同的重复不新增模板。

## Task 5: 集成与验收（root 串行）

1. 全部 Python/Node 回归、typecheck、生成一致性、公共包与生产站点构建、打包宿主检查。
2. ego-browser 检查真实模板和系统详情、文件入口、示例独立标记、窄屏与原有导航；核实实际最终构建。
3. 审核新增/改类数量和所有证据，不以数量增长代表正确分类。
4. 仅提交本任务文件到本地 main，不 push/部署。

## 完成判据

- 分类正本与公共类型/校验/UI 对齐用户四项裁定。
- 真实框架、指引、示例和辅助文件明确分工，上游混合状态不冒充独立模板。
- 设计系统的三个核心文件独立可见，可缺的参考资料明确标出缺口。
- 无按主题重复新增模板身份，无自动授予许可、安装或实测状态。
- 适用检查与实际页面通过，运行文档和数据对账。

## 目录接入与身份调整（实施裁决）

- 共用 Deck 框架新增 `opendesign.html-ppt`，原 `opendesign.html-ppt-pitch-deck` ID 保留并按募资内容配方归 Skill。
- Motion Frames、Docs Page、Social Carousel、Device Showcase 均只有方法与成品例，缺少独立起始框架/辅助代码，保留 ID 改归任务 Skill。后续找到独立框架再按证据登记，不把当前分类修改叫上游代码改造。
- Web Prototype/Live Dashboard 的 seed+references、HTML PPT 主框架已定位；上游仍有主题/视觉签名约束，明确 mixed/待拆分，继续候选。
- 152 套上游设计系统三核心文件均存在，保留既有 Agentic ID，新增其余151套独立候选。此处是人工审核公开目录元数据接入，不批准版权、品牌授权、运行或安装。原始正文和媒体不转存。
- 所有来源引用使用固定上游提交，扩展 source scope 覆盖完整已接入设计系统和共享 HTML PPT 框架；旧803条发现队列不变。本轮没有完成它们的逐条语义迁移，不以此冒充所有来源已收录。

## 本轮运行句柄

- 本轮唯一 ego-browser TaskSpace：162，页面 p1。不要恢复已关闭的阶段 2 Space 160。
- localhost:3001 原进程归属已核对为本独立项目，更新生产构建后已重启；3000 不触碰。

## 完成记录

本轮已完成定义、公共类型/校验、角色展示、实际目录重整和独立设计系统接入。验收正本：[acceptance.md](../evidence/template-decoupling/acceptance.md)。72 Python、38 Node、typecheck、生产构建及真实打包宿主通过；最终浏览器确认框架文件/示例独立、设计系统三核心/真实tokens预览、七类筛选与390px布局。

上游样式耦合仍明确为 mixed 候选，代码未被目录改造；未宣称172条资产已经可用。完整历史发现队列和其他框架/Skill 的语义迁移仍需后续按具体证据处理。本次提交仅到本地 main，公开发布另行授权。
