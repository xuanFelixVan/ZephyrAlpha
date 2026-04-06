#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为剩余文件添加职责描述
功能：为缺少职责描述的文件添加标准格式职责描述
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
    root_path = r'D:\ZephyrAlpha\docs'
    
    print("=" * 80)
    print("为剩余文件添加职责描述")
    print("=" * 80)
    print()
    
    # 定义文件和职责
    files_and_responsibilities = {
        '01_FRAMEWORK\\AUTOML_AUTOMATION_BLUEPRINT.md': 'AutoML自动化机器学习蓝图设计',
        '01_FRAMEWORK\\ENSEMBLE_LEARNING_BLUEPRINT.md': '模型集成学习蓝图设计',
        '01_FRAMEWORK\\LAYER_10_GOVERNANCE_COMPLIANCE_COMPLETENESS_ANALYSIS_FINAL.md': 'Layer 10治理与合规层完整性分析',
        '09_RESEARCH_INNOVATION\\BLUEPRINT.md': '研究与创新层蓝图设计'
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
