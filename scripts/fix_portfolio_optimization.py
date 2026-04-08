import os

file_path = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS\PORTFOLIO_OPTIMIZATION_BLUEPRINT.md'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到YAML头部结束位置
yaml_end = content.find('---', 3)
if yaml_end == -1:
    print("Cannot find YAML end")
else:
    yaml_content = content[4:yaml_end]
    
    # 检查是否已经有responsibility
    if 'responsibility:' in yaml_content:
        print("Already has responsibility")
    else:
        # 添加responsibility字段
        new_yaml = '''---
module_id: PORTFOLIO_OPTIMIZATION_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
standard_type: 专业量化机构蓝图
compliance_level: 专业标准
responsibility:
  - 投资组合优化框架
  - 优化流程协调
  - 优化结果整合
  - 多目标优化支持
layer: Layer 5.2 (组合优化)
---'''
        
        # 替换YAML头部
        new_content = new_yaml + content[yaml_end+3:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("Fixed PORTFOLIO_OPTIMIZATION_BLUEPRINT.md")
