---
blueprint_id: MOD-PF-014
module_id: MOD-PF-014
module_name: rebalance_cost_analyzer
domain: D_PF_CORE
doc_type: blueprint
ttl: permanent
design_maturity: production
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.1.1"
created: 2026-08-26
last_updated: 2026-08-26
owner: ZephyrAlpha-Owner
priority: P2
blueprint_level: module
domain_id: D_PF_CORE
path: src/zephyr/pf_core/core/rebalance_cost_analyzer.py
granularity: file
responsibility_domain: 
---

# MOD-PF-014 rebalance_cost_analyzer 蓝图（再平衡成本分析器）

> **module_id**: MOD-PF-014 | **域**: D_PF_CORE | **优先级**: P2
> **来源**: B10-02079（AUD-DRAFT-001-DIGEST P2 波 P2-W09，CAND-PF004-007，A1 PC-10）
> 代码：`src/zephyr/pf_core/core/rebalance_cost_analyzer.py`

## 0. 定位

调仓成本四拆解：显性（佣金/印花税）+隐性（冲击/价差）+税收（股息税/资本利得语义注入税率表）+机会成本（调仓期间偏离基准收益）+拆解报告（占比排序）+成本异常告警阈值。Decimal-only。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/pf_core/test_rebalance_cost_analyzer.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。

---

## 4. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 4.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/research/pf_core/test_rebalance_cost_analyzer.py` | ✅ 已实现 | |

### 4.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §4（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
