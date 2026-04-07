import os
import re

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'

file_path = os.path.join(blueprints_dir, 'MULTI_STRATEGY_HIERARCHICAL_SYSTEM_BLUEPRINT.md')

with open(file_path, 'r', encoding='utf-8-sig') as f:
    content = f.read()

content = content.replace('\ufeff', '')

yaml_delimiters = []
for match in re.finditer(r'^---', content, re.MULTILINE):
    yaml_delimiters.append(match.start())

print(f"检测到{len(yaml_delimiters)}个YAML分隔符")

if len(yaml_delimiters) >= 4:
    second_yaml_start = yaml_delimiters[2]
    new_content = content[second_yaml_start:]
    
    yaml_match = re.search(r'^---[\r\n]+(.*?)^---[\r\n]+', new_content, re.MULTILINE | re.DOTALL)
    if yaml_match:
        yaml_content = yaml_match.group(1)
        
        yaml_content = re.sub(r'layer:\s*.*?[\r\n]+', 'layer: Layer 6 (组合优化层)\n', yaml_content)
        
        if 'standard_type:' not in yaml_content:
            yaml_content += 'standard_type: 专业量化机构蓝图\n'
        if 'compliance_level:' not in yaml_content:
            yaml_content += 'compliance_level: 专业标准\n'
        
        if 'responsibility:' in yaml_content:
            yaml_content = re.sub(
                r'responsibility:\s*[\r\n]+(\s+-.*?[\r\n]+)+',
                'responsibility:\n  - 多策略分层系统\n  - 策略绩效评估\n  - 策略权重分配\n  - 信号融合\n  - 策略协调优化\n',
                yaml_content
            )
        
        new_content = '---\n' + yaml_content + '---\n\n' + new_content[yaml_match.end():]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"修复完成: {file_path}")
    else:
        print("未找到YAML内容")
else:
    print("YAML分隔符数量不足")
