# 历史发现队列

`legacy-v2.yaml` 从本地基线 `f8da353` 的 `data/resources.yaml` 按原始字节保留：803 条历史记录，包括 777 条旧资产记录与 26 条发现平台记录。首次迁移 SHA-256：`1111aff8040a5dc2acee51aee8f0a5a145e92387efc145145db0eee17cacdc35`。

本文件不是新的分类或资源正本。旧 manual/automated、source、platform、热度和点评保留历史含义，不转换成新目录的作者、许可、审核或运行验证。后续旧自动发现脚本只更新这一队列；人工追溯后，具体对象才能以新契约进入 `../resources.yaml`。

新正本文件及职责见 [architecture](../../docs/architecture.md)。

统一商店现在通过独立发现索引展示全部777条旧入口，并单列26个平台。`classification-overrides.yaml` 保存有实质歧义的语义重映射；`opendesign-references.yaml` 保存固定上游的风格/共享框架关联和待核查入口。它们供浏览，不能替代严格资源正本或成为已审核安装记录。

生成入口为 `npm run generate`；逐条覆盖与当前实现边界见 [完整目录计划](../../docs/plans/2026-10-07-complete-resource-directory.md)。
