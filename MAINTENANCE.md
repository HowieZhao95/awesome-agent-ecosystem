# 维护与更新策略

> 核心约束：单人维护。原则：**机器干粗活（发现、去重、刷数据、校验），人只做判断（点评、收录终审、下架决策）。**

## 一、节奏设计

| 周期 | 动作 | 执行者 | 耗时 |
|---|---|---|---|
| 每周（自动） | 增量导入新资源；`update-stars.py` 扫描所引用 GitHub 仓库的最新数据；重建页面；抽查链接 | CI（GitHub Actions） | 0 人工 |
| 每两周（人工） | 过候选增量：本周新导入的 automated 条目快速扫一遍，明显低质/错分的删掉或改类；Top 50 精品层润色 2-3 条 | 人 | ≤20 分钟 |
| 每月（自动+人工） |  staleness 降级：6 个月无更新 → 点评标注；12 个月 → 提下架 issue；人终审下架 | 机器提案，人终审 | ≤15 分钟 |
| 每季度（人工） | 对照 AUDIT.md 格式做一次轻量审计：占位链接、合集混入、subcat 准确率抽查 | 人 | ≤30 分钟 |

## 二、自动化管道（GitHub Actions）

```
weekly.yml
  1. python scripts/import-marketplace.py    # 官方市场 + cp.dev Top 增量
  2. python scripts/import-skills-mcp.py     # skills/MCP 注册表增量
  3. python scripts/update-stars.py          # GitHub 仓库去重查询；支持 GITHUB_TOKEN 与增量缓存
  4. python scripts/build.py                 # 重新生成 README + data.js
  5. link-check（抽样 50 条 URL HEAD 校验）
  6. 自动提 PR（标题：data: weekly sync YYYY-MM-DD）→ 人手机上点 merge
```

关键点：**自动更新一律走 PR 不直推 main**——人保留一键否决权，这是单点维护的安全阀。

将本目录初始化并推送为 GitHub 仓库后，在仓库 **Settings → Actions → General → Workflow permissions** 中开启 **Allow GitHub Actions to create and approve pull requests**。工作流默认使用 GitHub Actions 内置 token；如需要更高的跨仓库读取额度，可选配 `GH_TOKEN` secret。手动运行入口是 **Actions → weekly-sync → Run workflow**。同步 PR 使用固定的 `bot/weekly-sync` 分支，下一次运行会更新同一个 PR。

本地全量扫描要先设置 `GITHUB_TOKEN`；当前约 340 个独立 GitHub 仓库，匿名 API 配额不足以完成一次扫描。不要把 token 写入文件。GitHub Actions 的内置 token 会自动传给扫描脚本。

GitHub 发现与仓库扫描失败会使同步任务失败，避免提交不完整的核心数据；第三方目录站限流或暂时不可用时会在 Actions 日志中显示 warning，本轮跳过该来源。无新增、无星标或仓库元数据变化时，不创建新 PR。质量门禁运行测试、数据校验，并检查生成文件与 YAML 一致。

GitHub 引用资源的扫描状态在 `data/github-repo-state.json`：按仓库保存 ETag、仓库 stars、描述、默认分支、最近推送时间、归档状态和 topics。首次运行会新增该文件；后续对未变化的仓库使用条件请求，收到 `304` 时保持文件原样。多个条目引用同一仓库时只查询一次。目录条目只有原本填写了 `stars` 才刷新该值；留空代表该资产不使用仓库 stars 作为热度。该状态文件可随同步 PR 一起审查；删除后下次会重新抓取全部仓库。非 GitHub 链接仍由抽样链接检查覆盖。

## 三、数据质量门禁（CI 校验，随 build 触发）

- YAML schema 校验：必填字段（name/url/source/platform/note）齐全
- 归类规则校验：资产类条目 URL 不得指向已知合集域名/仓库（维护一份合集黑名单）
- 去重校验：name 全库唯一（build 时 fail-fast）
- vmethod 校验：import 脚本产出的条目必须 automated，不允许伪装人工

## 四、分层维护策略（人的精力分配）

| 层 | 范围 | 维护方式 |
|---|---|---|
| 精品层 | 每类 Top 10（约 70 条） | 人工中文点评、季度复核、优先更新 |
| 数据层 | 其余 automated 条目 | 全靠机器，坏了就下架不心疼 |
| 平台区 | 22 个分发渠道 | 半年看一次，活跃度低的标注 |

精品层的选择标准：安装量/stars 头部 + 自己实际用过 + 官方背书，三者取其二。

## 五、依赖外部数据源的脆弱性与预案

| 数据源 | 风险 | 预案 |
|---|---|---|
| claude-plugins.dev API | 第三方站，可能改接口或关停 | 导入脚本失败不阻塞主流程，告警即可；官方 marketplace.json 是一手备份 |
| Smithery registry | 同上 | MCP 导入有 GitHub topic 源兜底 |
| 官方 marketplace.json | 路径可能变 | 脚本内 URL 常量化，改一处即可 |
| GitHub API | 未登录 60 次/小时 | GITHUB_TOKEN 存 secret；分页带重试 |

## 六、三个待拍板事项（影响策略落地）

1. **精品层 Top 50 中文润色**：做 → 每两周节奏里包含；不做 → 全库英文原文，定位变成"数据索引"而非"策展"
2. **skills 热度口径改安装量**：改 → update-stars.py 需要接 skills CLI/awesomeclaude.ai 数据源（目前无公开 API，需爬或放弃，维持 stars 辅助口径）
3. **插件与 MCP 包装重复**：加 related 字段互链 → schema 变更 + build/页面展示改动；不加 → 接受少量重复

## 七、版本与变更记录

- 数据语义化版本：schema 变更（如加 related 字段）升 meta.version，CHANGELOG 记根目录
- 每次自动 PR 附 diff 摘要（新增 N 条、下架 N 条、stars 刷新 N 条），merge 即历史
- AUDIT.md 保留历次审计，新审计追加新日期段落不覆盖
