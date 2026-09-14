---
ttl: permanent
doc_type: architecture_view
status: executed
version: "1.0.0"
date: 2026-09-15
---

# 裁定书：battle_map 边/步冻结数据"回填 or 降级"（Owner 令 2026-09-15）

> 裁定人=夜班 AI（Owner 全权授权，架构师第一性原理框架）｜状态=**已执行完毕**

## 一、分析过程

**1. 事实核查（推翻了"冻结=坏账"的预判）**

| 证据 | 发现 |
|---|---|
| 定位书（panorama/battle_map_positioning.md V0.7） | battle_map=第五全景图，"钱怎么赚"装配真源；07_ 目录 MD=其派生人类视图（真源在 PG 三表） |
| 消费者 | dashboard api_server 读 steps（BM-READER）+ex_core 执行报告/审计日志读 battle_map |
| 派生视图 | 07_trading_decision_architecture/battle_map/ 26 个 MD **2026-09-14 刚重新生成** |
| edges/steps 冻结 34 天 | steps=340/edges=114 是**流程拓扑**，业务流程未变则拓扑不变——静态是正常态不是腐烂 |
| anchors 493→持续写入 | 锚点=模块挂载层，随代码演进变化，且被 BUSINESS-REGISTRY 门禁强制（增量已封堵） |

**2. 第一性原理**：battle_map 数据分两层——拓扑层（steps/edges，慢变量）与挂载层（anchors，快变量）。"冻结"只发生在慢变量层=健康；真正的债是老审计（#231 期）记的"504 孤儿模块欠账"=挂载层覆盖率，且当时无门禁、现在有。

**3. 专业实践对照**：Backstage 服务目录治理以**覆盖率度量**为核心工具而非人工补数据；OpenLineage 数据血缘治理以 completeness 审计驱动回填；GitHub dependency graph 同理（度量自动化、补录按需）。共同点：**度量机械化、补录走正门工具、不养人工台账**。

**4. 100% AI 开发约束**：一次性人工回填不可持续（未来会话无法信任也无法维护）；可复用的盘点工具+正门写入（apply_battle_map）才是可持续形态。

## 二、裁定结果

1. **edges/steps 不降级**：活真源（有消费者+派生视图+拓扑稳定），降级=自废第五全景图。
2. **回填不搞大水漫灌**：宇宙口径收窄到 BUSINESS-REGISTRY 门禁同源的 82 个业务模块（非 5265 全节点），先度量后补录。
3. **度量机械化**：新建 `scripts/battle_map_coverage_audit.py`（MOD-SCRIPT-battle_map_coverage_audit，REGISTRY_SPECS 同源防双真源，只读盘点，正门回填仍走 apply_battle_map）。

## 三、执行记录（2026-09-15 夜班）

1. 实测孤儿：**23 个（覆盖率 71.95%）**，分布于策略库×7/图形形态×2/数据资产×7/实验库×3 等。
2. 逐个挂载回填 23 锚（全部 target_role=supplement 保守处理，status_snapshot=generated 机械口径）：
   - BM-BT-01 回测引擎与撮合 ← MOD-BT-033/041/042/054/068/093、MOD-TDMVAL-001、MOD-REGIME_VAL-002
   - BM-SIM-01 市场仿真器 ← MOD-BT-084/091（sim 账本/日刊）
   - BM-SEL-01 数据接入 ← MOD-MKT-DATA；BM-SEL-02 因子与信号 ← MOD-L02-020、MOD-SIG-145、MOD-REGIME-002
   - BM-RES-01 研究数据 ← MOD-INT-AISA、MOD-INT-IMPACT-STREAM、MOD-INT-NEWS-CHAIN
   - BM-RC-01 风控限额 ← MOD-RISK-001、MOD-RK-23；BM-RC-11 风险数据管道 ← MOD-GOV-046（告警）
   - BM-BUY-09 信息合规 ← MOD-CMP-011；BM-MT-01 训练流水线 ← MOD-ML-DENSITY；BM-REC-01 运营清算 ← MOD-OBS-001
3. 复测：**孤儿 0，覆盖率 100%（82/82）**，锚点 493→516。
4. 派生视图重生成（26 文件，与库内已提交版本零 diff=一致收敛）。
5. 巡检配方：`python scripts/battle_map_coverage_audit.py`（建议纳入季度退役审计批次随跑）。

## 四、遗留

无。回填为正门操作+盘点件可复跑，后续漂移由 BUSINESS-REGISTRY 门禁（增量）+本盘点件（存量复测）双网兜底。
