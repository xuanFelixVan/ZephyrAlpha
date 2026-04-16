"""
AI因子挖掘主接口

统一管理三大AI挖掘引擎,提供因子挖掘、评估、注册的完整流程
"""

from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import logging

from .deep_learning_miner import DeepLearningFactorMiner
from .reinforcement_learning_miner import ReinforcementLearningMiner
from .genetic_algorithm_miner import GeneticAlgorithmMiner
from .factor_evaluator import FactorEvaluator
from .factor_registry import FactorRegistry

logger = logging.getLogger(__name__)


class AIFactorMiner:
    """AI因子挖掘主接口

    统一管理三大AI挖掘引擎,提供因子挖掘、评估、注册的完整流程
    """

    def __init__(self, config: Dict):
        """
        初始化AI因子挖掘器

        Args:
            config: 配置字典,包含三大引擎的参数
        """
        self.config = config
        self.dl_miner = DeepLearningFactorMiner(config.get('deep_learning', {}))
        self.rl_miner = ReinforcementLearningMiner(config.get('reinforcement_learning', {}))
        self.ga_miner = GeneticAlgorithmMiner(config.get('genetic_algorithm', {}))
        self.evaluator = FactorEvaluator(config.get('evaluation', {}))
        self.registry = FactorRegistry(config.get('registry', {}))

        logger.info("AI因子挖掘器初始化完成")

    def mine_factors(self,
                    data: pd.DataFrame,
                    target: pd.Series,
                    methods: List[str] = ['deep_learning', 'reinforcement_learning', 'genetic_algorithm'],
                    min_ic: float = 0.03,
                    max_factors: int = 20) -> List[Dict]:
        """
        挖掘因子主方法

        Args:
            data: 原始特征数据 (index=date, columns=features)
            target: 目标收益率序列
            methods: 使用的挖掘方法列表
            min_ic: 最小IC阈值
            max_factors: 最大返回因子数量

        Returns:
            因子列表,每个因子包含:
            - factor_id: 因子ID
            - factor_name: 因子名称
            - expression: 因子表达式
            - ic_mean: IC均值
            - ic_ir: IC信息比率
            - method: 挖掘方法
            - complexity: 复杂度评分
            - created_at: 创建时间

        Raises:
            ValueError: 数据格式不正确
            RuntimeError: 挖掘过程失败
        """
        logger.info(f"开始因子挖掘,使用方法: {methods}")

        self._validate_data(data, target)

        all_factors = []

        if 'deep_learning' in methods:
            logger.info("开始深度学习因子挖掘...")
            dl_factors = self.dl_miner.mine_factors(data, target)
            all_factors.extend(dl_factors)
            logger.info(f"深度学习挖掘完成,发现{len(dl_factors)}个因子")

        if 'reinforcement_learning' in methods:
            logger.info("开始强化学习因子优化...")
            rl_factors = self.rl_miner.optimize_factors(data, target)
            all_factors.extend(rl_factors)
            logger.info(f"强化学习优化完成,发现{len(rl_factors)}个因子")

        if 'genetic_algorithm' in methods:
            logger.info("开始遗传算法因子发现...")
            ga_factors = self.ga_miner.mine_factors(data, target)
            all_factors.extend(ga_factors)
            logger.info(f"遗传算法发现完成,发现{len(ga_factors)}个因子")

        logger.info(f"总共挖掘{len(all_factors)}个因子,开始评估和筛选...")

        evaluated_factors = []
        for factor in all_factors:
            evaluation = self.evaluator.evaluate(factor, data, target)
            factor.update(evaluation)

            if factor['ic_mean'] >= min_ic:
                evaluated_factors.append(factor)

        evaluated_factors.sort(key=lambda x: x['ic_mean'], reverse=True)
        selected_factors = evaluated_factors[:max_factors]

        logger.info(f"筛选完成,选中{len(selected_factors)}个因子")

        return selected_factors

    def evaluate_factor(self,
                       factor_expression: str,
                       data: pd.DataFrame,
                       target: pd.Series) -> Dict:
        """
        评估单个因子

        Args:
            factor_expression: 因子表达式
            data: 原始数据
            target: 目标收益率

        Returns:
            评估结果字典,包含IC、IR、相关性等指标
        """
        factor = {'expression': factor_expression}
        evaluation = self.evaluator.evaluate(factor, data, target)
        return evaluation

    def register_factor(self, factor: Dict) -> str:
        """
        注册因子到因子库

        Args:
            factor: 因子字典

        Returns:
            factor_id: 注册后的因子ID

        Raises:
            ValueError: 因子验证失败
        """
        factor_id = self.registry.register(factor)
        logger.info(f"因子注册成功: {factor_id}")
        return factor_id

    def _validate_data(self, data: pd.DataFrame, target: pd.Series):
        """
        验证数据格式

        Args:
            data: 特征数据
            target: 目标收益率

        Raises:
            ValueError: 数据格式不正确
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("data必须是pandas DataFrame")

        if not isinstance(target, pd.Series):
            raise ValueError("target必须是pandas Series")

        if len(data) != len(target):
            raise ValueError(f"data和target长度不一致: data={len(data)}, target={len(target)}")

        if data.isnull().any().any():
            null_count = data.isnull().sum().sum()
            raise ValueError(f"data包含{null_count}个缺失值")

        if target.isnull().any():
            null_count = target.isnull().sum()
            raise ValueError(f"target包含{null_count}个缺失值")

        logger.info("数据验证通过")
