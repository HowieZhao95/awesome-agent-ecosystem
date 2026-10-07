# Complete Public Resource Directory Implementation Plan

**Goal:** 补齐统一商店的内容覆盖：GitHub旧目录777条逐条有浏览去向，26个平台保持来源角色；OpenDesign全量入口有内容分类和去向，不再只显示样例或仅补设计系统。

**Architecture:** 保留严格资源正本及审核门槛；添加读取历史发现队列的独立发现索引，用明确的 DiscoveryEntry 与 BrowseResource 投影供同一UI浏览。原始出处未知时使用null，不把目录站伪装成内容上游，不创造component path。已查明的OD框架/Skill直接登记，风格变体合并到框架来源清单，不创建风格模板身份。

**Tech Stack:** 现有Python/TS/React/Vite公共包，TDD，单工作区Luna并行独占文件范围，root串行生成构建与浏览器验收。

## 授权、范围和关卡

用户持续要求所有相关资源汇总，并在前轮要求按五类与模板风格解耦方向实施；本轮指出模板/Skills/提示词/插件仍少，并要求“考虑全面一点”。完成标准不能再缩成新增少量样例。

项目 `/Users/howiez/Downloads/awesome-agent-ecosystem`，main，基线96839f9，启动干净。myApps只读，不碰账户、真实DB、旧商店业务身份；不创建worktree、不push/部署。现有777条来自完整固定历史数据，网站、类型、筛选仍读正本/生成结果。严格公开资源与待核查发现记录有不同契约，不降低usable条件。

## 覆盖原则

1. 全777旧条目：每个唯一legacy key必须映射到统一浏览条目、已有资源、合并重复或来源档案；排除需明确理由，不静默丢掉。26个平台不计作可安装资产。
2. MCP/CLI并入插件展示，保留技术类型与历史分发线索；不编造manifest、包含关系或安装指令。源地址不具体时标待定位。
3. 旧prompt库/教程/合集为发现来源或参考入口，不能伪装成一条图片/视频/原则正文。可以在对应类别查看这些入口并区分内容种类；五类下没有硬塞新增主类。
4. 旧design-docs须按内容重映射（系统参考、Skill/CLI工具、规范来源、原则），不能只复制旧栏目名。
5. 全OD入口：审计114个design-template入口及163个skills入口。已查明框架按七类登记、复用相同框架保持一个ID；主题/视觉变体关联其框架或来源；方法指令归Skill，纯原则归prompt/principle；上游官方插件身份必须真实manifest，不能每个example文件夹当插件。
6. 同一内容上游/path/分发单位去重，不能按同仓库URL就合并几十个不同plugin；标题相同不同来源不强合并。所有matched关系留证。
7. 统一UI默认展示全部公共资源与发现线索；可按收录来源/核查状态筛选。发现线索详情提供原地址、旧记录和缺口，不能开放安装或传假Resource给宿主。
8. 搜索/筛选、分页、稳定ID详情、来源页、预览、窄屏/键盘/主题与失败状态在大目录上验证。

## 最小类型与接口

`Catalog.discovery?: {schema_version:1, source_id:string, input_sha256:string, entries:DiscoveryEntry[], platforms:DiscoveryPlatform[], coverage:...}`。

`DiscoveryEntry` 用独立字段 `{id,title,summary,classification:{category,subtype:null|string,domains,formats,conventions,rationale}, source_url, channel_source, legacy_keys, legacy:{...}, content_kind:asset|reference|collection|specification, expected_components:[], missing:[...]}`；没有已确认content_source/upstream/author/license/manifest，不能填假值。合并已有Resource时记录mapped_resource_id并从浏览列表去重。

公共浏览投影 `BrowseResource` 保留Resource共有展示字段，但 `provenance.content_source` 与 `upstream` 可null，添加 `directory_origin:catalog|discovery` 和 discovery元信息。此投影不写入资源正本，不替代安装/执行契约。宿主操作仍仅接收真实Resource。目录纯函数提供getBrowseResources/filterBrowseResources/getBrowseResource，原getResource/filterResources继续只处理严格资源。

## 分工与步骤

### Legacy index and coverage (Luna A)
Files: `scripts/discovery-index.py`, `scripts/discovery_index/**`, `tests/test_discovery_index.py`, `data/discovery/classification-overrides.yaml`, `docs/evidence/complete-directory/legacy*.json/log`。
- TDD输入777全覆盖、平台单列、MCP/CLI映射、prompt合集内容类型、design-docs覆盖、重复和源未知、既有ID匹配、确定性。
- 输出JSON索引/覆盖报告，只读原803队列与资源正本；不修改build.py/UI/types/data正本。
- 分类override只记录实际旧条目内容判断、理由和lineage，不伪造语义。

### Public browse contract and UI (Luna B)
Files: `src/contracts.ts`, `src/catalog.ts`, `src/ui/**`, `tests/catalog.test.ts`, `tests/ui.test.ts`, `tests/discovery-browse.test.ts`。
- 根据独立DiscoveryEntry类型生成BrowseResource，unknown upstream保持null；别用假catalog-source当内容上游。
- 默认统一浏览、来源/状态区分、线索地址与原始记录，合集/工具类型可识别；既有Resource+host语义不变。
- TDD完整index读取/组合筛选/去重/详情直开/缺口/不开放宿主操作；不构建共享产物、不碰生成器/YAML。

### OpenDesign complete intake (Luna C)
Files: `scripts/opendesign-inventory.py`, `tests/test_opendesign_inventory.py`, `docs/evidence/complete-directory/opendesign*.json/log`, `docs/opendesign-directory-coverage.md`。
- 固定tar读内容/文件/manifest，逐条输出114+163入口的分类、共用框架/风格关系、证据与候选proposal。
- 真正框架需要instructions/framework/example/support路径；缺口明确候选。所有已有OD IDs映射保持、重复目录副本内容hash查证；不能品牌外观产生模板ID。
- Proposal由root审核再合并，agent不写data正本、不复制原始正文/媒体。

### Root integration and acceptance
Files: `scripts/build.py`, `scripts/generate.mjs`, `data/resources.yaml`, `data/sources.yaml`, `docs/architecture.md`, `README`生成、维护/接入/贡献文档、CI、证据。
- 接线索引生成至site/catalog.json可选字段和共享包；README明确canonical与discovery数量，不把发现标为可用。
- 审核OD提案与覆盖每条去向，维护来源scope；保留原批准/使用/许可、不改私有机制。
- 全测试/校验/生成一致性/包与站点/实际宿主通过，真实页面验证777与全部OD条目可追溯，数量对账。
- 唯有全覆盖报告+实际页面都证明完成才汇报；本地提交，不发布。

## 完成验收

- 777旧条目逐条有target和reason；26来源入口可访问；没有无理由遗漏。
- 114 OD模板入口 +163 Skill入口全覆盖；风格不是模板，样例不是假框架，实际methods/content/reference可以浏览。
- 五类统一浏览的大目录与严格元数据边界保持；无自动批准、许可/实测晋级或假安装。
- 搜索筛选分页详情/来源直开、公共包消费与目录生成对账，实际页面可见，不只测试夹具证明。

## 完成记录

777旧入口与26平台来源、277个OD输入全覆盖。实际浏览1166条（367严格资源+799独立发现），60个别名不重复算卡片；25模板框架候选、272Skills、31提示词/参考、653插件/工具、185系统/参考。固定源195提案与新增记录一致，原172记录和旧803字节保留。

公开模块、来源与未知信息、搜索/筛选/分页/详情/alias/来源平台接线完成。最终Node50、Python90、typecheck、构建与包消费检查通过，真实页面的大目录和失败/恢复已检查。验收正本：[acceptance.md](../evidence/complete-directory/acceptance.md)。

本轮ego-browser Space168，p1；任务完成后关闭。3001为本项目最终生产预览，3000未动。不push/部署。
