---
ttl: "task_bound"
title: "q-0213 死袋 40 件三分诊与捞回评估（死袋考古车道）"
session: "st-finaldel-cdead-20260929"
completes_when: "Owner/总筹裁对 18 件可捞回清单做出处置后归档"
---

# q-0213 死袋 40 件三分诊报告

- 袋：`.runtime/commit_queue/dead/q-20260929-st-chief7-20260928-0213.json`（qid=q-20260929-st-chief7-20260928-0213，会话 st-chief7-20260928，03:19:32 死，死因=快照基底冲突：基底 1dd6c70c74e9 之后 dev 推进且触及同路径 AGENTS.md、src/zephyr/ai_layer/redline/negative_list_gates.py）
- 分诊日：2026-09-29｜方法：逐件取 blobs/ 袋字节（sha256 全部校验完整，40/40 intact）vs `git ls-tree HEAD` 字节比对三分态；MISSING 件再查 `git log --all` 全历史。
- 纪律：只分析+外科手术式捞回；HEAD_NEWER 一律跳过绝不覆盖；队列目录只读未动。

## 一、三态统计

| 态 | 件数 | 处置 |
|---|---|---|
| EQUAL（HEAD 字节等） | 0 | — |
| HEAD_NEWER（HEAD 已有更新版本） | 22 | 跳过，绝不覆盖 |
| HEAD_MISSING（HEAD 无此文件） | 18 | 全历史核查后全部判"可捞回候选"，本次只登记 |

## 二、18 件 HEAD_MISSING＝可捞回清单（登记待裁，本次未落盘）

全历史判定：18 件 `git log --all -- <path>` 均 0 commits＝从未入过 git 历史，且袋字节完整＝真缺口候选。因件数 18>5 且含 1 件 scripts/ 件，不满足自动捞回门槛（≤5 且全在 docs/tests），按纪律全部登记列 Owner/总筹裁；字节均在 `.runtime/commit_queue/blobs/<sha256>` 可随取随落。

| # | 路径 | 字节 | 袋 blob sha256 |
|---|---|---|---|
| 1 | tests/governance/data_supply/test_no_cache_and_cli_rc.py | 4016 | f0df0ceb602dc7b3fc65f018cf5a1d93cb8ad48186d9dc96bd7878919eb89094 |
| 2 | tests/governance/data_supply/test_supply_conservation.py | 3871 | e3aac2bba4072f706e0e6aabe56ed921fc19eb6a3d97d7eef19660b0236d11b2 |
| 3 | tests/governance/test_ch_probe_json_serialization_canary.py | 2997 | 95cb59e3978d02c456fdb4d0cc8237acf173f26593156c0d8b6b7c388fda2439 |
| 4 | tests/governance/test_dead_letter_eviction_canary.py | 6593 | 319e7ad5aa210e583df12cd711778867d2b34d241902adb98e11e5718d9f81ca |
| 5 | tests/governance/test_dead_letter_ownership_canary.py | 6465 | 11376a99d8c81dcfbc82ebea4f8a61fa1a326f1411ebf383cbea33947e466c57 |
| 6 | tests/governance/test_delivery_card_canary.py | 4514 | cb267eb4b504741057da788e11f1b8bd87e56ca6c2d6845e3544900a4d88bdf7 |
| 7 | tests/governance/test_enforcement_surface_reconcile_canary.py | 8631 | e93869078483dc88241dea38b04fc7992efd52e3c34588bb8e58a483b9b664b6 |
| 8 | tests/governance/test_enqueue_preflight_bypass_canary.py | 5899 | 78f638f718da0e52babfbe673bc2f80ca751602e2d1c0fab325a59cab47ab330 |
| 9 | tests/governance/test_registry_derivation_canary.py | 12276 | ae6fc085e0527c1ef59604bbc2575a02d758b5f943582f56d148b7fc8a0d2336 |
| 10 | tests/governance/test_wave1a_query_shape_ruler.py | 4639 | 4d3db9e187b899a15529ebb2ca8a9ab896a1f611f81003acbc6cf7111db712b8 |
| 11 | tests/governance/test_wave1a_strict_read_canary.py | 6728 | eef4fcde8fb93c58e1c24a2443f4814de70c451cb6a3bcf54f7d55df449dcc84 |
| 12 | tests/infrastructure/test_process_reaper_identity_recheck.py | 7119 | 86f98d5b66ad0ac2a744dfe4d129d3f4f9d9308e64d15248ac610132022a1d3f |
| 13 | docs/_working/map_build/fig14_construction/00_skeleton.md | 54459 | 7fdf45461ecc8eed23d788f01c1c394ab006c876020d6094e548a0038ef2eea6 |
| 14 | docs/_working/map_build/fig14_construction/01_冷启动与设计段.md | 45596 | 96180ae5b4ea0fb9acf50859274c8e0ebeafddbc3051e801facea940a01f0800 |
| 15 | docs/_working/total_command_closeout/wave7/landing_surface_reds_20260927.md | 4241 | 97dcf68f3966915ad4badeb078895db6e894c7b557e90bc8948009b4be810267 |
| 16 | tests/governance/d5_architecture/test_strategy_card_lifecycle_map_adversarial.py | 33854 | 3daa7c5be0ca6ff5076d224a00abfefdb66a981f05f4880c03497240594bb5d1 |
| 17 | tests/governance/scripts_governance/test_detect_git_dangerous_selfdoc.py | 5115 | 1f1c578c1c23f5c7b50f306da3e43aa15f7aff3d18359684728fafefec5593cb |
| 18 | scripts/governance/d5_architecture/validators/validate_strategy_card_lifecycle_map.py | 71254 | a3115a818e8a2f10ded825507097be8648e86bc1d33ddaa746a18e5501ddd195 |

- 低风险区（docs/tests）＝17 件；**#18 在 scripts/**（生产治理脚本，71KB）＝按铁律只登记不动。
- 捞回操作配方（Owner 点头后任一会话可执行）：逐件从 blobs/ 拷出→重跑本报告三分态复核（防窗口期变化）→token 登记（.py 走 CREATE-GUARD 常规通道）→正门 git_commit.py 分域入袋；#18 需先确认 d5 注册面与其伴生测试 #16 同批。

## 三、22 件 HEAD_NEWER（跳过清单，他会话已以更新版本落地）

scripts/ch/archiver.py、tests/scripts/test_ch_archiver.py、scripts/governance/d8_doc_sync/algo_flow_reverse_orphan_reconciler.py、scripts/deadman_switch.ps1、tests/scripts/test_generate_resource_profile_registry.py、scripts/backtest/f06_e4_wfa_exam.py、src/zephyr/backtest/core/n_trial_ledger.py、tests/backtest/test_f06_e4_wfa_exam.py、tests/backtest/test_n_trial_ledger.py、src/zephyr/ex_core/qmt_trading_session.py、src/zephyr/frontend/dashboard/app_panel.py、tests/ex_core/test_qmt_trading_session.py、scripts/construction/qmt_bridge_regression_smoke.py、scripts/construction/demo_e2e_pipeline.py、src/zephyr/ai_layer/redline/negative_list_gates.py、scripts/governance/d6_security/detect_git_dangerous.py、src/zephyr/gov_enforcement/commit_gates/_diff_helpers.py、src/zephyr/gov_enforcement/commit_gates/arch_reference_gate.py、src/zephyr/gov_enforcement/commit_gates/_reference_helpers.py、tests/governance/commit_gates/test_arch_reference_gate.py、docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml、AGENTS.md。
其中 8 件 HEAD 版本相对袋基底 1dd6c70c74e9 又有推进（archiver 族/deadman/n_trial_ledger/negative_list_gates/architecture_issue_registry/AGENTS.md）＝与死因"同路径被推进"吻合，跳过判定正确。

## 四、R-1 蒸发件捞回（wiring_gap_inventory_20260927.md）

- **残骸找到**：本体 blob＝`.runtime/commit_queue/blobs/75549c3400f807b739a85ff3c11d175f5ea2e18d6f4d4de189d2ac6b4d967785`（17001B/145 行，sha256 自洽，frontmatter asset_id 自指精准命中）；队列侧 `dead_archive_final/q-20260927-st-chief7w-20260927-0010.json` 仅 message 引用（其 36 件清单未含此件，袋未随件即蒸发主因）。
- **时效判定（2026-09-29 复测）＝仍是活账**：①总册四态 built81/partial30/design5/missing6 与本文 §1.4 完全一致；②TDM `module_ref: null` 实测 37（本文记 38，仅闭合 1）；③HEAD 现存 ≥9 处引用原路径悬空（capability_canonical_file_registry.yaml、本战役 workorders 三件、fullconnect_campaign HANDOFF/90_rulings、night_sweep/00_skeleton_nightsweep.md 等）。
- **处置**：字节原样捞回＋换绑 asset_id＋头部加捞回/时效注记，落盘 `docs/_working/final_delivery_campaign/recovered_wiring_gap_inventory_20260927.md`，随本报告同袋提交。
