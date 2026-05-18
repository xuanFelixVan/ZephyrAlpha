# CLAUDE.md — ZephyrAlpha Project Context for Claude
# v0.4.0 — 自包含版，防幻觉/防漂移完整规则内嵌

> **补充规则**: [`.trae/rules/project_rules.md`](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md) | [`.trae/rules/onboarding_detail.md`](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)
> **本文件必须自包含**——Claude AI 可能不读 project_rules.md，以下规则不可省略。

## Project Identity
- **Project:** ZephyrAlpha — AI-driven software engineering platform
- **Version:** 0.14.0
- **Python:** 3.12+
- **Pydantic:** V2 (use_enum_values=True)

## Architecture Overview
- `src/zephyr/l01_infrastructure/` — Infrastructure layer (code dedup, A2A protocol, agent RBAC)
- `src/zephyr/governance/` — Governance domain (8 modules, GCT contracts)
- `src/zephyr/pipeline/` — Dual-track pipeline (M1-M11, DeepSeek/GLM/Claude)
- `src/zephyr/gates/` — Gate Engine (19 gate configs, circuit breaker, drift detection)
- `src/zephyr/kb/` — Knowledge Base (UnifiedMemoryAPI, ChromaDB, VMS bridge)
- `src/zephyr/mcp/` — MCP Servers (9 servers, gateway, RBAC, rate limiting)
- `src/zephyr/feedback_loop/` — FLE (collect→detect→diagnose→act→verify)
- `src/zephyr/context_engine/` — Context Engine (compression, RAG, token budget)
- `src/zephyr/orchestrator/` — Task Queue + Trigger Router
- `src/zephyr/agent_spec/` — 12 Domain Skills + 3 Role Skills + LLM Gateway
- `src/zephyr/vector_memory/` — VMS (8 collections, HybridRetriever, BGE-M3)
- `src/zephyr/shared/` — EventBus + ContractBus + API_INDEX + Skill Registry

## CBAC Capability Boundaries (5 Rules)
1. **write_src** — 8 AI-Modifiable layers + 8 kb files (deny: 4 Immutable + 2 Human-Gated + 6 cross-cut)
2. **write_script** — Only `validate_truth_source_cascade.py` (deny: all other governance scripts)
3. **write_rules** — Empty (deny: .cursor/rules + .trae/rules)
4. **write_docs** — docs/08_knowledge + drafts-and-audits only (deny: governance + architecture docs)
5. **write_config** — Only compression/policy.yaml (deny: capabilities + trigger_router + risk + drift_thresholds)

Default: DENY. Allow is exception to deny. Unmatched = deny.

## Hard Rules

| # | 规则 | 命令/操作 |
|---|------|----------|
| 1 | 写入任何文件前必须过门禁 | `python scripts/governance/pre_write_gate.py <file>` |
| 2 | 创建新文件必须走 scaffold | `python scripts/scaffold.py module/script/gate <参数>` |
| 3 | 删除文件必须过三步审判 | 见下方 RULE-THREE 三步审判 |
| 4 | 新建功能前必须搜索已有 | registry-of-registries.yaml → Grep → 复用决策 |
| 5 | 原子写入 | temp-file + `os.replace()`，禁止 `open(path, "w")` 直接写 |
| 6 | 强制并行 | `for`+subprocess/I/O → `ThreadPoolExecutor(max_workers=8)` |
| 7 | 零残留 | `_temp/_check/_fix` 前缀文件 session 关闭前必须删除 |
| 8 | 编码安全 | Python `open()` 禁止省略 `encoding='utf-8'` |
| 9 | 禁止占位符 | 无 `TODO`/`...`/`pass`/`NotImplementedError`，必须可执行 |
| 10 | 编辑优先 | 禁止删+建来"修改"，必须 surgical edit |
| 11 | 最小变更 | 只改必须改的，禁止"顺手重构""顺便优化" |
| 12 | 假设显式化 | 不确定 → 标记 `[ASSUMPTION]` 等待确认。路径和签名假设 = 禁止 |

### RULE-THREE 删除文件三步审判

```
STEP 1 登记检查：在 manifest/registry/__init__.py 中被引用？git log 中存在？
  YES → 有价值，不能删。只能 refactor/rehome
STEP 2 重复检查：有另一个文件与它内容完全相同？那个文件在正确位置且已注册？
  双 YES → 真正重复，可删
STEP 3 逐行价值检查：每行内容在其他地方存在？删除后有无代码引用此路径报错？
  ANY 有价值 → 保留并注册，不删除
```

**零消费者≠无价值**——判断删除看功能价值，不看消费者数量。零消费者可能因自动化管线未接通。

### RULE-TWO 反孤儿五问（任何新功能产出后 MUST 自问）

| # | 问题 | 不满足 → 处置 |
|---|------|-------------|
| 1 | 谁调用它？入口在哪？ | 没有入口 → 不能关闭任务 |
| 2 | 谁发现它？下一个 AI session 怎么知道？ | 没有发现机制 → 必须先注册 |
| 3 | 谁维护它？放在哪个模块/目录下？ | 没有归属 → 不能落盘 |
| 4 | 谁校验它？有 gate 检查吗？ | 没有校验 → 必须添加 gate |
| 5 | 谁更新它？模板/清单/注册表已更新？ | 没有 → 必须更新 |

**产出→集成映射**：新脚本→`script_manifest.yaml` | 新模块→`__init__.py __all__` | 新门禁→`_registry.yaml` + `phase_manager` | 新RULE→`rule-registry.md`

## 防幻觉十八条（Vibe Coding 铁律）

### 结构追溯（#1-#6）

| # | 规则 | 不遵守会怎样 |
|---|------|------------|
| 1 | **源头追溯**——代码文件 MUST 标注 `[BLUEPRINT] {module_id} \| {蓝图路径}` | 无标注 = 孤儿文件 |
| 2 | **不变量声明**——代码文件 MUST 标注 `[INVARIANTS] {不可违反的约束}` | AI 修改时破坏关键约束 |
| 3 | **修改守卫**——代码文件 MUST 标注 `[MODIFY-GUARD] {改此文件必须同步更新的文件}` | AI 改一处忘其他，集成断裂 |
| 4 | **依赖声明**——代码文件 MUST 标注 `[CONSUMERS] {依赖此文件的模块}` | AI 不知道修改的影响范围 |
| 5 | **蓝图锚点**——蓝图 MUST 在头部标注蓝图+施工图模板+AI 压缩工作流标准链接 | AI 偏离蓝图模板，产出不一致 |
| 6 | **漂移检测**——蓝图 §4 文件清单 ↔ 代码 `[BLUEPRINT]` 字段 MUST 双向对齐 | 蓝图与代码漂移 |

### 行为约束（#7-#10）

| # | 规则 | 不遵守会怎样 |
|---|------|------------|
| 7 | **禁止占位符**——代码中禁止 `TODO`/`...`/`pass`/`NotImplementedError`。必须产出可执行代码 | 半成品伪装完成 |
| 8 | **编辑优先**——禁止删除+重建来"修改"。必须 surgical edit | 丢失 history + 注册失效 |
| 9 | **最小变更**——只改必须改的。禁止"顺手重构""顺便优化" | 无关变更引入 bug |
| 10 | **假设显式化**——不确定的决策 MUST 标记 `[ASSUMPTION]` 等待确认。路径和签名假设 = 禁止 | AI 凭空假设 API/格式/配置 |

### 输出验证（#11-#14）

| # | 规则 | 不遵守会怎样 |
|---|------|------------|
| 11 | **步骤验证门**——每步完成 MUST 验证成功后才进下一步 | 错误累积，回溯成本指数增长 |
| 12 | **导入验证**——使用任何 `import`/API/函数前 MUST Grep/Read 确认存在 | 引用不存在的库/API/模块 |
| 13 | **自审闭环**——产出代码后 MUST 对照需求自审：功能完整？边界？错误路径？ | 输出与需求不匹配 |
| 14 | **新代码必测**——新建/修改代码 → MUST 写或更新测试。无测试 = 未完成 | bug 无从发现 |

### 安全防护（#15-#18）

| # | 规则 | 不遵守会怎样 |
|---|------|------------|
| 15 | **安全最低通过**——交付前 MUST 通过：认证/注入/数据暴露三项检查 | 安全漏洞交付 |
| 16 | **计划先行**——涉及 >3 文件或 >50 行 → MUST 先输出计划 → 确认 → 执行 | 无计划大范围修改，失控 |
| 17 | **跨文件影响检查**——修改前 MUST 检查 `[CONSUMERS]` + Grep 所有引用 | 改一处忘其他，集成断裂 |
| 18 | **上下文新鲜度**——对话 >30 轮或 AI 出现重复/矛盾 → 开新会话 | 上下文退化，幻觉温床 |

### 防幻觉头部十字段（新建/修改代码文件 MUST 包含）

| # | 字段 | 必填 | 枚举值/格式 |
|---|------|:---:|-----------|
| 1 | `[BLUEPRINT]` | ✅ | `{module_id} \| {path} \| §{N}` |
| 2 | `[MODULE]` | ✅ | `{full.module.path}` |
| 3 | `[INVARIANTS]` | ✅ | 分号分隔 |
| 4 | `[MODIFY-GUARD]` | ✅ | 分号分隔 |
| 5 | `[CONSUMERS]` | ⚠️ | 分号分隔 |
| 6 | `[STABILITY]` | ✅ | `frozen/stable/evolving/volatile` |
| 7 | `[SAFETY]` | ✅ | `H/M/L` |
| 8 | `[AI_AUTONOMY]` | ✅ | `immutable_core/human_gated/ai_modifiable` |
| 9 | `[ERROR_CONTRACT]` | ⚠️ | 分号分隔 |
| 10 | `[TESTS]` | ⚠️ | 分号分隔 |

**`[AI_AUTONOMY]` 约束**：`immutable_core` = 只读禁止修改 | `human_gated` = 需 Owner 批准 | `ai_modifiable` = 可直接修改

**`[STABILITY]` 约束**：`frozen` = 禁止修改 | `stable` = 需变更门控 | `evolving` = 可频繁修改 | `volatile` = AI 可自主调整

## Skill Discovery (Keywords → Skill, 19 Skills)

| 关键词 | Skill |
|--------|-------|
| database / sql / migration | SKILL-DOM-DBS-001 |
| mcp / server / tool | SKILL-DOM-MCP-001 |
| context / pipeline | SKILL-DOM-CTX-001 |
| feedback / loop / 根因 / 5 Whys / 治根 / 追问到底 / 诊断反转 | SKILL-DOM-FBL-001 |
| gate / rule / policy | SKILL-DOM-GAT-001 |
| permission / rbac | SKILL-DOM-AGT-001 |
| blueprint / architecture | SKILL-DOM-BLU-001 |
| audit / drift / governance | SKILL-DOM-DRF-001 |
| knowledge / KE | SKILL-DOM-KNW-001 |
| rollback / undo / checkpoint | SKILL-DOM-RBK-001 |
| security / lsg / injection / prompt_injection | SKILL-DOM-LSG-001 |
| vector / embedding / VMS / chromadb | SKILL-DOM-VMS-001 |
| task / taskcard / task-card | SKILL-DOM-TSK-001 |
| telemetry / observability / metrics | SKILL-DOM-TEL-001 |
| dedup / duplicate / monoculture | SKILL-DOM-DED-001 |
| budget / 预算 / cost limit / token limit | SKILL-DOM-BGT-001 |
| fix / repair / self-heal / 修复 / 故障 | SKILL-DOM-AFX-001 |
| a2a / agent-to-agent / 冲突 | SKILL-DOM-A2A-001 |
| behavioral / safety / 行为审计 | SKILL-DOM-BEH-001 |

加载: `python -m zephyr.agent_spec load <skill_id>`

## MCP Tool Catalog (9 Servers)
| Server | Tools | Safety |
|--------|-------|--------|
| task_manager | list/get/create/update/delete/health | L/M/H |
| knowledge_base | query/recall/write/delete/reindex/health | L/H |
| gate_engine | list_gates/get_result/evaluate/override/reload/simulate/health/bypass | L/M/H |
| session_handoff | load/save/validate/cleanup/health | L/M/H |
| intent_router | classify/route/train/health | L/M |
| blueprint_search | find/index/health | L |
| sandbox | execute/health | H |
| governance | health/list_contracts/run_gate/check_lock/acquire_lock | L/M/H |
| vector_memory | search/write/recall/list_collections/health | L/H |

## Trigger Router (6 Triggers)
| Trigger | Handler | Safety |
|---------|---------|--------|
| onboarding | handle_onboarding_stub → layer_router | M |
| drift_detected | handle_drift_stub → drift_detector.trigger_recovery | H |
| compression_needed | handle_compression_needed (real) | M |
| cleanup_due | handle_cleanup_stub → archive_drafts_zone | L |
| blueprint_published | handle_blueprint_stub → decision_engine.reflect | M |
| blueprint_lookup | handle_blueprint_lookup_stub → blueprint_routing.yaml | L |

## Key Conventions
- No comments unless explicitly required
- UTF-8 encoding everywhere
- Pydantic V2 BaseModel for all data structures
- Lazy imports via `__getattr__` + `_COREMODULES` pattern
- temp-file + atomic rename for concurrent write safety

## Test Commands
```
python -m pytest tests/agent_rbac/ -q
python -m pytest tests/governance/ -q -k "not test_all_scripts and not test_security_scripts"
python -m pytest tests/test_code_dedup_engine/ -q
```

## Session Lifecycle

**Start (Cold Start 14 Steps)**:
1. Read registry-of-registries.yaml (24 registries)
2. Read system master blueprint §0
3. Read project_rules.md
4. Session Continuity restore
5. Phase Manager check
6. Asset inventory
7. Skill discovery: `python -m zephyr.agent_spec list`
8. Knowledge Base self-check
9. Escalation Protocol activate
10. Drift Detector init
11. Agent RBAC activate
12. Rollback System activate
13. Budget Enforcer activate
14. Audit Trail context inject

**End**:
```
python scripts/lock_files.py release-all
python scripts/governance/audit_registration.py
python scripts/governance/sync_rule_registry.py
python scripts/governance/auto_sync_all_registries.py --all --warn-only
零残留扫描: _temp* / _check* / _fix* / _phase_* 前缀文件 → 全部删除
废墟引用检查: 删过文件/目录 → 确认无其他文件引用已删路径
```

## 强制集成对照表

| AI 要做什么 | 必须先跑什么 | 不跑会怎样 |
|------------|-------------|-----------|
| 创建新文件 | `python scripts/scaffold.py module/script/gate <参数>` | 绕开 scaffold → 孤儿文件 |
| 写入任何文件 | `python scripts/governance/pre_write_gate.py <文件>` | exit≠0 → 禁止写入 |
| 删除任何文件 | RULE-THREE 三步审判 → 全通过才能删 | 一步不通过 → 不能删 |
| 修改 `src/zephyr/` 源码 | `python -m pytest tests/ --collect-only -q` | 语法错误 → 禁止提交 |
| 修改 YAML 契约/配置 | `python scripts/governance/d5_architecture/checkers/check_contract_code_drift.py` | 契约断裂 → 禁止合并 |
| 修改 AGENTS.md | `python scripts/governance/d5_architecture/validators/validate_load_path_integrity.py --check` | LoadPath 断裂 → 禁止提交 |
| 任何文件变更后 | `python scripts/governance/audit_registration.py` | 有孤儿 → 禁止关闭任务 |
| 安全敏感变更 | `python scripts/governance/d6_security/scan_secret_leak.py` | 泄漏 → 硬阻断 CI |
| 回滚/撤销 | `python scripts/rollback.py preflight` → CLEAN → `rollback.py <cmd>` | preflight FAIL → 禁止回滚 |

## 根因追踪（MTH-006）

遇到 bug/失败/漂移/异常 → MUST 追问到底：连问为什么直到找到最根部原因。追问路上发现的每个中间问题 MUST 一并解决，不留尾巴。

| | 治根 | 治标 |
|---|------|------|
| 修复后同类问题 | 不再产生 | 可能重现 |
| 修复作用层面 | 系统设计层面 | 当前实例 |
| 可否泛化 | 可描述为一条原则 | 无法泛化 |

## 搜索先行复用决策

新建功能前 MUST 搜索已有覆盖。三步：①关键词全局搜索 ②注册表精确匹配 ③复用决策。

| 覆盖率 | 决策 |
|--------|------|
| 完全覆盖 | 直接用 |
| 80% | 扩展已有 |
| 50% | 重构+扩展 |
| 0% | scaffold 新建 |

放弃新建时 MUST 写 `[REUSE-DECISION] 放弃新建 <X>，因为已有 <Y> 覆盖了 <Z>`
