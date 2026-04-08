#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为INDEX.md文件添加职责描述
功能：批量为INDEX.md文件添加职责描述
"""

import os
import re

def add_responsibility_to_index(file_path):
    """为INDEX.md文件添加职责描述"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 检查是否已有职责描述
        if '**核心职责**' in content or '**本文档职责**' in content:
            return False, "已有职责描述"
        
        # 查找第一个标题
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if not title_match:
            return False, "未找到标题"
        
        # 构建职责描述
        responsibility_block = f"""
> **核心职责**: 目录导航和文档索引
> **职责边界**: 
> - ✅ 本文档负责：目录结构导航、文档索引、快速定位
> - ❌ 本文档不负责：具体内容实现、详细设计
"""
        
        # 在标题后插入职责描述
        insert_pos = title_match.end()
        new_content = content[:insert_pos] + responsibility_block + content[insert_pos:]
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, "已添加职责: 目录导航和文档索引"
    
    except Exception as e:
        return False, f"错误: {str(e)}"

def main():
    """主函数"""
    root_path = r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY'
    
    print("=" * 80)
    print("为INDEX.md文件添加职责描述")
    print("=" * 80)
    print()
    
    # 定义需要处理的INDEX.md文件
    index_files = [
        '02_ALPHA_FACTORS_INDEX.md',
        'INDEX.md',
        '01_STANDARDS\\INDEX.md',
        '03_RISK_FACTORS\\INDEX.md',
        '05_BACKTEST\\INDEX.md',
        '05_BACKTEST\\ic_reports\\INDEX.md',
        '05_BACKTEST\\strategy_reports\\INDEX.md',
        '05_BACKTEST\\value_factors\\INDEX.md',
        '06_REGISTRY\\INDEX.md',
        '07_FACTOR_MONITORING\\INDEX.md',
        '10_MANUAL\\INDEX.md'
    ]
    
    # 批量添加职责描述
    success_count = 0
    fail_count = 0
    
    for rel_path in index_files:
        file_path = os.path.join(root_path, rel_path)
        
        if not os.path.exists(file_path):
            print(f"❌ {rel_path}: 文件不存在")
            fail_count += 1
            continue
        
        success, message = add_responsibility_to_index(file_path)
        
        if success:
            print(f"✅ {rel_path}: {message}")
            success_count += 1
        else:
            print(f"⏭️ {rel_path}: {message}")
            fail_count += 1
    
    # 处理FACTOR_VALIDATION_BLUEPRINT.md
    blueprint_file = os.path.join(root_path, '05_BACKTEST', 'FACTOR_VALIDATION_BLUEPRINT.md')
    if os.path.exists(blueprint_file):
        try:
            with open(blueprint_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            if '**核心职责**' not in content and '**本文档职责**' not in content:
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                if title_match:
                    responsibility_block = """
> **核心职责**: 因子验证蓝图和架构设计
> **职责边界**: 
> - ✅ 本文档负责：因子验证流程设计、验证标准制定、验证系统架构
> - ❌ 本文档不负责：具体验证实现、回测执行
"""
                    insert_pos = title_match.end()
                    new_content = content[:insert_pos] + responsibility_block + content[insert_pos:]
                    
                    with open(blueprint_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    print(f"✅ 05_BACKTEST\\FACTOR_VALIDATION_BLUEPRINT.md: 已添加职责")
                    success_count += 1
                else:
                    print(f"⏭️ 05_BACKTEST\\FACTOR_VALIDATION_BLUEPRINT.md: 未找到标题")
                    fail_count += 1
            else:
                print(f"⏭️ 05_BACKTEST\\FACTOR_VALIDATION_BLUEPRINT.md: 已有职责描述")
                fail_count += 1
        except Exception as e:
            print(f"❌ 05_BACKTEST\\FACTOR_VALIDATION_BLUEPRINT.md: 错误 {str(e)}")
            fail_count += 1
    
    print()
    print("=" * 80)
    print(f"处理完成: 成功 {success_count} 个, 跳过 {fail_count} 个")
    print("=" * 80)

if __name__ == '__main__':
    main()
