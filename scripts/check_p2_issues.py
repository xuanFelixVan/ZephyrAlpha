"""
P2级遗留问题检查脚本
用途：检查路径引用冗余和文档质量问题
创建时间：2026-04-07
"""

import re
from pathlib import Path
from typing import Dict, List

BLUEPRINTS_DIR = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS")


def read_document(filepath: Path) -> str:
    """读取文档内容"""
    encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'latin-1']
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    return ""


def check_path_references(content: str) -> Dict:
    """检查路径引用"""
    # 统计../使用次数
    parent_dir_count = content.count('../')
    
    # 查找所有链接
    links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
    
    # 查找可能有问题的链接
    problematic_links = []
    for text, link in links:
        if link.startswith('../'):
            # 计算../数量
            parent_count = link.count('../')
            if parent_count > 3:
                problematic_links.append({
                    "text": text,
                    "link": link,
                    "parent_count": parent_count
                })
    
    return {
        "total_parent_dir_count": parent_dir_count,
        "problematic_links": problematic_links
    }


def check_document_quality(filepath: Path, content: str) -> Dict:
    """检查文档质量"""
    issues = []
    
    # 检查YAML头部
    if not content.startswith('---'):
        issues.append("缺少YAML头部")
    
    # 检查文档治理章节
    if '文档治理' not in content:
        issues.append("缺少文档治理章节")
    
    # 检查标题
    if not re.search(r'^#\s+', content, re.MULTILINE):
        issues.append("缺少主标题")
    
    # 检查编码问题
    if '�' in content or '�' in content:
        issues.append("存在编码问题")
    
    # 检查空行过多
    if '\n\n\n\n' in content:
        issues.append("存在过多空行")
    
    return {
        "filename": filepath.name,
        "issues": issues,
        "issue_count": len(issues)
    }


def analyze_p2_issues():
    """分析P2级问题"""
    print("="*80)
    print("P2级遗留问题详细分析")
    print("="*80)
    
    # 1. 检查路径引用冗余
    print("\n" + "="*80)
    print("1. 路径引用冗余检查")
    print("="*80)
    
    path_issues = []
    for filepath in BLUEPRINTS_DIR.glob("*.md"):
        if filepath.name == "INDEX.md":
            continue
        
        content = read_document(filepath)
        path_check = check_path_references(content)
        
        if path_check['total_parent_dir_count'] > 5:
            path_issues.append({
                "filename": filepath.name,
                "parent_dir_count": path_check['total_parent_dir_count'],
                "problematic_links": path_check['problematic_links']
            })
    
    if path_issues:
        print(f"\n发现 {len(path_issues)} 个路径引用冗余的文档:\n")
        print("| 文档名称 | ../使用次数 | 问题链接数 |")
        print("|----------|-------------|------------|")
        for issue in sorted(path_issues, key=lambda x: x['parent_dir_count'], reverse=True):
            print(f"| {issue['filename']} | {issue['parent_dir_count']} | {len(issue['problematic_links'])} |")
        
        # 显示具体问题链接
        print("\n详细问题链接:")
        for issue in path_issues[:5]:
            if issue['problematic_links']:
                print(f"\n{issue['filename']}:")
                for link in issue['problematic_links'][:3]:
                    print(f"  - [{link['text']}]({link['link']})")
    else:
        print("\n✅ 未发现路径引用冗余问题")
    
    # 2. 检查文档质量问题
    print("\n" + "="*80)
    print("2. 文档质量检查")
    print("="*80)
    
    quality_issues = []
    for filepath in BLUEPRINTS_DIR.glob("*.md"):
        if filepath.name == "INDEX.md":
            continue
        
        content = read_document(filepath)
        quality_check = check_document_quality(filepath, content)
        
        if quality_check['issue_count'] > 0:
            quality_issues.append(quality_check)
    
    if quality_issues:
        print(f"\n发现 {len(quality_issues)} 个存在质量问题的文档:\n")
        print("| 文档名称 | 问题数 | 具体问题 |")
        print("|----------|--------|----------|")
        for issue in quality_issues:
            print(f"| {issue['filename']} | {issue['issue_count']} | {', '.join(issue['issues'])} |")
    else:
        print("\n✅ 未发现文档质量问题")
    
    # 3. 生成修复建议
    print("\n" + "="*80)
    print("修复建议")
    print("="*80)
    
    if path_issues:
        print(f"\n路径引用冗余 ({len(path_issues)}个):")
        print("  - 建议: 优化链接路径，减少../使用")
        print("  - 优先级: P2（低优先级）")
        print("  - 影响: 文档可维护性")
    
    if quality_issues:
        print(f"\n文档质量问题 ({len(quality_issues)}个):")
        print("  - 建议: 补充缺失的YAML头部或文档治理章节")
        print("  - 优先级: P2（低优先级）")
        print("  - 影响: 文档规范性")
    
    return {
        "path_issues": path_issues,
        "quality_issues": quality_issues
    }


if __name__ == "__main__":
    results = analyze_p2_issues()
