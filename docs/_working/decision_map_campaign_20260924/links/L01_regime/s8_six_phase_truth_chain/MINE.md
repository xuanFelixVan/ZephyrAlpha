---
ttl: task_bound
title: L01-S8 子模块挖矿簿 · 六段相位折算真源链（R2SIX/预算带/相位全史）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成（含对 SKEL 三项状态改判）
---

# L01 · S8 六段相位折算真源链

**① 职责一句话**：把七态概率的 dominant 折算成 SIX_STATES 六段相位（含微观腿两段的合成），并唯一决定预算带映射，是全链"状态→档位"的法定咽喉。

**② 现状实测**

| 位点 | 实测 |
|---|---|
| 词表真源 | `src/zephyr/signal_ashare/core/environment_switch.py:41-48` SIX_STATES=(capitulation, accumulation, ignition, expansion, euphoria, distribution) |
| 映射唯一位点 | `src/zephyr/pf_core/strategy_engine/framework_composer.py:REGIME_STATE_TO_ACTIVATION_PHASE`（r1/r2 震荡不路由=宁漏勿误） |
| 挂图侧同表 | `scripts/backtest/auto_mount.py` R2SIX + `resolve_six_phase`（微观腿：乖离 250 日分位≥0.90 ∧ 20 日上涨家数占比分位≥0.85 ∧ 60 日收益>0 → euphoria；亢奋记忆窗破 MA20 ∧ br20<50% → distribution） |
| **改判 1（已落地）** | `src/zephyr/strategy_pipeline/daily_decision_orchestrator.py:534-548` `_regime_to_segment()` 现**惰性导入 framework_composer 真源**，导入失败返回 None→S2 走 no_trade 保守侧，函数 docstring 明写"禁 fallback 本地表"（占位表 75% 情绪门宽教训入注）；SKEL 记为"M 态未提交"——本册实测**已随 commit d27e0f0df3 进 HEAD**（`git log` 实测，同批含 L2 门接线/D13） |
| 预算带 | 同件 `BUDGET_BANDS` :103 起（capitulation 0-10%/accumulation 20-30%/ignition 30-50%/…），头注 :94 标"草案值 v0，裁定编号 305（ruling_registry 已登记）标可调" |
| 漂移守卫 | `tests/strategy_pipeline/test_decision_orchestrator.py::TestSixStateTruthChainSwitch`（docstring :539 指认） |
| **改判 2（仍未落地）** | 相位全史物化：生成器 `scripts/audit/t0_six_phase_materialize.py` 已在 HEAD（:159-166 写 `six_phase_history_v1.{csv,meta.yaml}`），**但 `docs/_working/t0_matrix/` 实测目录清单内无该二件**（仅 LEDGER/FINAL_REPORT/reconcile_pack 等）→ L01-C05 落地未达 |

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：dominant（S6 表）宏观腿 + 399106 广度微观腿（断更日 EQW_ALLA 补位，见 S4 册 G3）。外部：市场阶段划分的公开成例=四阶段/五阶段周期模型（本轮检索命中多为教程文，未达两源可引门槛）→ **已查无（可入图级）** |
| ②下游 | 内部：编排器 S2→position_cap→S5 预算；整装回测 activation α；做T状态门 P2-01；sector_preference 第一轴；P1-T1/T3 条件轴；挂图 CLASS_CANDIDATE_STATES。外部：已查无（下游=本仓） |
| ③算法 | 内部：两轴合成 + PHASE_PREEMPT（r10/r11 抢占）。外部：微观腿阈值（分位 0.90/0.85）为经验值，未见外部可引口径 → 已查无（列长尾） |
| ④后端 | 内部：**双表并存仅靠守卫钉**（R2SIX vs composer；附录 C 步 2 共享真源收编未完）；euphoria/distribution 无 r 态来源⇒纯宏观腿恒不激活（composer 披露在案） |
| ⑤前端 | 内部：挂图 phase_overlay + 仪表盘相位条。外部：已查无 |
| ⑥数据字段 | 内部：需 br20/乖离分位/MA20——字段在；399106 家数断更为已知质量洞（成例 dd04d9d20c） |

**④ 缺口清单**

| 编号 | 内容 | 册内出处 |
|---|---|---|
| L01-C04 步 2/4 | 共享真源收编 + 历史结论口径版本戳 | 附录 C 在册 |
| L01-C05 | 六段全史 CSV 0033 批落地（本册实测未落） | SKEL 在册 |
| LK-16 | 六段↔盘中五态映射未落地 | 09 号文在册 |
| L01-S8-G1 | 微观腿两阈值无预注册考试卡（euphoria/distribution 判据属经验值直接进产） | 册内未见 |

**⑤ 自审闸三态裁定**

| 缺口 | 裁定 | 理由 |
|---|---|---|
| L01-C04 步 2/4 | 施工（P1，在册） | 两表靠守卫=守卫失效即静默分叉；收编后净 -1 表 |
| L01-C05 | 施工（P1，在册） | 终局要"相位全史可自动重算"；前置=creation_token+模块翻译登记（机械动作） |
| LK-16 | 挂起排期 | 解锁=L09 车道六段↔五态映射页；本层只供真源侧 |
| L01-S8-G1 | 挂起排期 | 终局要"每判据有考试"，但现改=动判据（禁区）；解锁=下一轮预注册窗口，先登记为候选卡 |

**⑥ 挖矿日志**

| 轮 | 矿脉 | 判定 | noise 归因 |
|---|---|---|---|
| R1 | 内部：orchestrator 切换态 + commit 归属实测 | signal（改判 1） | — |
| R2 | 内部：物化脚本与产物目录对表 | signal（改判 2：脚本在、产物不在） | — |
| R3 | 外部：市场阶段划分口径 | noise | 归因=**来源质量不足**（命中教程/自媒体，无机构或学术两源）→ 已查无 |

**本册封矿判据**：四位点全实测 + 两项改判留证 → **子模块封矿**。
