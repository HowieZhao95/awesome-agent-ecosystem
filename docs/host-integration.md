# 公共模块与阶段 2+ 接入

阶段 2 的独立站点与宿主共享一份资源商店 UI。正式产品入口仍为 `thusdesign.ai/agent`，账号安装、个人资产、生产目录供给与旧页面迁移由阶段 2+ 单独验收。本阶段不修改 myApps。

## 公共边界

一个包通过 contracts、catalog、ui 子入口提供公共契约、纯目录逻辑和 React 界面；样式通过独立 CSS 入口提供。分类字面量及筛选定义读取 YAML 正本的生成结果，不在消费方复制分类名单。

公共目录包含公开身份、具体来源、许可声明、验证证据和限制。私人账号状态、用户已添加/安装记录、凭证和数据库不进入目录。

独立站点只提供公开浏览、来源与获取说明。未传入宿主时，不显示模拟登录或成功安装。最小宿主示例中的模拟账号和操作必须明确标为演示，不能作为产品接入证据。

## 宿主职责

宿主提供锁定目录版本的加载入口、账号状态与登录回调、个人资产状态，以及添加/安装/应用/配置回调。公共 UI 将操作交还宿主；业务权限、计费、状态持久化和执行由已有产品能力负责。

主题与文案通过共享接口输入；组件 CSS 使用可替换语义变量。宿主可提供资源链接与适用预览能力，公共目录仍保留原始来源和预览限制。

已有 Skill 安装继续采用只读指针、重新安装更新，不引入安装版本表或第二安装内核。公共目录版本是元数据基线，不能代替 Skill 安装指针的业务身份。

## 阶段 2+ 迁移对照

后续接入必须明确原提示词条目、Skill listing、公共资源 ID 之间的映射；保留旧能力与数据身份，不按公开目录重新分配安装记录。已添加、已安装、已内置、待配置分别由宿主投影；公共目录候选/参考/可用/下架与个人状态分别展示。

目标宿主的可用标记仍按冻结契约判断，预览成功不提升 `verification`。原有 Skill 安装判断不被公共目录回溯替代。

正式产品只消费经审核并锁定的发布目录；本次草稿和本地构建不是已发布版本。公开发布与部署需要另行授权。

## 验证记录

`npm run check:host` 已将实际打包产物装入临时消费项目，使用 `examples/host` 通过公开声明完成类型检查与 Vite 构建，证据见 [host-check-final.log](evidence/phase2/host-check-final.log) 和 [独立安装验证](evidence/phase2/clean-bootstrap.json)。宿主接口的登录、个人状态、四项操作、主题与文案、链接和预览回调已有行为测试，见 [host-adapter-tests.log](evidence/phase2/host-adapter-tests.log)。

## 使用公开子入口

完成 `npm run build` 后，`dist/` 提供 ESM 与 `.d.ts`，`web-dist/` 提供独立站点。宿主导入包的公开入口：

```tsx
import { loadCatalog } from '@public-agent-store/catalog/catalog';
import { CatalogApp } from '@public-agent-store/catalog/ui';
import type { HostAdapter } from '@public-agent-store/catalog/contracts';
import '@public-agent-store/catalog/ui/styles.css';

const catalog = await loadCatalog('/published/catalog.json', {
  expectedSchemaVersion: 3,
  expectedCatalogVersion: 'YOUR_APPROVED_PINNED_CATALOG_VERSION',
});
// host 由产品现有账号和资产能力实现；不是公共目录维护的状态。
export const Store = ({ host }: { host: HostAdapter }) =>
  <CatalogApp catalog={catalog} host={host} />;
```

`HostAdapter` 的 `account.status/login` 表示登录入口；`assetStatus` 分别提供 `added/installed/applied/builtIn/requiresConfiguration`；`operations` 接收 `add/install/apply/configure`。`theme`、`i18n`、`links` 和 `preview` 由消费方提供。回调拒绝时由共享界面展示错误，不能提前把资产标为成功安装。

`examples/host/` 是明确标注的演示消费方；`npm run check:host` 验证构建包导出与示例消费。生产账号、权限与持久化不能由该演示证明。具体检查证据见阶段 2 计划。

## 宿主可用投影

生成的 `catalog.json` 额外提供 `availability`（资源 ID → 已满足冻结门槛的宿主 ID 数组）。它由已有 Python 收录判断生成，原始资源记录保持原样；公共 UI 不重做许可审核或安装内核。`HostAdapter.hostId` 采用稳定宿主 ID，公开目录的新安装/使用入口按目标宿主投影判断。缺少投影或未验证目标宿主时不提供新的安装推荐。

“添加到个人收藏”不等于安装或运行。已有 Skill 指针与重新安装裁定仍由现有产品机制维护，本阶段没有生产适配器替代它。

## 文案与主题

`CatalogApp` 接受 `locale/messages/theme/accent`；宿主也可通过 `HostAdapter.i18n/theme` 提供它们。默认文案键由 `src/ui/index.tsx` 的 `DEFAULT_MESSAGES` 管理；宿主翻译器对未知键返回键本身，组件回退到默认文案。资源作者的正文与描述保持原文。分类标签可用 `category.<id>`、子类标签可用 `subtype.<id>` 覆盖，ID 仍由正本生成。

CSS 变量限定在 `.pas-app` 内，`accent` 控制链接、选择与焦点等语义交互色。宿主可按主题提供合适的强调色，不需要复制页面或导入私有设计系统。

## 模板与设计系统 profile（2026-10-07）

`Resource.template` 可选提供 instructions/framework/example/support 的文件位置及独立风格策略；`Resource.design_system` 可选提供 manifest/rules/tokens-css/example/support 的文件位置。宿主不能把示例外观固化为模板身份或向公共模板写入固定 design_system_id。模板与系统的选择/应用仍由宿主现有能力处理，公共包没有新的样式执行器或安装内核。

这两种 profile 是 v3 的可选扩展；旧候选可以继续浏览并显示待补充。当前上游 mixed 候选仅显示真实文件与限制，不能因预览成功开放安装。具体来源/分类修订见 [最新验收](evidence/template-decoupling/acceptance.md)。

## 全目录浏览与未审核发现记录

`Catalog.discovery` 是可选的独立发现索引，不是严格 `Resource` 数组。公共包新增 `getBrowseResources`、`filterBrowseResources`、`getBrowseResource`；它们输出 `BrowseResource` 供同一UI展示。未知内容上游保持null，具体核查缺口和原链接由发现记录说明；`getResource`/`filterResources` 继续只处理严格资源。

发现入口映射已登记资源时，通过只读 `discovery_aliases` 保留原始名称、分类和URL，旧ID能访问目标详情，搜索能命中旧名，但只产生一张资源卡片。分类按目标资源的当前主类，不因历史别名把同一资源放进多个主类。

发现条目不提供安装、应用或伪造个人状态；宿主操作仍只接收原始真实Resource。26个平台来源单列在来源档案，未算成资产。集合/规范/教程入口与单条资源分别说明，不能把它们的项目级许可、热度或历史official标签推导成逐项验证。
