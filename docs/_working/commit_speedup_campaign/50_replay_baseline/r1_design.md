---
ttl: task_bound
---

# R1 · 重放基线基建设计与验收（包8/9 出厂判据仪器）

> 立档 2026-09-24 深夜 ｜ 会话 st-commitspeed-tbl-20260924 ｜ 三件代码已独立验收（§3）
> 用途：A4 阶梯 S1（不可变树收口）与 T8（门禁三簇合并）的出厂判据＝「重放 N 笔逐台 verdict 全等」的仪器。

## 1. 背景与目标

S1 一次改 72 台门的输入源，失败模式是静默假绿而非报错；T8 合并门禁簇的出厂判据要求
「重放最近 100→1000 笔判定逐笔全等（必须真跑）」。本基建提供判据级安全网：不改任何门禁
判据，只在 git 历史与真实门禁代码之上复现"当时门禁看到的世界"，并逐台比对 verdict。

## 2. 架构（三件代码＋内置比较器）

- `src/zephyr/gov_enforcement/commit_gates/_tree_view.py`＝CommitTreeView：只读，按不可变
  git 树复现门禁当前从共享暂存区读到的视图（added_lines/文件内容/命令映射表），内置
  **工作树直读探针**（view_worktree_reads 恒 0＝绊线，防门改造后退回读物理路径）。
- `scripts/governance/replay_gate_verdicts.py`＝重放驱动器：枚举最近 N 笔非 merge 提交，
  逐笔构造 base/head 两树视图＋噪声集（`--noise real`=当日真实 index），装载名册全量
  enabled 门逐台跑，产出逐台 verdict；`--selfcheck` 只做逐字节复现自检不跑门；
  `--max-commits`/`--max-seconds` 预算闸；`--out-dir` 落 verdict JSON。
- `tests/governance/test_gate_replay_harness.py`＝红证测试 8 例（scratch 仓＋real host 双面）。
- 比较器（驱动器内置）：verdict/hits 逐台比对，漂移台点名输出。

## 3. 验收记录（2026-09-24 深夜，统筹会话独立复验）

1. 测试 8/8 绿（3.79s）——含 never_reads_working_tree / write_sandbox 隔离 / comparator drift 探测。
2. `--selfcheck --since 5 --max-commits 3`：commits=3 files=8 **byte_mismatch=0、
   view_worktree_reads=0**（逐字节复现与绊线双绿）。
3. 实弹冒烟 `--since 3 --max-commits 2`（全 102 门）：408 verdict 行、165.8s/笔；产出首个
   真发现：**MUTABLE-CONST-WITHOUT-FINAL verdict 随 index 噪声规模漂移**＝共享暂存区病灶
   的直接实证（正是本役 S1 要治的靶）。

## 4. 包8/S1 出厂判据用法

- 合并/改指**前后各跑一次** `replay --since 100 --all`（配 --max-seconds 预算），逐台
  verdict 全等才可发布；达标后扩 1000 笔。diff 台名单即回滚面；禁改判据凑绿。
- 已知慢源：全仓扫描门 ~166s/笔 → 100 笔约 4.6h，须后台＋预算分片跑。

## 5. 边界与诚实清单

- 重放＝门禁函数级复现，不覆盖 landing 相位/合并器行为（那是 A2 八段装表的靶）。
- 15 台故意读全索引的门（A3 `shared_index_without_own_scope`）在 own-tree 化时**禁**用本
  仪器判"全等"——其语义本就含他人在途噪声，走 S3 分道校验（A4 阶梯 S1 风险段）。
- `--noise real` 取主区当日 index：不同时刻噪声集不同，跨日对比须固定噪声口径。
