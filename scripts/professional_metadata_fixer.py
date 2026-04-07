#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
专业蓝图文件治理 - 元数据修复
修复缺失的module_id、responsibility、title
"""

import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

def extract_title(content):
    """从文档内容提取标题"""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def generate_module_id(file_path):
    """生成module_id"""
    rel_path = file_path.relative_to(FACTOR_LIBRARY)
    parts = list(rel_path.parts)
    
    # 移除.md后缀
    if parts:
        parts[-1] = Path(parts[-1]).stem
    
    # 转换为大写并替换特殊字符
    module_id = '_'.join(parts).upper()
    module_id = re.sub(r'[^A-Z0-9_]', '_', module_id)
    module_id = re.sub(r'_+', '_', module_id)
    
    return f"FACTOR_LIBRARY_{module_id}"

def generate_responsibility(file_path):
    """生成responsibility"""
    rel_path = file_path.relative_to(FACTOR_LIBRARY)
    parts = list(rel_path.parts)
    
    if len(parts) > 1:
        dir_name = parts[-2] if len(parts) > 1 else parts[0]
        file_name = Path(parts[-1]).stem
        return f"{dir_name}目录{file_name}文档"
    else:
        file_name = Path(parts[0]).stem
        return f"因子库{file_name}文档"

def fix_metadata(file_path):
    """修复文档元数据"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 检查是否有YAML头部
        yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        
        if yaml_match:
            yaml_content = yaml_match.group(1)
            body_content = content[yaml_match.end():]
            
            # 解析YAML
            yaml_dict = {}
            for line in yaml_content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    yaml_dict[key.strip()] = value.strip()
            
            # 检查缺失的字段
            needs_fix = False
            
            if 'module_id' not in yaml_dict or not yaml_dict['module_id']:
                yaml_dict['module_id'] = generate_module_id(file_path)
                needs_fix = True
            
            if 'responsibility' not in yaml_dict:
                yaml_dict['responsibility'] = generate_responsibility(file_path)
                needs_fix = True
            
            # 检查标题
            title = extract_title(body_content)
            if not title:
                # 添加标题
                file_stem = file_path.stem
                body_content = f"# {file_stem}\n\n{body_content}"
                needs_fix = True
            
            if needs_fix:
                # 重建YAML
                yaml_lines = ['---']
                for key, value in yaml_dict.items():
                    if key == 'responsibility':
                        yaml_lines.append(f'{key}:')
                        yaml_lines.append(f'  - {value}')
                    else:
                        yaml_lines.append(f'{key}: {value}')
                yaml_lines.append('---')
                
                new_content = '\n'.join(yaml_lines) + '\n\n' + body_content
                
                # 写入文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                return True
        
        else:
            # 没有YAML头部，创建新的
            module_id = generate_module_id(file_path)
            responsibility = generate_responsibility(file_path)
            title = extract_title(content)
            
            if not title:
                file_stem = file_path.stem
                content = f"# {file_stem}\n\n{content}"
            
            yaml_content = f"""---
module_id: {module_id}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 文档管理团队
responsibility:
  - {responsibility}
---

"""
            
            new_content = yaml_content + content
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
        
        return False
    
    except Exception as e:
        print(f"错误: {file_path.relative_to(FACTOR_LIBRARY)}")
        print(f"  {e}")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("专业蓝图文件治理 - 元数据修复")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    fixed_count = 0
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        if fix_metadata(file_path):
            rel_path = file_path.relative_to(FACTOR_LIBRARY)
            print(f"\n修复: {rel_path}")
            fixed_count += 1
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
    print(f"修复文件: {fixed_count}")

if __name__ == '__main__':
    main()
