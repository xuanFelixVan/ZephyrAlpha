---
ttl: task_bound
doc_type: mining_segment
campaign: mine_fullchain_20261015
segment_id: D14-15
figure: fig14 施工升级流（construction_workflow_map）
created: 2026-10-15
ssot: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-10-gitcommitgateway-落地 + 附录 D 锚块
---

# SD14-15 提交网关落地（policy Step 10）

## 1. 定义

Step 9 完整性确认后，本施工任务把改动控制权交给交付正门的交接段：走 GitCommitGateway 网关提交（正门 CLI=`scripts/git_commit.py`）+stash 生命周期检查+pre-commit 增量守门。提交方式优先级：worktree session_worktree_commit（首选）→GitCommitGateway（次选）→裸 git commit（禁止）。四链交汇点：图14 D14-15=图11 C 车道正门（两图同域衔接）。机制真源全归图11（政策自标"不重复，引用"），本段 role=handoff，verifiability 恒 manual（反洗白口径：禁借图11 auto 抬分）。handoff_to=D11-C01/C03/C04/C05/C07/C08/C09/C10/C11/C12/C13（11 条，本批全命中图11 骨架）。verified_scope=production（骨架 ✅）。

## 2. 六向台账

| 向 | 内容 | 路径证据 |
|---|---|---|
| 输入面 | 完整性确认（D14-14）；session sid+文件清单；失败重试带 `--adopt-prior-work` 语义 | `scripts/git_commit.py`（正门 CLI，在盘实证）；宪法 §2.3 |
| 输出面 | commit hash+reconcile status 文件面（`.runtime/reconcile_reports/reconcile_status_<sha>.json`）+审计面（`.runtime/claim_snapshots/{sid}.json`、`.runtime/gate_audit/commit_lock_fallback.jsonl`） | 政策 L633-654（网关工作流详解） |
| SSOT 真源 | 图11 C 车道环节（`config/dev_delivery_map.yaml`）+政策 Step 10 锚+`trae_075_stash_lifecycle.yaml`/`trae_084`；政策所指 `scripts/git_commit_gateway.py` CLI **不存在**（D14-G03，本批 ls 复证；网关真身=库 `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py` 在盘） | 双册图+rules+两路径核验 |
| 代码模块 | 正门 `scripts/git_commit.py`+网关库 `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py`（claim_files/_GlobalCommitLock/run_git 守卫/reconciler 注册 §_register_default_reconcilers；staging lifecycle reconciler priority=802 :160/:1903 本批实证）+`src/zephyr/gov_enforcement/commit_gates/stash_accumulation_gate.py`（在盘） | 四件在盘实证 |
| 门禁约束 | in_process gate 注册制（gate_auto_registrar，总数以 in_process_gate_registry 计数字段为准，散文禁写死）+pre-commit 通道（gate_registry）双册；关键 gate 按 priority：HELD-OVERLAP(50)/WORKTREE-REQUIRED(44)/FOREIGN-CHANGE(45)/COMMIT-SCOPE(48)/RENAME-DEPGRAPH-SYNC(39)/BLUEPRINT-NODE-ID-HARDCODE(57) 等；commit 四件套（trae_072/073/068/069）；滥用监控 6 维阈值 | `docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml`（756 行）+`.../gate_registry.yaml`（2367 行）；trae_069 |
| 自动化触发 | 队列化提交（`scripts/commit_queue.py` enqueue/drain）；40+ post-commit reconciler 异步框架（`src/zephyr/governance/audit/reconcile_runner.py` §launch_reconcile_async，detached worker+status file+心跳+sweep_orphans）；GATE-STASH-LIFECYCLE（AI 前缀+age>4h 自动清） | 政策附录 C（L1054-1079 全表）；附录 C 真源指向网关 §符号锚 |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 正门 CLI/重试语义/队列入口齐 |
| 输出面 | pass | hash+status file+三类审计面路径全在册 |
| SSOT 真源 | warn | 机制真源正确外指图11；但政策正文命令仍写幽灵件 `scripts/git_commit_gateway.py`（G03，注记与正文并存矛盾） |
| 代码模块 | pass | 正门+网关库+stash gate 三层实证在盘 |
| 门禁约束 | pass | 双册在册（107+191 台口径以计数字段为准） |
| 自动化触发 | pass | 队列+40+ reconciler+stash 自动清三层自动化实证 |

## 4. 缺口与建议

- 缺口1（D14-G03）：政策 Step 10 标题与命令注释仍指 `scripts/git_commit_gateway.py`（CLI 不存在）；R-03 注记已在（L616-617）但标题未改。建议：政策 Step 10 标题改"GitCommitGateway 落地（正门 CLI=scripts/git_commit.py）"，消除注记-正文矛盾。
- 缺口2：gate 关键清单政策散文写死实名（NO-SECRET-HARDCODE 等 2026-10-04 R-14 更正）——再次漂移风险。建议：散文只留"按注册表 priority 字段为准"，删实名清单。
- 缺口3：本段 verifiability 恒 manual 是图法规定（反洗白），实际链路自动化程度全图最高——建议在 capability_cards 注明"manual=账法口径非能力口径"，防误读。
