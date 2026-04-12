#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
手动修复职责描述脚本
功能：为修复失败的文件手动添加职责描述
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_DIR = PROJECT_ROOT / "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state"

def read_failed_files():
    """读取失败的文件列表"""
    json_path = OUTPUT_DIR / "responsibility_fix_result_20260407_030139.json"
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data['failed_files']

def infer_responsibility_from_path(file_path):
    """从文件路径推断职责"""
    file_name = os.path.basename(file_path)
    dir_name = os.path.basename(os.path.dirname(file_path))
    
    # 特殊文件处理
    if 'COMPLETENESS_ANALYSIS' in file_name:
        return '完整性分析和评估报告'
    if 'OPTIMIZATION_REPORT' in file_name:
        return '优化分析和改进报告'
    if 'REFACTOR_COMPLETE' in file_name:
        return '重构完成状态报告'
    if 'quality_monitoring_report' in file_name:
        return '质量监控和评估报告'
    if 'BLUEPRINT_AUDIT' in file_name:
        return '蓝图审计和评估报告'
    if 'DEEP_AUDIT' in file_name:
        return '深度审计和分析报告'
    
    # 蓝图文件
    if 'BLUEPRINT' in file_name:
        topic = file_name.replace('_BLUEPRINT.md', '').replace('_', ' ').title()
        return f'{topic}蓝图设计'
    
    # README文件
    if file_name == 'README.md':
        return '模块说明和快速入门指南'
    
    # 默认
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

def main():
    """主函数"""
    print("=" * 80)
    print("手动修复职责描述")
    print("=" * 80)
    print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 读取失败的文件列表
    print("读取失败的文件列表...")
    failed_files = read_failed_files()
    print(f"发现 {len(failed_files)} 个失败的文件")
    print()
    
    # 批量修复
    print("批量修复职责描述...")
    fixed_files = []
    still_failed = []
    
    for i, file_info in enumerate(failed_files, 1):
        file_path = file_info['path']
        responsibility = infer_responsibility_from_path(file_path)
        
        success, message = add_responsibility_to_file(file_path, responsibility)
        
        if success:
            fixed_files.append({
                'path': file_path,
                'responsibility': responsibility
            })
            print(f"✅ {i}/{len(failed_files)}: {file_path}")
        else:
            still_failed.append({
                'path': file_path,
                'reason': message
            })
            print(f"❌ {i}/{len(failed_files)}: {file_path} - {message}")
    
    print()
    print(f"处理完成: 成功 {len(fixed_files)} 个, 失败 {len(still_failed)} 个")
    
    # 保存结果
    json_path = OUTPUT_DIR / f'manual_fix_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_failed': len(failed_files),
            'total_fixed': len(fixed_files),
            'still_failed': len(still_failed),
            'success_rate': len(fixed_files) / len(failed_files) * 100 if failed_files else 0,
            'fixed_files': fixed_files,
            'still_failed': still_failed
        }, f, ensure_ascii=False, indent=2)
    
    print(f"结果已保存至: {json_path}")
    print()
    print("=" * 80)
    print("修复完成")
    print("=" * 80)

if __name__ == '__main__':
    main()
