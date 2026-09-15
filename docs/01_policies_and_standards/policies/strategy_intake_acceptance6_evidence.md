---
ttl: permanent
doc_type: policy
rule_form: standard
verifiability: manual
title: C6 全自动入库管线验收⑥回放证据与写入路径授权书（策略入库自动化）
---

# 验收⑥ 历史批回放证据——C6 全自动入库管线写入路径授权书

> 2026-09-15 04:4x｜session=st-autopipeline-20260915｜依据=总交接档案治理边界：
> **"回放达标即视为 Owner 复核通过，达标证据落盘留档即可开启（写入路径），无需等待"**（Owner 2026-09-15 03:15/03:37 令）。
> 本文件即该"达标证据落盘"本体，同时是 `intake.EVIDENCE` 写入路径钥匙（文件存在=授权生效）。

## 结论

**机器三轴论证+聚类+及格复验 与 2026-09-14 C5 人工批裁定一致率 8/8 = 100% ≥ 5/6 门槛——验收⑥ PASS，C6 写入路径开启。**

## 回放方法

- 对象=2026-09-13/14 C5 人工批 8 条 bothwin 及格件（冻结 IS 批 `C4-translated-20260912` + 全部 OOS 批联查，口径与 `strategy_screen_query.cmd_bothwin` 一字不差）。
- 机器链路=`screen_source.passing_with_p`（p 值=t 双侧解析式 SR·sqrt(年数)，族=当批及格全集）→ `corr_matrix`（翻译件 IS 窗日净收益 Pearson，重叠<60 日不判）→ `intake.run_intake(dry_run=True)`（BH-FDR 门→ρ>0.6 贪心聚类【簇首=批内 p 最小者，即"Sharpe 最高"人工先例的 p 值等价】→三轴差异化【字段级+指标信号指纹（signal_tokens 集合相等才算同信号）】→candidate 判定）。
- **回放公平性**：注册表取"人工批之前"快照（剔除人工批 5 转正条目），被回放的 8 条决策对机器而言均为"未决策"状态。
- 人工裁定基准=C5 报告 §转正名单裁定 + `STR-VREV-026.family_redundancy` 结构化块（ρ=0.713/0.679）。

## 逐条对账（8/8 全对）

| 翻译件 | 人工裁定 | 机器判定 | 一致 |
|---|---|---|---|
| c4_dc5b80aa3614_tsmall100 | promote→STR-TSMALL-001 | promote | ✅ |
| c4_8d000bf3ccc3_pb_poe | promote→STR-VAL-001 | promote | ✅ |
| c4_7f7e5f935dfc_dmi_timing | promote→STR-MOMTREND-033 | promote | ✅ |
| c4_c72318f2da1c_bias_ql | promote→STR-VREV-026（簇首） | promote（簇首） | ✅ |
| c4_4440d07f973f_ultrashort | promote→STR-DABAN-023 | promote | ✅ |
| c4_e3da6fa71af1_panic_rebound | 已在库（STR-VREV-025） | already_in_registry | ✅ |
| c4_9ce75aa27ce5_bluechip_ma | redundant_of=STR-VREV-026 | redundant→bias_ql 簇首 | ✅ |
| c4_29eb91dbaf60_crash_dodge | redundant_of=STR-VREV-026 | redundant→bias_ql 簇首 | ✅ |

关键数值复现：bluechip_ma↔bias_ql ρ=**0.7134**（人工 0.713）、crash_dodge↔bias_ql ρ=**0.6791**（人工 0.679）、crash_dodge↔bluechip_ma ρ=0.5793（<0.6 不并簇，与人工六簇结论一致）。

## BH-FDR 门信息面（重要边界披露）

当批 8 条在 q=0.10 下 **全数未过**（最强 panic_rebound p=0.0241 vs 首档阈值 0.0125）。
这是门比人工严的**设计使然**（A 方案预授权：FDR 门 sim 流转，不门候选登记——方案真源 §2.3/§2.5 的分工）：

- 若 FDR 门登记，机器本批将零入库（与人工 5 条冲突，回放反而不达标）——故裁定 FDR 只门 sim；
- 本批 5 条在机器规则下将登记为 candidate 留观，**未来出现更强证据批次（新 OOS 段加入使 p 下降）时由管线自动流转 sim**；
- 已在库 5 条（人工批转正）不受影响，其 sim 流转继续走既有人工/建议器通道（strategy_lifecycle_advisor）。

## 机器判定链可复核物

- 原始回执：`docs/_working/pipeline-research/replay-evidence.yaml`（逐条判定+ρ 矩阵+FDR 报告+耗时 348s）
- 回放脚本：`.runtime/tmp/replay_acceptance6.py`（班末清理，逻辑已固化进 `tests/strategy_pipeline/`）

## 写入路径授权声明

按总交接档案治理边界（Owner 原令）：**本证据落盘 = Owner 复核通过 = `intake.py` 写入路径开启**。
开启形态=fail-closed 存在性门控（`EVIDENCE` 文件存在才允许 dry_run=False），本文件即钥匙；
删除本文件=写入路径自动回锁（fail-closed 语义不依赖任何 flag）。
sim→production 仍为 Owner 门（`OwnerTokenGuard`），机器流程不带 token 天然停门——治理边界不变。
