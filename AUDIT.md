# 审计报告（2026-09-26）

对 data/resources.yaml（804 条）的系统性审查结果。按严重度分级：**P0 = 功能失效**，**P1 = 分类错误**，**P2 = 一致性/维护债**。

---

## P0 功能 bug（必须修）

### 1. update-stars.py 已完全失效
脚本依赖条目的 `repo` 字段拉 GitHub stars，但 v2 schema 重构后条目只有 `url` 字段。
**实测：0/804 条命中**，脚本空跑。
**修法**：从 `url` 正则解析 `github.com/owner/repo` 得到 repo 再查 API；非 GitHub URL 跳过。

### 2. README 目录锚点为空
build.py 生成目录时锚点写的是 `(#)`，GitHub 上无法跳转。
**修法**：按 GitHub slug 规则从分类名生成锚点（小写、空格转连字符、去括号与斜杠）。

---

## P1 分类错误

### 3. CLI 类 4 条占位链接
`recall`、`ccexp`、`gstack`、`cmux` 的 URL 全部指向 `hesreallyhim/awesome-claude-code`（合集页），不是项目本体。种子数据阶段图省事填的。
**修法**：找到真实仓库替换；找不到的下架。

### 4. MCP 类混入合集与非服务器
- `Awesome-MCP-ZH`、`Awesome-MCP-Servers`：是合集，按规则应去 platforms 或删除
- GitHub topic 导入可能混入 SDK/框架/网关（名字含 mcp 但不是 server，如 fastmcp 类）
**修法**：加过滤规则（名字含 awesome 直接排除）；人工筛一遍 Top 50。

### 5. plugins 类 4 条错位
`document-skills-xlsx/docx/pdf`、`content-research-writer`：链接指向 ComposioHQ 合集根目录（占位），且本质是 skills 不是 plugin。
**修法**：移到 skills 类并指向具体 SKILL.md 路径。

### 6. prompts 类 3 个合集
`awesome-chatgpt-prompts`、`awesome-agent-conventions`、`awesome-cursorrules` 是合集/目录，按"合集一律 platforms"规则应迁移。
（注：`awesome-chatgpt-prompts` 有争议——它既是合集也是单一事实来源的 prompt 库，建议移 platforms 保持一致性。）

### 7. 手录 MCP 条目 URL 未验证（猜测路径）
`postgres`、`sqlite`、`brave-search`、`puppeteer`、`slack-mcp` 指向 servers 仓库根目录而非具体子路径；`e2b-mcp`、`linear-mcp`、`supabase-mcp`、`notion-mcp` 的仓库路径是推断的，未实际验证。
**修法**：逐条 HTTP 校验 URL 存活性（可加进 CI：链接检查器）。

### 8. 设计规范类的两个"借住"条目
`@google/design.md CLI` 和 `Stitch` 严格说是工具不是规范。当时作为"格式本体"保留——这是个判断题，建议保留但在分类 desc 注明"含格式定义与官方工具"，或把 CLI 复制一份到 cli 类（cross-list）。

---

## P2 一致性与维护债

### 9. subcat 覆盖不全
| 分类 | subcat 缺失 |
|---|---|
| plugins | 403/403（全缺） |
| cli | 18/20 |
| prompts | 13/27 |
| platforms | 22/22（设计上可以缺） |

plugins 最需要子分类——官方 marketplace.json 和 claude-plugins.dev API 都带 category 字段（development/productivity 等），导入时丢掉了一个现成字段。
**修法**：import-marketplace.py 补读 category → subcat 映射。

### 10. 点评语言混杂
约 650 条批量导入条目是英文截断描述，与手工中文点评混排，观感割裂。
**建议**：定义"精品层"——下载量/stars Top 50 的条目人工润色中文点评，其余保留原文。这恰好形成库的策展梯度，而不是全量翻译（维护不起）。

### 11. last_verified 一刀切
所有条目标 2026-09-26，但批量导入的并未人工验证。原 schema 设计的 `verified.method: manual/automated` 未实现。
**修法**：导入脚本写 `verified: {date, method: automated}`；人工复核过的改 manual。页面可据此显示不同验证徽章。

### 12. skills 的 stars 归属问题
GitHub topic 导入的 skills，stars 是仓库级数据——多技能合集仓库的 stars 会高估单个技能热度。与"热度看安装量"原则冲突。
**建议**：skills 热度以 skills CLI / awesomeclaude.ai 安装量为准，GitHub stars 降为辅助。

### 13. plugins 与 mcp 的包装重复
官方市场里的插件有些是 MCP 服务器的包装（如 stripe、notion 既有插件条目又有 MCP 条目）。
**修法**：schema 加 `related` 字段互链，或制定规则：MCP 包装的插件不重复收录。

### 14. CONTRIBUTING.md 过时
条目格式示例还是 v1（无 platform/subcat/verified 字段），收录标准未提"合集一律 platforms"这条核心规则。

### 15. 导入脚本硬编码验证日期
`VERIFIED = "2026-09-26"` 写死在两个 import 脚本里，下次运行会打上错误的日期。
**修法**：改为运行当天日期。

---

## 修复优先级建议

| 批次 | 内容 | 工作量 |
|---|---|---|
| 第一批（脚本级） | #1 update-stars 修 url 解析、#2 目录锚点、#15 日期硬编码、#9 plugins 补 subcat、#4 合集过滤 | 纯代码，半小时 |
| 第二批（数据级） | #3 占位链接、#5 错位条目、#6 合集迁移、#7 URL 校验 | 数据修正 + 重跑 build |
| 第三批（制度级） | #10 精品层润色、#11 verified.method、#12 热度口径、#13 related 字段、#14 CONTRIBUTING 更新 | 需要决策 |
