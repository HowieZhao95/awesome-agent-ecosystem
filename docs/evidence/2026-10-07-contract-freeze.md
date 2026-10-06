# 2026-10-07 阶段 1 契约冻结证据

## 审批记录

- 用户批准原句：**“批准阶段 1 契约冻结”**。
- 审批日期：2026-10-07（客户端日期）。
- 审核基线：`16f06217e4d2fb1fe06c4d438d2391fc6dc4ccbf`（本次文档更新开始前的 `main` HEAD）。
- 审批对象：阶段 1 分类定义、公共元数据契约、来源策略和代表性映射定义。
- 审批不包含：逐资源许可、逐资源运行验证、`usable` 晋级、发布、推送或阶段 2。

## 正本与职责

- [`data/categories.yaml`](../../data/categories.yaml)：分类与维度的唯一正本。
- [`data/sources.yaml`](../../data/sources.yaml)：来源身份、来源角色、跟踪范围和维护策略的唯一正本。
- [`data/resources.yaml`](../../data/resources.yaml)：逐资源的身份、出处、许可、兼容、预览、组件及审核证据的唯一正本。
- [`docs/architecture.md`](../architecture.md)：公共元数据契约、收录门槛、更新规则及 ThusDesign 接入边界。

目录级 `meta.review` 表示阶段 1 契约审核；每条资源的 `review`、`lifecycle` 和 `verification` 独立生效。契约批准不构成资源许可审查、实测、`usable` 审批或发布。

## 六项阶段 1 交付与证据

1. **分类规范**：分类正本包含五主类、模板七子类、提示词的图片/视频/原则三子类，以及独立的领域、格式、文件约定和插件组件类型。类别与子类从该正本读取，分类 `review_status=approved`。
2. **公共元数据规范**：架构“公共元数据契约”明确 ID、用途、来源、作者、发布者、许可、具体上游引用、预览、兼容条件、实测宿主及验证状态；资源正本包含对应结构。未知值显式标注，宿主实测与声明分开。
3. **来源登记**：18 个来源区分内容上游、发现、分发及规范角色，逐项记录范围、基线和维护方法。OpenDesign 的路径数组覆盖实际资源、manifest、seed、示例、预览证据及许可相关路径；已有内容、OpenDesign、Remotion 均在登记范围。
4. **收录规则**：架构“收录规则”定义原创/适配/精选，以及参考/候选/可使用门槛；规范批准不代替单项资源许可与实测审核。41 项既有测试验证许可、审批和实测不足时不能标 usable。
5. **更新规则**：架构“身份、版本与更新规则”明确稳定身份、版本引用、重复、下架、更名和内容变化；Skill 安装复用只读指针和重新安装，不引入新版本或安装内核。
6. **代表性映射样例**：20 条资源覆盖 OpenDesign 模板/设计系统/Skill、Remotion Skills、图片/视频提示词、原则参考及组合插件；插件逐项列出组件与提供方式。旧 awesome 目录通过 Linear DESIGN.md 样例追溯到具体内容文件，目录/品牌不冒充内容作者。

正本分工、原始内容上游追溯、ThusDesign 私人数据与安装记录边界、OMP 单一执行内核，均见架构“正本与职责”和“ThusDesign 接入约定”；本轮未修改 myApps 产品代码。

## 三处审核修正

- **[P1] OpenDesign 跟踪范围**：`sources.yaml` 的 scope 使用仓库相对路径数组，覆盖当前 OpenDesign 资源实际 `upstream.path`、相关示例 manifest/seed/example/assets/references、设计系统 manifest/tokens/CSS/previews/source、craft 文档和根级相关文件。跟踪策略明确只覆盖选定路径，不表示收录或执行 OpenDesign 内核。
- **[P1] Skill 安装版本边界**：公共目录及上游引用可以锁定版本；Skill 安装继续使用现有只读指针及重新安装机制，不引入安装版本体系或新安装内核。详见架构文档“ThusDesign 接入约定”。
- **[P2] 宿主实测可识别性**：每项 `verification.tested_hosts` 是稳定宿主 ID 数组，空数组表示尚无宿主实测；`compatibility.hosts` 仍是声明。可用投影按具体目标宿主判断，不建立复杂兼容矩阵。

## 目录状态与既有验收证据

阶段 1 数据基线为 20 条资源、18 个来源，其中 17 个 candidate、3 个 reference、0 个 usable。所有资源各自保持 `review.status=pending`，`tested_hosts=[]`；目录版本保持 `0.1.0-draft`，没有发布语义变化。

既有 [`2026-10-07-review-fixes-tests.log`](2026-10-07-review-fixes-tests.log) 记录 41 项测试通过、`scripts/validate.py` 通过及 `git diff --check` 通过；[`2026-10-07-review-fixes-validation.json`](2026-10-07-review-fixes-validation.json) 记录 20 条资源、18 个来源、验证状态及生成文件 SHA；[`2026-10-07-review-fixes-render-smoke.json`](2026-10-07-review-fixes-render-smoke.json) 记录 20 张卡的元数据渲染烟测，并明确其不是视觉或资源运行验收。这些是既有证据，保留其原始时间与范围。

本次冻结后的新旧校验与生成一致性已通过：见 [`2026-10-07-freeze-validation.json`](2026-10-07-freeze-validation.json)。资源子树与审核基线完全一致，旧 803 条发现记录原始字节保持，生成文件二次生成一致。阶段 1 契约冻结不改变资源逐项状态。未发布、未推送、未进入阶段 2；myApps 中历史 raw-main consumer 迁移是后续接入工作。
