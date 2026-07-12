---
module_id: MOD-INF-013
submodule_path: src/zephyr/integration/mcp
title: "MCP Servers 蓝图 — MCP 服务器管理与调度"
doc_type: blueprint
status: Draft
version: "0.3.39"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-06"
valid_from: "2026-05-03"
ttl: permanent
construction_progress: design_only
actual_disk_path: "src/zephyr/integration/mcp/"
codification_level: L1
codification_at: "2026-05-13"
last_verified: "2026-05-13"
generation: 2
functional_domain: execution
parent_module: ""
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
belongs_to: "MOD-MASTER_BLUEPRINT"
summary: "MCP Servers 蓝图——11 个 MCP 服务端 + 1 Gateway 通过 stdio 协议暴露内部系统能力。357 项盲点（B1-B357）十八维闭合。"
tags: [mcp, mcp_servers, stdio, tool-contracts, model-context-protocol, external-api, infrastructure]
priority: P1
runtime_plane: hot
depends_on:
  - {target: "MOD-TASK_SYSTEM", at: "§3.2.1", why: "task_manager MCP——decompose_blueprint接口"}
  - {target: "MOD-KB-001", at: "§4", why: "knowledge_base MCP——KE查询接口"}
  - {target: "MOD-GATE_ENGINE", at: "§3.2", why: "gate_engine MCP——Gate判定接口"}
  - {target: "architecture_model/layers/b_mcp.yaml", at: "全篇", why: "MCP YAML SSoT——本蓝图真源"}
references: []
last_updated: "2026-05-15"
responsibility_domain: 
build_status: generated
design_maturity: prototype
---

<!--
COMPLIANCE_CHECKLIST — 机器可解析合规清单
蓝图 MUST 包含以下所有标题（精确匹配关键词）。缺一 = 不合规。
脚本：python scripts/governance/check_blueprint_compliance.py <蓝图路径>
-->
<!--
REQUIRED_SECTIONS:
  overview: "概述"
  §0: "代码对齐验证"
  §0.1: "代码文件清单"
  §0.2: "对齐验证矩阵"
  §0.3: "版本-代码映射"
  §1: "设计背景与目标"
  §1.1: "背景"
  §1.2: "目标"
  §1.3: "不包含的目标"
  §1.4: "运行场景约束"
  §2: "模块边界"
  §2.1: "职责范围"
  §2.2: "不包含的职责"
  §3: "架构设计"
  §3.1: "组件架构"
  §3.2: "数据流"
  §3.3: "状态生命周期"
  §4: "接口契约"
  §4.1: "公共 API"
  §4.2: "数据模型"
  §4.3: "输入契约"
  §4.4: "输出契约"
  §4.5: "MCP 接口"
  §4.6: "契约版本"
  §5: "约束条件"
  §5.1: "技术约束"
  §5.2: "容量估算"
  §5.3: "迁移"
  §6: "错误处理"
  §8: "安全考量"
  §9: "测试策略"
  §10: "依赖关系"
  §11: "产出物"
  §12: "集成目标"
  §13: "需要更新"
  §14: "风险"
  §16: "施工指引"
  §17: "容量升级"
  §18: "决策记录"
  pre_1: "Vibe Coding"
  pre_2: "安全删除"
  pre_3: "必备链接"
  pre_4: "已有类似功能"
  pre_5: "涉及的文件范围"
END_REQUIRED_SECTIONS
-->

# MCP Servers 蓝图 — MCP 服务器管理与调度

## 概述

本蓝图描述 MCP Servers——它解决了 AI 治理框架中 MCP (Model Context Protocol) 服务器统一管理与调度的核心问题。核心职责包括：MCP 服务端生命周期管理、Tool 注册与发现、JSON-RPC 2.0 协议实现、Gateway 网关路由。当前规模 5 个 MCP Server / 20+ Tools，目标容量 50+ Tools / 100 AI 并发调用。上游依赖 LLM 推理层（Tool 调用），下游被 Agent 编排、知识库检索消费。

| `_base_server.py` |
| `audit_logger.py` |
| `blueprint_search_server.py` |
| `doc_guard_server.py` |
| `error_codes.py` |
| `gate_engine_server.py` |
| `gateway_server.py` |
| `governance_server.py` |
| `handoff_auto_loader.py` |
| `knowledge_base_server.py` |
| `prompt_provider.py` |
| `rate_limiter.py` |
| `resource_provider.py` |
| `sandbox_server.py` |
| `sentinel_server.py` |
| `task_manager_server.py` |
| `telemetry_server.py` |
| `vector_memory_server.py` |
| `_base_server.py` |
---

> module_id: MOD-INF-013 | version: 0.3.37 | status: draft | layer: cross_layer
> actual_disk_path: src/zephyr/integration/mcp/ | generation: 2 | construction_progress: completed
>
> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

> 真源声明：本蓝图的 canonical SSoT 为 `architecture_model/layers/b_mcp.yaml`。
> 代码落位：`src/zephyr/integration/mcp/`（19 个 .py 文件，其中 task_manager / blueprint_search / telemetry / governance / vector_memory 已实现，gateway / audit_logger / rate_limiter / error_codes / prompt_provider / resource_provider / handoff_auto_loader 已实现，knowledge_base / gate_engine / doc_guard / sentinel / sandbox 为 skeleton）。
---

## §0 代码对齐验证

### 代码文件清单

> **架构归属SSoT**：`data/asset_index/project-architecture-panorama.yaml`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-015`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | `task_manager_server.py` | §2 | 蓝图→任务卡拆解、任务 CRUD | 已实现 | 业务逻辑归属 MOD-TASK_SYSTEM（任务系统），MOD-INF-013 仅负责 MCP 协议层（传输/序列化/注册） |
| 2 | `knowledge_base_server.py` | §2 | KE 查询/创建 | 未实现 | |
| 3 | `gate_engine_server.py` | §2 | Gate 判定/熔断 | 未实现 | |
| 4 | `doc_guard_server.py` | §2 | 文档安全校验（server_id=session_handoff） | 未实现 | |
| 5 | `sentinel_server.py` | §2 | 系统哨兵监控（server_id=intent_router） | 未实现 | |
| 6 | `blueprint_search_server.py` | §2 | 蓝图检索 | 已实现 | |
| 7 | `sandbox_server.py` | §2 | 安全代码执行沙箱 | 未实现 | |
| 8 | `telemetry_server.py` | §2 | 系统遥测可观测性 | 已实现 | |
| 9 | `governance_server.py` | §2 | 治理域统一 MCP 入口 | 已实现 | |
| 10 | `vector_memory_server.py` | §2 | VMS 向量记忆 | 已实现 | |
| 11 | `gateway_server.py` | §2 | 集中式治理网关 | 已实现 | |
| 12 | `_base_server.py` | §3 | MCP Server 基类 | 已实现 | |
| 13 | `audit_logger.py` | §3 | 审计日志 | 已实现 | |
| 14 | `rate_limiter.py` | §3 | 速率限制 | 已实现 | |
| 15 | `error_codes.py` | §3 | 错误码定义 | 已实现 | |
| 16 | `prompt_provider.py` | §3 | Prompt 原语提供 | 已实现 | |
| 17 | `resource_provider.py` | §3 | Resource 原语提供 | 已实现 | |
| 18 | `handoff_auto_loader.py` | §3 | Session 接班自动加载 | 已实现 | |
| 19 | `__init__.py` | §3 | 包初始化 | 已实现 | |

### 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = completed → 代码文件清单100%存在 | `ls src/zephyr/integration/mcp/` 逐文件核对 | ☐ |
| 蓝图描述的 server_id = 代码中的 server_id | `grep "server_id" *.py` | ☐ |
| tool-contracts.yaml 工具名 = 代码中注册的工具名 | `grep "def .*_tool" *.py` | ☐ |

### 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.3.37 (基线) | 6 个已实现 Server + 6 个基础设施模块 | 5 个 skeleton Server | 待施工 |
| v1.0.0 (容量升级) | 全部 11 Server + 增量扫描 + Worker Pool | 异步并发模型/增量扫描引擎/Worker Pool | 待施工 |

---

## §1 概述

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-013 |
| 代码落位 | `src/zephyr/integration/mcp/` |
| 核心职责 | 向外部 IDE/Agent 暴露内部系统能力的统一接口 |

### 核心职能

MCP 职责：通过 stdio 向外部 Agent 暴露任务管理/知识查询/门禁决策等能力。

### 1.4 运行场景约束

> 详见 §5.1 技术约束表。

---

## §2 MCP 服务端

| 服务端 | 文件名 | server_id | 实现状态 | 暴露能力 |
|------|------|------|:---:|------|
| **task_manager** | `task_manager_server.py` | `task_manager` | ✅ 已实现 | 蓝图→任务卡拆解、任务 CRUD（业务逻辑归属 MOD-TASK_SYSTEM，MOD-INF-013 仅负责 MCP 协议层） |
| **knowledge_base** | `knowledge_base_server.py` | `knowledge_base` | 🔶 skeleton | KE 查询/创建、健康检查 |
| **gate_engine** | `gate_engine_server.py` | `gate_engine` | 🔶 skeleton | Gate 判定/熔断状态 |
| **session_handoff** | `doc_guard_server.py` | `session_handoff` | 🔶 skeleton | 文档安全校验（文件名与 server_id 不同！） |
| **intent_router** | `sentinel_server.py` | `intent_router` | 🔶 skeleton | 系统哨兵监控/指标（文件名与 server_id 不同！） |
| **blueprint_search** | `blueprint_search_server.py` | `blueprint_search` | ✅ 已实现 | 蓝图检索（P0-2 experimental） |
| **sandbox** | `sandbox_server.py` | `sandbox` | 🔶 skeleton | 安全代码执行沙箱（Phase 7 skeleton） |
| **telemetry** | `telemetry_server.py` | `telemetry` | ✅ 已实现 | 系统遥测可观测性（MOD-INF-015） |
| **governance** | `governance_server.py` | `governance` | ✅ 已实现 | 治理域统一 MCP 入口（15 工具） |
| **vector_memory** | `vector_memory_server.py` | `vector_memory` | ✅ 已实现 | VMS 向量记忆（MOD-INF-011） |
| **gateway** | `gateway_server.py` | `gateway` | ✅ 已实现 | 集中式治理网关（Route/Auth/RateLimit/Audit/Degrade） |

> ⚠️ **文件命名 vs server_id 不一致**：`doc_guard_server.py` 的 server_id 是 `session_handoff`，`sentinel_server.py` 的 server_id 是 `intent_router`。这是已知差异，不可"修正"文件名——server_id 是 MCP 协议契约中的标识，不能改。

### 2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | 脚本执行调度（Worker Pool） | MOD-DATABASE worker-pool |
| 2 | 增量扫描匹配引擎 | MOD-DATABASE governance-automation |
| 3 | Agent 生命周期编排 | MOD-INF-005 agent-orchestrator |
| 4 | 数据库 Schema 管理 | MOD-TASK_SYSTEM task-repo |
| 5 | 向量数据库索引维护 | MOD-INF-011 VMS |

---

## §3 协议与契约

### 3.1 通信协议

- **传输**：MCP stdio（标准输入/输出流）
- **协议**：JSON-RPC 2.0
- **帧格式**：Content-Length 前缀（MCP 2024-11-05 规范），当前 `_base_server.py` 仅支持逐行读取，不支持 Content-Length 帧（B46）
- **工具调用模式**：request→response，同步阻塞模型
- **认证**：当前无——本地 stdio 进程内通信，无需网络层认证
- **基础设施**：FastMCP SDK（task_manager）和 BaseMCPServer（其余 5 个）双轨并行

### 3.2 契约定义

- **契约 SSoT**：`src/zephyr/integration/mcp/tool-contracts.yaml`
- **版本**：1.2.0
- **工具命名约定**：`{server_id}.{action}`（如 `task_manager.decompose_blueprint`）
- **工具稳定性生命周期**：experimental → beta → stable → frozen
- **safety_level**：L/M/H 三级访问控制（定义在 YAML，代码中未执行——B37）

### 3.3 MCP 原语覆盖

| 原语 | 实现状态 | 备注 |
|------|:---:|------|
| `initialize` | ✅ | BaseMCPServer 和 FastMCP 均支持 |
| `ping` | ✅ | BaseMCPServer 支持 |
| `tools/list` | ✅ | 返回所有注册工具 |
| `tools/call` | ✅ | 基础实现，缺 safety_level + timeout |
| `resources/list` | ❌ | 未实现（Resource 是最大 P0 缺口——B41） |
| `resources/read` | ❌ | 未实现 |
| `prompts/list` | ❌ | 未实现 |
| `prompts/get` | ❌ | 未实现 |
| `notifications/message` | ❌ | 未实现（Server→Client 通知） |

### 3.4 错误码体系

| 错误码 | 常量名 | 含义 | 状态 |
|:---:|------|------|:---:|
| -32700 | `ERR_PARSE_ERROR` | JSON 解析失败 | ✅ 标准 |
| -32600 | `ERR_INVALID_REQUEST` | 请求格式无效 | ✅ 标准 |
| -32601 | `ERR_METHOD_NOT_FOUND` | 方法不存在 | ✅ 标准 |
| -32602 | `ERR_INVALID_PARAMS` | 参数无效 | ✅ 标准 |
| -32603 | `ERR_INTERNAL_ERROR` | 内部错误 | ✅ 标准 |
| **-32001** | `ERR_TOOL_NOT_FOUND` | **工具未找到** | ⚠️ **与蓝图 GATE_FAILED(-32001) 冲突**（B36） |
| -32002 | `ERR_TOOL_EXECUTION` | 工具执行失败 | ✅ |
| -32003 | — | 预留：GATE_FAILED | 📋 需从 -32001 搬移 |
| -32004 | — | 预留：RBAC_DENIED | 📋 待定义 |

---

## §4 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| Phase 1 | task_manager decompose_blueprint + _base_server | ✅ 完成 |
| Phase 2 | knowledge_base / gate_engine MCP 实现 → stable | 📋 backlog |
| Phase 3 | session_handoff / intent_router MCP 实现 → stable | 📋 backlog |
| Phase 4 | blueprint_search → stable（含缓存/索引增量更新） | 📋 backlog |
| Phase 5 | MCP Gateway 落位（集中式安全 + 治理 + 观测） | 📋 backlog |
| Phase 6 | Resource / Prompt 原语补全 | 📋 backlog |
| Phase 7 | sandbox MCP Server（安全代码执行） | 📋 backlog |
| Phase 8 | 全链路压力测试 + 混沌工程 + 安全审计 | 📋 backlog |
| Phase 9 | 1人+AI 维护模式验收 | 📋 backlog |

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 影响 |
|---|------|------|
| TC1 | 本地 stdio 进程内通信，无网络层 | 无需网络认证，但依赖进程隔离安全 |
| TC2 | 单机 i7-12700KF 12C/20T, 64GB RAM | 并发上限受物理硬件约束 |
| TC3 | 1人+AI 维护模式 | 无 24/7 SRE，需自动恢复/自愈 |
| TC4 | Windows 开发环境 | 进程管理/信号处理需 Windows 适配 |
| TC5 | MCP SDK `mcp>=1.0.0` | 必须声明于 pyproject.toml / requirements.txt |
| TC6 | ChromaDB + SQLite 共享持久化目录 | 多进程写入需 busy_timeout + collection 隔离 |
| TC7 | Python 3.12+ / Pydantic V2 | 类型注解必须完整 |

### 5.2 容量估算

| 资源 | 估算 | 依据 |
|------|------|------|
| MCP Server 数量 | 7-11 | 当前 7 个 skeleton + 4 个已实现 |
| 并发请求 | ≤20 QPS | 单机 + stdio 瓶颈 |
| 内存 | ≤2GB（全部 Server） | 每个 Server ≤200MB |
| 启动时间 | ≤30s（全部） | 串行启动 + ChromaDB 初始化 |

### 5.3 迁移/废弃方案

> **时态属性**：本节为**临时时态**——迁移完成后从蓝图删除。
> M1（mcp_servers→mcp/）和 M2（tool_contracts内嵌→独立YAML）均已完成，已删除。

---

## §6 核心调用流程

### 6.1 IDE/Agent → MCP Server 典型交互

| 步骤 | 方向 | 消息 | 说明 |
|:---:|------|------|------|
| 1 | IDE → Server | stdio connect | 建立 stdin/stdout 管道 |
| 2 | IDE → Server | `initialize` | 返回 capabilities + serverInfo |
| 3 | IDE → Server | `tools/list` | 返回注册的全部工具 |
| 4 | IDE → Server | `tools/call` | 执行工具 → 返回结果 |
| 5 | IDE → Server | stdin EOF | session end → server 退出 |

### 6.2 跨 Server 编排流程（Agent 串联）

| 步骤 | 工具调用 | 返回 |
|:---:|---------|------|
| 1 | `task_manager.decompose_blueprint("MOD-INF-013")` | 子任务列表 [T1, T2, T3] |
| 2 | `knowledge_base.search("MCP authentication patterns")` | 相关 KE 列表 |
| 3 | `gate_engine.run_g4_contract({...})` | PASS/FAIL + 裁决理由 |
| 4 | `session_handoff.validate_doc_version({...})` | 版本校验结果 |

---

## §7 集成依赖

| 文件 | 更新内容 | 优先级 |
|------|---------|:---:|
| `shared_quickref.yaml` | MCP Server 消费者注册（当前 consumer_count 已从 9→17） | 🔴 |
| `AGENTS.md` | MCP 施工硬约束（6 条）| 🔴 |
| `pyproject.toml` | 追加 `mcp>=1.0.0` 依赖 | 🔴 |
| `requirements.txt` | 追加 `mcp>=1.0.0` 依赖 | 🔴 |
| `.env.example` | MCP 环境变量专节 | 🟡 |
| `docker-compose.yml` | MCP 服务编排 | 🟡 |
| `.pre-commit-config.yaml` | MCP 专项 gate | 🟡 |
| `ai_autonomy_authority_registry.yaml` | 目录自治级别修正（mcp/ 标记为 Human-Gated 但实际 100% AI 施工） | 🟡 |
| `directory-standard.md` | mcp/ 职责定义修正（"客户端"→"服务端"） | 🟡 |

---

## §8 交付物清单

> 代码文件见 §0.1。本节仅列出非代码交付物。

| 交付物 | 路径 | 状态 |
|------|------|:---:|
| 工具契约 SSoT | `src/zephyr/integration/mcp/tool-contracts.yaml` | ✅ |
| MCP 路由配置 | `config/blueprint_routing.yaml` | ✅ |
| IDE MCP 配置 SSoT | `config/mcp.json` | ❌ |
| 启动脚本 | `scripts/mcp/start_all.py` | ❌ |
| Makefile | `Makefile` | ❌ |
| MCP 威胁建模 | `docs/13_security/mcp-threat-model.md` | ❌ |

---

## §9 已知风险与缓解

> 本节同时承接原 §10 后果中的**负面后果**——设计决策带来的已知代价。
> 正面后果与 §1 目标重复，不在此记录。

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| R1 | **stdio 阻塞风险**——当前循环在 stdin.readline() 阻塞等待，一个慢请求阻塞所有后续请求 | 确定 | 🔴高 | Phase 4 引入 asyncio 或线程池处理并发请求 | 风险 |
| R2 | **无 RBAC 强制执行**——safety_level L/M/H 在 YAML 中定义但 `_handle_tools_call` 不检查 | 确定 | 🔴高 | 在工具调用入口添加 safety_level 检查，与 MOD-INF-018 对齐 | 风险 |
| R3 | **契约漂移**——tool_contracts.yaml 新增/修改后代码不同步 | 高 | 🔴高 | pre-commit hook：代码中的 input_schema 必须与 YAML 一致 | 风险 |
| R4 | **session_handoff 文件命名混乱**——文件叫 doc_guard_server.py 但 server_id 是 session_handoff | 确定 | 🟡中 | AGENTS.md 中硬约束声明此差异不可"修复" | 风险 |
| R5 | **intent_router 文件命名混乱**——文件叫 sentinel_server.py 但 server_id 是 intent_router | 确定 | 🟡中 | 同上 | 风险 |
| R6 | **无超时机制**——tool handler 同步执行无超时，慢 handler 永久阻塞 | 确定 | 🔴高 | `asyncio.wait_for(handler(**args), timeout=30)` | 风险 |
| R7 | **4 个 skeleton Server 全部 copy-paste 同一模板** | 确定 | 🟡中 | 重构为 `@register_tool` 装饰器 + 统一模板 | 风险 |
| R8 | **idempotency 缺失**——task_manager 的 create_task tool 声明 `idempotent: true` 但 code 不检查输入 hash 缓存 | 确定 | 🟡中 | 实现输入 hash 缓存 | 风险 |
| R9 | **无 Observer 告警**——MCP Server 崩溃/超时/异常无任何外部通知 | 确定 | 🔴高 | 实现 healthz/readyz + Prometheus metrics | 风险 |
| R10 | **测试不执行**——CI governance.yml 只 `--collect-only`，从不 `pytest -x` | 确定 | 🔴高 | CI 中改为 `pytest tests/ -x --timeout=120` | 风险 |
| R11 | **Content-Length 帧解析缺失**——MCP spec 要求 Content-Length 前缀帧格式 | 确定 | 🟡中 | 实现 Content-Length header 解析逻辑 | 风险 |
| R12 | **无多 session 并发安全设计（B82）** | 中 | 🟡中 | Phase 5 Gateway 引入乐观锁 + BUSY 重试 | 风险 |
| R13 | **金融合规标签缺失（B66）** | 中 | 🟡中 | 新增 `compliance_tags` 字段 | 风险 |
| R14 | **mcp>=1.0.0 未在依赖文件中声明（B67）** | 确定 | 🔴高 | 三处同步追加 `mcp>=1.0.0` | 风险 |
| R15 | **AGENTS.md 零 MCP 内容（B68）** | 中 | 🔴高 | AGENTS.md §8.2 任务菜单已新增 MCP 条目 | 风险 |
| R16 | **全工程无 IDE MCP 配置文件（B69）** | 确定 | 🔴高 | 创建 `config/mcp.json` SSoT | 风险 |
| R17 | **scripts/mcp/ 目录不存在（B70）** | 确定 | 🔴高 | 创建 `scripts/mcp/start_all.py` + `stop_all.py` + `status_all.py` | 风险 |
| NC1 | MCP Gateway 未完成 → 7 Server 直连，无中间治理层 | 确定 | 🔴高 | Phase 5 实现 Gateway | 负面后果 |
| NC2 | Resource/Prompt 原语未实现 → Agent 架构退化为纯 Tool 模式 | 确定 | 🟡中 | Phase 6 补全 | 负面后果 |
| NC3 | sandbox 未实现 → AI 生成代码无法安全执行验证 | 确定 | 🟡中 | Phase 7 实现 | 负面后果 |
| NC4 | 全链路压力测试未执行 → 不知道系统承压极限 | 确定 | 🔴高 | Phase 8 执行 | 负面后果 |
| NC5 | 1人+AI 验收未完成 → 不知道维护复杂度 | 确定 | 🟡中 | Phase 9 验收 | 负面后果 |

> R18-R233 详细风险项见 §16 盲点补全汇总。以下仅列出 P0 级关键风险：

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| R18 | 缺 MCP 专项共享测试基础设施（B71） | 确定 | 🟡中 | 新增 `mcp_client_factory` / `tmp_chroma` / `tmp_mcp_session` fixture | 风险 |
| R33 | 全工程无 MCP 专项安全审计（B86） | 低 | 🔴高 | 新增 `docs/13_security/mcp-threat-model.md` | 风险 |
| R34 | MCP Server 无法互调（B87）——MCP孤岛 | 中 | 🔴高 | `_base_server.py` 新增 `invoke_tool()` 方法 | 风险 |
| R44 | MCP Server 进程生命周期零管理（B97） | 中 | 🔴高 | PID file + kill 旧进程 + stdin 心跳超时 | 风险 |
| R50 | tool-contracts 无跨 tool 前置约束声明（B103） | 中 | 🔴高 | 新增 `depends_on: [{tool_id, required_outcome}]` 字段 | 风险 |
| R54 | MCP Server 全量内存占用无评估（B107） | 中 | 🔴高 | 每个 Server 记录 RSS；建立内存预算表 | 风险 |
| R66 | 无 MCP incident response runbook（B119） | 中 | 🔴高 | 新增 `runbook.md`：≥8 个 incident scenario | 风险 |
| R68 | 无 AI agent 集成测试（B121） | 中 | 🔴高 | 新增 `test_mcp_with_ai_agent.py` | 风险 |
| R89 | 零能力退化检测（B142） | 中 | 🔴高 | `test_mcp_capability_contract.py`：tools/list vs YAML 100% 一致性 | 风险 |
| R100 | 零工具执行超时——慢/死工具可永久挂起（B153） | 中 | 🔴高 | tool-contracts.yaml 新增 `timeout_ms` 字段 | 风险 |
| R134 | 零 STRIDE/DREAD 威胁模型（B187） | 高 | 🔴高 | 新增 `mcp-threat-model.md` | 风险 |
| R135 | 零工具参数输入净化——语义注入攻击全敞口（B188） | 高 | 🔴高 | `_base_server.py` 新增 `_sanitize_arguments()` | 风险 |
| R145 | 零工具参数 Fuzzing（B198） | 高 | 🔴高 | 新增 fuzz 测试 | 风险 |
| R150 | 零高风险(safety_level=H)工具确认流（B203） | 高 | 🔴高 | `_base_server.py` 新增 `require_confirmation` 逻辑 | 风险 |
| R154 | 零优雅关闭——SIGTERM/SIGINT 无处理（B207） | 高 | 🔴高 | `signal.signal()` + drain+cleanup | 风险 |
| R207 | 零 MCP 进程守护与崩溃自动恢复（B260） | 高 | 🔴高 | supervisor/watchdog 设计 | 风险 |
| R215 | 零 AI 可执行的架构适应度函数（B268） | 高 | 🔴高 | per-dimension fitness functions | 风险 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-TASK_SYSTEM | 必须 | task_manager MCP——decompose_blueprint接口 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\task-repo\blueprint.md` |
| MOD-KB-001 | 必须 | knowledge_base MCP——KE查询接口 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\knowledge_base\blueprint.md` |
| MOD-GATE_ENGINE | 必须 | gate_engine MCP——Gate判定接口 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\gate_engine\blueprint.md` |
| b_mcp.yaml | 必须 | MCP YAML SSoT | — | `D:\ZephyrAlpha\architecture_model\layers\b_mcp.yaml` |
| mcp | 必须 | MCP SDK | ≥1.0.0 | — |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-013` |
| 2 | §11 产出物路径 ↔ 依赖图 path_mappings | 路径一致 | 未对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 未对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| `_base_server.py` | 所有 `*_server.py` | 基类定义 | `import` 成功 |
| `tool_contracts.yaml` | `_base_server.py` | 工具契约注册 | `tools/list` 返回完整 |
| `error_codes.py` | `_base_server.py` | 错误码定义 | `MCPError` 可用 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| `task_manager_server.py` | `knowledge_base_server.py` | 任务上下文 | AI Agent 中转 |
| `blueprint_search_server.py` | `task_manager_server.py` | 蓝图检索结果 | AI Agent 中转 |
| `gateway_server.py` | 所有 `*_server.py` | 路由/限流/审计 | Gateway 代理 |

#### Server 启动依赖 DAG

| Server | 依赖 | 被依赖 |
|--------|------|--------|
| knowledge_base | ChromaDB, SQLite | task_manager |
| gate_engine | ChromaDB, SQLite | task_manager |
| blueprint_search | ChromaDB | session_handoff |
| task_manager | knowledge_base, gate_engine | session_handoff |
| session_handoff | task_manager, blueprint_search | intent_router |
| intent_router | session_handoff | — |

> 启动顺序：ChromaDB/SQLite → knowledge_base / gate_engine / blueprint_search（并行）→ task_manager → session_handoff → intent_router

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 19 个 .py 文件 + 7 个 Server 间依赖 |
| 2 | 依赖对齐自动验证 | 是 | 有外部依赖（MOD-TASK_SYSTEM/007, MOD-KB-001） |
| 3 | 临时时态内容自动清理 | 是 | §0 蓝图升级计划为临时时态 |
| 4 | 施工步骤完成度自动检测 | 是 | construction_progress = completed |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖图自动生成 | AST解析import + manifest字段 | asset-inventory/dependency.py | 不覆盖mcp/目录 |
| 2 | 依赖对齐自动验证 | CI门禁 | validate_path_alignment.py | 无 |
| 3 | 临时时态内容自动清理 | 压缩工作流脚本 | 无 | 需新建 |
| 4 | 施工步骤完成度自动检测 | pytest+mypy+ruff + 产出物存在性检查 | 部分有 | 需整合 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖图自动生成 | CI pipeline | 文件变更时 |
| 2 | 依赖对齐自动验证 | CI门禁 | PR提交时 |
| 3 | 临时时态内容自动清理 | 手动 | 压缩工作流执行时 |
| 4 | 施工步骤完成度自动检测 | CI pipeline | 代码提交时 |

---

## §11 施工指引

### 11.2 氛围编程专项施工原则

| 原则 | 说明 |
|------|------|
| **一切决策写入文件** | vibe coding 下 AI session 无持久记忆——所有约定写入 AGENTS.md + 本蓝图 |
| **一切信息工具化** | blueprint_search server 将所有蓝图决策变为 tool 调用——AI 在 IDE 里就能查 |
| **一切变动可追溯** | tool-contracts.yaml 版本号 + 变更字段 diff → git blame 可追溯 |
| **一切边界写死** | Gate Engine（G4/G5/G6）作为硬约束，AI 不能绕过 |

### 11.3 施工约束

| 约束 | 来源 |
|------|------|
| **LLM 预算不可超 $2.00/任务卡** | GOV-AI-002 + tool-contracts.yaml |
| **模型路由策略不可被 AI 改写** | GOV-AI-002 + Gate Engine |
| **safety_level L 的 tool 无限制；M 需确认；H 需 Owner 审批** | MOD-INF-018 + tool-contracts.yaml |
| **新增 tool 前必须先改 tool-contracts.yaml** | 本蓝图 §3.2 |

### 11.4 自动化脚本

| 脚本 | 路径 | 用途 | 状态 |
|------|------|------|:---:|
| start_all.py | `scripts/mcp/start_all.py` | 按依赖顺序启动 7 个 MCP Server | ❌ |
| stop_all.py | `scripts/mcp/stop_all.py` | 优雅关闭所有 Server | ❌ |
| status_all.py | `scripts/mcp/status_all.py` | 检查所有 Server 的 healthz | ❌ |
| generate_ide_config.py | `scripts/mcp/generate_ide_config.py` | 从 `config/mcp.json` SSoT 生成各 IDE 配置文件 | ❌ |

---

## §12 MCP Gateway 架构

| 层级 | 组件 | 职责 | 依赖 |
|:---:|------|------|------|
| L1 | Auth/ACL | 认证+授权 | MOD-INF-018 |
| L2 | RateLimit | 限流（10 req/s per client） | — |
| L3 | Route | 7 Server 路由分发 | — |
| L4 | Audit | 全量工具调用审计日志 | — |
| L5 | Degrade | 降级策略（Circuit Breaker） | — |

> 请求流向：外部 IDE/Agent → Gateway(L1→L2→L3→L4→L5) → 7 个 MCP Server

---

## §13 安全机制

### 13.1 OS 级进程隔离

- 每个 MCP Server 为独立 Python 进程
- stdio 管道隔离——无网络暴露
- 单进程崩溃不影响其他 Server

### 13.2 Gate 级别硬合规

| Gate | 检查内容 | 实现状态 |
|:---:|------|:---:|
| G4 | 结构化输出契约校验（JSON Schema 校验 tool 返回结果） | 🔶 skeleton |
| G5 | AI 代码质量门禁（lint/typecheck 通过率） | 🔶 skeleton |
| G6 | 蓝图合规触发（施工前自动查对应蓝图） | 🔶 skeleton |

### 13.3 工具级 safety_level

| Level | 含义 | 控制方式 |
|:---:|------|------|
| L | 低风险——无限制 | 直接执行 |
| M | 中风险——需确认 | 返回确认提示，Agent 再次调用 |
| H | 高风险——需 Owner 审批 | 返回审批请求，Agent 暂停等待 |

### 13.4 健康检查

- `healthz`：进程存活 + 关键依赖可用
- `readyz`：可服务（所有 tool handler 初始化完毕）
- 暴露为 MCP Tool：`{server_id}.health_check`

---

## §14 Server 依赖 DAG

| Server | 依赖 | 被依赖 |
|--------|------|--------|
| knowledge_base | ChromaDB, SQLite | task_manager |
| gate_engine | ChromaDB, SQLite | task_manager |
| blueprint_search | ChromaDB | session_handoff |
| task_manager | knowledge_base, gate_engine | session_handoff |
| session_handoff | task_manager, blueprint_search | intent_router |
| intent_router | session_handoff | — |

> 启动顺序：ChromaDB/SQLite → knowledge_base / gate_engine / blueprint_search（并行）→ task_manager → session_handoff → intent_router

---

## §15 氛围编程运维优化

### 15.1 AGENTS.md 硬约束（AI 冷启动零次理解成本）

1. MCP 模块的 canonical 真源是 `b_mcp.yaml` + `tool_contracts.yaml`
2. MCP Server 的 server_id 不可改——它是 MCP 协议契约
3. 新增 MCP tool 必须先改 `tool_contracts.yaml` 再写代码
4. MCP Server 日志强制走 `structlog` + `sys.stderr`（禁止 `print()` 到 stdout）
5. IDE 配置由 `config/mcp.json` SSoT 生成，不手写各 IDE 目录下的 mcp.json
6. blueprint_search 是 vibe coding 场景的「上下文导航器」——新增蓝图后更新 `config/blueprint_routing.yaml`

### 15.2 IDE 能力矩阵

| IDE | MCP 支持 | mcp.json 位置 | 建立 |
|:---|:---:|------|:---:|
| Trae | ✅ 支持 | `.trae/mcp.json` | 高 |
| Cursor | ✅ 支持 | `.cursor/mcp.json` | 高 |
| Claude Code | ✅ 支持 | `.claude/mcp.json` | 中 |
| VS Code (Copilot) | 🔶 扩展 | `.vscode/mcp.json` | 低 |

### 15.3 调试开关

- `ZEPHYR_DEBUG_MCP=1`：打印 JSON-RPC 原始请求/响应到 stderr
- `ZEPHYR_MCP_LOG_LEVEL=DEBUG`：开启逐请求追踪日志
- `ZEPHYR_MCP_TIMEOUT=30`：修改全域 tool handler 超时（秒）

### 15.4 文档同步策略

| 本蓝图声称 | 检查机制 | 频率 |
|------|------|:---:|
| 所有代码路径存在 | `scripts/governance/verify_file_paths.py`（待新增） | pre-commit |
| tool-contracts.yaml 无漂移 | 契约对比脚本（待新增） | pre-commit |
| AGENTS.md 包含 MCP 硬约束 | 手动检查 §8.2 任务菜单 | 每周 |

### 15.5 降级策略

| 场景 | 响应 |
|------|------|
| ChromaDB 不可达 | knowledge_base / blueprint_search → `unavailable` 状态 → 返回错误 |
| SQLite 不可达 | 全局 → `unhealthy` → 503 |
| MCP Gateway 不可达 | 降级为直连模式（7 Server 直接对外） |
| 单 Server OOM | 该 Server 的 stdio 管道断开 → IDE 感知到可用工具减少 |

### 15.6 Token 预算与成本追踪

| 条目 | 预算 | 追踪粒度 | 实施 |
|------|------|:---:|:---:|
| 单 Session LLM 成本 | ≤ $2.00 | Session | 📋 工具端无计数 |
| 单 tool call 预估 | ≤ 8000 tokens | 调用 | 📋 待 YAML 新增 `estimated_tokens` |
| 超预算处理 | 返回 `budget_exceeded` error | 实时 | 📋 待实现 |

---

## §16 盲点补全汇总（B1-B357）

> 来源：规格化 STEP 0.5.0 内容价值映射——分类为"蓝图特有"
> 不可砍理由：砍掉 = AI 施工时不知道有哪些已知缺陷需要处理

### 盲点总览

| 轮次 | 盲点范围 | 审计维度 | 🔴 P0 | 🟡 P1 | 📋 P2 |
|:---:|---------|---------|:---:|:---:|:---:|
| 1-5 | B1-B66 | 结构完整性+消费者契约+源码审计+生产就绪+跨模块引用 | 16 | 46 | 4 |
| 6-10 | B67-B116 | 构建系统+数据安全+进程通信+生命周期+内存经济学 | 14 | 35 | 0 |
| 11-15 | B117-B166 | SLO/SLA+国际化+部署+MCP协议合规+蓝图模板合规 | 18 | 30 | 0 |
| 16-20 | B167-B216 | 设计深度+基础设施+安全威胁+测试方法论+生命周期编排 | 16 | 35 | 0 |
| 21-25 | B217-B266 | 性能工程+开发者体验+弹性工程+治理集成+运行时契约 | 11 | 39 | 0 |
| 26-30 | B267-B316 | AI驱动演进+MCP Spec差距+社区模式+自愈+外部取证 | 18 | 21 | 8 |
| 31-35 | B317-B357 | 依赖hash+自优化+韧性+自主性+语义完整性 | 10 | 30 | 1 |
| **合计** | **B1-B357** | | **103** | **236** | **13** |

### P0 级盲点清单（必须修复）

| # | 盲点 | 严重度 | 对应§9风险 |
|---|------|:---:|---------|
| B1 | 缺 Gateway 集中式安全层 | 🔴 | NC1 |
| B2 | 缺 Resource 原语 | 🔴 | NC2 |
| B3 | 缺 Prompt 原语 | 🔴 | NC2 |
| B4 | 缺沙箱执行环境 | 🔴 | NC3 |
| B8 | 缺熔断/降级 | 🔴 | R1 |
| B9 | 缺审计日志 | 🔴 | — |
| B31 | 缺优雅关闭 SIGINT/SIGTERM | 🔴 | R154 |
| B37 | safety_level 零代码执行 | 🔴 | R2 |
| B47 | CI 测试收集但从不执行 | 🔴 | R10 |
| B87 | MCP Server 无法互调（MCP孤岛） | 🔴 | R34 |
| B97 | 进程生命周期零管理 | 🔴 | R44 |
| B107 | 全量内存无评估 | 🔴 | R54 |
| B117 | 无 MCP SLO | 🔴 | — |
| B147 | 协议方法仅 4/20+ | 🔴 | — |
| B184 | 零 STRIDE/DREAD 威胁模型 | 🔴 | R134 |
| B188 | 零工具参数输入净化 | 🔴 | R135 |
| B197 | 零 Property-based Testing | 🔴 | R145 |
| B207 | 零优雅关闭 SIGTERM drain | 🔴 | R154 |
| B277 | 零异步 Tasks 支持（SEP-1686） | 🔴 | — |
| B307 | MCP STDIO RCE 协议层漏洞（OX Security） | 🔴 | — |
| B308 | Tool Description 作为可执行代码的安全审查 | 🔴 | — |
| B309 | Context Budget 爆炸与 Lazy Schema Loading | 🔴 | — |
| B310 | 僵尸进程级联内存枯竭 | 🔴 | — |
| B311 | Rug Pull 攻击向量 | 🔴 | — |
| B317 | 零依赖完整性 hash 锁文件 | 🔴 | — |
| B330 | 零 AI 自我纠错循环检测与熔断 | 🔴 | — |
| B336 | 零 AI 会话预算实时计量 | 🔴 | — |
| B348 | 零工具输出语义防线 | 🔴 | — |

### 已知未知（持续监控）

| 盲点 | 描述 | 监控方式 |
|------|------|---------|
| B313 | MCP vs CLI 架构生存风险 | CLI shim layer + A/B test |
| B314 | Anthropic 利益冲突/供应商风险 | vendor_lockin_risk_score + 双栈接口 |

---

## §17 容量升级附录

### 17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| MCP Server 进程数 | 7+ | `ps aux | grep mcp` |
| 峰值内存 | ~2GB | psutil RSS 采样 |
| 并发 AI 数 | 1（实验性） | 单 Agent 测试 |

### 17.2 缺口与升级矩阵

| 缺口ID | 当前瓶颈 | 升级方案 | 触发阈值 | 代码文件 | 施工Phase |
|--------|---------|---------|---------|---------|----------|
| GAP-001 | 同步阻塞 stdin → ≤5 并发 | asyncio + ThreadPoolExecutor | AI 并发 > 5 | `_base_server.py` | Phase B2 |
| GAP-002 | 全量扫描 268 脚本 → 3.5h | 增量扫描匹配引擎 | 脚本数 > 500 | 新建 | Phase B3 |
| GAP-003 | 顺序执行 → 无并发 | Worker Pool (40-100 worker) | 脚本并发需求 > 10 | 新建 | Phase B4 |
| GAP-004 | 单进程 Orchestrator → ≤10 AI | Distributed (ARQ+Redis/NATS) | AI 并发 > 10 | 新建 | Phase B12 |

---

## §18 决策记录

> **时态属性**：决策记录属于**永久时态**——AI 修改设计时必读。没有它，AI 会重复犯已排除的错误。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-MCP-01 | 传输协议选择 | stdio / SSE / HTTP | stdio | 本地单机部署，无网络层需求，MCP 规范 stdio 为默认 | 2026-05-03 |
| 2 | D-MCP-02 | SDK 选择 | FastMCP / BaseMCPServer | 双轨并行 | task_manager 已用 FastMCP，其余用 BaseMCPServer | 2026-05-03 |
| 3 | D-MCP-03 | Gateway 集中式 vs 分布式 | 集中式 / 分布式 | 集中式 | 7 Server 规模下集中式更简单，100+ AI 并发时再迁移分布式 | 2026-05-05 |
| 4 | D-MCP-04 | server_id 命名保留差异 | 修正文件名 / 保留 | 保留 | server_id 是 MCP 协议契约标识，修改会破坏兼容性 | 2026-05-05 |
| 5 | D-MCP-05 | 盲点审计终止条件 | 继续审计 / 闭合 | 闭合（35轮） | 30轮后仅重复/微调，无新增结构性盲点 | 2026-05-06 |

---

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> MCP服务器——task_manager decompose_blueprint已实现

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/integration/mcp/_base_server.py` | ✅ 已实现 | |
| `src/zephyr/integration/mcp/audit_logger.py` | ✅ 已实现 | |
| `src/zephyr/integration/mcp/blueprint_search_server.py` | ✅ 已实现 | |
| `src/zephyr/integration/mcp/doc_guard_server.py` | ✅ 已实现 | |
| `src/zephyr/integration/mcp/error_codes.py` | ✅ 已实现 | |
| `src/zephyr/integration/mcp/gate_engine_server.py` | ✅ 已实现 | |
| `src/zephyr/integration/mcp/gateway_server.py` | ✅ 已实现 | |
| `src/zephyr/integration/mcp/governance_server.py` | ✅ 已实现 | |
| `src/zephyr/integration/mcp/handoff_auto_loader.py` | ✅ 已实现 | |
| `src/zephyr/integration/mcp/knowledge_base_server.py` | ✅ 已实现 | |
| `src/zephyr/integration/mcp/prompt_provider.py` | ✅ 已实现 | |
| `src/zephyr/integration/mcp/rate_limiter.py` | ✅ 已实现 | |
| `src/zephyr/integration/mcp/resource_provider.py` | ✅ 已实现 | |
| `src/zephyr/integration/mcp/sandbox_server.py` | ✅ 已实现 | |
| `src/zephyr/integration/mcp/sentinel_server.py` | ✅ 已实现 | |
| `src/zephyr/integration/mcp/task_manager_server.py` | ✅ 已实现 | |
| `src/zephyr/integration/mcp/telemetry_server.py` | ✅ 已实现 | |
| `src/zephyr/integration/mcp/tool-contracts.yaml` | ✅ 已实现 | |
| `src/zephyr/integration/mcp/vector_memory_server.py` | ✅ 已实现 | |

### 1.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/test_mcp_servers.py` | ✅ 已实现 | |
| `tests/integration/test_mcp_e2e.py` | ✅ 已实现 | |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| MCP Server 架构设计 | **本文档 §1-§3** | b_mcp.yaml（协议层真源，非蓝图层） |
| MCP 施工步骤 | **本文档 §11** | — |
| MCP 接口契约 | **本文档 §3** | tool-contracts.yaml（派生） |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | — |
| 盲点全量清单 | **本文档 §16** | — |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | MOD-TASK_SYSTEM task-repo 蓝图 | §3 接口契约 |
| Tier 2 | MOD-INF-005 agent-orchestrator | §3 MCP 通信协议 |
| Tier 3 | `src/zephyr/integration/mcp/*.py` 代码文件 | §3 数据模型、§11 产出物路径 |

### 变更同步规则

| 变更类型 | Tier 1（下游蓝图） | Tier 2（集成系统） |
|---------|------------------|------------------|
| 新增/修改接口契约 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 修改施工步骤 | 下游更新产出物引用 | 更新配置文件 |
| 修改模块边界 | 下游更新依赖声明 | 更新集成路由 |
| 新增容量升级组件（§17） | 下游评估影响 | 更新容量预算 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 接口契约新增/修改（§3） | 需 Owner 审批 + 通知所有消费者 |
| 模块边界修改（§2） | 需 Owner 审批 |
| construction_progress 变更 | 需 §0 对齐验证通过 |
| 施工步骤微调 | AI 可自主修改 |
| 非关键补充 | AI 可自主修改 |
| 容量升级方案新增（§17） | 需 Owner 审批 |

### 触发条件

| 触发场景 | 关键词/操作 |
|---------|-----------|
| 新增/修改 MCP Server | `mcp_server` / `tool_contracts` / `server_id` |
| MCP 工具调用异常 | `tools/call` / `MCPError` / `-32001` |
| MCP 容量规划 | `并发` / `QPS` / `容量` / `GAP-00` |
| MCP 安全审计 | `safety_level` / `RBAC` / `威胁模型` |
| IDE MCP 配置 | `mcp.json` / `stdio` / `MCP Gateway` |

### 导航路径

```
新 AI → registry_of_registries.yaml → MOD-INF-013 → 本蓝图
     → AGENTS.md §8.2 MCP 任务菜单 → 本蓝图 §11 施工指引
     → src/zephyr/integration/mcp/tool-contracts.yaml → 本蓝图 §3 契约定义
```

### 漂移防护

| 修改本蓝图 | MUST 同步更新 |
|-----------|-------------|
| §3 接口契约 | `src/zephyr/integration/mcp/tool-contracts.yaml` + 下游消费者蓝图 |
| §2 MCP 服务端列表 | `src/zephyr/integration/mcp/__init__.py` + `architecture_model/layers/b_mcp.yaml` |
| §11 施工步骤 | `AGENTS.md` §8.2 MCP 任务菜单 |
| §0 代码对齐验证 | `src/zephyr/integration/mcp/` 对应代码文件 `[BLUEPRINT]` 头部 |
| §17 容量升级 | `config/capacity_slo.yaml` + capacity_assurance 蓝图 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径（含盘符 `D:\`） | 文件创建到错误位置 |
| 2 | 必备链接不可省略 | AI 跳过不读，施工时缺少关键信息 |
| 3 | 蓝图必须是最终设计结果 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉——文件放错位置 |
| 5 | 涉及文件范围必须明确列出 | 范围漂移——改了不该改的文件 |
| 6 | 容量估算必须写 | 容量瓶颈——上线后发现不够用 |
| 7 | 迁移/废弃方案必须写 | 断链或垃圾积累 |
| 8 | "待定"/"建议"/"按需"等模糊词禁止使用 | 执行漂移——AI 自行决定 |
| 9 | 蓝图必须自包含 | 信息缺失——AI 缺少关键上下文 |
| 10 | 删除文件必须遵守安全删除协议 | 永久丢失——无法恢复 |
| 11 | construction_progress 必须与代码实际状态一致 | 误导下一个AI |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索失败、导入错误 |
| 13 | **已实现代码不在蓝图中重复**——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | 代码文件是 SSoT，蓝图复制代码=双源漂移 |
| 14 | **临时时态内容执行完毕后从蓝图删除**——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除。蓝图只保留永久时态内容 | 蓝图膨胀，关键信息被历史噪音淹没 |
| 15 | **蓝图内容拆分判定**——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | 职责不同的内容强行塞一个蓝图=职责不清 |

---

## 蓝图拆分判定标准

> 铁律 #15 的操作定义——当蓝图内容超过 ~800 行或包含多个独立职责域时，MUST 执行拆分判定。

### 判定流程

```
STEP 1: 识别职责域
  蓝图中的内容是否属于同一职责域？
  判定标准：该内容的服务对象、变更频率、依赖关系是否与蓝图主体一致？

STEP 2: 职责域判定
  ├ 职责相同（同一模块的升级/扩展）→ 原地升级
  │   条件：服务对象相同 + 变更频率同步 + 依赖关系重叠
  │   操作：在 §17 容量升级附录中增量记录
  │
  └ 职责不同（独立子系统/独立能力域）→ 拆分独立蓝图
      条件（满足任一即触发）：
      a) 有独立的 module_id 前缀
      b) 有独立的 Phase 路线图和交付节奏
      c) 有独立的依赖关系图（与蓝图主体的 depends_on 交集 <50%）
      d) 内容超过 100 行且与蓝图主体无直接数据流
      操作：创建子蓝图，本蓝图 §10 依赖关系引用子蓝图

STEP 3: 拆分后验证
  - 拆分出的蓝图 MUST 有独立 frontmatter + 概述 + §0~§18
  - 拆分出的蓝图 belongs_to = 本蓝图 module_id
  - 本蓝图 §10 依赖关系新增子蓝图引用
  - blueprint_registry.yaml 同步更新
```

### 本蓝图拆分判定

| 章节 | 服务对象 | 变更频率 | 与主体依赖交集 | 判定 |
|------|---------|---------|:---:|------|
| §12 MCP Gateway 架构 | MCP Server 用户 | 与主体同步 | 100% | 原地保留（蓝图特有） |
| §14 Server 依赖 DAG | MCP 运维 | 与主体同步 | 100% | 原地保留（蓝图特有） |
| §15 氛围编程运维优化 | AI 开发者 | 与主体同步 | 90% | 原地保留（蓝图特有） |
| §16 盲点补全汇总 | MCP 审计者 | 低频 | 80% | 原地保留（蓝图特有） |

> 结论：本蓝图所有章节服务对象相同、变更频率同步、依赖关系重叠 → **不拆分**。蓝图特有章节原地保留。

---

## ⚠️ 安全删除协议

本蓝图不涉及文件废弃/迁移/删除。升级计划中的文件变更通过新增实现，不删除现有文件。

---

## 必备链接

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type词表 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012 + MTH-013 |
| 4 | 文件命名规范 | GOV-DOC-003 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |

---

## 项目中已有类似功能

无。

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | MCP 实现目录 | `D:\ZephyrAlpha\src\zephyr\mcp\` | 读取 | 19 个 .py 文件 |
| 2 | MCP re-export shim | `D:\ZephyrAlpha\src\zephyr\mcp_servers\__init__.py` | 读取 | re-export |
| 3 | 工具契约 | `D:\ZephyrAlpha\src\zephyr\mcp\tool-contracts.yaml` | 读取 | 契约 SSoT |
| 4 | 蓝图路由配置 | `D:\ZephyrAlpha\config\blueprint_routing.yaml` | 读取 | blueprint_search 路由 |
| 5 | MCP YAML SSoT | `D:\ZephyrAlpha\architecture_model\layers\b_mcp.yaml` | 读取 | 协议真源 |
