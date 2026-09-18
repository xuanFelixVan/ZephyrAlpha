---
ttl: task_bound
completes_when: 战役 st-vocabconsol-20260918 W8 封账提交后转 archived
---

# W7 红蓝对抗执行日志（先记结果，判据以 w7_adversarial_plan.md 为准）

> 与落地波次串行：注入真实文件的场景（R1/R2/R7/R9/R10/R6）排在 0008~0021 落地波
> 与 requeue 波之间隙执行，避免污染 requeue 快照重建。沙箱/离线场景（R3/R5/R8/A1）即时执行。

| 场景 | 时刻 | 结果 | 证据摘要 |
|------|------|------|----------|
| R3 折叠自毁通道 | 08:2x | ✅ 红→撤→绿闭环 | 注释掉 _collect_vocab_values 别名折叠 → test_real_three_source_convergence_is_empty 红（values 72→62，丢 10 别名）；还原后 6 passed，全文件 sha256 与注入前逐字节相等（5283100f…9b1d） |
| R5 补标瞎填护栏 | 08:1x | ✅ 三护栏全中 | tmp 沙箱仓 apply：ghost→skip_ghost、.aidrafts→skip_excluded、脏文件→skip_git_dirty 且 sha_before==sha_after 零写入；非法值 D_NOT_A_REAL_DOMAIN 被兄弟票 replaced；audit.jsonl 行数 3==applied 3 |
| R1 词表块注入 | 09:0x | ✅ 红→撤→绿闭环 | target_layer_vocabulary.yaml 注入假 D_PLAN 块 → validate_target_layer ERROR(未知值) 命中；还原后 RC=0 且文件与注入前逐字节相等（sha 核对，还原用保存字节非 git checkout） |
| R2 别名清空 | 09:0x | ✅ 检出别名失真 | aliases:["D_SIGNAL"]→[] → 校验器对引用值报 WARNING(别名值)；还原后回绿、字节相等 |
| R4 TR 重复注入 | 09:1x | ✅ 去重闭环+CAS 活证 | 注入重复条目 7090→dedupe→7089 且 0 重复组；另 StaleWriteRefused 在外部 CAS 流量下正确拒写旧基线（=意外收获的正证） |
| R6 预检 message 透传 | 09:3x | ✅ 确认失明并钉死 | grep 证实既有测试零覆盖（失明为真）→ 新测试 test_commit_preflight_mass_deletion_message.py 4 例；红证：临时摘掉 commit_preflight.py:266 的 commit_message kwarg → 2 例红（seen 缺 key）；还原后 13 passed 且文件与 index 零差异 |
| R7 层映射行摘除 | 09:0x | ✅ 派生通道单一性 | domain_responsibility_layer_mapping.yaml 按行范围摘除 D_GOV_REPAIR 三行 → --sync-layer 不再给该域条目写 layer；回插后字节相等 |
| R9 自检计数器 | 09:0x | ✅ 自检拦截 | total_values 62→99 篡改 → validate_target_layer 自检 ERROR；还原 RC=0 |
| R8 DB 幂等 | 08:1x | ✅ 双路径拒绝 + 挖出 P1 真缺陷 | old 不在 domains（D_ZZZ_GHOST）→ 拒绝 RC=4 零写入；old 存在且依赖冲突（D_COMPLIANCE→D_GOV_ENFORCEMENT）→ PK 冲突预检拒绝 RC=4 零写入。**副作用挖矿**：D_DATA→D_MKT_DATA 真 merge 在 B1 兜底扫描把 domain_events.source_domain 复合值 D_DATA_ENG 子串替换成 FK 不存在的 D_MKT_DATA_ENG，提交时 FK 违例整笔崩（事务回滚保数据=幸运，功能对该类域必死）→ 见 w7_fixes.md FIX-R8-1 |
| A1 热文件 CAS | 08:5x | ✅ | 沙箱 hot.yaml 双写者：过期基线第二次写被 StaleWriteRefused，before/after sha 链完整 |
| A2 requeue 快照语义 | 09:2x | ✅ | 0008 落地后 worktree==HEAD 自然核验：requeue 重建快照取当前工作树字节，活文件必须在 requeue 前字节还原 |
| R10 豁免滥用 | 09:4x | ✅ 红→撤→绿闭环 + 边界钉 | 活注入：argparse manual 脚本塞短理由（<10字）m11 noqa → _check_manual_only_permanent_new 判违规(红)；无标记基线仍红；换合规长理由→绿；边界 9 字红/10 字绿；既有 30 例 noqa 测试全绿；临时件已删 |

## 基线复核（轮1 补充，全部只读）

- check_vocab_domain_convergence --with-db：RC=0，known=79/FDR=68/TR=66/在用=72，ADVISORY DB 未收编域 10（留案不变）
- validate_target_layer：RC=0，合法 62+废弃 9+别名 10，全树值合法
- process_reaper --status：活着，killed=0；worktree_changes=31（本战役在途批）
- tests/governance/commit_gates 全量：2547 passed（含 VOCAB-CHAIN 豁免扩展后）
