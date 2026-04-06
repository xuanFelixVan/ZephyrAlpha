#!/usr/bin/env python3
"""
修复BLUEPRINT.md的双YAML头部问题
"""
import re

def fix_blueprint():
    file_path = r'd:\ZephyrAlpha\docs\09_RESEARCH_INNOVATION\BLUEPRINT.md'
    
    # 读取文件
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # 查找所有YAML头部
    yaml_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    matches = list(re.finditer(yaml_pattern, content, re.MULTILINE | re.DOTALL))
    
    print(f"找到 {len(matches)} 个YAML头部")
    
    if len(matches) >= 2:
        # 删除第一个YAML头部
        first_match = matches[0]
        new_content = content[first_match.end():]
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ 已删除第一个YAML头部")
        print(f"保留的YAML头部:\n{matches[1].group(1)[:200]}...")
    else:
        print("⚠️ 未找到两个YAML头部，无需修复")

if __name__ == '__main__':
    fix_blueprint()
