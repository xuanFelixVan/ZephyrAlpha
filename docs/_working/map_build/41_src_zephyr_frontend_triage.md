---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.frontend（166 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.frontend（166 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：suspect_orphan=140，wired=15，wired_by_header=11；初判汇总：newmap=166

## 簇级 newmap 评估：它们构成一条流程线吗？（证据班长判断，终裁归 chief）

| 子域 | 台数 | tier 分布 | 语义 |
|---|---|---|---|
| dashboard/ | 149 | suspect_orphan=134，wired=13，wired_by_header=2 | 仪表盘（web 页面+features+static，人机界面） |
| （根）/ | 6 | wired=1，wired_by_header=5 | 顶层单文件模块 |
| implementations/ | 6 | suspect_orphan=1，wired=1，wired_by_header=4 | — |
| _extensions/ | 1 | suspect_orphan=1 | 扩展挂点（包扩展机制） |
| api/ | 1 | suspect_orphan=1 | API 路由层（fastapi 接口面） |
| core/ | 1 | suspect_orphan=1 | — |
| infrastructure/ | 1 | suspect_orphan=1 | — |
| models/ | 1 | suspect_orphan=1 | — |

**判断**：这批孤儿不是一条纵向流程线，是**一条横轴功能面被流程图漏挂**——frontend 的纵向流程事实是「数据→api 路由→dashboard 页面渲染→Owner 看板读数」，该流程的宿主=api_server.py 启动链与页面加载链，属**运行时拉起**而非 import 拉起，这正是 join checker 判孤的结构性原因（import 闭包看不见 HTTP/静态路由接线）。
建议：**newmap 不立项**（横轴功能图 frontend_map 已存在且非流程图，新立纵轴图违『一域一图』准入制），
改走 **挂载面补登**——api/ 子域挂图11（交付流水线·服务面）或图12（数据出口段），dashboard 页面族挂图11（交付物面），顶层单文件按语义逐台判；保留 6 台已豁免币圈页不动。
此判断为簇级建议，逐台终裁与挂载执行归 chief/各图车道。

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/frontend/_extensions/__init__.py` | frontend/_extensions | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/api/__init__.py` | frontend/api | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/compliance_dashboard.py` | ComplianceDashboard — 合规仪表盘数据器（MOD-FE-010）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/core/__init__.py` | frontend/core | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/__init__.py` | （无文档头，按文件名语义：__init__） | 2026-09-18（16天） | in=0/out=0·wired_by_header | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/app.py` | ZephyrAlpha Dashboard · Streamlit 仪表盘（已弃用 v3.1.0） | 2026-09-16（18天） | in=0/out=0·wired_by_header | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/components/alert_center.py` | alert_center · 告警中心面板组件（MOD-FE-003）。 | 2026-09-17（17天） | in=1/out=0·wired | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/components/backtest_performance.py` | backtest_performance · 掘金量化风格绩效分析可视化（v1.0.0, #ARCH-047） | 2026-08-21（44天） | in=2/out=0·wired | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/components/backtest_results.py` | backtest_results · 回测结果可视化组件（v3.0.0 Panel+HoloViz 重构, #ARCH-047） | 2026-09-17（17天） | in=3/out=0·wired | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/components/chart_factory.py` | chart_factory · 图表统一工厂（v3.0.0新增, #ARCH-047） | 2026-09-05（29天） | in=8/out=0·wired | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/components/connection_matrix.py` | connection_matrix — 全连接矩阵仪表盘面板（波 13 包 13.4，只当数据源）。 | 2026-10-01（3天） | in=1/out=0·wired | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/components/experiment_history.py` | D_FRONTEND — Panel「实验历史」Tab（C1 回测历史列表 + 多选横向对比 + 双净值对比视图）。 | 2026-09-16（18天） | in=1/out=0·wired | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/components/fitness_functions.py` | fitness_functions · Fitness Functions 仪表盘组件（v3.1.0 Panel 迁移, #ARCH-047） | 2026-08-21（44天） | in=2/out=0·wired | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/components/gate_statistics.py` | gate_statistics · 门禁统计组件（v3.1.0 Panel 迁移, #ARCH-047） | 2026-08-21（44天） | in=2/out=0·wired | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/components/knowledge_overview.py` | knowledge_overview · 知识库概览组件（v3.1.0 Panel 迁移, #ARCH-047） | 2026-08-21（44天） | in=2/out=0·wired | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/components/olap_trend.py` | olap_trend · OLAP 趋势组件（v3.1.0 Panel 迁移, #ARCH-047） | 2026-08-21（44天） | in=2/out=0·wired | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/components/task_progress.py` | task_progress · 任务进度看板组件（v3.1.0 Panel 迁移, #ARCH-047） | 2026-09-05（29天） | in=2/out=0·wired | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/components/tick_replay.py` | tick_replay · Tick 回放可视化组件（v3.0.0 Panel+HoloViz 重构, #ARCH-047） | 2026-09-17（17天） | in=3/out=0·wired | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/components/trade_panel.py` | trade_panel · 实盘交易面板组件（v3.0.0 Panel+HoloViz 重构, #ARCH-047, human_gated） | 2026-09-17（17天） | in=3/out=0·wired | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/core/app1.js` | （无文档头，按文件名语义：app1） | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/core/app2.js` | （无文档头，按文件名语义：app2） | 2026-08-30（35天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/core/app3.js` | （无文档头，按文件名语义：app3） | 2026-08-29（36天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/core/app4.js` | （无文档头，按文件名语义：app4） | 2026-08-29（36天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/core/dockpilot.js` | （无文档头，按文件名语义：dockpilot） | 2026-08-31（34天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/core/event_bus.js` | （无文档头，按文件名语义：event_bus） | 2026-08-31（34天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/core/loader.js` | （无文档头，按文件名语义：loader） | 2026-10-01（3天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/core/pool.js` | （无文档头，按文件名语义：pool） | 2026-09-14（20天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/backtest/bt-battle-stage.js` | （无文档头，按文件名语义：bt-battle-stage） | 2026-09-04（30天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/backtest/bt-engine.js` | （无文档头，按文件名语义：bt-engine） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/backtest/bt-live-tools.js` | （无文档头，按文件名语义：bt-live-tools） | 2026-10-01（3天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/backtest/btr-links.js` | （无文档头，按文件名语义：btr-links） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/bridge/br-page.js` | （无文档头，按文件名语义：br-page） | 2026-09-29（5天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/budget/budget.js` | （无文档头，按文件名语义：budget） | 2026-09-25（9天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/calendar/cal-engine.js` | （无文档头，按文件名语义：cal-engine） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/chainmap/chainmap-cluster.js` | （无文档头，按文件名语义：chainmap-cluster） | 2026-09-29（5天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/chainmap/chainmap-company-card.js` | （无文档头，按文件名语义：chainmap-company-card） | 2026-09-10（24天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/chainmap/chainmap-galaxy.js` | （无文档头，按文件名语义：chainmap-galaxy） | 2026-09-13（21天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/chainmap/chainmap-nav.js` | （无文档头，按文件名语义：chainmap-nav） | 2026-09-10（24天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/chainmap/chainmap-search.js` | （无文档头，按文件名语义：chainmap-search） | 2026-09-08（26天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/cost-line.js` | （无文档头，按文件名语义：cost-line） | 2026-09-01（33天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/datasrc/ds-page.js` | （无文档头，按文件名语义：ds-page） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/design/ds-spec-chart.js` | （无文档头，按文件名语义：ds-spec-chart） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/download/dl-page.js` | （无文档头，按文件名语义：dl-page） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/factor/fc-mini-charts.js` | （无文档头，按文件名语义：fc-mini-charts） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/factory/factory.js` | （无文档头，按文件名语义：factory） | 2026-10-01（3天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/govm.js` | （无文档头，按文件名语义：govm） | 2026-09-17（17天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/home/hm-engine.js` | （无文档头，按文件名语义：hm-engine） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/index/idx-engine.js` | （无文档头，按文件名语义：idx-engine） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/index/idx-patterns.js` | （无文档头，按文件名语义：idx-patterns） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/live/live-equity.js` | （无文档头，按文件名语义：live-equity） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/live/ord-ticket.js` | （无文档头，按文件名语义：ord-ticket） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/modledger/mod-engine.js` | （无文档头，按文件名语义：mod-engine） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/news/ann-panel.js` | （无文档头，按文件名语义：ann-panel） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/overseas/ov-mini-cards.js` | （无文档头，按文件名语义：ov-mini-cards） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/overseas/ov-rank.js` | （无文档头，按文件名语义：ov-rank） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/overseas/usyc-curve.js` | （无文档头，按文件名语义：usyc-curve） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/pano/pano-engine.js` | （无文档头，按文件名语义：pano-engine） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/pattern/pattern.js` | （无文档头，按文件名语义：pattern） | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/policy/pol-panel.js` | （无文档头，按文件名语义：pol-panel） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/position/acct-multi.js` | （无文档头，按文件名语义：acct-multi） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/position/perf-analysis.js` | （无文档头，按文件名语义：perf-analysis） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/position/pos-attribution.js` | （无文档头，按文件名语义：pos-attribution） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/position/pos-signal-board.js` | （无文档头，按文件名语义：pos-signal-board） | 2026-09-04（30天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/position/tolerance-band.js` | （无文档头，按文件名语义：tolerance-band） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/promotion/promotion.js` | （无文档头，按文件名语义：promotion） | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/reglib/reg-engine.js` | （无文档头，按文件名语义：reg-engine） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/resourceweek/rw-data.js` | （无文档头，按文件名语义：rw-data） | 2026-10-01（3天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/resourceweek/rw-engine.js` | （无文档头，按文件名语义：rw-engine） | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/review/rev-engine.js` | （无文档头，按文件名语义：rev-engine） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/schedulegate/schedulegate.js` | （无文档头，按文件名语义：schedulegate） | 2026-09-28（6天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/screener/scr-engine.js` | （无文档头，按文件名语义：scr-engine） | 2026-09-14（20天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/search/srch-overlay.js` | （无文档头，按文件名语义：srch-overlay） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/sector/sector-arc.js` | （无文档头，按文件名语义：sector-arc） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/sector/sector-contrib.js` | （无文档头，按文件名语义：sector-contrib） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/sentiment/sent-margin.js` | （无文档头，按文件名语义：sent-margin） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/services/sv-page.js` | （无文档头，按文件名语义：sv-page） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/stock/stock-profile.js` | （无文档头，按文件名语义：stock-profile） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/stockq/klp-indicator-dialog.js` | （无文档头，按文件名语义：klp-indicator-dialog） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/stockq/klp-mark-layer.js` | （无文档头，按文件名语义：klp-mark-layer） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/stockq/klp-period-picker.js` | （无文档头，按文件名语义：klp-period-picker） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/stockq/klp-timeline.js` | （无文档头，按文件名语义：klp-timeline） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/stockq/sq-event-row.js` | （无文档头，按文件名语义：sq-event-row） | 2026-09-04（30天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/stockq/sq-fav-list.js` | （无文档头，按文件名语义：sq-fav-list） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/stockq/sq-host-engine.js` | （无文档头，按文件名语义：sq-host-engine） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/stockq/sq-key-data.js` | （无文档头，按文件名语义：sq-key-data） | 2026-09-04（30天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/stockq/sq-order-book.js` | （无文档头，按文件名语义：sq-order-book） | 2026-09-04（30天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/stockq/sq-position-list.js` | （无文档头，按文件名语义：sq-position-list） | 2026-09-04（30天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/stockq/sq-quant-analysis.js` | （无文档头，按文件名语义：sq-quant-analysis） | 2026-09-04（30天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/stockq/sq-search-box.js` | （无文档头，按文件名语义：sq-search-box） | 2026-09-01（33天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/stockq/sq-sector-tags.js` | （无文档头，按文件名语义：sq-sector-tags） | 2026-09-04（30天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/stockq/sq-stock-header.js` | （无文档头，按文件名语义：sq-stock-header） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/t0/t0-intraday.js` | （无文档头，按文件名语义：t0-intraday） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/task/task-progress.js` | （无文档头，按文件名语义：task-progress） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/tdm.js` | （无文档头，按文件名语义：tdm） | 2026-09-30（4天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/warroom/wr-pool.js` | （无文档头，按文件名语义：wr-pool） | 2026-09-14（20天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/warroom/wr-risk-cards.js` | （无文档头，按文件名语义：wr-risk-cards） | 2026-10-01（3天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/warroom/wr-scenario-matrix.js` | （无文档头，按文件名语义：wr-scenario-matrix） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/features/warroom/wr-signal-strip.js` | （无文档头，按文件名语义：wr-signal-strip） | 2026-09-04（30天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/index.html` | （无文档头，按文件名语义：index） | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/klinechart-demo.html` | app { display:flex; width:100vw; height:100vh; } | 2026-08-31（34天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/klinecharts.min.js` | （无文档头，按文件名语义：klinecharts.min） | 2026-08-31（34天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/aichat.html` | （无文档头，按文件名语义：aichat） | 2026-08-29（36天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/aitask.html` | （无文档头，按文件名语义：aitask） | 2026-08-29（36天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/backtest.html` | （无文档头，按文件名语义：backtest） | 2026-10-01（3天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/bridge.html` | （无文档头，按文件名语义：bridge） | 2026-09-29（5天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/budget.html` | （无文档头，按文件名语义：budget） | 2026-09-26（8天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/calendar.html` | （无文档头，按文件名语义：calendar） | 2026-08-29（36天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/chainmap.html` | p-chainmap.active { display:flex; flex-direction:column; height:calc(100vh - 86px); } | 2026-09-13（21天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/datasrc.html` | （无文档头，按文件名语义：datasrc） | 2026-09-03（31天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/design.html` | （无文档头，按文件名语义：design） | 2026-09-01（33天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/download.html` | （无文档头，按文件名语义：download） | 2026-09-09（25天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/experiment.html` | （无文档头，按文件名语义：experiment） | 2026-08-29（36天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/factor.html` | （无文档头，按文件名语义：factor） | 2026-08-29（36天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/factory.html` | p-factory.active { display:flex; flex-direction:column; height:calc(100vh - 86px); } | 2026-09-14（20天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/fitness.html` | （无文档头，按文件名语义：fitness） | 2026-08-29（36天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/govana.html` | （无文档头，按文件名语义：govana） | 2026-08-29（36天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/govm.html` | govm-pipeline .gl { position:relative; display:flex; gap:14px; padding:0 0 18px 0; } | 2026-09-17（17天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/home.html` | （无文档头，按文件名语义：home） | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/index.html` | （无文档头，按文件名语义：index） | 2026-08-29（36天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/live.html` | （无文档头，按文件名语义：live） | 2026-09-05（29天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/macro.html` | （无文档头，按文件名语义：macro） | 2026-08-29（36天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/models.html` | （无文档头，按文件名语义：models） | 2026-08-29（36天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/modledger.html` | （无文档头，按文件名语义：modledger） | 2026-08-29（36天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/modlib.html` | （无文档头，按文件名语义：modlib） | 2026-09-01（33天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/news.html` | （无文档头，按文件名语义：news） | 2026-08-30（35天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/overseas.html` | （无文档头，按文件名语义：overseas） | 2026-08-30（35天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/overview.html` | （无文档头，按文件名语义：overview） | 2026-08-31（34天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/pano.html` | （无文档头，按文件名语义：pano） | 2026-08-29（36天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/pattern.html` | （无文档头，按文件名语义：pattern） | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/policy.html` | （无文档头，按文件名语义：policy） | 2026-08-30（35天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/position.html` | （无文档头，按文件名语义：position） | 2026-09-01（33天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/projmap.html` | （无文档头，按文件名语义：projmap） | 2026-08-31（34天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/promotion.html` | （无文档头，按文件名语义：promotion） | 2026-09-15（19天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/rating.html` | （无文档头，按文件名语义：rating） | 2026-08-29（36天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/reglib.html` | （无文档头，按文件名语义：reglib） | 2026-08-29（36天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/resweek.html` | rw-world .rw-grid { display:grid; grid-template-columns: 240px repeat(7, 1fr); gap:0; } | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/review.html` | （无文档头，按文件名语义：review） | 2026-08-29（36天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/schedulegate.html` | （无文档头，按文件名语义：schedulegate） | 2026-09-25（9天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/screener.html` | （无文档头，按文件名语义：screener） | 2026-08-29（36天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/sector.html` | （无文档头，按文件名语义：sector） | 2026-08-30（35天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/sentiment.html` | （无文档头，按文件名语义：sentiment） | 2026-08-30（35天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/services.html` | （无文档头，按文件名语义：services） | 2026-09-02（32天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/stock.html` | （无文档头，按文件名语义：stock） | 2026-08-29（36天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/stockq.html` | （无文档头，按文件名语义：stockq） | 2026-08-31（34天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/strategy.html` | （无文档头，按文件名语义：strategy） | 2026-09-02（32天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/sysstatus.html` | （无文档头，按文件名语义：sysstatus） | 2026-08-30（35天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/t0.html` | （无文档头，按文件名语义：t0） | 2026-08-30（35天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/task.html` | （无文档头，按文件名语义：task） | 2026-08-30（35天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/tdm.html` | p-tdm.active { display:flex; flex-direction:column; height:calc(100vh - 86px); } | 2026-09-12（22天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/pages/warroom.html` | （无文档头，按文件名语义：warroom） | 2026-09-14（20天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/services/api.js` | （无文档头，按文件名语义：api） | 2026-09-28（6天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/vendor/dockview/dockview.min.js` | （无文档头，按文件名语义：dockview.min） | 2026-08-31（34天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/dashboard/web/vendor/three/three.min.js` | （无文档头，按文件名语义：three.min） | 2026-09-10（24天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/frontend_api_proxy.py` | FrontendApiProxy — 前端 API 代理（MOD-FE-011）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/implementations/__init__.py` | D_FRONTEND — Human-AI Interface 具体实现包 | 2026-08-29（36天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/implementations/default_approval_gateway.py` | Default Approval Gateway — 默认审批网关 (MOD-L08-001 步骤2, B-007 审批载体) | 2026-09-02（32天） | in=0/out=0·wired_by_header | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/implementations/default_notification_manager.py` | Default Notification Manager — 默认通知管理器 (MOD-L08-001 步骤1) | 2026-09-02（32天） | in=1/out=0·wired | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/implementations/feishu_bot_sender.py` | FeishuBotSender — 飞书机器人推送器（MOD-FE-012）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/implementations/notification_channel_senders.py` | Email/WeChat 通知渠道 sender（MOD-L08-001 register_channel 生产接线位）。 | 2026-09-05（29天） | in=0/out=0·wired_by_header | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/implementations/wechat_bot_handler.py` | WeChatBotHandler — 企业微信机器人处理器（MOD-FE-013）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/infrastructure/__init__.py` | frontend/infrastructure | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/interface_base.py` | D_FRONTEND — Human-AI Interface Layer Skeleton | 2026-08-17（48天） | in=5/out=0·wired | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/lineage_view_renderer.py` | LineageViewRenderer — 血缘DAG渲染数据器（MOD-FE-008）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/models/__init__.py` | frontend/models | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/notification_router.py` | NotificationRouter — 通知路由器（MOD-FE-004）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
| `src/zephyr/frontend/trace_waterfall_view.py` | TraceWaterfallView — 端到端追踪瀑布视图器（MOD-FE-009）。 | 2026-09-17（17天） | in=0/out=0·wired_by_header | **newmap**（簇级评估见下节；倾向=挂载面补登非立新图） |
