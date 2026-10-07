# 完整资源目录验收

本轮纠正此前只展示代表样例、主要补入设计系统的覆盖缺口。用户明确指出 GitHub 原项目资源更多，并要求全面考虑；现在原发现队列与固定 OpenDesign 全入口均有真实浏览去向，仍保留五主类和框架/风格独立边界。

## 实际目录

| 类别 | 可浏览条目 |
|---|---:|
| 模板框架候选 | 25 |
| Skills 与方法/参考入口 | 272 |
| 提示词及教程/合集/规范入口 | 31 |
| 插件、MCP、CLI及工具线索 | 653 |
| 设计系统及参考入口 | 185 |
| 总计 | 1166 |

其中367条是严格Resource记录，799条是独立发现线索；60个关联发现入口附在目标资源下，不重复计为卡片。26个平台单列为来源，不计入条目总数。全部资源仍无宿主实测，不代表1166项已可安装。

## 逐条覆盖

- GitHub原777条资产线索有777个唯一outcome，原始803条YAML字节保留。MCP/CLI在插件类别浏览；旧design-docs中的工具、规范、原则按实际记录重映射。平台保持来源身份。见 [legacy-index.json](legacy-index.json)。
- 固定OpenDesign的114个design-template指令入口与163个Skill入口共277项，全部有内容哈希、文件证据、分类和target/reason；195个候选记录已合入，82个关联/参考入口已通过DiscoveryEntry显示。50个风格/共用框架引用与10个既有资源匹配均能用原名搜索并查看原址，22个未确认独立框架的入口保持可浏览参考。见 [上游覆盖](../../opendesign-directory-coverage.md) 与 [机器清单](opendesign-inventory.json)。
- 原172条Resource字段完整保留，逐项许可、审核、生命周期没有变化；新增195条保持pending、tested_hosts=[]。严格Resource与DiscoveryEntry契约分开，未知内容上游保持null，不以目录站当作者/内容源，不编造组件或安装路径。
- [final-data-audit.json](final-data-audit.json) 对账数量、目标、原字节、未知状态和公开数据边界；覆盖守卫直接从原输入与已生成产物比对，不靠写死总数证明去向。

## 页面与模块检查

- 最终生产bundle `index-9Tf1wpOG.js`；主页面显示“1166个目录条目 / 367已登记资源 / 799发现线索”，避免把发现入口称为已审核资产。
- 旧Skills/MCP/CLI/提示词/design-docs代表条目均能ID直开和刷新，保留原URL及待核查信息，发现条目没有宿主操作。
- 来源页面实际列出777条记录与26个平台；来源筛选Skills返回71条旧Skill入口；原名称`webapp-testing`可查，空查询反馈正确。
- 查询`html-ppt-zhangzara`只返回一次共用HTML Deck框架，详情保留47个关联入口和固定来源；风格名称未新增模板身份。
- 插件55页分页连续操作通过；390px无横向溢出，键盘类别切换、明暗主题与非默认强调色通过；阻断目录请求后出现错误，重试恢复1166条。
- [browser.json](browser.json)、[browser-final.json](browser-final.json)、[browser-errors.json](browser-errors.json) 是实际页面证据。浏览器PNG仅本地保留，不分发上游参考媒体。
- Node完整50项、TypeScript、生产构建、实际npm打包产物的宿主示例编译均通过，见 node-tests/typecheck/build/host日志。Python最终90项见 [python-tests-final.log](python-tests-final.log)；上游归档校验10项与发现索引4项也单独复跑。

## 实施细节与边界

纯浏览投影不会写回Resource。匹配旧入口时只保留别名、源地址与历史信息，搜索和来源筛选可命中，当前主类仍按目标资源，不把一个资源分进多个主类。未知作者/许可/内容路径与历史official/manual信息分别显示，未据此自动晋级。

上游盘点针对172条明确Git基线 `96839f9`，防止合入195条后重复读取活动正本产生循环匹配；实际新195条与提案完全一致。归档顶层目录和固定仓库身份均验证，错误归档在写报告前失败，保留旧报告字节。Linux/新环境测试使用调用方Python解释器，不依赖本机Xcode路径。

本轮仅独立项目、公共模块与目录。myApps、私人账号、数据库和旧Skill/提示词安装身份未修改；未push/发布/部署。正式账号安装与产品迁移仍在阶段2+。目录可浏览不等于逐项资源执行验收完成。
