---
ttl: task_bound
title: "门禁健康审计报告（99 台·数据驱动）"
session: st-commitsys-20260924
---

# ③门禁健康审计（2026-09-24 st-commitsys-20260924）

数据窗：`.runtime/audit/gate_execution_stats.jsonl` 全量 1612 次提交×99 台逐次计时；死信 112 封（`.runtime/commit_queue/dead/`）。
纪律：门禁只加严不放松（裁定#321）；注册表净删=Owner 门位（宪法 §5）；本报告**只提案不动刀**，每项施工前带等价证明+红蓝。

## A. 提速靶点（累计耗时 TOP20，1612 提交窗）

| 台 | 累计耗时 | 运行次数 | 均耗 | 提案 |
|---|---|---|---|---|
| CREATE-GUARD | 10,327s | 1176 | 8.8s | 40k 行 registry 每次重解析→进程内缓存+mtime 失效；等价证明=双跑 500 提交判定逐台一致 |
| CAPABILITY-OVERLAP | 5,788s | 1176 | 4.9s | CloneGuard AST 比对降采样（只比 own 新增 vs 同目录），外来件已 own 化 warn |
| CH-VERSION-COL | 5,080s | 1108 | 4.6s | 先正则预筛含 ReplacingMergeTree 行再 AST |
| RECONCILER-HEALTH | 4,489s | 1107 | 4.1s | governance.db 查询结果 30s 缓存（own-scope 已条件触发仍 4.1s/次） |
| GATE-ERRCODE-CONSISTENCY | 4,305s | 487 | 8.8s | 六断言只在 error_code_registry.yaml 或 src 变更时全跑（files_trigger 收窄） |
| REGISTRY-MASS-DELETION | 3,892s | 1176 | 3.3s | difflib 全文件对比→只对 staged∩catalogs 文件跑（own-scope 化） |
| NO-SECRET-HARDCODE | 3,082s | 1090 | 2.8s | added 行正则预筛密钥模式再深扫 |
| GATE-PANORAMA-ALIGNMENT(legacy) | 2,489s | 1054 | 2.4s | legacy 注册与 MAP-ALIGNMENT 同文件双跑→退役 legacy 注册位（等价=新台已覆盖同判据） |
| CH-BATCH-SIZE / GIT-CALL-BUDGET / GATE-DOMAIN-FK / SSOT-REDEFINITION / ARCH-REFERENCE / BLUEPRINT-FORMAT / MUTABLE-CONST | 各 1,400-2,400s | — | 1.6-2.0s | 同款预筛/收窄思路，P2 批 |

Top20 合计≈62,000s（窗内）≈均摊每提交 38s——**占门禁链 55%+**。全链 P50 43s（gateaudit 口径）→上述 P1 落地预估 -20s/提交；k4 池化 4 路并行后预检耗时直接除以吞吐系数，两项叠加=队列吞吐再翻倍。

## B. 拦截排行（真实阻断，与死信簇互相印证）

MUTABLE-CONST-WITHOUT-FINAL 230 / BLUEPRINT-FORMAT 113 / DEPGRAPH-PRE-REGISTRATION 110 / NO-LONG-PARAM-LIST 109 / CREATE-GUARD 108 / G1 96 / ORPHAN-MODULE 95 / NO-BARE-SQL 79 / VOCAB-HARDCODE 78 / HELD-OVERLAP 76。
死信面（112 封）与拦截面排序一致性好：CREATE-GUARD/ORPHAN/COMPLEXITY/BLUEPRINT 全在双榜——**撞墙热点=拦截热点=指南重点章节**，验证指南分层正确。

## C. 观测缺口（机制健康）

1. `gate_execution_stats` 混入非在册 gate_id：G1、bad、NO-LONG-PARAM-LIST、DEPGRAPH-WRITE-PATH、GATE-PANORAMA-ALIGNMENT（legacy）、ARCH-REFERENCE（并入 REFERENCE-INTEGRITY 前的旧 id）——**stats 写入面口径未随 114→99 合并同步**。提案：stats 写入器按 in_process 名册白名单归一，legacy id 映射聚合台（机生口径，防下次审计再踩）。
2. 条件触发台触发率 healthy：trigger_skip TOP=86/1612（5.3%），无零触发实锤台；低频台（GATE-PRECOMMIT-OFFLINE/ID-UNIQUENESS 只扫 .pre-commit-config.yaml）保留（低频≠零价值，判据唯一）。

## D. 瘦身候选（按 gslim 方法论，观察期后评）

- PANORAMA legacy 注册位退役（与 MAP-ALIGNMENT 同判据双跑）——同真源可派生→必并。
- ARCH-REFERENCE/BLUEPRINT-AMODULE-CROSS-CHECK 旧 id 清理（并入聚合台后 stats 遗留）。
- 每项退役须：等价证明（新台覆盖判据全集）+7 天观察窗+净删申报+Owner 批。

## E. 结论

99 台健康面良好：无零触发实锤、无判据过时实锤（两起"漂移"实为他会话在途编辑，已被 HEAD 指纹闸正确排除）；主要矛盾=**速度**不是数量。P1 提速六台包（CREATE-GUARD/CAPABILITY-OVERLAP/CH-VERSION-COL/RECONCILER-HEALTH/ERRCODE/MASS-DELETION）+stats 口径统一=下一批施工提案，候总指挥/Owner 批后动刀（gate 改动带 A/B 等价证明）。
