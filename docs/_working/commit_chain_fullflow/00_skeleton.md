---
created: 2026-09-30
ttl: task_bound
title: 提交链路全流通作战·环节骨架总册
session: st-gate-rationalize-20260929
---

# 提交链路全流通作战·环节骨架总册（00）

> 总包会话 st-gate-rationalize-20260929。Owner 令（2026-09-30 晨）：挖矿→封矿→施工→循环检查×2零→红蓝对抗→全绿交付，线内先挖后干、线间并行流水，六向台账+自审闸三态为挖干判据。
> 前序真源：`docs/_working/gate_survival_adjudication.md`（183门禁+69hook+22组件逐台裁定+§11执行留痕）。
> 版本注：本册 07:25 并发落地蒸发事件中随 e01/e03/e05/e06 一同被清，07:4x 由总包重写（六幸存簿因及时 git add 入 index 幸免）——多会话夜战期 unstaged 文件无生存权，产物即写即 add 是铁律。

## 一、环节骨架（10 环节，一笔提交的全程）

| # | 环节 | 子文档 | 一句话 |
|---|---|---|---|
| E1 | claim/锁/会话层 | e01_claim_locks.md | lock_files + claim_snapshots + SessionRegistry + 全局提交锁 |
| E2 | gateway 锁外/锁内前置 | e02_gateway_preflight.md | pg_probe/横幅/worktree 检测/tracked 快照/itA 清扫 |
| E3 | L2 门禁链（in-process） | e03_l2_gates.md | 统一册178条、名册104条、九簇重叠、逐台裁定指针 |
| E4 | pre-commit hook 通道 | e04_precommit_channel.md | 64 hook、SKIP 8 台、Phase-A/B、own-scope 临时索引 |
| E5 | git 核心操作 | e05_git_core.md | add/pathspec/rename 检测/commit/孤魂验证 |
| E6 | post-commit 链 | e06_postcommit.md | lfs/YAML regen/guard/（Qoder 已封存） |
| E7 | 队列序列化+落地 | e07_queue_landing.md | serializer worktree、八相位落地、converge、integrity 基线(head已翻)、stats_lock、advance_dev |
| E8 | reconciler/auto-commit 扇出 | e08_reconciler.md | ~40 reconciler、衍生再生、批 auto-commit 重入锁 |
| E9 | 遥测/旗标/缓存面 | e09_telemetry_flags.md | jsonl 18册、flags 19键全景、gate_cache_preflight、S1 视图 |
| E10 | 观测与验证面 | e10_observability.md | 三本耗时账、堵点横幅、commit_perf_report、红蓝套件 |

## 二、挖干判据（六向台账+自审闸）

六向=上游触发源/下游消费方/输入面/输出面/真源锚/耗时账。自审闸三态=【挖干】（六向齐+逐件有锚）/【未干】（列明缺口）/【不可挖】（他会话占用或属其他 lane，登记移交）。

## 三、施工序与执行留痕（截至 07:50）

- A 段（已挖干先行）：A1 GIT-CALL-BUDGET **证据改判不施工**（S1 后 p50 828→157ms，原处方"改读 _stat_ms"系误诊，撤销）；A2/A3/A4（并扫/parse共享）**验证已被提速队 S1 基建解决**（immutable_tree=ON，_diff_helpers 四入口有树读树，gate_survival_adjudication 处方被更底层方案实现=交叉验证收益）；A5 gate-test 增量化 **落地 7a4a7c9f**（全树3967收集→staged收集，双分支功能验证）；A6 regen_scope→main_only **翻转落地**+慢尾死id清出（死袋 q-0001，内容经核实已在 HEAD）。
- B 段：B1 pg_probe 新鲜度短路 + B5 flags 审计 32MB 轮转（q-0002 死袋→直提 q-0004）；B2 横幅尾读 256KB + B3 锁盲轮询指数退避 + 预检 TTL 直连脱钩 **落地 57ba32b2**；B4 tracked 快照 4→1 **缓修登记**（硬阻断安全门指纹语义，深夜不动）；CREATE-GUARD p90 44.8s 尾 **登记日班专班**（热册并发写，不宜夜间动）。
- C 段（等待解锁）：生成器登记债（gate_registry.yaml/generate_gate_registry.py 他队 MM 中）、D1 stats_lock（landing.py MM 中）、hook 通道出锁（需与 Phase-A/B 重设计一并）、SessionRegistry 增量写（整表重写竞态已被本夜三连拒实证，日班专项）。
- D 段：循环检查×2零 → 红蓝对抗 → 清理 → 终报。

## 四、施工红线（Owner 晨令）

1. 不抹掉/不回退任何他会话成果与临时文件；同文件撞车=登记让位或排后。
2. 他队已完成的任务=交叉验证巩固，不重做。
3. 内收原则：新功能须声明替代/合并的旧条目，净零。
4. 无法裁定→登记+跳过；堵塞→停。最终零遗留零待裁（能自主裁的全部裁掉）。
5. **产物即写即 add**（07:25 蒸发事件学费：unstaged=无生存权）。
