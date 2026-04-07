#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复职责重叠文档的职责描述
功能：为职责描述为"文档内容说明"的文档添加具体职责
"""

import os
import re
from pathlib import Path

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

# 定义文档职责映射
RESPONSIBILITY_MAP = {
    'BAOSTOCK_CONNECTOR.md': 'Baostock数据源连接器接口定义和使用说明',
    'CORRELATION_ANALYSIS.md': '因子相关性分析方法与统计检验实现',
    'DATA_ACQUISITION.md': '数据采集架构设计和多数据源接入方案',
    'DATA_REQUIREMENTS.md': '数据需求规格定义和数据质量标准',
    'DATA_SOURCE_ADAPTERS.md': '数据源统一适配器接口和多源数据整合',
    'DATA_SOURCE_LAYER_GAP_ANALYSIS_V2.md': '数据源层差距分析和改进方案',
    'factor_master_index.md': '因子主索引管理和元数据维护',
    'FREE_DATA_SOURCES.md': '免费数据源清单和接入指南',
    'IFIND_CONNECTOR.md': 'iFind数据源连接器接口和使用说明',
    'MACRO_DATA.md': '宏观经济数据采集和处理方法',
    'NEWS_SENTIMENT_DATA_SOURCE.md': '新闻情感数据源接入和情感分析',
    'QMT_INTERFACE.md': 'QMT量化交易接口定义和使用说明',
    'STATISTICAL_TOOLS.md': '统计分析工具集和数学计算方法',
    'SUPERCMD_CONNECTOR.md': 'SuperCMD数据源连接器接口定义',
    'SCHEDULER_API.md': '数据调度器API接口和任务调度管理',
    'CLEANING_RULES.md': '数据清洗规则定义和质量控制标准',
    'FINANCIAL_STATEMENTS_API.md': '财务报表数据API接口和使用说明',
    'THS_BD_COMPLETE_INDICATOR_LIST.md': '同花顺BD完整指标清单和映射关系',
    'DATA_QUALITY_CONTROL_SYSTEM.md': '数据质量控制体系和质量评估方法',
    'QUALITY_METRICS.md': '数据质量指标定义和评估标准'
}

def fix_responsibility():
    """修复职责描述"""
    print("=" * 80)
    print("修复职责重叠文档的职责描述")
    print("=" * 80)
    
    fixed_count = 0
    failed_count = 0
    
    for filename, responsibility in RESPONSIBILITY_MAP.items():
        # 查找文件
        file_path = None
        for root, dirs, files in os.walk(DOCS_DIR / "02_FACTOR_LIBRARY"):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
            
            if filename in files:
                file_path = os.path.join(root, filename)
                break
        
        if not file_path:
            print(f"⚠️ 文件不存在: {filename}")
            failed_count += 1
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 检查是否有"文档内容说明"这样的通用职责描述
            if '文档内容说明' in content:
                # 替换职责描述
                new_content = re.sub(
                    r'> \*\*核心职责\*\*:\s*文档内容说明',
                    f'> **核心职责**: {responsibility}',
                    content
                )
                
                # 更新职责边界
                new_content = re.sub(
                    r'> \*\*职责边界\*\*:\s*\n> - ✅ 本文档负责：文档内容说明相关内容',
                    f'> **职责边界**: \n> - ✅ 本文档负责：{responsibility}',
                    new_content
                )
                
                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    fixed_count += 1
                    print(f"✅ 修复: {filename}")
                    print(f"   新职责: {responsibility}")
                else:
                    print(f"⚠️ 未修改: {filename}")
            else:
                print(f"✓ 已有具体职责: {filename}")
        
        except Exception as e:
            print(f"❌ 错误: {filename} - {str(e)}")
            failed_count += 1
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
    print(f"成功修复: {fixed_count} 个")
    print(f"修复失败: {failed_count} 个")
    
    return fixed_count, failed_count

def main():
    """主函数"""
    fixed, failed = fix_responsibility()
    
    print("\n" + "=" * 80)
    print("总结")
    print("=" * 80)
    print(f"总处理文件: {len(RESPONSIBILITY_MAP)} 个")
    print(f"成功修复: {fixed} 个")
    print(f"修复失败: {failed} 个")

if __name__ == '__main__':
    main()
