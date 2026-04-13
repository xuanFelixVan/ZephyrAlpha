# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
Layer定位检查与修复脚本
用途：检查并修复文档的Layer定位问题
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

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


def extract_title(content: str) -> str:
    """提取文档标题"""
    match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    return match.group(1).strip() if match else ""


def infer_layer_from_filename(filename: str) -> Tuple[int, str]:
    """从文件名推断Layer"""
    layer_keywords = {
        # Layer 1 - 数据预处理层
        'DATA_QUALITY': (1, '数据预处理层'),
        'DATA_CATALOG': (1, '数据预处理层'),
        'DATA_MESH': (1, '数据预处理层'),
        'DATA_FABRIC': (1, '数据预处理层'),
        'DATA_GOVERNANCE': (1, '数据预处理层'),
        'DATA_LIFECYCLE': (1, '数据预处理层'),
        'DATA_SOURCE': (1, '数据预处理层'),
        'DATA_SECURITY': (1, '数据预处理层'),
        'DATA_VERSION': (1, '数据预处理层'),
        'DATA_COST': (1, '数据预处理层'),
        'DATA_OBSERVABILITY': (1, '数据预处理层'),
        'REALTIME_DATA': (1, '数据预处理层'),
        'HIGH_PERFORMANCE_DATA': (1, '数据预处理层'),
        'QUALITY_SCORING': (1, '数据预处理层'),
        'QUALITY_REPORT': (1, '数据预处理层'),
        'AUTO_REPAIR': (1, '数据预处理层'),
        'ENHANCED_ALERT': (1, '数据预处理层'),
        'UNIFIED_DATA': (1, '数据预处理层'),
        
        # Layer 1 - 微观执行层
        'INTRADAY_STRATEGY': (1, '微观执行层'),
        'OPENING_STRATEGY': (1, '微观执行层'),
        'RISK_CONTROL': (1, '微观执行层'),
        
        # Layer 5 - 策略执行层
        'SMART_EXECUTION': (5, '策略执行层'),
        'MARKET_IMPACT': (5, '策略执行层'),
        'TRADING_COST': (5, '策略执行层'),
        'LIQUIDITY_MANAGEMENT': (5, '策略执行层'),
        'STATISTICAL_ARBITRAGE': (5, '策略执行层'),
        'SMART_ORDER_ROUTER': (5, '策略执行层'),
        'TRADING_SIGNAL': (5, '策略执行层'),
        'ALGORITHMIC_TRADING': (5, '策略执行层'),
        'TRANSACTION_COST_ANALYSIS': (5, '策略执行层'),
        'EXECUTION_STRATEGY': (5, '策略执行层'),
        'STRATEGIC_WEIGHTING': (5, '策略执行层'),
        
        # Layer 6 - 组合优化层
        'MULTI_ASSET': (6, '组合优化层'),
        'PORTFOLIO_INSURANCE': (6, '组合优化层'),
        'BLACK_LITTERMAN': (6, '组合优化层'),
        'RISK_PARITY': (6, '组合优化层'),
        'MULTI_OBJECTIVE': (6, '组合优化层'),
        'CONSTRAINT_SOLVER': (6, '组合优化层'),
        'DYNAMIC_LEVERAGE': (6, '组合优化层'),
        'FINANCING_OPTIMIZATION': (6, '组合优化层'),
        'MARGIN_CALL': (6, '组合优化层'),
        'DYNAMIC_CORRELATION': (6, '组合优化层'),
        'COINTEGRATION': (6, '组合优化层'),
        'RISK_CONTRIBUTION': (6, '组合优化层'),
        'HIERARCHICAL_RISK': (6, '组合优化层'),
        'SIMPLIFIED_RISK': (6, '组合优化层'),
        'BARRA_RISK': (6, '组合优化层'),
        'RISK_ATTRIBUTION': (6, '组合优化层'),
        'STRESS_TESTING': (6, '组合优化层'),
        'SIMPLIFIED_TIMEFRAME': (6, '组合优化层'),
        'MULTI_STRATEGY': (6, '组合优化层'),
        'STRATEGY_PORTFOLIO': (6, '组合优化层'),
        'PORTFOLIO_PERFORMANCE': (6, '组合优化层'),
        'PORTFOLIO_ATTRIBUTION': (6, '组合优化层'),
        'PORTFOLIO_CONSTRAINT': (6, '组合优化层'),
        'PORTFOLIO_SCENARIO': (6, '组合优化层'),
        'PORTFOLIO_OPTIMIZER': (6, '组合优化层'),
        'PORTFOLIO_REBALANCING': (6, '组合优化层'),
        'TRANSACTION_COST_AWARE': (6, '组合优化层'),
        'RL_REBALANCING': (6, '组合优化层'),
        'QUARTERLY_REBALANCE': (6, '组合优化层'),
        'VAR_ES': (6, '组合优化层'),
        'MEAN_VARIANCE': (6, '组合优化层'),
        'FACTOR_NEUTRAL': (6, '组合优化层'),
        'ROBUST_OPTIMIZATION': (6, '组合优化层'),
        'TAX_LOSS': (6, '组合优化层'),
        'TURNOVER_CONTROL': (6, '组合优化层'),
        'LIQUIDITY_CONSTRAINED': (6, '组合优化层'),
        
        # Layer 7 - 风险控制层
        'REALTIME_RISK_HEDGE': (7, '风险控制层'),
        'TAIL_RISK': (7, '风险控制层'),
        
        # Layer 9 - AI增强层
        'AI_PATTERN': (9, 'AI增强层'),
        'AI_ENHANCEMENT': (9, 'AI增强层'),
        
        # 其他
        'FACTOR_BACKTEST': (0, '其他'),
        'ALTERNATIVE_DATA': (0, '其他'),
        'ECONOMIC_REGIME': (0, '其他'),
        'STRATEGY_SELECTION': (0, '其他'),
        'MODULE_RESPONSIBILITY': (0, '其他'),
        'SYSTEM_INTEGRATION': (0, '其他'),
        'SYSTEM_ENHANCEMENT': (0, '其他'),
        'MARKET_PARTICIPANT': (0, '其他'),
        'MARKET_REGIME': (0, '其他'),
        'ALPHA_FACTOR': (0, '其他'),
        'MONITORING_DASHBOARD': (0, '其他'),
        'STRATEGIC_ALLOCATION': (0, '其他'),
    }
    
    for keyword, (layer_num, layer_name) in layer_keywords.items():
        if keyword in filename.upper():
            return (layer_num, layer_name)
    
    return (0, 'Unknown')


def check_layer_positioning():
    """检查Layer定位"""
    print("="*80)
    print("Layer定位检查")
    print("="*80)
    
    issues = []
    correct_count = 0
    unknown_count = 0
    
    for filepath in BLUEPRINTS_DIR.glob("*.md"):
        if filepath.name == "INDEX.md":
            continue
        
        content = read_document(filepath)
        yaml_header = extract_yaml_header(content)
        title = extract_title(content)
        
        current_layer = yaml_header.get('layer', '')
        inferred_layer_num, inferred_layer_name = infer_layer_from_filename(filepath.name)
        
        # 检查是否有明确的Layer定位
        if not current_layer or current_layer == 'Unknown':
            unknown_count += 1
            issues.append({
                "filename": filepath.name,
                "title": title,
                "current_layer": current_layer or "缺失",
                "inferred_layer": f"Layer {inferred_layer_num} ({inferred_layer_name})",
                "action": "需要补充Layer定位"
            })
        else:
            # 检查Layer定位是否合理
            current_layer_num, _ = extract_layer_number(current_layer)
            
            if current_layer_num == inferred_layer_num or inferred_layer_num == 0:
                correct_count += 1
            else:
                issues.append({
                    "filename": filepath.name,
                    "title": title,
                    "current_layer": current_layer,
                    "inferred_layer": f"Layer {inferred_layer_num} ({inferred_layer_name})",
                    "action": "Layer定位可能不准确"
                })
    
    print(f"\n总文档数: {correct_count + unknown_count + len([i for i in issues if i['action'] != '需要补充Layer定位'])}")
    print(f"Layer定位正确: {correct_count}")
    print(f"Layer定位缺失: {unknown_count}")
    print(f"Layer定位可能不准确: {len([i for i in issues if i['action'] != '需要补充Layer定位'])}")
    
    if issues:
        print(f"\n发现 {len(issues)} 个Layer定位问题:\n")
        
        # 按问题类型分组
        missing_layer = [i for i in issues if i['action'] == '需要补充Layer定位']
        incorrect_layer = [i for i in issues if i['action'] != '需要补充Layer定位']
        
        if missing_layer:
            print("="*80)
            print(f"Layer定位缺失 ({len(missing_layer)}个)")
            print("="*80)
            print("\n| 文档名称 | 推断Layer |")
            print("|----------|-----------|")
            for issue in missing_layer[:20]:
                print(f"| {issue['filename']} | {issue['inferred_layer']} |")
            if len(missing_layer) > 20:
                print(f"| ... | 还有 {len(missing_layer) - 20} 个 |")
        
        if incorrect_layer:
            print("\n" + "="*80)
            print(f"Layer定位可能不准确 ({len(incorrect_layer)}个)")
            print("="*80)
            print("\n| 文档名称 | 当前Layer | 推断Layer |")
            print("|----------|-----------|-----------|")
            for issue in incorrect_layer[:20]:
                print(f"| {issue['filename']} | {issue['current_layer']} | {issue['inferred_layer']} |")
            if len(incorrect_layer) > 20:
                print(f"| ... | ... | 还有 {len(incorrect_layer) - 20} 个 |")
    
    return issues


def extract_layer_number(layer_str: str) -> Tuple[int, str]:
    """从layer字段提取层级编号"""
    if not layer_str:
        return (0, "Unknown")
    
    match = re.search(r'Layer\s*(\d+)', layer_str, re.IGNORECASE)
    if match:
        return (int(match.group(1)), layer_str)
    
    return (0, layer_str)


def generate_fix_commands(issues: List[Dict]):
    """生成修复命令"""
    if not issues:
        return
    
    print("\n" + "="*80)
    print("修复建议")
    print("="*80)
    
    missing_layer = [i for i in issues if i['action'] == '需要补充Layer定位']
    
    if missing_layer:
        print(f"\n需要补充Layer定位的文档: {len(missing_layer)}个")
        print("\n建议使用以下脚本批量修复:")
        print("\n```python")
        print("# 批量添加Layer定位")
        print("import re")
        print("from pathlib import Path")
        print()
        print("BLUEPRINTS_DIR = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS')")
        print()
        print("fixes = {")
        for issue in missing_layer[:10]:
            layer_num = issue['inferred_layer'].split()[1]
            layer_name = issue['inferred_layer'].split('(')[1].rstrip(')')
            print(f"    '{issue['filename']}': 'Layer {layer_num} ({layer_name})',")
        if len(missing_layer) > 10:
            print(f"    # ... 还有 {len(missing_layer) - 10} 个")
        print("}")
        print()
        print("for filename, layer in fixes.items():")
        print("    filepath = BLUEPRINTS_DIR / filename")
        print("    with open(filepath, 'r', encoding='utf-8-sig') as f:")
        print("        content = f.read()")
        print("    # 在YAML头部添加layer字段")
        print("    # ...")
        print("```")


if __name__ == "__main__":
    issues = check_layer_positioning()
    generate_fix_commands(issues)
