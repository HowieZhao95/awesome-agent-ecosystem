# 公共 Agent 资产：阶段 1 契约

状态：**draft，分类与总体边界已获认可，契约修正后待冻结审核**。本阶段建立定义、来源与映射样例；未实现账户登录、安装、站点迁移或运行时接入。机器校验通过不能代替内容审核或真实运行验证。

## 正本与职责

| 文件 | 唯一真相 |
| --- | --- |
| `data/categories.yaml` | 五主类、子类、归类规则、领域、文件格式、文件约定与插件组件类型 |
| `data/sources.yaml` | 来源身份、角色、跟踪范围、更新方式与维护状态 |
| `data/resources.yaml` | 具体资源身份、出处、许可、兼容条件、预览、组件及审核证据 |
| 本文件 | 公共元数据契约、收录与更新规则、项目边界和接入约定 |

README 与 `site/data.js`、`site/catalog.json` 由正本生成。未来的类型枚举、筛选项和客户端目录也必须生成或读取正本，不能再手抄分类名单。生成文件不是另一个可编辑来源。

公共目录属于本开源项目；原始内容追溯上游，不因为被收录就复制、改署名或改变许可。ThusDesign 维护用户安装记录、私人资产、账号权限与使用状态。公共仓库不存用户 ID、安装记录、凭证、私人 AGENTS.md、KB 或全局/项目记忆。

`data/discovery/legacy-v2.yaml` 完整保留旧目录，并继续承接旧自动发现流程。旧 `source=official/vendor/community`、`platform`、`manual`、stars 和描述只是历史线索，不能推导出原创作者、内容许可、安装成功或新分类。旧队列不是公共资产正本；进入正本必须追溯具体资源并按新契约人工审核。保留旧记录不代表把旧分类沿用为主类。

## 分类与维度

定义与标签直接见 [分类正本](../data/categories.yaml)。每条资源只有一个主类和一个适用子类；主类表达主要复用用途，domains 可多选。文件扩展名属于 formats，SKILL.md、AGENTS.md 等角色属于 conventions，运行依赖另记。插件的 components 描述它实际包含或声明的能力，dependencies 描述它需要的外部能力。

主类判断顺序是：具体插件分发单元 → 固定产物形态 → 完整设计系统 → 任务方法 → 图片/视频/原则文本。歧义必须写 `classification.rationale`，不能拿 custom 或 general 掩盖尚未查明的资源。上游栏目只作证据，不直接决定归类。一个插件及其可单独分发的 Skill 可以分别登记，但通过组件引用关联；不能把相同分发单元重复收录。单组件 MCP/CLI 要有独立安装、启用、版本或分发身份才建立插件资源；仅随父插件提供的能力只记组件，外部要求只记依赖。组件不另加进资源计数，已登记组件通过 resource_id 关联。general 仅在没有具体领域时使用，与具体领域互斥。

## 公共元数据契约

版本：`schema_version: 3`。日期用带引号的 ISO 8601 日期或时间；未知值用 `null` 并写原因。`[]` 表示已明确为空，不能用来隐藏未知。所有字段即使未知也保留结构；未知作者、许可、版本和验证必须可见。

资源记录字段如下。路径为上游仓库相对路径，禁止纳入本机绝对路径、token、环境变量值或个人数据。

| 字段 | 定义与约束 |
| --- | --- |
| `id` | 不随分类、展示名、来源迁移或版本变化的稳定 ASCII 标识，如 `opendesign.web-prototype`；在目录中唯一，删除后也不复用 |
| `title`, `summary`, `purpose` | 展示名称、客观简介、用户可复用它完成什么；名称可以重复，身份不能按标题推导 |
| `classification` | `category`、适用的 `subtype`（无子类用 null）、`domains`、实际内容 `formats`、`conventions` 和 `rationale`；取值来自分类正本 |
| `provenance.relation` | `original` 原创、`adapted` 适配、`curated` 精选；描述收录对象与上游的关系，不描述作者知名度或官方身份 |
| `provenance.content_source` | sources 中具有 `content-upstream` 角色的 ID；指向真正承载该资源的上游，而不是发现目录 |
| `provenance.discovered_via` | sources 中具有 `discovery-channel` 角色的 ID 数组，可为空；不自动成为作者或版权来源 |
| `provenance.upstream` | `kind`（git/web/product/catalog）、`url`、`path`（可为 null）、`selector`（具体条目/命名 ID，可为 null）、`ref: {kind, value}`；可复现资源必须锁定 commit、release、内容 hash 或不可变条目 |
| `provenance.derives_from`, `changes` | 适配的原资源 ID/精确出处及实质改动说明；原样精选用空 derives_from 和 null changes，不能把翻译或裁剪称为原创 |
| `authors` | `{status: known/unknown, identities: [{name, url}], evidence: [出处]}`；仓库 owner、提交者、图片人物都不能自动视为内容作者 |
| `publisher` | 同一 identity 结构，指该分发单元的发布者；公共目录的策展者记录在 meta，不冒充上游发布者 |
| `license` | `{status: verified/unknown, expression, scope, evidence, redistribution: allowed/blocked/unknown}`；只对证据覆盖的具体内容生效，字体、图片和第三方组件分别说明，不继承本目录 CC0 |
| `distribution` | 分发渠道数组：`{kind, channel_source, url}`；渠道可为 repository、marketplace、npm、product-bundled、upstream-link。有登记来源时引用具有 distribution-channel 角色的 ID；内容出处仍由 upstream 描述，发现途径由 discovered_via 描述 |
| `previews` | `{kind, url, status: reference/verified, evidence}` 数组；示例 HTML/媒体是 reference，只有检查实际可预览且写证据才是 verified；无预览写 [] 并在 verification.limits 说明 |
| `compatibility` | `hosts` 声明预期目标宿主，不代表已验证；`runtimes: [{name, version, status: declared/verified/unknown}]`；`dependencies: [{kind, name, version, source_id}]`；`constraints` 列出必要条件。null version 不代表兼容任何版本 |
| `components` | 仅 plugins 非空：`{id, type, resource_id, upstream, subtype, delivery}`；type 来自分类正本，resource_id 可引用已登记组件或为 null，此时仍须给精确 upstream；delivery=contained/referenced/host-provided，避免把宿主模块说成插件携带的内容 |
| `lifecycle` | `{state: reference/candidate/usable/withdrawn, reason, replacement_id}`；参考资料仅供阅读，candidate 待审核/适配/验证，usable 满足下面全部门槛，withdrawn 保留身份与原因 |
| `review` | `{status: pending/approved/rejected, by, at, evidence}`；by/at 在 pending 时为 null，不冒充用户审批 |
| `verification` | `{level: unverified/source-inspected/usage-tested, tested_hosts: [稳定宿主 ID], checked_at, by, evidence, limits}`；source-inspected 仅证明文件/声明查过；usage-tested 是总体概览，tested_hosts 明确在哪些宿主测过。实测必须写版本、环境、操作和结果，不能从兼容声明、README、热度或人工收录推导 |

`verification.evidence` 为 `{locator, claim}` 数组。locator 可以是精确公开 URL、同仓文件路径、`product-source:<commit>:<path>#<selector>` 等审计定位符；受限产品源码证据必须在 limits 明示不可公开访问，不能伪装公开下载入口。阶段 1 不复制私有产品内容；许可未知的记录保持 reference/candidate。

`verification.tested_hosts` 是可由程序精确匹配的 ASCII 宿主 ID 数组，例如 `opendesign`、`thusdesign-desktop`、`thusdesign-web`。显示名称或 `compatibility.hosts` 中的预期宿主不能填入此字段。无实测时明确为 `[]`，并保持 unverified/source-inspected；usage-tested 至少记录一个实测宿主，证据须能对应到该宿主与测试环境。Web 与 Desktop 分开记录，不自动互相扩展；跨宿主迁移需重新验证，不建设复杂兼容矩阵。

目标宿主的可用标记及安装入口按 **资源满足 usable 的全部门槛，并且目标宿主 ID 属于 tested_hosts** 判断。公开目录可投影符合门槛的 `usable_for_hosts`，消费者不能把全局 lifecycle=usable 或 usage-tested 当作所有宿主可用。只在 OpenDesign 测过的对象可标为“可使用于 opendesign”，不得因此显示为 ThusDesign 可用。阶段 1 没有安装入口；本条约束后续接入的展示与入口判断，不实现安装或运行内核。

该判断用于本公共目录的目标宿主可用投影及后续接入，不替换现有 Skill 商店的安装/重新安装裁定，也不追溯改写、删除或阻断既有安装指针。

tested_hosts 描述该资源记录对应上游基线的验证结果，不保证 Skill 安装指针未来指向的变化内容也已验证。内容变化仍按既有人工审查和重新安装机制处理，本字段不引入安装版本跟踪、分发快照或自动扫描。

upstream 的 url 必须指向具体文件、目录或不可变条目。git 记录必须有相对 path；Web/产品页面含多条目时必须有 selector；仓库首页本身、目录站搜索页不能作为唯一的具体出处。git ref.kind=commit 需完整 40 位 SHA；移动分支不能作为发布锁定引用。找不到公开分发入口时可以登记产品证据，但必须标为 candidate 并说明缺口。

`meta.catalog_version` 是目录版本，upstream.ref 是资源内容版本，两者独立。schema 版本变化不等于资源内容更新。本次 `0.1.0-draft` 不是已发布版本；`meta.review.status=pending` 禁止生成已审核声明。

## 来源登记与维护

一项来源可以具有多个角色，但每次引用必须明确用途。来源角色为 content-upstream、discovery-channel、distribution-channel 和 specification：内容上游负责内容；发现渠道帮助找到条目；分发渠道负责提供下载或安装入口；规范来源说明协议/格式，不提供该资源作者、许可或安装依赖。GitHub 或市场可能兼有发现与分发角色，两个字段仍分别表达实际行为。规范来源同样可以是需要关注变更的来源，具体范围见 sources 的 tracking。运行时依赖可以引用相应来源以便追踪，但 dependencies 仍是单独字段。

来源记录包括 `id/name/url/roles/access`，以及 `tracking` 的 scope、exclude、baseline、cadence、method、promotion、last_checked 和 limitations。source ID 不含需要更新的版本，版本放 baseline。access 为 public/restricted/unknown；未知入口 url 可为 null，但必须同时 access=unknown 且 limitations 写原因，不能用别的网站首页占位。scope 是实际跟踪目录/条目，baseline 是此次查证基线，不能把“仓库存在”说成“全仓收录完成”。代码仓库需要按路径比较时，scope 使用仓库相对路径数组，支持目录 `/**`；内容入口、manifest、seed、示例和许可证据的实际路径均须被覆盖，不能只跟踪另一个副本目录。其他发现/规范来源可保留可读的范围说明。所有自动更新只产生发现结果或审查提案，不静默晋级为 usable。

Sources 中每个已知上游必须说明：更新时比较哪些文件，如何锁定引用，谁审核分类/许可/兼容变化，无法获取时怎样保留原证据。登记 weekly/manual 等节奏只是维护策略；只有现有 weekly-sync 旧发现脚本已接线，新上游持续监控未实现，不宣称已自动运行。

## 收录规则

1. **原创**：可证明本团队创作并获公共分发授权；发布者是 ThusDesign 不足以证明作者也是 ThusDesign。授权和作者不明则保持候选。
2. **适配**：保留原作者和许可，登记 derives_from、上游固定引用、改动说明及适配发布者。翻译、格式转换、宿主工具替换或裁剪均属适配。
3. **精选**：原样索引第三方具体资源，保留原身份、作者、发布者和条目许可。目录中的“官方”最多说明已证实的发布者关系，不能表示 ThusDesign 原创或全面背书。
4. **参考资料**：教程、规范、单一风格文档或只有展示结果的材料可以做 reference；规范/目录本身放 sources，不能为了凑资源数变成插件或 Skill。
5. **候选**：已找到具体对象但作者/许可/可复现内容/适配/验证/审批存在缺口。旧队列和热度只能帮助发现，不是准入门槛的替代品。
6. **可使用**：必须有明确可复现内容、适用许可证据、source-inspected 以上证据、面向具体宿主/版本的 usage-tested 证据、approved 审核且 no unresolved blocker。设计系统须达到 minimum_profile，模板须有可复用结构，插件须解释全部组件及其提供方式。

原生上游可使用与 ThusDesign 可使用分别限定 tested_hosts 和证据；上游测试成功不能声称 ThusDesign 接入成功。文本原则的 usage-tested 可以是经审核后在具体 Agent/项目中应用并验证导引，不能只检查文件名。许可 unknown 或 redistribution unknown 禁止被自动安装或转存；reference 的链接不代表授予复制权限。

## 身份、版本与更新规则

- **身份**：ID 在首次登记时确定，以资源分发单元为边界。同一个仓库的多个 Skill/模板可有不同 ID，不能按仓库首页合并。命名变更只改 title；路径迁移更新 locator 并保留历史证据。
- **锁定**：发布目录锁定具体 upstream ref。tag 要同时保留解析后的 commit 证据；branch/未知引用只能进候选。上游变化先比较差异，审核后替换 ref，不把 main 隐式漂移当更新。
- **重复**：相同内容上游 + 具体 path/selector + 同一分发单元视为同一身份；分发镜像和市场链接追加 distribution。相同内容 hash 是线索，不能抹去不同作者/许可。重命名不新建 ID，名称相同不自动合并。组合插件通过 resource_id 引用独立组件，不复制成第二份资源内容。
- **适配分支**：实质改变内容且独立维护的适配是新资源 ID，derives_from 回指原对象；仅改变目录标签、发现渠道或展示名不是新资源。
- **内容变更**：作者/许可/入口/依赖/组件/任务语义变化须重新审核与相应 usage-tested；原有批准不自动继承。只改描述拼写也需记录目录 diff，但不伪造新的内容版本。
- **下架**：保留 ID、固定引用和 reason；设置 withdrawn，给 replacement_id（有则）并停止新的安装推荐。暂时网络失败只记录 unknown/维护提示，不自动删除或宣称恶意。既有用户副本或安装记录由 ThusDesign 处理，公共目录无权删除。
- **更名与回归**：恢复下架资源保留原 ID，重新审核与验证；旧名称可保留在变更证据。任何用户安装记录不随目录改名自动重建。
- **更新失败**：不得拿不完整抓取覆盖已审查记录；保留旧基线、记录失败并等待重试/人工查证。所有自动内容提案进入 PR，人工终审后才能发布。

## ThusDesign 接入约定

ThusDesign 的公共目录投影只消费**经审核的发布版本**，锁定 release/tag 及解析 commit 或校验值；不能动态拉取 main 或直接消费 draft。来源 ID、资源 ID、schema_version 及目录中的上游引用属于公共来源信息，目录锁定引用不等于用户安装版本体系，不能把目录版本当作内容包版本。

**Skill 安装保持现有产品契约：只读指针，更新靠用户重新安装，无安装版本体系。** 产品继续使用既有 listing/安装指针及 installedAt 等字段，公共资源 ID 可用于目录映射与来源投影；不要求 Skill 安装记录保存“选定内容版本”，不增加版本表、物化内容、分发快照、自动扫描/升级、fork 或第二套安装内核。公共目录和上游引用可以锁定版本，实际 Skill 内容获取、缓存与重新安装仍按既有 Skill 机制执行。依据为 myApps 的 `docs/plans/2026-09-12-skill-store-target-model-plan.md` §0 v4 收敛及当前 `packages/skill-catalog/store-listing-kernel.ts` 的指针安装/重新安装裁定。

其他类型的添加、实例化和应用记录留在 ThusDesign 数据库，按各自现有产品契约确定；阶段 1 不统一重设计安装表、版本状态机或运行内核。

当前 myApps 的设计风格目录仍引用此仓库 main 的旧 `site/data.js`；它是历史接入，尚未迁移，不符合新的发布约定。此阶段不改 myApps，也不伪造 release；发布获批后，后续接入必须换为固定发布版本并移除旧 raw-main 读取。旧 `design-docs` 栏目 ID 不作为新契约的兼容别名，避免形成第二套分类。

账号中的“已添加”与设备上的“可用”分别记录。提示词副本、模板实例、项目设计系统、原则应用和插件运行条件由产品按其语义处理；不强迫写入同一 Skill 表。MCP 凭证与本地配置只在桌面，私人记忆永不云同步。OMP 负责 Agent、Skill 和 MCP 的执行内核；本目录不实现插件运行时、权限引擎或第二套安装内核。

## 审核与发布

目录维护者先检查结构、引用与证据，再由用户审核分类、数据契约和来源策略。审批通过后才更新 meta.review 与对应记录 review，不批量把候选改成 usable。用户批准规范并不自动批准所有内容或运行兼容。

发布前必须运行测试、validate 和 build，并核对生成结果与源文件一致；版本固定引用与来源可访问范围须记录。发布动作另行授权。本阶段完成以用户审核为最终关卡；本地 draft、机器 PASS 和 Git 提交均不足以宣称完成。
