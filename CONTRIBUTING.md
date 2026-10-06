# 贡献公共资产

阶段 1 分类与公共契约已冻结；逐项资源仍按各自证据审核，契约批准不等于资源许可、实测或可用批准。主类、子类与维度只在 [data/categories.yaml](data/categories.yaml) 定义；记录字段、收录门槛及更新规则见 [docs/architecture.md](docs/architecture.md)。贡献时引用它们，不再手抄另一套分类或字段列表。

## 提交流程

1. 先从实际内容上游定位具体文件、目录或条目；发现目录和市场只记为 discovered_via/distribution，不替代原始出处。
2. 查询现有资源 ID 及具体 path/selector，合并镜像或新分发渠道，避免因名称改变创建重复身份。
3. 在 `data/sources.yaml` 登记尚未登记的来源角色、跟踪范围及维护策略；在 `data/resources.yaml` 填写完整记录结构。
4. 不明作者、许可、版本或预览状态保留 unknown/null 和原因。普通提交以 candidate 或 reference、review pending 开始，不自行写成 approved/usable。
5. 适配需写固定原引用、derives_from 和实质改动。精选不改原作者或许可，不能把目录维护者写成内容作者。
6. 插件解释每个组件的具体出处、提供方式及外部依赖；不把宿主模块或所需工具冒充包内内容。
7. 运行 `python scripts/validate.py`、`python -m unittest discover -s tests -v`、`python scripts/build.py`。README 和网站数据由正本生成，禁止手工编辑。
8. 在 PR 说明新增/更新/下架的身份、证据、已验证范围和未知项；审核后再决定收录状态，发布动作另行处理。

## 发现队列

`data/discovery/legacy-v2.yaml` 保留旧目录和现有自动发现流程。批量导入只进入这里，不写公共资源正本。旧名字、热度、source、platform 与 manual/automated 都是线索；不得据此自动补作者、许可证或验证结果。旧发现记录的 schema 由 `scripts/validate-discovery.py` 检查。

发现队列中的条目需要逐条追溯后才能晋级。热度可用于安排审核优先级，不作为可使用资源的充分条件；合集与市场登记为来源，不统计成资产。

## 隐私与许可

不提交用户安装记录、凭证、本机绝对路径、私人工作导引或学习记忆。已有 ThusDesign 内容只在允许的范围登记公共元数据；没有公开分发/许可证据时保持候选。

本仓库的 CC0 只覆盖目录自身资料，不改变被引用内容、代码、字体或媒体的许可。许可未知的原始内容不转存、不自动安装，链接索引也不授予复制权。
