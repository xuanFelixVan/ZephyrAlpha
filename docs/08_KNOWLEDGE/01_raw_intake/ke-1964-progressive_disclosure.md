---
module_id: KE-1873-----003
status: active
title: 2.3 Progressive Disclosure 加载策略（决策 D-019-04）
category: module_blueprint
---

# 2.3 Progressive Disclosure 加载策略（决策 D-019-04）

2.3 Progressive Disclosure 加载策略（决策 D-019-04）

> **决策 D-019-04（新增）**：所有 Skill 采用三层渐进披露加载策略——不一次性加载全部内容，而是按实际需要逐层展开。对标 Anthropic Claude Skills 标准实践。
>
> **决策依据**：
> - 一次性加载 2000-3000 tokens 的 Skill Pack 在 10+ 并发对话下 token 消耗超预计（AI 的注意力在长指令中会被稀释）
> - Anthropic 白皮书证实：frontmatter ~50 tokens + SKILL.md body ~500 tokens 是最优的组合粒度
> - 大型蓝图 §1-§12 全部加载无意义——99% 的情况下 AI 只需要其中 1-2 个章节

```yaml
progressive_disclosure:

  L1_metadata:
    description: "YAML frontmatter（~50 tokens）——always loaded，路由匹配用"
    contains:
      - "skill_id + name + description"
      - "allowed-tools（权限约束）"
      - "model_hint（推荐模型：DeepSeek/Claude/GLM）"
      - "freshness_score + last_validated"
    load_condition: "AGENTS.md 触发表匹配 → 常驻内存"

  L2_body:
    description: "SKILL.md body（~300-500 tokens）——task-match 时加载"
    contains:
      - "CRITICAL 规则（不可违反的铁律）"
      - "操作检查清单（Checklist 格式——非建议、非描述）"
      - "领域关键常量/模式速查表"
      - "需要加载的 reference 文件列表（可选，延迟加载）"
    load_condition: "任务类型匹配触发表 → 加载 L1+L2"

  L3_references:
    description: "关联文件（2000+ tokens per file）——按需探取"
    contains:
      - "蓝图对应章节（如数据库蓝图 §3 ATM 事务模式）"
      - "代码样例文件（如 gate_engine.py 门禁评估逻辑）"
      - "完整 bug 模式库（如 drift-detector 的异常行为签名表）"
    load_condition: "AI 判断需要更深入的上下文时，主动读取 L3 文件"
    retrieval_method: "文件路径索引（L2 中列出）或 MCP context retrieval"
```

**Progressive Disclosure 在 AGENTS.md 中的表达**：

```markdown
