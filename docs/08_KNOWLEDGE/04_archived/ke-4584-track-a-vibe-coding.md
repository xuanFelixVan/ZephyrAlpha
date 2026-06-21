---
module_id: KE-4418------8-008
title: Track A：Vibe Coding 施工知识（8 类）
category: module_blueprint
---

# Track A：Vibe Coding 施工知识（8 类）

Track A：Vibe Coding 施工知识（8 类）

> 来源：Session Log / AGENTS.md / ADR / 门禁阻断 / pre-commit hooks。提取优先级：自动（无需 Owner 触发）。

| # | `category` | 含义 | 优先级 | `halflife_h` | 典型来源 | 示例 |
|:--:|-----------|------|:---:|:---:|---------|------|
| A1 | `coding_convention` | 编码约定 | HIGH | 2160h(90d) | AGENTS.md / pre-commit 规则 | "ruff 不用 pylint：快 10-100x + pyproject.toml 原生集成" |
| A2 | `architecture_decision` | 架构决策 | HIGH | 4320h(180d) | ADR / 蓝图 | "L01 层选 SQLite 而非 PostgreSQL：< 10万 KE 规模时 SQLite 足够，零运维成本" |
| A3 | `governance_rule` | 治理规则 | HIGH | 2160h(90d) | AGENTS.md / PS 标准 | "新 .py 文件必须在 scripts/governance/ 注册（§6.5 入库强制约定）" |
| A4 | `failure_pattern` | 失败模式 | HIGH | ∞(permanent) | Session Log 教训 / 门禁阻断 | "KE-001: 3587 个误报源于一个多余的反斜杠——扫描器先自检" |
| A5 | `tool_configuration` | 工具配置 | MID | 4320h(180d) | justfile / pyproject.toml / CI 配置 | "pytest 必须用 --strict-markers：所有 @pytest.mark.* 装饰器必须注册到 pyproject.toml" |
| A6 | `dependency_knowledge` | 依赖知识 | MID | 2160h(90d) | 踩坑 / 升级记录 | "pydantic v2 BaseSettings → model_config SettingsConfigDict 迁移注意事项" |
| A7 | `workflow_pattern` | 工作流模式 | MID | 2160h(90d) | Session Log / AGENTS.md | "Session 启动顺序：AGENTS.md → 最新 Session Log → 按 §8.2 加载领域规则" |
| A8 | `context_engineering` | 上下文工程 | MID | 4320h(180d) | 实践经验 | "Hot ≤ 400 行 / Warm 按域触发 / Cold 按需检索——context utilization ≤ 40% 性能最优" |
