#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量补充元数据
处理所有缺少元数据的文档
"""

import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

# 必需字段
REQUIRED_FIELDS = ['module_id', 'version', 'status', 'created_date', 'owner']

def check_metadata_completeness(file_path):
    """检查元数据完整性"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 检查是否有YAML元数据
        if not content.startswith('---'):
            return False, [], content
        
        yaml_end = content.find('---', 3)
        if yaml_end < 0:
            return False, [], content
        
        yaml_content = content[3:yaml_end]
        
        # 检查必需字段
        missing_fields = []
        for field in REQUIRED_FIELDS:
            if f'{field}:' not in yaml_content:
                missing_fields.append(field)
        
        return len(missing_fields) == 0, missing_fields, content
    
    except Exception as e:
        return False, [], ''

def generate_module_id(file_path):
    """生成module_id"""
    # 使用文件名（去除扩展名）
    stem = file_path.stem
    
    # 转换为大写
    module_id = stem.upper()
    
    # 替换特殊字符
    module_id = re.sub(r'[^A-Z0-9_]', '_', module_id)
    
    # 移除连续下划线
    module_id = re.sub(r'_+', '_', module_id)
    
    # 移除首尾下划线
    module_id = module_id.strip('_')
    
    return module_id

def supplement_metadata_batch(batch_size=100):
    """批量补充元数据"""
    print("=" * 80)
    print("批量补充元数据")
    print("=" * 80)
    
    # 扫描所有文档
    all_files = []
    for file_path in FACTOR_LIBRARY.rglob('*.md'):
        # 跳过audit_state目录
        if 'audit_state' in str(file_path):
            continue
        
        all_files.append(file_path)
    
    print(f"\n总文件数: {len(all_files)}")
    
    # 检查元数据完整性
    files_to_supplement = []
    for file_path in all_files:
        is_complete, missing_fields, content = check_metadata_completeness(file_path)
        if not is_complete:
            rel_path = file_path.relative_to(FACTOR_LIBRARY)
            files_to_supplement.append({
                'path': file_path,
                'rel_path': str(rel_path),
                'missing_fields': missing_fields,
                'content': content
            })
    
    print(f"需要补充元数据的文档: {len(files_to_supplement)}")
    
    # 批量处理
    supplemented_count = 0
    failed_count = 0
    
    # 只处理前batch_size个文档
    for file_info in files_to_supplement[:batch_size]:
        file_path = file_info['path']
        content = file_info['content']
        
        try:
            # 生成module_id
            module_id = generate_module_id(file_path)
            
            # 生成标准化的元数据
            metadata = f"""---
module_id: {module_id}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
---

"""
            
            # 如果已有YAML元数据，替换它
            if content.startswith('---'):
                yaml_end = content.find('---', 3)
                if yaml_end > 0:
                    content = metadata + content[yaml_end + 3:]
                else:
                    content = metadata + content
            else:
                content = metadata + content
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  补充: {file_info['rel_path']}")
            supplemented_count += 1
        
        except Exception as e:
            print(f"  失败: {file_info['rel_path']} - {e}")
            failed_count += 1
    
    print(f"\n补充完成")
    print(f"补充文档: {supplemented_count}")
    print(f"失败文档: {failed_count}")
    print(f"剩余文档: {len(files_to_supplement) - batch_size}")
    
    return supplemented_count, failed_count, len(files_to_supplement) - batch_size

def generate_report(supplemented_count, failed_count, remaining_count):
    """生成报告"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = OUTPUT_DIR / f'BATCH_METADATA_SUPPLEMENT_REPORT_{timestamp}.md'
    
    report_content = f"""---
module_id: BATCH_METADATA_SUPPLEMENT_REPORT_{timestamp}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 首席文档架构师
standard_type: 补充报告
applicable_scope: 批量元数据补充
compliance_level: 专业标准
parent_document: ../INDEX.md
---

# 批量元数据补充报告

> **核心职责**: 记录批量元数据补充的过程和结果
> **职责边界**: 
> - [OK] 本文档负责：补充记录、效果评估、后续建议
> - [NO] 本文档不负责：后续审计执行、新问题发现

---

## 补充概要

**补充时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**补充范围**: 全系统文档  
**补充方法**: 批量自动补充  
**补充结论**: 成功补充元数据

---

## 补充统计

| 统计项 | 数量 | 说明 |
|--------|------|------|
| **补充文档** | {supplemented_count} | 成功补充元数据 |
| **失败文档** | {failed_count} | 补充失败 |
| **剩余文档** | {remaining_count} | 待补充文档 |

---

## 后续建议

### 立即行动

1. [x] 批量补充元数据
2. [ ] 继续处理剩余文档
3. [ ] 验证补充效果

### 持续改进

1. [ ] 定期执行元数据检查
2. [ ] 持续优化文档质量
3. [ ] 建立质量监控体系

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {datetime.now().strftime('%Y-%m-%d')} | 初始版本，批量元数据补充报告 | 首席文档架构师 |
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n报告已生成: {report_path}")
    return report_path

if __name__ == '__main__':
    # 批量补充元数据
    supplemented_count, failed_count, remaining_count = supplement_metadata_batch(batch_size=200)
    
    # 生成报告
    report_path = generate_report(supplemented_count, failed_count, remaining_count)
    
    print("\n" + "=" * 80)
    print("批量元数据补充完成")
    print("=" * 80)
    print(f"补充文档: {supplemented_count}")
    print(f"失败文档: {failed_count}")
    print(f"剩余文档: {remaining_count}")
    print(f"报告位置: {report_path}")
