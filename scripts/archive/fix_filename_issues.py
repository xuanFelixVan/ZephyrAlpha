#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
修复命名问题脚本
功能：将中文文件名改为英文文件名
"""

import os
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_DIR = PROJECT_ROOT / "docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state"

# 中文文件名到英文文件名的映射
FILENAME_MAPPING = {
    '资产类别定义.md': 'ASSET_CLASS_DEFINITION.md',
    '资产配置模型.md': 'ASSET_ALLOCATION_MODEL.md',
    '配置优化方法.md': 'ALLOCATION_OPTIMIZATION_METHOD.md',
    '风险调整机制.md': 'RISK_ADJUSTMENT_MECHANISM.md',
    '风险预算方法.md': 'RISK_BUDGETING_METHOD.md',
    '策略评估标准.md': 'STRATEGY_EVALUATION_CRITERIA.md',
    '市场环境评估.md': 'MARKET_ENVIRONMENT_ASSESSMENT.md',
    '战略调整机制.md': 'STRATEGIC_ADJUSTMENT_MECHANISM.md',
    '调整触发条件.md': 'ADJUSTMENT_TRIGGER_CONDITIONS.md'
}

def find_chinese_filename_files():
    """查找中文文件名的文件"""
    chinese_files = []
    
    for root, dirs, files in os.walk(DOCS_DIR):
        # 排除特定目录
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            # 检查是否包含中文
            if any('\u4e00' <= char <= '\u9fff' for char in file):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, DOCS_DIR)
                chinese_files.append({
                    'path': rel_path,
                    'abs_path': file_path,
                    'old_name': file
                })
    
    return chinese_files

def rename_file(file_info):
    """重命名文件"""
    old_name = file_info['old_name']
    new_name = FILENAME_MAPPING.get(old_name)
    
    if not new_name:
        return False, f"未找到映射: {old_name}"
    
    old_path = file_info['abs_path']
    new_path = os.path.join(os.path.dirname(old_path), new_name)
    
    try:
        # 检查新文件名是否已存在
        if os.path.exists(new_path):
            return False, f"目标文件已存在: {new_name}"
        
        # 重命名文件
        os.rename(old_path, new_path)
        return True, f"重命名成功: {old_name} -> {new_name}"
    except Exception as e:
        return False, f"重命名失败: {str(e)}"

def generate_rename_report(chinese_files, renamed_files, failed_files):
    """生成重命名报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'FILENAME_FIX_REPORT_{timestamp}.md'
    
    total_files = len(chinese_files)
    success_rate = (len(renamed_files) / total_files * 100) if total_files > 0 else 0
    
    report_content = f"""---
module_id: FILENAME_FIX_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 文件名修复报告
applicable_scope: 全系统文档
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 文件名修复报告

## 📊 修复概要

**修复时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**修复范围**: 全系统文档  
**修复方法**: 中文文件名改为英文文件名  
**修复结论**: 成功修复 {len(renamed_files)} 个文件

---

## 📈 修复统计

| 统计项 | 数量 |
|--------|------|
| **中文文件名文件** | {total_files} |
| **成功修复文件** | {len(renamed_files)} |
| **修复失败文件** | {len(failed_files)} |
| **修复成功率** | {success_rate:.1f}% |

---

## ✅ 成功修复文件列表

"""
    
    for i, file_info in enumerate(renamed_files, 1):
        report_content += f"{i}. {file_info['old_path']}\n   - 旧文件名: {file_info['old_name']}\n   - 新文件名: {file_info['new_name']}\n"
    
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

1. **手动修复失败文件**: 为 {len(failed_files)} 个修复失败的文件手动重命名

### 本周修复

1. **更新引用链接**: 检查并更新所有引用这些文件的链接
2. **更新索引文件**: 更新INDEX.md中的文件引用

### 长期优化

1. **建立命名规范**: 制定文件命名规范，避免使用中文
2. **建立自动化检查**: 定期检查文件命名规范性

---

## 📝 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，文件名修复报告 | 首席文档架构师 |
"""
    
    # 写入报告
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return report_path

def main():
    """主函数"""
    print("=" * 80)
    print("修复文件名问题")
    print("=" * 80)
    print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 查找中文文件名的文件
    print("查找中文文件名的文件...")
    chinese_files = find_chinese_filename_files()
    print(f"发现 {len(chinese_files)} 个中文文件名的文件")
    print()
    
    # 批量重命名
    print("批量重命名文件...")
    renamed_files = []
    failed_files = []
    
    for file_info in chinese_files:
        success, message = rename_file(file_info)
        
        if success:
            new_name = FILENAME_MAPPING.get(file_info['old_name'])
            renamed_files.append({
                'old_path': file_info['path'],
                'old_name': file_info['old_name'],
                'new_name': new_name
            })
            print(f"✅ {file_info['old_name']} -> {new_name}")
        else:
            failed_files.append({
                'path': file_info['path'],
                'reason': message
            })
            print(f"❌ {file_info['old_name']}: {message}")
    
    print()
    print(f"处理完成: 成功 {len(renamed_files)} 个, 失败 {len(failed_files)} 个")
    
    # 生成报告
    print()
    print("生成修复报告...")
    report_path = generate_rename_report(chinese_files, renamed_files, failed_files)
    print(f"报告已保存至: {report_path}")
    
    print()
    print("=" * 80)
    print("修复完成")
    print("=" * 80)
    
    # 保存JSON结果
    json_path = OUTPUT_DIR / f'filename_fix_result_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_chinese_files': len(chinese_files),
            'total_renamed': len(renamed_files),
            'total_failed': len(failed_files),
            'success_rate': len(renamed_files) / len(chinese_files) * 100 if chinese_files else 0,
            'renamed_files': renamed_files,
            'failed_files': failed_files
        }, f, ensure_ascii=False, indent=2)
    
    print(f"JSON结果已保存至: {json_path}")

if __name__ == '__main__':
    main()
