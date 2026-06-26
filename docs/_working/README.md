---
title: 临时工作区（_working/）
doc_type: index
ttl: permanent
---

# _working/ 临时工作区

> **本目录是所有过程性文档的默认落点。**
> AI 创建的过程性文档（施工方案/评估报告/提案/调研报告/临时笔记）**必须**放在本目录下，禁止直接放入永久区。

## 一、什么文件放这里

| 文件类型 | 示例 | ttl |
|---------|------|-----|
| 施工方案 | `domain_split_plan_xxx.md` | task_bound |
| 评估报告 | `xxx_assessment.md` | task_bound |
| 规则提案 | `xxx_proposal.md` | task_bound |
| 调研报告 | `xxx_root_cause_report.md` | task_bound |
| 临时笔记/探针产出 | `_tmp_xxx.md` | task_bound |

## 二、什么文件不放这里

以下路径是**永久区**，只存放"结果型"文档（经用户批准才能进入）：

- `docs/01_policies_and_standards/` — 规则、标准、协议
- `docs/02_enterprise_architecture/` — 架构定义、目标架构、决策记录
- `docs/03_modules/` — 模块蓝图、清单
- `docs/08_knowledge/` — 知识库沉淀

**永久区准入规则**：要晋升文件到永久区，必须经用户同意（GitCommitGateway 门禁，后续实现）。

## 三、文件生命周期

```
AI 创建过程文件 → 默认落 docs/_working/（ttl=task_bound）
    │
    ├─ 任务完成 → 文档失效，可清理
    │
    └─ 文件有长期价值，经用户批准 → 晋升到永久区（ttl=permanent）
```

## 四、判定规则

文档 ttl 二元判定（详见 [ttl_vocabulary.yaml](../01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml) 的 decision_tree）：

- **在永久区路径** → `permanent`
- **不在永久区路径**（含 `_working/`）→ `task_bound`

AI 创建文档时，**默认放 `_working/`**，除非用户明确要求创建永久文件。

## 五、AI 读取本目录文档前必须自查（防幽灵引用）

本目录是 task_bound 过程性文档堆积区，文档里引用的脚本路径、规则 YAML、blueprint_id 会随项目演进过时，变成"幽灵引用"。AI 读取本目录任何 .md 前，**必须**先验证文档提到的真源是否还在：

1. **提取引用**：把文档里提到的 `scripts/xxx.py`、`docs/.../*.yaml`、`MODULE-ID` 这类真源标识挑出来
2. **验证存在**：用 `git ls-files <path>` 或文件系统检查这些路径是否仍存在
3. **幽灵引用处置**（目标已删除/改名/移动）：
   - **不要照文档执行**——过时信息当真 = 幻觉和漂移的源头
   - 在回复里告诉用户"这文档引用的 xxx 已不存在，内容可能过时"
   - 去查当前真源：`python -m zephyr.governance.capability_lookup find <关键词>` 反查能力的 canonical 文件
4. **版本漂移处置**（目标还在但字段名/值域变了，如 ttl 词表从 6 值改 2 值）：
   - **以当前真源为准**，不以上述文档为准
   - 必要时提示用户文档内容与新真源不一致
