#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
为缺失职责说明的文档补充职责说明章节
"""

import os
import re
from pathlib import Path

def add_responsibility_section(file_path, doc_type, module_name):
    """
    为文档添加职责说明章节
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已有职责说明
        if '## 文档职责说明' in content:
            return False, "已有职责说明章节"
        
        # 根据文档类型生成职责说明
        if doc_type == 'INDEX':
            responsibility = f"""## 文档职责说明

**本文档职责**: {module_name}模块索引与导航
- 提供{module_name}模块所有文档的统一入口
- 组织模块内的文档结构
- 维护文档间的引用关系

**职责边界**:
- ✅ 本文档负责: {module_name}模块文档导航和索引
- ❌ 本文档不负责: 具体功能实现（由各功能文档负责）
"""
        else:
            responsibility = f"""## 文档职责说明

**本文档职责**: {module_name}
- 定义{module_name}的核心功能和设计
- 提供实现方案和技术规格
- 维护相关文档引用

**职责边界**:
- ✅ 本文档负责: {module_name}的设计和实现方案
- ❌ 本文档不负责: 其他模块功能（由相关模块文档负责）
"""
        
        # 找到第一个标题（通常是文档标题）
        title_match = re.search(r'^#\s+.+$', content, re.MULTILINE)
        
        if title_match:
            # 在标题后插入职责说明
            insert_pos = title_match.end()
            new_content = content[:insert_pos] + '\n\n' + responsibility + content[insert_pos:]
        else:
            # 如果没有标题，在YAML头部后插入
            yaml_match = re.match(r'^---\r?\n.*?\r?\n---\r?\n', content, re.DOTALL)
            if yaml_match:
                insert_pos = yaml_match.end()
                new_content = content[:insert_pos] + '\n' + responsibility + content[insert_pos:]
            else:
                # 在文件开头插入
                new_content = responsibility + content
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(new_content)
        
        return True, "已添加职责说明章节"
    
    except Exception as e:
        return False, f"处理失败: {str(e)}"

def main():
    """主函数"""
    # 数据源层目录
    data_source_dir = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY\04_DATA_SOURCE')
    
    # 定义需要补充职责说明的文件及其信息
    files_to_fix = {
        # INDEX文件
        'DATA_VERSION_CONTROL/INDEX.md': ('INDEX', '数据版本控制'),
        'DATA_TESTING_FRAMEWORK/INDEX.md': ('INDEX', '数据测试框架'),
        'DATA_SYNC_REPLICATION/INDEX.md': ('INDEX', '数据同步复制'),
        'DATA_SECURITY_PRIVACY/INDEX.md': ('INDEX', '数据安全与隐私保护'),
        'DATA_STANDARDIZATION/INDEX.md': ('INDEX', '数据标准化'),
        'DATA_PROFILING/INDEX.md': ('INDEX', '数据画像'),
        'DATA_PERMISSION_MANAGEMENT/INDEX.md': ('INDEX', '数据权限管理'),
        'DATA_OBSERVABILITY/INDEX.md': ('INDEX', '数据可观测性平台'),
        'DATA_MONITORING_ENHANCED/INDEX.md': ('INDEX', '数据监控系统'),
        'DATA_LINEAGE_TRACKING/INDEX.md': ('INDEX', '数据血缘追踪'),
        'DATA_LIFECYCLE_MANAGEMENT/INDEX.md': ('INDEX', '数据生命周期管理'),
        'DATA_FEDERATION/INDEX.md': ('INDEX', '数据联邦查询'),
        'DATA_CONTRACT/INDEX.md': ('INDEX', '数据契约管理'),
        'DATA_COMPRESSION_ARCHIVE/INDEX.md': ('INDEX', '数据压缩归档'),
        'DATA_CATALOG/INDEX.md': ('INDEX', '数据目录系统'),
        'DATA_BACKUP_RECOVERY/INDEX.md': ('INDEX', '数据备份恢复'),
        'DATA_API_GATEWAY/INDEX.md': ('INDEX', '数据API网关'),
        'DATA_ANOMALY_DETECTION/INDEX.md': ('INDEX', '数据异常检测'),
        '07_DATA_PIPELINE/INDEX.md': ('INDEX', '数据流水线'),
        'CONFIG_MANAGEMENT/INDEX.md': ('INDEX', '配置管理'),
        'TIME_SERIES_STORAGE/INDEX.md': ('INDEX', '时序数据存储'),
        'REALTIME_DATA_STREAMING/INDEX.md': ('INDEX', '实时数据流'),
        'DATA_ORCHESTRATION_ENHANCED/INDEX.md': ('INDEX', '数据编排增强'),
        # 其他文件
        'DOCUMENT_NAMING_STANDARD.md': ('OTHER', '文档命名标准'),
        'DATA_REQUIREMENTS.md': ('OTHER', '数据需求定义'),
        'CORRELATION_ANALYSIS.md': ('OTHER', '相关性分析工具'),
    }
    
    # 统计信息
    total_files = 0
    fixed_files = 0
    skipped_files = 0
    error_files = 0
    
    print("=" * 80)
    print("开始补充职责说明章节...")
    print("=" * 80)
    
    # 处理每个文件
    for rel_path, (doc_type, module_name) in files_to_fix.items():
        file_path = data_source_dir / rel_path
        total_files += 1
        
        if not file_path.exists():
            print(f"⚠️  文件不存在: {rel_path}")
            error_files += 1
            continue
        
        # 尝试添加职责说明
        fixed, message = add_responsibility_section(str(file_path), doc_type, module_name)
        
        if fixed:
            fixed_files += 1
            print(f"✅ [{fixed_files}] {rel_path}: {message}")
        elif "已有" in message:
            skipped_files += 1
            print(f"⏭️  {rel_path}: {message}")
        else:
            error_files += 1
            print(f"❌ {rel_path}: {message}")
    
    # 输出统计信息
    print("\n" + "=" * 80)
    print("补充完成！")
    print("=" * 80)
    print(f"总文件数: {total_files}")
    print(f"已补充: {fixed_files}")
    print(f"已有职责说明: {skipped_files}")
    print(f"处理失败: {error_files}")
    print(f"补充率: {fixed_files/total_files*100:.1f}%")

if __name__ == '__main__':
    main()
