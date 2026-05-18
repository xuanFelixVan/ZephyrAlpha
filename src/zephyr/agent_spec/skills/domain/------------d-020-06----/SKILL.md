---

skill_id: SKILL-DOM-{{MODULE_ABBR}}-{{NUMBER}}
name: "=== 蓝图漂移（决策 D-020-06）==="
description: ""
allowed-tools: [Read, Grep, Glob, Edit, Write, Bash]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-06
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
blueprint_id: MOD-INF-019
---


# Domain Skill: === 蓝图漂移（决策 D-020-06）===

## CRITICAL Rules

### Core Operations
### 5.5 间接操作检测（决策 D-020-21）

> **决策 D-020-21**（新增）：Agent 可能不直接修改目标文件，而是通过 symlink、hardlink、生成脚本、cron job、MCP 委托等方式间接操作。检测方法：(a) Agent 写入的任何内容扫描潜在执行路径（脚本/shebang/shell），(b) 写入文件后短时间内被执行→关联审计，(c) MCP 操作记录携带 `indirect_operation=True`。

```python
class IndirectOperationDetector:
    """间接操作检测器——对标 ANM-011"""

    def scan_generated_scripts(self, entry: AuditEntryV1) -> bool:
        """检测 Agent 是否生成了可执行脚本——潜在间接操作"""

    def correlate_write_execute(self, write_entry: AuditEntryV1, exec_entry: AuditEntryV1) -> float:
        """关联写入→执行——返回关联度 0.0~1.0"""

    def trace_indirect_path(self, entry: AuditEntryV1) -> list[str]:
        """追踪间接操作路径——symlink→target, script→cron→target"""
```

### Unique Constraints
### 1.3 运行场景约束

| 约束 | 影响 |
|------|------|
| 多 IDE 并发（TRAE/Cursor/RooCode） | 审计日志必须跨 IDE 统一——JSONL 是唯一所有 IDE 都能 append 的格式；需要 Lamport 逻辑时钟解决时序；需要跨 IDE 一致性交叉验证 |
| 10+ 并发对话 | 审计量可能很大——需要两层粒度 + 自动摘要，不能全是文件级 |
| 1 人 + AI，99% AI 维护 | 无人监控审计系统健康 → 必须自监控（heartbeat + 自检 + 自动修复）；审计日志读者 99% 是 AI → 查询结果必须是 AI 零推理可消费的结构；需要外部独立验证端点（AI 不能自证清白） |
| 先干后验模式 | 审计日志是后验的基础——没有审计就没有后验；需要 Dry-Run 预审计模式；Dry-Run vs Real 差异检测 |
| 100% AI 施工 | 审计系统自身的代码也是 AI 写的 → 元审计和自监控是刚性需求；审计代码不可用于自证（需要外部 verifier） |

### Common Error Patterns
待填写

## Checklist

- [ ] Verify blueprint before implementation
- [ ] Check upstream dependencies
- [ ] Validate against acceptance criteria
- [ ] Run gate engine checks (G0-G9)

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| DEFAULT_TIMEOUT | 30 | Default operation timeout (seconds) |

## References (L3, on-demand)

- module_blueprint.md
- integration_guide.md
- troubleshooting.md