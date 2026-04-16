---
module_id: FORM_SESSION_LOG_TEMPLATE
version: '1.0.0'
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
owner: Project Owner
layer: cross_layer
priority: P1
standard_type: template
parent_document: ../FORM_STANDARDS/INDEX.md
---

# Session Log 模板（会话日志）

> 用途：记录单次 AI 会话的完整上下文。
> 下一个 AI 会话开始前读取此文件可快速还原当前状态，无需重新阅读全库。
>
> 使用方法：复制本文件至 `docs/09_AUDIT/STATE/SESSION_LOGS/`，
> 按命名规范 `session-{YYYYMMDD}-{NNN}.md` 重命名，填写各字段。
> TTL：30 天（到期按价值提取协议处理，重要决策升级到 ADR 或 lessons-learned）。

---

## 元信息

| 字段 | 值 |
|------|-----|
| **会话 ID** | `session-YYYYMMDD-NNN` |
| **日期时间** | YYYY-MM-DD HH:MM |
| **执行模型** | Claude Sonnet 4 / Gemini 2.5 Flash / Kimi / Composer 2 |
| **平台** | Cursor / Trae |
| **当前 Phase** | Phase X（阶段名称）|
| **上一份 Session Log** | `session-YYYYMMDD-NNN.md`（若有）|

---

## 本次任务

> 用一句话描述本次会话的主要目标。

---

## 本次完成

- [ ] 任务 1
- [ ] 任务 2
- [ ] 任务 3

---

## 本次变更的文件

| 操作 | 文件路径 | 理由 |
|------|---------|------|
| 创建 | `path/to/file.md` | 简短理由 |
| 编辑 | `path/to/file.md` | 简短理由 |
| 删除 | `path/to/file.md` | 简短理由 |
| 搬迁 | `old/path.md` → `new/path.md` | 简短理由（需符合 File Movement Protocol）|

---

## 关键决策

> 记录本次会话中做出的、影响未来方向的决策（≤5 条）。
> 重要决策须同时写入 `docs/02_ARCHITECTURE/TECH_DECISION_RECORDS.md`（技术选型类）
> 或 `docs/01_GOVERNANCE/REGISTERS/lessons-learned-register.md`（教训类）。

- **决策 1**：…（理由：…）
- **决策 2**：…（理由：…）

---

## 未完成（交给下一个会话）

- [ ] 待做事项 1
- [ ] 待做事项 2

---

## 禁止事项（本任务范围内）

- 禁止 …
- 禁止 …

---

## 给下一个 AI 的快速交接指令

```
【ZephyrAlpha 任务交接指令】
执行模型：[模型名称] | Thinking: [ON/OFF] | MAX Mode: [ON/OFF]

## 当前状态
- 项目阶段：Phase X（[阶段名称]）
- 刚完成：[上一步完成的任务简述]
- 待执行：[下一步任务标题]
- 上一份 Session Log：docs/09_AUDIT/STATE/SESSION_LOGS/session-YYYYMMDD-NNN.md

## 必读文件（按顺序）
1. docs/01_GOVERNANCE/governance-asset-inventory.yaml — 确认治理资产总清单
2. [其他必读文件路径] — [读取目的]

## 执行任务
[具体任务描述，包括：操作文件路径、预期输出、验收标准]

## 禁止事项
- [具体禁止行为]
```
