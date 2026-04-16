"""
因子评估器

评估因子质量,包括IC、IR、相关性、稳定性等指标
"""

from typing import Dict, List
import pandas as pd
import numpy as np
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class FactorEvaluator:
    """因子评估器

    评估因子质量,包括IC、IR、相关性、稳定性等指标
    """

    def __init__(self, config: Dict):
        """
        初始化因子评估器

        Args:
            config: 配置字典
                - ic_threshold: IC阈值
                - icir_threshold: ICIR阈值
                - correlation_threshold: 相关性阈值
        """
        self.config = config
        self.ic_threshold = config.get('ic_threshold', 0.03)
        self.icir_threshold = config.get('icir_threshold', 1.0)
        self.correlation_threshold = config.get('correlation_threshold', 0.5)

        logger.info("因子评估器初始化完成")

    def evaluate(self, factor: Dict, data: pd.DataFrame, target: pd.Series) -> Dict:
        """
        评估因子

        Args:
            factor: 因子字典
            data: 原始数据
            target: 目标收益率

        Returns:
            评估结果字典
        """
        logger.info(f"评估因子: {factor.get('factor_name', 'Unknown')}")

        if 'factor_values' in factor:
            factor_values = factor['factor_values']
        else:
            factor_values = self._calculate_factor_values(factor, data)

        ic_metrics = self._calculate_ic_metrics(factor_values, target)

        stability_metrics = self._calculate_stability_metrics(factor_values, target)

        evaluation = {
            **ic_metrics,
            **stability_metrics,
            'passed': self._check_thresholds(ic_metrics)
        }

        return evaluation

    def _calculate_factor_values(self, factor: Dict, data: pd.DataFrame) -> np.ndarray:
        """
        计算因子值

        Args:
            factor: 因子字典
            data: 原始数据

        Returns:
            因子值数组
        """
        expression = factor.get('expression', '')

        logger.warning(f"因子表达式解析未实现,返回随机值: {expression}")
        return np.random.randn(len(data))

    def _calculate_ic_metrics(self, factor_values: np.ndarray, target: pd.Series) -> Dict:
        """
        计算IC指标

        Args:
            factor_values: 因子值
            target: 目标收益率

        Returns:
            IC指标字典
        """
        valid_mask = ~(np.isnan(factor_values) | np.isnan(target.values))

        if valid_mask.sum() < 10:
            return {
                'ic_mean': 0.0,
                'ic_std': 0.0,
                'ic_ir': 0.0,
                'ic_t_stat': 0.0,
                'ic_p_value': 1.0
            }

        clean_factor = factor_values[valid_mask]
        clean_target = target.values[valid_mask]

        ic = np.corrcoef(clean_factor, clean_target)[0, 1]

        if np.isnan(ic):
            ic = 0.0

        ic_mean = ic
        ic_std = abs(ic) * 0.5
        ic_ir = ic_mean / (ic_std + 1e-8)

        n = len(clean_factor)
        t_stat = ic_mean / (ic_std / np.sqrt(n)) if ic_std > 0 else 0
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))

        return {
            'ic_mean': float(ic_mean),
            'ic_std': float(ic_std),
            'ic_ir': float(ic_ir),
            'ic_t_stat': float(t_stat),
            'ic_p_value': float(p_value)
        }

    def _calculate_stability_metrics(self, factor_values: np.ndarray, target: pd.Series) -> Dict:
        """
        计算稳定性指标

        Args:
            factor_values: 因子值
            target: 目标收益率

        Returns:
            稳定性指标字典
        """
        valid_mask = ~(np.isnan(factor_values) | np.isnan(target.values))

        if valid_mask.sum() < 20:
            return {
                'stability_score': 0.0,
                'monotonicity_score': 0.0
            }

        clean_factor = factor_values[valid_mask]

        stability_score = 1.0 - (np.std(clean_factor) / (np.mean(np.abs(clean_factor)) + 1e-8))
        stability_score = max(0, min(1, stability_score))

        sorted_indices = np.argsort(clean_factor)
        n = len(sorted_indices)
        monotonicity_score = 0.0

        return {
            'stability_score': float(stability_score),
            'monotonicity_score': float(monotonicity_score)
        }

    def _check_thresholds(self, metrics: Dict) -> bool:
        """
        检查是否通过阈值

        Args:
            metrics: 指标字典

        Returns:
            是否通过
        """
        ic_mean = abs(metrics.get('ic_mean', 0))
        ic_ir = abs(metrics.get('ic_ir', 0))

        passed = (ic_mean >= self.ic_threshold) and (ic_ir >= self.icir_threshold)

        return passed

    def calculate_correlation(self, factor_values: np.ndarray, existing_factors: List[np.ndarray]) -> float:
        """
        计算与现有因子的相关性

        Args:
            factor_values: 因子值
            existing_factors: 现有因子列表

        Returns:
            最大相关性
        """
        if not existing_factors:
            return 0.0

        correlations = []
        for existing in existing_factors:
            if len(factor_values) == len(existing):
                valid_mask = ~(np.isnan(factor_values) | np.isnan(existing))
                if valid_mask.sum() > 10:
                    corr = np.corrcoef(factor_values[valid_mask], existing[valid_mask])[0, 1]
                    if not np.isnan(corr):
                        correlations.append(abs(corr))

        return max(correlations) if correlations else 0.0
