---
module_id: KE-019-------------index-reality-003
status: active
title: 6.11 索引-实际同步强制约定（Index-Reality Synchronization Mandate）
category: agent_instruction
---

# 6.11 索引-实际同步强制约定（Index-Reality Synchronization Mandate）

6.11 索引-实际同步强制约定（Index-Reality Synchronization Mandate）

> **v1.0.0（2026-05-02）**：触发条件——任何在 `01_policies_and_standards/` 下创建/重命名/删除/移动文件的操作。对标 §6.10 双层对齐闸门——GATE-A/B 管代码↔YAML↔MD，本节管**索引↔磁盘实际**的对齐。

**核心原则**：**索引文件声称的文件数和文件清单，必须与磁盘实际情况一致。** 这不是"建议"——false index 对 AI 冷启动的伤害等同于虚假路标：指向不存在的东西（幽灵文件）、漏掉存在的东西（遗漏登记）、数字对不上（算术错误）。

**为什么这个问题会反复出现**：每次新增/删除文件后，需要同步更新的索引文件多达 5+ 个（PS-IDX-001、目录级 index.md、document-metadata-index-registry.yaml、registry-master-index.yaml、module_id_registry.yaml）。没有自动化门禁强制校验，完全依赖 AI 人工记忆——而 Vibe Coding AI 的上下文记忆极短（§5.1），必然漂移。

- **强制同步清单**（创建/删除文件时，以下索引 MUST 同步更新）：
  1. **目录级 index.md**（被操作文件所在目录的导航索引）——文件清单表 + 文件数
  2. **PS-IDX-001**（`01_policies_and_standards/index.md`）——目录树 + §二文件数表格 + 总合计
  3. **_registry/catalogs/** 下的登记表（如 registry-master-index.yaml、document-metadata-index-registry.yaml）——若该文件在登记范围内
  4. **架构模型登记表**（如 module_id_registry.yaml、directory-registry.md）——若该文件需架构级登记

- **操作后自检**（创建/删除文件后，AI MUST 立即执行）：
  1. `grep` 扫描所有 index.md 中是否还引用了已删除的文件（幽灵检查）
  2. `grep` 扫描新文件是否被所有相关索引覆盖（遗漏检查）
  3. 对比 PS-IDX-001 的总文件数是否与 `document-metadata-index-registry.yaml` 的 total_files 一致

- **禁止行为**：
  - ❌ 跳过索引更新，认为"以后再说"——不存在"以后"
  - ❌ 更新了一个索引但漏了另一个——原子事务：要么全更新，要么全不更新
  - ❌ 手动维护类索引（PS-IDX-001）的数字凭"感觉"估算——必须先 `ls | wc -l` 或查 auto-generated registry 确认

- **终极解决方案（Backlog）**：
  - 当前所有索引数字和文件清单均为手动维护，这是漂移的根因
  -  `validate_index_reality.py` CI 脚本——自动扫描目录 ↔ 交叉对比所有 index.md 中声称的文件数
  - "手动维护的数字"改为从 auto-generated registry 派生，消除二次漂移可能

- **专业参考**：ITIL SACM → CMDB 与实际基础设施必须定期对账（reconciliation）/ AWS Config → 持续评估资源配置与期望状态的偏差 / Git `git ls-files` → 任何时刻都能精确回答"仓库里到底有什么文件"

