---
blueprint_id: MOD-ML-016
module_id: MOD-ML-016
module_name: decision_tree_decision_architecture
domain: D_ML_TRAIN
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
domain_id: D_ML_TRAIN
path: src/zephyr/ml_train/decision_tree_decision_architecture.py
granularity: file
responsibility_domain: 
---

# MOD-ML-016 decision_tree_decision_architecture 蓝图（决策树交易决策架构）

> **module_id**: MOD-ML-016 | **域**: D_ML_TRAIN | **优先级**: P2
> **来源**: B10-01480（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLT-022，A1 模块46）
> 代码：`src/zephyr/ml_train/decision_tree_decision_architecture.py`

## 0. 定位

GBM决策树学习历史决策日志（特征=模块输出向量/标签=事后收益符号，注入gbm_trainer，未装库降级规则 stump）+SHAP解释（注入shap_explainer降级特征重要性兜底）+关键节点人工干预接口（决策路径+干预钩子注入）+RL(PPO)仅离线评估语义不施工。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/ml_train/test_decision_tree_decision_architecture.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。

---

## 4. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 4.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/research/research/ml_train/test_decision_tree_decision_architecture.py` | ✅ 已实现 | |

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
