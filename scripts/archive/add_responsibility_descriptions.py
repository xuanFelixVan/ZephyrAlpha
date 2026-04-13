#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
职责描述补充工具
功能：为缺少职责描述的文档添加核心职责描述
"""

import os
import re
from datetime import datetime

def get_responsibility_by_filename(filename):
    """根据文件名推断职责"""
    responsibilities = {
        'FAQ.md': '常见问题解答和用户指引',
        'HANDOVER.md': '项目交接文档和知识传递',
        'KNOWLEDGE_MANAGEMENT.md': '知识管理体系和方法论',
        'MODULE_DESIGN_PLAN.md': '模块设计规划和架构设计',
        'SITEMAP.md': '文档位置导航和结构地图',
        '99_AUDIT_REPORT.md': '审计报告和问题追踪',
        '05_BACKTEST_REORGANIZATION.md': '回测目录重组方案和规划',
        '05_BREADTH_INDICATORS.md': '市场宽度指标定义和计算',
        'backtest_standards.md': '回测标准规范和流程',
        'FACTOR_MINING_GUIDE.md': '因子挖掘方法论和指南',
        'FACTOR_VALIDATION_GUIDE.md': '因子验证流程和标准',
        'TECHNICAL_INDICATORS.md': '技术指标定义和计算方法',
        'ic_analysis.md': 'IC分析方法和评估标准',
        'factor_return_analysis.md': '因子收益分析方法论',
        'factor_synthesis.md': '因子合成方法和策略',
        'factor_preprocessing.md': '因子预处理方法和流程',
        'factor_neutralization.md': '因子中性化方法和标准',
        'research_management.md': '研究管理流程和规范',
        'FUTURE_FACTOR_TOOLS.md': '未来因子工具规划和设计',
        'README.md': '模块概述和快速入门指引',
        'INDEX.md': '目录导航和文档索引',
        'BLUEPRINT.md': '系统架构设计和蓝图规划',
        'factor_library_manual.md': '因子库操作手册和使用指南',
        'AI_FACTOR_AGENT.md': 'AI因子代理设计和实现',
        'factor_monitoring.md': '因子监控系统和预警机制',
        'FACTOR_VALIDATION_BLUEPRINT.md': '因子验证蓝图和架构设计',
        'correlation_matrix.md': '相关性矩阵计算和分析',
        '09_OVERFITTING_TEST.md': '过拟合测试方法和标准',
        '06_FACTOR_DECAY.md': '因子衰减分析和预警',
        '07_LAYERED_BACKTEST.md': '分层回测方法和流程',
    }
    
    # 精确匹配
    if filename in responsibilities:
        return responsibilities[filename]
    
    # 模式匹配
    if 'BACKTEST' in filename:
        return '回测相关文档'
    if 'FACTOR' in filename:
        return '因子相关文档'
    if 'DATA' in filename:
        return '数据相关文档'
    if 'RISK' in filename:
        return '风险相关文档'
    
    return None

def add_responsibility_to_file(file_path):
    """为文件添加职责描述"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 检查是否已有职责描述
        if '**核心职责**' in content or '**本文档职责**' in content:
            return False, "已有职责描述"
        
        # 提取文件名
        filename = os.path.basename(file_path)
        
        # 推断职责
        responsibility = get_responsibility_by_filename(filename)
        if not responsibility:
            return False, "无法推断职责"
        
        # 查找第一个标题
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if not title_match:
            return False, "未找到标题"
        
        title = title_match.group(1)
        
        # 构建职责描述
        responsibility_block = f"""
> **核心职责**: {responsibility}
> **职责边界**: 
> - ✅ 本文档负责：{responsibility}相关内容
> - ❌ 本文档不负责：具体实现细节、其他模块内容
"""
        
        # 在标题后插入职责描述
        insert_pos = title_match.end()
        new_content = content[:insert_pos] + responsibility_block + content[insert_pos:]
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, f"已添加职责: {responsibility}"
    
    except Exception as e:
        return False, f"错误: {str(e)}"

def main():
    """主函数"""
    root_path = r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY'
    
    print("=" * 80)
    print("职责描述补充工具")
    print("=" * 80)
    print()
    
    # 收集缺少职责描述的文件
    files_without_responsibility = []
    
    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = os.path.join(root, file)
            
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                
                # 检查是否有职责描述
                if '**核心职责**' not in content and '**本文档职责**' not in content:
                    # 排除索引文件和蓝图文件
                    if 'INDEX.md' not in file and 'BLUEPRINT.md' not in file:
                        files_without_responsibility.append(file_path)
            except:
                pass
    
    print(f"发现 {len(files_without_responsibility)} 个缺少职责描述的文件")
    print()
    
    # 批量添加职责描述
    success_count = 0
    fail_count = 0
    
    for file_path in files_without_responsibility:
        rel_path = os.path.relpath(file_path, root_path)
        success, message = add_responsibility_to_file(file_path)
        
        if success:
            print(f"✅ {rel_path}: {message}")
            success_count += 1
        else:
            print(f"⏭️ {rel_path}: {message}")
            fail_count += 1
    
    print()
    print("=" * 80)
    print(f"处理完成: 成功 {success_count} 个, 跳过 {fail_count} 个")
    print("=" * 80)

if __name__ == '__main__':
    main()
