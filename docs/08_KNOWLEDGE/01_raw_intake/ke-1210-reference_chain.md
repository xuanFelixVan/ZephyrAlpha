---
module_id: KE-1124--------reference-chain-003
status: active
title: DOC-009：引用链完整性（Reference Chain Integrity）
category: governance
ttl: permanent
---

# DOC-009：引用链完整性（Reference Chain Integrity）

DOC-009：引用链完整性（Reference Chain Integrity）

`depends_on` 关系必须构成有向无环图（DAG）。禁止引用环、禁止引用已废弃的目标、引用链深度超过阈值时必须告警。

- **规则**：

  1. **无环约束**：`depends_on` 关系及其传递闭包（A→B→C→…）中，任意文件不得引用自身或其上游祖先。禁止 A→B→A 或 A→B→C→A。
  2. **断裂检测**：当 `depends_on` 引用的目标文件不存在、已被物理删除、或 `status: deprecated` 时，引用方在读写时必须立即阻断并告警。
  3. **深度阻断（死规则）**：引用链深度必须 = 1 层（A→B，直接声明）。不允许传递依赖（A→B→C）。如果 A 需要 C 的知识，A 必须直接在 depends_on 中声明 C。超过 1 层 → V1 阻断，不可绕过。对标 npm `dependencies` 字段——只声明直接 `import` 的包，传递依赖由工具解析。对 AI 治理体系而言，不存在"工具解析"——AI 就是消费者，依赖图必须平坦。
  4. **行级精度（Token 优化死规则）**：`depends_on` 必须使用结构化格式 `{target: module_id, at: "§N", why: "原因"}`。`at` 字段精确声明引用目标的章节/行号范围，禁止仅声明文件级依赖。"读整篇"行为直接浪费 AI 上下文窗口（每 100 行无效读取 ≈ 1500 token 虚耗），对标 Anthropic CLAUDE.md "上下文窗口是最重要的有限资源" + PS-REG-001 CODE 域已有 `money.py L152-158` 行级精度格式。缺失 `at` 字段 → V2 警告，累计 3 次 → V1 阻断。
  5. **重定向链防范**：禁止仅作为转发/重定向用途的文件（如"本文件已废弃，请参见 X"的占位文件）。废弃内容走 `superseded_by` 字段，不走节点跳转。

- **违反后果**：引用环导致 AI 无限循环引用解析；断裂引用导致运行时错误或治理信号失真；引用链过长降低解析性能并增大烟囱倒塌风险（改底层文件时不知道上游有谁依赖）；缺失行级精度导致 AI 每次引用全篇阅读，在 100% vibe coding 环境下造成大量 token 虚耗
- **验证方式**：pre-commit 或 CI 中执行所有 `depends_on` 的传递闭包可达性校验；校验 `at` 字段存在性（缺失 → V2 警告）；未被任何其他文件引用的文件标记为潜在废弃候选（与 DOC-008 补充审查）
- **专业参考**：npm → `dependencies` 字段只声明直接 `import` 的包，传递依赖由工具解析 / Kubernetes API → 用户可见引用必须直接，不存在 Deployment→ReplicaSet→Pod 的依赖链 / Anthropic CLAUDE.md → 上下文窗口是最重要的有限资源，精确引用优于全篇加载 / PS-REG-001 CODE 域 → 已有 `money.py L152-158` 行级精度先例
