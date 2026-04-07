#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心职责描述质量提升
扫描并标记需要改进的职责描述
"""

import re
from pathlib import Path

def check_responsibility_quality(file_path, docs_dir):
    """检查职责描述质量"""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 提取responsibility字段
        match = re.search(r'responsibility:\s*\n((?:\s+-\s+.+\n)+)', content)
        if not match:
            return None
        
        responsibilities = match.group(1).strip().split('\n')
        responsibilities = [r.strip('- ').strip() for r in responsibilities]
        
        # 检查质量
        issues = []
        
        for resp in responsibilities:
            # 检查是否过于模糊
            if len(resp) < 10:
                issues.append(f"职责描述过短: '{resp}'")
            
            # 检查是否包含通用描述
            generic_terms = ['管理', '处理', '负责', '维护']
            if any(term in resp and len(resp) < 20 for term in generic_terms):
                issues.append(f"职责描述过于通用: '{resp}'")
        
        return {
            'file': str(file_path.relative_to(docs_dir)),
            'responsibilities': responsibilities,
            'issues': issues
        }
        
    except Exception as e:
        return None

def main():
    """主函数"""
    docs_dir = Path("D:/ZephyrAlpha/docs")
    
    # 统计
    total_files = 0
    quality_issues = []
    
    print("=== 开始检查职责描述质量 ===\n")
    
    # 遍历所有Markdown文件
    for md_file in docs_dir.rglob("*.md"):
        # 跳过归档目录
        if any(keyword in str(md_file) for keyword in ['06_ARCHIVE', '09_ARCHIVE', '99_ARCHIVE', 'archive']):
            continue
        
        result = check_responsibility_quality(md_file, docs_dir)
        if result and result['issues']:
            total_files += 1
            quality_issues.append(result)
            if len(quality_issues) <= 10:
                print(f"  ⚠️  {result['file']}")
                for issue in result['issues']:
                    print(f"      - {issue}")
    
    print(f"\n=== 检查完成 ===")
    print(f"发现问题文件: {total_files}")
    print(f"建议: 手动优化这些文件的职责描述")

if __name__ == "__main__":
    main()
