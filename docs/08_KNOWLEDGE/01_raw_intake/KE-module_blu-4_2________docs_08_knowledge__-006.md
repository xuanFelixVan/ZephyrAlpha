---
module_id: KE-module_blu-4_2________docs_08_knowledge__-006
title: 4.2 知识数据层（`docs/08_knowledge/`）——KE 物理文件
category: module_blueprint
---

# 4.2 知识数据层（`docs/08_knowledge/`）——KE 物理文件

4.2 知识数据层（`docs/08_knowledge/`）——KE 物理文件

```
docs/08_knowledge/
├── index.md                        # 知识库总索引（由 validate_ke_index.py 自动维护）
│
├── track_a_vibe_coding/            # Track A：Vibe Coding 施工知识（8 类，§3.8）
│   ├── coding_convention/          # A1：编码约定
│   │   └── KE-{NNN}-{slug}.md
│   ├── architecture_decision/      # A2：架构决策
│   │   └── KE-{NNN}-{slug}.md
│   ├── governance_rule/            # A3：治理规则
│   │   └── KE-{NNN}-{slug}.md
│   ├── failure_pattern/            # A4：失败模式
│   │   └── KE-{NNN}-{slug}.md
│   ├── tool_configuration/         # A5：工具配置
│   │   └── KE-{NNN}-{slug}.md
│   ├── dependency_knowledge/       # A6：依赖知识
│   │   └── KE-{NNN}-{slug}.md
│   ├── workflow_pattern/           # A7：工作流模式
│   │   └── KE-{NNN}-{slug}.md
│   └── context_engineering/        # A8：上下文工程
│       └── KE-{NNN}-{slug}.md
│
├── track_b_finance/                # Track B：金融领域知识（7 类，§3.8）
│   ├── strategy_logic/             # B1：策略逻辑
│   │   └── KE-{NNN}-{slug}.md
│   ├── factor_design/              # B2：因子设计
│   │   └── KE-{NNN}-{slug}.md
│   ├── risk_management/            # B3：风险管理
│   │   └── KE-{NNN}-{slug}.md
│   ├── data_quality/               # B4：数据质量
│   │   └── KE-{NNN}-{slug}.md
│   ├── market_microstructure/      # B5：市场微观结构
│   │   └── KE-{NNN}-{slug}.md
│   ├── compliance/                 # B6：合规知识
│   │   └── KE-{NNN}-{slug}.md
│   └── backtest_methodology/       # B7：回测方法论
│       └── KE-{NNN}-{slug}.md
│
├── ko/                             # KO（Knowledge Observation）碎片层（§3.10）
│   ├── observed/                   # OBSERVED 状态——等待积累
│   │   └── KO-{NNN}-{slug}.md
│   ├── promoting/                  # PROMOTING 状态——等待 Owner 确认
│   │   └── KO-{NNN}-{slug}.md
│   └── discarded/                  # DISCARDED 状态——90d 后自动清理
│       └── KO-{NNN}-{slug}.md
│
├── kb/                             # KB（Knowledge Base Rule）规则层（§3.11）
│   ├── active/                     # ACTIVE 状态——当前生效规则
│   │   └── KB-{NNN}-{rule_name}.yaml
│   ├── superseded/                 # SUPERSEDED 状态——已被取代
│   │   └── KB-{NNN}-{rule_name}.yaml
│   └── retired/                    # DEPRECATED 状态——已废弃
│       └── KB-{NNN}-{rule_name}.yaml
│
└── _archive/                       # 归档层——REJECTED / ARCHIVED / SUPERSEDED 终态 KE
    └── KE-{NNN}-{slug}.md
```

> **为什么目录结构不是按 status 分层而是按 category 分层**：
> - category 是**静态属性**（一条 KE 的 category 不会变）→ 目录天然稳定
> - status 是**动态属性**（一条 KE 会从 DRAFT→VERIFIED→DEPRECATED）→ 会导致文件在不同目录间频繁移动
> - 对标：K8s CRD 按 kind 分组而非按 phase 分组 / Git 按内容类型分目录而非按"是否 merge"分目录
> - 例外：KO 和 KB 按 status 分目录——因为它们的状态变化频率低（OBSERVED→PROMOTING 是批量操作，非逐条移动）

##### 文件命名规范

| 实体 | 命名模式 | 示例 | 编号规则 |
|------|---------|------|---------|
| KE | `KE-{NNN}-{slug}.md` | `KE-042-ruff-over-pylint.md` | NNN = 3位全局递增编号（§3.2.1），`slug` = 标题的 kebab-case 缩写（≤40字符） |
| KO | `KO-{NNN}-{slug}.md` | `KO-015-ruff-vs-pylint-speed.md` | NNN = 3位独立递增编号（KE 和 KO 编号池独立，不共享） |
| KB | `KB-{NNN}-{rule_name}.yaml` | `KB-001-python-linter-must-be-ruff.yaml` | NNN = 3位独立递增编号，`rule_name` = snake_case（≤50字符
