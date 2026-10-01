---
ttl: task_bound
title: W3-2 三态变迁清单（E/F/G/H 四段，st-ffchief-20261001 S3）
session: st-ffchief-20261001
date: 2026-10-01
status: mined
---

# W3-2 三态变迁清单（E 段 F53-F58 / F 段 F59-F63 / G 段 F64-F71 / H 段 F72-F75）

> 基准=00_skeleton.md（S2，2026-10-01）§1/§2/§3；本清单只记 W3-2 负责段内经代码级复核确认的
> 三态变迁与口径漂移。判读口径承 §0.1（挖干/存疑/盲区）。

## 一、三态变迁（状态改判，6 项）

| # | 环节 | S2 态 | S3 复核态 | 证据锚（路径:行/实拍） | 性质 |
|---|------|-------|-----------|------------------------|------|
| 1 | E-06(F58) 执行成本反馈 | 存疑（§3 #11 断链） | **挖干（翻绿）** | trading_decision_map.yaml:2550-2561（TDM-E-L4-14 note_confirmed 2026-09-27"断链已闭合"）；algo_execution_selector.py:212/:339/:422/:528（quality_prior 字段+协议+注入+消费四点）；tests/ex_sor/test_execution_quality_scorer.py | 状态漂移：09-27 闭合批后骨架未回写 |
| 2 | F-04(F62) 合规门 | 存疑(P0 断链级，§3 #2"零注入") | **纸面链 built（五闸注入）**，残余 LIVE 两闸+broker_ack 人工面；**施工中 by lane-f62** | order_manager.py:348/:371-425（五闸链）；sim_saga_assembly.py:163-177（paper 五闸注入）；qmt_trading_session.py:121-129（三闸）；commit fa9ae365331（09-28）；F62.md=lane-f62 权威档 | P0 过期：08-15 三闸批+09-28 两闸批已清偿注入面；车道判"已闭（模拟侧）"留总筹改判 |
| 3 | F-03(F61) KillSwitch | 挖干(持久化待裁) | **挖干（持久化实证落地，建议追认注记）** | kill_switch_state_store.py:50/:60/:93（save/rebuild 链）；data/runtime/trading_kill_switch_state.json（saved_at 2026-09-30T10:15:46Z，POSITION_LIMIT active=true）；start_paper_session.py:8（"重启存活熔断，#ARCH-QUANT-002 治本"） | "待裁"项有实证解：JSON state store+影子件+rebuild 全链在跑 |
| 4 | H-01(F72) 模拟盘日跑 | 存疑(P0 断链嫌疑，§3 #4 SimBridge) | **执行腿 built 在跑；断点移位**=orders 委托批次文件生产者缺位（honest-SKIP）；P0→P1 候选 | sim_daily_runner.py:44/:944/:1242（断腿重建批）；.runtime/logs/sim_bridge_execute.log（09-30 双跑 exit 0，"why":"orders_file_missing"）；data/runtime/qmt_bridge/ 目录不存在+全仓无 in-repo 写入者（:1259 消费外部文件） | 根因移位：腿在单源断，主链（paper/plan/outpost）不受影响 |
| 5 | H-02(F73) A/B 联赛 | 存疑(P0 design 未施工，§3 #5) | **挖干（翻绿，执行器在跑）；残余=零参赛者空转** | league_judge.py 头注（"晋升判据执行器…F73"，MOD-AUTO-L11-JUDGE）；pipeline_events.py:214/:798（事件接线 st-c9-f73）；judgment-2026-09/10.json（10-01 05:51 UTC 实跑，empty_field=true 诚实空场） | P0 过期：执行器已建成并产出两档月度判定书；非断链是链末端低水位 |
| 6 | H-03(F74) Owner 拍板流量 | 挖干(翻绿)+"decide 待实测流量" | **挖干维持；流量仍零（有门无拍板）** | promotion_advisory.py:101/:659（token fail-closed）；pipeline_events.py:202；api_server.py:5014 POST /api/promotion-decide；data/docs 无近期决策产物（本轮 find 零命中） | 复核维持：门在流量无，与 S2 §5 注记一致 |

## 二、口径漂移（非状态变迁，4 项）

| # | 项 | S2 说法 | S3 实测 | 处置建议 |
|---|----|---------|---------|----------|
| 7 | F59 REG-RLM-001 条数 | 117 条 | **118**（grep -c risk_limit_id，risk_limit_registry.yaml 4421 行） | S4 汇总刷数 |
| 8 | G-04 实验档案条数 | 11 条 | **74**（experiment_registry.yaml experiment_id 计数） | 同上（累积型计数，建议字段化禁散文写死） |
| 9 | E-02 打板件数 | 六件套 | **8 件**（ex_core/daban_*.py：execution/signal_decision/exit_decision/instant_circuit_breaker/load_producer/monitors/pit_safety/named_functions） | 刷"六件套"表述 |
| 10 | G-01 三册路径 | config/universe|benchmark|cost_model_registry.yaml | **docs/01_policies_and_standards/_registry/catalogs/**（config/ 下无此三册；条数 9/10/7） | 刷 §2 代码入口列路径 |

## 三、W3-2 段内新发现断链

**零条新增断链**。F72 断点移位（orders 供单缺位）为既有断链的根因移位登记，非新断链；
F73 零参赛者、F75 低流量为链末端水位问题（非断链）；ex_core/position 双 PositionReconciler
同名件（218/207 行）为克隆嫌疑登记（clone_guard 面，非断链，移交 clone 审计线）。

## 四、P0 处方就绪度（本段涉及 P0 收敛一览）

| 环节 | 处方状态 |
|------|----------|
| F62（施工中 by lane-f62） | 处方已执行大半（W140 十二件 8+G12 接线，见其 F62.md §3/§4）；残余=G08 批扫承载件、G10/G11 Owner 门、LIVE 腿 TRD-A10 |
| F72 | 处方方向就绪：供单源三选一裁定（Owner 门）→ 导出腿/人工 SOP 落地；P1 候选 |
| F73 | 处方就绪：机制零缺口，等 F72 供单或 Owner 裁定 --register-first 首位参赛者；STD-SWITCH-001 转 frozen=Owner 门 |
| F58/F61/F74 | 无处方需求（F58 翻绿；F61 待 Owner 追认注记；F74 等自然流量） |
