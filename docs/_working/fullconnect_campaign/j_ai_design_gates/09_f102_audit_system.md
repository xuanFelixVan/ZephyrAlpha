---
ttl: task_bound
title: F102 审计体系——挖干案卷
session: zc-l10-20260927
---

# F102 · 审计体系（gov_audit 编排+语义/供应链/隐私审计+Merkle 小时链）

> 总册行（00_全环节总册.md:177）：built｜上游 全链｜下游 报告｜P2｜G6
> 第一证据源：fullflow_mining/m3_governance/02_reconcilers.md（governance.db 落库面）＋src/zephyr/gov_audit/

## 一、六向台账（实证锚点）

| 向 | 实测证据（本日复核） |
|---|---|
| 上游输入 | 全链事件（commit 审计 GATE-COMMIT-GW-AUDIT 恒真 :6875"审计始终运行"；emergency_commit reconcile_execution_log 落库 M3 01 §3.7④）＋gate_execution_stats.jsonl＋外部工具审计 |
| 下游消费 | 报告面（F115）/evidence_pack 取证包/observability_dashboard 投影/governance.db（reconcile_execution_log、emergency/abuse 计数，M3 02 §二） |
| 自动化触发 | 事件触发（commit/landing/reconcile 执行日志）；merkle_hourly 小时链（模块名自证节拍）；log_rotation/retention/tiered_storage 自维护 |
| 真源与注册表 | src/zephyr/gov_audit/（**本日 ls = 64 顶层条目**；bridges/ 7 桥件）；语义审计真身=src/zephyr/governance/semantic_audit（本日 find 实证）；蓝图/治理锚各文件头部 BLUEPRINT 头 |
| 门禁与质量尺 | audit_write_failure_protector.py（写失败防护）＋integrity_verifier.py＋agent_signer.py（签名）＋audit_admission_controller.py（审计准入） |
| 当前运行状态 | built（件全在产；测试面 tests/audit 103 件+tests/gov_audit 1 件+tests/semantic_auditor 专树） |

## 二、子模块三级枚举（64 条目按族收敛，本日 ls 实测）

1. **编排与写入**：pipeline_runner.py｜writer.py｜event_store.py｜audit_schema.py｜audit_admission_controller.py｜audit_write_failure_protector.py｜log_rotation.py｜resource_aware_pool.py｜_orchestrator_compat.py。
2. **完整性链（Merkle 小时链族，总册点名实证）**：merkle_audit.py＋**merkle_hourly.py**（小时链）｜integrity.py｜integrity_verifier.py｜provenance_tracker.py｜genesis.py｜changelog_manager.py。
3. **专项审计族**：语义=governance/semantic_audit（外包）＋text_to_finding_adapter.py｜供应链=supply_chain.py＋supply_chain_security.py＋sbom_generator.py＋external_tool_audit.py｜隐私=privacy.py｜合规=compliance_map.py＋spec_auditor.py＋corporate_actions.py＋code_archaeology.py。
4. **发现与信任**：finding_ingest.py｜finding_model.py｜anomaly.py｜trust_engine.py｜trust_ring_manager.py｜trust_bridge.py｜delegation_auditor.py｜wqa_scorer.py｜incremental_review.py。
5. **取证与消费**：evidence_pack.py｜forensic_package.py｜query.py｜replay_engine.py｜observability_dashboard.py｜dora_metrics.py｜action_history.py｜glossary_matrix.py｜feedback_policy.py/feedback_self_audit.py。
6. **桥接面（bridges/ 7 件）**：audit_anomaly/audit_contracts/audit_delegation/audit_drift/audit_feedback/audit_tiered_storage/audit_trust 七桥——对 F99 漂移、F104 委托、tiered 存储的互锁通道。
7. **存储分层**：tiered_storage.py＋tiered_storage_bridge.py＋retention.py＋indexer.py＋models.py＋cli.py＋self_monitor.py＋kb_gate.py＋secret_registry_drift.py（密钥册三方对账，F105 关联件）。

## 三、接线四态独立复核

- 总册判 **built**：成立——四总册点名件全实存：gov_audit 编排（pipeline_runner/writer）、语义审计（governance/semantic_audit 专包+适配器）、供应链（supply_chain_security+sbom）、隐私（privacy.py）、Merkle 小时链（merkle_hourly.py）。
- 测试面分化：tests/audit 103 件（主测试网）vs tests/gov_audit 1 件 vs tests/semantic_auditor 专树——三树并存是分层有意还是漂移，本卷不下结论（挂起，同 F99 G3 模式）。
- 小时链运维态：merkle_hourly 节拍声称小时级，但计划任务/常驻宿主归属本卷未挖（审计链若靠 reconcile 事件驱动则属 M3 02 面），进待裁。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| G1 | merkle_hourly 运行宿主不明（事件 vs 计划任务 vs 常驻） | 查启动登记与最近产出时间戳后归类 | P1 |
| G2 | 审计三测试树（audit 103/gov_audit 1/semantic_auditor）无对账说明 | Owner 认定分层口径；关键件（writer/integrity_verifier）确保主网覆盖 | P2 |
| G3 | 审计自身的"审计 boredom"（恒真审计失敏）无抽检机制 | 对齐 §1.6 装饰/失效普查节奏，审计件纳入同普查 | P2 |
| G4 | 64 件族谱无册面（仅盘面） | 按本卷 §二族谱生成器化登记 | P2 |

## 五、自审闸三态

**结构面=挖干可施工**（总册五点名件逐一 ls 命中+64 条目族谱收敛）；**小时链宿主=待裁**；**测试树分层口径=挂起**。

## 六、复跑命令

```bash
ls src/zephyr/gov_audit/ | wc -l                                  # 64 顶层条目
ls src/zephyr/gov_audit/ | grep -E "merkle|supply_chain|privacy"  # Merkle/供应链/隐私点名件
find src/zephyr -type d -name "semantic_audit"                    # 语义审计真身
find tests/audit tests/gov_audit tests/semantic_auditor -name "test_*.py" | wc -l  # 测试面总量
ls src/zephyr/gov_audit/bridges/*.py | wc -l                      # 7 桥
```
