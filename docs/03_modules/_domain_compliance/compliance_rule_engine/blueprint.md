---
blueprint_id: MOD-CMP-012
module_name: compliance_rule_engine
domain: D_COMPLIANCE
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
priority: P0
blueprint_level: module
domain_id: D_COMPLIANCE
path: src/zephyr/compliance/compliance_rule_engine.py
granularity: file
---

# MOD-CMP-012 compliance_rule_engine 蓝图（§10.8.1.2 合规引擎）

> **module_id**: MOD-CMP-012 | **域**: D_COMPLIANCE | **优先级**: P0
> **来源**: CAND-CMP-002（B5-07849，AUD-DRAFT-001-DIGEST P0 波 W2d）
> 代码：`src/zephyr/compliance/compliance_rule_engine.py`

## 0. 定位

合规引擎（对标 OPA：DSL 规则解析 + 版本化；SEC 15c3-5 盘前自查门禁）：
**DSL 规则解析器** + **规则版本管理器**（不可变历史 + 当前活跃指针）+
**实时评估器**（Pre-Trade 同步调用，Hard Block 拒单 / Soft Warn 转人工 /
Warning 放行）+ **盘后批量审计器**。命中落 compliance_log（MOD-CMP-010，
经 hit_sink 回调接线）并 T+1 归档（归档委托既有链路）。
执行前合规**自查型**（非报送型）；收编现有检测散件（trading_compliance_detector
MOD-CMP-007 / discipline 双 checker）为规则包——本引擎不重复实现其检测逻辑，
散件阈值语义以 DSL 规则包表达（`trading_compliance_rule_pack`）。

## 1. DSL 与处置

规则定义（dict DSL）：
`{rule_id, version, description, severity, condition}`；
severity ∈ `hard_block` / `soft_warn` / `warning`；
condition 为 `{field, op, value}`（op ∈ >,>=,<,<=,==,!=,in）或复合
`{all: [...]}` / `{any: [...]}`。解析期校验（InvalidComplianceRuleError）。

评估处置聚合：任一 hard_block 命中 → HARD_BLOCK（拒单）；否则任一 soft_warn
→ SOFT_WARN（转人工审批）；否则任一 warning → WARNING（放行+记录）；否则 PASS。
字段缺失等评估错误 → Fail-Closed：HARD_BLOCK + engine_error（检测引擎失效
拒发任何订单，对齐 MOD-CMP-007 不变量）。

## 2. 接口

```python
class ComplianceDisposition(str, Enum): PASS/WARNING/SOFT_WARN/HARD_BLOCK
@dataclass(frozen=True) ComplianceRule: rule_id/version/description/severity/condition
@dataclass(frozen=True) RuleHit / ComplianceVerdict(disposition/hits/engine_error)
class RuleDslParser: parse(definition: dict) -> ComplianceRule
class RuleVersionManager: register/activate/deactivate/active/history（不可变历史+活跃指针）
class ComplianceRuleEngine(manager=None, hit_sink=None):
    .load_rule_pack(pack: Iterable[dict]) / .evaluate_pre_trade(context) / .evaluate_batch(contexts) -> BatchAuditReport
def trading_compliance_rule_pack() -> tuple[dict, ...]  # 收编散件阈值 DSL 包
class InvalidComplianceRuleError(ZephyrBaseError)
```

## 3. 不变量

- 版本历史不可变（已注册版本拒绝重复写；active 指针显式切换，目标版本须已注册）。
- evaluate_pre_trade 同步纯判定（hit_sink 回调异常不阻断判定）。
- 评估错误 Fail-Closed 拒单；命中经 hit_sink 落 compliance_log 契约 dict。
- 规则 frozen；history 返回不可变 tuple。

## 4. 依赖

- MOD-CMP-010 compliance_log（设计边：命中留痕落点）
- MOD-CMP-007 trading_compliance_detector（设计边：散件阈值语义收编真源）
- MOD-CMP-002 discipline_prohibition_checker（设计边：散件收编面）

## 5. MVP 边界

- 与 pre_execution_checker（MOD-EX-024）及 C-004 风控引擎的 Pre-Trade 接线、
  compliance_log 真实写入与 T+1 归档、散件全量规则迁移留运行时装配批；
  本模块交付解析器+版本管理器+评估器+批量审计器+收编规则包样例。
