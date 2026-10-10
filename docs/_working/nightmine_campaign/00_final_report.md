---
ttl: task_bound
title: 过夜总令端到端总报告（机生，禁散文计数）
created: "2026-10-10"
sid: st-nightmine-20261010
family_id: NIGHTMINE-CAMPAIGN
---

# 端到端总报告（生成器=.runtime/tmp/st-nightmine-20261010/build_final_report.py）

> 本报告全部数字由生成器现读真源产出；重跑即刷新。真源=卡册/分数册/车道名册/gpu_util.log/台账正则。

## 一、总量面（机读）

- 卡册件总数=454（含 card_id 的有效卡=454，解析失败件=0）
- 在册节点数=186，名册覆盖面=186，未分配=0
- 族分布={'ablation': 67, 'calibration': 170, 'comparison': 182, 'shadow': 35}
- 状态分布={'blocked_on_data': 52, 'blocked_on_impl': 26, 'empty': 186, 'examined': 17, 'preregistered': 173}
- 分数册行数=17

## 二、车道×节点×卡态总表

| lane | 节点数 | 卡总数 | preregistered | examined | blocked | 可机判(runnable) | 带 data_binding |
|---|---|---|---|---|---|---|---|
| L1 | 30 | 65 | 26 | 1 | 8 | 35 | 35 |
| L2 | 26 | 65 | 15 | 0 | 24 | 39 | 39 |
| L3 | 32 | 91 | 44 | 15 | 0 | 59 | 39 |
| L4 | 18 | 55 | 24 | 0 | 13 | 37 | 37 |
| L5 | 19 | 44 | 25 | 0 | 0 | 25 | 25 |
| L6 | 16 | 37 | 21 | 0 | 0 | 21 | 21 |
| L7 | 45 | 97 | 18 | 1 | 33 | 52 | 52 |

## 三、逐节点考试状态（186 行全展开）

| node_id | lane | 卡数 | 骨架 | 族分布 | 状态分布 | 可机判 | binding |
|---|---|---|---|---|---|---|---|
| TDM-C-L1 | L3 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-C-L2 | L1 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-C-L3 | L2 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-C-L4 | L3 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-FLOW | L3 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L0 | L3 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L0-01 | L3 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L0-02 | L3 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L0-03 | L3 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L0-04 | L3 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L1 | L3 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L1-AGG | L3 | 2 | 1 | {'ablation': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L1-S0 | L3 | 7 | 1 | {'calibration': 7} | {'empty': 1, 'preregistered': 6} | 6 | 2 |
| TDM-E-L1-S0-1 | L3 | 3 | 1 | {'calibration': 3} | {'empty': 1, 'examined': 1, 'preregistered': 1} | 2 | 1 |
| TDM-E-L1-S1 | L3 | 3 | 1 | {'calibration': 3} | {'empty': 1, 'examined': 1, 'preregistered': 1} | 2 | 0 |
| TDM-E-L1-S2 | L3 | 15 | 1 | {'calibration': 15} | {'empty': 1, 'examined': 13, 'preregistered': 1} | 14 | 7 |
| TDM-E-L1-S3 | L3 | 6 | 1 | {'calibration': 6} | {'empty': 1, 'preregistered': 5} | 5 | 2 |
| TDM-E-L1-S4 | L3 | 4 | 1 | {'calibration': 4} | {'empty': 1, 'preregistered': 3} | 3 | 1 |
| TDM-E-L1-S5 | L3 | 3 | 1 | {'calibration': 3} | {'empty': 1, 'preregistered': 2} | 2 | 1 |
| TDM-E-L2 | L1 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L2-01 | L1 | 3 | 1 | {'ablation': 2, 'comparison': 1} | {'empty': 1, 'preregistered': 2} | 2 | 2 |
| TDM-E-L2-01-1 | L1 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L2-01-2 | L1 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L2-01-3 | L1 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L2-01-4 | L1 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L2-01-5 | L1 | 2 | 1 | {'ablation': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L2-02 | L1 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L2-02-1 | L1 | 3 | 1 | {'ablation': 1, 'calibration': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 2} | 2 | 2 |
| TDM-E-L2-02-2 | L1 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L2-03 | L1 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L2-03-1 | L1 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L2-04 | L1 | 2 | 1 | {'ablation': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L2-04-1 | L1 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L2-04-2 | L1 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L2-05 | L1 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L2-05-1 | L1 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L2-05-2 | L1 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L2-06 | L1 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L2-06-1 | L1 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L2-06-2 | L1 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L2-06-3 | L1 | 3 | 1 | {'calibration': 2, 'comparison': 1} | {'empty': 1, 'preregistered': 2} | 2 | 2 |
| TDM-E-L2-07 | L1 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L2-07-1 | L1 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L2-08 | L1 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L2-09 | L1 | 4 | 1 | {'calibration': 3, 'comparison': 1} | {'empty': 1, 'examined': 1, 'preregistered': 2} | 3 | 3 |
| TDM-E-L2-09-1 | L1 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L2-09-2 | L1 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L2-10 | L1 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L3 | L2 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'blocked_on_impl': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L3-01 | L2 | 4 | 1 | {'calibration': 2, 'comparison': 2} | {'blocked_on_data': 1, 'empty': 1, 'preregistered': 2} | 3 | 3 |
| TDM-E-L3-02 | L2 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'blocked_on_impl': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L3-03 | L2 | 2 | 1 | {'ablation': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L3-03-1 | L2 | 3 | 1 | {'calibration': 2, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1, 'preregistered': 1} | 2 | 2 |
| TDM-E-L3-03-2 | L2 | 4 | 1 | {'calibration': 3, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1, 'preregistered': 2} | 3 | 3 |
| TDM-E-L3-03-3 | L2 | 2 | 1 | {'ablation': 2} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L3-04 | L2 | 4 | 1 | {'ablation': 1, 'calibration': 2, 'comparison': 1} | {'blocked_on_data': 2, 'empty': 1, 'preregistered': 1} | 3 | 3 |
| TDM-E-L3-05 | L2 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L3-06 | L2 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L3-07 | L2 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'blocked_on_impl': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L3-07-1 | L2 | 3 | 1 | {'ablation': 2, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1, 'preregistered': 1} | 2 | 2 |
| TDM-E-L3-07-2 | L2 | 3 | 1 | {'ablation': 2, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1, 'preregistered': 1} | 2 | 2 |
| TDM-E-L3-07-3 | L2 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L3-08 | L2 | 2 | 1 | {'ablation': 2} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L3-09 | L2 | 2 | 1 | {'ablation': 1, 'calibration': 1} | {'blocked_on_impl': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L3-10 | L2 | 3 | 1 | {'calibration': 2, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1, 'preregistered': 1} | 2 | 2 |
| TDM-E-L3-11 | L2 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L3-11-1 | L2 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L3-11-2 | L2 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L3-12 | L2 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L3-12-1 | L2 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L3-12-2 | L2 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L3-12-3 | L2 | 4 | 1 | {'calibration': 3, 'comparison': 1} | {'blocked_on_impl': 1, 'empty': 1, 'preregistered': 2} | 3 | 3 |
| TDM-E-L3-12-4 | L2 | 3 | 1 | {'calibration': 2, 'comparison': 1} | {'blocked_on_data': 1, 'blocked_on_impl': 1, 'empty': 1} | 2 | 2 |
| TDM-E-L4 | L3 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L4-01 | L3 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L4-02 | L3 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L4-03 | L3 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L4-04 | L3 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L4-05 | L3 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L4-06 | L3 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L4-07 | L3 | 2 | 1 | {'ablation': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L4-08 | L3 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L4-09 | L3 | 2 | 1 | {'comparison': 1, 'shadow': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L4-10 | L3 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L4-11 | L3 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L4-12 | L3 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L4-13 | L3 | 2 | 1 | {'comparison': 1, 'shadow': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L4-14 | L3 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L9-A01 | L7 | 3 | 1 | {'calibration': 3} | {'empty': 1, 'preregistered': 2} | 2 | 2 |
| TDM-E-L9-A02 | L7 | 2 | 1 | {'calibration': 2} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-A03 | L7 | 2 | 1 | {'calibration': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L9-A04 | L7 | 3 | 1 | {'calibration': 3} | {'blocked_on_data': 1, 'empty': 1, 'examined': 1} | 2 | 2 |
| TDM-E-L9-A05 | L7 | 2 | 1 | {'calibration': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L9-A06 | L7 | 3 | 1 | {'calibration': 3} | {'blocked_on_data': 1, 'empty': 1, 'preregistered': 1} | 2 | 2 |
| TDM-E-L9-A07 | L7 | 2 | 1 | {'calibration': 2} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-A08 | L7 | 2 | 1 | {'calibration': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L9-A09 | L7 | 2 | 1 | {'calibration': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L9-A10 | L7 | 2 | 1 | {'calibration': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L9-A11 | L7 | 2 | 1 | {'calibration': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L9-A12 | L7 | 2 | 1 | {'calibration': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L9-A13 | L7 | 2 | 1 | {'calibration': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L9-A14 | L7 | 2 | 1 | {'calibration': 2} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-A15 | L7 | 4 | 1 | {'calibration': 4} | {'blocked_on_data': 1, 'empty': 1, 'preregistered': 2} | 3 | 3 |
| TDM-E-L9-A16 | L7 | 2 | 1 | {'calibration': 2} | {'blocked_on_impl': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-A17 | L7 | 3 | 1 | {'calibration': 3} | {'blocked_on_data': 1, 'empty': 1, 'preregistered': 1} | 2 | 2 |
| TDM-E-L9-AGG | L7 | 2 | 1 | {'ablation': 2} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-B01 | L7 | 2 | 1 | {'calibration': 2} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-B02 | L7 | 2 | 1 | {'calibration': 2} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-B03 | L7 | 2 | 1 | {'calibration': 2} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-B04 | L7 | 2 | 1 | {'calibration': 2} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-B05 | L7 | 2 | 1 | {'calibration': 2} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-B06 | L7 | 2 | 1 | {'calibration': 2} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-B07 | L7 | 2 | 1 | {'calibration': 2} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-B08 | L7 | 2 | 1 | {'calibration': 2} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-B09 | L7 | 2 | 1 | {'calibration': 2} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-B10 | L7 | 2 | 1 | {'calibration': 2} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-C01 | L7 | 2 | 1 | {'calibration': 2} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-C02 | L7 | 2 | 1 | {'calibration': 2} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-C03 | L7 | 2 | 1 | {'calibration': 2} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-D1 | L7 | 3 | 1 | {'ablation': 2, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1, 'preregistered': 1} | 2 | 2 |
| TDM-E-L9-D2 | L7 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'blocked_on_impl': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-E1 | L7 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-E2 | L7 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'blocked_on_impl': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-G1 | L7 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'blocked_on_impl': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-G2 | L7 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'blocked_on_impl': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-G3 | L7 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'blocked_on_impl': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-G4 | L7 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'blocked_on_data': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-G5 | L7 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'blocked_on_impl': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-V1 | L7 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L9-V2 | L7 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L9-V3 | L7 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-E-L9-Z1 | L7 | 2 | 1 | {'ablation': 1, 'shadow': 1} | {'blocked_on_impl': 1, 'empty': 1} | 1 | 1 |
| TDM-E-L9-Z2 | L7 | 2 | 1 | {'ablation': 1, 'shadow': 1} | {'blocked_on_impl': 1, 'empty': 1} | 1 | 1 |
| TDM-F-C1 | L6 | 3 | 1 | {'comparison': 1, 'shadow': 2} | {'empty': 1, 'preregistered': 2} | 2 | 2 |
| TDM-F-C1-01 | L6 | 2 | 1 | {'shadow': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-F-C1-02 | L6 | 3 | 1 | {'shadow': 3} | {'empty': 1, 'preregistered': 2} | 2 | 2 |
| TDM-F-C1-03 | L6 | 2 | 1 | {'shadow': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-F-C2 | L6 | 2 | 1 | {'comparison': 1, 'shadow': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-F-C2-01 | L6 | 2 | 1 | {'comparison': 1, 'shadow': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-F-C2-02 | L6 | 4 | 1 | {'shadow': 4} | {'empty': 1, 'preregistered': 3} | 3 | 3 |
| TDM-F-C2-03 | L6 | 2 | 1 | {'comparison': 1, 'shadow': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-F-C2-04 | L6 | 2 | 1 | {'shadow': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-F-C3 | L6 | 2 | 1 | {'comparison': 1, 'shadow': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-F-C3-01 | L6 | 3 | 1 | {'comparison': 2, 'shadow': 1} | {'empty': 1, 'preregistered': 2} | 2 | 2 |
| TDM-F-C3-02 | L6 | 2 | 1 | {'shadow': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-F-C3-03 | L6 | 2 | 1 | {'comparison': 1, 'shadow': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-F-C3-04 | L6 | 2 | 1 | {'shadow': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-F-C3-05 | L6 | 2 | 1 | {'shadow': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-F-FLOW | L6 | 2 | 1 | {'comparison': 1, 'shadow': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-P-FLOW | L4 | 2 | 1 | {'ablation': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-P-P1 | L4 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-P-P1-01 | L4 | 2 | 1 | {'comparison': 2} | {'blocked_on_impl': 1, 'empty': 1} | 1 | 1 |
| TDM-P-P1-02 | L4 | 4 | 1 | {'calibration': 2, 'comparison': 2} | {'blocked_on_impl': 1, 'empty': 1, 'preregistered': 2} | 3 | 3 |
| TDM-P-P1-03 | L4 | 3 | 1 | {'calibration': 1, 'comparison': 2} | {'blocked_on_impl': 1, 'empty': 1, 'preregistered': 1} | 2 | 2 |
| TDM-P-P1-04 | L4 | 6 | 1 | {'calibration': 3, 'comparison': 3} | {'blocked_on_data': 1, 'blocked_on_impl': 1, 'empty': 1, 'preregistered': 3} | 5 | 5 |
| TDM-P-P1-05 | L4 | 5 | 1 | {'ablation': 1, 'comparison': 3, 'shadow': 1} | {'blocked_on_impl': 1, 'empty': 1, 'preregistered': 3} | 4 | 4 |
| TDM-P-P1-06 | L4 | 2 | 1 | {'comparison': 2} | {'blocked_on_impl': 1, 'empty': 1} | 1 | 1 |
| TDM-P-P2 | L4 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-P-P2-01 | L4 | 3 | 1 | {'comparison': 3} | {'empty': 1, 'preregistered': 2} | 2 | 2 |
| TDM-P-P2-02 | L4 | 3 | 1 | {'ablation': 1, 'comparison': 2} | {'blocked_on_data': 1, 'blocked_on_impl': 1, 'empty': 1} | 2 | 2 |
| TDM-P-P2-03 | L4 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-P-P2-04 | L4 | 3 | 1 | {'ablation': 1, 'comparison': 2} | {'blocked_on_impl': 1, 'empty': 1, 'preregistered': 1} | 2 | 2 |
| TDM-P-P3 | L4 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-P-P3-01 | L4 | 4 | 1 | {'comparison': 4} | {'blocked_on_impl': 1, 'empty': 1, 'preregistered': 2} | 3 | 3 |
| TDM-P-P3-02 | L4 | 3 | 1 | {'calibration': 1, 'comparison': 2} | {'blocked_on_impl': 1, 'empty': 1, 'preregistered': 1} | 2 | 2 |
| TDM-P-P3-03 | L4 | 3 | 1 | {'ablation': 1, 'comparison': 2} | {'blocked_on_impl': 1, 'empty': 1, 'preregistered': 1} | 2 | 2 |
| TDM-P-P3-04 | L4 | 4 | 1 | {'calibration': 2, 'comparison': 2} | {'empty': 1, 'preregistered': 3} | 3 | 3 |
| TDM-X-FLOW | L5 | 2 | 1 | {'ablation': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-X-R1 | L5 | 2 | 1 | {'shadow': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-X-R1-01 | L5 | 3 | 1 | {'ablation': 1, 'comparison': 2} | {'empty': 1, 'preregistered': 2} | 2 | 2 |
| TDM-X-R1-02 | L5 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-X-R1-03 | L5 | 2 | 1 | {'calibration': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-X-S1 | L5 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-X-S1-01 | L5 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-X-S1-02 | L5 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-X-S1-03 | L5 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-X-S1-04 | L5 | 5 | 1 | {'calibration': 3, 'comparison': 2} | {'empty': 1, 'preregistered': 4} | 4 | 4 |
| TDM-X-S1-05 | L5 | 2 | 1 | {'ablation': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-X-S1-06 | L5 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-X-S2 | L5 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-X-S2-01 | L5 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-X-S2-02 | L5 | 4 | 1 | {'calibration': 2, 'comparison': 2} | {'empty': 1, 'preregistered': 3} | 3 | 3 |
| TDM-X-S2-03 | L5 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-X-S2-04 | L5 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-X-S2-05 | L5 | 2 | 1 | {'comparison': 2} | {'empty': 1, 'preregistered': 1} | 1 | 1 |
| TDM-X-S2-06 | L5 | 2 | 1 | {'ablation': 1, 'comparison': 1} | {'empty': 1, 'preregistered': 1} | 1 | 1 |

## 四、已出分成绩清单（门柱 vs 实测）

| card_id | run_id | verdict | pillars_all_pass | oos_ok | regimes | ic_mean | mono | oos_ic | n | fails |
|---|---|---|---|---|---|---|---|---|---|---|
| TDM-E-L1-S1/calibration/02_指数趋势位置 | examcard-S1-trend-20261010 | fail | False | False | ['bull', 'bear'] | -0.0012788417060495502 | 1.0 | 0.04454308396896059 | 1702 | ic_mean -0.0013 < 0.02; oos_sign_flip oos=0.0445 is=-0.0013 |
| TDM-E-L1-S0-1/calibration/02_新闻情绪时滞 | nightmine-02_新闻情绪时滞 | fail | False | False | ['bull', 'bear'] | -0.023109545890572448 | -0.22424242424242422 | 0.06776204714746234 | 1622 | mono_spearman -0.224 < 0.6; ic_mean -0.0231 < 0.02; oos_sign_flip oos=0.0678 is=-0.0231 |
| TDM-E-L1-S2/calibration/02_涨停家数 | nightmine-02_涨停家数 | fail | False | False | ['bull', 'bear'] | -0.014636875822621773 | -0.2606060606060606 | 0.0641936089358011 | 1622 | mono_spearman -0.261 < 0.6; ic_mean -0.0146 < 0.02; regime_sign_flip {'bull': -0.08637621333469589, 'bear': 0.006065302104912393}; oos_sign_flip oos=0.0642 is=-0.0146 |
| TDM-E-L1-S2/calibration/03_跌停家数 | nightmine-03_跌停家数 | fail | False | False | ['bull', 'bear'] | 0.052759730276699834 | 0.5393939393939393 | -0.012050829415383291 | 1622 | mono_spearman 0.539 < 0.6; oos_sign_flip oos=-0.0121 is=0.0528 |
| TDM-E-L1-S2/calibration/04_炸板率 | nightmine-04_炸板率 | fail | False | False | ['bull', 'bear'] | 0.07856819508616897 | 0.5757575757575757 | -0.010806251830648964 | 1622 | mono_spearman 0.576 < 0.6; oos_sign_flip oos=-0.0108 is=0.0786 |
| TDM-E-L1-S2/calibration/05_封板率 | nightmine-05_封板率 | fail | False | False | ['bull', 'bear'] | -0.07856819508616897 | -0.6363636363636362 | 0.010806251830648964 | 1622 | mono_spearman -0.636 < 0.6; ic_mean -0.0786 < 0.02; oos_sign_flip oos=0.0108 is=-0.0786 |
| TDM-E-L1-S2/calibration/06_连板最高高度 | nightmine-06_连板最高高度 | fail | False | True | ['bull', 'bear'] | -0.018375788057875635 | 0.07878787878787878 | -0.06238580668691902 | 1622 | mono_spearman 0.079 < 0.6; ic_mean -0.0184 < 0.02; regime_sign_flip {'bull': -0.06286929256233367, 'bear': 0.016098939836664154} |
| TDM-E-L1-S2/calibration/08_净广度 | nightmine-08_净广度 | fail | False | False | ['bull', 'bear'] | -0.01070485704926972 | -0.11515151515151514 | 0.024566197281316142 | 1622 | mono_spearman -0.115 < 0.6; ic_mean -0.0107 < 0.02; regime_sign_flip {'bull': -0.05006311539148888, 'bear': 0.0063029888329039566}; oos_sign_flip oos=0.0246 is=-0.0107 |
| TDM-E-L9-A04/calibration/02_估值ERP分位日增量 | nightmine-02_估值ERP分位日增量 | fail | False | False | ['bull', 'bear'] | 0.046670542330728974 | 0.9030303030303028 | -0.004755062276188134 | 4063 | oos_sign_flip oos=-0.0048 is=0.0467 |
| TDM-E-L2-09/calibration/02_板块催化剂密度 | nightmine-L2-09-density | fail | False | True | ['bull', 'bear'] | -0.027908808204430206 | -0.7212121212121211 | -0.03360817429586608 | 2367 | mono_spearman -0.721 < 0.6; ic_mean -0.0279 < 0.02; regime_sign_flip {'bull': 0.0002848796318657199, 'bear': -0.028969879096233806} |
| TDM-E-L1-S2/calibration/09_limit_up_count_derived | nightmine-09_limit_up_count_derive | fail | False | False | ['bull', 'bear'] | -0.014636875822621773 | -0.2606060606060606 | 0.0641936089358011 | 1622 | mono_spearman -0.261 < 0.6; ic_mean -0.0146 < 0.02; regime_sign_flip {'bull': -0.08637621333469589, 'bear': 0.006065302104912393}; oos_sign_flip oos=0.0642 is=-0.0146 |
| TDM-E-L1-S2/calibration/10_limit_down_count_derived | nightmine-10_limit_down_count_deri | fail | False | False | ['bull', 'bear'] | 0.052759730276699834 | 0.5393939393939393 | -0.012050829415383291 | 1622 | mono_spearman 0.539 < 0.6; oos_sign_flip oos=-0.0121 is=0.0528 |
| TDM-E-L1-S2/calibration/11_broken_board_rate_derived | nightmine-11_broken_board_rate_der | fail | False | False | ['bull', 'bear'] | 0.07856819508616897 | 0.5757575757575757 | -0.010806251830648964 | 1622 | mono_spearman 0.576 < 0.6; oos_sign_flip oos=-0.0108 is=0.0786 |
| TDM-E-L1-S2/calibration/12_sealed_board_rate_derived | nightmine-12_sealed_board_rate_der | fail | False | False | ['bull', 'bear'] | -0.07856819508616897 | -0.6363636363636362 | 0.010806251830648964 | 1622 | mono_spearman -0.636 < 0.6; ic_mean -0.0786 < 0.02; oos_sign_flip oos=0.0108 is=-0.0786 |
| TDM-E-L1-S2/calibration/13_max_consec_limit_height_derived | nightmine-13_max_consec_limit_heig | fail | False | True | ['bull', 'bear'] | -0.018375788057875635 | 0.07878787878787878 | -0.06238580668691902 | 1622 | mono_spearman 0.079 < 0.6; ic_mean -0.0184 < 0.02; regime_sign_flip {'bull': -0.06286929256233367, 'bear': 0.016098939836664154} |
| TDM-E-L1-S2/calibration/14_consec_limit_count_ge2_derived | nightmine-14_consec_limit_count_ge | fail | False | False | ['bull', 'bear'] | -0.017359123445562945 | 0.0303030303030303 | 0.023982423812634237 | 1622 | mono_spearman 0.030 < 0.6; ic_mean -0.0174 < 0.02; oos_sign_flip oos=0.0240 is=-0.0174 |
| TDM-E-L1-S2/calibration/15_net_breadth_derived | nightmine-15_net_breadth_derived | fail | False | False | ['bull', 'bear'] | -0.01070485704926972 | -0.11515151515151514 | 0.024566197281316142 | 1622 | mono_spearman -0.115 < 0.6; ic_mean -0.0107 < 0.02; regime_sign_flip {'bull': -0.05006311539148888, 'bear': 0.0063029888329039566}; oos_sign_flip oos=0.0246 is=-0.0107 |

## 五、GPU 窗取证（采样器每 10 分钟一档）

- samples: 17
- first_sample: 2026-10-10 06:33:06
- last_sample: 2026-10-10 08:33:38
- util_peak_pct: 44.0
- util_mean_pct: 28.59
- util_ge90_share: 0.0
- mem_used_peak_mib: 2372.0

### F06 窗现场（manifest+rc=W1 正式验收判据）

- last_fired_header: ==== F06 grid pipeline fired at 2026-10-09 19:17:00 ====
D:\ZephyrAlpha\scripts\
- elapsed_hours_since_fired: 13.35
- a2_ic_compose_markers: 1073
- fwd_shift_markers: 509
- proxy_sec_per_cell_wall: 44.8
- grid_dir_files: []
- manifest_present: False
- n_samples_requested: 6000
- 停手条款对照（架构册 §六，阈值 3.5 s/格）：实测代理值=44.8 s/格 ⇒ 判 L2 批并行**不触发**（口径=进度代理计数，须以收窗 summary 复核后再定档）

## 六、mined_out 申报（台账正则抽取，逐车道）

- L0d_ledger: mined_out=0 []
- L1_ledger: mined_out=0 []
- L2_ledger: mined_out=0 []
- L3_ledger: mined_out=0 []
- L4_ledger: mined_out=0 []
- L5_ledger: mined_out=0 []
- L6_ledger: mined_out=1 ['TDM-F-C1-02']
- L7_ledger: mined_out=1 ['TDM-E-L9-C01']
- L8b_ledger: mined_out=0 []

