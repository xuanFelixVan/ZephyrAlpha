---
ttl: task_bound
rule_form: data
verifiability: manual
title: S18 Flash 夜间施工包×3（机读判据完备版，v6-3）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-17
---

# S18 Flash 施工包（Owner 签 S18-R1~R4 后夜间执行；判据写死标准="写不出来=没想清楚"）

> 授权边界：本包只在 S18-R3（裁定#320）签署后启动 F2/F3；F1 任何时候可做。止痛件禁止混入。

## F1 衍生提交并入原子化（S18-R2 / 根因表 R-01）

- **改动文件**：`git_commit_gateway.py`（`_post_flush_rules_integrity_re_register` 改同 commit 追加而非独立笔）+ `scripts/governance/meta/validate_rules_integrity.py`（内容哈希未变短路）+ reconciler 派生写入点（`_commit_auto` 双路径已在 G1 挂台账，本包把它升级成并入）。
- **机读判据**：①无受保护文件（golden-hash 清单）变更的 commit 后 24h，`chore(integrity) post-flush` 独立 commit 数=0；②受保护文件变更而 DB 未更新 → `validate_rules_integrity.py --check` 必须真报 TAMPERED（反例样本：手改 rules_integrity_db.json 一行 hash → 必红）；③队列死信死因中 rules_integrity 漂移占比 24h <2%（基线 13.1%）。
- **验收命令**：`pytest tests/governance/ -k "integrity or reconciler"` 全绿 + 真仓一笔试点 commit 后 `git log -1` 无衍生尾笔。
- **预期节省**：衍生税 11%→~5%（≈34 笔/24h 消除）；队列死信 -13pp。
- **回滚**：revert 单笔（派生物随主 commit 同回滚）。

## F2 serializer k=4 分区通道（S18-R3③，前置未过不开工）

- **前置（机读，缺一不开工）**：lease 续租机制落地且 `tests/governance/test_commit_queue_landing.py` 新增"同域同文件双通道并发"压测绿；跨域热文件清单（注册表/ROOR/AGENTS.md/standards.yaml）强制走单一热通道的闸在案；夜间并发峰值连续 7 天>40 车道。
- **改动文件**：`scripts/commit_queue.py`（drain 按域取队）+`commit_queue_landing.py`（k 通道 worktree 池）+域映射配置。
- **机读判据**：k=4 下小时落地峰值 ≥76（4×24×0.8）；同域冲突率不升（对照单通道基线）；lease 双写者窗口=0（审计：任一时间点同域活跃 lease≤1）。
- **验收**：`python .runtime/tmp/rb2/harness.py --workers 20 --mode enqueue --scenario stress`（P2 harness，2026-09-18 自 `.runtime/tmp/closeout_residue_20260918/rb2_harness_preserved.py` 重建至 `.runtime/tmp/rb2/harness.py`，39193B，`py_compile` 通过）+既有队列测试全绿。**通道维说明**：本 harness 无 `--channels` 参（CLI 实参=scenario/workers/minutes/mode/kill-frac/kill-states/run-id/sandbox/results/phase）；k=4 分区通道是 F2 主体改动（`commit_queue.py` drain 按域取队 + landing k 通道 worktree 池 + 域映射配置），须 S18-R3 签署后方施工，届时通道数经域映射配置注入、压测在 k 通道 worktree 池上跑——原悬空行的 `--channels 4` 是 F2 落地后才存在的验收维，前置阶段以 `--workers 20 --mode enqueue` 验单写者通道并发安全（同域同文件双通道压测另见 `tests/governance/test_commit_queue_landing.py`）。
- **预期**：吞吐 24→82/h（3.4×）。**回滚**：通道数配置回 1（单开关）。

## F3 头部 O(仓库) 门禁 diff 化（S18-R3②/S18-R4 约束内）

- **对象白名单（只许这 6 件）**：CREATE-GUARD（P99 94s）/CAPABILITY-OVERLAP/ERRCODE-CONSISTENCY/FUNCTION-DUP/ALGO-FLOW-LINK/ALGO-NOTE-SYNC。白名单外一件不许动。
- **改法**：复用 604f414846 口径（git index+HEAD 基线差分+全绿短路）；语义判据零改动（输入同一 diff 应得同一判定——逐件做差分等值回归）。
- **机读判据**：①6 件 P50 合计 <10s（基线 46.4s 链的头部占比）；②差分等值：对近 100 笔历史提交重放，diff 化判定与全量扫描判定逐笔一致率 100%（不一致=该件回滚）；③own-scope 外来 staged 审计告警率不降为 0。
- **验收**：`pytest tests/governance/commit_gates/ tests/git/` 全绿+重放报告落盘。
- **预期**：链墙钟 -30~40%（1.4×/通道）。**回滚**：逐件 feature flag 回退。

## F4 GATE-REGENERATE 生成器并发化（根因表 R-08）

- **改动**：`reconciliation_registry.py:8097` 串联 15 生成器→按依赖拓扑分组并发（无依赖组内并发）；mtime 先行短路（输入未变不跑）。
- **机读判据**：reconcile 总墙钟 <180s（基线超时）；生成器输出与串行版逐字节一致（抽样 5 件 diff）；零工程裁定（architecture_issue_registry:20916）语义不变。
- **验收**：`python scripts/governance/reconcile_generators.py` 全量计时前后对照。
- **回滚**：并发开关回 off。
