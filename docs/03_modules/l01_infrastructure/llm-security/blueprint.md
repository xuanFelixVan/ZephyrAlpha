---
module_id: "MOD-INF-014"
title: "LLM Security Gateway 蓝图 — 四层安全防御 + fail-closed 原则"
doc_type: blueprint
status: draft
version: "0.1.1"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-03"
valid_from: "2026-05-03"
ttl: permanent
construction_progress: phase_1_partial
summary: "ZephyrAlpha LLM Security Gateway (LSG) 蓝图——四层深度防御：L1输入净化(path/command/token白名单) → L2进程沙箱(subprocess路径白名单) → L3输出验证(待施工) → L4行为审计(structlog JSONL)。fail-closed原则：LSG不可用→拒绝所有LLM流量。当前施工30%：input_sanitizer已实现，其余骨架待填。对标 OWASP LLM Top 10 v3.0 + NIST AI RMF."
tags: [llm-security, lsg, security-gateway, fail-closed, input-sanitizer, process-sandbox, infrastructure]
priority: P2
depends_on:
  - {target: "MOD-INF-008", at: "全篇", why: "Context Engine——LSG消费CE的prompt内容做注入检测"}
  - {target: "_b_track_interfaces/llm-security-gateway-interface.md", at: "全篇", why: "LSG接口合同——输入/输出契约定义"}
---

# LLM Security Gateway 蓝图

> **module_id**: MOD-INF-014 | **version**: 0.1.0 | **status**: draft | **layer**: cross_layer

> **真源声明**：本蓝图的 canonical SSoT 为 LPC B 轨 `llm_security/` 代码目录。
> 代码落位：`src/zephyr/llm_security/`（4 个 .py 文件）。

> **对标**：OWASP Top 10 for LLM Applications v3.0 + NIST AI RMF 1.0 + OWASP ASVS §V10.

---

## 1. 概述

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-014 |
| 代码落位 | `src/zephyr/llm_security/` |
| 核心职责 | 所有 LLM 交互的安全门禁——输入→输出全链路防护 |
| 安全原则 | **fail-closed**：LSG 不可用 → 拒绝所有 LLM 流量，不 bypass |

### 核心职能

LSG 是 ZephyrAlpha 中**所有 LLM 调用的安全闸门**。任何 AI agent 在发起 LLM 请求前，输入必须经过 LSG L1/L2 检测；LLM 返回后，输出必须经过 L3/L4 检测。如果 LSG 宕机，系统拒绝所有 LLM 流量（fail-closed）——宁可停服，不可裸奔。

---

## 2. 四层防御架构

```
                LLM Request
                     │
          ┌──────────▼──────────┐
          │ L1: InputSanitizer  │  path whitelist + command whitelist + token budget
          │   input_sanitizer   │  检测: 路径遍历 / 命令注入 / Token超预算
          └──────────┬──────────┘
                     │ clean
          ┌──────────▼──────────┐
          │ L2: ProcessSandbox  │  subprocess 路径白名单 + 禁止高危命令
          │   process_sandbox   │  检测: 任意代码执行 / 权限提升
          └──────────┬──────────┘
                     │ safe ──────────► LLM Provider
                     │                        │
                     │ ◄── LLM Response ──────┘
                     │
          ┌──────────▼──────────┐
          │ L3: OutputValidator │  Pydantic Schema 验证 + Secret Scanner
          │   (待施工)          │  (experimental: Pydantic + OWASP LLM Top 10 规则集)
          └──────────┬──────────┘
                     │ valid
          ┌──────────▼──────────┐
          │ L4: AuditLogger     │  structlog JSONL 全量审计
          │ behavior_audit_log  │  异常检测: EMA 历史攻击模式
          └─────────────────────┘
```

---

## 3. 文件组成

| 文件 | 职责 | 施工状态 |
|------|------|:---:|
| `input_sanitizer.py` | L1 输入净化——path whitelist + command whitelist + token budget guard | ✅ 已实现 |
| `process_sandbox.py` | L2 进程沙箱——subprocess 路径白名单 + 高危命令禁止 | ✅ 骨架 |
| `__init__.py` | LSG 模块入口 + 架构文档注释 | ✅ 已实现 |
| `behavior_audit_logger.py` | L4 审计日志——structlog JSONL + EMA 异常模式 | ✅ 骨架 |

> L3（输出验证）尚未独立文件——experimental 施工。

---

## 4. L1 InputSanitizer

```python
# input_sanitizer.py 核心接口
class InputSanitizer:
    def sanitize(self, prompt: str, context: dict) -> SanitizeResult:
        """路径遍历检测 + 命令注入检测 + Token 预算守卫"""
```

**三条检查**：
- **Path Traversal**：拒绝 `../` / `..\\` / 绝对路径逃逸
- **Command Injection**：拒绝 shell 元字符（`|` / `;` / `$()` / 反引号）在 prompt 中出现
- **Token Budget**：prompt 长度超过 8000 token → 拒绝（对标 CE 预算约束）

### 4.1 Token Budget Guard

```
if token_count(prompt) > 8000:
    return SanitizeResult(
        allowed=False,
        reason="TOKEN_BUDGET_EXCEEDED",
        detail=f"Prompt tokens={token_count}, budget=8000"
    )
```

**对标**：Anthropic 的 "prompt injection resistance" + OWASP LLM01:2025 Prompt Injection.

---

## 5. L2 ProcessSandbox

```python
# process_sandbox.py 核心接口
class ProcessSandbox:
    ALLOWED_COMMANDS = ["git", "python", "npm", "cargo", "pip", "poetry"]

    def authorize(self, command: str, args: list[str]) -> AuthorizeResult:
        """检查命令是否在白名单中"""
```

**核心约束**：
- 仅允许 `ALLOWED_COMMANDS` 中的命令
- 禁止高危操作：`rm -rf` / `chmod 777` / `sudo` / `eval`
- 禁止写入 `/etc/` / `/System/` / Windows `C:\\Windows\\`

**对标**：gVisor 容器沙箱最小权限原则 + OWASP LLM06:2025 Excessive Agency.

---

## 6. L3 OutputValidator（待施工）

> experimental 施工范围

- **Pydantic Schema 验证**：LLM 返回的 JSON/YAML 必须符合预期 Schema
- **Secret Scanner**：扫描输出中是否泄露 API key / token / 密码
- **OWASP LLM Top 10 规则集**：检测 LLM02（数据泄露）/ LLM03（供应链）/ LLM07（数据投毒）

### 施工步骤

| 步骤 | 内容 | 预估工时 |
|------|------|:---:|
| 3.1 | 创建 `output_validator.py` | 3h |
| 3.2 | Pydantic Schema Registry 注册 | 2h |
| 3.3 | Secret Scanner（正则 + entropy check） | 2h |

---

## 7. L4 BehaviorAuditLogger

```python
# behavior_audit_logger.py 核心接口
class BehaviorAuditLogger:
    def log(self, event: AuditEvent) -> None:
        """structlog → JSONL 持久化"""

    def detect_anomaly(self, pattern: AttackPattern) -> AnomalyResult:
        """EMA 指数移动平均检测异常攻击模式"""
```

**审计原则**：
- Append-only：审计日志不可修改（对标 ITIL 审计追踪）
- Tamper-evident：JSONL 带 checksum，修改可检测
- EMA 异常检测：攻击频率超过历史均值的 2σ → 告警

**beta 目标**：红队语料库 ≥150 条 + 绕过率 ≤5%.

---

## 8. fail-closed 原则

```
LSG 健康检查失败
    │
    ├── L1 失败 → 拒绝所有 LLM 输入（不 bypass）
    ├── L2 失败 → 禁止所有 subprocess
    ├── L3 失败 → 拒绝所有 LLM 输出
    └── L4 失败 → 日志降级为 stderr fallback（审计不可中断）
```

**为什么 fail-closed 而不是 fail-open**：AI agent 被注入后的破坏力远大于暂时不可用。对标银行金库——宁可今天不营业，不可开着门让人随便拿。

**对标**：AWS IAM 的 "deny by default" 原则 + OWASP ASVS §V10.2.1.

---

## 9. 施工进度

| 阶段 | 完成度 | 说明 |
|------|:---:|------|
| scaffold | ✅ 100% | 4 文件骨架 + __init__.py 架构注释 |
| experimental | ██ 30% | input_sanitizer.py 已实现；process_sandbox 骨架 |
| experimental | ░░ 0% | output_validator.py 待创建；L3 规则集待定义 |
| beta | ░░ 0% | 红队语料库 150+ 条；绕过率评估 |

### 下一步施工

1. **P0**：`process_sandbox.py` 补齐 authorize() 实现
2. **P1**：`behavior_audit_logger.py` 补齐 log() + detect_anomaly()
3. **P2**：`output_validator.py` 创建 + Pydantic Schema Registry

---

## 10. 施工指引

### 10.1 process_sandbox 施工

```
1. 读取 ALLOWED_COMMANDS 白名单
2. 检查 command 是否在白名单 → 不在则 reject
3. 检查 args 是否含高危 flag（--eval / -c "rm"）→ 有则 reject
4. 检查工作目录是否在 src/zephyr/ 下 → 不在则 reject
5. 通过 → 放行 subprocess.run()
```

### 10.2 audit_logger 施工

```
1. 配置 structlog → JSONL 输出到 src/zephyr/llm_security/audit_logs/
2. log(event) → 写入一行 JSON（带 timestamp + event_id）
3. detect_anomaly(pattern) → 加载历史 7 天 EMA 基线 → 当前频率 > 2σ 则告警
```

### 10.3 测试清单

```
□ input_sanitizer 路径遍历检测（../  /etc/passwd 等）
□ input_sanitizer 命令注入检测（|   ;   $()  反引号）
□ input_sanitizer Token 预算拒止（8000+ tokens）
□ process_sandbox 白名单外命令拒止
□ process_sandbox 高危 flag 拒止（--eval 等）
□ fail-closed：LSG 不可用时拒绝 LLM 流量
```

---

## 11. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> LLM安全网关——3文件骨架+input_sanitizer已实现

### 11.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/llm_security/behavior_audit_logger.py` | ✅ 已实现 | |
| `src/zephyr/llm_security/input_sanitizer.py` | ✅ 已实现 | |
| `src/zephyr/llm_security/process_sandbox.py` | ✅ 已实现 | |

### 11.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/unit/test_input_sanitizer.py` | ✅ 已实现 | |
| `tests/unit/test_process_sandbox.py` | ✅ 已实现 | |
| `tests/unit/test_ai_behavior_audit_logger.py` | ✅ 已实现 | |
| `tests/unit/test_hallucination_interception.py` | ✅ 已实现 | |

### 11.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §11（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
