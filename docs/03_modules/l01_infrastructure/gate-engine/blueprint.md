---
module_id: "MOD-INF-007"
title: "Gate Engine 蓝图 — G0-G7任务门禁 + G1-G5 KMS决策门 + 熔断器"
doc_type: blueprint
status: draft
version: "0.3.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-03"
valid_from: "2026-05-03"
ttl: permanent
construction_progress: phase_1_complete
summary: "ZephyrAlpha Gate Engine 蓝图——定义 G0-G7 任务门禁 + G1-G5 KMS 决策门 + GATE-16 蓝图读取合规检查（P1-2强制合规，experimental软合规WARNING + beta硬阻断P0）+ 熔断器 circuit_breaker 的完整架构。GATE-18 pre-commit 硬阻断。脚本 exit code → Gate 判定映射（CT-SCRIPT-GATE-001）。对标 ITIL Change Enablement 门禁 + K8s Admission Controller。"
tags: [gate-engine, gates, g0-g7, g1-g5, circuit-breaker, pre-commit, admission-controller, task-gate, kms-gate, infrastructure]
priority: P0
depends_on:
  - {target: "MOD-MASTER-001", at: "§2.8", why: "CT-SCRIPT-GATE-001 集成契约——脚本exit code→Gate判定"}
  - {target: "MOD-MASTER-001", at: "§4", why: "全局状态传播链——Gate FAIL→Orc BLOCKED 传播"}
  - {target: "MOD-INF-005", at: "§6", why: "脚本系统——Gate判定输入源（脚本exit code）"}
  - {target: "MOD-INF-006", at: "§4", why: "任务系统——Gate判定输出目标（status→BLOCKED）"}
  - {target: "MOD-KB-001", at: "§3.2", why: "知识库——G1-G5 KMS门禁判定对象"}
  - {target: "architecture-model/layers/b_gates.yaml", at: "全篇", why: "Gates YAML SSoT——本蓝图真源"}
---

# Gate Engine 蓝图 — G0-G7任务门禁 + G1-G5 KMS决策门

> **module_id**: MOD-INF-007 | **version**: 0.1.0 | **status**: draft | **layer**: cross_layer

> **真源声明**：本蓝图的 canonical SSoT 为 [b_gates.yaml](file:///D:/ZephyrAlpha/architecture-model/layers/b_gates.yaml)。
> 本蓝图是其人类可读翻译——发现不一致以 YAML 为准。
> 代码落位：`src/zephyr/gates/`（5 个 .py + 5 个门禁 YAML 配置）。

> **对标**：ITIL Change Enablement（变更前评估影响+授权）+ K8s Admission Controller（硬阻断不合规请求）+ 熔断器模式（Michael Nygard "Release It!"）。

---

## 1. 概述与模块定位

### 1.1 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-007 |
| 代码落位 | `src/zephyr/gates/` |
| 运行时平面 | Warm memory（任务触发时加载） |
| 核心职责 | 判定"这个任务/这个KE 能不能过"——决定放行还是阻断 |

### 1.2 核心职能（一句话）

**Gate Engine 是系统的一致性守卫**——它不生产任何内容，只在关键决策点上判断"是否合规"。相当于施工工地的安全员——检查安全帽、检查脚手架、不合格就不准入内。

### 1.3 责任范围

| 管什么 | 不管什么（→ 去哪） |
|------|------|
| G0-G7 任务门禁：任务执行前/后的合规判定 | 门禁判定的具体检测逻辑 → 脚本系统 (MOD-INF-005) |
| G1-G5 KMS 决策门：知识生命周期的阶段性判定 | 知识入库的具体规则 → 知识库 (MOD-KB-001) |
| GATE-18 pre-commit：提交时全量测试收集 | pre-commit 钩子框架 → `.pre-commit-config.yaml` |
| GATE-16 蓝图读取合规检查：AI 改代码前是否读了蓝图（P1-2 强制合规）| experimental 软合规 WARNING — beta 硬阻断 P0 |
| 熔断器 circuit_breaker：异常传播阻断 | 熔断后的修复执行 → Orchestrator (MOD-INF-006) |

---

## 2. 双门禁体系

### 2.1 G0-G7 任务门禁（任务生命周期判定）

```
G0 — 任务准入门禁
  • 触发：任务 DRAFT → QUEUED
  • 检查：TaskCard 必填字段完整？task_id 格式正确？
  • FAIL → 任务留在 DRAFT + 错误提示

G1-G3 — 施工前门禁
  • G1 蓝图合规：目标模块是否有 approved 蓝图？
  • G2 依赖完整：depends_on 依赖的模块实现状态
  • G3 容量检查：当前是否在全局容量预算内？
  • FAIL → status: BLOCKED

G4-G6 — 执行中门禁
  • G4 沙箱合规：sandbox_profile 与 task_type 匹配？
  • G5 模型合规：execution_model 在模型能力矩阵内？
  • G6 安全合规：tool_call 白名单检查？
  • FAIL → 中断执行 + status: FAILED

G7 — 交付前门禁
  • 触发：任务 REVIEWING → COMPLETED
  • 检查：任务关联文件全量审计 exit 0？
  • FAIL → status: BLOCKED（修复后再提交 G7）
```

### 2.2 G1-G5 KMS 决策门（知识生命周期判定）

```
G1 Ingest Gate — 入库门禁
  • 判定：这个内容是否值得进入知识库？
  • 检查：来源可追溯？内容可验证？格式合规？
  • FAIL → 拒绝入库

G2 Triage Gate — 分拣门禁
  • 判定：这个KE应该归档/激活/丢弃？
  • 检查：重复性、时效性、关联性
  • FAIL → 分流到 ARCHIVE 或废弃

G3 Evaluate Gate — 评估门禁
  • 判定：这个KE的质量是否达标？
  • 检查：四模型审计流水线通过？
  • FAIL → 退回修改

G4 Activate Gate — 激活门禁
  • 判定：这个KE是否可以注入Agent上下文？
  • 检查：人工确认 + 新鲜度 + 冲突裁决
  • FAIL → 保持 ANALYZED 状态

G5 Extract Gate — 提取门禁
  • 判定：是否可以从历史KE中提取模式？
  • 检查：≥3 个同类KE存在？模式置信度？
  • FAIL → 等待更多同类KE积累
```

---

## 3. 核心架构

### 3.1 文件组成

| 文件 | 职责 |
|------|------|
| `gate_engine.py` | 核心门禁引擎——加载门禁配置 → 执行判定 → 返回 PASS/FAIL |
| `task_completion_gate.py` | G7 交付前门禁——运行关联文件审计 → 判定 |
| `circuit_breaker.py` | 熔断器——检测异常传播 → 切断故障链路 |
| `contract_template_manager.py` | 契约模板管理——加载 G1-G5 KMS 门禁 YAML 配置 |
| `g1_ingest.yaml` ~ `g5_extract.yaml` | 五个 KMS 门禁的声明式配置（条件+阈值+动作） |

### 3.2 Gate 判定接口

```python
class GateResult:
    gate_id: str          # "G0"~"G7" | "G1"~"G5" (KMS) | "GATE-18"
    status: GateStatus    # PASS | PASS_WITH_WARNINGS | FAIL | CRITICAL_FAIL
    reasons: list[str]    # 失败原因
    affected_tasks: list[str]  # 受影响的任务 ID
    timestamp: datetime
```

### 3.3 熔断器模式

```yaml
circuit_breaker:
  states:
    CLOSED: "正常——请求通过"
    OPEN: "熔断——请求直接拒绝"
    HALF_OPEN: "试探——允许少量请求测试恢复"

  triggers:
    - condition: "连续 FAIL 次数 ≥ threshold"
      threshold: 5
      action: "CLOSED → OPEN"
    - condition: "OPEN 状态持续 ≥ cooldown"
      cooldown: 60s
      action: "OPEN → HALF_OPEN"
    - condition: "HALF_OPEN 试探全部 PASS"
      action: "HALF_OPEN → CLOSED"
```

---

## 四、集成概览（CT-SCRIPT-GATE-001）

> 详见总蓝图 [MOD-MASTER-001 §2.8](file:///D:/ZephyrAlpha/docs/03_modules/_master-blueprint/blueprint.md)。

```
脚本 exit 0 → GATE-n PASS → 任务状态不变
脚本 exit 1 → GATE-n PASS_WITH_WARNINGS → 任务 ⚠️
脚本 exit 2 → GATE-n FAIL → 关联任务 BLOCKED
脚本 exit 3 → GATE-n CRITICAL_FAIL → 全部活跃任务 BLOCKED
```

---
---

## 五、核心流程 — G0-G7 任务门禁结构化规则

> 以下将蓝图 §2 中的自然语言门禁描述升级为**确定性 YAML 规则**——AI agent 可直接消费。
> 每一条 `check` 是布尔表达式（禁止问句），每一条 `on_failure` 有明确的 `fix_hint`。

### 5.1 G0 — 任务准入门禁

```yaml
gate_id: G0
gate_name: task_entry
title: "G0 Task Entry Gate"
description: "任务从DRAFT进入TODO前的合规判定——确保任务卡片字段完整性"
trigger:
  event: "TaskCard.status DRAFT → TODO"
  precondition: "TaskCard.deliverables 非空"
  frequency: per_task
entry_conditions:
  - id: G0-C00
    name: required_fields_present
    type: schema_validation
    check: "task_id matches ^TASK-[0-9]{6}$ AND priority IN {P0,P1,P2,P3} AND assignee IS NOT NULL AND deadline IS NOT NULL"
    severity: error
    on_failure: reject
    fix_hint: "补齐缺失字段后重新提交——task_id格式TASK-NNNNNN，priority默认P2"
    anti_pattern:
      description: "AI创建任务时遗漏priority字段导致门禁拒绝"
      example: "AI直接 assignee='ai-agent' 但未填 priority → G0-C00 FAIL"
  - id: G0-C01
    name: task_type_valid
    type: enumeration
    check: "task_type IN {CODE_GEN, CODE_REVIEW, ANALYSIS, OPS, DOC, TEST, REFACTOR, AUDIT}"
    severity: error
    on_failure: reject
    fix_hint: "从合法枚举中选择task_type"
```

### 5.2 G1-G3 — 施工前门禁

```yaml
gate_id: G1
gate_name: blueprint_compliance
title: "G1 Blueprint Compliance Gate"
trigger:
  event: "TaskCard.status TODO → IN_PROGRESS"
  precondition: "任务关联的目标模块已登记"
entry_conditions:
  - id: G1-C00
    name: module_has_approved_blueprint
    type: registry_lookup
    check: "target_module_id IN MODULE_REGISTRY AND module.blueprint.status == 'approved'"
    severity: error
    on_failure: reject
    fix_hint: "先创建/审批目标模块蓝图后再执行任务"
    anti_pattern:
      description: "AI对未登记模块直接开发——绕过蓝图→产生不可追溯的代码"
      example: "AI创建一个新模块MOD-INF-999但没有先写蓝图→G1-C00 FAIL"

gate_id: G2
gate_name: dependency_complete
title: "G2 Dependency Gate"
entry_conditions:
  - id: G2-C00
    name: depends_on_modules_implemented
    type: dependency_check
    check: "ALL depends_on modules status IN {implemented, active}"
    severity: error
    on_failure: defer
    fix_hint: "等待依赖模块实现完成——进入deferred_queue(≤72h)"

gate_id: G3
gate_name: capacity_check
title: "G3 Capacity Gate"
entry_conditions:
  - id: G3-C00
    name: within_global_token_budget
    type: capacity
    check: "current_token_usage + estimated_task_tokens <= global_capacity_budget"
    severity: warning
    on_failure: defer
    fix_hint: "等待token容量释放或降低任务token估算"
```

### 5.3 G4-G6 — 执行中门禁

```yaml
gate_id: G4
gate_name: sandbox_compliance
title: "G4 Sandbox Compliance Gate"
entry_conditions:
  - id: G4-C00
    name: sandbox_profile_matches_task_type
    type: sandbox
    check: "sandbox_profile.task_type == task.task_type AND sandbox_profile.active == true"
    severity: error
    on_failure: reject
    fix_hint: "选择与task_type匹配的sandbox_profile——或创建新profile"

gate_id: G5
gate_name: model_compliance
title: "G5 Model Compliance Gate"
entry_conditions:
  - id: G5-C00
    name: model_in_capability_matrix
    type: capability
    check: "execution_model IN MODEL_CAPABILITY_MATRIX AND model.supports(task.task_type)"
    severity: error
    on_failure: reject
    fix_hint: "选择能力矩阵中支持此task_type的模型"

gate_id: G6
gate_name: security_compliance
title: "G6 Security Gate"
entry_conditions:
  - id: G6-C00
    name: tool_call_whitelist
    type: security
    check: "ALL requested_tool_calls IN TOOL_CALL_WHITELIST"
    severity: error
    on_failure: reject
    fix_hint: "移除不在白名单内的tool_call——或提交白名单扩展申请"
```

### 5.4 G7 — 交付前门禁

```yaml
gate_id: G7
gate_name: delivery_gate
title: "G7 Delivery Gate"
trigger:
  event: "TaskCard.status REVIEW → COMPLETED"
  precondition: "任务关联文件已修改"
entry_conditions:
  - id: G7-C00
    name: all_associated_scripts_audit_pass
    type: script_execution
    check: "ALL scripts in task.associated_scripts exit_code == 0"
    severity: error
    on_failure: reject
    fix_hint: "运行失败脚本→修复错误→重新触发G7判定"
    anti_pattern:
      description: "AI在脚本exit≠0时强行推进任务到COMPLETED"
      example: "run_all.py exit 2 但AI调用 task.status=COMPLETED → G7-C00 FAIL → 回退到REVIEW"
```

---

## 六、设计决策集中表

| ID | 决策 | 理由 | 被否决替代方案 | 重新评估条件 |
|----|------|------|--------------|------------|
| DD1 | **G0-G7 八门禁而非五或十** | 覆盖任务生命周期DRAFT→COMPLETED的7个状态过渡点+1个准入门 | 五门禁——不足覆盖；十二门禁——过度细粒度 | 新增TaskStatus时重新评估 |
| DD2 | **Validating-only（当前），Mutating为可选** | experimental优先实现硬阻断——自动修正是beta增强 | "所有门禁都提供自动修正"——experimental不可行 | beta引入时评估 |
| DD3 | **熔断器 threshold=5, cooldown=60s** | 连续5次FAIL表明系统性问题——单次FAIL可能是偶发；60s足够短暂恢复 | threshold=3（太敏感）, cooldown=300s（太慢恢复） | 生产环境运行数据收集后 |
| DD4 | **G1-G5 KMS和G0-G7任务门共享同一gate_engine** | 减少引擎碎片化——同一判定接口(GateResult)复用 | "各自独立的门禁引擎"——增加维护负担 | 任务门和KMS门的check_type差异超过50%时 |
| DD5 | **GATE-18 pre-commit独立于G0-G7** | pre-commit是git层守卫（hot路径≤50ms），G0-G7是任务层守卫（warm路径）| "统一为一个门禁列表"——hot/warm混合导致pre-commit过慢 | —无— |
| DD6 | **门禁目录按category而非module_id组织** | 门禁的核心维度的category(6种)——按module_id会1500个目录×2-3个门禁=碎片化 | "每个模块一个门禁目录"——目录树过深，AI遍历成本高 | —无— |

---

## 七、Anti-Patterns — AI agent 绝对禁止的集成行为

> 门控引擎是"AI被约束的地方"——Anti-Patterns比普通模块更重要。

| # | Anti-Pattern | 违反后果 | 正确做法 |
|---|-------------|---------|---------|
| AP1 | **绕过门禁直接修改TaskCard.status** — AI用 `task.status=COMPLETED` 而非通过 `task_repo.transition()` | G0-G7全部门禁被跳过——相当于安全员被支开 | 状态变更必须通过 task_repo.transition() → 自动触发对应门禁 |
| AP2 | **跳过G1-G5 KMS门禁直接写入知识库** — AI直接写 `docs/08_knowledge/ke-*.md` 而不通过activate→extract管道 | 未审查的知识进入AI上下文——可能包含错误/过时/冲突内容 | KE入库必须经过 G1→G2→G3→G4→G5 完整管道 |
| AP3 | **门禁规则留问句** — 写 `check: "TaskCard必填字段完整？"` | AI无法直接执行——需要"猜测"什么算完整 | check必须是布尔表达式：`check: "task_id IS NOT NULL AND priority IS NOT NULL"` |
| AP4 | **熔断器触发后手动override** — AI在circuit_breaker=OPEN时强行reset | 连续故障的系统性问题被掩盖——可能积累成灾难性故障 | OPEN期间只能等待cooldown到期——HALF_OPEN自动试探恢复 |
| AP5 | **创建门禁但不注册** — AI新建YAML但不写入 _registry.yaml | 门禁成为孤儿——引擎无法发现——形式上存在但实际不执行 | 新建门禁 = copy _template.yaml + 写入 _registry.yaml |
| AP6 | **废弃门禁直接删除** — AI `rm g5_extract.yaml` | 历史session回溯时找不到"当时为什么这个门禁存在" | 废弃= `status: deprecated` + 移到 `_deprecated/` ——铁律四 |
| AP7 | **门禁的on_failure只有reject没有fix_hint** | AI被拒绝后不知道"怎么才能通过"——反复重试→无限循环 | 每条reject的entry_condition必须配 fix_hint |

---

## 八、集成契约

### 8.1 CT-SCRIPT-GATE-001：脚本exit code → Gate判定

> 详见总蓝图 [MOD-MASTER-001 · CT-SCRIPT-GATE-001](file:///D:/ZephyrAlpha/docs/03_modules/_master-blueprint/blueprint.md)。

```
脚本 exit 0 → GATE-n PASS → 任务状态不变
脚本 exit 1 → GATE-n PASS_WITH_WARNINGS → 任务 ⚠️
脚本 exit 2 → GATE-n FAIL → 关联任务 BLOCKED
脚本 exit 3 → GATE-n CRITICAL_FAIL → 全部活跃任务 BLOCKED
```

### 8.2 CT-ORC-GATE-001：任务系统 → 门控引擎

> 详见总蓝图 [MOD-MASTER-001 · CT-ORC-GATE-001](file:///D:/ZephyrAlpha/docs/03_modules/_master-blueprint/blueprint.md)。
> 核心：TaskCard完整28字段 → G0-G7门禁判定 → PASS/FAIL → TaskCard.status迁移。

---

## 九、风险与缓解

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|:---:|:---:|------|
| R1 | **门禁过度阻断** — 过于严格的门禁导致合法任务被拒绝 | 中 | 高 | severity=error仅用于不可逆损失——可逆问题用warning |
| R2 | **门禁规则漂移** — YAML中的check与代码实际检查逻辑不一致 | 高 | 高 | CI门禁 validate_gate_yaml.py → 交叉校验YAML vs gate_engine代码 |
| R3 | **熔断器误触发** — 正常流量波动被判定为异常 | 低 | 中 | threshold=5（足够容纳偶发失败）+ cooldown=60s（快速恢复） |
| R4 | **门禁目录碎片化** — 1500模块后每个模块各自的gates子目录管理混乱 | 中 | 高 | 统一_category分类（6种）→ module专属门禁放入 modules/<MOD-XXX>/ |

---

## 十、施工/演进指南

> 门控引擎已有15个文件实现(construction_progress=phase_1_complete)——本章是**修改和演进指南**，非新建指南。

### 10.1 添加新门禁的标准流程

```
1. cp src/zephyr/gates/_template.yaml → src/zephyr/gates/<category>/<new_gate>.yaml
2. 按 _template.yaml 的11节填写全部字段（check必须是布尔表达式）
3. 写入 _registry.yaml 的 gates 列表
4. 在 gate_engine.py 的 _GATE_FILES 映射中添加
5. 写 tests/unit/test_<new_gate>.py ——至少覆盖每条 entry_condition 的 PASS/FAIL 两路径
6. 运行 validate_gate_discipline.py → 确认注册一致
```

### 10.2 修改现有门禁规则

```
1. 修改 YAML 中的 entry_conditions
2. bump change_log.version
3. 重新运行相关 test_<gate>.py
4. CI校验 validate_gate_yaml.py 自动触发
```

### 10.3 门禁模板本身升级流程

```
1. 修改 _template.yaml → bump schema_version
2. 归档当前模板 → _template_v{N}.yaml（铁律四——不删除）
3. 在 gate-engine blueprint 变更记录中登记
4. 通知所有门禁维护者评估是否需要迁移
```

---
---

## 十一、施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| scaffold | gate_engine.py + 5个KMS门禁YAML | ✅ implemented |
| experimental | G0-G7 完整判定逻辑 + CT-SCRIPT-GATE-001 落地 | 📋 Backlog |
| beta | 熔断器全链路测试 + CI门禁自动交叉校验 | 📋 Backlog |

---

## 十二、已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 门禁引擎——gate_engine.py+5个KMS YAML门禁已实现

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/gates/circuit_breaker.py` | ✅ 已实现 | |
| `src/zephyr/gates/contract_template_manager.py` | ✅ 已实现 | |
| `src/zephyr/gates/g1_ingest.yaml` | ✅ 已实现 | |
| `src/zephyr/gates/g2_triage.yaml` | ✅ 已实现 | |
| `src/zephyr/gates/g3_evaluate.yaml` | ✅ 已实现 | |
| `src/zephyr/gates/g4_activate.yaml` | ✅ 已实现 | |
| `src/zephyr/gates/g5_extract.yaml` | ✅ 已实现 | |
| `src/zephyr/gates/gate_engine.py` | ✅ 已实现 | |
| `src/zephyr/gates/task_completion_gate.py` | ✅ 已实现 | |

### 6.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/unit/test_gate_engine.py` | ✅ 已实现 | |
| `tests/unit/test_task_completion_gate.py` | ✅ 已实现 | |
| `tests/unit/test_circuit_breaker.py` | ✅ 已实现 | |
| `tests/unit/test_contract_template_manager.py` | ✅ 已实现 | |
| `tests/integration/test_gate_e2e.py` | ✅ 已实现 | |

### 6.4 治理脚本

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `scripts/governance/d6_security/validate_gate_discipline.py` | ✅ 已实现 | |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

## 4. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 门禁引擎——gate_engine.py+5个KMS YAML门禁已实现

### 4.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/gates/_registry.yaml` | ✅ 已实现 | |
| `src/zephyr/gates/_template.yaml` | ✅ 已实现 | |
| `src/zephyr/gates/admission/mad_001_architecture_necessity.yaml` | ✅ 已实现 | |
| `src/zephyr/gates/admission/mad_002_phase_relevance.yaml` | ✅ 已实现 | |
| `src/zephyr/gates/admission/mad_003_dependency_compliance.yaml` | ✅ 已实现 | |
| `src/zephyr/gates/admission/mad_004_interface_definability.yaml` | ✅ 已实现 | |
| `src/zephyr/gates/ai_capability_guard.py` | ✅ 已实现 | |
| `src/zephyr/gates/circuit_breaker.py` | ✅ 已实现 | |
| `src/zephyr/gates/contract_template_manager.py` | ✅ 已实现 | |
| `src/zephyr/gates/g1_ingest.yaml` | ✅ 已实现 | |
| `src/zephyr/gates/g2_triage.yaml` | ✅ 已实现 | |
| `src/zephyr/gates/g3_evaluate.yaml` | ✅ 已实现 | |
| `src/zephyr/gates/g4_activate.yaml` | ✅ 已实现 | |
| `src/zephyr/gates/g5_extract.yaml` | ✅ 已实现 | |
| `src/zephyr/gates/g6_blueprint_compliance.yaml` | ✅ 已实现 | beta 硬合规——G6 蓝图读取合规门禁 |
| `src/zephyr/gates/g6_ctr_compliance.yaml` | ✅ 已实现 | |
| `src/zephyr/gates/gate_engine.py` | ✅ 已实现 | |
| `src/zephyr/gates/task/g0_entry.yaml` | ✅ 已实现 | |
| `src/zephyr/gates/task_completion_gate.py` | ✅ 已实现 | |

### 4.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/unit/test_gate_engine.py` | ✅ 已实现 | |
| `tests/unit/test_task_completion_gate.py` | ✅ 已实现 | |
| `tests/unit/test_circuit_breaker.py` | ✅ 已实现 | |
| `tests/unit/test_contract_template_manager.py` | ✅ 已实现 | |
| `tests/integration/test_gate_e2e.py` | ✅ 已实现 | |

### 4.3 治理脚本

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `scripts/governance/d6_security/validate_gate_discipline.py` | ✅ 已实现 | |

### 4.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §4（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

## 十三、依赖关系（结构化）

| 依赖目标 | 关系类型 | 为什么 |
|------|:--:|------|
| MOD-INF-006 (Task System) | runtime_call | 读取 TaskCard 28字段 → G0-G7 判定 |
| MOD-INF-005 (Script System) | runtime_call | 脚本 exit code → GATE-n PASS/FAIL (CT-SCRIPT-GATE-001) |
| MOD-KB-001 (Knowledge Base) | data_flow | KE → G1-G5 KMS 门禁管道 |
| MOD-INF-008 (Context Engine) | config_consume | blueprint_routing.yaml 上下文范围 |
| MOD-INF-014 (LLM Security) | sibling_check | fail-closed 模式双门禁互校验 |
| MOD-INF-015 (Telemetry) | emit_to | GATE-16 blueprint_read_check → BLUEPRINT-READ-FREQ SLI |
| `architecture-model/layers/b_gates.yaml` | ssoT | Gates YAML canonical source |

## 十四、产出物存放目录

| 产出物 | 路径 |
|------|------|
| 门禁引擎代码 | `src/zephyr/gates/gate_engine.py` |
| 门禁 YAML 配置 | `src/zephyr/gates/g1_ingest.yaml` ~ `g6_blueprint_compliance.yaml` |
| 熔断器 | `src/zephyr/gates/circuit_breaker.py` |
| 门禁测试 | `tests/unit/test_gate_engine.py` 等 5 文件 |
| 门禁治理脚本 | `scripts/governance/d6_security/validate_gate_discipline.py` |
| 门禁注册表 | `src/zephyr/gates/_registry.yaml` |
| 门禁模板 | `src/zephyr/gates/_template.yaml` |

## 十五、集成目标

| 集成目标 | 状态 | 验证方式 |
|------|:--:|------|
| G6 硬合规阻断 P0 | ✅ 已实现 | `session_simulator.py` beta 验证 |
| G0-G7 全部 8 门禁 YAML 规则化 | ✅ 已实现 | G5 YAML §5.1-§5.4 |
| CT-SCRIPT-GATE-001 落地 | 📋 Backlog | 脚本 exit code → Gate 判定链路 |
| CT-ORC-GATE-001 落地 | 📋 Backlog | TaskCard.status transition → Gate 触发 |
| 熔断器全链路测试 | 📋 Backlog | OPEN→HALF_OPEN→CLOSED 循环 |

## 十六、需要更新的相关内容

当本蓝图变更时，同步更新：
1. `docs/03_modules/blueprint-registry.yaml` — 版本号和完整度
2. `config/blueprint_routing.yaml` — R009 路由项 keywords/path_patterns
3. `src/zephyr/mcp/gate_engine_server.py` — MCP 工具描述引用本蓝图
4. `src/zephyr/mcp/blueprint_search_server.py` — 若 keyword 变更
5. `docs/03_modules/_master-blueprint/blueprint.md` — MOD-MASTER-001 §2.8 CT-SCRIPT-GATE-001

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-03 | 0.1.0 | 初始创建——从 b_gates.yaml SSoT 派生。双门禁体系（G0-G7+G1-G5）+ 熔断器模式 + CT-SCRIPT-GATE-001 集成。 |
| 2026-05-04 | 0.2.0 | 黄金标准补齐：(1)修正 construction_progress not_started→phase_1_complete（15个文件已实现）；(2)新增§五 核心流程——G0-G7从自然语言升级为确定性YAML规则；(3)新增§六 设计决策集中表——6条关键决策；(4)新增§七 Anti-Patterns——7条门禁场景绝对禁止行为；(5)新增§八 集成契约——CT-SCRIPT-GATE-001+CT-ORC-GATE-001；(6)新增§九 风险与缓解；(7)新增§十 施工/演进指南——添加/修改/升级三级流程；(8)同步创建 _template.yaml(门禁标准模板)+_registry.yaml(全部门禁注册表)。 |
| 2026-05-04 | 0.2.1 | P1-2强制合规 GATE-16 蓝图读取合规检查落地——gate_engine.py 新增第 18 种 CheckType `blueprint_read_check`（含 `_check_blueprint_read_compliance` helper，读取 `data/telemetry/blueprint_reads.jsonl` 验证 AI 是否在改代码前读了对应蓝图）；experimental 软合规 WARNING（不阻断），beta 升级为硬阻断 P0。关联模块：MOD-INF-015 Telemetry（BLUEPRINT-READ-FREQ SLI）+ MOD-INF-009 Pipeline（触发路由表）。关联决策：R92。 |
