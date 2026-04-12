# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import re

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'

fixed_files = []

def find_best_yaml(yaml_blocks):
    """找到最完整的YAML块"""
    best_yaml = None
    best_score = 0
    
    for yaml_content in yaml_blocks:
        score = 0
        # 检查关键字段
        if 'module_id:' in yaml_content and '_001' in yaml_content:
            score += 10
        if 'responsibility:' in yaml_content:
            score += 5
        if 'created_date:' in yaml_content:
            score += 3
        if 'last_updated:' in yaml_content:
            score += 3
        if 'owner:' in yaml_content:
            score += 2
        if 'standard_type:' in yaml_content:
            score += 2
        if 'compliance_level:' in yaml_content:
            score += 2
        if 'layer:' in yaml_content:
            score += 2
        
        if score > best_score:
            best_score = score
            best_yaml = yaml_content
    
    return best_yaml

for file in os.listdir(blueprints_dir):
    if file.endswith('.md') and 'BLUEPRINT' in file:
        file_path = os.path.join(blueprints_dir, file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找所有YAML块
        yaml_pattern = r'---[\r\n\s]*(.*?)[\r\n\s]*---'
        matches = list(re.finditer(yaml_pattern, content, re.DOTALL))
        
        if len(matches) > 1:
            # 提取所有YAML块
            yaml_blocks = [m.group(1) for m in matches]
            
            # 找到最完整的YAML
            best_yaml = find_best_yaml(yaml_blocks)
            
            if best_yaml:
                # 清理YAML内容
                # 移除BOM字符
                best_yaml = best_yaml.replace('\ufeff', '')
                
                # 修复responsibility字段
                # 如果responsibility为空，添加默认值
                if re.search(r'responsibility:\s*[\r\n]', best_yaml):
                    # 检查下一行是否是layer或其他字段
                    if re.search(r'responsibility:\s*[\r\n]+layer:', best_yaml):
                        # responsibility为空，需要添加默认值
                        pass
                
                # 移除单独的 - 和 ? 行
                best_yaml = re.sub(r'^-\s*[\r\n]+', '', best_yaml, flags=re.MULTILINE)
                best_yaml = re.sub(r'^\?\s*[\r\n]+', '', best_yaml, flags=re.MULTILINE)
                
                # 获取最后一个YAML块之后的内容
                last_match = matches[-1]
                rest_content = content[last_match.end():]
                
                # 构建新内容
                new_content = '---\n' + best_yaml.strip() + '\n---' + rest_content
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                fixed_files.append(file)
                print(f'Fixed multi-YAML: {file}')

print(f'\nTotal fixed: {len(fixed_files)} files')
