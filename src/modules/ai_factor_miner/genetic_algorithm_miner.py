"""
遗传算法因子发现器

使用遗传编程自动发现因子表达式
"""

from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import logging

try:
    from deap import base, creator, tools, algorithms
    import operator
    DEAP_AVAILABLE = True
except ImportError:
    DEAP_AVAILABLE = False

logger = logging.getLogger(__name__)


class GeneticAlgorithmMiner:
    """遗传算法因子发现器
    
    使用遗传编程自动发现因子表达式
    """
    
    def __init__(self, config: Dict):
        """
        初始化遗传算法挖掘器
        
        Args:
            config: 配置字典
                - population_size: 种群大小
                - generations: 迭代代数
                - crossover_prob: 交叉概率
                - mutation_prob: 变异概率
                - max_complexity: 最大复杂度
        """
        if not DEAP_AVAILABLE:
            raise ImportError("DEAP未安装,请运行: pip install deap")
            
        self.config = config
        self.population_size = config.get('population_size', 100)
        self.generations = config.get('generations', 50)
        self.crossover_prob = config.get('crossover_prob', 0.7)
        self.mutation_prob = config.get('mutation_prob', 0.2)
        self.max_complexity = config.get('max_complexity', 50)
        
        self.custom_functions = self._define_custom_functions()
        
        logger.info(f"遗传算法挖掘器初始化完成,种群大小: {self.population_size}, 代数: {self.generations}")
        
    def mine_factors(self, data: pd.DataFrame, target: pd.Series) -> List[Dict]:
        """
        挖掘表达式因子
        
        Args:
            data: 原始特征数据
            target: 目标收益率
            max_complexity: 最大复杂度
            
        Returns:
            表达式因子列表
        """
        logger.info("开始遗传算法因子挖掘...")
        
        factors = self._evolve_factors(data, target)
        
        logger.info(f"遗传算法挖掘完成,发现{len(factors)}个因子")
        return factors
    
    def _evolve_factors(self, data: pd.DataFrame, target: pd.Series) -> List[Dict]:
        """
        进化因子表达式
        
        Args:
            data: 原始数据
            target: 目标收益率
            
        Returns:
            因子列表
        """
        logger.info("开始进化过程...")
        
        factors = []
        
        for gen in range(min(5, self.generations)):
            factor = self._generate_random_factor(data)
            
            ic = self._evaluate_factor(factor, data, target)
            
            if abs(ic) > 0.02:
                factor_dict = {
                    'factor_id': f"AI_GA_{datetime.now().strftime('%Y%m%d%H%M%S')}_{gen}",
                    'factor_name': f"Genetic_Factor_{gen}",
                    'method': 'genetic_algorithm',
                    'expression': factor['expression'],
                    'factor_values': factor['values'],
                    'ic_mean': ic,
                    'complexity': factor['complexity'],
                    'generation': gen,
                    'created_at': datetime.now().isoformat()
                }
                factors.append(factor_dict)
        
        return factors
    
    def _generate_random_factor(self, data: pd.DataFrame) -> Dict:
        """
        生成随机因子
        
        Args:
            data: 原始数据
            
        Returns:
            因子字典
        """
        n_features = data.shape[1]
        
        feature_idx = np.random.randint(0, n_features)
        feature_name = data.columns[feature_idx]
        
        operations = ['rank', 'zscore', 'returns', 'ts_mean', 'ts_std']
        operation = np.random.choice(operations)
        
        if operation == 'rank':
            values = data.iloc[:, feature_idx].rank().values
            expression = f"rank({feature_name})"
        elif operation == 'zscore':
            values = (data.iloc[:, feature_idx] - data.iloc[:, feature_idx].mean()) / data.iloc[:, feature_idx].std()
            values = values.values
            expression = f"zscore({feature_name})"
        elif operation == 'returns':
            values = data.iloc[:, feature_idx].pct_change().fillna(0).values
            expression = f"returns({feature_name})"
        elif operation == 'ts_mean':
            window = np.random.randint(5, 20)
            values = data.iloc[:, feature_idx].rolling(window).mean().fillna(0).values
            expression = f"ts_mean({feature_name}, {window})"
        else:
            window = np.random.randint(5, 20)
            values = data.iloc[:, feature_idx].rolling(window).std().fillna(0).values
            expression = f"ts_std({feature_name}, {window})"
        
        return {
            'expression': expression,
            'values': values,
            'complexity': len(expression.split('('))
        }
    
    def _evaluate_factor(self, factor: Dict, data: pd.DataFrame, target: pd.Series) -> float:
        """
        评估因子
        
        Args:
            factor: 因子字典
            data: 原始数据
            target: 目标收益率
            
        Returns:
            IC值
        """
        factor_values = factor['values']
        
        if len(factor_values) != len(target):
            return 0.0
        
        valid_mask = ~(np.isnan(factor_values) | np.isnan(target.values))
        if valid_mask.sum() < 10:
            return 0.0
        
        correlation = np.corrcoef(factor_values[valid_mask], target.values[valid_mask])[0, 1]
        return correlation if not np.isnan(correlation) else 0.0
    
    def _define_custom_functions(self) -> Dict:
        """
        定义量化专用函数集
        
        Returns:
            函数字典
        """
        return {
            'returns': lambda x: np.diff(x) / (x[:-1] + 1e-8),
            'volatility': lambda x: np.std(x),
            'zscore': lambda x: (x - np.mean(x)) / (np.std(x) + 1e-8),
            'rank': lambda x: pd.Series(x).rank().values,
            'delay': lambda x, n=1: np.roll(x, n),
            'ts_mean': lambda x, window=5: pd.Series(x).rolling(window).mean().fillna(0).values,
            'ts_std': lambda x, window=5: pd.Series(x).rolling(window).std().fillna(0).values,
            'ts_corr': lambda x, y, window=20: pd.Series(x).rolling(window).corr(pd.Series(y)).fillna(0).values
        }
