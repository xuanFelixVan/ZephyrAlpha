#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
综合修复剩余问题
"""

import re
import json
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

# 已删除的文件列表
DELETED_FILES = [
    '01_STANDARDS/factor_neutralization.md',
    '01_STANDARDS/factor_preprocessing.md',
    '01_STANDARDS/factor_return_analysis.md',
    '01_STANDARDS/factor_synthesis.md',
    '01_STANDARDS/ic_analysis.md',
    '01_STANDARDS/FACTOR_SCREENING_STRATEGY.md',
    '01_STANDARDS/FACTOR_VALIDATION_GUIDE.md',
    '04_DATA_SOURCE/IFIND_CONNECTOR.md',
    '04_DATA_SOURCE/SUPERCMD_CONNECTOR.md',
    '05_BACKTEST/OVERFITTING_TEST.md',
]

def fix_invalid_links():
    """修复无效链接"""
    print("=" * 80)
    print("修复无效链接")
    print("=" * 80)
    
    fixed_count = 0
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            original_content = content
            rel_path = file_path.relative_to(FACTOR_LIBRARY)
            
            # 检查并移除指向已删除文件的链接
            for deleted_file in DELETED_FILES:
                deleted_name = Path(deleted_file).stem
                
                # 匹配各种链接格式
                patterns = [
                    rf'\[([^\]]*)\]\([^)]*{deleted_name}[^)]*\)',
                    rf'\|\s*\[([^\]]*)\]\([^)]*{deleted_name}[^)]*\)\s*\|',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        # 移除链接，保留文本
                        content = re.sub(pattern, r'\1', content)
                        print(f"\n{rel_path}")
                        print(f"  移除链接: {deleted_name}")
                        fixed_count += 1
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
        
        except Exception as e:
            print(f"  错误: {e}")
    
    print(f"\n修复链接: {fixed_count}")
    return fixed_count

def fix_missing_metadata():
    """补充缺失的元数据"""
    print("\n" + "=" * 80)
    print("补充缺失的元数据")
    print("=" * 80)
    
    fixed_count = 0
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            rel_path = file_path.relative_to(FACTOR_LIBRARY)
            
            # 检查是否有YAML头部
            if not content.startswith('---'):
                continue
            
            # 提取YAML头部
            yaml_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if not yaml_match:
                continue
            
            yaml_content = yaml_match.group(1)
            
            # 检查是否缺少module_id
            if 'module_id:' not in yaml_content:
                # 生成module_id
                parts = rel_path.parts[:-1]
                file_name = file_path.stem
                
                if not parts:
                    module_id = f"FACTOR_LIBRARY_{file_name.upper()}"
                else:
                    clean_parts = [re.sub(r'^\d+_', '', p).upper() for p in parts]
                    module_id = '_'.join(clean_parts) + f"_{file_name.upper()}"
                
                module_id = re.sub(r'[^A-Z0-9_]', '_', module_id)
                module_id = re.sub(r'_+', '_', module_id).strip('_')
                
                # 在YAML头部添加module_id
                new_yaml = f"module_id: {module_id}\n" + yaml_content
                new_content = content.replace(yaml_content, new_yaml)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"\n{rel_path}")
                print(f"  添加module_id: {module_id}")
                fixed_count += 1
        
        except Exception as e:
            print(f"  错误: {e}")
    
    print(f"\n补充元数据: {fixed_count}")
    return fixed_count

def fix_missing_responsibility():
    """补充缺失的职责描述"""
    print("\n" + "=" * 80)
    print("补充缺失的职责描述")
    print("=" * 80)
    
    fixed_count = 0
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            rel_path = file_path.relative_to(FACTOR_LIBRARY)
            
            # 检查是否有YAML头部
            if not content.startswith('---'):
                continue
            
            # 检查是否缺少responsibility
            if 'responsibility:' in content:
                continue
            
            # 提取标题
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else file_path.stem
            
            # 生成职责描述
            parts = rel_path.parts[:-1]
            file_name = file_path.stem
            
            if file_name.upper() == 'INDEX':
                responsibility = f"{parts[-1] if parts else '因子库'}目录索引与导航"
            elif file_name.upper() == 'README':
                responsibility = f"{parts[-1] if parts else '因子库'}模块说明"
            else:
                clean_title = re.sub(r'\s*(文档|指南|标准|规范|系统|框架|模块|组件|工具|接口|连接器|蓝图)$', '', title)
                responsibility = f"{clean_title}相关文档"
            
            # 在YAML头部添加responsibility
            yaml_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
                new_yaml = yaml_content + f"\nresponsibility:\n  - {responsibility}"
                new_content = content.replace(yaml_content, new_yaml)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"\n{rel_path}")
                print(f"  添加职责: {responsibility}")
                fixed_count += 1
        
        except Exception as e:
            print(f"  错误: {e}")
    
    print(f"\n补充职责描述: {fixed_count}")
    return fixed_count

def fix_missing_title():
    """补充缺失的标题"""
    print("\n" + "=" * 80)
    print("补充缺失的标题")
    print("=" * 80)
    
    fixed_count = 0
    
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            rel_path = file_path.relative_to(FACTOR_LIBRARY)
            
            # 检查是否有标题
            if re.search(r'^#\s+.+$', content, re.MULTILINE):
                continue
            
            # 生成标题
            file_name = file_path.stem
            title = file_name.replace('_', ' ').replace('-', ' ')
            title = ' '.join(word.capitalize() for word in title.split())
            
            # 在YAML头部后添加标题
            if content.startswith('---'):
                yaml_end = content.find('---', 3)
                if yaml_end > 0:
                    new_content = content[:yaml_end + 3] + f'\n\n# {title}\n' + content[yaml_end + 3:]
                else:
                    new_content = f'# {title}\n\n' + content
            else:
                new_content = f'# {title}\n\n' + content
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"\n{rel_path}")
            print(f"  添加标题: {title}")
            fixed_count += 1
        
        except Exception as e:
            print(f"  错误: {e}")
    
    print(f"\n补充标题: {fixed_count}")
    return fixed_count

def rename_old_architecture_files():
    """重命名旧架构文件"""
    print("\n" + "=" * 80)
    print("重命名旧架构文件")
    print("=" * 80)
    
    fixed_count = 0
    
    old_files = [
        ('04_DATA_SOURCE/DATA_SOURCE_LAYER_GAP_ANALYSIS.md', '04_DATA_SOURCE/DATA_SOURCE_GAP_ANALYSIS.md'),
        ('05_BACKTEST/LAYERED_BACKTEST.md', '05_BACKTEST/STRATIFIED_BACKTEST.md'),
    ]
    
    for old_path, new_path in old_files:
        old_file = FACTOR_LIBRARY / old_path
        new_file = FACTOR_LIBRARY / new_path
        
        if old_file.exists():
            old_file.rename(new_file)
            print(f"\n{old_path} -> {new_path}")
            fixed_count += 1
    
    print(f"\n重命名文件: {fixed_count}")
    return fixed_count

def main():
    """主函数"""
    print("=" * 80)
    print("综合修复剩余问题")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    total_fixed = 0
    
    # 1. 修复无效链接
    total_fixed += fix_invalid_links()
    
    # 2. 补充缺失的元数据
    total_fixed += fix_missing_metadata()
    
    # 3. 补充缺失的职责描述
    total_fixed += fix_missing_responsibility()
    
    # 4. 补充缺失的标题
    total_fixed += fix_missing_title()
    
    # 5. 重命名旧架构文件
    total_fixed += rename_old_architecture_files()
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
    print(f"总修复数: {total_fixed}")

if __name__ == '__main__':
    main()
