---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：待办已闭环。处置=**软归档**。**
>
> **✅ 已完成（2 条，摘录）**
> - L111: - [x] 子代理审查 R2（A2 符号+修复核验 / B2 加载链+登记）→ A2 pass（229 函数体传递闭包审计 0 序依赖问题）；B2 抓出 1 blocker+1 minor 已修复：
> - L112: - B2-blocker：既有 pending 规划条目 F-STOCKQ-TIMELINE（自定义时间轴，sq-timeline.js 待建，SOP §六 #14）在修复窗口期被整条删除——已恢复原 6 行（347 条/零重复/双 id 并存）
>
> **⚠️ 未完成**：无待办信号
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 1 个，其中判废弃 0、路径漂移 0）+ commit 提及 3 处。
>
> **处置建议**：软归档。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）


# 前端全量拆件施工清单（2026-09-12 夜班自主批，SOP Step 1）

> task_bound 临时文档：本次拆件批的规划/裁定/执行记录，施工完成并提交后本文件保留作审计 trail。
> 依据：[frontend_component_split_sop.md](../01_policies_and_standards/sop/frontend_component_split_sop.md) v1.3.0 · TRAE-086 v1.2.0 · FEH-PC-008。
> 会话：sess-38668-20260912015945（GitCommitGateway 直提路径，worktree 因 WORKSPACE_DRIFT_BLOCKED 降级可选——TRAE-079 Phase 2）。

## 一、盘点结论（46 页 + web/ 全树）

| 区域 | 现状 | 判定 |
|---|---|---|
| pages/*.html（46 页） | 全部纯 HTML 片段，**零内联 `<script>`**（tdm/chainmap 仅 `<style>`） | ✅ 合规（pages/=页面片段），不动 |
| core/app1.js | **7115 行 / 34 区块 / 441 顶层声明**，混装 ~30 个页面引擎 | ❌ 唯一大杂烩，本轮主拆对象 |
| core/backtest.js 813 / services.js 227 / datasrc.js 99 / download.js 264 / bridge.js 125 / home.js 191 | 页面引擎错放 core/（core/ 现有 13 文件 > TRAE-086 ≤10 帽） | ❌ 迁 features/<page>/ |
| core/app2/3/4.js | 长城批 IIFE 渲染批（共 ~370 行，多页混装） | ⚠️ 接受保留（迁移=为拆而拆，见裁定 R4） |
| core/dockpilot.js / loader.js / event_bus.js | 启动器/布局引擎/事件总线 | ✅ 正宗 core 职责，不动 |
| features/**（13 文件） | 模块契约组件（registerFeature） | ✅ 不动（tdm.js 有专属测试契约，本轮不拆） |
| services/api.js | 数据通道 | ✅ 不动 |

## 二、自裁定记录（Owner 委托夜班自裁，第一性原理）

- **R1 拆分粒度=Tier-1 物理模块化**：app1.js 34 区块按既有 `/* ==== */` 语义边界拆为独立 feature 文件，**全局函数名零改动**（页面 onclick 全靠全局名绑定，改名=46 页 HTML 全 churn=高风险零收益）。registerFeature 契约化改造（含 HTML onclick 重接线）登记为 Tier-2 后续批，本轮不做。理由：TRAE-086 notes 点名的事故族根因是"改一处读六千行"的**文件级**单体；先消文件单体，契约化留待数据源接通时逐件做（对标 stockq sq-* 先例：接真源时才拆组件）。
- **R2 跨文件提升失效→统一延迟执行批**：原 app1.js 单文件求值靠 JS 函数提升实现跨区块前向引用（实证：L3587 `usycRender()` 前向引用 L4657；L4824 `IND_CAT.forEach` 引用 L195）。拆文件后提升跨文件失效。治本：所有抽离文件的非声明顶层语句（渲染批/window.xxxInit 赋值/事件监听注册/setInterval）**逐字搬入文件尾 `setTimeout(...,0)` 延迟批**——宏任务晚于整条微任务加载链，语义=原"全文件求值完再跑批"，且消除全部加载顺序地雷。app1.js 留守 chrome 的自包含 exec 保持同步。
- **R3 加载链保序**：抽离文件在 loader.js 中按原区块顺序挂接（app1→新批→event_bus→api→既有 features→app2/3/4→迁移文件原槽位→其余不变），保证 sq-* 组件自举时宿主变量已定义（FEH-PC-012 竞态前提）。
- **R4 app2/3/4 不迁**：各 ~10-311 行的 IIFE 渲染批，迁出收益（core/ 计数 10→7 已靠 6 文件迁移达标）不敌 46 页链路 churn 风险；登记为数据源接通时随页拆的后续批。
- **R5 core/ 回收**：6 个页面引擎迁 features/ 后 core/=7 文件（app1..4/dockpilot/event_bus/loader）≤10 帽 ✅；不新增任何 core/ 文件（指标计算库/形态识别库随 idx 页放 features/index/，理由：R1 页面辖域放置，避免为"未来复用"预支抽象——消费方当前仅 index 页+factor 迷你图，均经向后引用覆盖）。
- **R6 features/tdm.js 与 features/cost-line.js 不动**：tdm.js 有 tests/frontend/test_dashboard_smoke.py 源码级断言契约+TDM 负责人会话职权边界；cost-line.js 是 SOP 点名 pilot 路径。两者单文件单页语义合规。
- **R7 禁区**：pages/index.html（Owner 专属重设计）零触碰——指数引擎抽离只动 app1.js 侧，页面 onclick 引用的全局名全部保留。
- **R8 演示数据零新增**：搬移的演示数组全部携带原"演示数据"标记，FRONTEND-TRUTH-SOURCE gate（warn 起步）审计照记；不造任何新数据。

## 三、app1.js 拆分明细（37 个新文件 + 薄宿主 ~261 行；行段以 .runtime/tmp_split_build.py 构建脚本 PLAN 为准）

| # | 新文件 | 原行段 | 内容 |
|---|---|---|---|
| 1 | features/warroom/wr-scenario-matrix.js | L77-176 | 作战室 3×3 情景矩阵+决策弹层 |
| 2 | features/index/idx-patterns.js | L251-2267 | 指标计算+形态识别纯函数库（对齐 PAT-* 注册表） |
| 3 | features/index/idx-engine.js | L177-250 + L2268-3343 | 指数详情页渲染引擎（表/窗格/交互） |
| 4 | features/factor/fc-mini-charts.js | L3588-3590 | factor 页迷你走势启动批 |
| 5 | features/overseas/ov-mini-cards.js | L3344-3380 | 外盘迷你卡 |
| 6 | features/overseas/ov-rank.js | L3625-3669 | 全球市场排名榜（IIFE） |
| 7 | features/t0/t0-intraday.js | L3381-3428 + L5204-5220 | T 分析分时图+做T回验命中 |
| 8 | features/sector/sector-contrib.js | L3429-3451 | 板块贡献度 |
| 9 | features/sector/sector-arc.js | L4629-4656 | 板块档案下钻 |
| 10 | features/overseas/usyc-curve.js | L4657-4674 | 美债收益率曲线 |
| 11 | features/position/tolerance-band.js | L4675-4689 | 组合容忍带 |
| 12 | features/warroom/wr-risk-cards.js | L3452-3587 | 风险卡族+启动批 |
| 13 | features/live/ord-ticket.js | L3591-3593 + L3670-3707 | 下单票据+日志过滤 |
| 14 | features/stock/stock-profile.js | L3708-4055 + L5221-5252 | 个股档案（含 F9 补强） |
| 15 | features/screener/scr-engine.js | L4056-4356 | 条件选股 |
| 16 | features/calendar/cal-engine.js | L4357-4471 | 事件日历 |
| 17 | features/review/rev-engine.js | L4472-4563 | 盘后复盘 |
| 18 | features/news/ann-panel.js | L4564-4599 | 公司公告面板 |
| 19 | features/policy/pol-panel.js | L4600-4628 | 政策资金面板 |
| 20 | features/live/live-equity.js | L4690-4722 | 盘中实时权益 |
| 21 | features/task/task-progress.js | L4723-4768 | 任务进度下钻 |
| 22 | features/search/srch-overlay.js | L4769-4880 + L7114-7115 | 全局搜索（含 srchLate 尾调用+fsArm/slimAnnot 调用行迁入） |
| 23 | features/position/pos-attribution.js | L4881-4908 | 盈亏归因+experiment 门控 |
| 24 | features/position/acct-multi.js | L4909-5044 | 多账号持仓 |
| 25 | features/position/perf-analysis.js | L5045-5147 | 收益分析（含 init 批调用） |
| 26 | features/sentiment/sent-margin.js | L5148-5203 | 两融情绪 |
| 27 | features/reglib/reg-engine.js | L5253-5514 | 注册表库 |
| 28 | features/pano/pano-engine.js | L5515-5598 | 架构全景 |
| 29 | features/modledger/mod-engine.js | L5599-5733 | 模块总账 |
| 30 | features/backtest/btr-links.js | L5734-5764 | 回测+策略链接（fwInit） |
| 31 | features/stockq/sq-host-engine.js | L5866-6197 | 个股行情二级页宿主引擎 |
| 32 | features/stockq/klp-mark-layer.js | L6198-6357 | 主图标注层 |
| 33 | features/stockq/klp-timeline.js | L6358-6452 | 时间轴 |
| 34 | features/stockq/klp-period-picker.js | L6453-6510 | 周期选择弹层 |
| 35 | features/stockq/klp-indicator-dialog.js | L6511-6798 | 指标设置弹窗 |
| 36 | features/cryptomarket/cm-engine.js | L6799-6946 | 币圈组引擎 |
| 37 | features/design/ds-spec-chart.js | L6947-7061 | DS-5 K 线规范图 |

app1.js 留守：L1-76 全局 chrome（go/gToast/fold/theme/lang）+ L135-137 决策弹层 + ovxGo/ovxFold（跨页折卡工具）+ fsArm + slimAnnot + tkXxx 底部 ticker（含同步自包含 exec）。

## 四、core/ 迁移明细（6 文件）

| 原 | 新 | 备注 |
|---|---|---|
| core/backtest.js | features/backtest/bt-engine.js | loader 槽位不变；manifest bt-framework-panel file 字段同步 |
| core/services.js | features/services/sv-page.js | /api/services-status |
| core/datasrc.js | features/datasrc/ds-page.js | /api/sources-status |
| core/download.js | features/download/dl-page.js | /api/download-status |
| core/bridge.js | features/bridge/br-page.js | /api/bridge-status |
| core/home.js | features/home/hm-engine.js | 首页三件套（保持"最后加载"槽位） |

## 五、验证计划

1. `node --check` 全部新/改 JS（语法级）。
2. 符号完整性脚本：拆分前后顶层声明集合与逐声明规范化文本全等（441 项零丢失零漂移）；exec 语句逐字保留（含延迟批内层）。
3. loader 链存在性：每个 loadJs 目标文件在盘。
4. `pytest tests/frontend/test_dashboard_smoke.py`（playwright 结构断言全绿）。
5. 46 页扫掠：go() 逐页导航收集 console error（零未捕获错误）。
6. 子代理审查（并发 2-3，memory 实证额度）→修复→复审，连续两轮 0 问题。

## 六、执行记录（施工中如实更新）

- [x] 盘点+裁定（本文件）
- [x] 施工批 A（app1.js 7116 行→37 文件+261 行薄宿主；441 顶层声明零丢失）
- [x] 施工批 B（core/ 6 文件迁移 features/，头注释同步更新）
- [x] 施工批 C（loader 链 43 项挂接+ZK_BUILD=20260912-1；manifest+42 条目；frontend_map v2.3.0+42 条目+18 处迁移引用修复；ACC 42 份；creation_tokens 43 个；手册 FEH-PC-020+修订 2.0.0）
- [x] 验证：node --check 64 文件全过；loader 链 72 目标全存在；pytest tests/frontend/test_dashboard_smoke.py 6/6 绿；47 页扫掠唯一错误=stock 页 ERR_CONNECTION_REFUSED，经 HEAD 基线对照实验证实为**拆分前既有**（pano 页 8765 静态文档服务探针，.catch 诚实降级，8890 API 未起环境的预存在噪音）——拆分引入零 console 回归
- [x] 子代理审查 R1（A 符号完整性/B 加载链/C 登记治理 三代理并发）→ 2 blocker+1 登记 bug+若干 minor，全部修复：
  - A-blocker：fsArm()/slimAnnot() 调用行随 app1 提前执行，晚创建的加载期渲染卡拿不到 ⛶ 武装/注解收敛——两调用行迁至垫底的 srch-overlay.js 尾部（=原"全部加载期渲染之后"语义）
  - B-blocker：ovxInitSparks IIFE 留守宿主前向引用 drawLine/genCandles（DOM 守卫掩蔽的死代码地雷）——迁至 ov-mini-cards.js 尾部
  - C-blocker：manifest 追加脚本 bug（lines 构造在循环外）只落 1 条——重写为真 42 条目，version 1.1.0
  - C-major：F-STOCKQ-TIMELINE 撞既有 pending 规划条目→本批更名 F-STOCKQ-KLP-TIMELINE（map/manifest/ACC/token 四处同步）；F-SEARCH-OVERLAY page=search 悬空（无 search 页）→ 全局 overlay 不入 frontend_map（widgets 同口径），manifest page: none，ACC item3 改全局断言
  - minor：loader 头注释时效性、home.html/迁移 ACC 注释路径、手册 frontmatter 2.0.0
- [x] 子代理审查 R2（A2 符号+修复核验 / B2 加载链+登记）→ A2 pass（229 函数体传递闭包审计 0 序依赖问题）；B2 抓出 1 blocker+1 minor 已修复：
  - B2-blocker：既有 pending 规划条目 F-STOCKQ-TIMELINE（自定义时间轴，sq-timeline.js 待建，SOP §六 #14）在修复窗口期被整条删除——已恢复原 6 行（347 条/零重复/双 id 并存）
  - B2-minor：ACC-F-SEARCH-OVERLAY 关联.frontend_map 悬空——改为注明"不入 map（widgets 同口径）"
  - A2-minor：srch-overlay 尾注释"垫底加载"措辞失准——改为"37 页面引擎文件最后一个（其后仍有约 30 个契约件/app2-4）"
- [x] 子代理审查 R3（全新全量双代理）→ **双 pass**：代码向=603 顶层声明多重集等价/37+宿主覆盖 HEAD app1 7115/7115 行/237 条顶层执行语句一一对应/72 项加载链作用域感知闭包审计零违规/node --check 70 文件零错/冒烟 6/6；登记向=manifest 64 条/map 347 条双 id 并存/42 ACC 双射/43 token 双射/手册三处 2.0.0 一致/tdm 交叉负检零污染。可行动 minor 已当场修复：klp-timeline.js 头注释旧 ACC id→KLP-TIMELINE；blueprint.md（watchdog 派生收敛产物）与他会话 tdm×2 从提交 pathspec 剔除；rename 6 旧路径纳入 pathspec
- [x] 子代理审查 R4（连续第二轮 0 问题即通过）→ **pass，0 blocker/0 major**：六项终审（门禁自测/加载链语法/5 个时序敏感文件加载期引用 acorn 审计 0 违规/登记一致性 20 断言 20 过/冒烟 6/6/提交清单卫生 94 路径零夹带）。**R3+R4 连续两轮 0 问题，审查门通过**
- [x] GitCommitGateway 落地（并发风暴下的穿行实录）：
  - 提交窗口竞态实录：4-5 个并发会话+守护进程秒级搅动共享索引——FOREIGN-CHANGE 对"先编辑后 claim"的结构性误判反复阻断；overlap 配额（per-session 24h≥5）烧光；worktree 被他会话 WIP 挡死（WORKSPACE_DRIFT_BLOCKED，不可代清理）
  - 最终落地路径：c1a（45 运行时 js）+c2（manifest/map/home.html）经 commit_queue 异步落库（32b0d0118c/5ea1c90cc2）——队列路径无 claim 快照，FOREIGN-CHANGE 明文 PASS；剩余 c3/c4/删除侧经续作 session 的 last-resort allow_overlap 单提交收尾（配额=per-session 设计，标记留审计）
  - 他会话提交核实：近 5 commit 零前端文件（tdm RED_GLYPH 与 watchdog blueprint.md 未被吸收）

### 遗留登记（不在本批范围，交后续批）

- ~~frontend_map 幽灵引用~~ → **已治理（2026-09-12 深夜续批）**：245 条 auto_scanned 幽灵条目（core/<page>.js 从未存在）按"条目内容检索归属真源"全部修复——9 条命中拆分引擎文件、236 条归属页面片段 pages/<page>.html（区块普查条目的自然归宿）；frontend_map v2.3.1；7 条 status:pending 规划条目（sq-kline-main 等待建族）为合法占位保留
- **Tier-2 契约化（零件级拆分）——Owner 最终裁定（2026-09-12 二次对话拍板，取代同日路线 A）**：**触发器=页面彻底定型，定型一页拆一页**。页面反复修改期拆零件=零件随大改作废（浪费时间）；零件化的收益（优化个别组件只动一个零件）只在页面定型后兑现。未定型页保持"一页一总成"——这是**正式稳态而非欠账**。已落地判定：数据源接入只是定型条件之一，页面结构/交互不再大改才算定型。此前路线 A（等数据接入）/路线 B（全量立即拆）/路线 C（试点先行）均被本裁定取代。各页定型时按 stockq sq-* 样板逐件契约化（onclick 重接线随页施工）。
- **app2/3/4 批脚本**：多页混装 IIFE 渲染批留在 core/（迁移=为拆而拆，见裁定 R4）——随数据源接通逐页拆。
- **他会话 staged 改动**：features/tdm.js + pages/tdm.html 的 RED_GLYPH 红因徽章批系前班会话滞留暂存区，本批提交严格按 --files pathspec 避开，归属他会话。
