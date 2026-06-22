---
module_id: KE-041------canonical-ssot----arc-006
status: active
title: 6.9 架构数据 Canonical SSoT 铁律（Architecture Data Canonical SSoT Mandate）
category: agent_instruction
---

# 6.9 架构数据 Canonical SSoT 铁律（Architecture Data Canonical SSoT Mandate）

6.9 架构数据 Canonical SSoT 铁律（Architecture Data Canonical SSoT Mandate）

> **v1.1.0（2026-05-06）**：增补双树口径——详见仓库根 **`architecture-model/SCOPE.yaml`**。简而言之：**EA 契约/不变量/完整技术雷达**在 `docs/02_enterprise_architecture/target_architecture/architecture-model/`；**施工分区（C/B 轨）与 GATE-A 对齐**在根目录 `architecture-model/`。本节泛称「`architecture-model/`」时，AI MUST 先读 SCOPE 再落笔，避免改错文件。

> **v1.0.0（2026-05-02）**：架构数据的 canonical SSoT 必须是 YAML（`architecture-model/`），Markdown 视图（`00-10*.md`）是从 YAML 派生的人类可读呈现。对标 K8s CRD YAML / Terraform tf.json / OpenAPI spec.yaml —— 五家专业机构中四家用机器可读格式作为 canonical 真源。

**核心原则**：**谁能被机器零人工干预消费，谁就是真源。** YAML 能被 AI 直接解析、CI 门禁强校验、代码生成器消费——Markdown 需要 NLP 推理，有歧义风险。因此 YAML 是真源，Markdown 是翻译。

- **规则**：
  1. **YAML 优先**：任何架构事实（模块分层、技术选型、能力归属、接口契约、不变核心）必须先在 `architecture-model/` YAML 中定义，Markdown 视图可以引用、翻译、解释——但不得成为同一事实的独立定义源
  2. **冲突裁决**：YAML 与 Markdown 对同一事实描述不一致时 → **以 YAML 为准**。Markdown 视图需要同步更新以匹配 YAML。裁决记录写入 `architecture-rationale-log.md`
  3. **新事实入库流程**：新模块/新属性 → 先写入 **`SCOPE.yaml` 对应树** 下的 YAML：`architecture-model/layers/`（施工）或 `docs/02_enterprise_architecture/.../architecture-model/`（契约/雷达等 EA 条目）；**ThoughtWorks 风格完整技术雷达条目**仅以 `docs/.../architecture-model/technology/technology_landscape.yaml` 为真源——根目录 `architecture-model/technology_landscape.yaml` 仅为施工摘要，**条目 ID 使用 `IMPL-T-*`**（与 EA 树 `technologies[].id` 的 `T-*` 刻意隔离，禁止按同号对齐），语义（如 Python ≥3.11）须与 EA 对账。然后再更新 Markdown 视图引用（如需叙事扩展）
  4. **CI 门禁强制**：`check_architecture_gates.py` GATE-03 已校验"模块在 Markdown 视图中声明的分层 = YAML SSoT 中的分层"，不一致 → CI 失败。未来新增 Gate 应继续以此原则为基础
  5. **生成的文档标注**：从 YAML 自动生成的 Markdown 内容必须标注 `[generated from YAML SSoT]`，让读者知道这是派生内容、非独立定义

- **为什么 YAML 而不是 Markdown 作为 canonical**：

  | 维度 | YAML | Markdown |
  |------|:---:|:---:|
  | 机器可解析 | ✅ 零歧义，结构化解析 | ❌ 需要 NLP 推理，可能误解 |
  | CI 可强制校验 | ✅ `check_architecture_gates.py` 可直接比对 | ❌ 只能正则搜索，无法语义校验 |
  | AI 可消费 | ✅ 精确字段匹配 | ⚠️ 模糊匹配，可能漏读或误读 |
  | 人类可读性 | ⚠️ 需要一定学习成本 | ✅ 自然阅读 |
  | 适合做 canonical | ✅ | ❌（适合做 presentation） |

  YAML 的弱点"人类可读性"由 Markdown 视图补足——这恰恰是"一源双态"模式的设计意图：canonical 负责精确，presentation 负责易读。

- **专业参考**：K8s → CRD YAML as canonical schema + `kubectl explain` as derived docs / Terraform → `.tf.json` as canonical + `terraform-docs` as derived README / OpenAPI → `spec.yaml` as canonical + Swagger UI as rendered presentation / ISO 42010 → Architecture Description 可以有多种 View，但 Rationale（为什么）和 Model（有什么）必须可追溯至同一 canonical 源
