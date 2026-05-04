---
module_id: ADR-0018
doc_type: adr
title: Agent Sandbox — Windows ACL 起步，Docker Desktop 升级路径
version: 1.0.0
status: active
date: '2026-04-24'
owner: ZephyrAlpha-Owner
ttl: permanent
related_adrs:
- ADR-0017
- ADR-0020
- ADR-0021
priority: P0
phase: Phase-1
tech_refs:
- TECH-12
layer: L12
classification: confidential
language: zh
created_by: agent
valid_from: '2026-04-24'
superseded_by: null
supersedes: null
related_rationale: []
related_open_questions: []
tags: [adr, vibe-coding]
summary: "**Vibe Coding 2.0 安全基石** Agent Sandbox（Windows ACL + Firewall + Job Object 三件套）| accepted"
---

# ADR-0018: Agent Sandbox — Windows ACL 起步，Docker Desktop 升级路径

**状态**：Accepted
**日期**：2026-04-24
**决策者**：ZephyrAlpha-Owner
**优先级**：P0
**阶段**：Phase 1 首批上线

---

## 1. 状态（Status）

- **当前状态**：`accepted`
- **提议日期**：2026-04-24
- **拍板日期**：2026-04-24

## 2. 背景与问题（Context）

### 2.1 问题陈述

`vibe-coding-audit-merged.md §Kimi 11.6.1` 识别出 **Agent 失控** 是 Vibe Coding 2.0 的 P0 安全根因之一（与 Prompt Injection 并列）。具体攻击路径：

- AI Agent 通过 MCP 工具获得 `execute_command` 能力
- 被 Prompt Injection 劫持后生成 `rm -rf /` 或 `git push --force` 之类破坏性命令
- 无沙箱隔离则**一次失控 = 整个代码库毁灭**

当前 Windows 单人开发环境，**零沙箱防护**（SEC-02 P0 缺口）。

### 2.2 约束条件

- **平台约束**：当前唯一开发平台 = **Windows 11**；Linux 容器原生（namespace / cgroups）不可用
- **性能约束**：Sandbox overhead 目标 < 10%（不能让 AI 编码变慢）
- **可用性约束**：单人系统，不能要求用户学习 Docker
- **升级性**：Phase 2 接入真实资金时必须可升级到完整容器隔离

### 2.3 参考真源

- `vibe-coding-audit-merged.md §Kimi 11.6.1 双 P0 根因（Agent 沙箱）`
- `vibe-coding-audit-merged.md §Qwen 选型表 #12`
- `agent-orchestrator-interface.md §7 Sandbox`
- `06-security-architecture.md §5`

---

## 3. 考虑过的方案（Options Considered）

### 方案 A：Windows ACL + 只读挂载（文件系统虚拟化）✅

- **优点**：
  - **零外部依赖**：Windows 原生 API，Python `pywin32` 可直接调用
  - **低 overhead**：ACL 是 OS 内核级，< 5%
  - **粒度细**：按文件 / 目录分别配置 RO/RW/DENY
  - **可审计**：Windows Security Event Log 原生记录
  - **Phase 1 合格**：防御"删库级"攻击足够
- **缺点**：
  - 网络隔离依赖 Windows Firewall 手动规则（非同一栈）
  - 资源配额（CPU/RAM）需额外机制（Job Object API）
  - 不如 Linux namespace 隔离严格，有已知绕过路径

### 方案 B：Docker Desktop + 容器挂载

- **优点**：完整隔离（网络 + 文件系统 + 资源）；跨平台
- **缺点**：
  - Docker Desktop 个人版商业限制 + 10GB+ 内存占用
  - 每次 Agent 调用启动容器 overhead > 500ms
  - 单人系统 overkill
- **结论**：**保留为 Phase 2 升级路径**

### 方案 C：gVisor（用户态内核）

- **优点**：Google 设计的轻量级沙箱
- **缺点**：**Windows 兼容性差**（gVisor 主要 Linux）→ 直接否决

### 方案 D：WSL2 子系统 + Firejail

- **优点**：Linux 原生沙箱栈可用
- **缺点**：
  - WSL2 启动 overhead 大
  - Windows ↔ WSL2 文件系统性能衰减（9P 协议）
  - 需要维护两套代码路径
- **结论**：**否决（Phase 1）**

---

## 4. 决策（Decision）

**最终选择：方案 A — Windows ACL + 只读挂载 + Windows Firewall 出口规则 + Job Object 资源配额**

### 4.1 关键决策点

| 维度 | Phase 1 实现 | 升级触发 | Phase 2+ 目标 |
|------|-------------|---------|--------------|
| **文件系统隔离** | Windows ACL（RO/RW/DENY）| 首次资金接入或外部用户 | Docker Desktop 容器挂载 |
| **网络隔离** | Windows Firewall 出口白名单 | 同上 | Docker network + proxy |
| **资源配额** | Job Object (CPU/RAM limit) | 同上 | Docker resource limits |
| **命令执行** | Orc 命令解析器白名单 | — | 同 + 容器内白名单 |
| **环境变量** | 过滤 `SECRET_*` / `API_KEY_*` 前缀 | — | 同 |
| **日志** | Windows Security Event Log + 应用审计 | — | 容器日志 + 宿主机日志 |

### 4.2 沙箱规则（Phase 1）

| 资源类别 | 权限 | ACL 配置 |
|---------|:----:|---------|
| `src/` | RO | ACE: ReadData + ReadAttributes |
| `docs/` | RO | ACE: ReadData |
| `tests/` | RO | ACE: ReadData |
| `.runtime/sandbox-work/` | RW | ACE: Full（Agent 唯一写区）|
| `.runtime/chromadb/` | RW（部分）| ACE: Append + WriteData（不可删除）|
| `.env` / `*.key` / `secrets/` | DENY | ACE: DENY all |
| `C:\Users\*\` 除工作区外 | DENY | ACE: DENY all |
| `C:\Windows\` | DENY | ACE: DENY all |

### 4.3 命令白名单（Phase 1）

**允许**：`python` / `pytest` / `git status/log/diff`（只读）/ `mkdocs build` / `ruff` / `mypy` / `black`

**禁止**：`rm` / `del` / `git push/reset/rebase` / `curl/wget`（未白名单 URL）/ `powershell` / `cmd /c` / `net` / `sc` / `reg`

### 4.4 网络出口白名单

- LLM Provider API 域名（按 vibe_config.yaml 声明）
- `127.0.0.1` 任意端口（本地服务）
- `pypi.org` + `files.pythonhosted.org`（依赖安装，仅在 `dev` 模式）

其他目标 → Windows Firewall DROP + 审计日志。

### 4.5 资源配额（Job Object）

| 指标 | 默认值 | 可配 |
|------|:------:|:---:|
| 内存上限 | 2 GB | `vibe_config.yaml::sandbox.memory_mb` |
| CPU 上限 | 2 核 | `vibe_config.yaml::sandbox.cpu_cores` |
| 进程数 | 20 | — |
| 运行时长 | 30 分钟 | 超时强制 kill |

---

## 5. 后果（Consequences）

### 5.1 正面后果

- **SEC-02 P0 缺口修复**：防止 Agent 删库级攻击
- **LSG 双层防护**：与 ADR-0020 LSG 协同（LSG 前置 + Sandbox 运行时）
- **< 5% overhead**：ACL 是内核级，几乎无感
- **Phase 2 平滑升级**：同 `OrchestratorProtocol.sandbox_adapter`，切 Docker 零业务层改动

### 5.2 负面后果

- **Windows 专属**：本 ADR 在 Linux / macOS 不适用（但 Phase 1 约束平台即 Windows）
- **绕过风险**：熟悉 Windows 内部的攻击者可能通过 `\\?\` 路径规避 ACL；Phase 2 接入真实资金前**必须**升级容器隔离
- **Firewall 规则管理**：手动维护白名单，易漂移
- **PowerShell 禁用**：部分 Agent 工作流需手动适配（接受）

### 5.3 未来重新评估触发条件

- **TECH-12**：首次出现"需要网络隔离/资源配额强化"需求 → Docker Desktop
- **平台扩展**：Phase 2 团队成员使用 macOS / Linux → Sandbox 栈多实现
- **30 天内 > 0 逃逸事件** → 立即启动 Docker 升级，且本 ADR 进 superseded

---

## 6. 落地动作（Implementation）

| # | 动作 | 物理位置 | 估时 |
|---|------|---------|:----:|
| 1 | Sandbox 抽象接口 | `src/zephyr/orchestrator/sandbox/protocol.py` | 0.5 天 |
| 2 | Windows ACL 实现 | `src/zephyr/orchestrator/sandbox/windows_acl.py` | 1.5 天 |
| 3 | 命令白名单解析器 | `src/zephyr/orchestrator/sandbox/command_filter.py` | 0.5 天 |
| 4 | 环境变量过滤器 | `src/zephyr/orchestrator/sandbox/env_filter.py` | 0.5 天 |
| 5 | Job Object 资源配额 | `src/zephyr/orchestrator/sandbox/job_object.py` | 0.5 天 |
| 6 | Windows Firewall rule bootstrap | `scripts/infra/setup_sandbox_firewall.ps1` | 0.5 天 |
| 7 | 逃逸检测 + 告警 | `src/zephyr/orchestrator/sandbox/escape_detector.py` | 0.5 天 |
| 8 | IR-SEC-002 Runbook | `docs/10_operations_and_sre/runbooks/IR-SEC-002.md` | 0.5 天 |
| 9 | P0 测试组（10+ 越权场景）| `tests/orchestrator/sandbox/test_p0.py` | 1 天 |

**总工时**：约 5.5 人日

---

## 7. 参考

- **真源**：`vibe-coding-audit-merged.md §Kimi 11.6.1` + `§Qwen 选型表 #12`
- **接口规范**：[`agent-orchestrator-interface.md §7 Sandbox`](../../03_modules/_b_track_interfaces/agent-orchestrator-interface.md)
- **安全架构**：[`06-security-architecture.md §5`](../target-architecture/06-security-architecture.md)
- **技术选型**：[`technology-landscape.yaml TECH-12`](../target-architecture/architecture-model/technology/technology-landscape.yaml)
- **相关 ADR**：ADR-0017（Orchestrator 调用方）/ ADR-0020（LSG 协同双防）/ ADR-0021（SSoT 前置）
- **外部**：[Windows Job Objects (Microsoft Docs)](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects) / [Windows ACL (pywin32)](https://timgolden.me.uk/pywin32-docs/)

---

## 8. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-04-24 | v1.0.0 初版：Windows ACL + Firewall + Job Object 三件套；Phase 2 Docker Desktop 升级路径；B-e-5 产出。 |
| 2026-04-27 | v1.0.1 补充：Phase 1b L2a subprocess 沙箱已实施（`src/zephyr/llm_security/process_sandbox.py`），与 CBG 装饰器集成；CBAC capability_check 前置拦截；CLI 重置入口 `scripts/governance/cbg_reset.py`；T-V2-005 Step 9 GLM-5.1 文档。 |
