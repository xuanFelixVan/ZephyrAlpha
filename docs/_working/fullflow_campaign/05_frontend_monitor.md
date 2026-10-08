---
ttl: task_bound
completes_when: 全流通战役收官且最终交付报告落盘
---

# S5 前端与监控环节簿

> 战役: fullflow_20261008 ｜ 段: S5 前端与监控 ｜ 挖矿代理: F ｜ 日期: 2026-10-08
> 挖矿方式: 只读静态调研（源码 AST 提取 + import 冒烟，未启动任何服务器）
> 验证记录: Python 3.12.8（PATH 修正后）；`import zephyr.frontend.dashboard.api_server` 冒烟通过，`app.routes`=59（APIRoute 54 + 内建 Route 4 + Mount 1），与源码 AST 提取 54 条 API 路由完全一致。

## 一、输入面

- **上游数据**：S1 供给的 ClickHouse 行情（K 线/盘口快照导出）、S2 的信号与 TDM（config/trading_decision_map.yaml）、S3 的回测产物（artifacts 目录）、S4 的风控/regime 投影——api_server 全部路由即对这些面的只读投影。
- **配置真源**：config/strategy_production_map.yaml（factory 图）、config/governance_operations_map.yaml（govm 图）、config/trading_decision_map.yaml（tdm 图）、config/framework_plans.yaml（整装方案）、web/frontend_map.yaml v2.3.3（前端功能点唯一真源，364 条功能点行，D38 模块总线挂 module:MOD-*）。
- **运行时输入**：QMT 文件桥（E:\qmt_bridge\quote.csv 持仓/盘口）、tmp/*.heartbeat 心跳文件、数据源健康探针日志、alerter 告警流水。

## 二、输出面

- **可视面**：127.0.0.1:8890 单端口一体服务（API JSON + StaticFiles 直出 web/ 静态页面 54 页）——桌面壳唯一入口。
- **控制写回**：5 个 POST 路由把前端操作写回系统（发起回测/整装回测、服务启停、Owner 转正拍板、排产骨架确认）——前端是唯一人工控制台。
- **遥测输出**：dashboard-heartbeat 线程 60s 写 tmp/dashboard.heartbeat（供服务总闸判活）；服务控制审计 tmp/services_control_log.jsonl。
- **下游消费者**：Owner（人机门位操作面）、api.js（前端唯一 HTTP 通道）、takeover_pending_gate（L3 门禁读接管台账）。

## 三、入口面（启动命令 + 路由清单）

**启动命令**：`python -m zephyr.frontend.dashboard.api_server`（或 uvicorn 直跑；服务总闸控制台可一键重启）→ uvicorn 127.0.0.1:8890（log_level=warning，启动即设 SEM_FAILCRITICALERRORS=0x8003 防子进程弹窗风暴）。文档站已剥离至 `python scripts/serve_docs.py`（8765）。旧入口已弃用：app.py（Streamlit，v3.1.0 弃）、app_panel.py（Panel，2026-08-29 R22/R23 弃，保留作组件参考）。

**路由清单表**（api_server.py 5495 行，AST 静态提取，GET 49 + POST 5 = 54 条；另有 FastAPI 内建 /openapi.json、/docs、/redoc 与 Mount "/" 静态页面）：

| 方法 | 路径 | 用途 |
|---|---|---|
| GET | /api/health | 健康检查（手动冒烟入口，无 docstring） |
| GET | /api/kline | K 线 JSON（ClickHouse，period 1m/5m/15m/30m/60m/1d/1w/1M） |
| GET | /api/stock-header | 股票标题+关键数据（sq-stock-header/key-data/sector-tags 共用） |
| GET | /api/quote | 批量最新报价（sq-fav-list 组件） |
| GET | /api/position | QMT 文件桥真实持仓（sq-position-list） |
| GET | /api/events | 宏观事件日历（CH.calendar_event，非个股事件） |
| GET | /api/orderbook | 五档盘口（E:\qmt_bridge\quote.csv 快照导出） |
| GET | /api/stock-search | 股票搜索（代码/名称模糊匹配） |
| GET | /api/strategies | 策略库列表（StrategyRegistry+TickStrategyRegistry 真源） |
| GET | /api/battle-map-flow | 作战地图阶段树（策略所处环节模块真源，后端缓存 10min） |
| GET | /api/backtest-list | 回测产物列表（扫 artifacts 目录，created_at 降序） |
| GET | /api/backtest-detail | 回测产物详情（绩效三图/明细下钻，按 run_id 读全量 artifact） |
| POST | /api/backtest-run | 发起回测（入队后台执行，返回 task_id） |
| GET | /api/backtest-run | 回测任务状态轮询（backtest/整装两管道同构） |
| GET | /api/framework-plans | 整装方案清单（三套预设+子策略权重明细） |
| POST | /api/framework-backtest-run | 发起整装回测（后台串行线程池） |
| GET | /api/framework-backtest-run | 轮询整装回测状态（done 附 run_id 可跳详情） |
| GET | /api/signals | 个股最新信号（factor_synth+strategy_weight 双源） |
| GET | /api/signals-overview | 信号总览聚合（warroom：方向分布+强弱两端） |
| GET | /api/services-status | 服务总闸状态：启动项四态灯+CPU/内存+心跳年龄+整机水位 |
| POST | /api/services-control | 服务启停控制（start/stop/restart，分级开关） |
| GET | /api/sources-status | 数据源监管真源（健康探针+alerter 告警流水+KPI 聚合） |
| GET | /api/download-status | 表级下载实况（三库全表时间段/源/实时速率/VPN 联动） |
| GET | /api/reports | 报告归档只读投影（data/reports/ 落盘面直读，F115 R3） |
| GET | /api/data-asset | 库内资产总览（宽度/深度/完整度/缺口/存储层） |
| GET | /api/bridge-status | 交易通道监控真源（HTTP 桥健康+双通道延迟+miniqmt 退役倒计时） |
| GET | /api/tdm | 交易决策地图全量（前端原生实时渲染真源） |
| GET | /api/tdm/validation | 节点验证台账（c1_backtest.node_verdict，零写副作用） |
| GET | /api/tdm/verdicts | 全节点当前验证态地图（画布噪音/衰减徽章数据源） |
| GET | /api/factory | 策略生产全景图全量（config/strategy_production_map.yaml） |
| GET | /api/factory/ledger | 工厂台账统计（环节聚合+双窗及格名单+理由码分布） |
| GET | /api/factory/threehigh | E1D 三高候选榜（three_high_candidates.csv） |
| GET | /api/factory/candidates | 车道候选聚合（lane_b/c/c2/chain/g 五车道 CSV 投影） |
| GET | /api/factory/exam | C4 考试结果投影（strategy_screen verdict 过滤） |
| GET | /api/govm | 治理操作全景图全量（config/governance_operations_map.yaml） |
| GET | /api/chainmap-galaxy | 产业地图 L1 星系（族节点+族间边+全量链清单） |
| GET | /api/chainmap-cluster | 产业地图 L2 链层（链→环节 tier 三值分列+结构边） |
| GET | /api/chainmap-node | 环节公司面板（环节↔公司映射，龙头/核心优先） |
| GET | /api/chainmap-search | 产业地图搜索（链/环节/symbol 落位/公司名） |
| GET | /api/chainmap-catalyst | 产业链催化剂（宏观事件→主题→行业→链命中定位） |
| GET | /api/chainmap-company | 公司详情卡（链上落位+上下游+CH 行情/市值+股权域） |
| GET | /api/chain-impact-stream | 盘中事件冲击流（新闻→情绪→链传导→冲击标的） |
| GET | /api/pattern-events | 形态事件查询（market_pattern_event，按 symbol 倒序） |
| GET | /api/pattern-winrate | 形态胜率查询（四窗×regime 切片） |
| GET | /api/pattern-evidence | 形态证据查询（REG-PAT-001 evidence 直读） |
| GET | /api/promotion-advisories | 策略转正建议清单（C5 审批页数据源） |
| POST | /api/promotion-decide | Owner 拍板 approve/reject（批准=进整装组合） |
| GET | /api/ops-notifications | 运营告警通知清单（promotion 页横幅数据源） |
| GET | /api/risk-status | 风控实况只读投影（作战室风险卡真源，W-E1） |
| GET | /api/regime/current | 7 态市场 regime 只读投影（W-E2） |
| GET | /api/budget-advisories | AI 层预算建议清单（budget 页数据源） |
| GET | /api/schedulegate-queue | 排产队列投影（schedulegate 页，只读） |
| GET | /api/schedulegate-skeletons | 骨架级提案包（利弊对照+两问打分展示） |
| POST | /api/schedulegate-confirm | 骨架级一键确认（C9 确认态落 confirm_gate 三落点账） |

**前端取数通道**：web/services/api.js（191 行）= `ZK.api` 唯一 HTTP 通道，fetch(BASE=127.0.0.1:8890)+AbortController 超时（GET 5s/POST 15s，冷盘路由放宽至 15-20s）；错误契约 `{"ok":false}` 必 reject → 调用方回退演示数据并标"演示"角标（演示诚实纪律）。

## 四、模块面

| 模块 | 路径 | 一句话 |
|---|---|---|
| HMI Core（MOD-L08-001） | src/zephyr/frontend/dashboard/api_server.py | 8890 单端口只读+受控写 API 服务（5495 行，54 路由，[MATURITY] production） |
| 前端静态面 | src/zephyr/frontend/dashboard/web/ | pages/ 54 页 HTML + features/ 40 项域模块 + core/ 8（app1-4/event_bus/loader/pool/dockpilot）+ services/api.js |
| 服务总闸 | src/zephyr/frontend/dashboard/services_registry.py | 启动项注册表唯一真源（实测 35 启动项，四态灯 DS-12，分级开关，60s 缓存探测） |
| 顶层视图 renderer 族 | src/zephyr/frontend/{graph_view,lineage_view,trace_waterfall_view,value_stream_view,domain_mapping_view,compliance_dashboard,frontend_api_proxy,notification_router}.py | 图/血缘/瀑布/价值流/域映射/合规/代理/通知路由 8 个独立视图件 |
| 提交性能周报 | scripts/governance/commit_perf_report.py | 提交性能与并发健康周报（正式占比≥70%/机器伴生比≤30%/竞态≤4 每日/四维判级聚合） |
| 接管台账 | scripts/governance/session_takeover_ledger.py | 死会话资源接管台账（--scan/--list/--resolve；账本 .runtime/takeover_ledger.jsonl） |
| 域验收卡 | docs/03_modules/_domain_frontend/ | 145 文件（36 md + 16 模块子目录）；acceptance/ 98 文件=68 张 ACC YAML 验收卡+28 截图+2 md |
| 前端全景图 | web/frontend_map.yaml | v2.3.3，364 功能点行，唯一真源（backend_ref 类型化挂 module:/api:/none:） |

## 五、自动化面

- **已自动**：dashboard-heartbeat 遥测线程（60s，daemon 随主进程，M10 豁免留痕在案）；判死钩子自动落接管台账（session_concurrency list_active 热路径内触发，refresh 节流 600s）；服务总闸 60s 缓存自动探测（psutil+心跳+端口+schtasks）；前端各页定时轮询刷新（api.js 周期拉取）；commit_perf_report 计划任务（register_commit_perf_report_task.ps1 注册）。
- **手动触发**：api_server 本体启动（manual，[STARTUP] 标注；服务总闸可一键重启）；回测/整装回测发起（POST 后入队后台执行，轮询取态）；services-control 服务启停（分级开关 free/confirm/guard/external/self，写审计日志）；promotion-decide 与 schedulegate-confirm（Owner 人机门位，逐笔拍板）。
- **永久系统四要素符合性**：api_server=手动启动的服务进程（非永久系统，心跳/降级/日志面齐）；无 cron/sleep-loop 常驻（M10 豁免仅限进程内生遥测线程）。

## 六、缺口面（[绿|黄|红]）

- [绿] 路由面完整闭环：54 路由 AST 提取与 import 冒烟 app.routes 双实证一致；错误契约 ok:false 全覆盖，静态 web 目录缺失自动降级纯 API（日志可见）。
- [绿] 测试面在岗：tests/frontend/ 2 件（route_guard_order/main_guard_order）+ tests/infra/frontend/ 28 件（heartbeat/schedulegate_confirm/reports/ch_timeout/cron_single_source/dashboard_smoke 等）。
- [绿] 旧入口治理干净：Streamlit/Panel 双弃用均带 Owner 裁定留痕，保留不删有明确参考价值声明。
- [黄→已收口 10-08] 写端点授权声明漂移：api_server 头注 [INVARIANTS] 写"四个获准写端点"（backtest-run/framework-backtest-run/services-control/promotion-decide），实际 POST 路由 5 个——schedulegate-confirm（L5433）未入头注授权清单（路由自身带 confirm_gate 三落点账与 owner_gate 声明，授权链在但头注不同步）。**st-fullflow2 10-08 已修**：头注 INVARIANTS 升"五个获准写端点"并补 schedulegate-confirm 授权链注记，docstring 端点清单补第五端点行。
- [黄→已收口 10-08] 监控文案数字漂移：/api/services-status docstring 写"16 启动项"，services_registry 实测 len(SERVICE_CATALOG)=35（2026-09-25）——路由文案未随目录增长更新。**st-fullflow2 10-08 已修**：services-status docstring 与服务总闸注释两处 16→35（len(SERVICE_CATALOG) 现值口径）。
- [黄] frontend_map.yaml 364 功能点含 auto_scanned=true 待逐页人工复核转正（scan_frontend_pages.py 半自动补登，未全转正）。
- [黄] /api/health、/api/kline 两路由无 docstring（AST 提取用途为空，仅头注可查）——54 路由中 2 条自描述缺失。
- [黄] CORS allow_origins=["*"]（方法收窄 GET/POST）——本机单用户面可接受，若端口暴露面扩大需收紧。

## 七、自审闸（三态总裁定）

**总裁定：绿（可运行）**——S5 前端与监控链路无断链：
1. 路由清单经源码 AST 提取与模块 import 冒烟双重实证（54/54 一致，app.routes=59 全解释）；未启动任何服务器。
2. 前端静态面（54 页/40 特征域/ZK.api 单通道）与监控对账面（commit_perf_report/takeover_ledger/services_registry/backup_reconciler）全部源码定位在案。
3. 六向台账齐；黄项 5 条均为文案/转正级漂移（头注授权清单、启动项计数、auto_scanned 转正、docstring 补登、CORS 收紧），无一断链，不阻断全流通。
4. 本簿为唯一交付文件，未改其他任何文件；建议后续批次收口上述黄项（同一 commit 内头注+docstring 同步即可）。
