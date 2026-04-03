"""
AI因子挖掘模块

使用深度学习、强化学习、遗传算法自动挖掘原创Alpha因子
"""

from .ai_factor_miner import AIFactorMiner
from .deep_learning_miner import DeepLearningFactorMiner
from .reinforcement_learning_miner import ReinforcementLearningMiner
from .genetic_algorithm_miner import GeneticAlgorithmMiner
from .factor_evaluator import FactorEvaluator
from .factor_registry import FactorRegistry

__all__ = [
    'AIFactorMiner',
    'DeepLearningFactorMiner',
    'ReinforcementLearningMiner',
    'GeneticAlgorithmMiner',
    'FactorEvaluator',
    'FactorRegistry'
]

__version__ = '1.0.0'
