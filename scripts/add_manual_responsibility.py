#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
手动添加职责描述工具
功能：为特定文件手动添加职责描述
"""

import os
import re

def add_responsibility(file_path, responsibility_text):
    """为文件添加职责描述"""
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

def main():
    """主函数"""
    root_path = r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY'
    
    print("=" * 80)
    print("手动添加职责描述工具")
    print("=" * 80)
    print()
    
    # 定义文件和职责
    files_and_responsibilities = {
        'OPTIMIZATION_SUMMARY.md': '因子库优化成果总结和改进记录',
        '01_STANDARDS\\T.02.FE001.factor_definition.md': '因子命名规范和标准化定义规则',
        '03_RISK_FACTORS\\T.03.RF001.barra_style_factors.md': 'Barra风格因子体系定义（A股适配版）',
        '03_RISK_FACTORS\\T.03.RF002.industry_factors.md': '申万行业因子体系定义',
        '03_RISK_FACTORS\\T.03.RF003.tail_risk_factors.md': '尾部风险因子和极端风险度量定义',
        '03_RISK_FACTORS\\T.03.RM003.barra_optimizer.md': 'Barra风险模型和组合优化器设计',
        '03_RISK_FACTORS\\T.03.RM004.factor_transparency_report.md': '因子暴露度透明度报告生成',
        '05_BACKTEST\\value_factors\\PE_TTM_IC.md': 'PE_TTM因子IC验证结果记录'
    }
    
    # 批量添加职责描述
    success_count = 0
    fail_count = 0
    
    for rel_path, responsibility in files_and_responsibilities.items():
        file_path = os.path.join(root_path, rel_path)
        
        if not os.path.exists(file_path):
            print(f"❌ {rel_path}: 文件不存在")
            fail_count += 1
            continue
        
        success, message = add_responsibility(file_path, responsibility)
        
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
