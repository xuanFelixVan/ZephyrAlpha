---
ttl: task_bound
title: "战役验证与红蓝对抗报告（两轮）"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-01
---

# 战役验证与红蓝对抗报告（两轮）

> 验证代理 P4（只读为主）；被验对象=三笔落地 commit：46db7d42f5（SOP 升级）/ e405020493（册面接线）/ 080fdfec（MAC 传感器下游接线）。
> 验证环境注意：worktree 存在他会话在途覆写（295 处改动），故门禁读数按 worktree 实跑 + HEAD 基线算术核验双轨记录。

## 一、第一轮门禁读数（2026-10-01）

| # | 门禁 | 期望 | 实测 | 判定 |
|---|------|------|------|------|
| G1 | generate_wiring_registry.py --check | rc=0 | rc=0 | PASS |
| G2 | check_wiring_orphan.py | rc=0 problems=0 | problems=0 orphans=0 | PASS |
| G3 | check_registry_consistency.py | CR-007b PASS | CR-007b=PASS；CR-007 余 23 项 STALE（见注1） | PASS（批外余项见注2） |
| G4 | TDM yaml + 6 卡 9 处 mounts | YAML 可解析、9 处在图 | YAML OK；HEAD 基线 9/9 在图（注3） | PASS（HEAD 基线） |
| G5 | pytest 盘前两文件 | 43 passed | 43 passed（单测 37 + e2e 6；e2e 实际路径=tests/integration/test_phase2_premarket_intraday_e2e.py，任务书写的 plan_engine/ 路径不准） | PASS |

注1：23 项 STALE 中 REG-DATAFLOW-001（ROOR=334/实测=315）系 worktree 漂移伪影——worktree 的 data_asset_registry.yaml 遭他会话覆写（334→315 datasets，8004+/8376- 重排）；HEAD 基线 datasets=334=ROOR entry_count=334，算术核验一致。e405 commit 声称"REG-DATAFLOW 已修离 STALE"在 HEAD 成立。
注2：其余 22 项（REG-SCRIPT-001/002、REG-RESCHED-001、REG-CATALOG-001、REG-STATE-VOCAB-001、REG-DOC-001、REG-GATE-CAT-001、REG-INFRA-001、REG-FUNC-DOMAIN-001、REG-ARCH-ISSUE-001、REG-CAPCAN-001、REG-GEN-001、REG-ERRCODE-001、REG-ARCH-001、REG-UNI-001、REG-TECHNICAL-INDICATOR-001、REG-PAT-001、REG-DATAFLOW-001（伪影）、REG-FLD-001、REG-DAL-001、REG-BTB-001、REG-ATH-001、REG-METAQ-001）全为批外既有全仓漂移；e405 时点为 22 项，现 23 项之差=后续战役（如 1c9f4195f2 净删批）新增漂移，非本批缺陷。
注3：9 处挂点=HEAD nodes：TDM-E-L1 大盘总闸（STR-E-TIMING-001 verified + STR-MOMTREND-002/019 proposed）、TDM-E-L3 个股选择（STR-VREV-001）、TDM-X-FLOW 离场（STR-VREV-001）、TDM-F-FLOW 组合（MULTIFACTOR-098/099）、TDM-P-FLOW 持仓（MULTIFACTOR-098/099）——与 e405 commit 分账逐字吻合。

## 二、红队六招结果

| 招 | 攻击面 | 结果 | 明细 |
|----|--------|------|------|
| R1 | DS-306~345 撞号 | 未命中（PASS） | 40 张全新增、无重复号、无既有号段冲突、无非标 id；HEAD datasets 总数 334 与 entry_counts/ROOR 三处一致 |
| R2 | 幽灵降级残留引用 | **命中（登记不修）** | DS-029~039 已降 candidate，但 JOB-028~038（status=active）的 outputs 仍引用它们，共 11 处残留；DS-224/225 无 jobs 引用。属 production 域语义流转（risk_tier=high 人门位），非机械可修——修复方向：或降级对应 jobs 或按"设计态 job+待物化 DS"豁免登记，须 Owner/域会话裁定 |
| R3 | mounts 挂不存在卡 | 未命中（PASS） | 6 张 strategy_ref 全在 strategy_registry 在册：E-TIMING-001/MULTIFACTOR-098/099=active（mount verified/proposed 语义自洽），VREV-001/MOMTREND-002/019=candidate（proposed 自洽） |
| R4 | 20 岛 vs census 台账 | 未命中（PASS） | wiring_registry.consumption_islands 20 条 entity_id 与 data/runtime/consumption_census_ledger.json 逐条对上（20/20），booked_at 全='2026-09-29'，家族分布 macro4/strategy2/factor9/indicator5 |
| R5 | SOP §9A vs §14 自洽 | 未命中（PASS） | §14 编号 17-19 与 §11 十四查+§13 十五/十六查连续；17→§9A、18→§9B、19→§9D 引用节均存在；相对链接 4 处全存在（factor_mining_sop/skeleton_mining_policy/冷库 SOP/census ledger）；§9C"473 岛"分项和=115+126+129+61+15+27=473 自洽；真源 architecture_model/data/data_sources_registry.yaml 在仓库根存在 |
| R6 | DS-123 复活复验 | 未命中（PASS） | CH 只读查 daily_valuation：rows=273847、close≠0=272485（99.5%）、max(trade_date)=2026-09-30——与册面复登数字逐项一致 |

## 三、修复动作

- 可机械修复小错：未发现（本批册面/文档零错字零计数笔误；R2 命中属结构性语义问题，按"结构性只登记不修"处置）。
- 登记不修的结构性发现 2 项：
  1. **他会话在途覆写**：worktree 的 config/trading_decision_map.yaml（9 mounts 被回退为 []）与 data_asset_registry.yaml（-19 datasets+全量重排）存在未提交改动；HEAD 三笔 commit 基线完好。处置建议：由在途会话按宪法 §2.8/§3.4 自查（编辑消失先查 stash_notice；他会话在途违规不代修），勿盲目 revert。
  2. **R2 幽灵残留引用 11 处**（JOB-028~038 → DS-029~039）：见上表，待域裁定。

## 四、第二轮复跑读数（2026-10-01，与第一轮同环境）

| # | 门禁 | 第一轮 | 第二轮 | 稳定 |
|---|------|--------|--------|------|
| G1 | wiring --check | rc=0 | rc=0 | 是 |
| G2 | orphan | problems=0 | problems=0 | 是 |
| G3 | CR-007b / CR-007 | PASS / 23 STALE | PASS / 23 STALE（同清单） | 是 |
| G4 | TDM yaml + HEAD mounts | OK / 9 | OK / 9 | 是 |
| G5 | pytest | 43 passed | 43 passed | 是 |
| R2 | 幽灵残留引用 | 11 | 11 | 是 |

## 五、结论

1. 三笔落地 commit 在 HEAD 基线上：五项门禁全过、红队六招四过一伪影一命中（命中项均非本批新引入的可机械修复缺陷）。
2. "连续两次 0 问题"未达成——但两次复跑读数完全一致（稳定复现），且两处登记项均为 worktree 在途漂移与批前既有语义挂账，非三笔 commit 的回归缺陷。
3. 落地质量判定：**PASS（附 2 项登记移交）**——登记项移交在途会话/域 Owner 处置，不阻塞本批验收。
