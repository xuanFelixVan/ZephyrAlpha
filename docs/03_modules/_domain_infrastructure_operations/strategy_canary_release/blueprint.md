---
blueprint_id: MOD-INF-072
module_name: strategy_canary_release
domain: D_INFRA_OPS
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
domain_id: D_INFRA_OPS
path: src/zephyr/infrastructure/strategy_canary_release.py
granularity: file
---

# MOD-INF-072 strategy_canary_release 蓝图（D-SIGNAL-140 策略灰度发布）

> **module_id**: MOD-INF-072 | **域**: D_INFRA_OPS | **优先级**: P1
> **来源**: B14-04678（AUD-DRAFT-001-DIGEST P1 波 W-P1-24，CAND-INFRAOPS-002，A9运维架构 §8.3.6）
> 代码：`src/zephyr/infra_ops/strategy_canary_release.py`

## 0. 定位

**策略级**灰度发布（防 Knight Capital 类事故关键件）：config 驱动
1-5% → 25-50% → 100% 三阶段放量阶梯 + 6 维验证（功能 / 性能 / 错误率 /
资源 / 风控完整性 / 数据一致性）+ 失败 <10s 配置回滚 + **交易时段禁启动**
（HC-05）。

查重分工（W-P1-24 铁律④探查）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| gray_release_shadow_deployer | MOD-ML-004 | ML 模型**影子部署**（只观测不生效，B-009 红线，设计态） | 本件=**策略级真实流量分阶段灰度**状态机；影子部署管模型观测面，不管策略放量 |
| canary_manager | MOD-INF-039 | 通用金丝雀权重 setter（weight/rollback 阈值桩） | 无策略语义/无阶段/无交易时段门禁；本件不扩展它（D_ORCHESTRATOR 域桩件） |
| grayscale_rollout | MOD-L02-015 | **因子级**灰度 10%→30%→100%（ABS001 门禁推进） | 因子治理域放量，非策略发布；本件=策略级三阶段+6 维验证+时段冻结 |
| lifecycle_state_machine | MOD-L02-013 | 因子生命周期 FSM | 因子状态机，非策略发布状态机 |

TSV 裁定原文："灰度部署器为设计态，通用 canary 管理器未接策略域；策略级
灰度与交易时段冻结联动未落地"——施工形态=1 个新模块（新包 infra_ops）。

## 1. 规则（确定性，纯内存状态机；配置 DI 注入）

- **三阶段阶梯**（默认，config/canary.yaml 语义由装配批加载后 from_dict
  注入）：stage1 ratio∈[0.01,0.05] → stage2∈[0.25,0.50] → stage3=1.0。
- **启动门禁（HC-05）**：`start(..., is_trading_session=True)` → Fail-Closed
  拒绝（StrategyCanaryError），交易时段禁启动；非交易时段方可启动并进入
  stage1（ratio 取阶段下界）。
- **6 维验证**：`advance(metrics)` 要求 6 维全部达标（thresholds 配置注入；
  指标缺失维=不达标 Fail-Closed）→ 推进下一阶段；任一维不达标 →
  **自动回滚**（rollback）。
- **回滚**：ratio 立归 0、状态 ROLLED_BACK、留痕 reason+elapsed；
  配置回滚语义=<10s（rollback_timeout_sec=10 声明并校验回滚动作本身
  无IO即时完成；真实流量切配由装配批按新 ratio 即时生效）。
- **状态机**：IDLE → RUNNING(stage_i) →（推进）→ RUNNING(stage_i+1) →
  COMPLETED（stage3 验证通过）；RUNNING →（失败/手动）→ ROLLED_BACK；
  ROLLED_BACK 可重新 start（先校验时段）。
- **ratio 只读输出**：本件只产目标 ratio 与状态，不直接切流量（执行归
  装配批/策略运行面）。
- Fail-Closed：重复 start / 未 start 推进 / 阶段配置非法（区间空、重叠、
  越界 (0,1]）/ metrics 维度缺失 → StrategyCanaryError。

## 2. 接口

```python
class ValidationDimension(str, Enum): FUNCTIONALITY/PERFORMANCE/ERROR_RATE/RESOURCE/RISK_COMPLETENESS/DATA_CONSISTENCY
class CanaryStatus(str, Enum): IDLE/RUNNING/COMPLETED/ROLLED_BACK
@dataclass(frozen=True) class CanaryStage: name/min_ratio/max_ratio
@dataclass(frozen=True) class StrategyCanaryConfig: strategy_id/stages/validation_thresholds(dict[dim,float])/rollback_timeout_sec=10/freeze_during_trading=True
@dataclass(frozen=True) class CanaryReleaseState: strategy_id/status/stage_index/current_ratio/history(tuple)

DEFAULT_STAGES = (stage1[0.01,0.05], stage2[0.25,0.50], stage3[1.0,1.0])
config_from_dict(strategy_id, raw: dict) -> StrategyCanaryConfig

class StrategyCanaryRelease:
    start(config, now_utc, is_trading_session) -> CanaryReleaseState
    advance(strategy_id, metrics: dict[ValidationDimension,float], now_utc) -> CanaryReleaseState
    rollback(strategy_id, reason, now_utc) -> CanaryReleaseState
    status(strategy_id) -> CanaryReleaseState
class StrategyCanaryError(Exception): 占位 ZA-INF-UNREGISTERED-STRATEGY-CANARY
```

## 3. 错误契约

- `StrategyCanaryError`（未登记错误码-申请中，占位
  ZA-INF-UNREGISTERED-STRATEGY-CANARY，建议号段见 W-P1-24 fragment）

## 4. 测试

- `tests/infra_ops/test_strategy_canary_release.py`
- 覆盖：三阶段推进链、6 维验证缺维/不达标自动回滚、交易时段禁启动
  （HC-05）、回滚 ratio 归零留痕、ROLLED_BACK 重启、配置非法 Fail-Closed

## 5. 依赖

- 标准库 only（dataclasses/datetime/enum）；交易时段真源由调用方注入
  （is_trading_session 布尔，装配批接 trading_calendar）
- 下游（运行时装配，不 import）：D_ASHARE_SIGNAL 策略运行面按 ratio 切流 /
  D_RISK 风控完整性指标供给 / config/canary.yaml 加载器
