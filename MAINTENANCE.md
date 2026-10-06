# 维护与更新

来源跟踪的唯一正本是 [data/sources.yaml](data/sources.yaml)；资源身份、内容变更、下架与发布规则见 [docs/architecture.md](docs/architecture.md)。本文件只说明当前执行入口，避免重复维护来源名单。

## 当前执行范围

- `.github/workflows/weekly-sync.yml` 保留旧市场/注册表发现与 GitHub 元数据刷新，只更新 `data/discovery/legacy-v2.yaml` 和扫描缓存，走 `bot/weekly-sync` PR，不直接写新公共资源正本。
- OpenDesign、Remotion 和 ThusDesign 的新来源策略已登记；本阶段未增加它们的持续抓取器或监控任务。cadence 是维护约定，不代表自动化已经执行。
- `scripts/validate.py` 校验新分类、来源和具体记录契约；`scripts/validate-discovery.py` 校验旧发现队列。
- `scripts/build.py` 从三份 YAML 正本生成 README、`site/data.js` 和 `site/catalog.json`；生成可重复，不把运行时校验或用户审核状态补为已通过。
- `scripts/update-stars.py` 仍按仓库去重、ETag 请求和显式 API 失败策略刷新历史发现热度；仓库热度不代表单资源采用度或质量验证。

本地命令：

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/validate-discovery.py
python scripts/validate.py
python scripts/build.py
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
