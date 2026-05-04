---
module_id: MOD-INF-017
doc_type: blueprint
status: draft
layer: l01_infrastructure
version: 0.1.1
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: AI
date: "2026-05-03"
valid_from: "2026-05-03"
ttl: permanent
construction_progress: not_started
depends_on:
  - MOD-INF-005
  - MOD-INF-016
title: "代码去重引擎蓝图"
summary: "语义级代码重复检测引擎——检测词法不同但语义相同的函数/常量定义，消除 Vibe Coding AI 的'上下文失忆'导致的重复代码"
tags:
  - code-dedup
  - deduplication
  - ast-analysis
  - semantic-similarity
  - code-quality
  - infrastructure
priority: P2
---

# 代码去重引擎（Code Dedup Engine）蓝图

## §1 问题陈述

### 1.1 现象

Vibe Coding AI 的上下文记忆极短（AGENTS.md §5.1），每次新 session 不知道已有代码，导致：
- `_now_iso()` 在 9 个文件中重复定义（词法完全相同）
- `_default_now()` 在 5 个文件中重复定义（词法相同，命名不同）
- `REPO_ROOT` 在 7 个文件中独立计算（语义相同，写法不同）
- `_estimate_tokens()` 在 3 个文件中重复（词法微差——空字符串处理不一致）

### 1.2 当前工具的局限

| 工具 | 检测能力 | 盲区 |
|------|---------|------|
| `validate_script_quality.py` D-D-07 | 词法精确匹配（符号名 = _shared API 名） | ❌ 无法检测 `_now_iso` vs `now_iso`（命名不同） |
| `fix_shared_bypass.py` | 词法精确匹配 + 自动修复 | ❌ 同上 |
| Ruff F811 | 同一文件内重定义 | ❌ 无法跨文件检测 |
| Ruff/per-file-ignores | 导入风格 | ❌ 无法检测语义重复 |

**核心盲区**：词法不同但语义相同的重复定义——`_now_iso()` 和 `now_iso()` 和 `_default_now()` 功能完全相同，但名字不同，现有工具检测不到。

### 1.3 目标

构建**语义级代码重复检测引擎**，能识别：
1. 函数体结构相似度 > 阈值的重复函数
2. 常量值相同但名称不同的重复常量
3. 同一功能在不同文件中的"独立发明"

## §2 专业对标

| 机构 | 工具 | 方法 | 我们能学什么 |
|------|------|------|------------|
| Google | Kythe + Tricorder | 全局符号索引 + AST 结构匹配 | 符号索引是基础 |
| Meta | Glean + Pyre | 代码索引 + 类型推断 | 类型签名辅助匹配 |
| SonarQube | 内置重复检测 | Token 序列匹配 + 阈值 | Token 匹配比 AST 匹配更快 |
| JetBrains | IntelliJ 重复检测 | AST 子树哈希 | AST 哈希是精确方案 |
| 学术界 | CCFinder / Deckard | Token/AST 后缀树 + 向量聚类 | 向量聚类可扩展 |

## §3 技术方案

### 3.1 三阶段检测流水线

```
Stage 1: Token 级快速扫描（秒级）
  → 提取所有函数的 token 序列
  → 计算归一化 token 序列的 MinHash
  → LSH 近似去重：候选对集合

Stage 2: AST 级精确比对（分钟级）
  → 对候选对进行 AST 子树哈希
  → 结构相似度 > 0.8 → 标记为"疑似重复"

Stage 3: 语义级验证（可选，需 LLM）
  → 对 AST 相似但不确定的候选对
  → 用 LLM 判断"这两个函数是否做同一件事"
  → 输出：确认重复 / 非重复 / 需人工判断
```

### 3.2 检测维度

| 维度 | 检测方法 | 精确度 | 速度 |
|------|---------|:---:|:---:|
| **词法精确匹配** | 符号名 = 已知 SSoT 名 | ★★★★★ | ★★★★★ |
| **函数体 token 匹配** | MinHash + LSH | ★★★★ | ★★★★ |
| **AST 结构匹配** | 子树哈希 + 相似度 | ★★★★★ | ★★★ |
| **签名+返回值匹配** | 参数类型 + 返回类型 | ★★★ | ★★★★★ |
| **LLM 语义判断** | Prompt: "这两个函数是否等价？" | ★★★★ | ★ |

### 3.3 输出格式

```yaml
dedup_report:
  generated_at: "2026-05-03T..."
  scan_scope: "src/zephyr/"
  total_functions: 342
  duplicate_groups:
    - group_id: DUP-001
      similarity: 1.0
      members:
        - file: "orchestrator/state_synchronizer.py"
          function: "_now_iso"
          line: 45
        - file: "orchestrator/file_task_mapper.py"
          function: "_now_iso"
          line: 45
      recommendation: "提取到 zephyr.shared.time_utils.now_iso()"
      severity: high
    - group_id: DUP-002
      similarity: 0.85
      members:
        - file: "context_engine/context_injector.py"
          function: "_estimate_tokens"
          line: 49
        - file: "context_engine/prompt_registry.py"
          function: "_estimate_tokens"
          line: 76
      recommendation: "提取到 zephyr.shared.token_utils.estimate_tokens()"
      severity: medium
```

## §4 模块结构

```
src/zephyr/l01_infrastructure/code_dedup_engine/
├── __init__.py
├── scanner.py          # Stage 1: Token 级快速扫描
├── ast_comparator.py   # Stage 2: AST 级精确比对
├── semantic_verifier.py # Stage 3: LLM 语义验证（可选）
├── report.py           # 报告生成（YAML/JSON）
└── config.py           # 配置（阈值、排除目录等）

scripts/governance/d1_structure/
└── detect_code_duplicates.py   # CLI 入口（注册到 manifest）

tests/unit/
└── test_code_dedup_engine.py   # 单元测试
```

## §5 实施路线

| 阶段 | 内容 | 依赖 | 预估工作量 |
|------|------|------|:---:|
| **Phase 1** | Token 级扫描（MinHash + LSH） | 无 | 3 天 |
| **Phase 2** | AST 级精确比对 | Phase 1 | 3 天 |
| **Phase 3** | CLI 入口 + manifest 注册 | Phase 2 | 1 天 |
| **Phase 4** | LLM 语义验证（可选） | Phase 2 + LLM API | 2 天 |
| **Phase 5** | CI 集成 + Pre-commit Hook | Phase 3 | 1 天 |

## §6 风险评估

| 风险 | 概率 | 影响 | 缓解 |
|------|:---:|:---:|------|
| 误报率高（相似但非重复的函数被标记） | 中 | 中 | 可调阈值 + 人工确认环节 |
| LLM 语义判断不稳定 | 高 | 低 | Phase 4 可选，不依赖 LLM |
| 扫描速度慢（大型代码库） | 低 | 中 | MinHash LSH 是近似算法，O(n) 而非 O(n²) |
| 与现有 D-D-07 checker 功能重叠 | 低 | 低 | D-D-07 是词法级，本引擎是语义级，互补 |

## §7 成功标准

1. 能检测出 `_now_iso()` / `now_iso()` / `_default_now()` 三者功能相同（Phase 2 验证）
2. 误报率 < 20%（人工确认后）
3. 扫描 `src/zephyr/` 全量代码 < 30 秒（Phase 1 性能目标）
4. 报告格式与现有治理脚本一致（YAML + exit code）

## §8 与现有系统的关系

```
现有系统（词法级）           本引擎（语义级）
┌────────────────────┐     ┌────────────────────┐
│ validate_script_   │     │ code_dedup_engine/  │
│ quality.py D-D-07  │     │ scanner.py          │
│ (符号名精确匹配)    │     │ ast_comparator.py   │
│                    │     │ (函数体结构匹配)     │
│ fix_shared_bypass  │     │ report.py           │
│ .py (自动修复)      │     │ (候选重复报告)       │
└────────────────────┘     └────────────────────┘
       ↓ 互补而非替代 ↓
┌─────────────────────────────────────────────┐
│ 完整防线：词法精确 → 结构相似 → 语义等价     │
└─────────────────────────────────────────────┘
```

## §9 开放问题

1. **阈值如何确定？** AST 相似度 0.7 还是 0.8 算"重复"？需要用实际代码库调参
2. **是否需要 LLM？** Phase 1-2 不需要，Phase 4 可选。LLM 增加延迟和成本
3. **与 SonarQube 的关系？** 如果项目未来引入 SonarQube，本引擎的部分功能可能被替代
4. **增量扫描？** 当前设计是全量扫描，增量扫描需要 git diff 集成

## §11 施工指引

### 11.1 第一步

1. 创建 `src/zephyr/l01_infrastructure/code_dedup_engine/` 包
2. 实现 `scanner.py`：遍历 `src/zephyr/` 下所有 `.py` 文件，提取函数定义，计算 MinHash
3. 实现 `ast_comparator.py`：对 MinHash 候选对进行 AST 子树哈希比对
4. 编写 `test_code_dedup_engine.py`：用已知的重复函数（如 `_now_iso` / `now_iso`）作为测试用例

### 11.2 验收标准

- `detect_code_duplicates.py --warn-only` 能检测出至少 5 组已知重复
- 全量扫描 `src/zephyr/` < 30 秒
- 误报率 < 20%

---

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 代码去重引擎——蓝图已创建但尚无代码实现

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
