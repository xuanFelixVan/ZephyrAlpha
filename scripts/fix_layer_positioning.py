"""
批量修复Layer定位脚本
用途：自动为缺失Layer定位的文档添加layer字段
创建时间：2026-04-07
"""

import re
from pathlib import Path
from typing import Dict

BLUEPRINTS_DIR = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS")


def infer_layer_from_filename(filename: str) -> str:
    """从文件名推断Layer"""
    layer_keywords = {
        # Layer 1 - 数据预处理层
        'DATA_QUALITY': 'Layer 1 (数据预处理层) | 业务架构: 三级时间框架融合架构',
        'DATA_CATALOG': 'Layer 1 (数据预处理层) | 业务架构: 三级时间框架融合架构',
        'DATA_MESH': 'Layer 1 (数据预处理层) | 业务架构: 三级时间框架融合架构',
        'DATA_FABRIC': 'Layer 1 (数据预处理层) | 业务架构: 三级时间框架融合架构',
        'DATA_GOVERNANCE': 'Layer 1 (数据预处理层) | 业务架构: 三级时间框架融合架构',
        'DATA_LIFECYCLE': 'Layer 1 (数据预处理层) | 业务架构: 三级时间框架融合架构',
        'DATA_SOURCE': 'Layer 1 (数据预处理层) | 业务架构: 三级时间框架融合架构',
        'DATA_SECURITY': 'Layer 1 (数据预处理层) | 业务架构: 三级时间框架融合架构',
        'DATA_VERSION': 'Layer 1 (数据预处理层) | 业务架构: 三级时间框架融合架构',
        'DATA_COST': 'Layer 1 (数据预处理层) | 业务架构: 三级时间框架融合架构',
        'DATA_OBSERVABILITY': 'Layer 1 (数据预处理层) | 业务架构: 三级时间框架融合架构',
        'REALTIME_DATA': 'Layer 1 (数据预处理层) | 业务架构: 三级时间框架融合架构',
        'HIGH_PERFORMANCE_DATA': 'Layer 1 (数据预处理层) | 业务架构: 三级时间框架融合架构',
        'QUALITY_SCORING': 'Layer 1 (数据预处理层) | 业务架构: 三级时间框架融合架构',
        'QUALITY_REPORT': 'Layer 1 (数据预处理层) | 业务架构: 三级时间框架融合架构',
        'AUTO_REPAIR': 'Layer 1 (数据预处理层) | 业务架构: 三级时间框架融合架构',
        'ENHANCED_ALERT': 'Layer 1 (数据预处理层) | 业务架构: 三级时间框架融合架构',
        'UNIFIED_DATA': 'Layer 1 (数据预处理层) | 业务架构: 三级时间框架融合架构',
        
        # Layer 1 - 微观执行层
        'INTRADAY_STRATEGY': 'Layer 1 (微观执行层) | 业务架构: 三级时间框架融合架构',
        'OPENING_STRATEGY': 'Layer 1 (微观执行层) | 业务架构: 三级时间框架融合架构',
        'RISK_CONTROL': 'Layer 1 (微观执行层) | 业务架构: 三级时间框架融合架构',
        
        # Layer 5 - 策略执行层
        'SMART_EXECUTION': 'Layer 5 (策略执行层) | 业务架构: 三级时间框架融合架构',
        'MARKET_IMPACT': 'Layer 5 (策略执行层) | 业务架构: 三级时间框架融合架构',
        'TRADING_COST': 'Layer 5 (策略执行层) | 业务架构: 三级时间框架融合架构',
        'LIQUIDITY_MANAGEMENT': 'Layer 5 (策略执行层) | 业务架构: 三级时间框架融合架构',
        'STATISTICAL_ARBITRAGE': 'Layer 5 (策略执行层) | 业务架构: 三级时间框架融合架构',
        'SMART_ORDER_ROUTER': 'Layer 5 (策略执行层) | 业务架构: 三级时间框架融合架构',
        'TRADING_SIGNAL': 'Layer 5 (策略执行层) | 业务架构: 三级时间框架融合架构',
        'ALGORITHMIC_TRADING': 'Layer 5 (策略执行层) | 业务架构: 三级时间框架融合架构',
        'TRANSACTION_COST_ANALYSIS': 'Layer 5 (策略执行层) | 业务架构: 三级时间框架融合架构',
        'EXECUTION_STRATEGY': 'Layer 5 (策略执行层) | 业务架构: 三级时间框架融合架构',
        'STRATEGIC_WEIGHTING': 'Layer 5 (策略执行层) | 业务架构: 三级时间框架融合架构',
        
        # Layer 6 - 组合优化层
        'MULTI_ASSET': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'PORTFOLIO_INSURANCE': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'BLACK_LITTERMAN': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'RISK_PARITY': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'MULTI_OBJECTIVE': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'CONSTRAINT_SOLVER': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'DYNAMIC_LEVERAGE': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'FINANCING_OPTIMIZATION': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'MARGIN_CALL': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'DYNAMIC_CORRELATION': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'COINTEGRATION': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'RISK_CONTRIBUTION': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'HIERARCHICAL_RISK': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'SIMPLIFIED_RISK': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'BARRA_RISK': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'RISK_ATTRIBUTION': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'STRESS_TESTING': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'SIMPLIFIED_TIMEFRAME': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'MULTI_STRATEGY': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'STRATEGY_PORTFOLIO': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'PORTFOLIO_PERFORMANCE': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'PORTFOLIO_ATTRIBUTION': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'PORTFOLIO_CONSTRAINT': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'PORTFOLIO_SCENARIO': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'PORTFOLIO_OPTIMIZER': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'PORTFOLIO_REBALANCING': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'TRANSACTION_COST_AWARE': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'RL_REBALANCING': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'QUARTERLY_REBALANCE': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'VAR_ES': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'MEAN_VARIANCE': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'FACTOR_NEUTRAL': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'ROBUST_OPTIMIZATION': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'TAX_LOSS': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'TURNOVER_CONTROL': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        'LIQUIDITY_CONSTRAINED': 'Layer 6 (组合优化层) | 业务架构: 三级时间框架融合架构',
        
        # Layer 7 - 风险控制层
        'REALTIME_RISK_HEDGE': 'Layer 7 (风险控制层) | 业务架构: 三级时间框架融合架构',
        'TAIL_RISK': 'Layer 7 (风险控制层) | 业务架构: 三级时间框架融合架构',
        
        # Layer 9 - AI增强层
        'AI_PATTERN': 'Layer 9 (AI增强层) | 业务架构: 三级时间框架融合架构',
        'AI_ENHANCEMENT': 'Layer 9 (AI增强层) | 业务架构: 三级时间框架融合架构',
        
        # 其他
        'FACTOR_BACKTEST': 'Layer 0 (系统架构) | 业务架构: 三级时间框架融合架构',
        'ALTERNATIVE_DATA': 'Layer 0 (系统架构) | 业务架构: 三级时间框架融合架构',
        'ECONOMIC_REGIME': 'Layer 0 (系统架构) | 业务架构: 三级时间框架融合架构',
        'STRATEGY_SELECTION': 'Layer 0 (系统架构) | 业务架构: 三级时间框架融合架构',
        'MODULE_RESPONSIBILITY': 'Layer 0 (系统架构) | 业务架构: 三级时间框架融合架构',
        'SYSTEM_INTEGRATION': 'Layer 0 (系统架构) | 业务架构: 三级时间框架融合架构',
        'SYSTEM_ENHANCEMENT': 'Layer 0 (系统架构) | 业务架构: 三级时间框架融合架构',
        'MARKET_PARTICIPANT': 'Layer 0 (系统架构) | 业务架构: 三级时间框架融合架构',
        'MARKET_REGIME': 'Layer 0 (系统架构) | 业务架构: 三级时间框架融合架构',
        'ALPHA_FACTOR': 'Layer 0 (系统架构) | 业务架构: 三级时间框架融合架构',
        'MONITORING_DASHBOARD': 'Layer 0 (系统架构) | 业务架构: 三级时间框架融合架构',
        'STRATEGIC_ALLOCATION': 'Layer 0 (系统架构) | 业务架构: 三级时间框架融合架构',
    }
    
    for keyword, layer in layer_keywords.items():
        if keyword in filename.upper():
            return layer
    
    return 'Layer 0 (系统架构) | 业务架构: 三级时间框架融合架构'


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


def add_layer_to_yaml(content: str, layer: str) -> str:
    """在YAML头部添加layer字段"""
    # 检查是否已有layer字段
    if re.search(r'^layer:', content, re.MULTILINE):
        # 更新现有layer字段
        content = re.sub(
            r'^layer:.*$',
            f"layer: '{layer}'",
            content,
            flags=re.MULTILINE
        )
    else:
        # 在YAML头部添加layer字段
        # 找到第一个YAML分隔符后的位置
        yaml_end = content.find('\n---\n')
        if yaml_end > 0:
            # 在YAML结束前添加layer字段
            content = content[:yaml_end] + f"\nlayer: '{layer}'" + content[yaml_end:]
    
    return content


def fix_layer_positioning():
    """修复Layer定位"""
    print("="*80)
    print("批量修复Layer定位")
    print("="*80)
    
    fixed_count = 0
    skipped_count = 0
    error_count = 0
    
    for filepath in BLUEPRINTS_DIR.glob("*.md"):
        if filepath.name == "INDEX.md":
            continue
        
        try:
            content = read_document(filepath)
            yaml_header = extract_yaml_header(content)
            
            # 检查是否需要修复
            current_layer = yaml_header.get('layer', '')
            
            if not current_layer or current_layer == 'Unknown':
                # 推断Layer
                inferred_layer = infer_layer_from_filename(filepath.name)
                
                # 添加layer字段
                new_content = add_layer_to_yaml(content, inferred_layer)
                
                # 保存文件
                with open(filepath, 'w', encoding='utf-8-sig') as f:
                    f.write(new_content)
                
                fixed_count += 1
                print(f"✅ {filepath.name}: {inferred_layer}")
            else:
                skipped_count += 1
        
        except Exception as e:
            error_count += 1
            print(f"❌ {filepath.name}: {e}")
    
    print("\n" + "="*80)
    print("修复统计")
    print("="*80)
    print(f"已修复: {fixed_count}")
    print(f"已跳过: {skipped_count}")
    print(f"错误数: {error_count}")
    
    return fixed_count, skipped_count, error_count


if __name__ == "__main__":
    fix_layer_positioning()
