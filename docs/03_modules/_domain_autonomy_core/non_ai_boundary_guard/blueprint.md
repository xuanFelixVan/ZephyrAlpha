---
blueprint_id: MOD-AU-012
module_id: MOD-AU-012
module_name: non_ai_boundary_guard
domain: D_AUTONOMY_CORE
doc_type: blueprint
ttl: permanent
design_maturity: production
stability: evolving
safety_level: H
ai_autonomy: human_gated
version: "0.1.1"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_AUTONOMY_CORE
path: src/zephyr/autonomy_core/non_ai_boundary_guard.py
granularity: file
responsibility_domain: 
---

# MOD-AU-012 non_ai_boundary_guard 蓝图（Non-AI 边界守卫 / D-AUTONOMY-33）

> **module_id**: MOD-AU-012 | **域**: D_AUTONOMY_CORE | **优先级**: P1
> **来源**: B10-02362（AUD-DRAFT-001-DIGEST P1 波 W-P1-12，§30.5.2）
> 代码：`src/zephyr/autonomy_core/non_ai_boundary_guard.py`

## 0. 定位

AI/非AI**决策权重占比计量器** + 超限（默认 >30%）阻断信号：guardrails 思路的
门禁化实现，守护非AI（人工/确定性规则）决策权重不被 AI 决策稀释越界。
最小施工形态（TSV §30.5.2）：AI/非AI决策权重计量器 + 超过 30% 自动阻断
（信号），挂 autonomy_guard 动作面（装配批接线）。

查重分工（W-P1-12 探查结论，均不复制）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| a2a_check_gateway | MOD-INF-025 | 跨 Agent 通信三段检查（身份/能力/边界） | 不管决策占比 |
| per_agent_gate | MOD-AU-006 | 单 Agent 规则集（黑白名单/限额/时段） | 不管跨决策流占比 |
| autonomy_boundary_gate | MOD-AU-001 | 写操作三区运行时拦截 | 不管决策权重计量 |
| autonomy_level_registry | MOD-AU-005 | Agent 四级自治级别 | 不计量 |
| ai_agent_monitor | MOD-RK-14 | 行为异常风险分（涌现/轨迹/指纹） | 不管占比硬顶 |
| autonomy_guard | MOD-INF-039 | Owner 缺位分级自治降级 | 本模块计量结论的挂载动作面 |

不做什么：不直接阻断下单（仅产 `block_trigger` 信号，执行委托风控/执行闸）、
不写决策溯源库（`audit_sink` 委托 D_GOV_AUDIT，不 import 不复制）、不做
Agent 行为异常检测（MOD-RK-14 职责）。

## 1. 判定规则（确定性，纯函数）

`meter(decisions) -> BoundarySnapshot`：
- 窗口取尾部 `window_size`（默认 200）条；
- `ai_share = Σ AI 决策 weight / Σ 全部 weight`（total ≤ 0 视为 0）；
- 样本 < `min_samples`（默认 20）→ 观察期 ALLOW；
- `ai_share` 严格大于 `max_ai_share`（默认 0.30，§30.5.2 硬顶）→ BLOCK_NEW_AI；
- 其余 ALLOW。

`admit(record, window) -> BoundaryAction`：
- 记录 Fail-Closed 校验 → meter(window) →
  非AI 恒 ALLOW；AI 且快照 BLOCK_NEW_AI → BLOCK_NEW_AI；
- BLOCK 时 `block_trigger(snapshot, record)` 阻断信号（异常不阻断，
  `block_signaled` 如实记录）；
- 双审计：meter_snapshot（必）+ block_signal（BLOCK 时）。

## 2. 接口

```python
class DecisionOrigin(str, Enum): AI/NON_AI
class BoundaryVerdict(str, Enum): ALLOW/BLOCK_NEW_AI
@dataclass(frozen=True) DecisionRecord: decision_id/origin/weight
@dataclass(frozen=True) BoundaryThresholds: max_ai_share=0.30/window_size=200/min_samples=20
@dataclass(frozen=True) BoundarySnapshot: samples/total_weight/ai_weight/ai_share/verdict/reason
@dataclass(frozen=True) BoundaryAction: verdict/snapshot/block_signaled/audit_records
class NonAIBoundaryGuard(thresholds=None, block_trigger=None, audit_sink=None):
    .thresholds / .meter(decisions) / .admit(record, window)
class InvalidDecisionRecordError / InvalidBoundaryConfigError(ZephyrBaseError)
```

## 3. 不变量

- meter/admit 判定纯函数无 IO；记录非法（空 id / weight 非正或非有限 /
  origin 非 ai|non_ai）→ InvalidDecisionRecordError（Fail-Closed，脏输入
  不参与计量）；窗口内坏记录同样 Fail-Closed。
- 阈值非法（max_ai_share∉(0,1) / window_size<1 / min_samples∉[1,window]）
  → InvalidBoundaryConfigError。
- 非AI决策恒 ALLOW（守卫对象）；AI 占比严格大于硬顶且样本达标才阻断；
  阻断仅产信号不直接执行；回调/sink 异常不阻断判定；双审计记录。

## 4. 依赖

- MOD-INF-039 autonomy_guard（设计边：计量结论挂载其分级动作面）
- MOD-AU-006 per_agent_gate / MOD-AU-001 autonomy_boundary_gate（设计边：双层分工对齐）
- MOD-RK-14 ai_agent_monitor（设计边：行为异常面分工对齐）
- MOD-INF-020 gov_audit writer（设计边：决策溯源落账委托）

## 5. 测试

`tests/autonomy/test_non_ai_boundary_guard.py`（37 例）：计量（占比/加权/窗口
截断/空窗/样本不足/纯函数）/ 判定（超限 BLOCK / 恰界 ALLOW / 自定义阈值）/
admit（AI 阻断与放行 / 非AI 恒放行 / 信号回调）/ Fail-Closed（记录与配置）/
回调异常不阻断 / 双审计 / frozen。

---

## 6. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
