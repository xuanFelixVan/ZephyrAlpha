import os

blueprints_dir = 'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS'

files_to_fix = [
    'SMART_EXECUTION_ENGINE_BLUEPRINT.md',
    'MARKET_IMPACT_MODEL_BLUEPRINT.md',
    'AI_PATTERN_RECOGNITION_ENGINE_BLUEPRINT.md',
    'REALTIME_RISK_HEDGE_ENGINE_BLUEPRINT.md',
    'LIQUIDITY_MANAGEMENT_SYSTEM_BLUEPRINT.md',
    'ECONOMIC_REGIME_ENGINE_BLUEPRINT.md',
    'STRATEGIC_WEIGHTING_BLUEPRINT.md',
    'QUARTERLY_REBALANCE_BLUEPRINT.md',
]

replacements = [
    ("layer: 'Layer 5 (微观执行层)", "layer: 'Layer 5 (策略执行层)"),
    ("layer: 'Layer 5 (中观策略层)", "layer: 'Layer 5 (策略执行层)"),
    ("layer: 'Layer 5 (宏观配置层)", "layer: 'Layer 5 (策略执行层)"),
]

fixed_count = 0

for filename in files_to_fix:
    filepath = os.path.join(blueprints_dir, filename)
    
    if not os.path.exists(filepath):
        print(f'文件不存在: {filename}')
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    for old, new in replacements:
        content = content.replace(old, new)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'已修复: {filename}')
        fixed_count += 1
    else:
        print(f'无需修复: {filename}')

print(f'\n总计修复 {fixed_count} 个文件')
