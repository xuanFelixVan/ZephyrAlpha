---
ttl: task_bound
completes_when: 总筹裁决采纳/修订后由总筹落图（本件只出稿禁改 yaml）
title: "任务D·182节点 confidence 初填草案（机生）"
owner: st-tdm-mount-flash-20261003
generation: machine_generated
generator: .runtime/tmp/tdm_mount/task_d_confidence_draft.py（一次性脚本不入产）
---

# 任务D·confidence 初填草案

> 输入=config/trading_decision_map.yaml 182 节点只读；规则序：red_reason 非空→untested｜strategy_mounts 含回测证据字段→verified｜其余→proposed。

## 计数（字段）

- untested: 62
- verified: 2
- proposed: 118
- total_nodes: 182

## 逐节点草案（182 行全）

| node_id | flow | 建议 confidence | 所中规则 | 证据/红因摘要 |
|---|---|---|---|---|
| TDM-E-FLOW | entry_flow | untested | R1: red_reason 非空 | terminal |
| TDM-P-FLOW | position_flow | untested | R1: red_reason 非空 | terminal |
| TDM-X-FLOW | exit_flow | untested | R1: red_reason 非空 | terminal |
| TDM-F-FLOW | portfolio_flow | untested | R1: red_reason 非空 | terminal |
| TDM-E-L0 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L0-01 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L0-02 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L0-03 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L0-04 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L1 | entry_flow | verified | R2: strategy_mounts 含回测证据字段（evidence 带 run=/SR=/oos_tested） | STR-VREV-025: 三窗全绿 IS 1.15/OOS 0.83/S3 0.98, run=SCR-C4-20260913-002056+C4 |
| TDM-E-L1-S1 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L1-S2 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L1-S3 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L1-S4 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L1-S0 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L1-S0-1 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L1-S5 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L1-AGG | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2 | entry_flow | untested | R1: red_reason 非空 | structural |
| TDM-E-L2-01 | entry_flow | untested | R1: red_reason 非空 | structural |
| TDM-E-L2-01-1 | entry_flow | proposed | R3: 有 strategy_mounts 但无回测证据字段 | 1 条 mount 均无回测标记 |
| TDM-E-L2-01-2 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-01-3 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-01-4 | entry_flow | proposed | R3: 有 strategy_mounts 但无回测证据字段 | 1 条 mount 均无回测标记 |
| TDM-E-L2-01-5 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-02 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-02-1 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-02-2 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-03 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-03-1 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-04 | entry_flow | untested | R1: red_reason 非空 | structural |
| TDM-E-L2-04-1 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-04-2 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-05 | entry_flow | untested | R1: red_reason 非空 | pending_gate |
| TDM-E-L2-05-1 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-05-2 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-06 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-06-1 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-06-2 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-06-3 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-07 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-07-1 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-08 | entry_flow | proposed | R3: 有 strategy_mounts 但无回测证据字段 | 1 条 mount 均无回测标记 |
| TDM-E-L2-09 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-09-1 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-09-2 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L2-10 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L3 | entry_flow | untested | R1: red_reason 非空 | structural |
| TDM-E-L3-01 | entry_flow | proposed | R3: 有 strategy_mounts 但无回测证据字段 | 2 条 mount 均无回测标记 |
| TDM-E-L3-02 | entry_flow | proposed | R3: 有 strategy_mounts 但无回测证据字段 | 1 条 mount 均无回测标记 |
| TDM-E-L3-03 | entry_flow | untested | R1: red_reason 非空 | structural |
| TDM-E-L3-03-1 | entry_flow | proposed | R3: 有 strategy_mounts 但无回测证据字段 | 1 条 mount 均无回测标记 |
| TDM-E-L3-03-2 | entry_flow | proposed | R3: 有 strategy_mounts 但无回测证据字段 | 1 条 mount 均无回测标记 |
| TDM-E-L3-03-3 | entry_flow | proposed | R3: 有 strategy_mounts 但无回测证据字段 | 2 条 mount 均无回测标记 |
| TDM-E-L3-04 | entry_flow | proposed | R3: 有 strategy_mounts 但无回测证据字段 | 6 条 mount 均无回测标记 |
| TDM-E-L3-05 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L3-06 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L3-07 | entry_flow | untested | R1: red_reason 非空 | structural |
| TDM-E-L3-07-1 | entry_flow | proposed | R3: 有 strategy_mounts 但无回测证据字段 | 2 条 mount 均无回测标记 |
| TDM-E-L3-07-2 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L3-07-3 | entry_flow | verified | R2: strategy_mounts 含回测证据字段（evidence 带 run=/SR=/oos_tested） | STR-TSMALL-001: 双窗及格 IS 1.066(DSR 0.888)/OOS 0.694, run=SCR-C4-20260914-0452 |
| TDM-E-L3-08 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L3-09 | entry_flow | proposed | R3: 有 strategy_mounts 但无回测证据字段 | 1 条 mount 均无回测标记 |
| TDM-E-L3-10 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L3-11 | entry_flow | untested | R1: red_reason 非空 | structural |
| TDM-E-L3-11-1 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L3-11-2 | entry_flow | proposed | R3: 有 strategy_mounts 但无回测证据字段 | 1 条 mount 均无回测标记 |
| TDM-E-L3-12 | entry_flow | untested | R1: red_reason 非空 | structural |
| TDM-E-L3-12-1 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L3-12-2 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L3-12-3 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L3-12-4 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L4 | entry_flow | untested | R1: red_reason 非空 | structural |
| TDM-E-L4-01 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L4-02 | entry_flow | proposed | R3: 有 strategy_mounts 但无回测证据字段 | 2 条 mount 均无回测标记 |
| TDM-E-L4-03 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L4-04 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L4-05 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L4-06 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L4-07 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L4-08 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L4-09 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L4-10 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L4-11 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L4-12 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L4-13 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L4-14 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-P-P1 | position_flow | untested | R1: red_reason 非空 | structural |
| TDM-P-P2 | position_flow | untested | R1: red_reason 非空 | structural |
| TDM-P-P3 | position_flow | untested | R1: red_reason 非空 | structural |
| TDM-P-P1-01 | position_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-P-P1-02 | position_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-P-P1-03 | position_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-P-P1-04 | position_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-P-P1-05 | position_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-P-P1-06 | position_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-P-P2-01 | position_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-P-P2-02 | position_flow | proposed | R3: 有 strategy_mounts 但无回测证据字段 | 3 条 mount 均无回测标记 |
| TDM-P-P2-03 | position_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-P-P2-04 | position_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-P-P3-01 | position_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-P-P3-02 | position_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-P-P3-03 | position_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-P-P3-04 | position_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-X-S1 | exit_flow | untested | R1: red_reason 非空 | structural |
| TDM-X-S2 | exit_flow | untested | R1: red_reason 非空 | structural |
| TDM-X-R1 | exit_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-X-R1-01 | exit_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-X-R1-02 | exit_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-X-R1-03 | exit_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-X-S1-01 | exit_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-X-S1-02 | exit_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-X-S1-03 | exit_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-X-S1-04 | exit_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-X-S1-05 | exit_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-X-S1-06 | exit_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-X-S2-01 | exit_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-X-S2-02 | exit_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-X-S2-03 | exit_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-X-S2-04 | exit_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-X-S2-05 | exit_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-X-S2-06 | exit_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-F-C1 | portfolio_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-F-C2 | portfolio_flow | untested | R1: red_reason 非空 | structural |
| TDM-F-C3 | portfolio_flow | untested | R1: red_reason 非空 | structural |
| TDM-F-C2-01 | portfolio_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-F-C2-02 | portfolio_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-F-C2-03 | portfolio_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-F-C2-04 | portfolio_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-F-C3-01 | portfolio_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-F-C3-02 | portfolio_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-F-C3-03 | portfolio_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-F-C3-04 | portfolio_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-F-C3-05 | portfolio_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-C-L1 | entry_flow | untested | R1: red_reason 非空 | not_built |
| TDM-C-L2 | entry_flow | untested | R1: red_reason 非空 | not_built |
| TDM-C-L3 | entry_flow | untested | R1: red_reason 非空 | not_built |
| TDM-C-L4 | entry_flow | untested | R1: red_reason 非空 | not_built |
| TDM-E-L9-A01 | entry_flow | untested | R1: red_reason 非空 | by_ref_design |
| TDM-E-L9-A02 | entry_flow | untested | R1: red_reason 非空 | by_ref_design |
| TDM-E-L9-A03 | entry_flow | untested | R1: red_reason 非空 | by_ref_design |
| TDM-E-L9-A04 | entry_flow | untested | R1: red_reason 非空 | by_ref_design |
| TDM-E-L9-A05 | entry_flow | untested | R1: red_reason 非空 | by_ref_design |
| TDM-E-L9-A06 | entry_flow | untested | R1: red_reason 非空 | by_ref_design |
| TDM-E-L9-A07 | entry_flow | untested | R1: red_reason 非空 | by_ref_design |
| TDM-E-L9-A08 | entry_flow | untested | R1: red_reason 非空 | by_ref_design |
| TDM-E-L9-A09 | entry_flow | untested | R1: red_reason 非空 | by_ref_design |
| TDM-E-L9-A10 | entry_flow | untested | R1: red_reason 非空 | by_ref_design |
| TDM-E-L9-A11 | entry_flow | untested | R1: red_reason 非空 | by_ref_design |
| TDM-E-L9-A12 | entry_flow | untested | R1: red_reason 非空 | by_ref_design |
| TDM-E-L9-A13 | entry_flow | untested | R1: red_reason 非空 | by_ref_design |
| TDM-E-L9-A14 | entry_flow | untested | R1: red_reason 非空 | by_ref_design |
| TDM-E-L9-A15 | entry_flow | untested | R1: red_reason 非空 | by_ref_design |
| TDM-E-L9-A16 | entry_flow | untested | R1: red_reason 非空 | by_ref_design |
| TDM-E-L9-B01 | entry_flow | untested | R1: red_reason 非空 | not_built |
| TDM-E-L9-B02 | entry_flow | untested | R1: red_reason 非空 | not_built |
| TDM-E-L9-B03 | entry_flow | untested | R1: red_reason 非空 | not_built |
| TDM-E-L9-B04 | entry_flow | untested | R1: red_reason 非空 | not_built |
| TDM-E-L9-B05 | entry_flow | untested | R1: red_reason 非空 | not_built |
| TDM-E-L9-B06 | entry_flow | untested | R1: red_reason 非空 | not_built |
| TDM-E-L9-B07 | entry_flow | untested | R1: red_reason 非空 | not_built |
| TDM-E-L9-B08 | entry_flow | untested | R1: red_reason 非空 | not_built |
| TDM-E-L9-B09 | entry_flow | untested | R1: red_reason 非空 | not_built |
| TDM-E-L9-B10 | entry_flow | untested | R1: red_reason 非空 | not_built |
| TDM-E-L9-C01 | entry_flow | untested | R1: red_reason 非空 | not_built |
| TDM-E-L9-C02 | entry_flow | untested | R1: red_reason 非空 | not_built |
| TDM-E-L9-C03 | entry_flow | untested | R1: red_reason 非空 | not_built |
| TDM-E-L9-G1 | entry_flow | untested | R1: red_reason 非空 | structural |
| TDM-E-L9-G2 | entry_flow | untested | R1: red_reason 非空 | structural |
| TDM-E-L9-G3 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L9-G4 | entry_flow | untested | R1: red_reason 非空 | structural |
| TDM-E-L9-G5 | entry_flow | untested | R1: red_reason 非空 | not_built |
| TDM-E-L9-V1 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L9-V2 | entry_flow | untested | R1: red_reason 非空 | not_built |
| TDM-E-L9-V3 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L9-AGG | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L9-D1 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L9-D2 | entry_flow | untested | R1: red_reason 非空 | structural |
| TDM-E-L9-E1 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
| TDM-E-L9-E2 | entry_flow | untested | R1: red_reason 非空 | pending_gate |
| TDM-E-L9-Z1 | entry_flow | untested | R1: red_reason 非空 | structural |
| TDM-E-L9-Z2 | entry_flow | proposed | R4: 无 red_reason 无 strategy_mounts |  |
