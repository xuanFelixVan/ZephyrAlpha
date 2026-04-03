"""
强化学习因子优化器

使用DQN、PPO、A2C等强化学习算法优化因子组合
"""

from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import logging

try:
    import gymnasium as gym
    from gymnasium import spaces
    GYM_AVAILABLE = True
except ImportError:
    GYM_AVAILABLE = False

try:
    from stable_baselines3 import DQN, PPO, A2C
    from stable_baselines3.common.vec_env import DummyVecEnv
    SB3_AVAILABLE = True
except ImportError:
    SB3_AVAILABLE = False

logger = logging.getLogger(__name__)


class FactorOptimizationEnv(gym.Env):
    """因子优化环境"""
    
    def __init__(self, factors: List[Dict], data: pd.DataFrame, target: pd.Series):
        super(FactorOptimizationEnv, self).__init__()
        
        self.factors = factors
        self.data = data
        self.target = target
        self.n_factors = len(factors)
        
        self.action_space = spaces.Box(low=0.0, high=1.0, shape=(self.n_factors,), dtype=np.float32)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, 
                                           shape=(self.n_factors,), dtype=np.float32)
        
        self.current_step = 0
        self.weights = np.ones(self.n_factors) / self.n_factors
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.weights = np.ones(self.n_factors) / self.n_factors
        return self._get_observation(), {}
        
    def step(self, action):
        self.weights = action / (np.sum(action) + 1e-8)
        
        combined_factor = self._calculate_combined_factor()
        
        ic = self._calculate_ic(combined_factor)
        
        reward = ic
        
        self.current_step += 1
        done = self.current_step >= len(self.data) - 1
        
        return self._get_observation(), reward, done, False, {}
        
    def _get_observation(self):
        obs = np.array([f.get('ic_mean', 0) for f in self.factors], dtype=np.float32)
        return obs
        
    def _calculate_combined_factor(self):
        combined = np.zeros(len(self.data))
        for i, factor in enumerate(self.factors):
            if 'factor_values' in factor:
                combined += self.weights[i] * factor['factor_values']
        return combined
        
    def _calculate_ic(self, factor_values):
        if len(factor_values) != len(self.target):
            return 0.0
        
        valid_mask = ~(np.isnan(factor_values) | np.isnan(self.target.values))
        if valid_mask.sum() < 10:
            return 0.0
        
        correlation = np.corrcoef(factor_values[valid_mask], self.target.values[valid_mask])[0, 1]
        return correlation if not np.isnan(correlation) else 0.0


class ReinforcementLearningMiner:
    """强化学习因子优化器
    
    使用DQN、PPO、A2C等强化学习算法优化因子组合
    """
    
    def __init__(self, config: Dict):
        """
        初始化强化学习优化器
        
        Args:
            config: 配置字典
                - algorithm: 'dqn' | 'ppo' | 'a2c'
                - learning_rate: 学习率
                - gamma: 折扣因子
                - buffer_size: 经验回放缓冲区大小
                - batch_size: 批次大小
        """
        if not GYM_AVAILABLE or not SB3_AVAILABLE:
            raise ImportError("gymnasium或stable-baselines3未安装,请运行: pip install gymnasium stable-baselines3")
            
        self.config = config
        self.algorithm = config.get('algorithm', 'ppo')
        self.learning_rate = config.get('learning_rate', 0.0003)
        self.gamma = config.get('gamma', 0.99)
        self.buffer_size = config.get('buffer_size', 100000)
        self.batch_size = config.get('batch_size', 64)
        
        self.model = None
        
        logger.info(f"强化学习优化器初始化完成,算法: {self.algorithm}")
        
    def optimize_factors(self, data: pd.DataFrame, target: pd.Series) -> List[Dict]:
        """
        优化因子权重
        
        Args:
            data: 原始数据
            target: 目标收益率
            
        Returns:
            优化后的因子列表
        """
        logger.info(f"开始{self.algorithm}因子优化...")
        
        dummy_factors = [
            {
                'factor_id': f'DUMMY_{i}',
                'factor_name': f'Dummy_Factor_{i}',
                'factor_values': data.iloc[:, i].values,
                'ic_mean': 0.03
            }
            for i in range(min(5, data.shape[1]))
        ]
        
        optimized_factors = self._optimize_factor_weights(dummy_factors, data, target)
        
        logger.info(f"{self.algorithm}优化完成,发现{len(optimized_factors)}个优化因子")
        return optimized_factors
        
    def _optimize_factor_weights(self, factors: List[Dict], data: pd.DataFrame, target: pd.Series) -> List[Dict]:
        """
        优化因子权重
        
        Args:
            factors: 因子列表
            data: 原始数据
            target: 目标收益率
            
        Returns:
            优化后的因子权重字典
        """
        env = DummyVecEnv([lambda: FactorOptimizationEnv(factors, data, target)])
        
        if self.algorithm == 'dqn':
            self.model = DQN(
                'MlpPolicy',
                env,
                learning_rate=self.learning_rate,
                gamma=self.gamma,
                buffer_size=self.buffer_size,
                batch_size=self.batch_size,
                verbose=1
            )
        elif self.algorithm == 'ppo':
            self.model = PPO(
                'MlpPolicy',
                env,
                learning_rate=self.learning_rate,
                gamma=self.gamma,
                batch_size=self.batch_size,
                verbose=1
            )
        elif self.algorithm == 'a2c':
            self.model = A2C(
                'MlpPolicy',
                env,
                learning_rate=self.learning_rate,
                gamma=self.gamma,
                verbose=1
            )
        else:
            raise ValueError(f"不支持的算法: {self.algorithm}")
        
        self.model.learn(total_timesteps=10000)
        
        obs = env.reset()
        action, _ = self.model.predict(obs)
        optimized_weights = action[0]
        
        optimized_factor = {
            'factor_id': f"AI_RL_{self.algorithm.upper()}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'factor_name': f"RL_Optimized_{self.algorithm.upper()}",
            'method': 'reinforcement_learning',
            'algorithm': self.algorithm,
            'expression': f"rl_optimized_combination(weights={optimized_weights.tolist()})",
            'optimized_weights': optimized_weights.tolist(),
            'complexity': len(factors),
            'created_at': datetime.now().isoformat()
        }
        
        return [optimized_factor]
    
    def dynamic_factor_selection(self,
                                factors: List[Dict],
                                market_state: str) -> List[str]:
        """
        动态因子选择
        
        Args:
            factors: 因子列表
            market_state: 市场状态 ('bull' | 'bear' | 'sideways')
            
        Returns:
            选中的因子ID列表
        """
        logger.info(f"动态因子选择,市场状态: {market_state}")
        
        sorted_factors = sorted(factors, key=lambda x: x.get('ic_mean', 0), reverse=True)
        
        if market_state == 'bull':
            selected = [f['factor_id'] for f in sorted_factors[:5]]
        elif market_state == 'bear':
            selected = [f['factor_id'] for f in sorted_factors[5:10]]
        else:
            selected = [f['factor_id'] for f in sorted_factors[:7]]
        
        logger.info(f"选中{len(selected)}个因子")
        return selected
