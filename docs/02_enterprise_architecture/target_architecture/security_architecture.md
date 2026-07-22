---
module_id: VIEW-06-SECURITY-ARCH
title: Target Architecture –Security Architecture / 目标架构：安全架�?
doc_type: architecture_view
status: Active
version: 1.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-04-24
superseded_by: null
supersedes: null
related_rationale: R38, R70, R71, R72
related_open_questions: []
related_kb:
- KBG-0018
- KBG-0020
tags:
- security-architecture
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
summary: TOGAF Security Architecture 视图（v1.0.0 完整版，�?skeleton 升格）。本视图�?D6 安全架构�?2 维审计基�?2.2/10 P0 红线）的真源文档。核心焦点：AI 安全（Prompt Injection / Agent Sandbox / LLM Security Gateway�? Secret Scanning + 分阶�?IAM。LSG 接口契约 + Windows ACL Sandbox + git-secrets 扫描为三�?experimental 落地基石�?
date: '2026-04-24'
ttl: permanent
---

# Target Architecture –Security Architecture （被恢复）
# 目标架构：安全架�?

---

## §0 Reader's Guide / 读者指�?

### 0.1 本文档是什�?

- ZephyrAlpha 2.0 安全架构�?*真源文档**（Single Source of Truth�?
- TOGAF 八视图中 D6 Security Architecture 视图�?active 版本
- 定义 **AI 编码协作场景下的安全边界**：Prompt Injection 防御、Agent Sandbox、Secret Scanning、审计日�?
- �?KBG-0018（Agent Sandbox）和 KBG-0020（LLM Security Gateway）提供架构上下文

### 0.2 本文档不�?

- �?**LLM Security Gateway 接口实现文档** –�?[`03_modules/_b_track_interfaces/llm-security-gateway-interface.md`](../../03_modules/_b_track_interfaces/llm-security-gateway-interface.md)
- �?**密钥具体轮换操作手册** –�?`docs/10_operations_and_sre/`（beta 产出�?
- �?**合规审计细则**（CSRC / MAS / SOX）–未到接入真实资金阶段，不展开
- �?**代码级安全规�?* –�?`.cursor/rules/code-conventions.mdc` �?`encoding-tool-guard.mdc`
- �?**SRE 事件响应 Runbook** –beta 启动时另行产�?
- �?**加密算法选型细节** –仅声明策略（AES-256-GCM / TLS 1.3），不铺算法原理

### 0.3 适用读�?

| 读�?| 关注章节 |
|------|---------|
| 架构�?/ 安全负责�?| §1 ~ §3, §10 |
| AI 基础设施开发�?| §4 LSG, §5 Agent Sandbox |
| 单人开发者（当前阶段）| §6 Secret Mgmt, §7 IAM experimental |
| 未来 SRE 团队 | §8 Data Protection, §9 Audit, §11 Incident Response |
| 审计 / 合规 | §3 Threat Model, §9 Audit Logging |

---

## §1 Purpose / 本视图用�?

Security Architecture 视图回答�?

1. **威胁在哪**：面�?AI 编码协作场景，主要攻击面是什么？（�? Threat Model�?
2. **怎么防御**�? 大核心服务如何协同防御？（�? LSG + §5 Sandbox�?
3. **密钥安全**：API Key / Token / 凭证如何不泄露到代码和日志？（�? Secret Mgmt�?
4. **谁能做什�?*：当前单人场景到 beta 多用户场景如何演进？（�? IAM�?
5. **数据保护**：历史行�?/ 策略代码 / 交易数据如何分级保护？（§8 Data Protection�?
6. **审计回溯**：发生事件后如何重建现场？（§9 Audit Logging�?
7. **何时升级**：Phase 边界如何触发安全能力升级？（§10 Roadmap�?

**驱动关系**：本视图受应用架构（§application_architecture.md §4A 6 大核心服务）驱动，并**反向约束**应用架构（拒绝不满足安全门禁的服务上线）�?

**基线评分**�?2 维架构审计（`dimension_audit_matrix.md`）中 D6 Security 当前得分 **2.2/10（P0 红线�?*。本文档升格（skeleton→active）是消除该红线的**前置条件**。experimental 末目标：D6 �?5.5/10�?

---

## §2 Security Domains / 安全�?

### 2.1 域划分原�?

**Security Domain** 是具有相同安全要求和信任级别的系统部分的逻辑边界。跨域必须经�?*显式授权关口**（Gateway）�?

本系统采�?**"AI 协作域突�?+ 渐进扩展"** 的域划分�?

| �?ID | 域名 | 信任级别 | 边界关口 | experimental 状�?|
|-------|------|:--------:|---------|:------------:|
| D-EXT | **外部接入�?* | 不可�?| `data/connectors/` ACL | �?已有 |
| D-AI  | **AI 协作�?* | 半可�?| **LLM Security Gateway** (§4) | 🔴 P0 待建 |
| D-AGT | **Agent 执行�?* | 半可�?| **Agent Sandbox** (§5) | 🔴 P0 待建 |
| D-INT | **内部计算�?* | 可信 | 进程边界（单人单机）| �?天然隔离 |
| D-STORE | **数据存储�?* | 可信 | 文件系统 + `.gitignore` | 🟡 部分 |
| D-SECRET | **密钥管理�?* | 最高信�?| `.env` + git-secrets + 1Password CLI | 🟡 需加固（�?）|
| D-MGMT | **管理/审计�?* | 最高信�?| SQLite WAL + Session Log | 🔴 P0 待建 |

**关键决策**：experimental 单人阶段�?*D-AI �?D-AGT 是新增的 P0 安全�?*，是传统量化系统没有的。这�?Vibe Coding 2.0 的核心安全挑战�?

### 2.2 域间信任�?

```
┌──────────────────────────────────────────────────────────────────�?
�?                   D-EXT 外部接入域（不可信）                      �?
�? Broker API �?Market Data �?LLM Provider �?Third-party packages �?
└───────────────────────────┬──────────────────────────────────────�?
                            �?ACL 隔离 + HTTPS 强制
                            �?
┌──────────────────────────────────────────────────────────────────�?
�?                   D-AI AI 协作域（半可信）                        �?
�?                                                                 �?
�? ┌──────────────────────────────────────────────────────────�?  �?
�? �?          LLM Security Gateway (LSG) –§4               �?  �?
�? �?  [ 输入分类 �?System Prompt 隔离 �?输出 Schema 校验 ]  �?  �?
�? �?  [ Pattern 巡检 ] [ fail-closed 原则 ]                 �?  �?
�? └─────────────────────┬────────────────────────────────────�?  �?
�?                       �?                                        �?
�?                       �?                                        �?
�? ┌──────────────────────────────────────────────────────────�?  �?
�? �?          D-AGT Agent 执行�?–§5                       �?  �?
�? �?  [ Windows ACL 只读挂载 ] [ 白名单命令集 ]             �?  �?
�? �?  [ 网络出口 Proxy 强制 ] [ 沙箱逃逸检�?]              �?  �?
�? └─────────────────────┬────────────────────────────────────�?  �?
└────────────────────────┼─────────────────────────────────────────�?
                         �?工具调用 / 文件写入（受 Sandbox 限制�?
                         �?
┌──────────────────────────────────────────────────────────────────�?
�?  D-INT 内部计算�?(可信)      D-STORE 数据存储�?(可信)          �?
�?  量化策略 / 因子 / 风控       历史行情 / 策略代码 / 向量记忆     �?
└──────────────────────────────────────────────────────────────────�?
                         �? 读取 API Key / Token
                         �?
┌──────────────────────────────────────────────────────────────────�?
�?  D-SECRET 密钥管理�?(最高信�? –§6                            �?
�?  .env + 1Password CLI + git-secrets + trufflehog               �?
└──────────────────────────────────────────────────────────────────�?

所有跨域调�?�?D-MGMT 管理/审计�?(SQLite WAL Session Log) –§9
```

### 2.3 零信任原则（beta 起启用）

**experimental 简�?*：D-INT / D-STORE 之间不强制边界校验（单进程、单机、单人）�?

**beta 及以�?*：接入真实券商后，必须升级为零信任：

- 每次 API 调用都带显式 scope（最小权限）
- 所有密钥都有过期时间（�?TTL�?
- 所有跨服务调用都带 `request_id` 和来源鉴�?

---

## §3 Threat Model / 威胁模型

### 3.1 STRIDE-Lite 威胁分析

针对单人 AI 协作开发场景，使用 STRIDE 精简版（Spoofing / Tampering / Repudiation / Information Disclosure / DoS / Elevation）：

| 威胁类别 | 代表威胁 | 影响�?| 严重�?| 缓解措施 | 所在域 |
|---------|---------|-------|:------:|---------|-------|
| **T1 Spoofing** | LLM Provider 中间人攻�?/ Broker 伪装响应 | D-EXT | 🔴 P0 | HTTPS + API Key Fingerprint 校验 | D-EXT |
| **T2 Tampering** | 数据源注入错误行情污染因�?| L00→L02 | 🔴 P0 | L00 ACL 质量门禁 + 数据签名验证 | D-EXT→D-INT |
| **T3 Repudiation** | AI 决策"不是我说�? / 无法追溯改动 | L08, L10 | 🟡 P1 | Session Log + Handoff Log (§9) | D-MGMT |
| **T4 Info Disclosure** | `.env` 泄漏 / API Key 误写 git | D-SECRET | 🔴 P0 | git-secrets + trufflehog + LSG Output Filter | D-SECRET |
| **T5 DoS** | LLM API 限流 / 连接池耗尽 | D-AI | 🟡 P1 | 限流 + 熔断 + 降级（规则基）| D-AI |
| **T6 Elevation** | Agent 越权写系统文�?/ 逃逸沙�?| D-AGT | 🔴 P0 | Windows ACL 只读挂载 + 白名�?| D-AGT |

### 3.2 OWASP LLM Top 10 映射�?023/2024�?

AI 协作域带�?10 �?LLM 特有威胁，本系统覆盖情况�?

| OWASP ID | 威胁 | 本系统暴露面 | experimental 防御 | 参�?|
|----------|------|-------------|-------------|------|
| LLM01 | **Prompt Injection** | Cursor / Trae 对话 + 注入外部文档 | LSG L1 输入分类�?+ L2 System Prompt 隔离 | LSG §4 |
| LLM02 | **Insecure Output Handling** | AI 输出直接写文�?| LSG L3 输出 Schema + Pydantic extra='forbid' | LSG §4 |
| LLM03 | **Training Data Poisoning** | �?不训练模型（只用推理）| N/A | –|
| LLM04 | **Model DoS** | LLM API 被重复调�?| Orchestrator 任务限�?+ 配额 | Orc §6 |
| LLM05 | **Supply Chain** | 第三�?MCP Tool 不可�?| Agent Sandbox 白名单（§5）| KBG-0018 |
| LLM06 | **Sensitive Info Disclosure** | AI 输出包含 API Key | LSG L3 输出 Secret Pattern 扫描 | LSG §4 |
| LLM07 | **Insecure Plugin Design** | MCP tools 接口越权 | LSG L4 Pattern 巡检 + Sandbox | LSG §4 |
| LLM08 | **Excessive Agency** | Agent 拥有过多权限 | 白名单命令集 + 资源配额 | KBG-0018 |
| LLM09 | **Overreliance** | AI 幻觉未检�?| Orchestrator 幻觉检�?+ Context Engine validate | Orc §5 |
| LLM10 | **Model Theft** | �?本地 BGE-M3 / Qwen2.5-3B 是开源公开模型 | N/A | –|

**关键洞察**：本系统 AI 攻击面集中在 **LLM01 / LLM02 / LLM06 / LLM08 / LLM09**�? �?P0），其他 5 条不适用�?P2 级�?

### 3.3 攻击�?–最高优先级场景（P0�?

```
攻击目标：导出生�?API Key / 资金账户凭证
�?
├── 路径 A：Prompt Injection 触发 AI 输出密钥
�?  ├── A1：恶�?Markdown 注入 Cursor 聊天
�?  �?  └── 缓解：LSG L1 classify_input() 检测注入模�?[P0]
�?  └── A2：污染向量库�?AI 读取包含密钥的上下文
�?      └── 缓解：VMS 写入�?Secret Scanner (§6.3) [P0]
�?
├── 路径 B：Agent 越权读取 .env
�?  ├── B1：AI 生成 `cat .env` 命令
�?  �?  └── 缓解：Agent Sandbox 命令白名�?[P0]
�?  └── B2：AI 通过 Python os.environ 读取
�?      └── 缓解：Sandbox 环境变量过滤（移�?SECRET_* 前缀）[P0]
�?
└── 路径 C：误提交 .env �?git
    ├── C1：开发者手动提�?
    �?  └── 缓解：git-secrets pre-commit hook [P0]
    └── C2：AI 代码生成中包含密钥常�?
        └── 缓解：LSG L3 输出 Secret Pattern + trufflehog CI [P0]
```

**防御深度**：每条路径有 **2+ 缓解�?*，任何单点失效不应导致密钥泄露（fail-closed）�?

---

## §4 LLM Security Gateway (LSG) / LLM 安全�?

### 4.1 锚点声明

**本节是架构锚�?*，实现细节见 [`03_modules/_b_track_interfaces/llm-security-gateway-interface.md`](../../03_modules/_b_track_interfaces/llm-security-gateway-interface.md)（v1.0.0�?14 行）�?

### 4.2 核心设计原则

1. **fail-closed**：任何校验器故障 �?拒绝调用（而非放行）�?*与其�?6 大核心服务的 degraded=True 降级不同**，LSG 是唯一必须 fail-closed 的服�?
2. **四层防御**：L1 输入分类 �?L2 System Prompt 隔离 �?L3 输出 Schema �?L4 Pattern 巡检
3. **Pydantic v2 + `extra='forbid'`**：所有输入输出都有严�?Schema，未知字段一律拒�?
4. **零信�?LLM 响应**：即便是本地 Qwen2.5-3B 的输出也必须�?L3/L4 校验
5. **审计完整�?*：每次调用生�?`request_id` + `input_hash` + `output_hash` 写入 Session Log

### 4.3 安全编排�?

```
Cursor / Trae / Claude Desktop
         �? MCP 协议调用
         �?
┌────────────────────────────────────�?
�?  LSG L1  Input Classifier        │◀─── 阻止 Prompt Injection（OWASP LLM01�?
�?  [ Pattern + 启发�?+ 正则 ]     �?
└───────────┬────────────────────────�?
            �?
┌────────────────────────────────────�?
�?  LSG L2  System Prompt Isolator   │◀─── 防止用户指令提升权限
�?  [ 双层 Prompt + 分隔�?]        �?
└───────────┬────────────────────────�?
            �?
         LLM Call
            �?
            �?
┌────────────────────────────────────�?
�?  LSG L3  Output Validator         │◀─── Schema + Secret Scan（OWASP LLM02/06�?
�?  [ Pydantic + Regex 敏感词扫�?]  �?
└───────────┬────────────────────────�?
            �?
┌────────────────────────────────────�?
�?  LSG L4  Pattern Auditor          │◀─── 累积异常模式检�?
�?  [ 滑动窗口 + EMA 异常�?]        �?
└───────────┬────────────────────────�?
            �?
    Agent Orchestrator / Context Engine 消费
```

### 4.4 误报与性能预算（硬约束�?

| 指标 | experimental SLO | beta 目标 | 当前基线 |
|------|:----------:|:------------:|:--------:|
| 误拦率（合法请求被拒）| < 2% | < 0.5% | 未测 |
| 漏拦率（攻击被放行）| < 5% | < 1% | 未测 |
| LSG 延迟 P99 | < 200ms | < 100ms | 未测 |
| fail-closed 触发�?| < 0.1%/�?| < 0.01%/�?| 未测 |

**红队评估**：experimental 末必须跑一次红队评估（模拟 OWASP LLM01/02/06/08/09 攻击），记录漏拦率。阈�?> 5% 触发 **TECH-16 升级**（见 `technology_landscape.yaml upgrade_watchboard`）�?

---

## §5 Agent Sandbox / Agent 执行沙箱

### 5.1 锚点声明

**本节是架构锚�?*，实现细节见 [`03_modules/_b_track_interfaces/agent-orchestrator-interface.md §7 Sandbox`](../../03_modules/_b_track_interfaces/agent-orchestrator-interface.md)，技术选型�?KBG-0018�?

### 5.2 experimental 实现：Windows ACL + 只读挂载

选型理由�?

- **零外部依�?*：不需�?Docker Desktop，单人机器直接可�?
- **可观�?*：Windows Security Event Log 原生记录违规访问
- **可升�?*：beta 可切�?Docker Desktop（同一接口，TECH-12 watchboard�?

**沙箱规则**�?

| 资源类别 | 权限 | 实现 |
|---------|:----:|------|
| `src/` | RO | ACL + FileSystemWatcher |
| `docs/` | RO | ACL |
| `.runtime/sandbox-work/` | RW | Agent 唯一写入�?|
| 其他路径（`.env` / `~/` / `C:\Windows`）| 拒绝 | ACL DENY ACE |
| 网络出口 | �?LLM Provider 白名�?| Windows Firewall Rule |
| 系统命令 | 白名单（`python`, `git status`, `mkdocs build`, ...）| Orc 命令解析�?|
| 环境变量 | 过滤 `SECRET_*` / `API_KEY_*` | Orc 进程派生时移�?|

### 5.3 逃逸检�?

**P0 检测项**�?

1. Agent 尝试访问白名单外路径 �?立即 kill + 记录 Session Log
2. Agent 尝试执行白名单外命令 �?拒绝 + 触发 FLE 异常事件
3. Agent 进程内存 / CPU 超配额（默认 2GB / 2 cores）→ 强制回收

**已知局�?*：Windows ACL 不如 Linux namespace 隔离严格，beta 接入真实资金�?*必须**升级�?Docker 沙箱�?

---

## §6 Secret Management / 密钥管理

### 6.1 当前资产清单

| 密钥类型 | 来源 | 存储位置 | 轮换频率 | experimental 保护 |
|---------|------|---------|:--------:|-------------|
| LLM API Key（Anthropic/OpenAI/DeepSeek 等）| 官网 | `.env` | 90 �?| .gitignore + git-secrets |
| Broker API Key（未来）| 券商 | `.env`（experimental 不用）| N/A | –|
| Feishu Bot Token | 飞书 | `.env` | 180 �?| .gitignore |
| 1Password Service Account Token | 1Password | OS Keychain | 1 �?| 不落文件 |

### 6.2 三道防线（fail-closed�?

```
Dev-Time                     Commit-Time                  Runtime
─────────                    ───────────                  ────────
L1: .env + .gitignore   �?  L2: git-secrets    �?       L3: LSG Output Scanner
    开发时本地保存            pre-commit hook              AI 输出过滤
    [ 基础约束 ]              [ 阻止提交 ]                  [ �?AI 生成密钥 ]

                                      �?
                                      �?
                              L2-CI: trufflehog           L3-Audit: Secret
                              Scan on PR                   Leak Weekly Scan
                              [ 追赶漏网 ]                 [ 历史库扫�?]
```

**fail-closed 语义**：任何一道防线检测到潜在泄露 �?阻塞下游流程（commit rejected / CI failed / AI response dropped），**不允�?记录下来但继�?**�?

### 6.3 具体实施

**L1（已有）**�?

- `.env` 在根目录 `.gitignore`�? 行规则）
- `docs/.env.example` 提供占位模板
- `.cursor/rules/encoding-tool-guard.mdc` 禁止 agent �?`.env` 文件

**L2（P0 待建�?*�?

- `scripts/hooks/git-secrets-setup.sh`（experimental 新增�?
- 规则模式：`AKIA[0-9A-Z]{16}` / `sk-ant-*` / `sk-proj-*` / 自定�?`ZEPHYR_SECRET_*`
- CI �?`trufflehog` 扫描 git 全历�?

**L3（已�?�?LSG 接口�?*�?

- LSG Output Validator 内置 25+ 正则（LLM API Key / JWT / Private Key 等）
- 触发立即返回 `degraded=True` + 拒绝输出 + FLE 上报 anomaly

**L3-Audit（experimental 每周�?*�?

- `scripts/governance/scan_secret_leak.py` –全库扫描 + 对比历史快照
- Finding �?`docs/_working/audit/findings/secret-leak-*.md`

### 6.4 beta 升级触发

接入真实资金前必须：

- 迁移�?**1Password CLI** �?**HashiCorp Vault**�?env 仅作开发便利，生产禁用�?
- 所有密�?**�?TTL**�?4h�? 自动轮换
- 访问日志�?D-MGMT 审计�?

---

## §7 IAM –Identity & Access Management / 身份与访问控�?

### 7.1 experimental 简化模型（单人�?

**现状**：单人开发，单机运行�?*无多用户 IAM 需�?*�?

**最小约�?*�?

- 操作系统用户：Windows 本机用户一�?
- 本地服务（Ollama / ChromaDB）：仅绑�?`127.0.0.1`，拒绝外�?
- API Key 即身份：所有外部调用的授权来源

### 7.2 AI Agent 身份模型（experimental P0�?

虽然无多�?IAM，但 **AI Agent 必须有独立身�?*�?

| Agent | 身份 | 权限�?| 实现 |
|-------|------|-------|------|
| Cursor Agent | `agent:cursor` | Sandbox RW + LSG 配额 A | Orc 签发 Session Token |
| Trae Agent | `agent:trae` | Sandbox RW + LSG 配额 B | Orc 签发 Session Token |
| Human Owner | `human:owner` | 全权（绕�?Sandbox）| �?Token，文件系统直接操�?|

**关键约束**：AI Agent 的每次调用都�?`agent_id`，Session Log �?agent_id 分流，便于事后追溯（"这次污染是哪�?Agent 造成�?）�?

### 7.3 beta+ 多用户演�?

接入第二个用户时�?

- 启用 **RBAC**（Role-Based Access Control�?
- 角色草案：Owner / Researcher / Auditor / Viewer
- 身份源：本地 LDAP �?OIDC（视部署模式�?
- 本视图届时发�?**v2.0.0 重大修订**

---

## §8 Data Protection / 数据保护

### 8.1 数据分级（experimental 基线�?

| 级别 | 数据类型 | 加密策略 |
|------|---------|---------|
| **L4 最高敏�?* | API Key / 交易凭证 / 账户数据 | 传输 TLS 1.3；静�?OS Keychain 或加密卷 |
| **L3 高敏�?* | 策略代码 / 参数 / 持仓 | 传输 HTTPS；静�?OS 权限 + .gitignore |
| **L2 中敏�?* | 历史行情 / 因子�?| 传输 HTTPS；静�?文件系统权限 |
| **L1 低敏�?* | 公开文档 / KB 决策记录 / README | 无加密要�?|

### 8.2 experimental 关键约束

- **所有外�?API 调用强制 HTTPS/TLS 1.3**；证书校验不得禁�?
- **静止数据不入 git**：`.runtime/`、`*.db`、`*.parquet`、`*.env` 均在 `.gitignore`
- **PII 豁免**：当前系统无用户 PII；未来接�?KYC 数据时触�?beta 升级

### 8.3 数据保留与销�?

| 数据 | 保留�?| 销毁策�?|
|------|:------:|---------|
| Session Log | 180 �?| 90 天后归档 .gz�?80 天后删除 |
| 向量库（VMS）| 永久 | 手动 TTL（个人系统无合规销毁要求）|
| Broker 交易日志（未来）| 7 �?| 合规要求（beta 定）|
| Audit Finding | 2 �?| 压缩归档 |

---

## §9 Audit Logging / 审计日志

### 9.1 审计数据架构

审计日志�?**D-MGMT �?* 的核心。采�?**SQLite WAL 模式 + Session Log JSON Lines** 双轨存储�?

```
.runtime/sqlite/audit.db (WAL)         .runtime/logs/session/
├── table: security_events             ├── YYYY-MM-DD/
├── table: llm_calls                   �?  ├── session-<uuid>.jsonl
├── table: agent_actions               �?  └── ...
├── table: secret_scan_findings        └── carryover-<uuid>.json
└── table: sandbox_violations              （见 session_carryover_schema.md�?
```

### 9.2 关键字段（experimental 必采�?

每条审计记录 **至少包含**�?

- `event_id`（UUID v4�?
- `timestamp`（UTC RFC3339 纳秒�?
- `event_type`（枚举：`llm_call` / `agent_action` / `secret_alert` / `sandbox_violation` / `auth_event`�?
- `actor`（`human:owner` / `agent:cursor` / ...�?
- `resource`（受影响资源路径 / service ID�?
- `result`（`allow` / `deny` / `degraded`�?
- `reason`（策略命�?ID / 异常原因�?
- `input_hash` + `output_hash`（SHA-256，防篡改�?
- `request_id`（跨服务链路追踪�?

### 9.3 防篡改机制（experimental 轻量 �?beta 加强�?

- SQLite WAL + 周期全库哈希（每�?00:00 UTC 写入 `audit.db.sha256`�?
- 哈希文件 git commit（形成外部锚点）

**beta（接入真实资金）**�?

- 哈希链（每条事件 include 前一条事件哈希）
- 异地只读副本（beta upgrade_watchboard 触发�?

### 9.4 日志消费�?

| 消费�?| 用�?| 访问模式 |
|--------|------|---------|
| Feedback Loop Engine | 异常检�?+ 自调�?| 流式�?|
| Session Carryover | 下次 IDE 会话恢复上下�?| 批读 |
| 人工审计 / 合规 | 事件回溯 | SQL 查询 |
| ML 模型训练（beta+）| 异常模式学习 | 历史回放 |

---

## §10 Phase Roadmap / 分阶段路�?

### 10.1 Phase 对齐表（配合 phase-transition-protocol.md�?

| Phase | 阶段�?| D6 目标�?| 本视图必交付 |
|:-----:|-------|:--------:|-------------|
| scaffold | 基础奠基 | 2.2 �?3.5 | §6 L1+L2�?env + git-secrets�? §9 SQLite audit schema |
| experimental | 核心服务上线 | 3.5 �?5.5 | §4 LSG + §5 Agent Sandbox + §6 L3 + §9 Session Log |
| beta | 接入真实券商 | 5.5 �?7.0 | §7 RBAC 启用 + §6 1Password 迁移 + §8 数据分级落地 + 合规审计 |
| beta | 多用�?部分自动�?| 7.0 �?8.0 | 零信�?+ OIDC + WAF + 多区审计 |
| stable | 机构�?全自�?| 8.0 �?9.0+ | SOC2/ISO27001 合规 + 专职安全团队 |

### 10.2 Phase 门禁（不可越级）

**scaffold �?experimental 出口门禁**（必�?ALL PASS）：

- [ ] `scripts/hooks/git-secrets-setup.sh` 已部署，所�?commit 必须过检
- [ ] 历史 git 全库 trufflehog 扫描 0 finding
- [ ] SQLite audit.db schema 定稿 + 写入一条测试事�?
- [ ] 本视�?`status: active` + �?`overview.md §5` 引用

**experimental �?beta 出口门禁**�?

- [ ] LSG 部署 + 红队评估漏拦�?< 5%
- [ ] Agent Sandbox 部署 + 30 �?0 逃逸事�?
- [ ] D6 审计 �?5.5/10
- [ ] Secret Leak Weekly Scan 连续 4 �?0 finding

---

## §11 Incident Response / 事件响应（experimental 启动�?

### 11.1 experimental 最小响应流�?

�?D6 任一 P0 事件发生（`secret_alert` / `sandbox_violation` / `llm_injection_detected`）：

1. **自动**：LSG/Sandbox/Scanner 立即拦截 + �?audit 事件 + FLE 异常上报
2. **10 分钟�?*：飞�?Bot 推送告警（优先�?P0 / P1�?
3. **1 小时�?*：人工确�?+ 决定是否启动手动响应
4. **24 小时�?*：写 `docs/_working/audit/findings/incident-YYYYMMDD-<id>.md`（时间线 + 根因 + 缓解�?
5. **7 天内**：复�?+ 产出 KB 决策记录（如需要架构修改）

### 11.2 Runbook 清单（experimental P0�?

| Runbook ID | 触发事件 | 所�?|
|-----------|---------|------|
| IR-SEC-001 | 密钥疑似泄漏（git-secrets / trufflehog 触发）| P0 |
| IR-SEC-002 | Agent 沙箱逃逸尝�?| P0 |
| IR-SEC-003 | LSG fail-closed 频繁触发�? 10 �?天）| P1 |
| IR-SEC-004 | Secret Leak Weekly Scan �?Finding | P0 |

**Runbook 正文**：experimental �?`docs/10_operations_and_sre/runbooks/` 产出（不在本视图中展开）�?

---

## §12 Revision history / 修订记录

| Date / 日期 | Description / 说明 |
|------------|-------------------|
| 2026-04-19 | v0.1.0：初版骨架建立�? 节安全域占位（�?-§7�? §8 Activation Triggers 8 条�?|
| 2026-04-24 | **v1.0.0**：B-d-4 完整重写。从 skeleton 升格�?active。新�?§0 读者指南、�? 安全�?7 域模型（�?D-AI/D-AGT AI 特有域）、�? STRIDE-Lite + OWASP LLM Top 10 威胁映射 + P0 攻击树、�? LSG 架构锚点、�? Agent Sandbox 锚点、�? Secret 三道防线 fail-closed、�? Phase-based IAM、�? 数据分级与保护、�? 审计日志 SQLite WAL + Session Log 双轨、�?0 Phase 路线（D6 目标�?2.2�?.0）、�?1 事件响应 experimental 启动。消�?12 维审�?D6 P0 红线。依�?KBG-0018（Sandbox�? KBG-0020（LSG）�?|

---

## §13 Open Questions / 待决问题

| ID | 问题 | 决定期限 |
|----|------|---------|
| SEC-OQ-01 | LSG 的红队评估工具选型（内部脚�?vs 外部工具 garak / promptbench）| experimental �?|
| SEC-OQ-02 | Session Log 归档加密选型（AES-256-GCM vs age）| experimental �?|
| SEC-OQ-03 | beta Sandbox 升级路径：Docker Desktop vs WSL2 vs Firejail（WSL 下）| experimental �?|
| SEC-OQ-04 | beta IAM 身份提供者：本地 LDAP vs OIDC vs Authentik | beta �?|
| SEC-OQ-05 | 合规审计冻结期限�? 年？合规机构决定）| beta �?|
