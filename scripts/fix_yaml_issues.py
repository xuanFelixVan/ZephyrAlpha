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
        # 模式：---\n...旧YAML...\n---\n\n\ufeff\ufeff---\n...新YAML...\n---
        double_yaml_pattern = r'^---[\r\n]+(.*?)[\r\n]+---[\r\n\s]+\ufeff\ufeff---[\r\n]+(.*?)[\r\n]+---'
        match = re.search(double_yaml_pattern, content, re.DOTALL)
        
        if match:
            # 保留第二个YAML头部，清理BOM字符
            second_yaml = match.group(2)
            
            # 修复responsibility字段中的格式错误
            # 移除单独的 - 和 ? 行
            second_yaml = re.sub(r'^-\s*[\r\n]+', '', second_yaml, flags=re.MULTILINE)
            second_yaml = re.sub(r'^\?\s*[\r\n]+', '', second_yaml, flags=re.MULTILINE)
            
            # 构建新内容
            new_content = '---\n' + second_yaml + '---' + content[match.end():]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            fixed_files.append(file)
            print(f'Fixed: {file}')
            continue
        
        # 检查是否有BOM字符开头的YAML
        bom_pattern = r'^\ufeff\ufeff---[\r\n]+(.*?)[\r\n]+---'
        match = re.search(bom_pattern, content, re.DOTALL)
        
        if match:
            yaml_content = match.group(1)
            
            # 修复responsibility字段中的格式错误
            yaml_content = re.sub(r'^-\s*[\r\n]+', '', yaml_content, flags=re.MULTILINE)
            yaml_content = re.sub(r'^\?\s*[\r\n]+', '', yaml_content, flags=re.MULTILINE)
            
            new_content = '---\n' + yaml_content + '---' + content[match.end():]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            fixed_files.append(file)
            print(f'Fixed BOM: {file}')

print(f'\nTotal fixed: {len(fixed_files)} files')
