---
ttl: task_bound
---
# L3 三件悬空 .py 与 GOMAP 图有物无 · 挖矿簿

> 环节=E07 ｜ 子环节=4（三件四态 / 幻影已入 HEAD / 生成侧根因 / 同族第三例）｜ 状态=封矿·已施工·已红绿双证

## 子环节 1｜三件四态实测（本包亲验，`git log --all -- <path>` 三件皆 0 提交）

| 文件 | HEAD | index | 盘 | 内容寻址袋 | 属主 | 定性 |
|---|---|---|---|---|---|---|
| `scripts/governance/check_meta_question_audit_reconcile.py` | 无 | 无（`??`） | 07:10 | 命中 | `st-metaq-20260923-0022`(pending) | 在途，**非 absorbed** |
| `scripts/sector_line/build_gpu_input_pack.py` | 无 | 无（整目录 `??`） | 09:46 | 命中 | `st-pipeline-final-20260924-0029`(pending) | 在途，**非 absorbed** |
| `src/zephyr/intelligence/budget_analyzer.py` | 无 | `A `（已 stage 未提交） | 08:01 | 命中 | `st-ailayer-final-20260924-0003`(dead→该会话 14:39 又起一笔直提含它) | 在途+死信+staged，三态最险 |

⇒ Owner 令的"内容已在他批落地=标 absorbed"分支**三件皆不成立**（无一进过任何 ref）；
"真悬空=落地或登记"分支适用，但**代投他包代码=EVAP-02 搭便车**（本包 §5 纪律 + 案卷先例）⇒
裁定=**不代投代码，改为治生成侧 + 归零图面 + 登记三件归属**（下表已登记 qid/属主/时间）。

件级成熟度复核（为何不能代投）：①`[MATURITY] new` 且其依赖 `src/zephyr/governance/meta_question/registry.py` 同样未跟踪，
单独落地=HEAD 里 import 不存在的模块；②`[MATURITY] prototype`，依赖 `scripts/sector_line/freeze_baseline.py` 亦未跟踪，HEAD 零引用；
③最完整，且 `tests/intelligence/test_budget_analyzer.py` **已被跟踪而模块未跟踪**（HEAD 现带一个测不存在模块的测试）——仍属 `st-ailayer-final` 的批。

## 子环节 2｜污染**已提交进 HEAD**（案卷低估的一面）

真源=`config/governance_operations_map.yaml`（非 docs/、非 architecture_model/）：
`git show HEAD:该册` 含三件各 1 处（行号 1095/1389/1757 区段），引入笔=`fa0ca806fb`（两件 scripts/）
+ `8135b0675d`/`5f4136315e`（budget_analyzer）。⇒ 不是"盘上脏一下"，是**已入库的假条目**。

分母实测（同口径集合差，纯内存零写入）：`rglob`=427 / `git ls-files`(index)=424 / `git ls-tree HEAD`=424。
⇒ 案卷给的免门位路径"收窄到 git 跟踪集"若按 **index** 口径会**错删 `t0_gpu_condition_pack.py` 且留下 `budget_analyzer.py`**；
**唯一正确口径=HEAD 树**（差集恰为幻影 3）。本包按 HEAD 落地。

## 子环节 3｜生成侧根因与红绿双证

- 代码位：`scripts/governance/generate_governance_map.py:143` `for p in base.rglob("*.py")`（`SCAN_ROOTS=("src/zephyr","scripts")`）。
- 既有校验为何看不见：`align_all._gomap_diff_families`（:167-179）两侧都取工作树 ⇒ "磁盘已消失"永远不等于"不在 HEAD"，
  **HEAD 面幻影结构性不可判**（这就是案卷"漏挂 1→0/悬空 0→3"读数能反复横跳的原因）。
- 治本：入选枚举改 HEAD 提交树；口径真源收敛到**共享件** `zephyr.governance.audit._git_helpers.git_ls_tree_paths`
  （放这里=该模块存在的唯一目的就是消除各 reconciler/generator 自写 git helper 的 FUNCTION-DUP；
  函数体 fail-open 返 None，**策略留给调用方**：生成器一律 raise，因静默降级=把病灶原样放回且只在"git 恰好不可用"那次发作）。
- 红证（用**生产函数** `_check_gomap_alignment`，非另造判据）：
  HEAD 版图 + HEAD 基 scan() ⇒ `硬=(3,3)`，三条 FAIL 逐字为
  `机生层幽灵 L2_resource: scripts/sector_line/build_gpu_input_pack.py`／`…budget_analyzer.py`／`…check_meta_question_audit_reconcile.py`；
  本包重生成版 ⇒ `硬=(0,3)`。修复**前**同一函数对 HEAD 版图报 `硬=0`＝案卷 BLIND 面的反向实证（尺非恒红亦非恒绿）。
- 文案错位一并治（本仓有判例：判据与文案错位会误导诊断方向）：`机生层幽灵 …（磁盘已消失）` →
  `…（不在 HEAD 提交树，yaml 却带着——多为脏工作区重跑烤进的在途件）`；`机生层漂移` 同步改准。

## 子环节 4｜同族第三例（本包新发现，案卷未载）

`scripts/governance/generators/generate_script_manifest.py:219` 同样 `SCRIPTS_DIR.rglob("*.py")`，
且 **HEAD 版清单已带 4 条 NOT_IN_HEAD 幻影**：`apply_meta_question_ddl.py`、`check_meta_question_audit_reconcile.py`、
`check_meta_question_batch.py`、`check_meta_question_status_band.py`。`total_scripts 452 → 448`、`governance 64 → 60`。
定性=与 GOMAP 同一病灶的第二实例（脏工作区重跑派生件）。
处置=同口共享件收窄 + `--auto-fix` 重生成；逐字段差分实证**零真实资产净损**（消失 4 条全为 NOT_IN_HEAD 幻影，字段级净损=0）。

红证：在 worktree 造一个未跟踪、带 `__manifest__` 块的 `scripts/governance/zz_inflight_probe.py` →
重跑生成器 → `grep -c zz_inflight_probe script_manifest.yaml` = **0**（修复前必为 1），且生成器幂等（跳写）。

## 判据（E11 复跑）

1. `python -c "align step9"` 或 `align_all.py`：GOMAP `硬=0`；
2. `python scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py --check` ⇒ `GATE-21 PASS`（实测 worktree 已 PASS，rc=0）；
3. 三件属主袋任一落地后，重跑 `generate_governance_map.py` 应把它们**自然挂上**（HEAD 基已含=不再是幻影）——此为本包留给属主的免门位归零路径。
