---
campaign: matrix-20261006
lane: S-skeleton
status: draft
ttl: task_bound
---

# st_e6_intake_monitor —— E6 入库监控（SPM 15 节点）

- 真源: `config/strategy_production_map.yaml`；行号=SPM:L*。
- 职责: 考过的策略入库台账化，并在库内做生命周期/漂移/降级持续监控。
- 计数: 15 = 1 stage(built) + 14 mech（全 built，零 pending）。

## 1. 族内节点全清单

| node_id | 名称 | 状态 | module_ref | 行 |
|---|---|---|---|---|
| FAC-E6 | 入库监控（stage） | built | MOD-BT-078 | SPM:L349 |
| FAC-E6-M-001 | 策略台账查询器 | built | MOD-BT-078 | SPM:L3836 |
| FAC-E6-M-002 | ④ 4级告警判定 | built | MOD-BT-018 | SPM:L3852 |
| FAC-E6-M-003 | 策略生命周期状态机 | built | MOD-BT-188 | SPM:L3867 |
| FAC-E6-M-004 | 自动入库编排器 | built | MOD-BT-189 | SPM:L3886 |
| FAC-E6-M-005 | 策略注册表条目追加写入器 | built | MOD-BT-192 | SPM:L3910 |
| FAC-E6-M-006 | 日度决策快照表（decision_daily DDL+schema） | built | MOD-BT-212 | SPM:L3929 |
| FAC-E6-M-007 | 分层参与门快照采集器 | built | MOD-BT-213 | SPM:L3945 |
| FAC-E6-M-008 | 日度编排器 | built | MOD-BT-214 | SPM:L3962 |
| FAC-E6-M-009 | 模型漂移监控（Kronos 等基线模型衰减位） | built | dir:_domain_ml_serve/model_drift_monitor | SPM:L3981 |
| FAC-E6-M-010 | 信号降级监控（衰减族） | built | dir:_domain_signal_quality/signal_degradation_monitor | SPM:L3993 |
| FAC-E6-M-011 | 信号可解释性保证 | built | dir:_domain_signal_quality/signal_explainability_guarantor | SPM:L4004 |
| FAC-E6-M-012 | 因子生命周期 runner | built | dir:_domain_factor/factor_lifecycle_runner | SPM:L4016 |
| FAC-E6-M-013 | 分布漂移监控（衰减信号源） | built | dir:_domain_fbl_detectors/distribution_drift_monitor | SPM:L4027 |
| FAC-E6-M-014 | 策略 lifecycle 流转建议器 | built | code:scripts/backtest/strategy_lifecycle_advisor.py | SPM:L4039 |

## 2. 接线现状与缺口判定

- 已接线：入库链（查询/编排/追加写入器）+ 监控链（模型漂移/信号降级/分布漂移三监控 + 4 级告警）+ 日度快照三件（M-006/007/008）全 built。
- 缺口：图内零 pending。可考性：内务层不进回测考卷；其衰减结论经 feedback E6→E1 反哺进货方向（SPM feedback_loops[1]）。
- 观察位（登记不判）：M-010 信号降级监控与 TDM-F-C3-05 可靠度养成挂同一模块族（TDM:L4549 mounts 含 MOD-SIGQC-003/005/006、MOD-BT-018）——两图共享衰减族，防双头维护。

## 3. 修复建议（一句话）

零缺口层无需修复；建议把 E6 衰减结论→E1 反哺边的触发证据（近期是否有真实反哺案例）列入矩阵考试题库（effectiveness=not_mined）。

## 4. 交叉验证

- 图15 策略卡生命周期（0 节点/17 transitions，chief 01 §1 表）与 E6-M-003 生命周期状态机/M-014 流转建议器是同域两制——卡状态登记面未建（census §4 第二波）正是图15 缺口，E6 是其事实载体。
- chief B1 ENV-17 计数一致；census 未触 E6 层内构成（本册补充挖矿）。
