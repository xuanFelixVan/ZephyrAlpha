---
module_id: ADR-0020
doc_type: adr
title: LLM Security Gateway — 四层防御 + fail-closed + OWASP LLM Top 10
version: 1.0.0
status: active
date: '2026-04-24'
owner: ZephyrAlpha-Owner
ttl: permanent
related_adrs:
- ADR-0017
- ADR-0018
- ADR-0019
- ADR-0021
priority: P0
phase: Phase-1
tech_refs:
- TECH-15
- TECH-16
- TECH-17
supersedes_doc: archive/reorg-2026-04-24/08_ai_engineering/tool-interface-contract.md
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
summary: "**Vibe Coding 2.0 安全基石** LLM Security Gateway（四层防御 + fail-closed + OWASP LLM Top 10 映射，D6 红线 2.2→5.5）| accepted"
---

# ADR-0020: LLM Security Gateway — 四层防御 + fail-closed + OWASP LLM Top 10

**状态**：Accepted
**日期**：2026-04-24
**决策者**：ZephyrAlpha-Owner
**优先级**：P0（最高，D6 红线修复）
**阶段**：Phase 1 首批上线

---

## 1. 状态（Status）

- **当前状态**：`accepted`
- **提议日期**：2026-04-24
- **拍板日期**：2026-04-24

## 2. 背景与问题（Context）

### 2.1 问题陈述

`vibe-coding-audit-merged.md §GLM D11 2.2/10` 判定 **D6 Security Architecture 为 12 维审计最薄弱项（P0 红线）**。核心暴露面：

- **SEC-01 Prompt Injection**：AI IDE 对话 + 注入恶意 Markdown 未经任何防护
- **SEC-03 Insecure Output**：AI 输出可能含 API Key / 越权命令 / 幻觉代码
- **SEC-04 Sensitive Info Disclosure**：LLM 响应可能泄密（API Key / 策略参数）
- **SEC-05 Excessive Agency**：Agent 调用外部工具无白名单

OWASP LLM Applications Top 10 (2023/2024) 中 **LLM01 / LLM02 / LLM06 / LLM08 / LLM09** 5 条 P0 级威胁当前零防护。

### 2.2 设计目标

- **fail-closed 原则**：**唯一例外于其他 6 大核心服务的降级策略** —— LSG 任何校验器故障必须**拒绝调用**，不能 "degraded=True 继续"
- **四层防御**：输入分类 → System Prompt 隔离 → 输出 Schema → Pattern 巡检
- **零信任 LLM 响应**：即便本地 Qwen2.5-3B 输出也必须过 L3/L4
- **绕过率 < 5%**：Phase 1 末红队评估基准
- **与 Agent Sandbox 协同**：LSG（输入输出检查）+ Sandbox（运行时隔离）= 双层

### 2.3 参考真源

- `vibe-coding-audit-merged.md §Kimi 11.6.1 双 P0 根因（Prompt Injection）`
- `vibe-coding-audit-merged.md §Qwen 选型表 #15-17`
- `vibe-coding-audit-merged.md §GLM D11 2.2/10（最薄弱）`
- `llm-security-gateway-interface.md v1.0.0`（814 行，B-a-5）
- `06-security-architecture.md §4`

---

## 3. 考虑过的方案（Options Considered）

### 方案 A：四层防御 + Pydantic v2 + 正则 Pattern 库 ✅

- **优点**：
  - **zero-trust** 四层独立校验，单层失效不导致漏防
  - Pydantic v2 `extra='forbid'` 未知字段一律拒绝
  - 正则 Pattern 库对 API Key / Secret 漏报率业界基线 < 3%
  - 规则可由人工或红队评估持续扩充
  - Phase 1 本地实现，零外部依赖
- **缺点**：
  - 静态规则对 zero-day prompt injection 漏拦（接受）
  - 正则对变体攻击敏感（需定期更新）

### 方案 B：重型 NLP 分类器（BERT / DeBERTa-based）

- **优点**：对新型 prompt injection 识别率高
- **缺点**：
  - 模型大（300MB+）+ 推理延迟 > 200ms（影响 AI 编码体验）
  - 单模型黑盒，误拦后难调试
  - 训练数据依赖
- **结论**：**否决 Phase 1**（TECH-16 升级路径保留）

### 方案 C：LLM-as-Judge（用另一个 LLM 检测攻击）

- **优点**：识别最灵活
- **缺点**：
  - 成本高（每次调用双 LLM）
  - LLM-as-Judge 本身可能被 injection
  - 延迟叠加
- **结论**：**保留为 Phase 2 补强**（与方案 A 叠加）

### 方案 D：商业服务（如 Lakera Guard / Rebuff）

- **优点**：专业团队维护
- **缺点**：
  - 数据上云（合规风险 + 代码外泄）
  - 月费不可控
- **结论**：**否决**

---

## 4. 决策（Decision）

**最终选择：方案 A — 四层防御 + Pydantic v2 + 正则 Pattern 库 + fail-closed**

### 4.1 关键决策点

| 决策点 | 首选 | 备选 | 升级触发 |
|-------|------|------|---------|
| **Schema 校验** | Pydantic v2 + `extra='forbid'` | Marshmallow | 不升级（Pydantic 是事实标准）|
| **Pattern 库** | 正则基（LLM API Key 25+ 条）| LLM-as-Judge | 红队绕过率 > 5%（TECH-16）|
| **Secret 扫描** | git-secrets + trufflehog | HashiCorp Vault Policy | Phase 2 生产 |
| **供应链扫描** | pip-audit + safety | Snyk | 出现 CVE 被利用 |
| **运行位置** | MCP Server 前置（library 模式）| 独立网关进程 | Phase 3+ 多 IDE 多用户 |
| **降级策略** | **fail-closed**（不降级）| — | 本 ADR 核心原则 |

### 4.2 四层防御细则

**L1 输入分类器（前置）**：

- 检测已知 Prompt Injection Pattern（`ignore previous instructions` 变体）
- 过滤注入外部文档（Markdown / 图片 EXIF / ZIP 含恶意）
- 启发式评分 > 阈值 → fail-closed 拒绝

**L2 System Prompt 隔离（Wrapper）**：

- 双层 prompt：System Prompt（硬约束）+ User Prompt（可变）
- 分隔符 `<|USER_INPUT_START|>` ... `<|USER_INPUT_END|>`（模型不可 echo）
- 权限升级请求（如"as root" / "扮演管理员"）→ 拒绝

**L3 输出 Schema 验证（后置）**：

- 所有工具调用返回必须 Pydantic v2 Model + `extra='forbid'`
- 输出正则扫描 Secret Pattern（25+ 条，含 `AKIA*` / `sk-ant-*` / `sk-proj-*` / 自定义）
- 发现 Secret → **fail-closed 丢弃整个响应** + FLE 异常事件

**L4 Pattern 巡检（累积）**：

- 滑动窗口 (60s) 累计异常分
- EMA 阈值触发后，暂停该 Agent 会话 + 人工审查
- 触发计入 `security_events` audit 表

### 4.3 fail-closed 语义（关键差异）

| 服务 | 故障时策略 |
|------|-----------|
| CE / VMS / Orc / FLE | **degraded=True** 返回空或降级，继续工作流 |
| **LSG** | **fail-closed**：任何校验器故障立即**拒绝调用**，不允许继续 |

理由：**LSG 是安全屏障**，"宁可拒绝合法请求，不可放行攻击"。误拦 2% 可接受（用户重试）；漏拦 5% 不可接受（可能泄密 / 资金损失）。

### 4.4 Phase 1 SLO（硬约束）

| 指标 | Phase 1 | Phase 2 |
|------|:-------:|:-------:|
| 误拦率（合法请求被拒）| < 2% | < 0.5% |
| 漏拦率（攻击被放行）| < 5% | < 1% |
| LSG 延迟 P99 | < 200ms | < 100ms |
| fail-closed 触发率 | < 0.1%/天 | < 0.01%/天 |

Phase 1 末**必须跑一次红队评估**（模拟 LLM01/02/06/08/09 攻击），阈值未达标触发 **TECH-16 升级**。

---

## 5. 后果（Consequences）

### 5.1 正面后果

- **D6 红线修复**：12 维审计 D6 从 2.2/10 升至 Phase 1 末目标 5.5/10
- **SEC-01 / 03 / 04 / 05 四个 P0 缺口一并关闭**
- **ADR-0018 双层防护**：LSG（前置）+ Sandbox（运行时）双保险
- **零外部依赖**：Phase 1 本地可运行

### 5.2 负面后果

- **fail-closed 初期误拦**：用户体验短期下降（预计 1-2% 合法请求被拒）
- **规则维护成本**：Pattern 库需季度更新（红队评估驱动）
- **延迟叠加**：+ ~100ms（已在 SLO 约束内）
- **对新型 zero-day 攻击防御弱**：Phase 2 补 LLM-as-Judge

### 5.3 未来重新评估触发条件

- **TECH-16**：红队绕过率 > 5% → Pattern + LLM-as-Judge + 专用模型（混合栈）
- 出现 zero-day 且 >5% 用户中招 → 立即启动专用分类器（本 ADR superseded）
- Phase 2 接入真实资金 → SLO 从 "漏拦 < 5%" 升级 "漏拦 < 1%"
- Phase 3 外部用户 → LSG 需支持多租户策略隔离

---

## 6. 落地动作（Implementation）

| # | 动作 | 物理位置 | 估时 |
|---|------|---------|:----:|
| 1 | `LLMSecurityProtocol` 抽象基类 | `src/zephyr/llm_security/protocol.py` | 0.5 天 |
| 2 | L1 输入分类器（启发式 + Pattern）| `src/zephyr/llm_security/layers/l1_input.py` | 1 天 |
| 3 | L2 System Prompt Isolator | `src/zephyr/llm_security/layers/l2_isolator.py` | 0.5 天 |
| 4 | L3 输出 Schema + Secret Scanner | `src/zephyr/llm_security/layers/l3_output.py` | 1 天 |
| 5 | L4 Pattern Auditor + EMA | `src/zephyr/llm_security/layers/l4_auditor.py` | 0.5 天 |
| 6 | Pattern 库（25+ Secret 正则）| `src/zephyr/llm_security/patterns/secrets.yaml` | 0.5 天 |
| 7 | git-secrets + trufflehog 集成 | `scripts/hooks/secret_scan.py` | 0.5 天 |
| 8 | pip-audit + safety CI 接入 | `.github/workflows/supply_chain.yml` | 0.5 天 |
| 9 | 红队评估脚本 | `scripts/governance/red_team_eval.py` | 1 天 |
| 10 | P0 测试组（5 个 OWASP 场景覆盖）| `tests/llm_security/test_p0.py` | 1 天 |

**总工时**：约 7 人日

---

## 7. 参考

- **真源**：
  - `vibe-coding-audit-merged.md §Kimi 11.6.1`（Prompt Injection 双 P0 根因）
  - `vibe-coding-audit-merged.md §Qwen 选型表 #15-17`
  - `vibe-coding-audit-merged.md §GLM D11 2.2/10`
- **接口规范**：[`llm-security-gateway-interface.md v1.0.0`](../../03_modules/_b_track_interfaces/llm-security-gateway-interface.md)
- **安全架构**：[`06-security-architecture.md §4`](../target-architecture/06-security-architecture.md)
- **归档旧契约**：`archive/reorg-2026-04-24/08_ai_engineering/tool-interface-contract.md`
- **技术选型**：[`technology-landscape.yaml TECH-15/16/17`](../target-architecture/architecture-model/technology/technology-landscape.yaml)
- **相关 ADR**：ADR-0017（Orc 集成）/ ADR-0018（Sandbox 协同双防）/ ADR-0019（FLE 上报方）/ ADR-0021（SSoT 前置）
- **外部**：
  - [OWASP LLM Applications Top 10 (2024)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
  - [Pydantic v2 strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/)
  - [git-secrets](https://github.com/awslabs/git-secrets) / [trufflehog](https://github.com/trufflesecurity/trufflehog)

---

## 8. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-04-24 | v1.0.0 初版：四层防御 + fail-closed + OWASP LLM Top 10 映射；12 维审计 D6 红线修复；B-e-7 产出。 |
