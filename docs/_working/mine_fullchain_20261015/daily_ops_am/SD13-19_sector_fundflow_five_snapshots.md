---
doc_type: mining_segment_doc
parent: docs/_working/mine_fullchain_20261015/00_skeleton.md
map_node: config/trading_day_cycle_map.yaml#D13-19
segment: fig13-B 盘中
mined: 2026-10-15
miner: daily_ops_am
ttl: task_bound
---

# SD13-19 板块资金流日内五快照

## 1. 定义

交易日五拍（上午两拍、下午两拍、收盘后一拍 15:05；时点语义见 ps1 声明面）Windows 计划任务 ZephyrAlpha_IntradayFundFlow 采集板块资金流快照落库——**完全不在 APScheduler 视野内**（独立 ps1 注册）。差分分析需段内至少 1 快照；五拍未跑完前（15:05 前）快照数不足属正常非断供。决策问题：日内五快照都落库了吗？段内快照数够下跌段差分吗？

地图在册态：wiring=wired、build=built、skeleton ✅；证据：留痕两拍各 90 个行业、落库各 90 行+表侧 max 为当日（三证齐）。tdm_refs=TDM-E-L2-01-4。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | 资金流外部源（行业级，每拍 90 行业） | `scripts/tasks/register/register_counter_trend_feeder_tasks.ps1:11`（采集器声明） |
| 输出面 | 板块资金流快照表（当日 max + 逐拍 90 行） | `logs/fundflow_collect.log`（exec_evidence 复跑：逐拍行业数与落库行数同为正） |
| SSOT 真源 | 图13 节点契约（行 1535-1610）+ 注册脚本五拍时点声明面 | `config/trading_day_cycle_map.yaml#D13-19`；`scripts/tasks/register/register_counter_trend_feeder_tasks.ps1:80` |
| 代码模块 | 采集执行体+计划任务注册（机制=B_windows_task，resource_optimization 引擎族） | `scripts/tasks/register/register_counter_trend_feeder_tasks.ps1`；`src/zephyr/signal_ashare/counter_trend_board.py:4`（消费点） |
| 门禁约束 | .ps1 纯 ASCII 铁律；跨机制漏拍风险（独立 ps1 不在 APScheduler 视野=排班三表不可见，GATE-SCHEDULE-CONSISTENCY 826 不覆盖） | `AGENTS.md` §9.7；`config/trading_day_cycle_map.yaml#D13-19` note_zh |
| 自动化触发 | mechanism=B_windows_task，交易日五拍；trigger_facts last_run=2026-10-08T15:05:01（240h 窗内 count=1）；schtasks registered=true 双证 | `config/trading_day_cycle_map.yaml#D13-19` trigger_facts/machine_facts |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 90 行业/拍源稳定 |
| 输出面 | pass | 三证齐（留痕/落库行数/表侧 max），verified_scope=production |
| SSOT 真源 | pass | 节点契约+声明面双证 |
| 代码模块 | pass | 注册 ps1+执行体+消费点实存 |
| 门禁约束 | pass | ASCII 铁律适用且脚本为纯 ASCII 族（注册脚本族惯例）；invalidation 注记防误判 |
| 自动化触发 | pass | 五拍 last_run 在窗 |

## 4. 缺口与建议

- 图13 全图缺口在本格的落点：无；B 段健康样板之二（与 D13-11 同批 ✅）。
- gap_refs 空；fallback=「错过即缺拍，段内差分退化」已知取舍。
- 建议：唯一风险面=跨机制不可见（schtasks 族排班盲区），建议资源画像补该任务 window_expr（同 D13-07 漏拍问题），归属排班族工具链统一处置。
