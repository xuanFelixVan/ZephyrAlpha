#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复职责不清文档 - 补充完整标题
"""

import re
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')
OUTPUT_DIR = Path(r'D:\ZephyrAlpha\docs\09_AUDIT\STATE')

# 需要修复的文档列表
DOCS_TO_FIX = [
    {
        'path': 'OPTIMIZATION_SUMMARY.md',
        'new_title': '因子库优化总结',
        'description': '记录因子库架构优化和文档治理的改进历程'
    },
    {
        'path': '01_STANDARDS/backtest_standards.md',
        'new_title': '因子回测标准规范',
        'description': '定义因子回测的标准流程和评估指标'
    },
    {
        'path': '01_STANDARDS/INDEX.md',
        'new_title': '因子标准规范目录索引',
        'description': '因子库标准规范模块的导航和索引'
    },
    {
        'path': '03_RISK_FACTORS/INDEX.md',
        'new_title': '风险因子目录索引',
        'description': '风险因子模块的导航和索引'
    },
    {
        'path': '05_BACKTEST/INDEX.md',
        'new_title': '因子回测目录索引',
        'description': '因子回测模块的导航和索引'
    },
    {
        'path': '06_REGISTRY/INDEX.md',
        'new_title': '因子注册表目录索引',
        'description': '因子注册表模块的导航和索引'
    },
    {
        'path': '07_FACTOR_MONITORING/factor_monitoring.md',
        'new_title': '因子实时监控系统',
        'description': '监控因子表现和异常预警'
    },
    {
        'path': '07_FACTOR_MONITORING/INDEX.md',
        'new_title': '因子监控目录索引',
        'description': '因子监控模块的导航和索引'
    },
    {
        'path': '04_DATA_SOURCE/CONFIG_MANAGEMENT/README.md',
        'new_title': '数据配置管理系统',
        'description': '数据源配置和参数管理'
    },
    {
        'path': '04_DATA_SOURCE/DATA_CATALOG/README.md',
        'new_title': '数据目录管理系统',
        'description': '数据资产目录和元数据管理'
    },
    {
        'path': '04_DATA_SOURCE/DATA_CONTRACT/README.md',
        'new_title': '数据契约管理系统',
        'description': '数据交换契约和接口规范'
    },
    {
        'path': '04_DATA_SOURCE/DATA_FEDERATION/README.md',
        'new_title': '数据联邦系统',
        'description': '分布式数据源联邦查询'
    },
    {
        'path': '04_DATA_SOURCE/DATA_PROFILING/README.md',
        'new_title': '数据分析系统',
        'description': '数据质量分析和统计画像'
    },
    {
        'path': '04_DATA_SOURCE/TIME_SERIES_STORAGE/README.md',
        'new_title': '时序数据存储系统',
        'description': '高频时序数据存储和查询'
    }
]

def fix_document(file_path, new_title, description):
    """修复单个文档"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 检查是否已有标题
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        
        if title_match:
            old_title = title_match.group(1)
            # 检查标题是否过短
            if len(old_title) < 5:
                # 替换标题
                content = re.sub(r'^#\s+.+$', f'# {new_title}', content, count=1, flags=re.MULTILINE)
                print(f"  替换标题: '{old_title}' -> '{new_title}'")
            else:
                print(f"  标题已存在: '{old_title}'")
                return False
        else:
            # 添加标题
            # 找到YAML头部结束位置
            if content.startswith('---'):
                yaml_end = content.find('---', 3)
                if yaml_end > 0:
                    # 在YAML头部后添加标题
                    content = content[:yaml_end + 3] + f'\n\n# {new_title}\n\n> {description}\n\n' + content[yaml_end + 3:]
                    print(f"  添加标题: '{new_title}'")
            else:
                # 在文件开头添加标题
                content = f'# {new_title}\n\n> {description}\n\n' + content
                print(f"  添加标题: '{new_title}'")
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    
    except Exception as e:
        print(f"  错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("修复职责不清文档")
    print("=" * 80)
    
    fixed_count = 0
    failed_count = 0
    
    for doc_info in DOCS_TO_FIX:
        file_path = FACTOR_LIBRARY / doc_info['path']
        
        print(f"\n处理: {doc_info['path']}")
        
        if file_path.exists():
            if fix_document(file_path, doc_info['new_title'], doc_info['description']):
                fixed_count += 1
            else:
                failed_count += 1
        else:
            print(f"  文件不存在")
            failed_count += 1
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
    print(f"修复文档: {fixed_count}")
    print(f"失败文档: {failed_count}")

if __name__ == '__main__':
    main()
