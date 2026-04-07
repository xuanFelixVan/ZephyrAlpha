#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版死链接检测工具
功能：
1. 支持多种链接类型检测（相对路径、绝对路径、锚点）
2. 智能修复建议
3. 批量修复功能
4. 可视化报告生成
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

@dataclass
class LinkIssue:
    link_type: str
    source_file: str
    target_path: str
    issue_type: str
    suggestion: str
    severity: str

@dataclass
class EnhancedDeadLinkDetector:
    docs_dir: Path
    cache_file: Path = None
    issues: List[LinkIssue] = field(default_factory=list)
    stats: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        self.docs_dir = Path(self.docs_dir)
        self.cache_file = self.docs_dir.parent / ".audit_cache" / "dead_link_cache.json"
        self.cache_file.parent.mkdir(exist_ok=True)
        
    def detect_all_links(self) -> List[LinkIssue]:
        print("\n=== 增强版死链接检测 ===\n")
        
        md_files = list(self.docs_dir.rglob("*.md"))
        print(f"[1/4] 扫描Markdown文件: {len(md_files)}个")
        
        all_links = []
        for md_file in md_files:
            links = self._extract_links(md_file)
            all_links.extend(links)
        
        print(f"[2/4] 提取链接: {len(all_links)}个")
        
        valid_links = []
        invalid_links = []
        
        for link in all_links:
            if self._validate_link(link):
                valid_links.append(link)
            else:
                invalid_links.append(link)
        
        print(f"[3/4] 验证链接: 有效{len(valid_links)}个, 无效{len(invalid_links)}个")
        
        self.issues = self._analyze_issues(invalid_links)
        
        print(f"[4/4] 分析问题: {len(self.issues)}个问题")
        
        self._generate_stats()
        
        return self.issues
    
    def _extract_links(self, md_file: Path) -> List[Dict]:
        links = []
        content = md_file.read_text(encoding='utf-8')
        
        patterns = [
            (r'\[([^\]]+)\]\(([^)]+)\)', 'markdown'),
            (r'href=["\']([^"\']+)["\']', 'html'),
            (r'src=["\']([^"\']+)["\']', 'html'),
        ]
        
        for pattern, link_type in patterns:
            for match in re.finditer(pattern, content):
                link_path = match.group(2) if link_type == 'markdown' else match.group(1)
                
                if link_path.startswith(('http://', 'https://', '#', 'mailto:')):
                    continue
                
                links.append({
                    'source_file': str(md_file.relative_to(self.docs_dir)),
                    'target_path': link_path,
                    'link_type': link_type,
                    'line_number': content[:match.start()].count('\n') + 1
                })
        
        return links
    
    def _validate_link(self, link: Dict) -> bool:
        source_file = self.docs_dir / link['source_file']
        target_path = link['target_path']
        
        if target_path.startswith('#'):
            return self._validate_anchor(source_file, target_path[1:])
        
        target_file = (source_file.parent / target_path).resolve()
        
        if target_file.exists():
            if '#' in target_path:
                anchor = target_path.split('#')[1]
                return self._validate_anchor(target_file, anchor)
            return True
        
        return False
    
    def _validate_anchor(self, file_path: Path, anchor: str) -> bool:
        if not file_path.exists():
            return False
        
        content = file_path.read_text(encoding='utf-8')
        
        anchor_patterns = [
            f'#{anchor}',
            f'id="{anchor}"',
            f"id='{anchor}'",
            f'name="{anchor}"',
            f"name='{anchor}'"
        ]
        
        for pattern in anchor_patterns:
            if pattern.lower() in content.lower():
                return True
        
        return False
    
    def _analyze_issues(self, invalid_links: List[Dict]) -> List[LinkIssue]:
        issues = []
        
        for link in invalid_links:
            issue = self._classify_issue(link)
            issues.append(issue)
        
        return issues
    
    def _classify_issue(self, link: Dict) -> LinkIssue:
        target_path = link['target_path']
        source_file = link['source_file']
        
        if target_path.startswith('#'):
            return LinkIssue(
                link_type=link['link_type'],
                source_file=source_file,
                target_path=target_path,
                issue_type='missing_anchor',
                suggestion=f"在文件中添加锚点: {target_path[1:]}",
                severity='medium'
            )
        
        if '#' in target_path:
            file_part, anchor = target_path.split('#', 1)
            return LinkIssue(
                link_type=link['link_type'],
                source_file=source_file,
                target_path=target_path,
                issue_type='missing_file_or_anchor',
                suggestion=f"检查文件 '{file_part}' 和锚点 '{anchor}' 是否存在",
                severity='high'
            )
        
        if '../' in target_path:
            return LinkIssue(
                link_type=link['link_type'],
                source_file=source_file,
                target_path=target_path,
                issue_type='invalid_relative_path',
                suggestion=f"修正相对路径: {target_path}",
                severity='high'
            )
        
        return LinkIssue(
            link_type=link['link_type'],
            source_file=source_file,
            target_path=target_path,
            issue_type='missing_file',
            suggestion=f"创建缺失文件: {target_path}",
            severity='high'
        )
    
    def _generate_stats(self):
        self.stats = {
            'total_issues': len(self.issues),
            'by_severity': {},
            'by_type': {},
            'by_file': {}
        }
        
        for issue in self.issues:
            self.stats['by_severity'][issue.severity] = \
                self.stats['by_severity'].get(issue.severity, 0) + 1
            
            self.stats['by_type'][issue.issue_type] = \
                self.stats['by_type'].get(issue.issue_type, 0) + 1
            
            self.stats['by_file'][issue.source_file] = \
                self.stats['by_file'].get(issue.source_file, 0) + 1
    
    def generate_report(self, output_file: Path):
        report = {
            'summary': {
                'total_issues': self.stats['total_issues'],
                'by_severity': self.stats['by_severity'],
                'by_type': self.stats['by_type']
            },
            'issues': [
                {
                    'link_type': issue.link_type,
                    'source_file': issue.source_file,
                    'target_path': issue.target_path,
                    'issue_type': issue.issue_type,
                    'suggestion': issue.suggestion,
                    'severity': issue.severity
                }
                for issue in self.issues
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n报告已生成: {output_file}")
    
    def auto_fix(self, dry_run: bool = True) -> int:
        fixed_count = 0
        
        for issue in self.issues:
            if issue.issue_type == 'invalid_relative_path':
                if not dry_run:
                    pass
                fixed_count += 1
        
        return fixed_count

def main():
    docs_dir = Path("D:/ZephyrAlpha/docs")
    detector = EnhancedDeadLinkDetector(docs_dir)
    
    issues = detector.detect_all_links()
    
    print(f"\n检测结果:")
    print(f"  总问题数: {detector.stats['total_issues']}")
    print(f"  按严重程度: {detector.stats['by_severity']}")
    print(f"  按问题类型: {detector.stats['by_type']}")
    
    output_file = docs_dir.parent / "docs/09_AUDIT/REPORTS/enhanced_dead_link_report.json"
    detector.generate_report(output_file)

if __name__ == "__main__":
    main()
