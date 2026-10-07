# 阶段 2 验收记录

**结论：开源目录商店和公共模块已可用，基础来源维护工具已可用。** 本地验收完成；未推送、发布或部署。正式 `thusdesign.ai/agent` 挂载、账号安装、个人资产与旧商店迁移仍由阶段 2+ 独立验收。

## 完成标准与权威证据

| 标准 | 已检查结果 | 证据 |
|---|---|---|
| 新环境运行、构建、测试 | 独立源码副本、全新 Python venv 与 npm 依赖；移除业务凭证环境变量、排除私有源码与 `.env`；文档命令全部退出 0；真实生产启动 HTTP 200、20 条资源；临时目录已清理 | [clean-bootstrap.json](clean-bootstrap.json)、`bootstrap-*.log`、[重现脚本](clean-bootstrap.py) |
| 五类浏览、筛选、详情直开 | 五类逐项点击与详情刷新；精确路由 ID 与标题一致；子类/领域/来源/验证/生命周期和搜索组合返回正确单项，空结果正确 | [browser-navigation.json](browser-navigation.json)、`bootstrap-node-tests.log` |
| 正本一致 | 五类与全部维度类型对账 YAML；生成目录保持资源正本；独立副本生成输出字节相等；阶段 1 定义与逐项审核/验证状态未变 | [completion-data-audit.json](completion-data-audit.json)、[clean-bootstrap.json](clean-bootstrap.json) |
| 预览与获取真实 | 固定 OpenDesign 9 条预览路径存在；真实 HTML 隔离预览、设计系统 kit、DESIGN.md 文本与 tokens 链接正常；无预览/受限来源提供真实入口；候选不冒充实测 | [source-preview-path-check.txt](source-preview-path-check.txt)、[browser-html-preview.json](browser-html-preview.json)、[browser-appearance.json](browser-appearance.json) |
| 公共产物宿主消费 | npm pack 后安装临时消费者，真实 `examples/host` 用公开契约/逻辑/UI/CSS 入口类型检查与构建通过；登录、状态、四操作、文案、主题、链接及预览回调行为通过 | `bootstrap-host.log`、[host-adapter-tests.log](host-adapter-tests.log)、[接入说明](../../host-integration.md) |
| 来源正常/无变化/变化/失败 | 16 项来源测试通过，含新 SHA 读取与真实删除、增改更名、重复内容配对、部分失败和基线保留；真实固定来源 OD 94/Remotion 145 文件，两次读取 0 差异；发现队列只取显式选定条目 | [source-green.log](source-green.log)、`source-*-repeat.json`、[来源工具](../../source-tools.md) |
| 页面体验 | 390px 列表/插件详情无横向溢出；键盘 Enter/Tab 与焦点样式正常；浅/深主题与两种背景下绿色强调色；目录加载/失败/重试与预览失败反馈真实；最新构建的原生详情展开正常 | [browser-appearance.json](browser-appearance.json)、[browser-failure-states.json](browser-failure-states.json)、[browser-disclosure-final.json](browser-disclosure-final.json) |
| 文档一致 | README 从正本生成，所有运行命令已在独立依赖目录执行；运行、维护、贡献、宿主接入与来源工具说明对应实际文件和产物 | [clean-bootstrap.json](clean-bootstrap.json)、README、MAINTENANCE、CONTRIBUTING |

## 首批目录与边界

20 条资源、18 个来源：17 个候选、3 个参考、0 个可使用、0 个下架。所有 `tested_hosts` 仍为空。唯一原资源内容变化是给 Social Carousel 增加已查明的上游参考图片入口，未转存原图，未提升许可或验证。

旧 803 条发现队列与原始 `f8da353:data/resources.yaml` 字节一致。公共目录的 `availability` 由已有 Python 门槛生成，当前所有目标宿主列表均为空。它是展示投影，不是新安装内核。既有 Skill 指针与重新安装业务不被改写。

## 预览夹具与清理

当前正式目录没有已查明的公开视频直链。媒体能力用明确标注“仅验收夹具 · 非正式资源”的独立页面检查；页面消费实际编译后的公共 UI，未提供账号或安装状态。自生成 H.264 视频实际播放（1.5s、readyState=4、currentTime 增长），图片轮播切换到第二个不同 SVG，下架原因正确显示。见 [browser-media-fixtures-final.json](browser-media-fixtures-final.json)。

QA 输出按 [qa-manifest.json](qa-manifest.json) 精确清理，正式 HTML 与目录哈希未变，见 [qa-cleanup.json](qa-cleanup.json)。正式页面恢复原目录，见 [browser-final-baseline.json](browser-final-baseline.json)。可能包含上游参考媒体的 PNG 仅留本地，不进入公共 Git。

## 已解释的中间失败

- 生成最新目录后，空预览测试错误选中已有 Markdown 正文的 Skill；修正夹具选择，未删除正确的正文预览能力。相关日志 `node-tests.log`，最终全套通过。
- 外部消费首先暴露声明文件未输出：构建配置继承了 `noEmit=true`；修正单个 `noEmit=false` 后，真实打包宿主通过。保留 `host-check.log` 与最终日志。
- 第一轮路由证据错误要求 ID 出现在可见正文中；修正为 URL ID 与实际标题匹配，五项刷新均通过，初始记录保留为 `browser-navigation-initial.json`。
- 首次媒体测试临时改变已服务的构建目录，无法可靠加载视频；原目录在 finally 恢复，见 `browser-media-fixtures.json`。之后改用独立 QA 入口和注册后的媒体文件，成功播放并清理；未改正式数据或播放器行为。
- 详情最终升级后，旧浏览器片段导航仍持有旧 JS；显式 reload 并核实最新 `index-B8RmBWIF.js` 后完成原生展开验收。

## 最终状态

独立项目工作区 `/Users/howiez/Downloads/awesome-agent-ecosystem`，分支 `main`。myApps 保持本任务只读；未操作真实 PGlite、生产账号、付费模型或云端安装。正式本地预览运行于 `3001`，已有 `3000` 服务未改动。浏览器 TaskSpace 160 在最终审计后关闭。
