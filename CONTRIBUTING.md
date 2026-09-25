# 收录标准与贡献指南

## 收录标准（全部满足）

1. **热度**：GitHub ★1k+，或细分领域公认标杆（需在 PR 中说明理由）；skill/插件以安装量为主要口径，stars 为辅助
2. **活跃**：近 6 个月内有实质性 commit（非文档 typo 类）
3. **质量**：README 完整、有安装/使用说明、有真实采用案例
4. **可验证**：提供安装量、下载量或权威第三方背书之一

## 核心归类规则（不可违反）

- **条目必须是资产本体**：单个 skill / MCP server / 插件 / CLI / 具体模板或规范文件
- **合集、目录、市场一律进 platforms 分类**（发现渠道，不计入资产统计），即使它很知名
- **生成器类工具归 prompts**（subcat=生成工具）；**设计 token 等工程工具归 cli**
- 拿不准专有名词时**先查证再归类**，不按字面联想（教训：DESIGN.md ≠ SDD 的 design.md）

## 分层标注

- `source`: `official`（协议组织/模型厂商/基金会）/ `vendor`（商业公司）/ `community`（个人或社区）
- `vmethod`: `manual`（人工复核过）/ `automated`（脚本批量收录，未经人工复核）——批量导入一律 automated

## 条目字段（v2 schema）

```yaml
- name: webapp-testing              # 资产名
  url: https://...                  # 项目本体链接（禁止指向合集页）
  source: official                  # official / vendor / community
  platform: "anthropics/skills 仓库" # 分发渠道
  subcat: "开发/测试"                # 子分类（12 类关键词体系，见 import-skills-mcp.py）
  note: "一句话点评，必须含差异化判断"  # 禁止裸抄官方简介
  stars: 166000
  installs: null
  last_verified: 2026-09-26
  vmethod: manual
```

要求：
- 点评必须说明"为什么是它"，不超过 40 字
- 一个 PR 只加一个条目；官方/社区分区不要混
- 批量导入条目的英文描述可由人工逐步润色为中文点评（精品层优先 Top 50）

## 下架标准

- 超过 12 个月无维护
- 被证实存在恶意行为（数据回传、供应链投毒）
- 规范已废弃（移入归档区并注明替代者）
- URL 失效且找不到新地址

## 数据维护

- `data/resources.yaml` 是唯一事实源；README 与页面由 `scripts/build.py` 生成，**禁止手改**
- `scripts/update-stars.py` 定期刷新 GitHub 引用仓库元数据与 stars；GitHub Actions 使用内置 token，本地全量运行请设置 `GITHUB_TOKEN`（当前约 340 个仓库，匿名额度不足）
- `scripts/import-*.py` 从市场/注册表增量导入（自动去重，vmethod=automated）
- 全量审计记录见 [AUDIT.md](AUDIT.md)
