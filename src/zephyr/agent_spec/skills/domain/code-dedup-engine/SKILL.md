---
skill_id: SKILL-DOM-{{MODULE_ABBR}}-{{NUMBER}}
name: "code-dedup-engine"
description: ""
allowed-tools: [Read, Grep, Glob, Edit, Write, Bash]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-06
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
---

# Domain Skill: code-dedup-engine

## CRITICAL Rules

### Core Operations
### 3.14 原子性修复——中断操作的崩溃恢复（v0.7.0 终极审视 #3）

**发现**：当前 auto_fixer 的描述是"提取→替换→验证→回滚失败"。外部审计师立刻发现一个致命漏洞：**如果进程在"提取"和"替换"之间崩溃了（断电/OOM/crash），代码库会处于不一致状态**——shared 中有新函数但 caller 没更新，或 caller 更新了 import 但 shared 没创建函数。

**WAL 式 fix_plan + 原子性提交**：

```
1. PREFLIGHT（干运行）：
   → 生成 fix_plan.yaml（所有要创建/修改/删除的文件及 diff）
   → 验证 fix_plan 语义完整性（所有 import 可解析 + 无循环依赖 + 所有引用可追溯）
   → 计算 plan_hash = SHA256(fix_plan)

2. CHECKPOINT（快照）：
   → 备份所有被影响的文件的原始内容到 fix_checkpoint_{plan_hash}.tar.gz
   → 备份所有被影响的文件的 SHA256 列表到 fix_manifest_{plan_hash}.json

3. APPLY（顺序执行）：
   → 按 fix_plan 中的依赖顺序依次执行文件修改
   → 每个文件修改后立即验证其 SHA256 与 plan 中的 expected_sha256 一致
   → 任何步骤 SHA256 不匹配 → ABORT → 跳转到 RECOVER

4. RECOVER（崩溃恢复）：
   → 引擎下次启动时扫描 fix_checkpoint_*.tar.gz 残留文件
   → 发现未完成的 fix_plan（checkpoint 存在但 completion_marker 不存在）
   → 自动从 checkpoint tar.gz 恢复所有原始文件
   → 写入 Session Log："检测到未完成的修复操作 DUP-xxx，已自动恢复代码库到修复前状态"
```

```yaml

### Unique Constraints
### 1.3 项目运维约束

本引擎运行在以下硬约束下：

| 约束 | 值 | 对设计的冲击 |
|------|-----|------------|
| 开发模式 | 100% AI 施工（Vibe Coding） | 重复会持续产生——不能只靠一次清理 |
| 运维模式 | 1人 + AI 维护 | 误报成本极高——人的时间是瓶颈 |
| 施工频率 | 高频（每天多个 session） | 增量扫描是刚需，全量扫描不可持续 |
| 上下文记忆 | AI 每次 session 零记忆 | 生成时预防比事后检测重要 10 倍 |
| **Session边界** | **AI session ≠ Git commit 边界——session内可能数小时无commit** | **Pre-commit 不是唯一防线——需要 session 内轻量拦截 + Session Log Wave 1 落地** |
| **依赖脆弱性** | **Tree-sitter Python grammar 每年随 Python 版本更新；MinHash/LSH 库可能弃坑** | **引擎依赖版本漂移 = CI 全红风险——需要锁定版本 + 自检 + 降级运行** |
| **增长非线性** | **项目 5000+ 行后 AI "创造性漂移"指数级恶化（"5000行魔咒"）；342 函数→2000 函数时数据结构退化风险** | **阈值必须规模感知——小项目(0-5000行)偏漏报/大项目(5000+)偏拦截；引擎需项目规模自检** |

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
