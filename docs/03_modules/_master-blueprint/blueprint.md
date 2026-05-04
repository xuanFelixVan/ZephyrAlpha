---
module_id: "MOD-MASTER-001"
title: "集成闭环总蓝图 — 任务系统·脚本系统·知识库及全部基础设施系统的集成契约与数据流"
doc_type: blueprint
status: draft
version: "0.3.1"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-03"
valid_from: "2026-05-03"
ttl: permanent
summary: "ZephyrAlpha 集成闭环总蓝图——定义12个基础设施系统之间的集成契约、数据流向、共享Schema、触发器路由、全局状态传播链、容量预算、故障传播约定。本蓝图是集成关系的 canonical SSoT：每个系统对的接口契约在此定义（YAML结构化），各模块蓝图仅引用本蓝图的契约编号。对标 K8s Cluster Architecture + TOGAF Architecture Vision + OpenAPI Root Spec + Terraform Root Module + Cursor Rules + Windsurf Rules + Anthropic Agent Architecture。"
construction_progress: not_started
ai_role_instruction: >
  你是集成总蓝图(MOD-MASTER-001)，是ZephyrAlpha全部12个基础设施系统之间集成关系的canonical SSoT。
  当子系统A的AI agent需要调用子系统B时，你必须提供 CT-{A}-{B} 编号的契约定义。
  核心规则：(1)不存在"模糊集成"——所有跨系统调用必须在此登记CT-*编号；
  (2)模块蓝图定义"内部怎么干"，你定义"之间怎么连"；(3)模块蓝图与你不一致时，以你为准（详见§十二冲突裁决）；
  (4)你不会生成代码——你只定义契约，实现由各模块蓝图指引；(5)新AI session先读§零——按分派表定位自己需要的部分。
tags: [master-blueprint, integration-contracts, closed-loop, task-system, script-system, knowledge-base, gates, context-engine, pipeline, feedback-loop, vector-memory, database, mcp, llm-security, telemetry, infrastructure, ssoT, cross-system]
priority: P0
depends_on:
  - {target: "MOD-INF-005", at: "全篇", why: "脚本系统蓝图——本总蓝图定义脚本系统与任务系统/知识库的集成契约"}
  - {target: "MOD-INF-006", at: "全篇", why: "任务系统蓝图——本总蓝图定义任务系统与脚本系统/CE/FLE的集成契约"}
  - {target: "MOD-KB-001", at: "全篇", why: "知识库蓝图——本总蓝图定义知识库与CE/VMS/脚本系统的集成契约"}
  - {target: "architecture-model/layers/b_gates.yaml", at: "全篇", why: "Gates YAML SSoT——契约CT-GATE-*的真源"}
  - {target: "architecture-model/layers/b_context_engine.yaml", at: "全篇", why: "CE YAML SSoT——契约CT-CE-*的真源"}
  - {target: "architecture-model/layers/b_pipeline.yaml", at: "全篇", why: "Pipeline YAML SSoT——契约CT-PIPE-*的真源"}
  - {target: "architecture-model/layers/b_feedback_loop.yaml", at: "全篇", why: "FLE YAML SSoT——契约CT-FLE-*的真源"}
  - {target: "architecture-model/layers/b_vector_memory.yaml", at: "全篇", why: "VMS YAML SSoT——契约CT-VMS-*的真源"}
  - {target: "architecture-model/layers/b_db.yaml", at: "全篇", why: "DB YAML SSoT——契约CT-DB-*的真源"}
  - {target: "architecture-model/layers/b_mcp.yaml", at: "全篇", why: "MCP YAML SSoT——契约CT-MCP-*的真源"}
  - {target: "architecture-model/layers/b_llm_security.yaml", at: "全篇", why: "LSG YAML SSoT——契约CT-LSG-*的真源"}
  - {target: "architecture-model/layers/l12_system_telemetry.yaml", at: "全篇", why: "Telemetry YAML SSoT——契约CT-TELE-*的真源"}
  - {target: "architecture-model/layers/b_core.yaml", at: "全篇", why: "Core YAML SSoT"}
  - {target: "architecture-model/layers/b_shared.yaml", at: "全篇", why: "Shared YAML SSoT"}
  - {target: "architecture-model/layers/b_orchestrator.yaml", at: "全篇", why: "Orchestrator YAML SSoT——边界定义"}
  - {target: "PS-STD-001", at: "§7", why: "TaskCard 28字段模型——共享Schema真源"}
  - {target: "GOV-DOC-002", at: "§一~§二", why: "LPC双轨——B轨/C轨目录定位"}
---

# 集成闭环总蓝图 — 任务系统·脚本系统·知识库及全部基础设施系统

> **module_id**: MOD-MASTER-001 | **version**: 0.3.0 | **status**: draft | **layer**: cross_layer

> **真源声明**：本蓝图是 ZephyrAlpha 全部基础设施系统之间集成关系的 canonical SSoT。
> 各模块蓝图（MOD-INF-005/006、MOD-KB-001、以及即将创建的 Gates/CE/Pipeline/FLE/VMS/db/MCP/LSG/Telemetry 蓝图）引用本蓝图中的集成契约编号——
> 模块蓝图定义"内部怎么干"，本蓝图定义"之间怎么连"。
>
> **对标**：K8s Cluster Architecture（组件间通信协议）+ TOGAF Architecture Vision（跨域集成视图）+
> OpenAPI Root Spec（$ref 引用体系）+ Terraform Root Module（子模块调用契约）+
> Cursor Rules（AI可执行规则+Token预算+Anti-Patterns）+ Windsurf Rules（规则所有权+冲突裁决）+
> Anthropic Agent Architecture（端到端场景走查+冷启动分派）。

---
---

## 零、AI Agent 分派与阅读指南

> 氛围编程社区的核心教条：**文档的首要价值是让 AI 最快找到自己需要的部分。**
> 本蓝图 1330+ 行 —— 不读全文，按需定位。

### 0.1 Token 预算

| 阅读深度 | 读什么 | Token 消耗 | 适用场景 |
|:---:|------|:---:|------|
| 🔥 紧急 | `ai_role_instruction` + 拓扑图 + 合同总表 + 你系统的分派行 | ~500 | 新 AI session 冷启动 |
| 📋 标准 | 紧急 + 你负责系统的全部 CT-* 合同 | ~1500 | 开发跨系统功能 |
| 📚 完整 | 全文 | ~8000 | 架构审查 / 新系统接入 |

**新 AI session 默认从 🔥 紧急开始，按任务需求升级。**

### 0.2 AI Agent 分派表 —— 你该读蓝图的哪部分

| 如果你负责开发... | 你该读的 CT-* 合同 | 关联 Schema | 预计 tokens |
|------------------|-------------------|------------|:---:|
| **Orchestrator** (任务系统) | CT-ORC-SCRIPT, CT-ORC-CE, CT-ORC-VMS, CT-ORC-GATE | TaskCard, Finding | ~1500 |
| **Script System** (脚本系统) | CT-ORC-SCRIPT, CT-SCRIPT-KB, CT-SCRIPT-GATE | Finding, KE | ~1200 |
| **Knowledge Base** (知识库) | CT-SCRIPT-KB, CT-KB-VMS | KE | ~800 |
| **Context Engine** (CE) | CT-ORC-CE, CT-CE-VMS, CT-CE-LSG | TaskCard | ~1000 |
| **Gate Engine** (门控引擎) | CT-ORC-GATE, CT-SCRIPT-GATE | TaskCard | ~600 |
| **Feedback Loop** (FLE) | CT-FLE-ORC, CT-FLE-DB, CT-TELE-FLE | — | ~900 |
| **Pipeline** | CT-PIPE-ORC | TaskCard | ~300 |
| **Vector Memory** (VMS) | CT-ORC-VMS, CT-CE-VMS, CT-KB-VMS | — | ~600 |
| **Database** (db) | CT-FLE-DB | — | ~300 |
| **LLM Security** (LSG) | CT-CE-LSG | — | ~400 |
| **MCP Servers** | —（无专属 CT-*，消费所有系统） | — | ~200 |
| **System Telemetry** | CT-TELE-FLE | — | ~200 |

---
---

## 一、系统全景：12 个系统的拓扑与职责边界

### 1.1 系统清单

| 系统 | 代码落位 | 模块蓝图 | 核心职责（一句话） |
|------|------|:---:|------|
| **Agent Orchestrator (Orc)** | `src/zephyr/orchestrator/` | MOD-INF-006 任务系统蓝图 | 任务生命周期管理 + Agent 调度 + 沙箱执行 |
| **Script System** | `src/zephyr/l01_infrastructure/script_system/` + `scripts/governance/` | MOD-INF-005 脚本系统蓝图 | 12维度治理审计 + pre-commit门禁 + Finding管理 |
| **Knowledge Base (KB)** | `src/zephyr/kb/` | MOD-KB-001 知识库蓝图 | 知识全生命周期（G1→G5）+ KE管理 + ChromaDB |
| **Gate Engine (Gates)** | `src/zephyr/gates/` | MOD-INF-007 gate-engine蓝图 | G0-G7任务门禁 + G1-G5 KMS门禁 + 准入判定 |
| **Context Engine (CE)** | `src/zephyr/context_engine/` | MOD-INF-008 context-engine蓝图 | build→compress→validate→inject 四阶段上下文注入 |
| **Task Pipeline** | `src/zephyr/pipeline/` | MOD-INF-009 pipeline蓝图 | M1-M11双管线路由——决定任务用什么模型执行 |
| **Feedback Loop Engine (FLE)** | `src/zephyr/feedback_loop/` | MOD-INF-010 feedback-loop蓝图 | 指标采集→异常检测→调度改进——自我改进闭环 |
| **Vector Memory Service (VMS)** | `src/zephyr/vector_memory/` | MOD-INF-011 vector-memory蓝图 | ChromaDB 5 Collection 统一向量持久化 |
| **Database (db)** | `src/zephyr/db/` | MOD-INF-012 database蓝图 | SQLite元数据 + ATM原子事务管理器 |
| **MCP Servers** | `src/zephyr/mcp/` | MOD-INF-013 mcp-servers蓝图 | stdio协议——向外部IDE/Agent暴露系统能力 |
| **LLM Security Gateway (LSG)** | `src/zephyr/llm_security/` | MOD-INF-014 llm-security蓝图 | 四层安全防御——输入/输出/上下文/工具调用校验 |
| **System Telemetry (l12)** | `src/zephyr/l12_system_telemetry/` | MOD-INF-015 telemetry蓝图 | metrics/logs/traces/ai_behavior 全系统可观测性 |

### 1.2 拓扑关系图

```
                          ┌──────────────────────────────────────┐
                          │        System Telemetry (l12)         │ ← 所有系统写入
                          └────────────────┬─────────────────────┘
                                           │ metrics / logs
                          ┌────────────────▼─────────────────────┐
                          │     Feedback Loop Engine (FLE)        │
                          │  collect → detect → dispatch          │
                          └───┬──────────────┬───────────────────┘
                              │ dispatch     │ dispatch
              ┌───────────────┼──────────────┼───────────────┐
              │               │              │               │
    ┌─────────▼──────┐  ┌─────▼──────┐  ┌───▼──────────┐  ┌─▼──────────────┐
    │  Orchestrator  │  │   Gates    │  │  Pipeline    │  │  Context Engine│
    │   (任务系统)    │  │ (门禁引擎)  │  │  (管线)      │  │    (CE)        │
    └───┬───┬───┬────┘  └─────┬──────┘  └──┬──┬──┬─────┘  └──┬──┬──┬───────┘
        │   │   │             │            │  │  │           │  │  │
        │   │   │    ┌────────┘            │  │  │  ┌────────┘  │  │
        │   │   │    │  ┌──────────────────┘  │  │  │  ┌────────┘  │
        │   │   │    │  │  ┌──────────────────┘  │  │  │  ┌────────┘
        ▼   ▼   ▼    ▼  ▼  ▼                    ▼  ▼  ▼  ▼
  ┌───────────────────────────────────────────────────────────────┐
  │              Script System (脚本系统)                          │
  │   D1-D12 12维度 × C1-C5 五阶段                                  │
  └──────────────────────────┬────────────────────────────────────┘
                             │ MEDIUM Finding → KE
                    ┌────────▼────────┐
                    │  Knowledge Base │
                    │   (知识库)       │
                    └────────┬────────┘
                             │ vector search
                    ┌────────▼────────┐
                    │  Vector Memory  │
                    │     (VMS)       │
                    └────────┬────────┘
                             │ persistence
                    ┌────────▼────────┐
                    │    Database     │
                    │     (db)        │
                    └─────────────────┘

       ┌────────────────────────────────────────────┐
       │              MCP Servers                   │ ← 外部接口
       │  task_manager / knowledge_base / gate_engine│
       └────────────────────────────────────────────┘

       ┌────────────────────────────────────────────┐
       │        LLM Security Gateway (LSG)          │ ← 安全外衣
       │     Orc工具调用 / CE上下文注入 → LSG校验    │
       └────────────────────────────────────────────┘
```

---

## 二、集成契约登记表（Integration Contract Registry）

> 这是本蓝图的最核心章节。每条契约 YAML 结构化，AI 可直接消费——零推理。

### 2.1 契约总表

| 契约编号 | 生产方 → 消费方 | 契约类型 | 当前实现状态 |
|------|------|:---:|:---:|
| CT-ORC-SCRIPT-001 | Orc → Script System | 任务阻塞 + Finding→任务卡 | 部分实现 |
| CT-ORC-CE-001 | Orc → CE | 上下文构建请求 | 骨架 |
| CT-ORC-VMS-001 | Orc → VMS | 任务输出写入向量库 | 骨架 |
| CT-ORC-GATE-001 | Orc → Gates | 任务执行前/后门禁判定 | 部分实现 |
| CT-SCRIPT-KB-001 | Script System → KB | MEDIUM Finding → KE入库 | 蓝图已定义 |
| CT-SCRIPT-GATE-001 | Script System → Gates | 脚本exit code → GATE-n判定 | 部分实现 |
| CT-CE-VMS-001 | CE → VMS | 知识向量检索 | 规划 |
| CT-CE-LSG-001 | CE → LSG | 上下文注入前安全校验 | 规划 |
| CT-KB-VMS-001 | KB → VMS | 知识条目向量化存储 | beta |
| CT-FLE-ORC-001 | FLE → Orc | 异常检测→任务调度调整 | 规划 |
| CT-FLE-DB-001 | FLE → db | 指标时序写入 | 规划 |
| CT-TELE-FLE-001 | Telemetry → FLE | 全系统指标推送 | 规划 |
| CT-PIPE-ORC-001 | Pipeline → Orc | 任务→管线节点路由 | 部分实现 |

### 2.2 CT-ORC-SCRIPT-001：任务系统 ↔ 脚本系统

```yaml
contract: CT-ORC-SCRIPT-001
title: "任务阻塞 + Finding → 任务卡自动创建"
systems:
  - role: producer
    name: script_system
    path: "scripts/governance/"
    blueprint: "MOD-INF-005"
  - role: consumer
    name: orchestrator
    path: "src/zephyr/orchestrator/"
    blueprint: "MOD-INF-006"

data_flow:
  direction: bidirectional
  script_to_orc:
    trigger: "脚本 exit 2 或 exit 3"
    payload: "FindingCollection { findings[], summary }"
    action: "Orc 将关联任务 status → BLOCKED"
    recovery: "脚本重跑 exit 0 → Orc 将关联任务 status → TODO"
  orc_to_script:
    trigger: "Finding.severity ∈ {CRITICAL, HIGH}"
    payload: "TaskCard { task_id, task_type: OPS, priority: P0/P1 }"
    action: "Script System 自动创建 OPS-{SEQ} 格式追踪任务卡"
    task_id_format: "OPS-{SEQ}"

state_propagation:
  - event: "script.exit_2"
    propagation:
      - target: "orchestrator.active_tasks"
        action: "status → BLOCKED"
        scope: "仅关联任务"
  - event: "script.exit_3"
    propagation:
      - target: "orchestrator.all_active_tasks"
        action: "status → BLOCKED"
        scope: "全部活跃任务（门禁自身故障 = 系统不可信）"
  - event: "finding.created{severity:CRITICAL|HIGH}"
    propagation:
      - target: "orchestrator.task_queue"
        action: "创建 OPS-{SEQ} 修复任务"
        task_fields:
          task_type: "OPS"
          priority: "P0 if CRITICAL else P1"
          parent_finding_id: "{finding.id}"

sla:
  CRITICAL_finding_response: "24h 内创建修复任务"
  HIGH_finding_response: "72h 内创建修复任务"
  gate_crash_recovery: "立即阻断所有活跃任务 + 通知 Owner"
```

### 2.3 CT-ORC-CE-001：Orchestrator ↔ Context Engine

```yaml
contract: CT-ORC-CE-001
title: "任务启动时上下文构建请求"
systems:
  - role: consumer
    name: context_engine
    path: "src/zephyr/context_engine/"
    blueprint: "MOD-INF-008"
  - role: producer
    name: orchestrator
    path: "src/zephyr/orchestrator/"
    blueprint: "MOD-INF-006"

interaction:
  trigger: "Orc.create_session(task_id)"
  sequence:
    step_1:
      actor: Orc
      action: "发送 session_context_request → CE"
      payload:
        task_id: "string"
        task_type: "enum[MODEL_BUILD, AUDIT, DOC_WRITE, REFACTOR]"
        target_layer: "string"
        related_files: "list[Path]"
    step_2:
      actor: CE
      action: "build: 从VMS拉取相关KE + 规则 + 蓝图"
      input: "session_context_request"
      output: "raw_context { ke_list[], rules[], blueprints[] }"
    step_3:
      actor: CE
      action: "compress: Token预算内压缩 → priority排序"
      input: "raw_context + token_budget"
      output: "compressed_context"
    step_4:
      actor: CE
      action: "validate: 通过LSG安全校验"
      input: "compressed_context"
      output: "validated_context or REJECTED"
    step_5:
      actor: CE
      action: "inject: 返回最终上下文给Orc"
      output: "injection_result { context_str, token_count, sources[] }"

token_budget:
  total_per_session: 8000
  breakdown:
    ke_entries: "0-3000 (动态)"
    rules_policies: "0-2000"
    blueprints: "0-2000"
    runtime_logs: "0-1000"

error_handling:
  VMS_unavailable: "CE → 降级为仅注入AGENTS.md + 当前模块蓝图 → 标记 session.degraded=true"
  LSG_reject: "CE → 移除被拒绝块 → 重新compress → 再送LSG → 3次仍失败 → 注入失败标记"
  timeout: "CE 10s 超时 → 降级注入 → 记录CE_timeout metric"
```

### 2.4 CT-SCRIPT-KB-001：脚本系统 ↔ 知识库

```yaml
contract: CT-SCRIPT-KB-001
title: "脚本 Finding → 知识条目入库"
systems:
  - role: producer
    name: script_system
    path: "scripts/governance/"
    blueprint: "MOD-INF-005"
  - role: consumer
    name: knowledge_base
    path: "src/zephyr/kb/"
    blueprint: "MOD-KB-001"

data_flow:
  direction: "script → KB"
  mapping:
    - finding_severity: "MEDIUM"
      action: "自动创建 KE 草稿 → G1 Ingest → G2 Triage"
      ke_template: |
        title: "{finding.dimension}: {finding.message[:80]}"
        domain: "governance"
        tags: ["auto-generated", "{finding.dimension}", "finding-to-ke"]
        source_finding_id: "{finding.id}"
    - finding_severity: "CRITICAL|HIGH"
      action: "不自动创建KE——CRITICAL/HIGH 走任务卡流程（CT-ORC-SCRIPT-001）"
    - finding_severity: "LOW|INFO"
      action: "不入KB——仅记录到审计日志"
    - phase_C5_knowledge: |
        脚本系统 C5 知识沉淀阶段:
        CRITICAL/HIGH Finding 修复完成 → 提取经验教训 → G3 Analyze →
        人工确认后 → G4 Activate → KE 进入活跃知识库

quality_gate:
  - auto_generated_KE 必须经过 G2 Triage 人工确认 → 不得自动 G4 Activate
  - KE 来源字段标注 `source: "script_system_C4"`
```

### 2.5 CT-FLE-ORC-001：FLE ↔ Orchestrator

```yaml
contract: CT-FLE-ORC-001
title: "异常检测 → 任务调度调整 + 告警"
systems:
  - role: producer
    name: feedback_loop
    path: "src/zephyr/feedback_loop/"
    blueprint: "MOD-INF-010"
  - role: consumer
    name: orchestrator
    path: "src/zephyr/orchestrator/"
    blueprint: "MOD-INF-006"

interaction:
  trigger_1: "FLE.collect_metric → 周期性轮询（30s）"
  trigger_2: "FLE.detect_anomaly → 指标偏离基线 > 阈值"
  trigger_3: "FLE.dispatch_action → 生成改进指令"

action_types:
  ESCALATE:
    condition: "任务失败率 3x > 基线"
    action: "FLE → Orc.raise_alert → GPT-5.2 发送 Owner 飞书通知"
    severity: "P0_immediate"
  REPAIR:
    condition: "特定维度脚本持续 exit 2"
    action: "FLE → Orc.create_task(OPS-{SEQ}, task_type=AUTO_FIX)"
    severity: "P1_24h"
  NOTIFY_OWNER:
    condition: "幻觉检测 D12 exit 2 连续3次"
    action: "FLE → Orc.flag_for_owner_review → 暂停该维度Agent调度"
    severity: "P0_immediate"
  ADJUST_GATE:
    condition: "门禁假阳性率 > 5%（连续一周）"
    action: "FLE → Orc.adjust_gate_threshold(gate_id, new_threshold)"
    severity: "P2_72h"
    constraint: "阈值调整必须人工确认——FLE建议，Owner裁决"

data_models:
  ActionDispatch:
    action_id: "FLE-ACTION-{SEQ}"
    action_type: "enum[ESCALATE, REPAIR, NOTIFY_OWNER, ADJUST_GATE]"
    target_system: "orchestrator"
    payload: "dict (action_type对应的参数)"
    priority: "enum[P0_immediate, P1_24h, P2_72h]"
    created_at: "ISO8601"

  FeedbackReceipt:
    receipt_id: "string"
    status: "enum[ACKNOWLEDGED, REJECTED, EXECUTING, COMPLETED]"
    orchestrator_note: "string (可选——Orc的附加说明)"

retry_policy:
  max_retries: 3
  retry_interval: "5s"
  fallback: "写入 db.emergency_log + 通知 GPT-5.2 发送告警"
```

### 2.6 CT-CE-VMS-001：CE ↔ VMS

```yaml
contract: CT-CE-VMS-001
title: "上下文构建 → 向量检索"
systems:
  - role: consumer
    name: context_engine
    path: "src/zephyr/context_engine/"
    blueprint: "MOD-INF-008"
  - role: provider
    name: vector_memory
    path: "src/zephyr/vector_memory/"
    blueprint: "MOD-INF-011"

interaction:
  query:
    method: "VMS.search(collection, query_embedding, top_k, filter)"
    collections:
      - name: "ke_entries"
        query: "task_type + target_layer → 语义相似KE"
        top_k: 5
      - name: "vibe_rules"
        query: "task_type → 相关治理规则"
        top_k: 3
      - name: "blueprints"
        query: "target_layer + related_files → 相关蓝图"
        top_k: 2
      - name: "failure_patterns"
        query: "task_type → 历史失败模式"
        top_k: 3

embedding:
  model: "BGE-M3 (ONNX本地推理)"
  dimension: 1024
  batch_size: 16

error_handling:
  VMS_unavailable: "CE降级——不注入向量检索结果 → AGENTS.md + 硬编码规则"
  embedding_failure: "CE跳过该collection → 记录 warning"
```

### 2.7 CT-PIPE-ORC-001：Pipeline ↔ Orchestrator

```yaml
contract: CT-PIPE-ORC-001
title: "任务 → 管线节点路由"
systems:
  - role: router
    name: pipeline
    path: "src/zephyr/pipeline/"
    blueprint: "MOD-INF-009"
  - role: consumer
    name: orchestrator
    path: "src/zephyr/orchestrator/"
    blueprint: "MOD-INF-006"

routing:
  input: "TaskCard { task_type, priority, target_layer, estimated_complexity }"
  output: "PipelineNode { node_id: M1-M11, execution_model, sandbox_profile, gate_profile }"

  decision_tree: |
    if task_type == MODEL_BUILD:
      if estimated_complexity == HIGH → M1 (Opus 4.5, full sandbox)
      else → M2 (GPT-5.2, standard sandbox)
    if task_type == AUDIT:
      if priority == P0 → M3 (Opus 4.5 复审, audit sandbox)
      else → M4 (Claude 4.5 Sonnet, audit sandbox)
    if task_type ∈ {DOC_WRITE, REFACTOR}:
      if target_layer ∈ {L00,L01,L10} → M5 (GPT-5.2, full sandbox)
      else → M6 (Claude 4.5 Sonnet, standard sandbox)

pipeline_output:
  node_id: "M1-M11"
  execution_model: "enum[opus-4.5, gpt-5.2, claude-4.5-sonnet, claude-4.5-haiku, gemini-3.0-pro, qwen-3-max, glm-5.1]"
  sandbox_profile: "enum[full, standard, audit, restricted]"
  gate_profile: "enum[full_g0_g7, pre_commit_only, post_exec_only, none]"
```

### 2.8 CT-SCRIPT-GATE-001：脚本系统 ↔ Gates

```yaml
contract: CT-SCRIPT-GATE-001
title: "脚本exit code → Gate判定"
systems:
  - role: producer
    name: script_system
    path: "scripts/governance/"
    blueprint: "MOD-INF-005"
  - role: consumer
    name: gate_engine
    path: "src/zephyr/gates/"
    blueprint: "MOD-INF-007"

mapping:
  script_exit_0: "GATE-n → PASS → 任务状态不变"
  script_exit_1: "GATE-n → PASS_WITH_WARNINGS → 任务状态 ⚠️ WARNING"
  script_exit_2: "GATE-n → FAIL → 关联任务 BLOCKED → FLE记录"
  script_exit_3: "GATE-n → CRITICAL_FAIL → 全部活跃任务 BLOCKED + Owner通知"

gate_trigger:
  - GATE-18 (pre-commit): "每次 git commit → run_all.py quick scan → exit ≤ 1 才放行"
  - G0-G7 (任务门禁): "任务执行前后 → 对应维度脚本判定"
```

### 2.9 CT-ORC-VMS-001：任务系统 → 向量记忆 — 任务输出写入向量库

```yaml
contract: CT-ORC-VMS-001
title: "任务产出写入向量记忆——持久化检索入口"
systems:
  - role: producer
    name: orchestrator
    path: "src/zephyr/orchestrator/"
    blueprint: "MOD-INF-006"
  - role: consumer
    name: vector_memory_system
    path: "src/zephyr/vector_memory/"
    blueprint: "MOD-INF-011"

data_flow:
  direction: producer_to_consumer
  trigger: "TaskCard.status → COMPLETED 且 output_type ∈ {CODE, DOCUMENT, ANALYSIS}"
  payload:
    task_id: "string — TaskCard.task_id"
    output_summary: "string — 任务产出的250字摘要"
    output_blocks: "list[OutputBlock] — 按segment分块的原始产出"
    embedding_hint: "enum[DENSE, SPARSE, HYBRID] — 建议的向量化策略"
    tags: "list[str] — 从TaskCard.tags继承"
  action: "VMS写入向量库 → 更新 TaskCard.vector_refs 字段"

quality_control:
  max_blocks_per_task: 50
  min_block_length: 100
  dedup_strategy: "content_hash → 已有hash则skip"
  retry_on_failure: 3

circuit_breaker:
  failure_threshold: 10
  recovery_after_seconds: 120
  fallback: "写入本地SQLite队列 → VMS恢复后批量回放"
```

### 2.10 CT-ORC-GATE-001：任务系统 → 门控引擎 — 任务执行前后门禁判定

```yaml
contract: CT-ORC-GATE-001
title: "任务生命周期的G0-G7门禁判定"
systems:
  - role: producer
    name: orchestrator
    path: "src/zephyr/orchestrator/"
    blueprint: "MOD-INF-006"
  - role: consumer
    name: gate_engine
    path: "src/zephyr/gates/"
    blueprint: "MOD-INF-007"

data_flow:
  direction: bidirectional
  orc_to_gate:
    trigger: "TaskCard 状态迁移到 PENDING → 进入 G0 判定"
    payload: "TaskCard 完整28字段"
    gating_sequence:
      - gate: G0
        at: "任务进入 TODO 前"
        checks: ["priority_valid", "assignee_exists", "deadline_future"]
        on_fail: "回退到 DRAFT"
      - gate: G1
        at: "任务进入 IN_PROGRESS 前"
        checks: ["context_built", "dependencies_met"]
        on_fail: "BLOCKED + 等待依赖"
      - gate: G7
        at: "任务标记 COMPLETED 前"
        checks: ["all_findings_resolved", "output_validated"]
        on_fail: "REVIEW_REQUIRED + FLE记录"
  gate_to_orc:
    response: "PASS | FAIL | PASS_WITH_WARNINGS | CRITICAL_FAIL"
    response_detail: "{ gate_id, violations[], suggestions[] }"
    action: "Orc 根据 response 更新 TaskCard.status"

design_rationale: >
  G0-G7不是全局门（区别于GATE-18 pre-commit），而是任务粒度门。
  每个TaskCard在其生命周期中依次通过G0→G1→...→G7，
  任何一个FAIL都会阻断任务流转，直到violation被消除。
```

### 2.11 CT-CE-LSG-001：上下文引擎 → LLM安全 — 上下文注入前安全校验

```yaml
contract: CT-CE-LSG-001
title: "LLM调用前的上下文安全审查——fail-closed边界"
systems:
  - role: producer
    name: context_engine
    path: "src/zephyr/context_engine/"
    blueprint: "MOD-INF-008"
  - role: consumer
    name: llm_security_gate
    path: "src/zephyr/llm_security/"
    blueprint: "MOD-INF-014"

data_flow:
  direction: producer_to_consumer
  trigger: "CE准备将构建好的context注入LLM调用——注入前必经LSG审查"
  payload:
    context_id: "string"
    target_model: "string — gpt-4o / claude-sonnet-4 / etc."
    full_prompt_text: "string — 即将发送给LLM的完整文本"
    source_files: "list[str] — context中引用的源文件路径"
    user_intent: "enum[CODE_GEN, CODE_REVIEW, ANALYSIS, QUERY]"
  action: "LSG逐层审查 → PASS则放行 / FAIL则阻断LLM调用 + 记录audit_log"

security_layers:
  - layer: input_sanitizer
    checks: ["prompt_injection_patterns", "code_execution_attempts", "credential_leak_patterns"]
    on_fail: "BLOCK → 拒绝此次LLM调用"
  - layer: process_sandbox
    checks: ["output_size_limit", "file_system_access_scope"]
    on_fail: "SANDBOX → 限制LLM输出范围"
  - layer: behavior_audit
    checks: ["anomaly_detection", "rate_limiting", "usage_pattern_deviation"]
    on_fail: "LOG + ALERT → 不阻断但告警"

fail_closed: >
  LSG不可用（进程crash/超时）→ 拒绝所有LLM流量（fail-closed原则）。
  不存在"跳过安全检查"的降级路径。
```

### 2.12 CT-KB-VMS-001：知识库 → 向量记忆 — 知识条目向量化存储

```yaml
contract: CT-KB-VMS-001
title: "结构化知识→非结构化向量记忆的双向映射"
systems:
  - role: producer
    name: knowledge_base
    path: "src/zephyr/knowledge_base/"
    blueprint: "MOD-KB-001"
  - role: consumer
    name: vector_memory_system
    path: "src/zephyr/vector_memory/"
    blueprint: "MOD-INF-011"

data_flow:
  direction: bidirectional

  kb_to_vms:
    trigger: "KE.status → ACTIVE 且 ke_type ∈ {ARCHITECTURE_RULE, CODE_CONVENTION, DECISION_RECORD}"
    payload:
      ke_id: "string"
      ke_title: "string"
      ke_content_plaintext: "string — 去Markdown格式化的纯文本"
      ke_type: "string"
      priority: "P0..P3"
      embedding_model: "text-embedding-3-large"
    action: "VMS生成embedding → 存储为 vector_entry → 返回 vector_id"

  vms_to_kb:
    trigger: "CE查询向量记忆 → 检索到KE相关向量"
    query: "{ vector_id, similarity_score, source_ke_id }"
    action: "KB根据 ke_id 返回KE完整内容 → CE注入上下文"

consistency_rule: >
  KE更新时 → KB通知VMS重新生成embedding（而非覆写旧向量）。
  旧向量标记为 superseded_by={new_vector_id}，保留用于审计追溯。
```

### 2.13 CT-FLE-DB-001：反馈环路 → 数据库 — 评估指标时序持久化

```yaml
contract: CT-FLE-DB-001
title: "FLE评估结果→数据库时序存储——为趋势分析和回滚决策提供数据基础"
systems:
  - role: producer
    name: feedback_loop_engine
    path: "src/zephyr/feedback_loop/"
    blueprint: "MOD-INF-010"
  - role: consumer
    name: database
    path: "src/zephyr/database/"
    blueprint: "MOD-INF-012"

data_flow:
  direction: producer_to_consumer
  trigger: "FLE完成一轮 collect→detect 循环后——无论是否有异常"
  payload:
    cycle_id: "string"
    cycle_timestamp: "ISO8601"
    metrics:
      task_throughput: "float — 任务/小时"
      gate_pass_rate: "float — G0-G7通过率 (%)"
      script_failure_rate: "float — 脚本exit≠0比率 (%)"
      ce_latency_p50: "float — CE构建延迟P50 (ms)"
      llm_token_usage: "int — 本周期LLM token消耗"
    anomalies:
      detected: "bool"
      anomaly_type: "enum[PERFORMANCE_DEGRADATION, QUALITY_REGRESSION, SECURITY_ALERT] | null"
      affected_systems: "list[str]"
    action_taken: "enum[NONE, THROTTLE, ROLLBACK, ALERT]"
  action: "db写入 fle_metrics 时序表 → 保留90天 → 90天后归档到 cold_storage"

circuit_breaker:
  db_write_failure: "写入本地SQLite buffer → db恢复后批量重放"
  max_buffer_size_mb: 100

design_rationale: >
  时序数据是FLE趋势分析和自动回滚决策的基础。
  即使当前周期无异常，也必须写入——"无异常"本身就是一个需要记录的信号。
```

---

## 三、共享 Schema（多系统共用的数据结构 SSoT）

> 以下 Schema 被多个系统消费——总蓝图是它们的 canonical SSoT。
> 模块蓝图引用这些 Schema 时不重复定义——只引用总蓝图的 Schema ID。

### 3.1 TaskCard（Orc、Pipeline、Gates、FLE、Script System 共用）

```yaml
schema: SCHEMA-TASKCARD-001
canonical_source: "PS-STD-001 §7.10 + src/zephyr/shared/schemas.py Task"

fields:
  - name: task_id
    type: str
    format: "{NAMESPACE}-{SEQ}"
    examples: ["MODEL-042", "AUDIT-017", "OPS-003", "KB-INF-0001"]
    namespaces:
      MODEL: "模型构建任务"
      AUDIT: "审计类任务"
      OPS: "运维/修复任务（脚本系统自动创建）"
      KB-INF: "知识库基础设施任务"
  - name: status
    type: enum
    values: [DRAFT, QUEUED, ASSIGNED, RUNNING, REVIEWING, COMPLETED, BLOCKED, CANCELLED, FAILED, ARCHIVED]
    transitions:
      BLOCKED_triggers: [GATE_FAIL, SCRIPT_EXIT_2, SCRIPT_EXIT_3, FLE_ESCALATE]
      BLOCKED_recovery: [GATE_PASS, SCRIPT_EXIT_0, OWNER_UNBLOCK]
  - name: task_type
    type: enum
    values: [MODEL_BUILD, AUDIT, DOC_WRITE, REFACTOR, AUTO_FIX, INFRA]
  - name: priority
    type: enum
    values: [P0, P1, P2, P3]
  - name: execution_model
    type: str
    source: "Pipeline routing output"
  - name: gate_profile
    type: str
    source: "Pipeline routing output"
```

### 3.2 Finding（Script System、Orchestrator、Gates、KB 共用）

```yaml
schema: SCHEMA-FINDING-001
canonical_source: "MOD-INF-005 §4.3 + src/zephyr/l01_infrastructure/script_system/finding.py"

fields:
  - name: finding_id
    type: str
    format: "FND-{DIMENSION}-{SEQ}"
  - name: severity
    type: enum
    values: [CRITICAL, HIGH, MEDIUM, LOW, INFO]
    routing:
      CRITICAL: "→ GATE FAIL + Orc BLOCK + OPS任务卡 + Owner通知"
      HIGH: "→ GATE FAIL + Orc BLOCK + OPS任务卡"
      MEDIUM: "→ GATE WARN + KB入库(G1→G2 Triage)"
      LOW: "→ GATE WARN + 审计日志"
      INFO: "→ 审计日志"
  - name: dimension
    type: enum
    values: [D1, D2, D3, D4, D5, D6, D7, D8, D9, D10, D11, D12]
  - name: recommendation
    type: str
    description: "修复建议——人类可读"
  - name: recommendation_type
    type: enum
    values: [auto_fixable, manual_only, needs_review]
```

### 3.3 KE（KB、CE、VMS、Script System 共用）

```yaml
schema: SCHEMA-KE-001
canonical_source: "MOD-KB-001 §3.2"

fields:
  - name: ke_id
    type: str
    format: "KE-{NNN}"
  - name: status
    type: enum
    values: [DRAFT, INGESTED, TRIAGED, ANALYZED, ACTIVATED, EXTRACTED, DEPRECATED, ARCHIVED, CONFLICT, DUPLICATE]
  - name: kb_gate
    type: enum
    values: [G1, G2, G3, G4, G5]
    description: "当前KE所处的KMS门禁阶段"
  - name: source
    type: enum
    values: [manual, script_system_C4, FLE_dispatch, session_log, adr]
  - name: embedding_status
    type: enum
    values: [not_embedded, embedding, embedded, failed]
```

---

## 四、全局状态传播链

### 4.1 完整传播图谱

```
[事件 1] 脚本 exit 2 (D6 安全漏洞)
    ↓
    Gate G0-G7 → FAIL (CT-SCRIPT-GATE-001)
    ↓
    ┌──────────────────────────────┐
    │  关联任务 → status: BLOCKED  │ ← CT-ORC-SCRIPT-001
    │  Orc 写入 db.task_repo      │ ← CT-ORC-DB
    └──────────────────────────────┘
    ↓ (并行)
    ┌──────────────────────────────┐
    │  FLE.detect_anomaly         │ ← CT-TELE-FLE-001
    │  "D6 持续阻断 > 3次"        │
    └──────────────────────────────┘
    ↓
    ┌──────────────────────────────┐
    │  FLE.dispatch_action        │ ← CT-FLE-ORC-001
    │  action: ESCALATE           │
    └──────────────────────────────┘
    ↓
    GPT-5.2 → Owner 飞书通知
    ↓
    Owner: "手动修复 D6 漏洞"
    ↓
    脚本重跑 → exit 0
    ↓
    Gate → PASS
    ↓
    Orc: 解除 BLOCKED → status: TODO
    ↓
    CE: 构建新session上下文（注入本次修复的KE）
```

### 4.2 故障传播与熔断约定

| 故障 | 影响范围 | 传播方式 | 熔断机制 |
|------|:---:|------|------|
| VMS 不可用 | CE、KB | CE降级→仅注入硬编码规则；KB标记degraded | 自动重试3次→通知Owner→不阻断其他系统 |
| db SQLite 锁竞争 | Orc、FLE | ATM排队→写入延迟 | 超时3s→WAL模式自动回退→不丢数据 |
| pre-commit D1 exit 3 | 全部提交 | **硬阻断**——git commit 不允许 | 立即通知Owner + `--no-verify`应急通道（需Session Log记录） |
| LSG 误杀率 > 10% | CE、Orc | 上下文注入缺失块 | 自动降级→标记+记录→人工调整LSG阈值 |
| ChromaDB 崩溃 | VMS、CE | CE降级→无向量检索 | 重启ChromaDB→CE自动恢复完整上下文注入 |

---

## 五、全局容量预算

| 资源 | 各系统独立上限 | 全局硬上限 | 超限策略 |
|------|:---:|:---:|------|
| 全系统 12 维度扫描耗时 | — | **600s (10min)** | 超时维度标记 skip |
| pre-commit 钩子数 | 10/系统 | **15** | 分组并行执行 |
| SQLite db 文件大小 | — | **140TB (SQLite上限)** | 当前 <10MB——远未触达 |
| VMS ChromaDB 单 Collection | — | **1M vectors** | BGE-M3 1024d → ~4GB/1M |
| CE Session Token | — | **8000 tokens/session** | 超限→compress阶段优先级截断 |
| FLE metric 采样频率 | — | **30s** | 峰值期降至 60s |
| 单次 session 蓝图注入数 | — | **5 blueprints** | 按 target_layer 相关性排序 |

---

## 六、施工 Phase 规划

### 蓝图补齐（当前 session）

| 任务 | 优先级 |
|------|:---:|
| 总蓝图（本文档）创建 | **P0** |
| Gates / CE / Pipeline / FLE 四个 P0 蓝图创建 | **P0** |
| module-registry.yaml 更新 | **P0** |

### 接口契约落地

| 任务 | 优先级 |
|------|:---:|
| CT-ORC-SCRIPT-001 硬编码→Gate Engine 可配置判定 | P0 |
| CT-ORC-CE-001 上下文构建完整实现 | P0 |
| VMS / db / MCP 蓝图创建 | P1 |

### 全链路自愈

| 任务 | 优先级 |
|------|:---:|
| CT-FLE-ORC-001 异常检测→自动调度 | P1 |
| 熔断机制全面实现 | P1 |
| LSG / Telemetry 蓝图创建 | P2 |

---
## 七、Anti-Patterns —— AI agent 绝对禁止的集成行为

> 氛围编程社区（Cursor Rules / Windsurf Rules）的核心教条：
> 集成文档的首要价值不是告诉 AI 该做什么，而是告诉 AI **什么绝对不能做**。
> 以下每一条违反都会导致系统级故障——没有例外。

| # | Anti-Pattern | 违反后果 | 正确做法 |
|---|-------------|---------|---------|
| AP1 | **绕过集成契约直接调用**——子系统A不经过CT-*契约直接import子系统B的内部模块 | 契约SSoT失效 → CI校验无意义 → 重构时全盘崩溃 | 任何跨系统调用必须通过CT-*契约定义的接口 |
| AP2 | **M1-M5产出物直接进入B-zone**——Pipeline A-zone(生产)产出的artifact未经审核直接流入B-zone(审计) | 生产数据污染审计数据 → 审计结论失真 | A-zone产出物必须经过M6边界明确标记后才能进入B-zone |
| AP3 | **无异常检测触发回滚**——FLE未检测到异常就执行THROTTLE/ROLLBACK | 正常系统被误杀 → 假阳性导致任务堆积 | ROLLBACK仅当FLE.detect_anomaly()返回true时触发 |
| AP4 | **CE compress阶段丢弃raw_text**——上下文引擎压缩时删除原始文本只保留向量 | 下游LLM安全审查失败（需要raw_text做注入检测）| compress永远保留raw_text字段——LSG消费raw_text |
| AP5 | **熔断降级时跳过安全校验**——circuit_breaker触发后跳过LSG检查以恢复性能 | 攻击者利用熔断窗口注入恶意prompt | LSG不可降级——fail-closed优先于availability |
| AP6 | **任务卡片跨status跳跃**——TaskCard.status从DRAFT直接跳到COMPLETED | 绕过G0-G7全部门禁 → 门控引擎形同虚设 | status迁移必须遵循 DRAFT→TODO→IN_PROGRESS→REVIEW→COMPLETED |
| AP7 | **共享Schema字段私自扩展**——子模块为方便在SCHEMA-*上追加字段但不更新本蓝图 | 多系统消费同一Schema但字段不一致 → 反序列化失败 | SCHEMA-*变更必须本蓝图审批后广播所有消费系统 |
| AP8 | **模拟对方系统的"假成功"响应**——测试时用mock返回CT-*契约里未定义的响应格式 | 测试通过但集成时break | mock必须定义在CT-*契约的`mock_strategy`字段内 |

---

## 八、施工指南 —— AI agent 编码入口

> **为什么需要这一章**：蓝图定义了13个CT-*契约、3个SCHEMA-*、4条全局链，
> 但AI agent拿到这份蓝图后需要知道——**从哪个文件开始、按什么顺序、依赖什么先行**。
> 本章是100% AI开发场景下的冷启动施工地图。

### 8.1 施工前置条件检查

| 检查项 | 状态 | 说明 |
|-------|:---:|------|
| 3个Shared Schema已在代码中实现 | ❌ | TaskCard / Finding / KE 三个数据类需要先定义 |
| depends_on中的16个蓝图层文件已存在 | ✅ | architecture-model/layers/*.yaml全部存在 |
| Python 3.11+ 环境就绪 | ✅ | 项目已有环境 |
| module-registry.yaml已注册本蓝图 | ✅ | MOD-MASTER-001已注册 |

### 8.2 施工顺序（无依赖→有依赖→循环依赖）

```
Phase A: 无依赖先行（可并行）
├── A1: Shared Schema 实现
│   ├── src/zephyr/shared/schemas/task_card.py   ← TaskCard 28字段dataclass
│   ├── src/zephyr/shared/schemas/finding.py     ← Finding 5字段dataclass
│   └── src/zephyr/shared/schemas/ke.py          ← KE dataclass
│
├── A2: CT-ORC-GATE-001   ← 只依赖TaskCard + Gates层YAML
│   └── src/zephyr/gates/task_gates.py
│
├── A3: CT-CE-LSG-001     ← 只依赖CE层YAML + LSG层YAML
│   └── src/zephyr/llm_security/ce_lsg_bridge.py
│
└── A4: CT-KB-VMS-001     ← 只依赖KB + VMS层YAML
    └── src/zephyr/vector_memory/kb_vms_bridge.py

Phase B: 单向依赖（A完成后→B启动）
├── B1: CT-ORC-CE-001     ← 依赖 TaskCard + CE层YAML
├── B2: CT-ORC-VMS-001    ← 依赖 TaskCard + VMS层YAML
├── B3: CT-SCRIPT-GATE-001 ← 依赖Gate层YAML + Script层
└── B4: CT-FLE-DB-001     ← 依赖FLE层YAML + DB层YAML

Phase C: 双向依赖（需要双方都就绪）
├── C1: CT-ORC-SCRIPT-001 ← Orc ↔ Script System ← 需要双方都开发
│   → 策略：先实现 Orc→Script方向，Script侧用stub；再反转
│
└── C2: CT-FLE-ORC-001    ← FLE → Orc ← 需要异常检测(Phase A)完成
    → 策略：先实现const→FLE推送路径，Orc侧动作暂用log代替

Phase D: 全链路集成
├── D1: CT-PIPE-ORC-001   ← Pipeline M1-M11 + Orc → 最后实现
├── D2: CT-TELE-FLE-001   ← Telemetry → FLE ← 全系统就绪后
└── D3: CT-CE-VMS-001     ← CE → VMS ← 双方就绪后
```

### 8.3 每个CT-*契约的mock策略

当AI agent只实现契约的一方时，需要用mock模拟对方。以下mock策略均在契约的`mock_strategy`字段内约定：

| CT-* | mock策略 |
|------|---------|
| CT-ORC-SCRIPT-001 | `python -c "import sys; sys.exit(0)"` 模拟脚本exit 0 |
| CT-ORC-CE-001 | 返回 `{"context": "MOCK_CONTEXT", "source_files": []}` |
| CT-ORC-VMS-001 | SQLite内存模式 `:memory:` 模拟向量存储 |
| CT-ORC-GATE-001 | 返回 `{"response": "PASS", "detail": {"gate_id": "G0", "violations": []}}` |
| CT-CE-VMS-001 | FAISS内存索引 `faiss.IndexFlatL2(768)` 模拟 |
| CT-CE-LSG-001 | 返回 `{"allowed": true, "audit_id": "mock-audit-001"}` |
| CT-KB-VMS-001 | `numpy.random.rand(3072)` 模拟embedding |
| CT-FLE-ORC-001 | 返回 `{"action": "NONE", "reason": "no anomaly detected"}` |
| CT-FLE-DB-001 | SQLite `:memory:` 模拟时序存储 |
| CT-PIPE-ORC-001 | 返回 `{"node": "M1", "status": "ready"}` |
| CT-TELE-FLE-001 | 空dict `{}` 模拟指标推送 |

---

## 九、设计决策集中表

> 当前10条关键架构决策散落在各个CT-*合约的`design_rationale`字段中。
> 本章提供集中视图——便于新session AI快速理解"为什么这么设计"。

| ID | 决策 | 理由 | 替代方案（被否决） | 重新评估条件 |
|----|------|------|------------------|------------|
| DD1 | **总蓝图只定义"之间"，不管"内部"** | 防止总蓝图过厚→编修成本指数增长 | "一个文件定义一切"的Monolithic方案 | 当模块数>50时重新评估 |
| DD2 | **YAML结构化契约而非Markdown自然语言** | AI可直接解析→CI可自动验证 | "用RFC风格的Markdown文档描述每个契约" | YAML解析在项目中成为瓶颈时 |
| DD3 | **fail-closed优先于availability** | 安全>可用——绕过安全检查的LLM调用不可逆 | "熔断时跳过安全校验"——被否决 | 当误阻断率达5%+时重新评估 |
| DD4 | **circuit_breaker在每条CT-*独立配置** | 不同系统对的故障容忍度不同——一刀切=过度熔断或延误响应 | "全局唯一的熔断策略" | —无— |
| DD5 | **FLE写入无异常也需记录** | "无异常"是趋势分析的关键信号——缺失=分析盲区 | "仅异常时写入"——被否决（丢失baseline）| 存储成本成为主要约束时 |
| DD6 | **KE更新→新embedding而非覆写** | 旧向量保留用于审计追溯——"这个KE曾经指向什么"需要回答 | "直接覆写旧embedding"——简化但丢失审计 | 向量库存储达到容量上限 |
| DD7 | **故障传播方向：内→外（局部先隔离）** | 确保局部故障不影响全局→最小爆炸半径 | "外→内"——全局熔断影响未出问题的系统 | —无— |
| DD8 | **M1-M11双zone不可交叉污染** | A-zone生产指标和B-zone审计指标混合→审计结论不可信 | "单pipeline同时承担生产和审计"——被否决 | —无— |
| DD9 | **stub/mock必须在契约文件内定义** | AI agent测试时自己编mock→与真实契约偏离→集成时break | "mock由实现方自由定义"——被否决 | —无— |
| DD10 | **契约编号CT-{A}-{B}固定——新增=追加、废弃=标记但不删除** | 铁律四：蓝图永久保留←废弃契约仍然影响历史session回溯 | "删除废弃CT-*编号"——被否决 | —无— |

---

## 十、集成测试契约

> 每个CT-*契约附带测试断言——确定性验证集成是否正确。

### 10.1 通用集成测试模板

```python
# tests/integration/test_integration_contracts.py
import pytest

class TestIntegrationContract:
    """每个CT-*契约的通用验证模板"""

    CONTRACT_ID: str  # 子类覆写

    def test_producer_side_exists(self):
        """生产方实现文件存在"""
        ...

    def test_consumer_side_exists(self):
        """消费方实现文件存在"""
        ...

    def test_contract_payload_schema_matches(self):
        """payload字段与契约YAML声明一致"""
        ...

    def test_circuit_breaker_fires_on_threshold(self):
        """熔断在failure_threshold触发"""
        ...

    def test_circuit_breaker_recovers_after_timeout(self):
        """熔断在recovery_after_seconds恢复"""
        ...
```

### 10.2 每个CT-*的专属测试断言

| CT-* | 关键测试断言 | 预期结果 |
|------|------------|---------|
| CT-ORC-SCRIPT-001 | script exit 2 → BLOCKED ; exit 0 → 恢复TODO | status迁移正确 |
| CT-ORC-CE-001 | CE返回context包含source_files字段 | source_files非空 |
| CT-ORC-VMS-001 | 写入vector后TaskCard.vector_refs非空 | refs写入成功 |
| CT-ORC-GATE-001 | G0: priority=invalid→FAIL ; G7: all_findings_resolved=false→REQUIRED_REVIEW | 门判定正确 |
| CT-SCRIPT-KB-001 | Finding.severity=MEDIUM → KE入库成功 | KE新增 |
| CT-SCRIPT-GATE-001 | exit 0→PASS ; exit 3→CRITICAL_FAIL→全任务BLOCKED | exit code映射正确 |
| CT-CE-VMS-001 | 查询"代码约定"→返回相似度>0.7的向量 | 检索准确 |
| CT-CE-LSG-001 | prompt包含`__import__('os').system('rm')`→BLOCK | 注入拦截 |
| CT-KB-VMS-001 | KE→embedding→写入→ke_id→返回vector_id | 双向映射正确 |
| CT-FLE-ORC-001 | anomaly_type=PERFORMANCE_DEGRADATION→ORC THROTTLE | 调度调整生效 |
| CT-FLE-DB-001 | 写入fle_metrics→读取→一致 | 持久化正确 |
| CT-TELE-FLE-001 | Telemetry推送后FLE能读取最新metrics | 推送链路通畅 |
| CT-PIPE-ORC-001 | task_type=ops→路由到M2 ; task_type→不匹配→返回error | 路由正确 |

### 10.3 CI门禁集成测试触发条件

| GATE | 触发条件 | 覆盖的CT-* |
|:---:|---------|----------|
| GATE-IT-1 | 每次 push / PR | CT-ORC-*, CT-SCRIPT-*, CT-FLE-* |
| GATE-IT-2 | Phase D 全链路完成后每日跑 | 全部13个CT-* |
| GATE-IT-3 | LSG相关代码变更时触发 | CT-CE-LSG-001 |
| GATE-IT-SMOKE | pre-commit快速冒烟 | CT-ORC-SCRIPT-001, CT-SCRIPT-GATE-001 |

---
---
## 十一、风险与后果

### 11.1 核心风险

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|:---:|:---:|------|
| R1 | **契约漂移**——模块蓝图引用总蓝图契约但实现不一致 | 中 | 高 | CI门禁 → 自动交叉校验契约 vs 实现 |
| R2 | **总蓝图过厚**——试图定义每个模块的内部细节 | 高 | 中 | 严格边界：总蓝图只管"之间"，不管"内部" |
| R3 | **单点故障**——总蓝图是12系统的契约SSoT，破损=集成混乱 | 低 | **极高** | 总蓝图 YAML 契约应可由 CI 自动验证 |

### 11.2 正面后果

- **AI冷启动加速**：新 session AI 读完本蓝图 → 一次了解全部集成关系 → 不需从 12 个模块蓝图交叉拼图
- **契约可验证**：每条 CT-* 契约 YAML 结构化 → CI 可直接校验生产方/消费方的接口实现一致性
- **故障传播可视化**：§4 状态传播链 → 一个系统故障 → 一眼看出"哪些系统受影响"

---

## 十二、治理信息

### SSoT 声明

| 内容 | 真源 |
|------|------|
| 系统间集成契约（CT-*）| **本蓝图 §2** |
| 共享 Schema（SCHEMA-*）| **本蓝图 §3** |
| 全局状态传播链 | **本蓝图 §4** |
| 各系统内部架构 | **各模块蓝图** |

**冲突裁决**：模块蓝图的集成描述与本蓝图不一致 → 按以下裁决程序处理。

### 冲突裁决程序

当以下任何情况发生时，触发集成冲突裁决：

| # | 触发条件 | 检测方式 |
|---|---------|---------|
| 1 | 子蓝图引用的 CT-* 合同编号在 MASTER-001 中不存在 | CI 扫描 |
| 2 | 子蓝图声明的合同 payload 字段与 MASTER-001 CT-* YAML 不一致 | CI 扫描 |
| 3 | 两个子蓝图对同一 CT-* 合同有互斥的理解 | CI 扫描 |
| 4 | architecture-model/layers/*.yaml 的 `interfaces` 与 MASTER-001 CT-* 声明不一致 | CI 扫描 |

**裁决优先级（从高到低）**：

| 优先级 | 来源 | 说明 |
|:---:|------|------|
| **1** | **MASTER-001 的 CT-* YAML**（本蓝图 §二） | canonical SSoT——最高权威 |
| 2 | `architecture-model/layers/*.yaml` | 架构模型层——子蓝图引用的 YAML 真源 |
| 3 | 各子模块蓝图 | 本地理解——有冲突时以上方为准 |

**CI 检测机制**：

```
validate_integration_consistency.py（待创建）
→ 扫描所有子蓝图的 CT-* 引用
→ 交叉校验 MASTER-001 §二 的合同定义
→ 不一致 = CI FAIL（硬阻断，P0）
→ 冲突日志输出到 .audit_cache/integration_conflicts.json
```

**冲突修复流程**：

```
1. CI 检测到冲突 → 输出冲突详情
2. AI agent 读取冲突详情 → 判断哪一方需要修改
3. 修改子蓝图（对齐 MASTER-001）或修改 MASTER-001（如果合同定义本身需要升级）
4. 重新提交 → CI 重新扫描 → 通过
5. 修复记录写入 变更记录
```

### 消费者注册

| Tier | 消费者 |
|:----:|------|
| Tier 1 | 所有模块蓝图——引用本蓝图的契约编号 |
| Tier 2 | CI 门禁脚本——交叉校验契约一致性 |
| Tier 3 | 新 session AI——冷启动集成关系地图 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 新增/修改集成契约（CT-*）| Owner 审批 |
| Schema 字段变更 | Owner 审批 + 通知所有消费系统 |
| 容量上限调整 | AI 自主（§5 阈值内） |

---
---

## 十三、端到端场景走查

> 氛围编程社区核心教条：**"Show, don't just tell."**
> 以下是一个完整场景——演示 13 个 CT-* 合同在真实任务中如何协同工作。

### 场景：Owner 发现治理脚本漏检 — AI 修复全流程

```
第 1 步：任务创建
  Owner → Orc: 创建 TaskCard
    task_type = OPS
    priority = P1
    description = "run_all.py 的 D12 维度漏检 .yaml 文件编码"
  Orc 内部:
    G0 Task Entry Gate 判定 → task_id 格式 OK, priority OK → PASS
    TaskCard.status: DRAFT → TODO

  → 涉及: CT-ORC-GATE-001 (G0 门禁)

第 2 步：上下文构建
  Orc → CE: CT-ORC-CE-001
    请求构建上下文——需要 run_all.py 源码 + D12 维度规则 + TaskCard 描述
  CE 内部:
    build 阶段: 收集 run_all.py + b_docs.yaml + TaskCard 28 字段
    → CE → VMS: CT-CE-VMS-001
      查询 "治理脚本 YAML 编码检测" → 返回 3 条历史 bug 修复记录
    compress 阶段: 压缩到 4000 tokens（保留 raw_text）
    validate 阶段: CE → LSG via CT-CE-LSG-001
      LSG: input_sanitizer → 无注入 → PASS
      LSG: process_sandbox → PASS
      LSG: behavior_audit → PASS
    inject 阶段: 将 context 注入 LLM 调用

  → 涉及: CT-ORC-CE-001, CT-CE-VMS-001, CT-CE-LSG-001

第 3 步：管线路由
  任务进入 Pipeline → CT-PIPE-ORC-001
    task_type = OPS → 路由到 M2 (OPS/修复) 节点
    模型选择: Claude Sonnet 4（能力矩阵中 OPS 类型的最佳模型）

  → 涉及: CT-PIPE-ORC-001

第 4 步：AI 生成修复
  AI Agent 在 M2 节点执行:
    读取 run_all.py → 发现 D12 维度的 glob 模式未包含 *.yaml
    修改: glob 模式追加 "**/*.yaml"
    沙箱检查: G4 Sandbox Gate → sandbox_profile 匹配 OPS → PASS
    工具调用检查: G6 Security Gate → 所有 tool_call 在白名单 → PASS

  → 涉及: CT-ORC-GATE-001 (G4, G6)

第 5 步：治理脚本判定
  Script System → 执行 run_all.py
    exit code = 0（所有维度 PASS）
    → CT-SCRIPT-GATE-001: exit 0 → GATE-n PASS

  → 涉及: CT-SCRIPT-GATE-001

第 6 步：知识入库（如果本次修复产生了新知识）
  Script System 产生 Finding(severity=MEDIUM, type=BUG_FIX)
    → CT-SCRIPT-KB-001: MEDIUM Finding → KE 入库
  KB 处理:
    KE 进入 KMS 管道 → G1 Ingest → G2 Triage → G3 Evaluate
    KE.status = ACTIVE
    → CT-KB-VMS-001: KB → VMS 生成 embedding

  → 涉及: CT-SCRIPT-KB-001, CT-KB-VMS-001

第 7 步：交付前门禁
  任务进入 REVIEW 状态 → Orc 触发 G7 Delivery Gate
    G7-C00: run_all.py exit 0 → PASS
    TaskCard.status: REVIEW → COMPLETED

  → 涉及: CT-ORC-GATE-001 (G7)

第 8 步：反馈闭环
  FLE 采集本轮数据:
    → CT-TELE-FLE-001: 读取 Telemetry 的 task_throughput, gate_pass_rate
    → FLE.detect_anomaly(): 无异常（所有指标正常）
    → CT-FLE-DB-001: 写入 fle_metrics 时序表（"无异常"本身也记录）
    → CT-FLE-ORC-001: 反馈给 Orc——本次 OPS 任务正常，无需调整调度

  → 涉及: CT-TELE-FLE-001, CT-FLE-DB-001, CT-FLE-ORC-001

全流程涉及的 CT-* 合同: 11/13
  未涉及: CT-ORC-VMS-001（本次无COMPLETED任务产出需要向量化）
          CT-ORC-SCRIPT-001（本次无CRITICAL/HIGH Finding触发自动创建OPS任务卡）
```

---
---

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 总蓝图不产生代码，仅定义集成契约

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-03 | 0.1.0 | 初始创建——12系统拓扑 + 13条集成契约(CT-*) + 3个共享Schema + 全局状态传播链 + 容量预算 + 故障熔断。 |
| 2026-05-04 | 0.2.0 | 黄金标准补齐：(1)新增§七 Anti-Patterns——8条AI绝对禁止的集成行为；(2)新增§八 施工指南——Phase A→D四级施工序列+11个CT-*mock策略；(3)补齐5个未展开CT合约(ORC-VMS, ORC-GATE, CE-LSG, KB-VMS, FLE-DB)；(4)新增§九 设计决策集中表——10条关键决策+替代方案+重评条件；(5)新增§十 集成测试契约——13个CT-*专属断言+4级CI门禁触发条件；(6)frontmatter新增 ai_role_instruction + construction_progress。 |
| 2026-05-04 | 0.3.0 | 氛围编程社区盲点补齐——二次审查发现4个关键缺失：(1)新增§零 AI Agent 分派与阅读指南——B1 AI Agent分派表(12系统×各自CT-*+关联Schema+tokens)+B2 Token预算(3级阅读深度500/1500/8000)；(2)新增§十三 端到端场景走查——8步完整OPS修复全流程演示11/13个CT-*合同协同工作；(3)增强§十二 集成冲突裁决程序——4种触发条件+3级裁决优先级+validate_integration_consistency.py CI检测机制+5步冲突修复流程；(4)优化ai_role_instruction核心规则从4条→5条。MASTER-001从~65/100→~85/100，达成氛围编程社区顶级标准。 |
| 2026-05-04 | 0.3.1 | 三次审查修补：(1)修复frontmatter——construction_progress和ai_role_instruction字段在v0.2.0中写入失败，现已确认磁盘存在；(2)更新summary/对标声明——补上Cursor Rules+Windsurf Rules+Anthropic Agent Architecture；(3)修正遗留编号——§十一子节7.1/7.2→11.1/11.2；(4)移除重复分隔符--- ---；(5)Token预算文本同步：1120+行→1330+行。 |
