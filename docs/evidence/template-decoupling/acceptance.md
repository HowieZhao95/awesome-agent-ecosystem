# 模板与设计系统独立登记验收

2026-10-07 用户明确四项裁定并授权实施：模板是内容与代码框架，包含 SKILL.md/示例/辅助文件；七类不变；设计系统核心 manifest.json + DESIGN.md + tokens.css；模板与风格解耦。

## 已落地内容

- 正本定义、贡献规则、公共 profile 类型和校验一致。新增可选 profile 保持 v3 旧候选可读，模板新安装可用门槛要求完整文件角色和独立样式边界，系统可用门槛要求三核心。
- 模板登记实际 instructions/framework/example/support 文件，不写固定 design_system_id。视觉示例独立显示；上游混合的样式约束如实显示待拆分，未把元数据重整称为上游代码已经改造。
- 共用 HTML PPT 框架单独登记。Pitch Deck、Motion Frames、Docs Page、Social Carousel、Device Showcase 原 ID 保留，按只有方法和成品示例的实际内容改为 Skill，未复制一个风格入口作为新模板。
- 152 套上游设计系统的三件套与声明映射逐项查验。Agentic 保留既有 ID，新增其余151套候选；品牌名不推导官方授权，作者、发布者和许可保持未知；正文/媒体不转存。
- 修复 HTML 参考预览的相对文件目录，并仅在运行时读取同一固定 GitHub 提交的 CSS，处理原始 CSS text/plain 返回类型导致的浏览器样式拒绝；保留来源 URL，iframe 仍不允许 same-origin。未建设风格执行/安装内核。

## 数据结果

172 条资源，18 个来源：模板3、设计系统154（152套三件套 + 2条参考）、Skills10、提示词3、插件2。七种模板分类仍全部可选；当前只有原型/Deck/仪表盘三种实际框架候选被查明，其他分类没有以示例凑数。

169 candidate、3 reference、0 usable；全部 tested_hosts=[]。原20个ID、逐项审核、许可及生命周期状态保留；803条历史发现队列原始字节不变。详见 [data-audit.json](data-audit.json)。旧发现队列和其余框架候选的完整语义迁移没有在本轮宣称完成。

## 验证

| 检查 | 结果/证据 |
|---|---|
| 固定上游身份与文件 | 核对 1,825 个 profile 文件路径；152套三核心对应明确包与路径。清单见 [design-system-inventory.json](design-system-inventory.json) 和 [源审计](../../template-decoupling-audit.md)。 |
| Python | 72/72；[python-tests-final.log](python-tests-final.log)。涵盖旧目录、来源、profile、框架身份、未知 ref 和已有宿主门槛。 |
| Node | 38/38；[node-tests-final.log](node-tests-final.log)。真实正本与两种生成投影对账，UI 文件角色/示例/旧记录和 CSS 读取回归。 |
| 类型/生产构建/外部宿主 | [typecheck-final.log](typecheck-final.log)、[build-final.log](build-final.log)、[host-final.log](host-final.log) 全部退出0；实际打包产物由宿主例通过公开 exports 消费。 |
| 真实页面 | [browser.json](browser.json) 检查共用框架、旧配方路由、DS三核心和154项搜索/分页；[browser-final.json](browser-final.json) 核对最终构建、七类选项、390px详情不溢出。 |
| CSS 实效 | [preview-css-final.json](preview-css-final.json) 记录确切源 CSS 与最终 bundle，原始 tokens 被用于沙箱预览；真实截图已查看，颜色卡和字体/间距已呈现。PNG 只留本地，不随公共项目分发。 |

## 已解释的集成修正

- 最初 profile 校验用仓库首页假夹具，无法接受实际 full-blob 上游 URL；已用真实 OpenDesign 记录复现并修复。同样保留 VoltAgent 未查明 ref 的原始 URL，不虚构固定 SHA。
- 原测试写死20条并假设模板尚无profile；已改用正本分页/载入对账和显式无profile旧夹具。正向宿主可用测试使用完整独立框架夹具，保持原判断覆盖。
- Tom Modern 映射用同一个 components.html 作两处示例，登记合并为一个 role/path，避免同包重复。
- UI 角色清单最初过滤了与 profile 同URL的显式 HTML 示例；真实 Agentic 回归已恢复它的预览入口。
- DS相对 tokens.css 文件存在，但 raw GitHub 的 text/plain MIME 阻止浏览器直接作为 stylesheet 消费；窄范围运行时 CSS 读取修复已由真实页面证实，未把源数据或资源验证状态升为可用。

## 边界

改动只在独立开源目录项目。本次不改 myApps、账号/旧安装身份或真实数据库，不推送、不发布、不部署。OMP与阶段2+边界保持；原冻结证据保留并明确新裁定。当前生产预览在 localhost:3001，已有3000服务未动。浏览器本轮 Space162 最终验收后关闭。
