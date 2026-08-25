---
blueprint_id: MOD-SIG-088
module_name: capital_behavior_orchestrator
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
---

# MOD-SIG-088 capital_behavior_orchestrator 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B1-00152（C-011 资金行为分析，裁定=做 P1）+
> 候选注册表 CAND-TESTB-003。代码：`src/zephyr/signal_ashare/capital_behavior_orchestrator.py`

## 0. 定位

主力行为分析单点已在（MOD-SIG-021），七类画像+六阶段识别+动态推演+自迭代修正
未成体系（深挖裁定理由）。本模块是**资金行为分析收口**：

- **七类主力画像**：北向/公募/私募/游资/量化/散户/产业资本（封闭枚举），
  每类观测（净流入/参与占比/置信度）→ 画像（方向+强度）。
- **六阶段识别复用**：直接复用 MOD-SIG-021 `BehaviorPhase`（建仓→洗盘→试盘→
  再洗盘→拉升→出货），不重写识别算法；当前阶段由调用方注入。
- **推演状态机**：沿六阶段主链按合力方向推演下一阶段（不可跳跃）。
- **预测-复盘自迭代修正**：预测方向 vs 实际方向误差按类 EMA 校准偏置，
  后续画像打分自动修正（偏置限幅 [-0.5,0.5]，可审计）。
- **合力方向输出**：CapitalConsensus（方向/强度/画像明细/当前+推演阶段），
  供 C-014 大盘预测（后续波次）消费。

与既有件边界：
- MOD-SIG-021 institutional_behavior_analyzer：分时价量行为学 6 阶段识别件，
  本模块**复用其阶段枚举**、消费其识别结果（注入），不重复实现。
- MOD-SIG-022 capital_flow_pattern_analyzer / MOD-SIG-057 lhb_premium_analyzer：
  资金流/龙虎榜单点件，为本模块观测数据的候选生产方（注入契约，不 import）。

## 1. 接口

```python
class CapitalClass(str, Enum)        # 7 类封闭集
class ForceDirection(str, Enum)      # 做多/做空/中性
@dataclass(frozen=True) class CapitalObservation
@dataclass(frozen=True) class CapitalBehaviorConfig
@dataclass(frozen=True) class CapitalProfile
@dataclass(frozen=True) class CapitalConsensus
class CapitalBehaviorOrchestrator:
    def analyze(self, symbol, observations, *, phase=BehaviorPhase.UNKNOWN) -> CapitalConsensus
    def review(self, consensus, actual_direction) -> CalibrationReport   # 预测-复盘自迭代
```

## 2. 纪律

- 七类枚举封闭；观测占比∈[0,1]、置信度∈[0,1]，越界 ValueError（fail-closed）。
- 合力强度=Σ(带符号净流入×置信度×(1+类偏置))/Σ(|净流入|×置信度)，空观测→NEUTRAL。
- 校准偏置限幅 ±0.5；复盘仅调整偏置不改历史记录。
- frozen dataclass、to_dict JSON 可序列化；纯内存，不直连 DB。
