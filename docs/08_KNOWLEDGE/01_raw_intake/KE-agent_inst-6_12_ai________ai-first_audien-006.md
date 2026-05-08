---
module_id: KE-agent_inst-6_12_ai________ai-first_audien-006
title: 6.12 AI 受众优先原则（AI-First Audience Principle）
category: agent_instruction
---

# 6.12 AI 受众优先原则（AI-First Audience Principle）

6.12 AI 受众优先原则（AI-First Audience Principle）

> **v1.0.0（2026-05-02）**：本项目 100% AI 开发 + 99% AI 维护治理。所有内容和规则的**首要受众是 AI**——人类 Owner 是第二位受众。对标 OpenAPI（spec 面向机器，Swagger UI 面向人）+ Terraform（`.tf.json` 面向机器，`terraform-docs` 面向人），本项目需要同样的"机器优先"设计哲学。

**核心原则**：**写到让 AI 零歧义消费，人类也能读。** 不是写到让人类读得舒服，AI 也能勉强理解。优先级翻转。

- **AI 优先设计的四个维度**：

  1. **机器可解析 > 人类自然阅读**
     - ✅ 优先：YAML / JSON 结构化格式（AI 零歧义解析）
     - ⚠️ 次选：结构化 Markdown 表格（AI 需要表头推理，但尚可）
     - ❌ 反模式：纯自然语言 prose 描述关键事实（AI 可能误读）
     - **对标**：OpenAPI → `spec.yaml`（机器 canonical）→ Swagger UI（人类派生）

  2. **Canonical 格式 = 机器可消费格式**
     - §6.9 YAML canonical SSoT 是本原则的具体执行层
     - 任何"AI 需要读的文件"，应优先使用 YAML 作为 canonical
     - Markdown 是 YAML 的**人类翻译**——不是独立定义源
     - **大白话**：AI 读 YAML 跟读菜单一样精确——字段名就告诉它"这是什么"。AI 读散装 prose 跟读情书一样——需要猜"这句话到底是什么意思"

  3. **受众判定三步法**（新建文件/字段/规则时，AI MUST 执行）：
     - **第一步**："这个文件/字段的**主要消费者**是 AI 还是人？"
       - AI → 格式选 YAML 或结构化 Markdown 表格
       - 人 → 格式可为自然语言 prose（但关键事实仍需结构化交叉引用）
     - **第二步**："AI 读完这一条，能否**零推理**执行？"
       - ✅ 能 → 零歧义（如受控词表中枚举值）
       - ⚠️ 可能需要推理 → 补充大白话翻译
       - ❌ 必须推理 → 格式错误，重构为机器可读格式
     - **第三步**："人类 Owner 读这个格式，**是否需要额外解释**？"
       - 如果需要 → 在机器可读格式基础上追加大白话（双轨模式，§5）
       - 如果不需要 → 保持简洁
     - **对标**：OpenAPI `spec.yaml` → 机器零推理消费 + `description` 字段给人类附加解释

  4. **内容设计偏好——面向 AI session 冷启动**
     - 每个文件的 frontmatter 和开头段落应该能**自描述**——AI 读完第一屏就知道这个文件是什么、怎么用
     - 禁止"读者应该已经知道 X"的隐含前提——**每个 AI session 都是新员工（§5.1）**
     - 自描述结构：文件名说明责任 + 第一行说明格式 + frontmatter 说明状态 + 首段说明"本文解决什么问题"
     - **大白话**：AI 读文件跟拆快递一样——一眼看到盒子上的标签（文件名+frontmatter）就知道里面是什么，不用拆开再猜

- **已有示例（本项目已做好的 AI 优先设计）**：
  - `capabilities.yaml` → YAML 结构化规则，AI 零歧义解析 allow/deny globs
  - `script_manifest.yaml` → YAML 注册表 + `run_all.py` 自动调度
  - `declarative-contract-tracker.yaml` → YAML 五条契约（CT-001~006）+ 自动对账
  - `architecture-model/layers/lXX.yaml` → YAML canonical SSoT（§6.9）

- **未来增强方向**：
  - "人类可读文档中硬编码的数字"改为从 YAML SSoT 自动派生（消除二次漂移）
  - YAML 变更 → 自动触发 `generate_md_from_yaml.py` → Markdown 人类视图自动更新
  - 远期：所有手工维护类索引（PS-IDX-001 等）的数字改为 auto-generated——消除手动维护数字的根本性漂移

- **专业参考**：OpenAPI → Machine-First spec + Human-Second docs（spec 是 canonical，Swagger UI 是派生）/ Terraform → `.tf.json` Machine-First + `terraform-docs` Human-Second / K8s CRD → YAML for API Server + `kubectl explain` for human / ISO 42010 → Architecture Description 可以有多种 View，但 Canonical Model 必须是精确可追溯的

> **大白话**：以前写文档默认给 Owner 看——写 prose 叙事、写"本文件是…"的人类友好开头。从今天起翻转——写文档默认给 AI 看，AI 需要**结构化机器可读格式**在前、人类翻译在后。AI 读 YAML 跟读房产证一样精确、读 prose 跟读小说一样容易误解——所以新东西优先用 YAML 登记，再写 Markdown 解释。"先让机器零歧义消费，再让人轻松阅读"。
