---
blueprint_id: MOD-AU-013
module_name: ai_ops_autonomy_card
domain: D_AUTONOMY_CORE
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: H
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_AUTONOMY_CORE
path: src/zephyr/autonomy_core/ai_ops_autonomy_card.py
granularity: file
---

# MOD-AU-013 ai_ops_autonomy_card 蓝图（C-008 AI 自治运维能力卡片，A1§12.2 迁移）

> **module_id**: MOD-AU-013 | **域**: D_AUTONOMY_CORE | **优先级**: P1
> **来源**: B14-04565（AUD-DRAFT-001-DIGEST P1 波 W-P1-12，A9 §3.5）
> 代码：`src/zephyr/autonomy_core/ai_ops_autonomy_card.py`

## 0. 定位

自监控→自诊断→自修复→自保障（Learn）四阶段闭环的**运维自治判定核心**：
7 类检测源事件 → 四路诊断（规则/关联/LLM/因果）→ AUT-001~008 修复策略库
（A-L1~L4 分级）→ TNR 可撤销修复（restore 快照 + 恶化自动回滚）→ 故障模式
库 Learn。边界：C-008=运行时保障（不崩溃） vs C-023=性能优化（跑更快）。

查重分工（W-P1-12 探查结论，均不复制）：

| 既有件 | module_id | 职责 | 与本卡边界 |
|---|---|---|---|
| capability_card | MOD-INF-035 | 能力卡数据模型（pydantic schema 族） | 本卡为业务实例判定核心 |
| autonomy_level_registry | MOD-AU-005 | Agent 角色四级自治（L0~L3） | 本卡 A-L1~L4 为运维动作分级 |
| self_diagnosis | MOD-FEEDBACK_LOOP | 策略/信号层自诊断 | 诊断路委托面 |
| auto_fix_engine | infrastructure | 开发侧代码自愈 | 不管交易运行时 |
| process_supervisor | MOD-INF-066 | 进程守护执行体 | 修复执行委托（repair_sink） |
| health_monitor | trading/MOD-INF-035 | 健康监控散件 | 检测源之一 |

不做什么：不直接执行修复/回滚（仅产信号，执行委托存量）、不接检测源管线
（装配批）、不写运维审计库（audit_sink 委托 D_GOV_AUDIT）、不做性能优化
（C-023 职责）。

## 1. 判定阶梯（确定性，纯函数）

`evaluate(incident) -> RemediateAction`：
1. 事件 Fail-Closed 校验（id/source/route/severity/action_tag）；
2. **禁区硬编码**：action_tag 命中 B-014/015/016 且交易时段 → ESCALATE_HUMAN
   （卡级别抬升不可绕过）；
3. 策略无匹配 → OBSERVE + learn_candidate 审计（故障模式库 Learn）；
4. 策略不可逆（AUT-008）→ ESCALATE_HUMAN（TNR 可撤销修复不满足）；
5. 无 restore 快照引用 → ESCALATE_HUMAN（TNR 无法保证）；
6. 策略分级 > 卡分级 → ESCALATE_HUMAN；
7. 其余 EXECUTE_REPAIR + repair_sink 信号。

`evaluate_post_repair(incident, health_delta)`：delta<0（恶化）→ ROLLBACK +
rollback_trigger 信号（TNR 自动回滚）；否则 OBSERVE 巩固观察。

## 2. 接口

```python
class DetectorSource(str, Enum): process_health/metric_anomaly/log_error/dlq_backlog/latency_slo/data_staleness/resource_exhaustion  # 7类
class DiagnosisRoute(str, Enum): rule/correlation/llm/causal  # 四路
class AutonomyGrade(IntEnum): A_L1=1..A_L4=4
class ForbiddenZone(str, Enum): B_014/B_015/B_016
FORBIDDEN_ZONES: dict[ForbiddenZone, tuple[str,...]]  # 禁区→动作标签（硬编码）
@dataclass(frozen=True) RepairStrategy: strategy_id/name/grade/reversible/action_tags
REPAIR_STRATEGIES: tuple  # AUT-001~008
CAPABILITY_CARD: dict  # C-008 卡声明（四阶段/检测源/诊断路/策略库/禁区/TNR/边界）
@dataclass(frozen=True) OpsIncident: incident_id/source/action_tag/severity/in_trading_session/snapshot_ref/diagnosis_route
@dataclass(frozen=True) RemediateAction: verdict/strategy_id/reason/restore_snapshot_ref/rollback_signaled/audit_records
class AiOpsAutonomyCard(grade=A_L2, repair_sink=None, rollback_trigger=None, audit_sink=None):
    .grade/.card/.evaluate(incident)/.evaluate_post_repair(incident, health_delta)
class InvalidOpsIncidentError / InvalidAutonomyCardConfigError(ZephyrBaseError)
```

## 3. 不变量

- evaluate/evaluate_post_repair 判定纯函数无 IO；事件非法（空 id / 空
  action_tag / source/route 越集 / severity 非 P1|P2|P3）→
  InvalidOpsIncidentError（Fail-Closed）；grade 非 A_L1~L4 →
  InvalidAutonomyCardConfigError。
- B-014/015/016 禁区硬编码（FORBIDDEN_ZONES 常量，不可配置）：交易时段命中
  必 ESCALATE_HUMAN，A_L4 也不可绕过。
- TNR：不可逆策略或无 restore 快照必人工；修复后健康度恶化自动 ROLLBACK
  信号；修复/回滚仅产信号不直接执行；回调/sink 异常不阻断判定；
  remediate_decision + 处置（escalate/repair_execute/rollback/learn_candidate）
  双审计记录。

## 4. 依赖

- MOD-INF-035 capability_card（设计边：卡模型族对齐）
- MOD-AU-005 autonomy_level_registry（设计边：自治分级语义对齐）
- MOD-FEEDBACK_LOOP self_diagnosis（设计边：诊断路委托面）
- MOD-INF-066 process_supervisor（设计边：修复执行委托）
- MOD-INF-035 health_monitor（设计边：自监控检测源对齐）

## 5. 测试

`tests/autonomy/test_ai_ops_autonomy_card.py`（46 例）：卡声明（四阶段/7源/四路/
8策略/禁区/边界）/ 策略库（编号/分级/可逆性/标签唯一）/ 禁区（三区交易时段
人工/非时段放行/L4 不可绕过）/ 判定（执行/未知 OBSERVE+Learn/超分级人工/抬级
放行/不可逆人工/无快照人工/sink 委托/纯函数）/ 修复后（恶化 ROLLBACK/改善
OBSERVE）/ Fail-Closed / 回调异常不阻断 / 审计与 frozen。
