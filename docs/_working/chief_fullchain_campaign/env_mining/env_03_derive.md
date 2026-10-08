---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_03_derive.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-03 衍生 挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案

- **真源锚**：config/data_supply_chain_map.yaml segments[S3_derive]；血肉卷=docs/_working/map_build/fig12_datachain/03_衍生加工三族.md＋11_消费端需求反查.md
- **职责一句话**：internal DAG 任务 + 任务表外进程内写手把原始表加工为派生表
- **节点清单（10）**：DSC-07 技术指标/多周期重采样(partial)｜DSC-08 财务/一致预期派生 PIT 双守卫(partial)｜DSC-09 形态/情绪/板块状态衍生(partial)｜DSC-21 任务表外进程内派生生产(partial)｜DSC-HA 交接A出图(partial)｜DSC-GAP-CONSENSUSCHAIN 预期链停摆(pending)｜DSC-GAP-NAV 净值表零接线(pending)｜DSC-GAP-EXECEP 执行报告仅sim(pending)｜DSC-GAP-FFVAL factor_feature_value DDL未apply(pending)｜DSC-GAP-FFSIG factor_signal 未建表(pending)
- **状态分布**：partial=5 / pending=5（与 counts.segment_S3_derive=10 合；全链唯一零 built 段＝最重红区）

## §1 六向台账

| 向 | 内部反查发现（带路径证据） | 全网/外部 | 判定 |
|---|---|---|---|
| ①上游 | 边：DSC-06→DSC-07/08/09（原始表就绪）＋DSC-03→DSC-08（research_report→consensus_daily_build，断链在册）。指标腿任务在册：src/zephyr/data/config/tasks.yaml:2299 technical_indicator_incremental、:2314 technical_indicator_full_refresh。跨槽依赖全 advisory（假依赖不报错+3 组档期倒挂在册） | — | signal |
| ②下游 | 派生表消费方 grep：src/zephyr/factor/expectations.py（consensus_daily）、factor/indicator_reader.py、factor/technical_indicators/{chips,statistics,momentum,volatility}.py（technical_indicator）；进程内六表消费：backtest/core/n_trial_ledger.py:411、pf_alloc/allocation_orchestrator.py、crisis_gate.py；交接 A 出图 consumers=TDM 因子族/工厂/图13（图内 174 点分母） | — | signal |
| ③算法机制 | 财务派生核=单标的 store→行 dict（src/zephyr/data/implementations/financial_derived_compute.py:226，列序真源 schemas/categories/fundamental/financial_derived.py INSERT_COLUMNS）；一致预期核=纯函数研报事件流→20 元组（consensus_daily_compute.py:127-138）；PIT 双守卫=1970 哨兵+publish_date<=trade_date 零 embargo（图 note）；重采样=生产上 ≥5 处并行实现（kline_resampler.py、implementations/ch_tick_kline.py、multi_timeframe_fusion.py、miniqmt_provider 内联 resample、tqcenter_provider——grep resample 命中 8 文件），同域重复簇待收敛（内收判据 w5_1） | — | signal |
| ④后端代码 | src/ 执行体全在盘：kline_resampler.py、financial_derived_compute.py、consensus_daily_compute.py、internal_compute_provider.py、sector_state_pipeline.py、signal_ashare/strategy_signal/series_transform.py；进程内写手六件全在盘：pf_alloc/allocation_inputs.py、allocation_orchestrator.py、core/strategy_screener_3d.py、backtest/core/n_trial_ledger.py、plan_engine/daily_plan.py、daily_loop_master_switch.py。特殊槽硬编码白名单=src/zephyr/data/scheduler.py:574-582（sector_close_final/sector_pre_open）、:208 _run_special_schedule。scripts/ 双入口=scripts/ch/build_*.py --check（CLI 回补）。tests/：tests/data/data/implementations/ 有 test_index_breadth_compute 等；financial/consensus compute 专项 test 首屏未命中＝待验证（不判无） | — | signal |
| ⑤前端呈现（只登记不施工） | frontend 命中集中在行情/因子读侧（api_server.py、chart_factory.py）；sector_state/emotion_index 独立面板未逐一定位——长尾登记，不施工 | — | noise（登记） |
| ⑥数据字段 | 五张等未产表状态（图 as_of 10-04，本批未直查 CH＝实查待施工批）：account_nav_daily 0 行+max=1970 哨兵+写器 live_nav_recorder 零调用方；execution_report 1 行（09-18，sim 链偶发）；factor_feature_value/factor_signal=CH Code 60 表不存在（DDL 件 schemas/categories/factor_feature_value.py 在仓未 apply）；consensus_daily max=09-14 停 10 日 vs research_report max=09-18＝**派生自身停**（比上游还早 4 天=双断）。financial_derived_build 末次 FAILED（'<' str vs datetime.date 类型比较异常） | — | signal/实查待施工批 |

## §2 挖干自评

- **三扫收敛?** 收敛。三轮后无新病灶；确认图对 S3 的"全段无 built"判词无高估（各腿红/黄证据链自洽）。
- **未挖长尾清单**：(a) 22 个 internal 任务逐任务成功率（task_runs 台账在 data/integrator_progress.db，DB 只读面归施工批）；(b) 重采样五实现簇收敛的唯一正门选型（属内收季度审计窗）；(c) renko/point_figure/kagi 信号域纯函数叶的 series_transform 覆盖面；(d) FFVAL/FFSIG 建表后的消费方回归清单。
- **🌑不可得清点**：①今日各派生表 max(date)（禁直查 DB）；②consensus_daily_build 连日漏跑是否已自愈（task_progress 只读 URI 归施工批复核）。

## §3 挖后自审闸三态裁定

**施工（本段是全链施工价值最高的一段）**

- 理由（终局全貌量尺）：派生段的红全部是"产线断点"——consensus 链死、financial 腿跑必失败、四张消费方在等的表不存在/0 行。人工参与今天实际存在于两处：修复失败任务要人盯、等未产表要人催 DDL/接线——施工正是消灭这两处人工。终局里每张派生表都必须有无人值守的产线位置，故全部有位置、无一封矿。
- 施工清单（按解锁依赖排序）：
  1. financial_derived_build 类型比较异常修复＋重跑（src/zephyr/data/implementations/financial_derived_compute.py，病例在 integrator_progress 台账）——纯代码，无门位。
  2. consensus_daily_build 恢复打卡（依赖 research_report 上游回供）＋与 DSC-17 互验联动核对 coverage_shrink（05 簿 P-7 线索：互验行量缩水与预期腿停更交叉）。
  3. factor_feature_value DDL apply（schemas/categories/factor_feature_value.py 在仓未 apply）——**Owner 窗口门位**（建表+资金面无关但属结构演进，按宪法 §5 报 Owner）。
  4. account_nav_daily 写器接线（src/zephyr/position/live_nav_recorder.py 零调用方→挂 plan_engine/lifecycle 触发）——施工＋在册消费方（SPM FAC-E8/E9、ops_alert_feed.py:39）验收。
  5. factor_signal 默认落点建表（buffer.py:25/78/87）——与 3 同批。
  6. execution_report 实盘链接线（ex_core/adapters/qmt_file_bridge_broker.py 断点 E4）——挂交易域排期，非本批。
- 唯一封矿候选：重采样五实现簇**收敛方案不施工**（属内收判据 w5_1 同域重复簇→收敛唯一，排季度合并审计窗，不在本批扩面）。

## §4 挖矿日志

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| 1 | 图字段轮：S3 十节点+facets 腿级状态（map:1065-2575） | signal | 分面行级判词录全：指标✅/重采样🔨、财务🔨/预期🔴、形态✅/情绪✅/打板🟡/板块🔴 |
| 2 | 代码轮：两计算核+特殊槽+进程内写手+重采样簇行号核验 | signal | 五实现在码坐实（含 multi_timeframe_fusion.py 为图外第五件旁证）；进程内六写手全在盘；financial 核 INSERT_COLUMNS 走 schema 真源 |
| 3 | 消费方轮：派生表名全 factor/backtest/pf_alloc/plan_engine grep | signal | expectations/indicator_reader/technical_indicators 四件＋n_trial_ledger:411 与图 consumers 互证；live_nav_recorder 零调用复核（NAV gap 维持） |
| 4 | 复核轮：五张等未产表仅文件面证据（不直查 DB） | 受阻→登记 | DB 读数标实查待施工批；文件面（DDL 在仓未 apply、写器零接线、契约在仓）全部维持图判词 |
