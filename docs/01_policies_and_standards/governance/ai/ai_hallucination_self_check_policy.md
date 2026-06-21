---
module_id: GOV-AI-003
title: AI 幻觉自检清单
doc_type: policy
status: active
version: 1.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-01"
valid_from: "2026-05-01"
ttl: permanent
summary: "每个 AI session 开始前必须逐项自检，防止 AI 在无完整上下文的情况下幻觉补全架构信息。"
tags: [ai, hallucination, self-check, governance]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
ai_autonomy: human_gated
depends_on:
  - {target: PS-STD-001, at: "§2.5", why: "frontmatter 字段真源——SSoT 验证依赖元数据注册表"}
  - {target: META-GLS-001, at: "L1", why: "核心术语定义——SSoT/原子事务等术语的仲裁源"}
---

# AI 幻觉自检清单

> 每个 AI session 开始前 MUST 逐项自检。禁止在无完整上下文时幻觉补全路径/接口/依赖。
> 历史教训：AI 在不知道完整架构时会幻觉补全接口（超时/重试/异常类型）、编造路径、推断错误依赖 → 架构污染。

## 自检清单（session 开始前逐项确认）

### 检查项 1：文件路径验证

在引用任何文件路径之前，必须确认该文件实际存在：

- [ ] 我引用的所有文件路径都已通过 `Glob` / `LS` / `Read` 确认存在
- [ ] 我没有编造任何文件路径（即使路径"看起来合理"）
- [ ] 如果文件不存在，我会明确说明"文件不存在"而不是假装它存在

### 检查项 2：模块 ID 验证

在使用任何模块 ID 之前，必须确认该 ID 在注册表中存在：

- [ ] 我使用的所有模块 ID 都已在 `metadata-registry.md`（PS-STD-001）或 `document-metadata-index.yaml` 中确认存在
- [ ] 我没有自行发明模块 ID
- [ ] 如果需要新 ID，我会按 `metadata-registry.md` §2.1 命名空间清单申请

### 检查项 3：接口定义验证

在引用任何接口定义之前，必须确认该接口在契约文件中存在：

- [ ] 我引用的所有接口都已在 `src/zephyr/shared/contracts/` 中确认存在
- [ ] 我没有幻觉补全接口的参数类型、超时值、异常类型
- [ ] 如果接口未定义，我会标注"接口待定义"而不是自行补全

### 检查项 4：依赖关系验证

在声明任何模块依赖关系之前，必须确认依赖方向正确：

- [ ] 依赖方向符合项目分层架构（低层依赖高层是错误的）
- [ ] 我没有创建循环依赖
- [ ] 如果依赖关系不确定，我会标注置信度（L1/L2/L3）

### 检查项 5：SSoT 验证

在修改任何字段值之前，必须确认权威来源：

- [ ] 我修改的字段的权威来源已在 `meta/metadata-registry.md` §2.5 中确认
- [ ] 我没有在非权威文件中修改权威字段
- [ ] 如果字段在多个文件中出现，我只修改权威来源文件

### 检查项 6：编号规范验证

在使用任何编号之前，必须确认符合统一编号规范：

- [ ] 模块 ID 使用 `GOV-XXX` / `PS-XXX` / `OPS-XXX` / `META-XXX` 格式（对齐 `metadata-registry.md` §2.1 命名空间清单）
- [ ] 文档编号不包含版本号后缀（-v2/-v3），生命周期由 `version` 字段表达
- [ ] 编号引用使用 `module_id` 精确引用，不使用"在上级目录中"等相对描述

### 检查项 7：操作权限验证

在执行任何文件操作之前，必须确认在权限范围内：

- [ ] 我要操作的文件路径在我的 `model-capability-contract.yaml` 允许路径列表中
- [ ] 我本次 session 新建的文件数量未超过限制（≤5 个）
- [ ] 我没有操作禁止路径（`.cursor/rules/`、`AGENTS.md`、`.roomodes`）

### 检查项 8：编码安全验证

- [ ] 当前编辑器编码设置为 UTF-8
- [ ] 如果使用 Trae：`files.autoGuessEncoding = false`
- [ ] 没有两个编辑器同时打开同一文件

### 检查项 9：任务范围验证

- [ ] 本次 session 的任务在 `document-metadata-index.yaml` 中有明确对应
- [ ] 任务的前置条件已满足
- [ ] 我不会执行任务清单之外的操作（除非 Owner 明确指示）

### 检查项 10：引用出处验证

在引用任何架构决策、技术选型、设计原则时：

- [ ] 我能指出该信息的具体来源文件和行号
- [ ] 我没有从"记忆"中引用（每次 session 都是全新的，没有跨 session 记忆）
- [ ] 如果来源不确定，我会明确说明"来源待确认"

## 自检失败的处理

如果任何检查项无法确认（无法验证文件存在、无法确认 ID 合法等）：

1. **停止当前操作**
2. **明确说明无法确认的原因**
3. **如果是幻觉类失败**（编造路径/补全接口/假设 ID）：参见 `ai-onboarding-guide.md`（GOV-AI-002）事故响应路由表 → 幻觉列 → OPS-VC-006
4. **其他无法判定的失败**：请求 Owner 提供缺失的信息
5. **禁止用"合理推断"替代实际验证**

---

## Session 中期二次自检

**触发条件**：context 用量达 60% 时 MUST 执行。AI 在 context window 60%+ 时倾向跳过文件读取、凭残片"记忆"补全 → 幻觉率显著升高。

重跑以下 5 项：

- [ ] **检查项 1**（文件路径）：本次 session 已完成的操作中，所有文件路径引用是否确实读取了源文件？
- [ ] **检查项 2**（模块 ID）：本次 session 使用的模块 ID 是否均在注册表中？
- [ ] **检查项 5**（SSoT）：本次 session 修改的字段是否均来自权威来源？
- [ ] **检查项 7**（操作权限）：剩余上下文内是否还有超出权限的操作计划？
- [ ] **检查项 10**（引用出处）：近期输出中的架构决策/路径引用能否追溯到具体源文件？

**二次自检失败**：立即停止剩余操作，写 Session Log 标注失败点，走事故响应路由（幻觉 → OPS-VC-006）。剩余任务留给下一个 session 续接。

---

## 附录：已知幻觉模式清单

| # | 幻觉模式 | 典型表现 | 后果实例 |
|---|---------|---------|---------|
| 1 | **路径幻觉** | 引用语法正确但不存在的文件路径（如 `ssot-authority-map.md`、`module-id-registry.json`） | 下游操作全部基于不存在的文件，需回滚整次 session |
| 2 | **接口补全幻觉** | 未读接口定义就"合理推断"参数类型/超时值（300ms）/异常类型（TimeoutError） | 代码运行时报 TypeError，因为实际参数是 dict 不是 int |
| 3 | **编号格式幻觉** | 假设 ID 是 `MOD-XXX`/层编号 `L00-L13`，实际已变为 `GOV-XXX`/`PS-XXX` 命名空间 | 注册表中找不到引用，产生孤儿引用链 |
| 4 | **上下文溢出幻觉** | Session 60%+ context 时不读文件，凭残片"记忆补全" | 路径引用出现相对路径（如"在上级目录中"），违反路径不可漂移原则 |
| 5 | **权限假设幻觉** | 未查 `ai-autonomy-authority-registry.md` 就判断"看起来应该是 AI-Modifiable" | 越权修改 Immutable Core 组件，触发 pre-commit 拒绝 |

**MUST 逐条对照**：本次 session 是否复现了上述任何模式？如有 → 标记 L3（高风险幻觉）→ 走事故路由（`→ OPS-VC-006`）。
