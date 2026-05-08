---
module_id: KE-module_blu-2_225_counterfactual_reasoning-000
title: 2.225 Counterfactual Reasoning Engine - counterfactual_engine.py (🆕 v0.21.0 - 盲点
category: module_blueprint
---

# 2.225 Counterfactual Reasoning Engine - counterfactual_engine.py (🆕 v0.21.0 - 盲点

2.225 Counterfactual Reasoning Engine - counterfactual_engine.py (🆕 v0.21.0 - 盲点274 — "如果我没做这个修复会怎样"的反事实学习)

**致命问题**：FLE从成功修复中学到"这个action有效"，但不知道真是action有效还是问题自愈了。反事实推理(counterfactual reasoning)问："如果我没执行这个REPAIR→系统会怎样？" 这是因果推断的金标准。金融系统中，很多"异常"是短暂的市场噪音→5分钟后自恢复→FLE以为是自己的REPAIR修好了→强化错误的action→下次相同噪音→再次做无效REPAIR。
**对标**：Judea Pearl Causal Inference + Google Causal Impact R Package + Meta Prophet Counterfactual Forecasting

```python
class CounterfactualEngine:
    async def compute_counterfactual(self,
                                       action: FLEAction,
                                       outcome: Verdict) -> CounterfactualResult:
        # 1. 构建反事实基线：如果没做action，系统的预测轨迹是什么
        #    使用action前30min的系统状态+相似历史窗口做time-series forecast
        pre_action_metrics = await self._load_pre_action_metrics(
            action.target, lookback_min=30)
        counterfactual_trajectory = await self._forecast_without_intervention(
            pre_action_metrics, forecast_min=15)
        # 2. 实际轨迹（做了action之后）
        actual_trajectory = await self._load_post_action_metrics(
            action.target, lookahead_min=15)
        # 3. Attribution: actual vs counterfactual的差异
        delta = self._compute_trajectory_delta(actual_trajectory,
                                                 counterfactual_trajectory)
        if abs(delta) < 0.05:  # 差异<5%→action可能无效，问题自愈了
            self.FLE.notify_owner("COUNTERFACTUAL_NO_EFFECT",
                f"Action {action.action_type} shows NO significant effect vs counterfactual. "
                f"Delta={delta:.1%}. The anomaly may have self-resolved. "
                f"FLE will DOWNGRADE confidence in this action for similar anomaly patterns.")
            await self._downgrade_action_for_pattern(action)
            return CounterfactualResult(effect="NONE", delta=delta,
                conclusion="ANOMALY_LIKELY_SELF_RESOLVED")
        elif delta < -0.10:  # 反事实更差→action确实有效
            return CounterfactualResult(effect="POSITIVE", delta=delta,
                conclusion="ACTION_EFFECTIVE")
        else:  # actual比反事实更差→action造成了恶化
            self.FLE.notify_owner("COUNTERFACTUAL_NEGATIVE",
                f"Action {action.action_type} made things WORSE than no-intervention. "
                f"Delta={delta:.1%}. Counterfactual trajectory was better. "
                f"FLE will IMMEDIATELY retire this action for this anomaly pattern.")
            await self._retire_action_for_pattern(action)
            return CounterfactualResult(effect="NEGATIVE", delta=delta,
                conclusion="ACTION_HARMFUL")
```
