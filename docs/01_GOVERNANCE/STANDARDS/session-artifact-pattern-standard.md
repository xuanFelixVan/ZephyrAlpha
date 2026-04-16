---
module_id: GOV_SESSION_ARTIFACT_PATTERN_STANDARD
version: '1.0.0'
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
owner: Project Owner
layer: cross_layer
priority: P1
standard_type: governance
parent_document: ../STANDARDS/INDEX.md
---

# Session Artifact Pattern 标准

> **核心目标**：解决 AI 辅助开发（氛围编程）中"每次新会话 = 新员工入职"的上下文丢失问题。
>
> 对标来源：企业知识管理 Session Continuity Pattern / Bridgewater Error-to-Rule 机制 /
> 跨会话 AI 交接最佳实践。

---

## 一、为什么需要 Session Artifact Pattern

在 AI 辅助开发中，每次会话结束后 AI 的上下文窗口清空，相当于**员工瞬间离职**。
下一个 AI 会话（"新员工"）面临：

| 问题 | 表现 |
|------|------|
| 不知道上一步做了什么 | 重复执行已完成的工作，或跳过关键前置步骤 |
| 不知道文件为什么在这里 | 凭感觉搬迁文件，导致反复移动 |
| 不知道某个决策的理由 | 推翻上一个 AI 的正确决定 |
| 不知道下一步该做什么 | 读全部文档重新推断，耗时且不准确 |

Session Artifact Pattern 通过**四部分标准产出物**建立 AI 会话间的异步通信通道，
使任意 AI 会话都能在 **5 分钟内**还原完整的工作上下文。

---

## 二、四部分产出物（Four-Part Artifact）

```
Session Artifact
├── Part 1: Session Log（会话日志）    ← 记录做了什么
├── Part 2: Decision Journal（决策日记）← 记录为什么这样做（嵌入 Session Log）
├── Part 3: Movement Ledger（搬迁台账）← 记录搬了哪些文件（嵌入 Session Log）
└── Part 4: Handoff Ticket（交接工单） ← 记录下一步该做什么（嵌入 Session Log）
```

Part 2、3、4 均以**字段**形式嵌入 Part 1（Session Log），无需独立文件，
降低维护成本的同时保持完整性。

---

## 三、Session Log 规范

### 3.1 命名规则

```
session-{YYYYMMDD}-{NNN}.md
```

- `YYYYMMDD`：会话发生日期（北京时间）
- `NNN`：当日序号，从 `001` 起，按会话开始时间递增
- 示例：`session-20260416-001.md`、`session-20260416-002.md`

### 3.2 存放位置

```
docs/09_AUDIT/STATE/SESSION_LOGS/
```

- 此目录的 TTL 策略：**30 天**
- 到期处理：先检查"关键决策"字段，若有升级价值则提取至 ADR 或 lessons-learned，
  再删除原文件

### 3.3 模板

模板路径：`docs/09_AUDIT/FORM_STANDARDS/session-log-template.md`

**必填字段**（缺少任一字段视为不合规）：

| 字段 | 章节名 | 说明 |
|------|-------|------|
| 元信息 | `## 元信息` | 会话 ID、日期、模型、Phase、上一份日志链接 |
| 本次任务 | `## 本次任务` | 一句话目标 |
| 本次完成 | `## 本次完成` | Checkbox 列表 |
| 本次变更文件 | `## 本次变更的文件` | 操作/路径/理由三列表格 |
| 关键决策 | `## 关键决策` | 可为空列表（明确写"无"），不可省略节标题 |
| 未完成 | `## 未完成` | 交给下一个会话的 Checkbox 列表 |
| 交接指令 | `## 给下一个 AI 的快速交接指令` | 标准化 Handoff Protocol 文本块 |

### 3.4 写作时机

- **会话结束前**：在完成主要工作任务后，由执行 AI 自行填写并保存
- **会话中途搬迁文件后**：立即更新"本次变更的文件"表格
- **出现重要决策时**：立即写入"关键决策"字段，无需等到会话结束

---

## 四、搬迁台账（Movement Ledger）使用规则

嵌入 Session Log 的 `## 本次变更的文件` 表格即为搬迁台账。

**查询方法**：下一个 AI 想知道某文件的搬迁历史时，执行：

```bash
# 1. 通过 git history 查询（首选，完整且自动）
git log --follow --diff-filter=R --name-status --oneline -- "docs/path/to/file.md"

# 2. 通过 Session Logs 全文检索（补充，可查理由）
grep -r "path/to/file.md" docs/09_AUDIT/STATE/SESSION_LOGS/
```

两者互补：`git log` 提供时间线，Session Log 提供**理由**（git log 只记录 commit message，
Session Log 记录完整决策上下文）。

---

## 五、决策日记（Decision Journal）升级规则

Session Log 中的"关键决策"字段是**轻量级决策记录**，满足以下条件时须升级：

| 条件 | 升级目标 |
|------|---------|
| 涉及技术选型（"为什么用 X 不用 Y"） | `docs/02_ARCHITECTURE/TECH_DECISION_RECORDS.md` |
| 涉及失败教训或已踩过的坑 | `docs/01_GOVERNANCE/REGISTERS/lessons-learned-register.md` |
| 涉及架构层级变动（新增/废弃子系统） | `docs/subsystem-registry.yaml` + `docs/02_ARCHITECTURE/MODULE_INVENTORY.md` |
| 涉及治理工具新增/废弃 | `docs/01_GOVERNANCE/governance-asset-inventory.yaml` |

升级后在 Session Log 原条目标注 `→ 已升级至 [目标文件]`。

---

## 六、Handoff Ticket（交接工单）规范

Session Log 末尾的"给下一个 AI 的快速交接指令"即为交接工单，
格式继承自 `.cursor/rules/project-conventions.mdc` 中的 Handoff Protocol，
新增字段：`上一份 Session Log`（必填）。

**下一个 AI 会话的入职顺序**（覆盖通用 Context Loader）：

1. 读 `docs/01_GOVERNANCE/governance-asset-inventory.yaml`（治理资产总清单）
2. 读 **最新一份 Session Log**（`docs/09_AUDIT/STATE/SESSION_LOGS/` 下日期最大者）
3. 按 Session Log 中"交接指令"的"必读文件"清单继续读取
4. 执行"执行任务"章节中指定的工作

---

## 七、TTL 与价值提取

Session Log 的生命周期：

```
创建（会话结束前）
  → 活跃期（被后续会话引用）
    → 到期（30 天后）
      → 价值提取：扫描"关键决策"字段
          ├── 有升级价值 → 提取到对应桶 → 删除原文件
          └── 无升级价值 → 直接删除（git history 已保留文件变更记录）
```

批量过期处理可运行：

```bash
python scripts/audit/purge_expired_state.py
```

（该脚本会跳过 SESSION_LOGS/ 下 30 天内的文件）

---

## 八、禁止行为

- **禁止**创建 Session Log 后不填写"本次变更的文件"表格
- **禁止**在 Session Log 到期时直接删除（必须先检查"关键决策"字段）
- **禁止**在 SESSION_LOGS/ 之外存放 Session Log（防止被误清理）
- **禁止**省略"给下一个 AI 的快速交接指令"章节（即使会话内容简单）

---

## 九、Change Propagation

修改本标准后，必须同步更新：

| 目标文件 | 原因 |
|---------|------|
| `docs/01_GOVERNANCE/STANDARDS/INDEX.md` | 标准索引 |
| `docs/01_GOVERNANCE/governance-asset-inventory.yaml` | AI 入职体系的 missing_components 状态 → 标记为 active |
| `.cursor/rules/project-conventions.mdc` 中的 Context Loader | 将最新 Session Log 读取步骤加入入职顺序 |

---

## 变更历史

| 版本 | 日期 | 变更描述 | 变更人 |
|------|------|---------|--------|
| 1.0.0 | 2026-04-16 | 初始创建，对标企业 Session Continuity Pattern | AI |
