---
ttl: task_bound
working_doc_type: fig11_gap_verification
map_nodes: D11-G01/D11-G02
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-G01,#D11-G02
---

# 图11 骨架外 2 个 gap 件核实专档（D11-G01/G02）

任务令：骨架缺口「图11 2 个骨架外 gap 件」须核实。结论先行：**G01 成立（维持）；G02 实质已修复（代码侧收口），残余=图注未回写**。

## D11-G01 退出码死分支（码 4 与 STASH_CONFLICT 支无生产者）——维持成立

- 判据：_COMMIT_RESULT_MAP 有专码条目 ∧ 全仓 `CommitStatus.X` 生产者构造计数=0。
- 复核证据（2026-10-15 实扫）：
  - `scripts/git_commit.py:149` STASH_CONFLICT→2、`:162` SSOT_VIOLATION→4 两条映射在表（实读）。
  - `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:592` `STASH_CONFLICT = "..."  # 阶段3 已弃用，保留向后兼容`（枚举自认弃用）；`:631-632` stash_ref/stash_kept 同注。
  - 全仓 grep `CommitStatus.SSOT_VIOLATION`（src/+scripts/）：仅命中枚举定义+分发表+生成器自引（scripts/governance/d5_architecture/generators/generate_dev_delivery_map.py:807 字符串）——**零生产者**。
  - 全仓 grep `CommitStatus.STASH_CONFLICT`：**唯一消费支=src/zephyr/governance/persistence/task_repo.py:2528**（elif 分派），零生产者。
- 三态：fail（按 gap 定义即缺口成立）。
- 建议：内收判据 w5_1「零触发零消费→退役」适用但 STASH_CONFLICT 尚有孤儿消费支——处置序列=先摘 task_repo.py:2528 分派支→再退役两码+表行；处置权在总包（本图不删表不改码，图注已声明）。

## D11-G02 precommit 通道回滚旗恒失效（代码键未注册 × default=True）——实质已修复

- 图载旧况：代码读 `gate_precommit_run_enabled`（is_enabled default=True）而 flags.yaml 在册键=`gate_precommit_run` ⇒ 未注册键走 default ⇒ 通道恒 ON、Owner「flag OFF 回滚」不可兑现，回滚面=幽灵引用。
- 复核证据（2026-10-15 实扫）：
  - 修复 commit：`b192fa39126`（[ND-E9·st-nightsweep2-nd-20260930][Owner 2026-09-30 E 组批文·SW15 R-5 配方]，git log -S 实查）——「旗标名对齐：gateway _PRECOMMIT_RUN_FLAG 'gate_precommit_run_enabled'→'gate_precommit_run'（对齐 flags.yaml 在册键）……旧值指向不存在键=is_enabled 恒 default=True=回滚通道坏死，对齐后复活；同批重生成图11（D11-G02 对账尺翻绿）」。
  - 现码：`git_commit_gateway.py:386` `_PRECOMMIT_RUN_FLAG = "gate_precommit_run"`（在册键）；`:553` `_precommit_run_enabled()`（flag 读取异常回退 OFF=#341 前现状，fail-safe）；`:3900` 通道首检消费。旧键 `gate_precommit_run_enabled` 全仓 grep 零引用。
  - 册面：`config/flags.yaml:127` gate_precommit_run enabled=true production（描述含「回滚通道=flag OFF」——现已可兑现）。
  - 图机生面已翻绿：map machine_facts.precommit_flag_pair = {code_key: gate_precommit_run, registered: true, in_roster: true, default_on: true}。
- 三态：代码侧 pass（已收口）；账务侧 fail——map（今日 18:22 重生成）仍保留 G02 gap 节点+旧 note 散文（述 :358 幽灵键），与自身 machine_facts 自相矛盾（文档纪律 §4.4：文档矛盾=事故）。
- 建议：G02 节点退役回写——总包按「六图终局卷 §4 图11 判据②」流程回写骨架 §1/§6，把 G02 从 gap 节点清出（G01 保留）；随 D05（cascade_stale 已接通）同批。

## 共性发现（三件同构：代码先修、图注未跟）

| 件 | 图判 | 代码现实 | 性质 |
|---|---|---|---|
| G02 | unwired_slot_hollow/ghost_ref | 已修复（b192fa39126，09-30） | 账务滞后 |
| D05 | unwired_slot_hollow | QUEUE-04 已接通（base_blob 真填充+landing :4271 接线） | 账务滞后 |
| S07 | partial（如实） | partial 维持（_PRE_MERGE_SKIP_ALL_COMMIT_GATES=True :391 实读） | 判定仍准 |

图11 真正需要治理动作的缺口收敛为：S05 晋升面缺失、S07 merge 门预演短路、C02 递送无审计 sink、G01 死码退役——四件皆有明确收口路径，见各环节子文档 §4。
