"""
AI因子挖掘模块使用示例

演示如何使用深度学习、强化学习、遗传算法挖掘因子
"""

import pandas as pd
import numpy as np
from src.modules.ai_factor_miner import AIFactorMiner


def generate_sample_data():
    """
    生成示例数据

    Returns:
        data: 特征数据
        target: 目标收益率
    """
    np.random.seed(42)
    n_samples = 1000
    n_features = 10

    dates = pd.date_range('2020-01-01', periods=n_samples, freq='D')
    feature_names = [f'feature_{i}' for i in range(n_features)]

    data = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        index=dates,
        columns=feature_names
    )

    target = pd.Series(
        np.random.randn(n_samples) * 0.02,
        index=dates,
        name='return'
    )

    return data, target


def example_deep_learning_mining():
    """
    深度学习因子挖掘示例
    """
    print("=" * 60)
    print("深度学习因子挖掘示例")
    print("=" * 60)

    config = {
        'deep_learning': {
            'model_type': 'lstm',
            'hidden_size': 64,
            'num_layers': 1,
            'epochs': 10,
            'batch_size': 32,
            'lookback_window': 10
        },
        'evaluation': {
            'ic_threshold': 0.01,
            'icir_threshold': 0.5
        },
        'registry': {
            'db_path': 'data/factors/example_factor_registry.db'
        }
    }

    miner = AIFactorMiner(config)

    data, target = generate_sample_data()

    factors = miner.mine_factors(
        data=data,
        target=target,
        methods=['deep_learning'],
        min_ic=0.01,
        max_factors=5
    )

    print(f"\n挖掘到 {len(factors)} 个因子:")
    for i, factor in enumerate(factors, 1):
        print(f"\n因子 {i}:")
        print(f"  ID: {factor['factor_id']}")
        print(f"  名称: {factor['factor_name']}")
        print(f"  方法: {factor['method']}")
        print(f"  IC均值: {factor.get('ic_mean', 0):.4f}")
        print(f"  ICIR: {factor.get('ic_ir', 0):.4f}")
        print(f"  复杂度: {factor.get('complexity', 0)}")

    return factors


def example_genetic_algorithm_mining():
    """
    遗传算法因子挖掘示例
    """
    print("\n" + "=" * 60)
    print("遗传算法因子挖掘示例")
    print("=" * 60)

    config = {
        'genetic_algorithm': {
            'population_size': 100,
            'generations': 10,
            'max_complexity': 30
        },
        'evaluation': {
            'ic_threshold': 0.01,
            'icir_threshold': 0.5
        },
        'registry': {
            'db_path': 'data/factors/example_factor_registry.db'
        }
    }

    miner = AIFactorMiner(config)

    data, target = generate_sample_data()

    factors = miner.mine_factors(
        data=data,
        target=target,
        methods=['genetic_algorithm'],
        min_ic=0.01,
        max_factors=5
    )

    print(f"\n挖掘到 {len(factors)} 个因子:")
    for i, factor in enumerate(factors, 1):
        print(f"\n因子 {i}:")
        print(f"  ID: {factor['factor_id']}")
        print(f"  名称: {factor['factor_name']}")
        print(f"  表达式: {factor.get('expression', 'N/A')}")
        print(f"  IC均值: {factor.get('ic_mean', 0):.4f}")
        print(f"  复杂度: {factor.get('complexity', 0)}")

    return factors


def example_multi_method_mining():
    """
    多方法组合挖掘示例
    """
    print("\n" + "=" * 60)
    print("多方法组合因子挖掘示例")
    print("=" * 60)

    config = {
        'deep_learning': {
            'model_type': 'lstm',
            'hidden_size': 32,
            'epochs': 5,
            'lookback_window': 5
        },
        'genetic_algorithm': {
            'population_size': 50,
            'generations': 5
        },
        'evaluation': {
            'ic_threshold': 0.01
        },
        'registry': {
            'db_path': 'data/factors/example_factor_registry.db'
        }
    }

    miner = AIFactorMiner(config)

    data, target = generate_sample_data()

    factors = miner.mine_factors(
        data=data,
        target=target,
        methods=['deep_learning', 'genetic_algorithm'],
        min_ic=0.01,
        max_factors=10
    )

    print(f"\n总共挖掘到 {len(factors)} 个因子:")

    method_counts = {}
    for factor in factors:
        method = factor['method']
        method_counts[method] = method_counts.get(method, 0) + 1

    print("\n按方法统计:")
    for method, count in method_counts.items():
        print(f"  {method}: {count} 个因子")

    print("\nTop 5 因子 (按IC排序):")
    sorted_factors = sorted(factors, key=lambda x: x.get('ic_mean', 0), reverse=True)[:5]
    for i, factor in enumerate(sorted_factors, 1):
        print(f"\n  {i}. {factor['factor_name']}")
        print(f"     方法: {factor['method']}")
        print(f"     IC: {factor.get('ic_mean', 0):.4f}")

    return factors


def main():
    """
    主函数
    """
    print("\n" + "=" * 60)
    print("AI因子挖掘模块使用示例")
    print("=" * 60)

    try:
        factors_dl = example_deep_learning_mining()
    except Exception as e:
        print(f"\n深度学习示例失败: {e}")

    try:
        factors_ga = example_genetic_algorithm_mining()
    except Exception as e:
        print(f"\n遗传算法示例失败: {e}")

    try:
        factors_multi = example_multi_method_mining()
    except Exception as e:
        print(f"\n多方法组合示例失败: {e}")

    print("\n" + "=" * 60)
    print("示例运行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
