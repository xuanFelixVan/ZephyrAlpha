---
ttl: task_bound
---

# M6 前端API链 · 分册 02 · api_server（8890 单端口一体服务）

> 挖矿会话 st-commitspeed-tbl-20260924 ｜ 2026-09-25 ｜ 只读挖矿。
> 真源文件：`src/zephyr/frontend/dashboard/api_server.py`（4561 行，FastAPI）。前端契约面：`web/services/api.js`。

## 一、环节定义与边界
一句话：把 ClickHouse/QMT 文件桥/治理注册表/调度种子等后端真源以 47 条 /api 路由 JSON 投影给 web/ 页面族，并经 StaticFiles mount 直出页面——8890 单端口一体（W6-1，2026-09-19，服务 2→1 故障面减半）。
- 供料方：DatabaseService（CH slot=dashboard）、QMT 文件桥（E:\qmt_bridge\Stock）、治理注册表族（config/*.yaml mtime）、ai_layer.scheduling、intelligence.budget_analyzer、strategy_pipeline.promotion_advisory、infrastructure.system_telemetry.alerts。
- 消费方：web/ 全部页面（api.js BASE=http://127.0.0.1:8890，api.js:7）；桌面壳健康探针（tools/desktop/main.js:42）。

## 二、六向台账
| 向 | 实测证据 |
|---|---|
| 上游输入 | CH 连接唯一经 DatabaseService 槽位领取（api_server.py:77-87 `get_db_service().get_clickhouse_conn(role="admin", slot="dashboard")`）；QMT 文件桥目录硬编码 `E:\qmt_bridge\Stock`（:115-116，GBK CSV 读取 :119-122）；策略元真源=两注册表（:786 `_strategy_rows`：StrategyMeta.name 中文+battle_map_ref 环节归属）；调度种子=seed_writer.load_seeds（:4526）；预算=budget_analyzer（:4505-4507）；转正=promotion_advisory（:4343-4345） |
| 下游消费 | api.js 47 方法逐条对映（api.js:27-163）；tdm.js/govm.js/factory.js 直连 API_BASE（绝对地址，tdm.js:20）；桌面壳 /api/health 探活；promotion 页=ops-notifications 唯一前端出口（:4414，2026-09-15 裁定飞书/SMTP 裁撤） |
| 自动化触发 | 模块导入即启动 3 个 daemon 线程：bt-strategy-warm（:870，策略注册表预热）、data-asset-audit（:2042，慢档 10min 自动重审 `_ASSET_TTL_SEC=600` :1813）、ops-alert-feed（:4459-4460，5s 首跳后每 30s tick；pytest 在 sys.modules 时不启动 :4459——测试隔离）；后台回测执行=线程池任务 `_bt_run_task`(:873)/`_fw_run_task`(:1009)；无 cron/计划任务直属本服务，进程由桌面壳 spawn 或服务总闸手拉 |
| 真源与注册表 | 头注 INVARIANTS（:8-10）："只读服务+四个获准写端点（backtest-run/framework-backtest-run/services-control/promotion-decide）写权限扩张均有授权留痕"；模块卡 TTL=permanent（:17）；TESTS=手动冒烟 /api/health + /api/kline（:15）；AI 层接线批（st-ailayer-final-20260924 遗产）=文件尾 :4495-4561 四路由+一诚实拒执行路由 |
| 门禁与质量尺 | 非法输入 fail-closed 返回 ok:false（:10）；CH 双道超时防线：socket send_receive_timeout=15s（:86）+ 服务端 max_execution_time=12s（:90,:104）；单连接非线程安全→`_ch_exec` 全局锁 30s 限时+异常弃连重建（:93-112，2026-09-03 假死实证加固）；GATE-20/LSG 不在本链（无 LLM 调用） |
| 当前运行状态 | 绿（代码级）。COMPILE_OK+IMPORT_OK 实测；app.routes /api 路由 47 条实测；黄点=前端侧消费缺口（01 册 §四-1）、schedulegate-confirm 诚实拒执行待 C9 批文（:4547-4561） |

## 三、子模块清单（路由级穷尽，grep @app 实测：GET 44 + POST 5 = 47 条 route，47 unique path）
### 3.1 只读 GET（44 条）
| 端点 | file:line | 真源 | 前端消费方 |
|---|---|---|---|
| /api/health | :164 | 常量 | 桌面壳探活 |
| /api/kline | :169 | CH kline_{1m..1M} 白名单表 `_PERIOD_TABLE` :61-70 | stockq K 线 |
| /api/stock-header | :205 | stock_basic argMax + kline_daily + daily_valuation | sq-stock-header/key-data/sector-tags |
| /api/quote | :279 | kline_daily 批量 | sq-fav-list |
| /api/position | :352 | QMT 文件桥 | sq-position-list |
| /api/events | :411 | 宏观事件表 | sq-event-row/日历 |
| /api/orderbook | :443 | QMT 文件桥五档 | sq-order-book |
| /api/stock-search | :501 | stock_basic | 全局搜索 |
| /api/strategies | :555 | 两注册表 `_strategy_rows` :785 | 回测页 |
| /api/battle-map-flow | :588 | battle_map_steps（BattleMapReader，TTL 600s :585,:597） | 作战地图 |
| /api/backtest-list | :647 | 产物目录+指纹缓存 :584,:634 | backtest 页 |
| /api/backtest-detail | :703 | 产物 JSON（127 万点 tick 冷盘 20s 超时预算，api.js:65） | backtest 详情 |
| GET /api/backtest-run | :978 | 任务状态投影 | 发起回测轮询 |
| /api/framework-plans | :1064 | config/framework_plans.yaml fail-closed | 整装组合 |
| GET /api/framework-backtest-run | :1172 | 任务状态 | 整装轮询 |
| /api/signals | :1183 | factor_synth+strategy_weight 双源 | pos-signal-board |
| /api/signals-overview | :1232 | 聚合 | warroom |
| /api/services-status | :1286 | services_registry.get_services_status + control_log | 服务总闸页 |
| /api/sources-status | :1329 | logs/source_health_*.log + data/failures/*.json（:1331-1333） | datasrc 页 |
| /api/download-status | :1683 | CH 146 表分区/行数/新鲜度 | download 页 |
| /api/data-asset | :2047 | 库内资产审计（内存缓存 600s+refresh=1 后台重审 :2019-2045） | datasrc 资产列 |
| /api/bridge-status | :2114 | HTTP 桥探活+桥文件族活性（:2061,:2087） | bridge 页 |
| /api/tdm | :2315 | config/trading_decision_map.yaml（mtime 缓存 :2144,:2325-2327） | tdm.js 一张图 |
| /api/tdm/validation | :2419 | CH c1_backtest.node_verdict 最近 20 条 | tdm 抽屉验证档案 |
| /api/tdm/verdicts | :2475 | CH c1_backtest.node_verdict 全节点最新 | tdm 噪音/衰减徽章 |
| /api/factory | :2597 | config/strategy_production_map.yaml（mtime 缓存 :2500,:2607） | factory 一张图 |
| /api/factory/ledger | :2654 | strategy_screen 台账统计（TTL 300s :2502,:2522） | factory 成绩区 |
| /api/govm | :2667 | 治理运营图 YAML（mtime 缓存 :2664,:2681） | govm.js |
| /api/factory/threehigh | :2731 | 三高筛选（mtime 缓存 :2727） | factory |
| /api/chainmap-galaxy | 3642 段内 | ig_* 聚类（TTL 600s :2784,:3096-3107） | chainmap L1 |
| /api/chainmap-cluster | （galaxy 后段） | 聚类簇详情（:3217,:3350，随 galaxy 失联失效 :3108） | chainmap L2 |
| /api/chainmap-node / -search / -company | （同段） | ig_company_edge 等 | chainmap 抽屉/搜索/公司卡 |
| /api/chainmap-catalyst | :3642 | 宏观事件→主题→行业→链命中（MOD-ALT-005 方向语义） | 环节催化角标 |
| /api/chain-impact-stream | :4140 | 事件影响流 | chainmap |
| /api/pattern-events | :4168 | CH c1_market.market_pattern_event（2300 万行，冷扫描秒级十位→前端 20s，api.js:149-153） | 图形库页 |
| /api/pattern-winrate | :4215 | 形态胜率切片（min_n=30 low_sample 纪律线） | 图形库页 |
| /api/pattern-evidence | :4278 | REG-PAT-001 evidence 直读 | 图形库页 |
| /api/promotion-advisories | :4329 | promotion_advisory.list_advisories + switch_engine.approval_router 双源（切换源异常只降级本段 :4366-4367） | 转正审批页 |
| /api/ops-notifications | :4423 | OpsAlertFeed.list_active（通知唯一前端出口） | promotion 横幅 |
| /api/budget-advisories | :4497 | budget_analyzer.analyze+render（AI 层接线批） | budget 页 |
| /api/schedulegate-queue | :4513 | load_seeds+dispatcher.rank_pending（tz-aware now 服务端注入） | schedulegate 页 |
| /api/schedulegate-skeletons | :4534 | seeds 内 owner_gate 提案（不占自动派工队列） | schedulegate 页 |

### 3.2 写端点（5 POST；4 获准+1 诚实拒执行）
| 端点 | file:line | 授权/语义 |
|---|---|---|
| POST /api/backtest-run | :918 | 回测产物写（获准写#1，后台线程 :873） |
| POST /api/framework-backtest-run | :1093 | 整装回测编排（获准写#2，线程池 :1009） |
| POST /api/services-control | :1296 | 服务编排（获准写#3；分级闸门在 services_registry：confirm 未带 confirm=true→need_confirm；guard/external 拒；self 仅 restart） |
| POST /api/promotion-decide | :4375 | Owner 拍板门位数字化（获准写#4：Owner 2026-09-15 通宵指令+宪法 §5；token=None 服务端自取密钥；执行器缺位 503 :4394-4398） |
| POST /api/schedulegate-confirm | :4547 | **诚实拒执行**：C9 确认态落点无 DESIGN 批文前恒 ok:false（:4551-4561）——不做假持久化 |

## 四、堵点与病灶
1. **【红】api.js 客户端层落后路由面（契约漂移实证）**：api.js 无 schedulegate 三方法（01 册 §四-1b），且 budget 走裸相对 fetch（01 册 §四-2）。后端路由已就绪（导入实测 callable：load_seeds/rank_pending/analyze/render_budget_advisory_payload 全 True）——断点纯在前端接线批。修法同 01 册。
2. **【黄】单 CH 连接串行化瓶颈**：clickhouse_driver 单连接非线程安全→`_ch_exec` 全局锁串行（:94-101）；chainmap-galaxy 首算 3-6s（api.js:111 注释）、pattern-events 冷扫描"秒级十位"（api.js:149）这类慢查询会占住锁，其余端点排队（锁 30s 未获即抛"CH 通道忙" :102）。历史已两次加固（弃连重建 :105-110、查询级 12s 超时 :90）。修法草案：连接池化（DatabaseService 多 slot 或 clickhouse-connect http 池），预估 2-3 天，需 DatabaseService 域协同（非本车道单方可修）。
3. **【黄】调度种子排序在请求线程内重算**：/api/schedulegate-queue 每请求 load_seeds()+rank_pending 全量打分（:4526-4528），无缓存——种子文档大时 30s 轮询（schedulegate.js:177）会反复重算。修法：仿 _BMF_CACHE 加 30-60s TTL。0.2 天，本车道可修（与 01 册接线批同批）。
4. **【黄】QMT 桥路径硬编码盘符**：`E:\qmt_bridge\Stock`（:116）裸编码，盘位迁移即断；且 api.js:104-108 注释披露 miniqmt 信号 2026-09-18 退役（券商清退）——退役日语义靠前端本地日期比较，属时间炸弹式契约。修法：路径入 shared.io.paths；retire 语义后端出字段（后端真源原则）。0.5 天+跨域协调。
5. **【灰】[TESTS] 头注为"手动冒烟"（:15）**：49 端点零自动化契约测试（仅直调归一注释 :3652 暗示部分进程内测试），api↔前端契约漂移（本册 §四-1）正是无契约测试的后果。修法：FastAPI TestClient 契约测试（禁写生产路径，tmp_path 隔离），按端点分级先写 5 写端点+高频读端点。1-2 天。

## 五、提速与合并机会
1. 三张"YAML mtime 缓存"图（tdm/factory/govm/threehigh 四端点同模式 :2144/:2500/:2664/:2727）可抽一个 `_yaml_map_cache(path, builder)` 装饰器——同真源多消费合并，删四处重复失效逻辑。
2. sources-status/download-status/data-asset 三数据监管端点同域（:1329/:1683/:2047），前端可合并为一次聚合拉取或后端合并路由，减轮询次数。
3. ai.js 逐方法手写与 api_server 路由面靠人肉同步——可机生：脚本扫 @app 路由产出 api.js 方法清单差集报告（喂给 01 册 §四-3 的 R4 门）。
4. 线程三件套（warm/asset/ops-feed）启动模式一致（导入即启+pytest 守卫），可抽 `_spawn_daemon(name, fn)` 收敛守卫逻辑。

## 六、自审闸三态
**挖干可施工**：47 路由全清单 file:line、真源/消费方两源交叉（api.js × api_server × 页面 js）、写端点授权链齐、三线程/缓存/超时防线实证。
- 挖干可施工：§四-3/4/5；配合 01 册接线批（§四-1）。
- 待裁：§四-2 连接池化（动 DatabaseService 域，跨域取舍需裁定）；§四-4 retire 日语义（时间炸弹过退役日再触发，届时裁定展示口径）。
- 缺口移交：端点运行态压测需起服务（本车道禁），移交施工批。

## 七、复核命令（10 分钟）
```bash
# 1. 路由清单复现（GET=44 POST=5）
grep -c '@app.get' src/zephyr/frontend/dashboard/api_server.py; grep -c '@app.post' src/zephyr/frontend/dashboard/api_server.py
# 2. 纯导入路由计数（应 47；pytest 桩防探针线程启动）
python -c "import sys,types;sys.modules['pytest']=types.SimpleNamespace();import zephyr.frontend.dashboard.api_server as m;print(len([r for r in m.app.routes if getattr(r,'path','').startswith('/api')]))"
# 3. 写端点授权头注复核
sed -n '8,10p;4377,4385p;4547,4561p' src/zephyr/frontend/dashboard/api_server.py
# 4. CH 防线复核（锁/弃连重建/双超时）
sed -n '90,112p' src/zephyr/frontend/dashboard/api_server.py
# 5. 前端方法缺口复核（应无输出）
grep -n "fetchSchedulegateQueue" src/zephyr/frontend/dashboard/web/services/api.js
```
