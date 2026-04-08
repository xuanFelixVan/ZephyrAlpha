import os
import re

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'

responsibility_additions = {
    'MULTI_ASSET_ALLOCATION_BLUEPRINT.md': [
        '多资产配置',
        '跨资产优化',
        '资产相关性建模'
    ],
    'PORTFOLIO_DIVERSIFICATION_METRIC_BLUEPRINT.md': [
        '分散度度量',
        '风险分散评估',
        '集中度分析'
    ],
    'PORTFOLIO_SCENARIO_ANALYSIS_BLUEPRINT.md': [
        '情景分析',
        '压力测试',
        '情景归因'
    ],
    'ROBUST_OPTIMIZATION_BLUEPRINT.md': [
        '鲁棒优化',
        '不确定性建模',
        '鲁棒解求解'
    ]
}

fixed_files = []

for file, items in responsibility_additions.items():
    file_path = os.path.join(blueprints_dir, file)
    
    if not os.path.exists(file_path):
        print(f'File not found: {file}')
        continue
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已有responsibility字段
    resp_match = re.search(r'responsibility:\s*\n((?:\s+-\s+.+\n?)+)', content)
    
    if resp_match:
        # 提取现有职责项
        resp_text = resp_match.group(1)
        existing_items = re.findall(r'-\s+(.+)', resp_text)
        existing_items = [item.strip() for item in existing_items if item.strip()]
        
        # 添加缺失的职责项
        new_items = [item for item in items if item not in existing_items]
        
        if new_items:
            # 构建新的responsibility内容
            all_items = existing_items + new_items
            new_resp_content = 'responsibility:\n' + '\n'.join([f'  - {item}' for item in all_items]) + '\n'
            
            # 替换旧的responsibility内容
            new_content = content[:resp_match.start()] + new_resp_content + content[resp_match.end():]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            fixed_files.append(file)
            print(f'Added {len(new_items)} items to {file}: {new_items}')
    else:
        # 添加新的responsibility字段
        # 在layer字段之前添加
        layer_match = re.search(r'layer:', content)
        if layer_match:
            new_resp_content = 'responsibility:\n' + '\n'.join([f'  - {item}' for item in items]) + '\n'
            new_content = content[:layer_match.start()] + new_resp_content + content[layer_match.start():]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            fixed_files.append(file)
            print(f'Added responsibility field to {file}')

print(f'\nTotal fixed: {len(fixed_files)} files')
