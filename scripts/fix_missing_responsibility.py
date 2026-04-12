#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
修复职责描述缺失脚本
功能：为缺少职责描述的文件添加职责描述
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_DIR = PROJECT_ROOT / "docs/09_AUDIT/STATE"

def check_responsibility_description(file_path):
    """检查职责描述是否存在"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        has_responsibility = '**核心职责**' in content or '**本文档职责**' in content
        return has_responsibility
    except:
        return False

def infer_responsibility_from_path(file_path):
    """从文件路径推断职责"""
    file_name = os.path.basename(file_path)
    dir_name = os.path.basename(os.path.dirname(file_path))
    
    # 特殊文件处理
    if file_name == 'INDEX.md':
        return '目录导航和文档索引'
    if file_name == 'README.md':
        return '模块说明和快速入门指南'
    if file_name == 'ARCHITECTURE.md':
        return '系统架构设计和模块关系说明'
    
    # 蓝图文件
    if 'BLUEPRINT' in file_name:
        topic = file_name.replace('_BLUEPRINT.md', '').replace('_', ' ').title()
        return f'{topic}蓝图设计'
    
    # 标准文件
    if 'STANDARD' in file_name:
        return '标准规范制定'
    
    # 指南文件
    if 'GUIDE' in file_name or 'TUTORIAL' in file_name:
        return '使用指南和教程'
    
    # API文件
    if 'API' in file_name:
        return 'API接口文档'
    
    # 测试文件
    if 'TEST' in file_name:
        return '测试文档和测试用例'
    
    # 审计文件
    if 'AUDIT' in file_name:
        return '审计报告和审计记录'
    
    # 报告文件
    if 'REPORT' in file_name:
        return '分析报告和评估结果'
    
    # 配置文件
    if 'CONFIG' in file_name:
        return '系统配置和参数设置'
    
    # 从目录名推断
    if 'STANDARDS' in dir_name:
        return '标准规范制定'
    if 'GUIDE' in dir_name or 'TUTORIAL' in dir_name:
        return '使用指南和教程'
    if 'API' in dir_name:
        return 'API接口文档'
    if 'TEST' in dir_name:
        return '测试文档和测试用例'
    if 'AUDIT' in dir_name:
        return '审计报告和审计记录'
    if 'REPORT' in dir_name:
        return '分析报告和评估结果'
    
    # 默认职责
    return '文档内容说明'

def add_responsibility_to_file(file_path, responsibility_text):
    """为文件添加职责描述"""
    try:
        abs_path = DOCS_DIR / file_path
        
        if not abs_path.exists():
            return False, "文件不存在"
        
        with open(abs_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 检查是否已有职责描述
        if '**核心职责**' in content or '**本文档职责**' in content:
            return False, "已有职责描述"
        
        # 检查文件是否为空或只有YAML头部
        lines = content.strip().split('\n')
        
        if len(lines) == 0:
            # 空文件，创建基本结构
            new_content = f"""---
module_id: {os.path.basename(file_path).replace('.md', '').upper()}_001
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
---

# {os.path.basename(file_path).replace('.md', '').replace('_', ' ')}

> **核心职责**: {responsibility_text}
> **职责边界**: 
> - ✅ 本文档负责：{responsibility_text}相关内容
> - ❌ 本文档不负责：其他模块内容
"""
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True, f"已创建基本结构并添加职责: {responsibility_text}"
        
        # 查找YAML头部结束位置
        yaml_end = content.find('---', 3) if content.startswith('---') else -1
        
        if yaml_end > 0:
            # 有YAML头部，在YAML后添加标题和职责描述
            yaml_section = content[:yaml_end + 3]
            rest_content = content[yaml_end + 3:].strip()
            
            # 检查是否有标题
            title_match = re.search(r'^#\s+(.+)$', rest_content, re.MULTILINE)
            
            if title_match:
                # 有标题，在标题后添加职责描述
                insert_pos = title_match.end()
                responsibility_block = f"""

> **核心职责**: {responsibility_text}
> **职责边界**: 
> - ✅ 本文档负责：{responsibility_text}相关内容
> - ❌ 本文档不负责：其他模块内容
"""
                new_content = yaml_section + '\n' + rest_content[:insert_pos] + responsibility_block + rest_content[insert_pos:]
            else:
                # 无标题，添加标题和职责描述
                title = os.path.basename(file_path).replace('.md', '').replace('_', ' ')
                new_content = f"""{yaml_section}

# {title}

> **核心职责**: {responsibility_text}
> **职责边界**: 
> - ✅ 本文档负责：{responsibility_text}相关内容
> - ❌ 本文档不负责：其他模块内容

{rest_content}
"""
        else:
            # 无YAML头部，添加YAML头部、标题和职责描述
            title = os.path.basename(file_path).replace('.md', '').replace('_', ' ')
            new_content = f"""---
module_id: {os.path.basename(file_path).replace('.md', '').upper()}_001
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
---

# {title}

> **核心职责**: {responsibility_text}
> **职责边界**: 
> - ✅ 本文档负责：{responsibility_text}相关内容
> - ❌ 本文档不负责：其他模块内容

{content}
"""
        
        # 写回文件
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, f"已添加职责: {responsibility_text}"
    
    except Exception as e:
        return False, f"错误: {str(e)}"

def scan_missing_responsibility():
    """扫描缺少职责描述的文件"""
    missing_files = []
    
    for root, dirs, files in os.walk(DOCS_DIR):
        # 排除特定目录
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, DOCS_DIR)
            
            if not check_responsibility_description(file_path):
                missing_files.append(rel_path)
    
    return missing_files

def main():
    """主函数"""
    print("=" * 80)
    print("修复职责描述缺失")
    print("=" * 80)
    print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 扫描缺少职责描述的文件
    print("扫描缺少职责描述的文件...")
    missing_files = scan_missing_responsibility()
    print(f"发现 {len(missing_files)} 个文件缺少职责描述")
    print()
    
    if not missing_files:
        print("✅ 所有文件都有职责描述")
        print()
        print("=" * 80)
        print("修复完成")
        print("=" * 80)
        return
    
    # 批量修复
    print("批量修复职责描述...")
    fixed_files = []
    failed_files = []
    
    for i, file_path in enumerate(missing_files, 1):
        responsibility = infer_responsibility_from_path(file_path)
        
        success, message = add_responsibility_to_file(file_path, responsibility)
        
        if success:
            fixed_files.append({
                'path': file_path,
                'responsibility': responsibility
            })
            print(f"✅ {i}/{len(missing_files)}: {file_path}")
        else:
            failed_files.append({
                'path': file_path,
                'reason': message
            })
            print(f"❌ {i}/{len(missing_files)}: {file_path} - {message}")
    
    print()
    print(f"处理完成: 成功 {len(fixed_files)} 个, 失败 {len(failed_files)} 个")
    
    # 保存结果
    json_path = OUTPUT_DIR / f'fix_missing_responsibility_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_missing': len(missing_files),
            'total_fixed': len(fixed_files),
            'total_failed': len(failed_files),
            'success_rate': len(fixed_files) / len(missing_files) * 100 if missing_files else 0,
            'fixed_files': fixed_files,
            'failed_files': failed_files
        }, f, ensure_ascii=False, indent=2)
    
    print(f"结果已保存至: {json_path}")
    print()
    print("=" * 80)
    print("修复完成")
    print("=" * 80)

if __name__ == '__main__':
    main()
