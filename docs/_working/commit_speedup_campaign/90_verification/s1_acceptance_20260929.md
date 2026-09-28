---
created: 2026-09-29
ttl: task_bound
---

# S1 验收实测台账（2026-09-29 夜战，st-nightsweep-sw8-20260929 代 SW3 执行）

- 卡源: SW3/A08（夜战总 Sweep Wave1）；执行会话: st-nightsweep-sw8-20260929
- 判据: 门禁改指不可变提交树视图（S1）发布前绊线=「门禁判定随 index 规模漂移」——
  验收=重放实测 own_tree（改指后口径）与 shared_index_sim（共享暂存区规模复刻口径）
  双口径逐台 verdict 全等，且对照既有字节保真基线 selfcheck100 无回归。

## 一、实测执行

- 命令: `python scripts/governance/replay_gate_verdicts.py --since 30 --all --out-dir .runtime/tmp/st-nightsweep-sw8-20260929/s1_replay_out`
- 实测窗口: 2026-09-29 06:27 → 07:12（elapsed 2860.8s，后台单进程，不占提交链）
- 规模: commits 30/30（非 merge）× 名册全量 100 台（gate_load_failures=[]）× 2 口径 = **6000 verdict 行**
- 外来噪声: real 模式，真实共享 index 当日 612 文件（复刻生产规模敏感性）

## 二、验收结论（全数实测，非抽测）

| 判据 | 结果 | 判定 |
|---|---|---|
| verdict 逐台双口径全等 | **100/100 台 verdict_diverged=0**（verdict_pairs 全为 pass->pass/skip->skip 等同态对） | ✅ 清零 |
| 命中数逐台一致 | **100/100 台 hits_diverged=0** | ✅ |
| detail 哈希一致 | **100/100 台 detail_diverged=0** | ✅ |
| 随 index 规模漂移 | **100/100 台 verdict_drifts_with_index_size=False** | ✅ 绊线不存在 |
| 门禁装载 | 100 台全载，0 装载失败 | ✅ |

## 三、性能副产物（own_tree 收益实测）

- 逐台均耗时: own_tree 均值 109.34ms/台 vs shared_index 均值 778.53ms/台
- 30 笔全册合计: own 10,934ms vs shared 77,853ms → **7.1x**（读面收窄收益与 D27 L1 hoisting 5.6x 同向互证）

## 四、对照基线（selfcheck100，本日实测非陈数）

- `.runtime/tmp/csx_replay_selfcheck100/selfcheck.json`: commits_checked=100、files_checked=1522、
  **byte_mismatch_total=0**、worktree_reads_from_view=0 —— 重放机制字节保真基线成立，
  本轮 verdict 验收建立在可信重放之上。

## 五、产物与可复核性

- `<out-dir>/verdicts.jsonl` 6000 行（每台每笔每口径一行，含 detail_sha 可逐条复核）
- `<out-dir>/verdict_divergence.yaml`（生成器产出，逐台聚合+样例区=0）
- `<out-dir>/run_summary.json`（运行元数据：gates_loaded=100/commits_processed=30/sandbox_writes=5498）
- 外来 staged 告警面：重放过程 own 化作用域按设计对外来 staged 文件 warn+审计不阻断
  （157/632 文件级 WARN 属 #ARCH-310 R2 own-diff 设计语义，非缺陷）

## 六、判定

**S1 验收 PASS**：门禁判定不随 index 规模漂移（100/100 台零漂移），改指不可变提交树视图
的发布前置绊线实测清零；附 7.1x 读面收益实测。verdict 证据=6000 行全量落盘，非"全绿"式虚报。
