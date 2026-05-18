---

skill_id: SKILL-DOM-{{MODULE_ABBR}}-{{NUMBER}}
name: "MOD-INF-013"
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


# Domain Skill: MOD-INF-013

## CRITICAL Rules

### Core Operations
# 所有变更操作默认 --dry-run=True，明确传 --apply 才真正执行

### Unique Constraints
### 1.3 运行场景约束

| 约束 | 影响 |
|------|------|
| 1 人 + AI，100% AI 施工 | 盘点系统自身代码也是 AI 写的 → 必须自监控 + 自愈；盘点扫描由定时 Pipeline 触发，无需人工 |
| 多 IDE 并发（TRAE/Cursor/RooCode） | 多个 IDE 同时创建文件 → 盘点扫描可能读到不完整文件 → 扫描时需检测锁文件 `.ailocks/` 并跳过锁定中的文件 |
| 10+ 并发对话 | 资产变更频繁 → 全量扫描不宜太频繁（建议 1 次/小时），增量对账可实时（事件驱动） |
| 先干后验模式 | 盘点发现孤儿 → 先不阻断施工 → 标记为 orphan → 定期报告 → Owner 决策是否补注册或清理 |
| 项目持续膨胀 | 从当前 ~600 资产 → 未来可能数千 → 扫描器必须支持增量模式 + 并行（RULE-SEVEN ThreadPoolExecutor） |
| 99% AI 消费者 | 盘点输出格式必须 AI 零推理可消费——结构化 YAML/JSON，禁止自然语言描述关键字段 |

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