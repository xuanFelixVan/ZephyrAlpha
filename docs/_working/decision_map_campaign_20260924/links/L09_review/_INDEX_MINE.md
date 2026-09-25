---
ttl: task_bound
title: L09 复盘与监控 · 挖矿总勾表（_INDEX_MINE）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-L09
scope: docs/_working/decision_map_campaign_20260924/links/L09_review/
status: 7/7 子块落盘完成 + 外部对表最小统一轮已补做（唯一硬阻塞=L09-C01 待裁）
---

# L09 复盘与监控 · 总勾表

> 起点真源=`SKEL.md`（本目录），本批往下钻一层：逐子块给"实码行号 / 表与注册表实测 / **生产触发面三态判定** / 数据新鲜度"。
> 方法真源=`docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md` §2/§5/§6。
> 量尺=终局全貌（Owner 一人 + 100% AI 自制，一切可自动化者全自动化）；**禁以现状规模小封矿**。

## 一 · 七块总勾

| 子块 | 目录 | 通电判定（一句话） | 主实测证据 | 新增缺口 | 三态 |
|---|---|---|---|---|---|
| S9-1 日循环编排（心脏） | `s1_daily_loop_orchestrator/` | **9 跳中 7 已接电 / 1 覆盖未接电（H1 盘前晨间窗）/ 1 部分接电（H8 监控告警）** | 事件链 16 钩子实序（`pipeline_events.py:1026-1117`）+ `dloop_post` 16:45（`schedule.yaml:249-253`）+ `PHASE_STAGES` full=16（`daily_loop_master_switch.py:337-368`）+ schtasks 50 项状态实测 + 总闸文件 ABSENT | 3（G1 哨兵自身无人监控／G2 alert 无消费／G3 trial 转正无判据） | 封矿（附 L09-C01 待裁口） |
| S9-2 盘前链 | `s2_premarket_chain/` → 实为 `s2_premarket_chain`（见下注） | **覆盖未接电**：T 日 08:00-09:15 零触发面；预案由 T-1 16:45 产 | 三套实现装配方逐个 grep（021=7 命中皆非装配、023=3 命中零生产、dloop 丙套在产但跑在 T-1） | 3 | 封矿（TRD-A04 随 L09-C01） |
| S9-3 判定台账与结算 | `s3_judgment_ledger_settlement/` | **已接电但"链通而账未满"** | 回填率实测：intraday 20/20、next_day `brier_score` **1/4**、daily_plan `eval_score` **2/9**、verification `plan_quality_score` **6/14** | 5（G1 unresolvable 显式化=P0） | 封矿 |
| S9-4 日刊与 decision_daily | `s4_daily_publication_and_decision_snapshot/` | **两账均已接电；账 B 零读侧** | 账 A 72 行/6 目标日/66 行为单次批量、**72/72 全 degraded=1**；账 B 16 行、三健康检 16/16 满填、**周末 09-19/09-20 有行** | 4 | 封矿（L09-C02 随裁定） |
| S9-5 warroom | `s5_warroom_operations/` | **两委托在产；三任务 1.5/3 健康** | `prediction_log` 35 行分布（scenario_plan **6**／outcome **4**／auction_hit **1**／plan_revision 17 全在 08-21）；intraday payload 键=`evidence/rest_of_day/state_label/state_probs`；`next_day_forecast` 末次 asof **09-20** | 5（G1 停摆检测=P1） | 封矿 |
| S9-6 监控自动化 | `s6_monitoring_automation/` | **产报面普遍接电，汇聚/分发/处置三段全空转** | schtasks 状态实测（Running 7／Ready 有排程 34／Ready 无排程 3／Disabled 6）；`alert_aggregator`（MOD-RPT-030）**零 import**；THD-TRD-001..004 **0/4 有消费代码、0/4 演练**；sentinel alert 文件 ABSENT | 6（G1 接上 aggregator=P0） | 封矿（Prometheus/Grafana 选型层封） |
| S9-7 归因与绩效报告 | `s7_attribution_engine_and_performance_reports/` | **算法在产、装配从未跑通** | `attribution_results` 实测 **0 行**（列全集含 `transaction_cost_drag`/`net_pnl`/`invariant_status`）；C3 五子枝 module_ref 逐个读=**五接头零焊**；PF-007 唯二消费全在风险域 | 5（G1 打通装配=P1） | 封矿（仅限算法选型层） |

（目录名实盘：`s2_premarket_chain/`。全部 7 个目录名均以字母结尾，合 R5 门禁。）

**合计：7/7 份 MINE.md 落盘 + 本总勾表；新增缺口 31 条；对 SKEL 的实测勘误 7 处。**

## 二 · 对 SKEL 的勘误清单（本批最重要的一致性变更，须回灌骨架/13 号文/17 号文）

| # | SKEL 原述 | 本批实测 | 出处册 |
|---|---|---|---|
| 1 | §S9-1⑥/§S9-6⑤「TRD-A01／L09-C04 决策链哨兵**未落地**」 | **已落地并在产**：`scripts/governance/decision_chain_sentinel.py` + `register_decision_chain_sentinel_task.ps1` + `tests/governance/`；schtasks `ZephyrAlpha_DecisionChainSentinel` 状态 Ready、下次 09-26 09:40、XML 实读命令指向该脚本 | S1 |
| 2 | §S9-6 摘要「禁用=NightlySentiment（已有 schedule.yaml 08:20 槽接管）」 | 状态 **Ready**、下次 09-25 22:30，与 08:20 槽**同时在排** ⇒ TRD-A03 从"待确认"升级为"实证双通道并存" | S6 |
| 3 | §S9-6 摘要「C4Exam 与 FactoryLaneC 一次性两件禁用」 | 基件 `C4Exam`/`FactoryLaneC` 均 Ready 在排；禁用的是 `_Full0916`/`_OneShot0915` 派生件 | S6 |
| 4 | §S9-2「双实现治理（MOD-PLAN-021 vs dloop premarket 段）」 | **三实现**：增 `premarket_workflow_engine.py`（MOD-PLAN-023，六工序 handler 引擎，零生产装配方）；L09-C09 须扩为三件一次收拢 | S2 |
| 5 | §S9-4 二判据「深史 🟡／decision_daily 自 09-16 起产行」 | 精确化：**72 行中 66 行是 09-16 单次批量，自然日频仅 6 行 / 6 个目标日** ⇒ "深史≈10 日"应改"6 个目标日" | S4 |
| 6 | §S9-5④「warroom 第三任务（盘中实时走势）本体=新增件未建」 | **部分已建**：`intraday_l1_tracker` 在产（20 行/5 日、结算满填），证据与尾盘预测在 payload（`evidence`/`rest_of_day`）⇒ L09-C08 靶心改写为"payload 升列 + 60min vs 分钟级节拍差"，不是"从零新建" | S5 |
| 7 | `config/trading_decision_map.yaml:3803`「D50 三项已由 TDM-F-C3-01 承接落位」 | **证伪**：该引擎方法集为 brinson/factor/risk/degradation/crowding，`slippage/decision_price/fill_price/TCA/trade_pnl/position_pnl` **零命中** ⇒ LK-15 三欠账仍活；TDM 注记须回改（属热注册表，交专批，本车道未动） | S7 |

## 三 · 三个"待裁项"的材料齐备度（本批只出材料，未拍板、未施工）

| 待裁项 | 材料 | 齐否 |
|---|---|---|
| **L09-C01 编排器收拢**（蓝图版 vs 双轨转正） | S1 册⑤：两版各自代码位置／当前谁在真跑（**两条都在跑**，实测 16 钩子 + 16 段 + 各自触发面）／合并技术路径四步／保留两条的运维代价 4 条／不可逆点（事件链摘钩=当日全链停摆且节拍不可追溯；T4 落库新增列难回退）／附带三个必答子问题（盘前三实现、cron 二次驱动 reconciler 是否保留、晨间窗挂哪条节拍）；S5 册补 T3 基座已存在（`plan_revision` 17 行历史实证）⇒ 工时按"复活"不按"新建" | **齐**（Owner 一句话即解） |
| **L09-C03 日刊双账合流** | S4 册②：两账定义／**5 条实测冲突**（`trade_date` 前瞻 vs 回顾时间轴、日频 vs 日历日、只增修订 vs 幂等替换、production vs experimental、2 读侧 vs 0 读侧）／可执行工作项 4 步／分期主张（3 步可绕开 L09-C02 先行） | **齐**（并主张解除 L09-C02 串行的误置） |
| **TRD-A04 盘前双（三）实现治理** | S2 册②⑤：三套实现逐个装配方实测 + 023 是"晨间窗天然实现骨架"的判读 + 复用已有实码补触发面的最小施工路径 + 显式豁免路径 | **齐**（随 L09-C01） |

## 四 · 宪法 §9.3 偏差登记（遵任务书"如实登记、不自行改"）

| 对象 | 形态 | 裁定 |
|---|---|---|
| `close_verify`/`settle`/`warroom` 三段 | 事件链钩子（头注明文自证 §9.3 合规、不建 cron）+ 又被 `dloop_post` 16:45 计划任务二次驱动 | **真偏差候选**，移交 L09-C01 必答；未改任何代码/排班 |
| `DecisionChainSentinel` | schtasks 日频 09:40 | **不构成偏差**（检测对象=事件的缺席，缺席无法事件唤醒），登记为已论证豁免 |
| `integrity_check 23:00` 只告警 | cron | 符合设计意图，非偏差 |

## 五 · 本环节穷尽性声明

**声明口径**：本批（LANE-MINE-L09，2026-09-26）对 L09 七个子块**各成册、六向封口**，并对下列四问给出可复核答案：

1. **日循环通没通电** → 已答（S1 册逐跳表：7 接电／1 覆盖未接电／1 部分接电；并附 09-25 全链事件面停摆的三源对拍实证——`last_audit.json` 无 `*:2026-09-25` 记号、`kline_index max=09-24`、`decision_daily` 缺 09-25 目标行却有 09-28 行）。
2. **L09-C01 收拢** → 材料齐（未拍板、未施工）。
3. **L09-C03 双账合流** → 5 条冲突 + 4 步工作项。
4. **监控消费面（17 号文 TRD-A06/15 验收线）** → 0/4 有消费代码、0/4 演练，并定位到单点死总线 `alert_aggregator`。

**已穷尽（本批实测覆盖）**：SKEL §〇 全 7 子块的实码位置、触发面（APScheduler 29 槽 + schtasks 50 项状态级）、表与注册表（CH `c1_market`/`c1_backtest` + sqlite `governance.db` + `alert_threshold_registry.yaml:20-22,961-1032` + `trading_decision_map.yaml:3782-4146`）、数据起止与新鲜度（decision_daily/sim_platform_journal/sim_attribution_daily/四张 judgment 表/prediction_log 全测）。

**未穷尽（如实挂账，非隐蔽遗漏）**：
1. **外部对表：全部落盘后已补做一轮最小统一对表（2026-09-26，3 次检索）**，逐条如实定级：
   - **Grafana 许可（S6 册封矿判语的直接依据）＝已达 ≥2 独立来源**：InfoQ 中文《Grafana、Loki 和 Tempo 更改开源协议，由 Apache License 2.0 转为 AGPL v3》(infoq.cn, 2026-06-26) 与 quant67《AGPL、SSPL、BSL：云厂商时代的…》(2026-04-22) 相互独立共证实体结论。**仍缺**：两源摘要内未明写 "2021-04" 时点 ⇒ 该月份沿用 SKEL §5.2 前批口径，标"时点未本批复核"。
   - **Brinson 三效应（配置/选股/交互）＝行业正典，已达 ≥2 独立来源**：ziguanyun《Brinson 归因模型-超额收益来源拆解》(2026-09-21)、CSDN《基于 gs-quant 的 Brinson 模型实战》(2026-04-10)、juejin《量化策略绩效归因…3 步定位收益来源》(2026-03-12)、MBA 智库《资产配置》多源共证 ⇒ 支持 S7 册"仓内 PF-007 已是标准件同构、欠的是装配不是算法"。**新增线索（待核、本批未据此改判）**：Goldman Sachs `gs-quant` 亦实现 Brinson，若需工业级交叉验证参考实现它比 pybrinson 更近，**但许可条款本批未查，查清前禁止引为依赖**（pybrinson 的 Py≥3.14 硬墙结论不变）。Brinson & Fachler 1985 *JPM* / BHB 1986 *FAJ* 的**首发出处与年份本批只获二手转述、无一手源** ⇒ 沿用前批并标"未独立核验"。
   - **burn-rate / 多窗口告警＝业界标准实践（SRE Ch.5 判语），已达 ≥2 独立来源**：Datadog 官方文档《Burn Rate Alerts》(2026-02-26，独立厂商实现即惯例反证) + O'Reilly《Google SRE 工作手册》章节目录 + 阿里云开发者《以 SLI/SLO 为驱动的可观测性》(2025-11-28)；主源 sre.google/workbook/alerting-on-slos/（Google）沿用前批。
   - **仍未做**：data-driven DAG（Airflow dataset triggers / Dagster assets）本批未检；three-way reconciliation 开源生态续搜（SKEL §5.3 已声明不引入）；A 股适配闸逐项书面结论未单独成表。
   ⇒ 净效果：S6 的技术选型封矿判语与 S7 的"欠装配不欠算法"判语已从"沿用前批"升级为"本批双源共证"；其余仍挂账。各册 §⑥ 原有"未做外部对表"标注按本条为准做增量覆盖，不回改各册（保留单册自足性）。
2. SKEL §三未挖清单第 1/2/3/4/5 项：蓝图 238 行全文的降级矩阵 D1-D7 逐条对表、`owner-vision-system-mapping.md` §二.3 逐层归因消费语义、`data-sufficiency-matrix.md` §五 L4 行原文、55 号周月复盘件与 `sim_deviation_report.py` 关系、`alert_threshold_registry.yaml` 全册（本批仅精读 THD-TRD 四条与头部 schema）。
3. 判定四表的 `asof_ts` 逐日新鲜度序列（本批工具按 date 列设计，四表无 date 列 ⇒ 已取得 min/max 与唯一日数，未取得逐日分布）。
4. 仪表盘 warroom 组件的"三任务卡片"前端完成度（本批只证面板函数 `warroom.py:1296/1320` 在，未逐卡核 UI 覆盖）。
5. `plan_followed`/`deviations` 与作战室"执行不一致"记账的对接程度（addendum 任务 3 要求，未追到落点）。

**封矿判定**：本环节 **仍不转 SEALED**，但阻塞项已从两条收敛为**一条**——外部对表已完成最小统一轮（第 1 条由"未做"降为"部分完成，余下 3 项挂账：DAG 范式 / 1985·1986 一手文献 / Grafana 时点"），**唯一硬阻塞=L09-C01 待 Owner 裁定**。
转 SEALED 的前置=①L09-C01 裁定回来后补录结果（SKEL §六 封矿条件原文即如此约定）；②续做第 1 条三项挂账（非阻塞，属完备性）。
七子块自身在"仓内实证"维度已全部封口。
