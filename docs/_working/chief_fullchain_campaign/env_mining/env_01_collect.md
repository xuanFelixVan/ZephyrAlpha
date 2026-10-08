---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_01_collect.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-01 采集 挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案

- **真源锚**：config/data_supply_chain_map.yaml segments[S1_collect]（map_id=DSCMAP-012，机生 as_of=2026-10-04）；血肉卷=docs/_working/map_build/fig12_datachain/01_采集三段与源熔断.md
- **职责一句话**：23 家外部源经 provider 归一为 normalized rows（FetchPayload→FetchResult + CapabilityContract 启动期 fail-closed 校验）
- **节点清单（7）**：DSC-SRC 外部源面(partial)｜DSC-01 盘后批量采集(built)｜DSC-02 盘中实时/竞价采集(built)｜DSC-03 事件驱动采集(built)｜DSC-GAP-NEWSGHOST 幽灵引用(pending)｜DSC-GAP-MACRO 运行事故(pending)｜DSC-GAP-L2TICK 双0行断供(pending)
- **状态分布**：built=3 / partial=1 / pending=3（与 counts.segment_S1_collect=7 合）

## §1 六向台账

| 向 | 内部反查发现（带路径证据） | 全网/外部 | 判定 |
|---|---|---|---|
| ①上游 | 源面=23 家（map machine 层 distinct_sources=23；本批实抽 tasks.yaml 计 akshare=100/miniqmt=56/akshare_alt=38/internal=24/tushare=13，akshare_alt 较图 as_of 10-04 的 36 增 2＝机生层未重建的漂移，只录不改）。归一入口 FetchPayload(src/zephyr/data/provider_base.py:58)/FetchResult(:97)/CapabilityContract(:124，"不一致则阻断启动(fail-closed)"行 128 在码)。error_classifier 分级 unrecoverable/recoverable/unknown（src/zephyr/data/error_classifier.py:106-117） | 业界常规=主源限流→按序 failover 备源+异常分级（网络超时重试/环境性故障换源/逻辑错误止损），与本仓 classifier+fallback_sources 同构，无反例 | signal |
| ②下游 | grep 消费方（排除 data 域）12+ 文件：src/zephyr/alt_data/cohort_daily_ledger.py、alt_data/emotion_index_builder.py、backtest/core/matching_engine.py、backtest/core/cost_model_calibration.py、backtest/core/data_handler.py、backtest/core/preflight_checker.py 等；图内 consumers=TDM 16 表/约 64 点、SPM 276/56、code:matching_engine.py:1171、factor/fundamentals.py:24 | — | signal |
| ③算法机制 | 熔断 SourceCircuitBreaker（src/zephyr/data/source_circuit_breaker.py:49 状态枚举/:57 类/:175 Registry）——全文件 grep 无 persist/save/json 落盘调用＝"纯内存重启即复位"（🌑-4）复核成立。五态预筛 source_health_check.py:52 streaks 落盘 data/source_health_streaks.json、:25 集成点 scheduler.start()。新闻去重=标题 MD5（src/zephyr/data/news_dedup.py:144/172/189）。盘中秒级竞价窗 6 段 cron+max_instances=1（图 note） | 外部无对应物可比（熔断留痕属仓内合规需求） | signal |
| ④后端代码 | src/ 全在盘：provider_base.py、scheduler.py、source_circuit_breaker.py、source_health_check.py、news_dedup.py、implementations/ch_tick_kline.py（tick→分钟K CH 内自拼）。scripts/ 无采集主执行体（执行在 src 调度面）。tests/：tests/data/data/test_l00_data_source.py、test_fx_ecb_provider.py、test_internal_compute_provider_cohort_daily.py、implementations/test_realtime_snapshot_tencent.py、implementations/test_akshare_etf_benchmark.py | — | signal |
| ⑤前端呈现（只登记不施工） | src/zephyr/frontend/dashboard/api_server.py、components/chart_factory.py、components/tick_replay.py、app_panel.py 及 web/features/stockq/*、web/features/download/dl-page.js 均命中 kline_daily/tick_data/news_data——原始行情表直供仪表盘图表与下载页 | — | signal（登记） |
| ⑥数据字段 | data_refs 六档期原始表族：kline_daily/stock_daily_basic/money_flow/tick_data/realtime_snapshot/kline_1min/l2_tick/suspend/news_data/macro_data/alt_fx_rate_ecb/crypto_kline_daily。新鲜度证据=图内 freshness_evidence（kline_daily max=2026-09-24 lag=0 双版并报 10108162/10108049）；今日 DB 读数按本批纪律不直查＝实查待施工批。l2_tick/suspend 双 0 行断供在册（GAP-L2TICK，L2 权限=💰-4 花钱可解） | — | signal/部分待验证 |

## §2 挖干自评

- **三扫收敛?** 收敛。图字段轮→代码轮→消费方轮三轮新增发现递减至零：仅剩 akshare_alt 38 vs 图 36 一处机生层漂移（生成器重建即吸收，不立新格）。
- **未挖长尾清单**：(a) 23 家源逐家行为档案（骨架 §7-B 有逐源计数，本批未逐家复核）；(b) 271 任务逐任务 fallback_sources 配置质量（machine 层 fallback_nonempty=39，配副源占比低=图 residual 在册）；(c) akshare_alt 新增 2 任务的档期归属复核。
- **🌑不可得清点**：①熔断历史上是否真触发过（纯内存无痕，旁证仅 data/failures/_circuit_breaker_fred 族 163 件 ls）；②今日 DB 新鲜度读数（本批禁直查 DB，标实查待施工批）。

## §3 挖后自审闸三态裁定

**方案封矿（built 三节点 DSC-01/02/03 + DSC-SRC）＋ 挂起排期（三个 gap 子项）**

- 理由（终局全貌量尺）：采集段已实现全自动——档期派工(wired_cron)、源切换、熔断、健康预筛全部无人工参与位置，production 三节点 trigger_facts 均判 alive（7 日窗 480/879/20247 笔打卡）。终局里采集就是这个形态，无"再多一步自动化"可做——继续施工=无位置。三个 gap 各有外因：L2TICK 解锁条件=L2 行情权限采购到位（💰-4，Owner 预算门位）；NEWSGHOST 解锁条件=SPM 侧改册（他域施工，非本环节）；MACRO 解锁条件=DSC-19 探测器扩口径落地（归 ENV-05 段施工项）。
- 挂起者解锁条件已各注于上；三者在解锁前不得以任何采集段施工遮盖。

## §4 挖矿日志

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| 1 | 图字段轮：S1 七节点 L0/L1/L2 字段全读（map:122-2471） | signal | 节点清单/状态分布/fallback residual 全录；slot 计数（六盘后槽 196 任务+盘中六槽） |
| 2 | 代码轮：provider_base/error_classifier/circuit_breaker/health_check/news_dedup 五件真身核验 | signal | CapabilityContract fail-closed 在码；熔断纯内存复核成立（🌑-4 维持）；health streaks 有落盘 |
| 3 | 消费方轮：原始表名全 src 排除 data 域 grep + 前端 grep | signal | 12+ 消费文件与 10+ 前端呈现点；matching_engine/cost_model_calibration 双锚与图 consumers 互证 |
| 4 | 漂移轮：tasks.yaml 每源计数 vs machine 层 | noise→登记 | akshare_alt 38 vs 36（+2），其余源序一致；归机生层重建吸收，不立新格 |
