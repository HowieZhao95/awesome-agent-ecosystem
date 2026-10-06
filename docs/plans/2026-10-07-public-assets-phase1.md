# Public Assets Phase 1 Plan

**Goal:** 建立公共资产的分类、元数据、来源、收录与更新正本，以真实样例检验定义，交用户审核。

**Architecture:** `data/categories.yaml` 管分类与维度，`data/sources.yaml` 管来源与维护，`data/resources.yaml` 管具体记录与证据，`docs/architecture.md` 管职责和契约。保留旧目录为发现队列；生成文件只读新正本。原内容在上游，账户安装与私人资产在 ThusDesign 数据库。

**Tech Stack:** YAML、Markdown、现有 Python/PyYAML 构建与 unittest。

## 授权与关卡

- 工作位置：awesome-agent-ecosystem 现有干净 `main` 检出；不使用 worktree，不改 myApps。
- 本阶段仅定义、来源登记、样例与必要的数据校验/生成接线，不实现站点账户、安装或 Agent runtime。
- 历史记录：用户先认可五类定义与总体边界，随后提出 P1/P1/P2 三处契约修正；修正后的阶段 1 契约已于 2026-10-07 获用户批准并冻结（见文末冻结记录）。分类 `review_status` 保持 approved；目录级 `meta.review` 记录契约审核，逐资源 `review` 仍独立保持 pending，不代表资源实测或可使用批准。
- 不 push、不发 release、不替用户审核或合并。提交前检查所有改动与暂存状态，按适用授权执行。
- 来源查证、代码检查可由 GPT-6 Luna 分工；写文件前划分范围。主会话终审。

## 步骤与验收

1. 核对本地与公开上游；保留旧 v2 数据全部字节，作为发现队列，不继承旧 manual 为运行验证。
2. 定义五主类、模板七子类、提示词三子类；分别定义领域、文件格式、文件约定、插件组件。
3. 定义完整记录契约、未知值、身份/版本/重复/下架规则；登记内容、发现和规范来源的独立角色与更新范围。
4. 查证 OpenDesign 固定版本、Remotion 官方 Skills、ThusDesign 已有内容与原始提示词出处；记录精确路径/selector，不复制原内容或私人文件。
5. 收录代表性映射；包括混合插件的组件与依赖区分、格式相同但用途不同、单文件规范与完整设计系统区分。
6. 必要的脚本行为先写失败测试：引用完整性、未知许可阻断 usable、精确上游引用、组件和分类边界、旧扫描不写正本、生成可重复。
7. 运行完整既有测试、规范校验、生成与幂等检查，审查差异及链接。机器检查仅证明结构和规则，不代表运行兼容或用户审核。
8. 出示分类、来源策略和代表样例给用户审核；阶段 1 冻结审批已完成，发布/接入仍属后续阶段。

## 当前证据

- 初始本地 HEAD：`f8da353`；初始工作区与暂存为空。
- 公开仓库 main 页面可读取；本轮 `gh` API TLS 超时，不能据此断言远端分支/PR 或发布状态。
- 实际验证与审核记录在工作完成后补充，禁止预填 PASS。

## 2026-10-07 验收记录

- 新正本：五主类、模板七子类、提示词三子类，领域/文件格式/文件约定/组件分开；公共契约包含身份、用途、作者/发布者、许可、引用、预览、兼容、验证、状态、收录与更新规则。
- 初始验收时为 17 个来源、19 个代表记录（17 candidate、2 reference）；2026-10-07 阶段1补漏后为 18 个来源、20 个代表记录（17 candidate、3 reference、0 usable）。目录和资源 review 全部 pending；作者/许可未明的记录没有伪造权利或实测状态。
- OpenDesign 模板只索引内容，不搬其 atom/pipeline 包装；三维样例为 CSS 设备展示，非 DCC；原则样例为特定仓库参考；Remotion 技能非 MG 工程模板。
- 组合插件记录覆盖 td-drama-production 的 7 Skills + 宿主模块 + 引用 CLI，以及 @thusdesign/cli 的 CLI + stdio MCP，逐项有路径、选择器和提供方式。
- Remotion 浏览器查证取得固定 commit `473352613039e718e46655a26df224851e84c4aa`；文件声明版本 `4.0.533` 未被当成运行兼容；许可仍 unknown。见 `docs/evidence/2026-10-07-remotion-source-check.json`。
- OpenDesign 各路径逐项在冻结归档查到；ThusDesign 主记录及 td-drama 组件路径在固定产品 commit 查到。没有读取真实 PGlite、生成模型、安装插件或改变私人资料。
- 旧 803 条记录与 `f8da353:data/resources.yaml` 字节一致；发现导入、stars、link-check 已改默认目标，不写新正本。
- TDD 红绿覆盖分类/来源角色、未知引用、身份重复、作者证据、适配关系、组件、usable 门槛、生成失败不写文件、幂等、README 锚点与混合插件投影。最终 35 tests PASS，完整日志 `docs/evidence/2026-10-07-tests.log`。
- 新旧校验 PASS；真实 build 输出 19 记录；第二次生成字节一致，证据见 `docs/evidence/2026-10-07-data-validation.json`。
- ego-browser 已打开实际本地目录页，显示 19 资源 / 17 候选 / 0 可使用 / 19 待审核 / 0 已实测；未实现新站点、账号或安装闭环。
- 2026-10-07 补漏：新增 `voltagent.linear-design-reference`，以 `data/discovery/legacy-v2.yaml#categories[id=design-docs].entries[name=linear.app DESIGN.md]` 追溯发现项，以 VoltAgent 实际 `design-md/linear.app/DESIGN.md` 文件作为内容上游。读取 main 文件但未锁定 SHA；只索引元数据，不复制正文，不推断作者、许可、官方身份或兼容性；历史 manual/stars 不继承为实测。修正 quiet-product 的发布者证据与格式为实际 TypeScript preset 路径，不再称其为 DESIGN.md，也不再声称源文件未查明。
- 补漏验收：新记录与旧发现条目精确匹配，发现角色与实际内容角色分开；Quiet Product 格式/证据修正经核对。新正本校验 PASS，20 记录生成通过且二次生成字节一致，旧 803 条原始字节仍保持。详见 `docs/evidence/2026-10-07-discovery-lineage-check.json`。未改脚本或客户端逻辑，未扩大重复测试；此前 35 项脚本测试与浏览器检查保留其原验收范围。

## 冻结前关卡记录（历史）

- 当时仍待用户批准契约冻结；2026-10-07 用户现已明确批准，阶段 1 契约完成。具体依据和边界见下方冻结记录。
- 两条原始 X 线索未独立核验、Remotion 许可未知、各候选尚未完成使用验证，均为逐项资源后续审核事项，不是阶段 1 契约冻结的阻断项。
- 未 push、发布或修改既有远端 PR；myApps 的 raw-main 历史消费者尚未迁移。这些分别属于发布/接入后续工作，不是阶段 1 冻结剩余项。

## 2026-10-07 用户审核修正（冻结前历史状态）

- [P1] OpenDesign tracking.scope 改相对路径数组；覆盖真实官方 examples 内容和 manifest、seed、example、素材/引用、设计系统及许可路径。另核对归档中存在的 `apps/web/public/community-templates/social-carousel.jpg` 并纳入跟踪，防预览证据漏跟踪。
- [P1] 公共目录/上游引用锁版本与 Skill 安装解耦。Skill 仍用既有只读指针和重新安装，无安装版本、物化/分发快照、扫描、fork 或新的安装内核；依据产品 v4 收敛及当前指针安装代码。
- [P2] 新增 verification.tested_hosts 稳定宿主 ID 数组；所有 20 条当前资源均为 []，不伪造实测。usable_for_hosts 为已验证记录派生的公开投影，只在具体 host 匹配且原门槛全满足时可用。仅测 OpenDesign 不得标 ThusDesign 可用，当前已有 Skill 安装裁定不被改写。
- 只改公共数据/契约与必要校验/生成投影；不改 myApps 产品源码、DB 或安装机制，不进入阶段 2。
- 修正验收：先红后绿，完整 41 tests PASS，日志 `docs/evidence/2026-10-07-review-fixes-tests.log`。涵盖实际 OpenDesign 路径/预览证据与 scope 覆盖、tested_hosts 类型/唯一性/验证层级、仅 OpenDesign 实测时 ThusDesign 两宿主均不可用及生成投影。
- 新旧校验 PASS，20 条记录/18 来源生成通过，二次生成字节一致；旧发现队列 803 条原始字节保持。证据 `docs/evidence/2026-10-07-review-fixes-validation.json`。实际 20 条 tested_hosts 全为空且未增加任何 usable 标记。
- 使用实际页面脚本与生成数据执行 Node VM 元数据渲染烟测：20 张卡、0 已实测/可用宿主，无泛化可用声明。此检查不是浏览器视觉验收或资源运行验证；见 `docs/evidence/2026-10-07-review-fixes-render-smoke.json`。
- 分类认可已记录；三处修正准备复核，未代替用户批准契约冻结，未进入阶段 2，未 push/release。

## 2026-10-07 阶段 1 契约冻结

用户明确批准：“批准阶段 1 契约冻结”。该审批完成阶段 1 的分类、公共元数据契约、来源策略和映射定义审核；不批准任何单项资源的许可、运行实测、可用状态，也不授权发布或推送。

截至本次冻结，目录为 20 条资源、18 个来源：17 个 candidate、3 个 reference、0 个 usable。逐资源 review 仍全部 pending，`tested_hosts` 仍全部为空，`catalog_version` 保持 `0.1.0-draft`。因此目录契约已冻结，资源审核和发布状态保持各自独立。

P1/P1/P2 修正和全部六项阶段 1 交付由 [冻结证据](../evidence/2026-10-07-contract-freeze.md) 记录。冻结后的新旧校验、真实生成与二次生成一致性已通过，资源子树与审核基线相同；新证据为 `docs/evidence/2026-10-07-freeze-validation.json`。既有 41 项测试和渲染烟测仍保留各自时间和范围，不扩大为资源运行验证。未进入阶段 2；未发布、未推送；myApps 历史 raw-main consumer 迁移留待后续接入。
