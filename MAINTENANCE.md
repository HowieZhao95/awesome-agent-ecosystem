# 维护与更新

来源跟踪的唯一正本是 [data/sources.yaml](data/sources.yaml)；资源身份、内容变更、下架与发布规则见 [docs/architecture.md](docs/architecture.md)。本文件只说明当前执行入口，避免重复维护来源名单。

## 当前执行范围

- `.github/workflows/weekly-sync.yml` 保留旧市场/注册表发现与 GitHub 元数据刷新，只更新 `data/discovery/legacy-v2.yaml` 和扫描缓存，走 `bot/weekly-sync` PR，不直接写新公共资源正本。
- OpenDesign、Remotion 的选定范围由 `scripts/auto-source-sync.py` 在 `weekly-sync` 中解析最新 main commit、下载固定 SHA 归档、复用来源快照工具并写入 review-only 候选证据；weekly workflow 通过 PR 提交差异。它不修改资源正本、不自动晋级或覆盖 baseline；失败不覆盖旧候选。受限 ThusDesign 内容不被采集。其他来源的 `cadence: manual` 仍只走人工来源工具。
- `scripts/validate.py` 校验新分类、来源和具体记录契约；`scripts/validate-discovery.py` 校验旧发现队列。
- `scripts/build.py` 从三份 YAML 正本生成 README、`site/data.js` 和 `site/catalog.json`；生成可重复，不把运行时校验或用户审核状态补为已通过。
- `scripts/update-stars.py` 仍按仓库去重、ETag 请求和显式 API 失败策略刷新历史发现热度；仓库热度不代表单资源采用度或质量验证。

本地命令：

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/validate-discovery.py
python scripts/validate.py
npm ci
npm run generate
npm test
npm run typecheck
npm run build
npm run check:host
```

自动发现用 GitHub Actions 内置 token；本地全量 GitHub 扫描需要足够配额的 GITHUB_TOKEN，只在运行环境读取，不写入文件或日志。来源抓取失败时保留旧基线，显示缺口，不把失败当作资源已下架。

## 晋级与更新

维护者先审核具体内容出处和分发单元，登记候选；分类、许可、依赖、组件和使用验证的变化通过 PR 审查。只有满足 architecture 的全部门槛，具体记录才可晋级为 usable。规范获批与具体内容获批是两个关卡，不能批量晋级。

来源每次查证只承诺 tracking.scope 覆盖范围，更新 last_checked、baseline 和 limitations。原始作者不明、许可不明或新版本行为未验证时，保持明确未知状态。发布日期、目录版本与上游内容引用分别维护。

## 发布与接入

阶段 1 契约已冻结，但 `0.1.0-draft` 仍未发布；逐项资源仍待独立审核，ThusDesign 不得将当前草稿当成已审查可安装目录。发布须另行授权并生成固定版本；消费者锁定 release/tag 对应的 commit 或内容校验值，不读取移动 main。

当前 myApps 的旧设计风格适配器仍读取 main 的旧栏目。该接入尚未迁移；发布后另行替换为固定版本，不能声称阶段 1 已完成客户端接入。

## 既有 PR 迁移注意

2026-10-07 查到的 [PR #1 weekly-sync](https://github.com/HowieZhao95/awesome-agent-ecosystem/pull/1) 修改旧 resources.yaml、README 和网站数据，与本次正本切换冲突。不能原样合并其生成产物；后续需把增量变成发现队列更新，并重新生成新正本输出。[PR #2 Statsnet MCP](https://github.com/HowieZhao95/awesome-agent-ecosystem/pull/2) 是候选提案，仍需具体来源、组件与许可查证。

本轮未关闭、合并或修改这些远端 PR。`AUDIT.md` 和旧计划是历史快照，不证明新目录全部审核通过。

## 公共商店维护

`npm run generate` 更新正本投影与类型枚举；构建结果是公共模块和独立站点，不是资源安装结果。来源工具提案不覆盖三份 YAML 正本，也不继承旧审批或许可结论。核对差异后人工修改数据、重新生成并执行检查。

运行入口与独立安装步骤见 README；宿主接口与阶段 2+ 迁移边界见 [接入文档](docs/host-integration.md)。公开发布仍单独授权，不能把测试产物或 npm 打包成功当成已发布。

## 验收证据

阶段 2 记录见 [acceptance.md](docs/evidence/phase2/acceptance.md)。公共 Git 保留命令、结构与状态的检查记录；可能包含上游参考媒体的浏览器 PNG 只保留在本地，不随公共项目再分发。QA 夹具代码和生成方法位于 `docs/evidence/phase2/preview-qa/`，其临时站点输出已经按清单清理；正式目录没有夹具数据。

## 框架身份维护

2026-10-07 用户追加模板与风格解耦裁定，正本定义与文件角色见 architecture。上游重复的视觉入口不直接新增模板；先核对是否共享同一框架、只有外观差异，或属于调用框架的任务配方。来源工具仍只输出差异提案，不能自动把 SKILL.md/HTML 示例判为框架。

## 完整浏览覆盖

历史发现队列由 `scripts/discovery-index.py` 只读生成独立发现索引，随 `npm run generate` 纳入公开目录。它保留逐条去向、输入哈希和未知内容出处；语义覆盖通过 `data/discovery/classification-overrides.yaml` 审查。来源可浏览与资源可安装分别判断，不因目录地址不够具体而让整个历史队列在UI消失。

OpenDesign框架/Skill的全入口清单由 `scripts/opendesign-inventory.py` 按固定归档生成；人工审核提案后才写资源正本，主题入口不新增模板身份。贡献与更新需要核对777旧条目和上游入口的覆盖报告，不能只对数量总和或几项夹具做验收。

本轮覆盖结果和数量以 [完整目录验收](docs/evidence/complete-directory/acceptance.md) 为准。旧777条和26平台不因未审核而消失；发现条目的状态与安装资格分别维护。

维护命令示例（先运行常规生成/测试）：

```sh
python scripts/discovery-index.py --data data/discovery/legacy-v2.yaml --resources data/resources.yaml --categories data/categories.yaml --overrides data/discovery/classification-overrides.yaml --output /tmp/legacy-review-index.json
python scripts/opendesign-inventory.py --archive /path/to/open-design-53231d40b778d88eba23f35547bf99485d3ae9fc.tar.gz --resource-data data/resources.yaml --json /tmp/opendesign-review.json --coverage /tmp/opendesign-review.md
```

需要复现某次提案时使用显式 `--resource-data-ref <commit>` 读取当时的资源基线；默认读取当前正本用于新维护，不能把合入后的条目数与旧提案输入混为一谈。CLI只产生提案，不修改已审核数据。不要把这些一次性读取当作阶段5持续调度已上线。
