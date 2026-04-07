import os
import re

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'

fixed_files = []

for file in os.listdir(blueprints_dir):
    if file.endswith('.md') and 'BLUEPRINT' in file:
        file_path = os.path.join(blueprints_dir, file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 清理YAML头部后面的表格片段
        # 模式：layer: ... \n-----| ... | ... \n\n---
        content = re.sub(
            r'(layer:.*?)[\r\n]+-----\|.*?\|.*?[\r\n\s]+---',
            r'\1\n---',
            content,
            flags=re.DOTALL
        )
        
        # 清理YAML头部后面的多余表格行
        content = re.sub(
            r'(layer:.*?)[\r\n]+\|.*?\|.*?[\r\n]+---',
            r'\1\n---',
            content,
            flags=re.DOTALL
        )
        
        # 清理YAML头部后面的损坏内容
        # 模式：layer: ... \n损坏内容 \n---
        content = re.sub(
            r'(layer:\s*Layer\s*[\d\.]+\s*\(.*?\))[\r\n]+(?!>|\#|\-)(.*?)[\r\n]+---',
            r'\1\n---',
            content,
            flags=re.DOTALL
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            fixed_files.append(file)
            print(f'Cleaned: {file}')

print(f'\nTotal fixed: {len(fixed_files)} files')
