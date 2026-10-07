---
ttl: task_bound
completes_when: Owner 复核销账
card: C346
session: st-mastertc-l2
date: 2026-10-07
---

# C346 CAPABILITY-OVERLAP 禁用期回溯核查案卷（只读核查）

## 一、背景与窗口界定

- CAPABILITY-OVERLAP 门禁曾处 enabled: false；**2026-09-30 由 Owner 批复翻闸**
  （裁定#431 第①项，commit `3dda7e481a2`：原禁用理由"echo-guard 21 对 sync 不到位"
  已被 `98ce6370c5` 治愈）。统一册 gate_registry 无 enabled 字段、status=active
  （L821-829 实证）。
- 回溯窗口=**2026-09-20 起**（卡面指令口径），覆盖"禁用尾段（09-20→09-30）+
  复闸后（09-30→今）"两段——若禁用期有漏判重复入库，应在该窗新增 .py 中现形。

## 二、方法（机械三检，全部可复算）

1. 取样框：`git log --since=2026-09-20 --diff-filter=A --name-only -- '*.py'`
   去重后 **417 个非 tests/ 新建 .py**（tests/ 为 CREATE-GUARD 豁免域，不入框）；
2. 等距抽样 30 个（步长≈13.9，首尾覆盖全窗；清单见 §三，原始读数
   `.runtime/tmp/c346_sample.json`）；
3. 逐个三检（2026-10-07 HEAD=`600abe9991` 时点）：
   - **token 面**：路径是否在 `capability_canonical_file_registry.yaml`（13853 条）；
   - **同名碰撞面**：文件 stem 在 src/+scripts/ 全树是否多文件同名
     （`__init__.py` 包标记 stem 除外）；
   - **存活面**：HEAD 是否仍存在（排除已迁走样本的假阴性）。
   补充框级扫描：417 全量过 `(_v[2-9]|_new|_backup|_copy|_old|_dup|_2).py$`
   疑重复命名式扫描。

## 三、结论

**未发现漏判重复（0/30 嫌疑，0 框级命中）**——禁用期回溯核查通过，无补闸动作：

| 检查面 | 读数 |
|---|---|
| 30 样本 token 登记 | **30/30 全登记**（含禁用尾段 09-20→09-30 内入仓者） |
| 30 样本 stem 碰撞 | **0**（唯一 572 命中=`__init__.py` 包标记，非重复信号） |
| 30 样本 HEAD 存活 | 30/30（无迁走失联样本） |
| 417 全量疑重复命名式 | 1 命中=`scripts/backup/library_ledger_backup.py`，**判合法**：
  MOD-INF-043 灾备域（图书馆 PG 账本双链备份，12 号令任务 2），token 在册，非克隆 |
| acknowledged 白名单 | 0 样本需要（无命中无豁免面） |

**解释（为何禁用期也干净）**：CREATE-GUARD 六/八道链（含查功能关键词两档化、
#456 判重腿）与 CloneGuard 在 CAPABILITY-OVERLAP 停用期间**独立在岗**
（三台门禁判据不同层：token 登记=CREATE-GUARD、extract 级克隆=CloneGuard、
关键词重叠=CAPABILITY-OVERLAP）——单台停用不形成判重真空，与裁定#431
"原禁用理由已被治愈"的翻闸前提互证。

## 四、样本表（30，等距抽样）

| # | 路径 | token | 碰撞 | HEAD |
|---|---|---|---|---|
| 1 | schemas/categories/ai_cost_daily.py | ✓ | 0 | ✓ |
| 2 | scripts/ai_layer/apply_ai_heritage_ddl.py | ✓ | 0 | ✓ |
| 3 | scripts/audit/t0_conditional_e4_v3_exam.py | ✓ | 0 | ✓ |
| 4 | scripts/backtest/fexam/ch_data.py | ✓ | 0 | ✓ |
| 5 | scripts/backtest/league_registry.py | ✓ | 0 | ✓ |
| 6 | scripts/ch/apply_sim_daily_report_ddl.py | ✓ | 0 | ✓ |
| 7 | scripts/governance/check_trd_a20_a21_dual_gates.py | ✓ | 0 | ✓ |
| 8 | scripts/governance/d5_architecture/generators/generate_panorama_master_map.py | ✓ | 0 | ✓ |
| 9 | scripts/governance/data_supply/false_green_crosscheck.py | ✓ | 0 | ✓ |
| 10 | scripts/governance/generators/check_library_tri_consistency.py | ✓ | 0 | ✓ |
| 11 | scripts/governance/meta_question/reexam/a06/stats_core.py | ✓ | 0 | ✓ |
| 12 | scripts/governance/meta_question/wo006/generate_micro_chain_retirement_nominations.py | ✓ | 0 | ✓ |
| 13 | scripts/governance/meta_question/wo_a2legs/_probe.py | ✓ | 0 | ✓ |
| 14 | scripts/governance/meta_question/wo_b2_e1c/apply_e1c_ledgers.py | ✓ | 0 | ✓ |
| 15 | scripts/governance/register_asset.py | ✓ | 0 | ✓ |
| 16 | scripts/governance/wave1a/verified_promotion_check.py | ✓ | 0 | ✓ |
| 17 | src/zephyr/ai_layer/comparator/__init__.py | ✓ | 包标记 | ✓ |
| 18 | src/zephyr/ai_layer/heritage/heritage_events.py | ✓ | 0 | ✓ |
| 19 | src/zephyr/ai_layer/redline/freedom_weekly_report.py | ✓ | 0 | ✓ |
| 20 | src/zephyr/ai_layer/switch_engine/__init__.py | ✓ | 包标记 | ✓ |
| 21 | src/zephyr/alt_data/emotion_index_replay.py | ✓ | 0 | ✓ |
| 22 | src/zephyr/data/cleaning_engines.py | ✓ | 0 | ✓ |
| 23 | src/zephyr/data/quarantine_manifest.py | ✓ | 0 | ✓ |
| 24 | src/zephyr/gov_enforcement/commit_gates/_capability_registry_io.py | ✓ | 0 | ✓ |
| 25 | src/zephyr/gov_enforcement/commit_gates/takeover_pending_gate.py | ✓ | 0 | ✓ |
| 26 | src/zephyr/governance/meta_question/exam_loop/arbitration.py | ✓ | 0 | ✓ |
| 27 | src/zephyr/governance/registry_ledger/ledger_identity.py | ✓ | 0 | ✓ |
| 28 | src/zephyr/intelligence/model_intel/intel_card.py | ✓ | 0 | ✓ |
| 29 | src/zephyr/library/collectors/mcp_collector.py | ✓ | 0 | ✓ |
| 30 | src/zephyr/plan_engine/daily_loop_master_switch.py | ✓ | 0 | ✓ |

## 五、局限与残余

- 本核查为机械面（token/同名/命名式）三检，非 AST 级 extract 克隆重扫——后者归
  CloneGuard 全量扫描（`scripts/clone_guard_audit.py` 通道），不在本卡只读范围；
- 抽样 30/417≈7.2%，等距覆盖禁用尾段与复闸后两段；若 Owner 需全量 417 复扫，
  处方=上表三检脚本化（`.runtime/tmp/c346_sample.json` 含全部判据读数，可一键扩量）。
