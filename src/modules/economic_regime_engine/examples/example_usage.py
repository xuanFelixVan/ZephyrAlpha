"""
经济范式判断引擎使用示例

演示如何使用经济范式判断引擎进行宏观经济周期识别和资产配置建议。

模块ID: ECONOMIC_REGIME_ENGINE_001
版本: v1.0.0
"""

from datetime import datetime
import logging
from economic_regime_engine import (
    EconomicRegime,
    RegimeAnalysis,
    MacroIndicators,
    EconomicRegimeEngine
)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def example_basic_usage():
    """基本使用示例"""
    print("\n" + "="*80)
    print("示例1: 基本使用 - 自动采集数据并分析经济范式")
    print("="*80 + "\n")
    
    engine = EconomicRegimeEngine()
    
    analysis = engine.analyze_current_regime()
    
    print(f"主导经济范式: {analysis.dominant_regime.value}")
    print(f"置信度: {analysis.confidence:.2%}")
    print(f"风险等级: {analysis.risk_level}")
    
    print("\n范式概率分布:")
    for regime, prob in analysis.probabilities.items():
        print(f"  {regime.value:15s}: {prob:.2%}")
    
    print("\n推荐资产配置:")
    for asset, weight in analysis.recommended_assets.items():
        print(f"  {asset:15s}: {weight:.2%}")
    
    if analysis.risk_warnings:
        print("\n风险预警:")
        for warning in analysis.risk_warnings:
            print(f"  ⚠️  {warning}")


def example_custom_macro_data():
    """自定义宏观数据示例"""
    print("\n" + "="*80)
    print("示例2: 自定义宏观数据 - 使用特定经济指标进行分析")
    print("="*80 + "\n")
    
    engine = EconomicRegimeEngine()
    
    custom_macro_data = MacroIndicators(
        gdp_growth=5.5,          # GDP增长率 5.5%
        cpi=4.2,                 # CPI通胀率 4.2%
        ppi=3.5,                 # PPI通胀率 3.5%
        pmi=48.5,                # PMI景气度 48.5（收缩区间）
        interest_rate=3.5,       # 利率 3.5%
        m2_growth=8.5,           # M2增速 8.5%
        credit_growth=10.2,      # 信贷增速 10.2%
        industrial_output=5.0,   # 工业增加值 5.0%
        timestamp=datetime.now()
    )
    
    print("输入宏观经济指标:")
    print(f"  GDP增长率: {custom_macro_data.gdp_growth}%")
    print(f"  CPI通胀率: {custom_macro_data.cpi}%")
    print(f"  PMI景气度: {custom_macro_data.pmi}")
    
    analysis = engine.analyze_current_regime(custom_macro_data)
    
    print(f"\n主导经济范式: {analysis.dominant_regime.value}")
    print(f"置信度: {analysis.confidence:.2%}")
    print(f"风险等级: {analysis.risk_level}")
    
    print("\n范式概率分布:")
    for regime, prob in analysis.probabilities.items():
        print(f"  {regime.value:15s}: {prob:.2%}")


def example_get_specific_info():
    """获取特定信息示例"""
    print("\n" + "="*80)
    print("示例3: 获取特定信息 - 分别获取概率、配置、预警")
    print("="*80 + "\n")
    
    engine = EconomicRegimeEngine()
    
    probabilities = engine.get_regime_probability()
    print("范式概率分布:")
    for regime, prob in probabilities.items():
        print(f"  {regime.value:15s}: {prob:.2%}")
    
    allocation = engine.get_asset_allocation()
    print("\n资产配置建议:")
    for asset, weight in allocation.items():
        print(f"  {asset:15s}: {weight:.2%}")
    
    warnings = engine.get_risk_warnings()
    if warnings:
        print("\n风险预警:")
        for warning in warnings:
            print(f"  ⚠️  {warning}")
    else:
        print("\n当前无风险预警")


def example_regime_scenarios():
    """不同经济范式场景示例"""
    print("\n" + "="*80)
    print("示例4: 不同经济范式场景 - 模拟四种经济周期")
    print("="*80 + "\n")
    
    engine = EconomicRegimeEngine()
    
    scenarios = {
        "扩张期场景": MacroIndicators(
            gdp_growth=7.5, cpi=2.0, ppi=1.5, pmi=53.5,
            interest_rate=3.0, m2_growth=11.0, credit_growth=14.0,
            industrial_output=7.5, timestamp=datetime.now()
        ),
        "滞胀期场景": MacroIndicators(
            gdp_growth=4.5, cpi=5.5, ppi=6.0, pmi=47.0,
            interest_rate=4.5, m2_growth=7.5, credit_growth=9.0,
            industrial_output=4.0, timestamp=datetime.now()
        ),
        "衰退期场景": MacroIndicators(
            gdp_growth=4.0, cpi=1.0, ppi=-1.0, pmi=45.0,
            interest_rate=2.5, m2_growth=8.0, credit_growth=8.0,
            industrial_output=3.5, timestamp=datetime.now()
        ),
        "复苏期场景": MacroIndicators(
            gdp_growth=6.8, cpi=3.5, ppi=3.0, pmi=52.0,
            interest_rate=3.5, m2_growth=12.0, credit_growth=13.0,
            industrial_output=6.5, timestamp=datetime.now()
        )
    }
    
    for scenario_name, macro_data in scenarios.items():
        print(f"\n{scenario_name}:")
        print(f"  GDP={macro_data.gdp_growth}%, CPI={macro_data.cpi}%, PMI={macro_data.pmi}")
        
        analysis = engine.analyze_current_regime(macro_data)
        
        print(f"  → 识别范式: {analysis.dominant_regime.value} (置信度: {analysis.confidence:.2%})")
        print(f"  → 风险等级: {analysis.risk_level}")
        print(f"  → 推荐配置: 股票{analysis.recommended_assets['equity']:.0%}, "
              f"债券{analysis.recommended_assets['bonds']:.0%}, "
              f"商品{analysis.recommended_assets['commodities']:.0%}")


def example_export_results():
    """导出结果示例"""
    print("\n" + "="*80)
    print("示例5: 导出结果 - 将分析结果转换为字典格式")
    print("="*80 + "\n")
    
    engine = EconomicRegimeEngine()
    
    analysis = engine.analyze_current_regime()
    
    result_dict = analysis.to_dict()
    
    import json
    print("分析结果（JSON格式）:")
    print(json.dumps(result_dict, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    print("\n" + "="*80)
    print("经济范式判断引擎使用示例")
    print("="*80)
    
    example_basic_usage()
    example_custom_macro_data()
    example_get_specific_info()
    example_regime_scenarios()
    example_export_results()
    
    print("\n" + "="*80)
    print("示例执行完成")
    print("="*80 + "\n")
