---
module_id: KE-1828
status: active
title: 2.245 Internal Model Ensemble Diversity Monitor - model_ensemble_diversity.py (🆕
category: module_blueprint
ttl: permanent
---

# 2.245 Internal Model Ensemble Diversity Monitor - model_ensemble_diversity.py (🆕

2.245 Internal Model Ensemble Diversity Monitor - model_ensemble_diversity.py (🆕 v0.23.0 - 盲点294 — FLE所有内部模型趋向于相同的世界观→集体盲区)

**致命问题**：FLE内的anomaly_detector、regime_detector、diagnosis_engine、action_selection_model、verification_engine——这些都是基于相似数据训练的模型。随着时间的推移，共享的训练数据和统一的LLM backbone可能使它们收敛到相同的世界观。当所有模型同质化→FLE的"多样性"（diversity）完全消失→这就是金融系统中的"herding"（羊群效应）在AIOps中的体现——"CRC=CPU负载→所有模型同意→95% confidence→实际上这是一个新类型的anomaly，所有模型都没见过"→集体误诊。
**对标**：Google Ensemble Diversity in ML + Netflix Diversity-Aware Recommendation + scikit-learn Classifier Diversity Metrics + Q-statistic Measure + Meta FAIR Model Zoo Diversity

```python
@dataclass
class ModelOutputPair:
    model_a: str
    model_b: str
    spearman_rho: float         # 排序一致性
    agreement_rate: float       # 二元决策一致率
    q_statistic: float          # 分类器多样性Q统计量 (-1:max diversity, +1:max agreement)
    trend_direction: str        # "DIVERGING"|"CONVERGING"|"STABLE"

class ModelEnsembleDiversityMonitor:
    MIN_DIVERSITY_ALERT: float = -0.3     # Q< -0.3 →足够多样
    CONVERGENCE_ALERT_Q: float = 0.75     # Q> 0.75 →过度一致
    TREND_WINDOW_DAYS: int = 30

    async def monitor_ensemble_diversity(self) -> DiversityDashboard:
        models = ["anomaly_detector", "regime_detector", "diagnosis_engine",
                   "action_selection_model", "verification_engine"]
        pairs = []
        for i in range(len(models)):
            for j in range(i + 1, len(models)):
                a, b = models[i], models[j]
                outputs_a = await self._get_recent_outputs(a)
                outputs_b = await self._get_recent_outputs(b)
                spearman = await self._compute_spearman(outputs_a, outputs_b)
                q = await self._compute_q_statistic(outputs_a, outputs_b)
                agreement = len([x for x, y in zip(outputs_a, outputs_b)
                               if x.classification == y.classification]) / len(outputs_a)
                trend = await self._compute_diversity_trend(a, b, self.TREND_WINDOW_DAYS)
                pairs.append(ModelOutputPair(
                    model_a=a, model_b=b,
                    spearman_rho=spearman, agreement_rate=agreement,
                    q_statistic=q, trend_direction=trend))
        converged_pairs = [p for p in pairs if p.q_statistic > self.CONVERGENCE_ALERT_Q]
        if len(converged_pairs) >= 3:
            self.FLE.notify_owner("MODEL_ENSEMBLE_CONVERGENCE",
                f"{len(converged_pairs)}/{len(pairs)} model pairs have converged "
                f"(Q > {self.CONVERGENCE_ALERT_Q}). Ensemble diversity at RISK. "
                f"Most converged: {', '.join(f'{p.model_a}/{p.model_b}(Q={p.q_statistic:.2f})' for p in converged_pairs[:3])}. "
                f"Recommend: (a) inject adversarial test cases known to trigger disagreements, "
                f"(b) add adversarial noise to training data to force diversity, "
                f"(c) temporarily increase anomaly creation rate for novel patterns.")
            await self._inject_
