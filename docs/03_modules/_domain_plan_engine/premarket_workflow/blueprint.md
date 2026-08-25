---
blueprint_id: MOD-PLAN-021
module_name: premarket_workflow
domain: D_PLAN
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_PLAN
path: src/zephyr/plan_engine/premarket_workflow.py
granularity: file
---

# MOD-PLAN-021 premarket_workflow 蓝图（D-TRADING-15 A股盘前标准化工作流）

> **module_id**: MOD-PLAN-021 | **域**: D_PLAN | **优先级**: P1
> **来源**: B10-02213（AUD-DRAFT-001-DIGEST P1 波 W-P1-19，CAND-PLAN-015，D-TRADING-15 §30.2.5）
> 代码：`src/zephyr/plan_engine/premarket_workflow.py`

## 0. 定位

A股盘前标准化工作流：08:00-09:15 三段式 DAG 挂 trading work_dag + 进度追踪
落 state_store。TSV 裁定注记："盘前SOP分钟级编排单人项目用work_dag即可承载，
无需独立BPM引擎"。

查重分工（W-P1-19 铁律④探查——**检查器 vs 工作流编排**，均不复制）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| premarket_checker | MOD-EX-063 | 盘前**就绪核查器**（限额/纪律/数据完整性/系统就绪四道关） | 本工作流的确认段**其中一道工序**，编排归本模块，核查归它 |
| pre_execution_checker | MOD-EX-024 | 逐单执行前四级硬拦（production） | 交易时段逐单面，与盘前 SOP 编排正交 |
| premarket_constraint_loader | MOD-PLAN-002 | 盘前约束加载（边界+竞价匹配） | 分析段工序之一，不编排 |
| llm_premarket_analysis | MOD-PLAN-007 | LLM 盘前分析 | 分析段工序之一，不编排 |
| work_dag | MOD-INF-035 | WorkDAG/WorkItem 数据模型 | 本模块**复用**其模型产 DAG 定义，不重造调度器 |
| boot_hooks | MOD-INF-035 | 启动订阅链 | 运行时装配面（本模块进度追踪落 state_store 经回调委托） |

与 W-P1-22 盘前检查器候选（B1-00382/B14-04680）区分：彼为**检查器族**（将被
归并到 MOD-EX-063 族），本件为**工作流编排**；CAND-PLAN-017（B14-04681，P2，
"A股盘前标准化工作流引擎"）与本件近重复，注明归并指向本件 canonical。

不做什么：不做就绪核查判定（MOD-EX-063）、不做真实调度执行（运行时
conductor 装配面）、不直接写 state_store（state_sink 回调委托）。

## 1. 规则（确定性，纯函数/纯声明）

- **三段式 SOP**（分钟级排程，全部在 08:00-09:15 窗口内）：
  - 段1 数据就绪（08:00-08:30）：data_sync → quality_gate（mandatory）。
  - 段2 分析（08:30-09:00）：overnight_review → scenario_plan →
    llm_premarket（llm 工序非 mandatory，失败降级不阻断）。
  - 段3 确认（09:00-09:15）：premarket_check（mandatory，MOD-EX-063）→
    readiness_confirm（mandatory，人工在环确认点）。
- **DAG 产出**：build_premarket_dag(trading_date) → trading.work_dag.WorkDAG
  （节点=工序 capability_id，边=依赖 success 条件），复用模型零重造。
- **进度追踪**：PremarketWorkflowTracker 状态机 PENDING→RUNNING→DONE/
  FAILED/SKIPPED（非法迁移 Fail-Closed）；mandatory 工序 FAILED →
  blocked=True + takeover_point=该工序（人工接管点）；ready=全部 mandatory
  DONE 且无 blocked；进度快照经 state_sink 回调落 state_store（装配批接线，
  sink 异常不阻断如实记录）。
- Fail-Closed：排程越出 08:00-09:15/段序颠倒/依赖不存在/mandatory 工序缺失
  （premarket_check 与 readiness_confirm 必备）→ PremarketWorkflowError。

## 2. 接口

```python
@dataclass(frozen=True)
class StageSpec: stage_id / name / phase / scheduled_at / deadline / capability_id / mandatory / depends_on
def default_stages() -> tuple[StageSpec, ...]
def build_premarket_dag(trading_date, stages=None) -> WorkDAG
class PremarketWorkflowTracker: mark_running/mark_done/mark_failed/mark_skipped / progress() / ready / blocked
class PremarketWorkflowError(Exception)  # error_code 待登记
```

## 3. 依赖前置

- MOD-INF-035 work_dag（WorkDAG 模型复用，node 10620315）。
- MOD-INF-016 state_store（进度追踪落库契约，state_sink 回调，node 10619858）。
- MOD-EX-063 premarket_checker（确认段核查工序，node 10617649）。
- MOD-INF-035 boot_hooks（启动订阅链装配面对齐，node 10620280）。

## 4. 验收标准

- 单测全绿（默认 SOP 三段式排程窗口/依赖拓扑/DAG 模型字段/进度状态机非法
  迁移拒绝/mandatory 失败阻断与人工接管点/ready 口径/state_sink 回调容错/
  畸形输入 Fail-Closed）；tests/plan_engine 零回归。
