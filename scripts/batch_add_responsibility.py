#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量补充职责描述脚本
功能：为缺少职责描述的文档自动添加职责描述
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_DIR = PROJECT_ROOT / "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state"

def extract_responsibility(content):
    """提取职责描述"""
    patterns = [
        r'\*\*核心职责\*\*:\s*(.+?)(?:\n|$)',
        r'\*\*本文档职责\*\*[：:]\s*(.+?)(?:\n|$)',
        r'核心职责[：:]\s*(.+?)(?:\n|$)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()
    
    return None

def infer_responsibility_from_path(file_path, content):
    """从文件路径推断职责"""
    file_name = os.path.basename(file_path)
    dir_name = os.path.basename(os.path.dirname(file_path))
    
    # INDEX.md文件
    if file_name == 'INDEX.md':
        return '目录导航和文档索引'
    
    # README.md文件
    if file_name == 'README.md':
        return '模块说明和快速入门指南'
    
    # ARCHITECTURE.md文件
    if file_name == 'ARCHITECTURE.md':
        return '系统架构设计和模块关系说明'
    
    # BLUEPRINT.md文件
    if 'BLUEPRINT' in file_name:
        # 从文件名提取蓝图主题
        topic = file_name.replace('_BLUEPRINT.md', '').replace('_', ' ').title()
        return f'{topic}蓝图设计'
    
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
    
    # 从内容标题推断
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
        # 提取关键词
        if '蓝图' in title:
            return '蓝图设计和规划'
        if '架构' in title:
            return '架构设计和模块关系'
        if '标准' in title or '规范' in title:
            return '标准规范制定'
        if '指南' in title or '教程' in title:
            return '使用指南和教程'
        if '报告' in title:
            return '分析报告和评估结果'
    
    # 默认职责
    return '文档内容说明'

def add_responsibility(file_path, responsibility_text):
    """为文件添加职责描述"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 检查是否已有职责描述
        if extract_responsibility(content):
            return False, "已有职责描述"
        
        # 查找第一个标题
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if not title_match:
            return False, "未找到标题"
        
        # 构建职责描述
        responsibility_block = f"""
> **核心职责**: {responsibility_text}
> **职责边界**: 
> - ✅ 本文档负责：{responsibility_text}相关内容
> - ❌ 本文档不负责：其他模块内容
"""
        
        # 在标题后插入职责描述
        insert_pos = title_match.end()
        new_content = content[:insert_pos] + responsibility_block + content[insert_pos:]
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, f"已添加职责: {responsibility_text}"
    
    except Exception as e:
        return False, f"错误: {str(e)}"

def scan_and_fix_responsibility():
    """扫描并修复职责描述"""
    missing_files = []
    fixed_files = []
    failed_files = []
    
    print("扫描文档目录...")
    
    for root, dirs, files in os.walk(DOCS_DIR):
        # 排除特定目录
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, DOCS_DIR)
            
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 检查是否有职责描述
                if not extract_responsibility(content):
                    missing_files.append({
                        'path': rel_path,
                        'abs_path': file_path,
                        'content': content
                    })
            except Exception as e:
                print(f"读取文件失败: {rel_path}, 错误: {str(e)}")
    
    print(f"发现 {len(missing_files)} 个文件缺少职责描述")
    print()
    
    # 批量添加职责描述
    print("批量添加职责描述...")
    
    for i, file_info in enumerate(missing_files, 1):
        if i % 100 == 0:
            print(f"处理进度: {i}/{len(missing_files)}")
        
        # 推断职责
        responsibility = infer_responsibility_from_path(file_info['abs_path'], file_info['content'])
        
        # 添加职责描述
        success, message = add_responsibility(file_info['abs_path'], responsibility)
        
        if success:
            fixed_files.append({
                'path': file_info['path'],
                'responsibility': responsibility
            })
        else:
            failed_files.append({
                'path': file_info['path'],
                'reason': message
            })
    
    print(f"处理完成: 成功 {len(fixed_files)} 个, 失败 {len(failed_files)} 个")
    
    return missing_files, fixed_files, failed_files

def generate_report(missing_files, fixed_files, failed_files):
    """生成报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'RESPONSIBILITY_FIX_REPORT_{timestamp}.md'
    
    total_files = len(missing_files)
    success_rate = (len(fixed_files) / total_files * 100) if total_files > 0 else 0
    
    report_content = f"""---
module_id: RESPONSIBILITY_FIX_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 职责描述修复报告
applicable_scope: 全系统文档
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 职责描述批量修复报告

## 📊 修复概要

**修复时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**修复范围**: 全系统文档  
**修复方法**: 自动推断和批量添加  
**修复结论**: 成功修复 {len(fixed_files)} 个文件

---

## 📈 修复统计

| 统计项 | 数量 |
|--------|------|
| **缺少职责描述文件** | {total_files} |
| **成功修复文件** | {len(fixed_files)} |
| **修复失败文件** | {len(failed_files)} |
| **修复成功率** | {success_rate:.1f}% |

---

## ✅ 成功修复文件列表（前50个）

"""
    
    for i, file_info in enumerate(fixed_files[:50], 1):
        report_content += f"{i}. {file_info['path']}\n   - 职责: {file_info['responsibility']}\n"
    
    if len(fixed_files) > 50:
        report_content += f"... 还有 {len(fixed_files) - 50} 个文件\n"
    
    if failed_files:
        report_content += f"""
---

## ❌ 修复失败文件列表

"""
        for i, file_info in enumerate(failed_files, 1):
            report_content += f"{i}. {file_info['path']}\n   - 原因: {file_info['reason']}\n"
    
    report_content += f"""
---

## 💡 改进建议

### 立即修复（24小时内）

1. **手动修复失败文件**: 为 {len(failed_files)} 个修复失败的文件手动添加职责描述

### 本周修复

1. **优化职责描述质量**: 为职责描述过短的文件补充详细说明
2. **添加职责边界说明**: 为所有文件添加完整的职责边界说明

### 长期优化

1. **建立自动化检查机制**: 定期检查职责描述缺失情况
2. **建立职责描述规范**: 制定职责描述模板和审查机制

---

## 📝 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，职责描述批量修复报告 | 首席文档架构师 |
"""
    
    # 写入报告
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return report_path

def main():
    """主函数"""
    print("=" * 80)
    print("批量补充职责描述")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 扫描并修复
    missing_files, fixed_files, failed_files = scan_and_fix_responsibility()
    
    print()
    print("生成修复报告...")
    report_path = generate_report(missing_files, fixed_files, failed_files)
    print(f"报告已保存至: {report_path}")
    
    print()
    print("=" * 80)
    print("处理完成")
    print("=" * 80)
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 保存JSON结果
    json_path = OUTPUT_DIR / f'responsibility_fix_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
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
    
    print(f"JSON结果已保存至: {json_path}")

if __name__ == '__main__':
    main()
