import os
import re

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'

fixed_files = []

for file in os.listdir(blueprints_dir):
    if file.endswith('.md') and 'BLUEPRINT' in file:
        file_path = os.path.join(blueprints_dir, file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有双YAML头部
        yaml_pattern = r'^---[\r\n\s]*(.*?)[\r\n\s]*---[\r\n\s]*---[\r\n\s]*(.*?)[\r\n\s]*---'
        match = re.search(yaml_pattern, content, re.DOTALL)
        
        if match:
            # 保留第二个YAML头部
            second_yaml = match.group(2)
            
            # 检查第二个YAML是否包含module_id
            if 'module_id:' in second_yaml:
                # 移除第一个YAML头部，保留第二个
                new_content = '---\n' + second_yaml + '---' + content[match.end():]
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                fixed_files.append(file)
                print(f'Fixed: {file}')

print(f'\nTotal fixed: {len(fixed_files)} files')
