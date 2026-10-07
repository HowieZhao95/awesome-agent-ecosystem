# Phase 2 Public Agent Store Implementation Plan

**Goal:** 交付独立可运行的开源五类资源商店、公共模块和基础来源工具；正式 ThusDesign 接入留在阶段 2+。

**Architecture:** 保留阶段 1 三份 YAML 正本和校验。一个 npm 包使用 contracts/catalog/ui 子入口；React 共享 UI 由 Vite 独立入口与最小宿主示例消费。维护工具独立 Python 进程运行，不进入浏览器、不写审核正本。

**Tech Stack:** TypeScript strict、React、Vite、Node tests、Python unittest/PyYAML；浏览器验收使用 ego-browser。

## 执行边界与关卡

- 工作区 `/Users/howiez/Downloads/awesome-agent-ecosystem`，`main`，基线 `7f609fe`；复用当前目录，不创建 worktree。
- 不修改 myApps、真实数据库、生产账号、安装内核；不推送、发布或部署。
- 分类及资源审核不批量提升；预览不等于使用验证。私人来源只展示已有公开元数据与缺口。
- 实施遵守 TDD：先行为测试、记录预期失败、最小实现、通过后审核；声明配置与生成类型直接生成并做一致性检查。
- 三名 Luna 的文件范围互不重叠；共享产物生成及重型构建串行。提交由主会话在最终检查后执行。
- 最终完成需覆盖原目标八项完成标准，不能用模块测试代替真实页面。

## Task 1: 公共契约、目录逻辑与运行基础

Files: `package.json`, lockfile, `tsconfig*.json`, `vite.config.*`, `src/contracts.ts`, `src/catalog.ts`, `src/generated/**`, `scripts/generate-package.py`, `scripts/build-package.mjs`, `scripts/serve.mjs`, `tests/catalog.test.*`, `tests/package.test.*`。

1. 测试真实正本的筛选组合、稳定 ID/URL、分页、组件关联、加载失败与版本匹配；观察缺失实现的失败。
2. 定义 Catalog/Resource/HostAdapter 稳定类型和最小宿主契约；类型枚举从 YAML 生成。
3. 实现浏览器可用纯目录逻辑及版本加载，保持来源/状态信息原样。
4. 安装独立项目依赖，生成类型，构建 ESM/d.ts 和站点入口所需配置。
5. 测试导出子入口与外部消费，不依赖私有路径。

## Task 2: 共享 UI 与独立站点

Files: `src/ui/**`, `site/index.html`, `site/main.tsx`, `examples/host/**`, `tests/ui.test.*`。

1. 写 UI 行为测试（五类导航、筛选、详情/来源路由、状态、宿主回调），观察失败。
2. 实现语义 HTML 的统一目录/详情/来源结构，分页及稳定 hash 路由。
3. 按真实记录展示预览：图片/轮播/视频、隔离 HTML、文本/设计系统关系；不支持时准确链接与说明。
4. 主题使用可替换 CSS 语义变量，支持宿主文案与预览接口、键盘和窄屏。
5. 独立站点只公开浏览，不伪造账号或安装；明确演示的宿主示例用构建子入口，无复制 UI。

## Task 3: 来源读取与差异提案

Files: `scripts/source-sync.py`, `scripts/source_tools/**`, `tests/test_source_sync.py`, `docs/source-tools.md`, `docs/reuse-assessment.md`。

1. 测试正常读取、无变化、新增/修改/删除/更名、失败保留基线与重复执行一致性，观察失败。
2. 支持锁引用的选定 OpenDesign/Remotion 路径与发现队列；只输出候选/差异与失败报告。
3. 复查选定上游内容/预览依赖边界，记录实际可复用内容及限制；不搬运未知许可全文。
4. 用真实固定上游基线执行维护工具，输出可审查证据；私有或不可达来源如实保留。

## Task 4: 集成、检查与文档

Files: `README.md`（生成器管理）、`scripts/build.py`、`.github/workflows/quality-gate.yml`、`CONTRIBUTING.md`、`MAINTENANCE.md`、`docs/architecture.md`（保留冻结定义，追加阶段 2 实现）、`docs/host-integration.md`、`docs/evidence/phase2/**`。

1. 验证类型生成与正本一致、公共包及最小宿主构建、原 Python 回归、新 Node 测试。
2. 更新运行/维护/贡献/接入说明，核对全新安装流程和公开产物依赖。
3. 检查本机 3000/3001 端口归属，选择空闲端口提供生产构建页面。
4. 在真实页面逐项验收五类筛选/详情直开刷新、来源、真实预览、窄屏、键盘、明暗主题、非默认 accent、加载和失败状态。
5. 修复实际失败，保留日志/截图，按八项标准做逐项完成审计。
6. 无关改动不入提交；本地提交后不 push。只有全部标准实际证明后才标记 goal complete。

## 验收证据表（完成）

| 目标 | 权威证据 | 状态 |
|---|---|---|
| 独立安装/运行/测试/构建 | lockfile、命令日志、生产页面 | PASS，见 docs/evidence/phase2/acceptance.md |
| 五类浏览/筛选/详情直开 | UI 测试 + 真实页面 | PASS，见 docs/evidence/phase2/acceptance.md |
| 正本生成分类/状态 | 生成一致性、枚举对账 | PASS，见 docs/evidence/phase2/acceptance.md |
| 真实预览/获取/候选状态 | 内容来源记录、页面与许可边界 | PASS，见 docs/evidence/phase2/acceptance.md |
| 公共产物被宿主消费 | exports/d.ts、外部消费构建与回调测试 | PASS，见 docs/evidence/phase2/acceptance.md |
| 来源正常/无变化/变化/失败 | 来源测试与固定基线执行证据 | PASS，见 docs/evidence/phase2/acceptance.md |
| 窄屏/键盘/主题/accent/失败 | ego-browser 验收与截图 | PASS，见 docs/evidence/phase2/acceptance.md |
| 文档与实际产物一致 | clean install、引用/命令核对 | PASS，见 docs/evidence/phase2/acceptance.md |

## 活动验收句柄

- 本阶段唯一 ego-browser TaskSpace：`160`，页面 `p1`；后续轮次只恢复此 space，不新建替代。
- 生产站点预计使用 `3001`（2026-10-07 检查 `3000` 已有 Node 服务，`3001` 空闲）；启动前再次核对。

## 最终交付记录

- 单包公共契约/目录逻辑/React UI 与 CSS，独立 Vite 生产入口和真实打包宿主示例已完成。
- 来源工具已完成固定范围读取、元数据、目录关联、候选差异、增改删更名与失败保基线；OD/Remotion 与发现队列真实读取已留证。
- 最终独立依赖目录验证：58 Python + 29 Node 测试、类型检查、生成、公共包/站点构建、真实宿主消费与生产启动均通过。
- 五类真实页面、组合筛选、详情刷新、来源、HTML/文本预览、窄屏、键盘、主题/accent、加载/错误/重试与原生详情展开已检查。
- 目录仍 20/18，17 candidate + 3 reference，0 usable；阶段 1 定义、逐资源 review/verification 与旧 803 条原始字节未改。
- 完整权威证据：[acceptance.md](../evidence/phase2/acceptance.md)。Phase 2+ 和 Phase 5 范围保持原目标；未推送/发布/部署。
