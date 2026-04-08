"""
修复Layer定位脚本
用途：为缺少Layer的文档添加Layer定位
创建时间：2026-04-07
"""

import re
from pathlib import Path
from datetime import datetime

BLUEPRINTS_DIR = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS")


def read_document(filepath: Path) -> str:
    """读取文档内容"""
    encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'latin-1']
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    return ""


def extract_yaml_header(content: str) -> dict:
    """提取YAML头部"""
    yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not yaml_match:
        return {}
    
    yaml_content = yaml_match.group(1)
    yaml_dict = {}
    
    for line in yaml_content.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            yaml_dict[key.strip()] = value.strip().strip('"\'')
    
    return yaml_dict


def fix_layer(filepath: Path) -> bool:
    """修复Layer定位"""
    content = read_document(filepath)
    if not content:
        return False
    
    # 提取已有的YAML头部
    yaml_header = extract_yaml_header(content)
    
    # 如果已有layer字段，检查格式是否正确
    if 'layer' in yaml_header:
        layer_value = yaml_header.get('layer', '')
        # 检查是否是简单的Layer格式（如"Layer 6"）
        if re.match(r'^["\']?Layer\s+\d+', layer_value):
            return True  # 已有正确的Layer定位
        # 如果是复杂的格式，尝试修复
        if '|' in layer_value or '业务架构' in layer_value:
            # 简化layer字段
            new_layer = re.sub(r'^["\']?(Layer\s+\d+).*$', r'\1', layer_value)
            content = re.sub(
                r'layer:\s*["\']?.*?["\']?\s*\n',
                f'layer: "{new_layer}"\n',
                content
            )
            with open(filepath, 'w', encoding='utf-8-sig') as f:
                f.write(content)
            return True
        return True
    
    # 从文件名推断Layer
    filename = filepath.stem
    
    layer_mapping = {
        "DATA": "Layer 1 (数据源层)",
        "ALPHA": "Layer 2 (Alpha因子层)",
        "STRATEGY": "Layer 3 (策略层)",
        "AI": "Layer 4 (机器学习层)",
        "PORTFOLIO": "Layer 6 (组合优化层)",
        "REBALANCING": "Layer 6 (组合优化层)",
        "RISK": "Layer 7 (风险管理层)",
        "EXECUTION": "Layer 8 (执行层)",
        "TRADING": "Layer 8 (执行层)",
        "MONITORING": "Layer 9 (监控层)",
        "MEAN_VARIANCE": "Layer 6 (组合优化层)",
        "MARGIN": "Layer 7 (风险管理层)",
    }
    
    layer = "Layer 6 (组合优化层)"  # 默认
    for keyword, layer_name in layer_mapping.items():
        if keyword in filename.upper():
            layer = layer_name
            break
    
    # 添加layer字段到YAML头部
    content = re.sub(
        r'^(---\s*\n)(.*?)(\n---\s*\n)',
        r'\1\2\nlayer: "' + layer + '"\n\3',
        content,
        flags=re.DOTALL
    )
    
    with open(filepath, 'w', encoding='utf-8-sig') as f:
        f.write(content)
    
    return True


def main():
    """主函数"""
    print("="*80)
    print("修复Layer定位")
    print("="*80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 需要修复Layer的文档列表
    docs_need_layer = [
        "AI_PATTERN_RECOGNITION_ENGINE_BLUEPRINT.md",
        "ALPHA_FACTOR_FACTORY_BLUEPRINT.md",
        "CONSTRAINT_SOLVER_BLUEPRINT.md",
        "DATA_QUALITY_MONITORING_BLUEPRINT.md",
        "DYNAMIC_CORRELATION_MODELING_BLUEPRINT.md",
        "DYNAMIC_LEVERAGE_MANAGEMENT_BLUEPRINT.md",
        "ECONOMIC_REGIME_ENGINE_BLUEPRINT.md",
        "FINANCING_OPTIMIZATION_BLUEPRINT.md",
        "INTRADAY_STRATEGY_BLUEPRINT.md",
        "LIQUIDITY_MANAGEMENT_SYSTEM_BLUEPRINT.md",
        "MARGIN_CALL_MONITOR_BLUEPRINT.md",
        "MARKET_IMPACT_MODEL_BLUEPRINT.md",
        "MARKET_REGIME_DETECTION_BLUEPRINT.md",
        "MEAN_VARIANCE_OPTIMIZATION_BLUEPRINT.md",
        "MULTI_ASSET_ALLOCATION_BLUEPRINT.md",
        "MULTI_STRATEGY_HIERARCHICAL_SYSTEM_BLUEPRINT.md",
        "OPENING_STRATEGY_BLUEPRINT.md",
        "PORTFOLIO_INSURANCE_STRATEGY_BLUEPRINT.md",
        "PORTFOLIO_REBALANCING_BLUEPRINT.md",
        "QUARTERLY_REBALANCE_BLUEPRINT.md",
        "REALTIME_RISK_HEDGE_ENGINE_BLUEPRINT.md",
        "RISK_CONTROL_BLUEPRINT.md",
        "RL_REBALANCING_SYSTEM_BLUEPRINT.md",
        "SMART_EXECUTION_ENGINE_BLUEPRINT.md",
        "STATISTICAL_ARBITRAGE_MODULE_BLUEPRINT.md",
        "STRATEGIC_WEIGHTING_BLUEPRINT.md",
        "TAIL_RISK_HEDGING_BLUEPRINT.md",
        "TRADING_COST_OPTIMIZATION_BLUEPRINT.md",
        "UNIFIED_DATA_INFRASTRUCTURE_BLUEPRINT.md",
    ]
    
    fixed_count = 0
    
    for filename in docs_need_layer:
        filepath = BLUEPRINTS_DIR / filename
        if not filepath.exists():
            continue
        
        if fix_layer(filepath):
            fixed_count += 1
            print(f"✅ {filename}")
    
    print("\n" + "="*80)
    print("完成")
    print("="*80)
    print(f"修复Layer定位: {fixed_count}个文档")


if __name__ == "__main__":
    main()
