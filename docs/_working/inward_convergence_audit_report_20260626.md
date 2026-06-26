---
doc_type: audit_report
title: "向内收4原则审查报告 — docs/01_policies_and_standards"
status: completed
ttl: task_bound
created_by: agent
created_at: 2026-06-26
owner: ZephyrAlpha-Owner
layer: cross_layer
module_id: AUDIT-INWARD-001
tags:
  - audit-report
  - inward-convergence
  - policies-and-standards
  - circadian-scheduler
  - orphan-cleanup
summary: "对 docs/01_policies_and_standards 及子目录用向内收4原则（唯一真源·事件驱动·第一性原理·新AI可发现性）审查，完成 P0-P2-4 + 遗留1-2 修复。本报告基于 git commit 历史重建，P0-P2-3 详细信息来自 commit message。"
completes_when: "P3 文档级治理范围确定后归档至 .runtime/working_archive/，或经用户确认本次审查收尾"
related_rationale:
  - "向内收4原则定义见 trae_060_inward_consolidation.yaml"
  - "审查范围：docs/01_policies_and_standards/ 全树"
---

# 向内收4原则审查报告

**审查日期**：2026-06-26
**审查范围**：`docs/01_policies_and_standards/` 及其全部子目录（policies/、rules/、_registry/、templates/）
**审查原则**：向内收4原则
1. **唯一真源**（Single Source of Truth）—— 消除重复副本，扩展已有而非创造新文件
2. **事件驱动**（Event-Driven）—— 废除定时轮询，改为事件触发
3. **第一性原理**（First Principles）—— 治本不治标，从根因解决问题
4. **新AI可发现性**（AI Discoverability）—— 规则必须有指针引用真源，新AI能定位

## 修复优先级总览

| 优先级 | 范围 | 状态 | 核心提交 |
|--------|------|------|----------|
| P0 | GitCommitGateway 缺口审查 | ✅ 完成 | `f0227f306` (auto-sync 标记) |
| P1 | scope 过滤重复 + GATE-ID-UNIQ 修复 | ✅ 完成 | `bb86302de`, `400c72586` |
| P2-1 | 删除 document_metadata_index_registry.yaml 真重 | ✅ 完成 | `ca88e472e` |
| P2-2 | 生成器解析逻辑修复（trae_047 代码头格式） | ✅ 完成 | `ab0a3f812` |
| P2-3 | L0 executors 补全 + 词表硬编码修复 | ✅ 完成 | `a83044260`, `798520d99` |
| P2-4 | CircadianScheduler 完整迁移废除 | ✅ 完成 | `c4f4f3791d` |
| 遗留1 | stale_task_recovery 文档更新（事件驱动覆盖） | ✅ 完成 | `3c67cd296e` |
| 遗留2 | 孤儿文件清理（4个 __init___from_orches.py） | ✅ 完成 | `3c67cd296e` |
| P3 | 文档级治理（policies/rules 关系、词表统一） | ⏳ 待评估 | — |

---

## P0 — GitCommitGateway 缺口审查

**提交**：`f0227f306` (session: p0-review-gateway-gaps-20260626)

**审查内容**：GitCommitGateway 作为项目唯一合法 git commit 入口，检查其门禁覆盖完整性。

**结果**：P0 级阻塞问题已在 P0 阶段清零，后续 P1-P2 修复均通过 GitCommitGateway 提交验证。

---

## P1 — scope 过滤重复 + GATE-ID-UNIQ 修复

### P1-1: 提取 _in_audit_scope() 单一真源

**提交**：`bb86302de` (Fix 1)

**问题**：scope 过滤逻辑在多处重复实现，违反唯一真源原则。

**修复**：提取 `_in_audit_scope()` 为单一真源方法，消除 scope 过滤重复。

### P1-2: GATE-ID-UNIQ registry 空格手误修复

**提交**：`400c72586`

**问题**：GATE-ID-UNIQ registry 中存在空格手误（`scripts/` 与 `scripts/` 不一致）。

**修复**：修正空格手误，补通用词扩展提示。此修复被并发 session sweep 提交，本次提交仅修正空格。

### P1-3: GATE-ID-UNIQ 引号绕过漏洞修复

**提交**：`7b708ab63`

**问题**：GATE-ID-UNIQ 钩子存在引号绕过漏洞。

**修复**：修复引号绕过漏洞 + AGENTS.md 补注册门禁（红蓝对抗修改）。

### P1-4: ttl decision_tree 机器可读化

**提交**：`9463dd11a`

**问题**：ttl decision_tree 非机器可读，内容判定逻辑不治本。

**修复**：ttl decision_tree 机器可读化 + 内容判定治本。

---

## P2-1 — 删除 document_metadata_index_registry.yaml 真重

**提交**：`ca88e472e` (session: p2-1-doc-metadata-delete)

**问题**：`document_metadata_index_registry.yaml` 是真重（与另一个 registry 内容重复），违反唯一真源原则。

**修复**：向内收删除该文件，保留权威 registry。

**验证**：post-commit auto-sync `c6c5dda7a` 确认无破坏性影响。

---

## P2-2 — 生成器解析逻辑修复

**提交**：`ab0a3f812` (session: p2-2-generator-parser)

**问题**：`trae_047` 代码头格式不被生成器解析支持，`CFG-` 前缀无法识别，存在自跳过 bug。

**修复**：
- 修复生成器解析逻辑，支持 `trae_047` 代码头格式
- 支持 `CFG-` 前缀
- 修复自跳过 bug

**验证**：post-commit auto-sync `985a3057d` 确认生成器输出正常。

---

## P2-3 — L0 executors 补全 + 词表硬编码修复

### P2-3a: L0 空 executors 补全

**提交**：`a83044260` (session: p2-3-l0-executors)

**问题**：6条规则的 `enforcement executors` 为空数组，导致线上约束无机械执行路径（违反第一性原理——约束必须可机械验证）。

**修复**：补全 6条规则的 enforcement executors，执行脚本与 `trae_018` 同款。

**验证**：post-commit auto-sync `929656e52` 确认无破坏。

### P2-3b: 词表硬编码副本修复

**提交**：`798520d99` (session: p2-3-audit-update)

**问题**：trae_060 审计发现 13 处硬编码词表副本，违反唯一真源原则。

**修复**：
- 13处修复为64处2词表全量排查结果
- TRAE-042 引用 section 名同步

### P2-3c: 附加修复（P2-3 审计期间发现）

| 提交 | 修复内容 |
|------|----------|
| `6e0d0204a` | Fix 5: 向内收消除 `analyze_orphan_consumers.py` 重复消费者地图 |
| `63c65c44c` | 修复7个生成器脚本 doc_type 硬编码为合法值，防止 GATE-DOMAIN-DOC reconciler 重新生成时覆盖回非法值 |
| `dceeba447` | 修复 `_validate_ssot_linkage` 文档残留 + 补顶部 docstring 可发现性 |
| `e4cb24bcd` | split AGENTS.md L157 completes_when+reconciler into main line + indented sub-item for Grep visibility |
| `dcbffbdb1` | cure 6 inward-convergence audit violations（6处向内收审计违规修复：删除CN别名v4/删除冗余section 7 v6/移动R7-R8设计权衡到代码docstring v6/替换CLI cmd为capability_id指针v2+3/添加git add -A lesson v1） |

---

## P2-4 — CircadianScheduler 完整迁移废除

**提交**：`c4f4f3791d` (session: p2-4-circadian) — 33 files changed, 85 insertions(+), 2649 deletions(-)

**问题**：CircadianScheduler 是定时调度机制，违反事件驱动原则。MOD-INF-030 规则要求红蓝对抗验证器采用事件驱动触发，废除 CircadianScheduler 定时触发。

**修复范围**：
- 删除核心文件 3 个：`circadian_scheduler.py`、`circadian_tasks/` 目录、死数据文件
- 修改源文件 15 个：移除 CircadianScheduler import/调用/引用
- 更新测试 16 个：重写测试匹配事件驱动新机制
- 清理死数据：`schedule_state.json`、`schedule-state.json`
- 更新红蓝场景：`_scenario-registry.yaml` 中 CircadianScheduler 相关场景标记 deprecated

**事件驱动覆盖验证**：
- `Conductor.plan_cycle()` 在每次规划周期开始时调用 `recover_stale_claims()`（见 `src/zephyr/trading/conductor.py:79-98`）
- `register_boot_cron_jobs` 仅保留 `bus.subscribe("skill.freshness_critical")` 事件订阅
- 失去的只是"CircadianScheduler 不运行时的定时清理"——低风险回归，已被 Conductor 事件驱动覆盖

**6 个 [CONSUMERS] 注释漂移清理**（P2-4 主提交未覆盖的残余）：
- `src/zephyr/autonomy_core/skill_freshness_ext.py`
- `src/zephyr/trading/resource_optimization.py`
- `src/zephyr/security/adversarial_validation/commit_trigger.py`
- `src/zephyr/governance/audit_trail/pipeline_runner.py`
- `src/zephyr/governance/finding_ingest.py`
- `src/zephyr/governance/audit_orchestrator/pipeline_runner.py`

---

## 遗留1 — stale_task_recovery 文档更新

**提交**：`3c67cd296e` (session: cleanup-orphans)

**问题**：P2-4 废除 CircadianScheduler 后，`_scenario-registry.yaml` 中 stale_task_recovery 相关场景的 defense 描述仍指向已废除的定时调度，需更新为反映 Conductor 事件驱动覆盖现状。

**修复**：
- `RB-SCEN-045` defense 更新为：`"transition() DM-401 warning + Conductor.plan_cycle recover_stale_claims 事件驱动 + session close IN_PROGRESS=0 check"`
- `RB-SCEN-046` defense 更新为：`"circadian_scheduler 已废除（2026-06-26），本攻击向量失效；Conductor.plan_cycle() 已事件驱动覆盖 recover_stale_claims"`
- `[CHANGE-NOTE]` 更新为：`Conductor.plan_cycle() 已事件驱动覆盖 recover_stale_claims`
- `tests/unit/db/test_dm400_stale_task_fix.py` docstring 更新为：`recover_stale_claims 方法（Conductor.plan_cycle 事件驱动覆盖，CircadianScheduler 定时注册已废除）`

---

## 遗留2 — 孤儿文件清理

**提交**：`3c67cd296e` (session: cleanup-orphans) — 10 files changed, 9 insertions(+), 520 deletions(-)

**问题**：4 个 `__init___from_orches.py`（三下划线变体名）文件无任何 import 引用，是历史迁移遗留的孤儿文件。

**验证**：`grep -r "import.*__init___from_orches"` 返回空，确认无消费者。

**修复**：
- 删除 4 个孤儿文件：
  - `src/zephyr/autonomy_core/__init___from_orches.py` (238行)
  - `src/zephyr/integration/__init___from_orches.py` (109行)
  - `src/zephyr/integration/governance/__init___from_orches.py` (35行)
  - `src/zephyr/trading/__init___from_orches.py` (129行)
- 更新 4 个 [CONSUMERS] 注释（`zephyr.integration.governance.__init___from_orches` → `zephyr.integration.governance`，指向真正的消费者 `__init__.py` 的 `__all__` 导出）：
  - `src/zephyr/integration/governance/protocol.py:5`
  - `src/zephyr/integration/governance/phase_hold.py:5`
  - `src/zephyr/integration/governance/governance_adapter.py:5`
  - `src/zephyr/integration/governance/auditor.py:5`

**Import 验证**：`from zephyr.integration.governance import protocol, phase_hold, governance_adapter, auditor` 通过。

---

## P3 — 文档级治理（待评估）

**状态**：⏳ 待评估

**初步扫描结果**（2026-06-26）：
- `policies/` 仅 1 个文件（`parallel_session_coordination_policy.md`，战略层契约），`rules/` 60 个规则（操作层）—— 结构合理，非"合并"关系
- `layer_vocabulary.yaml` v1.1.0 已含 `dir_prefix` 字段，对齐 `architecture_model/layers/` —— 无明显不统一
- `rules/_index.yaml` v2.2.0 已对齐 trae_060 向内收原则 §2 索引真源唯一

**结论**：快速扫描未发现明显 P3 治理缺口。需用户确认是否需要深入 P3 审查。

---

## 审查统计

| 指标 | 数值 |
|------|------|
| 审查范围 | `docs/01_policies_and_standards/` 全树 |
| 修复优先级 | P0-P2-4 + 遗留1-2 |
| 总提交数 | 15+ 个相关 commit |
| 总文件变更 | 50+ 文件 |
| 总代码删除 | 3000+ 行（主要是 CircadianScheduler 废除） |
| 验证方式 | git commit 历史 + import 验证 + post-commit auto-sync |

## 审查原则落地情况

| 原则 | 落地证据 |
|------|----------|
| **唯一真源** | P2-1 删除重复 registry；P2-3 修复词表硬编码副本；遗留2 删除孤儿文件 |
| **事件驱动** | P2-4 完整废除 CircadianScheduler 定时调度，迁移至 Conductor.plan_cycle() 事件驱动 |
| **第一性原理** | P2-3 补全 L0 executors 机械执行路径；P1-4 ttl decision_tree 机器可读化治本 |
| **新AI可发现性** | P2-3 修复 docstring 可发现性；AGENTS.md 补注册门禁；[CONSUMERS] 注释指向真正消费者 |

---

## 注意事项

1. **报告重建限制**：本报告基于 git commit 历史重建。P0-P2-3 的详细信息来自 commit message，P2-4 及遗留1-2 有完整的对话上下文记录。如需更详细的修复前后对比，请查阅对应 commit 的 `git show <hash>`。

2. **并发 session 影响**：审查期间有其他 session（`rb3-cure`、`rb-fix-iduniq` 等）并发提交，部分 auto-sync commit 是其他 session 的 post-commit 触发。

3. **P3 范围不确定**：审查报告原始 P0-P3 优先级清单在对话上下文压缩中丢失，P3 范围基于摘要中的模糊描述重建。需用户确认是否需要深入 P3 审查。
