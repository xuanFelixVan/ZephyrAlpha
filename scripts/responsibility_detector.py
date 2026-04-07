#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
职责检测工具
功能：
1. 语义分析文档职责
2. 检测职责相似度
3. 生成职责关系图
4. 提供合并建议
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class ResponsibilityInfo:
    file_path: str
    title: str
    description: str
    keywords: Set[str]
    section_count: int
    word_count: int

@dataclass
class ResponsibilityDetector:
    docs_dir: Path
    responsibilities: List[ResponsibilityInfo] = field(default_factory=list)
    similarity_matrix: Dict[Tuple[str, str], float] = field(default_factory=dict)
    
    def __post_init__(self):
        self.docs_dir = Path(self.docs_dir)
    
    def analyze_responsibilities(self) -> List[ResponsibilityInfo]:
        print("\n=== 职责检测分析 ===\n")
        
        md_files = list(self.docs_dir.rglob("*.md"))
        print(f"[1/4] 扫描Markdown文件: {len(md_files)}个")
        
        self.responsibilities = []
        for md_file in md_files:
            resp_info = self._extract_responsibility(md_file)
            if resp_info:
                self.responsibilities.append(resp_info)
        
        print(f"[2/4] 提取职责信息: {len(self.responsibilities)}个")
        
        self._calculate_similarity_matrix()
        print(f"[3/4] 计算职责相似度: {len(self.similarity_matrix)}对")
        
        duplicate_groups = self._find_duplicates()
        print(f"[4/4] 检测职责重复: {len(duplicate_groups)}组")
        
        return self.responsibilities
    
    def _extract_responsibility(self, md_file: Path) -> ResponsibilityInfo:
        try:
            content = md_file.read_text(encoding='utf-8')
            
            title = self._extract_title(content)
            description = self._extract_description(content)
            keywords = self._extract_keywords(content)
            section_count = self._count_sections(content)
            word_count = len(content.split())
            
            return ResponsibilityInfo(
                file_path=str(md_file.relative_to(self.docs_dir)),
                title=title,
                description=description,
                keywords=keywords,
                section_count=section_count,
                word_count=word_count
            )
        except Exception as e:
            print(f"处理文件失败 {md_file}: {e}")
            return None
    
    def _extract_title(self, content: str) -> str:
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1) if match else "未命名文档"
    
    def _extract_description(self, content: str) -> str:
        lines = content.split('\n')
        description_lines = []
        
        for i, line in enumerate(lines):
            if line.startswith('#') and i > 0:
                break
            if line.strip() and not line.startswith('#'):
                description_lines.append(line.strip())
        
        return ' '.join(description_lines[:3])
    
    def _extract_keywords(self, content: str) -> Set[str]:
        keywords = set()
        
        keyword_patterns = [
            r'职责[：:]\s*(.+)',
            r'功能[：:]\s*(.+)',
            r'目标[：:]\s*(.+)',
            r'范围[：:]\s*(.+)',
        ]
        
        for pattern in keyword_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                words = re.findall(r'[\w\u4e00-\u9fff]+', match)
                keywords.update(words)
        
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            title_words = re.findall(r'[\w\u4e00-\u9fff]+', title_match.group(1))
            keywords.update(title_words)
        
        return keywords
    
    def _count_sections(self, content: str) -> int:
        return len(re.findall(r'^#{1,6}\s+', content, re.MULTILINE))
    
    def _calculate_similarity_matrix(self):
        for i, resp1 in enumerate(self.responsibilities):
            for j, resp2 in enumerate(self.responsibilities):
                if i < j:
                    similarity = self._calculate_similarity(resp1, resp2)
                    if similarity > 0.3:
                        self.similarity_matrix[(resp1.file_path, resp2.file_path)] = similarity
    
    def _calculate_similarity(self, resp1: ResponsibilityInfo, resp2: ResponsibilityInfo) -> float:
        title_similarity = self._jaccard_similarity(
            set(resp1.title.split()),
            set(resp2.title.split())
        )
        
        keyword_similarity = self._jaccard_similarity(
            resp1.keywords,
            resp2.keywords
        )
        
        description_similarity = self._jaccard_similarity(
            set(resp1.description.split()),
            set(resp2.description.split())
        )
        
        weighted_similarity = (
            title_similarity * 0.4 +
            keyword_similarity * 0.4 +
            description_similarity * 0.2
        )
        
        return weighted_similarity
    
    def _jaccard_similarity(self, set1: Set[str], set2: Set[str]) -> float:
        if not set1 or not set2:
            return 0.0
        
        intersection = set1 & set2
        union = set1 | set2
        
        return len(intersection) / len(union) if union else 0.0
    
    def _find_duplicates(self) -> List[List[str]]:
        duplicate_groups = []
        processed = set()
        
        for (file1, file2), similarity in sorted(
            self.similarity_matrix.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            if similarity > 0.7:
                if file1 not in processed and file2 not in processed:
                    group = [file1, file2]
                    processed.add(file1)
                    processed.add(file2)
                    
                    for (f1, f2), sim in self.similarity_matrix.items():
                        if sim > 0.7:
                            if f1 in group and f2 not in processed:
                                group.append(f2)
                                processed.add(f2)
                            elif f2 in group and f1 not in processed:
                                group.append(f1)
                                processed.add(f1)
                    
                    duplicate_groups.append(group)
        
        return duplicate_groups
    
    def generate_report(self, output_file: Path):
        report = {
            'summary': {
                'total_documents': len(self.responsibilities),
                'total_similar_pairs': len(self.similarity_matrix),
                'high_similarity_pairs': sum(1 for s in self.similarity_matrix.values() if s > 0.7),
                'duplicate_groups': len(self._find_duplicates())
            },
            'similarities': [
                {
                    'file1': files[0],
                    'file2': files[1],
                    'similarity': round(sim, 3)
                }
                for files, sim in sorted(
                    self.similarity_matrix.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:20]
            ],
            'duplicate_groups': self._find_duplicates(),
            'recommendations': self._generate_recommendations()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n报告已生成: {output_file}")
    
    def _generate_recommendations(self) -> List[Dict]:
        recommendations = []
        
        duplicate_groups = self._find_duplicates()
        
        for i, group in enumerate(duplicate_groups, 1):
            recommendations.append({
                'type': 'merge',
                'priority': 'high',
                'description': f'合并重复职责文档组{i}',
                'files': group,
                'action': '建议合并这些职责相似的文档'
            })
        
        for (file1, file2), similarity in self.similarity_matrix.items():
            if 0.5 < similarity <= 0.7:
                recommendations.append({
                    'type': 'review',
                    'priority': 'medium',
                    'description': f'审查职责相似文档',
                    'files': [file1, file2],
                    'action': f'相似度{similarity:.2%}，建议审查是否有重复内容'
                })
        
        return recommendations

def main():
    docs_dir = Path("D:/ZephyrAlpha/docs")
    detector = ResponsibilityDetector(docs_dir)
    
    responsibilities = detector.analyze_responsibilities()
    
    print(f"\n检测结果:")
    print(f"  总文档数: {len(responsibilities)}")
    print(f"  相似文档对: {len(detector.similarity_matrix)}")
    print(f"  高相似度文档对: {sum(1 for s in detector.similarity_matrix.values() if s > 0.7)}")
    
    output_file = docs_dir.parent / "docs/09_AUDIT/REPORTS/responsibility_detection_report.json"
    detector.generate_report(output_file)

if __name__ == "__main__":
    main()
