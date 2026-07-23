---
module_id: VIEW-04PRINC-SECURITY
title: Architecture Principles — Security / 架构原则：安全
doc_type: architecture_view
status: Active
version: 1.0.1
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-07-19
superseded_by: null
supersedes: VIEW-06-SECURITY-ARCH
related_rationale: []
related_open_questions: []
tags:
- security-principles
- togaf
- iam
- secret-management
- data-protection
- audit-log
- threat-model
- owasp-llm-top10
- prompt-injection
- agent-sandbox
- fail-closed
- llm-security-gateway
summary: 安全架构永恒原则文档。timeless 方法论——安全域划分、STRIDE-Lite 威胁模型、OWASP LLM Top 10 映射、LSG fail-closed 四层防御、Agent Sandbox 沙箱规则、Secret Management 三道防线、IAM AI Agent 身份模型、Data Protection 数据分级、Audit Logging 防篡改、Incident Response 响应流程。派生数据（密钥资产清单、Phase 进度、Open Questions）不在本文档，由各自自动化系统维护。
date: '2026-07-19'
ttl: permanent
---

# Architecture Principles — Security
# 架构原则：安全（Security Principles）

---

## §1 定位 / Position

本文档是**安全架构的永恒指导原则**。

**保留内容**：方法论、设计原则、不变约束——这些不随 Phase 演进或资产清单变化而改变。

**不保留内容**（派生/动态数据，由各自自动化系统维护）：
- 密钥资产清单 → 由 `scripts/governance/scan_secret_leak.py` 自动扫描生成
- Phase Roadmap 进度 → 由 `phase-transition-protocol.md`（待创建）+ 自动化 phase gate 维护
- Open Questions → 由决策注册表（`docs/02_enterprise_architecture/04_architecture_principles_decisions/`）维护
- LSG 接口实现细节 → `../../03_modules/_cross_layer/_b_track_interfaces/llm_security_gateway_interface.md`
- Agent Sandbox 技术选型 → KBG-0018
- STRIDE/OWASP 详细威胁映射（含 severity/domain/exposure/reference 列）+ 数据保留表 + 日志消费者表 → `architecture_model/security/threat_model.yaml`

**与其他原则文档关系**：
- [capability_maturity_principles.md](capability_maturity_principles.md)：能力成熟度方法论（跨域）
- [data_principles.md](data_principles.md)：数据架构原则（PIT/血缘/MDM/质量门禁）
- 本文：安全架构原则（威胁模型/LSG/Sandbox/密钥/IAM/审计）

---

## §2 Security Domains / 安全域划分原则

### 2.1 域划分原则

**Security Domain** 是具有相同安全要求和信任级别的系统部分的逻辑边界。跨域必须经过**显式授权关口**（Gateway）。

本系统采用 **"AI 协作域突围 + 渐进扩展"** 的域划分策略。

**永恒约束**：
- 跨域调用必须经过显式 Gateway（ACL / LSG / Sandbox）
- 信任级别从低到高：不可信（D-EXT）→ 半可信（D-AI/D-AGT）→ 可信（D-INT/D-STORE）→ 最高信任（D-SECRET/D-MGMT）
- **D-AI 与 D-AGT 是 AI 编码协作场景特有的 P0 安全域**——传统量化系统没有，这是 Vibe Coding 2.0 的核心安全挑战

### 2.2 域间信任流（永恒约束）

```
D-EXT 外部接入域（不可信）
  │ ACL 隔离 + HTTPS 强制
  ▼
D-AI AI 协作域（半可信）── LLM Security Gateway (LSG)
  │
  ▼
D-AGT Agent 执行域（半可信）── Agent Sandbox
  │ 工具调用 / 文件写入（受 Sandbox 限制）
  ▼
D-INT 内部计算域（可信）+ D-STORE 数据存储域（可信）
  │ 读取 API Key / Token
  ▼
D-SECRET 密钥管理域（最高信任）

所有跨域调用 → D-MGMT 管理/审计域（审计日志）
```

### 2.3 零信任原则（beta 起启用）

**experimental 简化**：D-INT / D-STORE 之间不强制边界校验（单进程、单机、单人）。

**beta 及以后**：接入真实券商后，必须升级为零信任：

- 每次 API 调用都带显式 scope（最小权限）
- 所有密钥都有过期时间（带 TTL）
- 所有跨服务调用都带 `request_id` 和来源鉴权

---

## §3 Threat Model / 威胁模型

### 3.1 STRIDE-Lite 威胁分析（永恒框架）

针对 AI 编码协作场景，使用 STRIDE 精简版：

| 威胁类别 | 代表威胁 | 影响域 | 缓解措施 |
|---------|---------|-------|---------|
| **Spoofing** | LLM Provider 中间人攻击 / Broker 伪装响应 | D-EXT | HTTPS + API Key Fingerprint 校验 |
| **Tampering** | 数据源注入错误行情污染因子 | D_MKT_DATA → D_DATA_ENG | D_DATA ACL 质量门禁 + 数据签名验证 |
| **Repudiation** | AI 决策"不是我说的" / 无法追溯改动 | D_GOVERNANCE | Session Log + Handoff Log |
| **Info Disclosure** | `.env` 泄漏 / API Key 误写 git | D-SECRET | git-secrets + trufflehog + LSG Output Filter |
| **DoS** | LLM API 限流 / 连接池耗尽 | D-AI | 限流 + 熔断 + 降级（规则基）|
| **Elevation** | Agent 越权写系统文件 / 逃逸沙箱 | D-AGT | Windows ACL 只读挂载 + 白名单 |

### 3.2 OWASP LLM Top 10 映射（永恒覆盖矩阵）

AI 协作域带着 10 条 LLM 特有威胁，本系统覆盖原则：

| OWASP ID | 威胁 | 防御原则 |
|----------|------|---------|
| LLM01 | **Prompt Injection** | LSG L1 输入分类器 + L2 System Prompt 隔离 |
| LLM02 | **Insecure Output Handling** | LSG L3 输出 Schema + Pydantic extra='forbid' |
| LLM03 | Training Data Poisoning | 不训练模型（只用推理）→ N/A |
| LLM04 | Model DoS | Orchestrator 任务限流 + 配额 |
| LLM05 | Supply Chain | Agent Sandbox 白名单 |
| LLM06 | Sensitive Info Disclosure | LSG L3 输出 Secret Pattern 扫描 |
| LLM07 | Insecure Plugin Design | LSG L4 Pattern 巡检 + Sandbox |
| LLM08 | Excessive Agency | 白名单命令集 + 资源配额 |
| LLM09 | Overreliance | Orchestrator 幻觉检测 + Context Engine validate |
| LLM10 | Model Theft | 本地模型是开源公开 → N/A |

**关键洞察**：本系统 AI 攻击面集中在 **LLM01 / LLM02 / LLM06 / LLM08 / LLM09**（P0），其他 5 条不适用。

> **注**：STRIDE 各威胁的 severity（P0/P1）+ 所在域、OWASP 各条的本系统暴露面 + 参考链接见 `architecture_model/security/threat_model.yaml`（从 security_architecture.md §3.1/§3.2 迁移）。本文 §3.1/§3.2 为永恒框架版。

### 3.3 防御深度原则（永恒）

每条攻击路径必须有 **2+ 缓解**，任何单点失效不应导致密钥泄露（fail-closed）。

攻击树示例（密钥泄露场景）：

```
攻击目标：导出 API Key / 资金账户凭证
│
├── 路径 A：Prompt Injection 触发 AI 输出密钥
│   ├── A1：恶意 Markdown 注入 IDE 聊天 → LSG L1 classify_input() 检测
│   └── A2：污染向量库，AI 读取包含密钥的上下文 → VMS 写入前 Secret Scanner
│
├── 路径 B：Agent 越权读取 .env
│   ├── B1：AI 生成 `cat .env` 命令 → Agent Sandbox 命令白名单
│   └── B2：AI 通过 os.environ 读取 → Sandbox 环境变量过滤（移除 SECRET_* 前缀）
│
└── 路径 C：误提交 .env 到 git
    ├── C1：开发者手动提交 → git-secrets pre-commit hook
    └── C2：AI 代码生成中包含密钥常量 → LSG L3 输出 Secret Pattern + trufflehog CI
```

---

## §4 LLM Security Gateway (LSG) 核心设计原则

### 4.1 五大永恒原则

1. **fail-closed**：任何校验器故障 → 拒绝调用（而非放行）。**与其余 5 大核心服务的 degraded=True 降级不同**，LSG 是唯一必须 fail-closed 的服务
2. **四层防御**：L1 输入分类 → L2 System Prompt 隔离 → L3 输出 Schema → L4 Pattern 巡检
3. **Pydantic v2 + `extra='forbid'`**：所有输入输出都有严格 Schema，未知字段一律拒绝
4. **零信任 LLM 响应**：即便是本地 Qwen2.5-3B 的输出也必须过 L3/L4 校验
5. **审计完整性**：每次调用生成 `request_id` + `input_hash` + `output_hash` 写入 Session Log

### 4.2 四层防御流（永恒编排）

```
IDE / AI Client
     │ MCP 协议调用
     ▼
LSG L1  Input Classifier       ← 阻止 Prompt Injection（OWASP LLM01）
  [ Pattern + 启发式 + 正则 ]
     ▼
LSG L2  System Prompt Isolator ← 防止用户指令提升权限
  [ 双层 Prompt + 分隔符 ]
     ▼
   LLM Call
     ▼
LSG L3  Output Validator       ← Schema + Secret Scan（OWASP LLM02/06）
  [ Pydantic + Regex 敏感词扫描 ]
     ▼
LSG L4  Pattern Auditor        ← 累积异常模式检测
  [ 滑动窗口 + EMA 异常分 ]
     ▼
Agent Orchestrator / Context Engine 消费
```

### 4.3 性能预算（永恒 SLO 约束）

| 指标 | experimental SLO | beta 目标 |
|------|:----------:|:------------:|
| 误拦率（合法请求被拒）| < 2% | < 0.5% |
| 漏拦率（攻击被放行）| < 5% | < 1% |
| LSG 延迟 P99 | < 200ms | < 100ms |
| fail-closed 触发率 | < 0.1%/天 | < 0.01%/天 |

**红队评估原则**：experimental 末必须跑一次红队评估（模拟 OWASP LLM01/02/06/08/09 攻击），记录漏拦率。阈值 > 5% 触发升级。

---

## §5 Agent Sandbox 沙箱规则（永恒约束）

### 5.1 沙箱资源权限矩阵

| 资源类别 | 权限 | 原则 |
|---------|:----:|------|
| `src/` | RO | 代码只读，Agent 不可修改源码 |
| `docs/` | RO | 文档只读 |
| `.runtime/sandbox-work/` | RW | Agent 唯一写入区 |
| 其他路径（`.env` / `~/` / `C:\Windows`）| 拒绝 | ACL DENY ACE |
| 网络出口 | 仅 LLM Provider 白名单 | Windows Firewall Rule |
| 系统命令 | 白名单 | Orc 命令解析器 |
| 环境变量 | 过滤 `SECRET_*` / `API_KEY_*` | Orc 进程派生时移除 |

### 5.2 逃逸检测（永恒 P0 检测项）

1. Agent 尝试访问白名单外路径 → 立即 kill + 记录 Session Log
2. Agent 尝试执行白名单外命令 → 拒绝 + 触发 FLE 异常事件
3. Agent 进程内存 / CPU 超配额（默认 2GB / 2 cores）→ 强制回收

**永恒约束**：beta 接入真实资金后**必须**升级到 Docker 沙箱（Windows ACL 不如 Linux namespace 隔离严格）。

---

## §6 Secret Management 三道防线（fail-closed）

### 6.1 三道防线架构（永恒）

```
Dev-Time                     Commit-Time                  Runtime
─────────                    ───────────                  ────────
L1: .env + .gitignore   →   L2: git-secrets    →         L3: LSG Output Scanner
    开发时本地保存            pre-commit hook              AI 输出过滤
    [ 基础约束 ]              [ 阻止提交 ]                  [ 拦截 AI 生成密钥 ]

                                      │
                                      ▼
                              L2-CI: trufflehog           L3-Audit: Secret
                              Scan on PR                   Leak Weekly Scan
                              [ 追赶漏网 ]                 [ 历史库扫描 ]
```

### 6.2 fail-closed 语义（永恒铁律）

任何一道防线检测到潜在泄露 → 阻塞下游流程（commit rejected / CI failed / AI response dropped），**不允许"记录下来但继续"**。

### 6.3 L2 规则模式（永恒正则集）

- `AKIA[0-9A-Z]{16}`（AWS）
- `sk-ant-*`（Anthropic）
- `sk-proj-*`（OpenAI）
- 自定义 `ZEPHYR_SECRET_*`

### 6.4 beta 升级触发（永恒门禁）

接入真实资金前必须：
- 迁移到 **1Password CLI** 或 **HashiCorp Vault**（.env 仅作开发便利，生产禁用）
- 所有密钥**带 TTL**（24h）自动轮换
- 访问日志入 D-MGMT 审计域

---

## §7 IAM – AI Agent 身份模型（永恒约束）

### 7.1 AI Agent 必须有独立身份

即使单人开发无多用户 IAM，**AI Agent 必须有独立身份**：

| Agent | 身份 | 权限组 |
|-------|------|-------|
| Cursor Agent | `agent:cursor` | Sandbox RW + LSG 配额 A |
| Trae Agent | `agent:trae` | Sandbox RW + LSG 配额 B |
| Human Owner | `human:owner` | 全权（绕过 Sandbox）|

### 7.2 审计分流原则（永恒）

AI Agent 的每次调用都带 `agent_id`，Session Log 按 agent_id 分流，便于事后追溯（"这次污染是哪个 Agent 造成"）。

### 7.3 beta+ 多用户演进

接入第二个用户时：
- 启用 **RBAC**（Role-Based Access Control）
- 角色草案：Owner / Researcher / Auditor / Viewer
- 身份源：本地 LDAP 或 OIDC
- 届时发布重大修订

---

## §8 Data Protection 数据保护原则

### 8.1 数据分级（永恒基线）

| 级别 | 数据类型 | 加密策略 |
|------|---------|---------|
| **L4 最高敏感** | API Key / 交易凭证 / 账户数据 | 传输 TLS 1.3；静态 OS Keychain 或加密卷 |
| **L3 高敏感** | 策略代码 / 参数 / 持仓 | 传输 HTTPS；静态 OS 权限 + .gitignore |
| **L2 中敏感** | 历史行情 / 因子值 | 传输 HTTPS；静态文件系统权限 |
| **L1 低敏感** | 公开文档 / KB 决策记录 / README | 无加密要求 |

### 8.2 永恒关键约束

- **所有外部 API 调用强制 HTTPS/TLS 1.3**；证书校验不得禁用
- **静止数据不入 git**：`.runtime/`、`*.db`、`*.parquet`、`*.env` 均在 `.gitignore`
- **PII 豁免**：当前系统无用户 PII；未来接入 KYC 数据时触发 beta 升级

---

## §9 Audit Logging 审计日志原则

### 9.1 双轨存储架构（永恒）

```
.runtime/sqlite/audit.db (WAL)         .runtime/logs/session/
├── table: security_events             ├── YYYY-MM-DD/
├── table: llm_calls                   │  ├── session-<uuid>.jsonl
├── table: agent_actions               │  └── ...
├── table: secret_scan_findings        └── carryover-<uuid>.json
└── table: sandbox_violations
```

### 9.2 关键字段（永恒必采集）

每条审计记录 **至少包含**：

- `event_id`（UUID v4）
- `timestamp`（UTC RFC3339 纳秒）
- `event_type`（枚举：`llm_call` / `agent_action` / `secret_alert` / `sandbox_violation` / `auth_event`）
- `actor`（`human:owner` / `agent:cursor` / ...）
- `resource`（受影响资源路径 / service ID）
- `result`（`allow` / `deny` / `degraded`）
- `reason`（策略命中 ID / 异常原因）
- `input_hash` + `output_hash`（SHA-256，防篡改）
- `request_id`（跨服务链路追踪）

### 9.3 防篡改机制（永恒原则）

- SQLite WAL + 周期全库哈希（每日 00:00 UTC 写入 `audit.db.sha256`）
- 哈希文件 git commit（形成外部锚点）

**beta（接入真实资金）**：
- 哈希链（每条事件 include 前一条事件哈希）
- 异地只读副本

---

## §10 Incident Response 事件响应原则

### 10.1 永恒最小响应流程

若任一 P0 事件发生（`secret_alert` / `sandbox_violation` / `llm_injection_detected`）：

1. **自动**：LSG/Sandbox/Scanner 立即拦截 + 写 audit 事件 + FLE 异常上报
2. **10 分钟内**：飞书 Bot 推送告警（优先级 P0 / P1）
3. **1 小时内**：人工确认 + 决定是否启动手动响应
4. **24 小时内**：写 incident 报告（时间线 + 根因 + 缓解）
5. **7 天内**：复盘 + 产出 KB 决策记录（如需要架构修改）

### 10.2 Runbook 清单（永恒 P0）

| Runbook ID | 触发事件 | 优先级 |
|-----------|---------|------|
| IR-SEC-001 | 密钥疑似泄漏（git-secrets / trufflehog 触发）| P0 |
| IR-SEC-002 | Agent 沙箱逃逸尝试 | P0 |
| IR-SEC-003 | LSG fail-closed 频繁触发（> 10 次/天）| P1 |
| IR-SEC-004 | Secret Leak Weekly Scan 有 Finding | P0 |

---

## §11 视图边界 / Boundaries

### 11.1 本文档覆盖

- 安全域划分原则（§2）
- 威胁模型方法论（§3）
- LSG/Sandbox/Secret/IAM/Data Protection/Audit/Incident 的永恒设计原则（§4-§10）

### 11.2 本文档不覆盖（由其他系统维护）

| 内容 | 真源 |
|------|------|
| LSG 接口实现 | `../../03_modules/_cross_layer/_b_track_interfaces/llm_security_gateway_interface.md` |
| Agent Sandbox 技术选型 | KBG-0018 |
| 威胁映射详细表（STRIDE severity/domain + OWASP exposure/reference）+ 数据保留 + 日志消费者 | `architecture_model/security/threat_model.yaml` |
| 密钥资产清单（动态） | `scripts/governance/scan_secret_leak.py` 自动扫描 |
| Phase Roadmap 进度 | `phase-transition-protocol.md`（待创建）+ 自动化 phase gate |
| Open Questions | 决策注册表（`04_architecture_principles_decisions/`）|
| 代码级安全规范 | `.cursor/rules/code-conventions.mdc` 与 `encoding-tool-guard.mdc` |
| SRE Runbook 正文 | D_OPS 域产出 |
| 加密算法选型细节 | 仅声明策略（AES-256-GCM / TLS 1.3），不铺算法原理 |

### 11.3 与其他原则文档关系

- [capability_maturity_principles.md](capability_maturity_principles.md)：能力成熟度方法论
- [data_principles.md](data_principles.md)：数据架构原则（PIT/血缘/MDM/质量门禁）
- 本文：安全架构原则（威胁模型/LSG/Sandbox/密钥/IAM/审计）

---

> **文档维护原则**：本文档只包含永恒指导原则。任何随 Phase 演进、资产变化、技术选型更新的内容，均不应