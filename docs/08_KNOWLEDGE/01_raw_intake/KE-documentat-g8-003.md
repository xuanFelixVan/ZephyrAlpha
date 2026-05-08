---
module_id: KE-documentat-g8-003
title: G8 门禁：路径校验（施工前）
category: documentation
---

# G8 门禁：路径校验（施工前）

G8 门禁：路径校验（施工前）

**触发时机**：施工前（打开任务卡后、写任何文件前）。

**工具**：`python scripts/governance/construction_gate.py check <task_card.md>`

**原理**：PathResolver 扫描 `src/zephyr/` 当前目录树，对比任务卡的 `downstream_outputs` 路径：

| 状态 | 含义 | 处置 |
|------|------|------|
| `OK` | 路径匹配当前项目结构 | 放行 |
| `PATH_DRIFT` | 同名文件在其他位置找到 | **自动更正**任务卡路径 → 放行 |
| `NAME_VARIANT` | 相似文件名（≥90%）找到 | **自动更正**任务卡路径 → 放行 |
| `MISSING` | 项目内无匹配 | **人工确认**——可能需创建新目录 |

> **铁律**：G8 状态不是 OK 时，AI 必须先更正路径再施工，禁止按原任务卡路径盲目创建文件。

---
