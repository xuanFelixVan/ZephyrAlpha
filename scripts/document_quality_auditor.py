#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档质量审查工具
功能：
1. 文档质量评分
2. 文档规范检查
3. 文档完整性检查
4. 质量报告生成
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class QualityScore:
    total_score: float
    structure_score: float
    content_score: float
    format_score: float
    completeness_score: float
    issues: List[Dict]

@dataclass
class DocumentQualityAuditor:
    docs_dir: Path
    scores: List[QualityScore] = field(default_factory=list)
    
    def __post_init__(self):
        self.docs_dir = Path(self.docs_dir)
    
    def audit_all_documents(self) -> Dict:
        print("\n=== 文档质量审查 ===\n")
        
        md_files = list(self.docs_dir.rglob("*.md"))
        print(f"[1/5] 扫描文档: {len(md_files)}个")
        
        self.scores = []
        for md_file in md_files:
            score = self._audit_document(md_file)
            self.scores.append(score)
        
        print(f"[2/5] 质量评分完成")
        
        stats = self._calculate_statistics()
        print(f"[3/5] 统计分析完成")
        
        recommendations = self._generate_recommendations()
        print(f"[4/5] 生成建议完成")
        
        report = self._generate_report(stats, recommendations)
        print(f"[5/5] 生成报告完成")
        
        return report
    
    def _audit_document(self, md_file: Path) -> QualityScore:
        try:
            content = md_file.read_text(encoding='utf-8')
            
            structure_score = self._check_structure(content)
            content_score = self._check_content(content)
            format_score = self._check_format(content)
            completeness_score = self._check_completeness(content, md_file)
            
            total_score = (
                structure_score * 0.25 +
                content_score * 0.35 +
                format_score * 0.20 +
                completeness_score * 0.20
            )
            
            issues = self._identify_issues(content, md_file)
            
            return QualityScore(
                total_score=total_score,
                structure_score=structure_score,
                content_score=content_score,
                format_score=format_score,
                completeness_score=completeness_score,
                issues=issues
            )
        except Exception as e:
            return QualityScore(
                total_score=0.0,
                structure_score=0.0,
                content_score=0.0,
                format_score=0.0,
                completeness_score=0.0,
                issues=[{'type': 'read_error', 'message': str(e)}]
            )
    
    def _check_structure(self, content: str) -> float:
        score = 100.0
        
        if not re.search(r'^#\s+.+$', content, re.MULTILINE):
            score -= 20
        
        if not re.search(r'^##\s+.+$', content, re.MULTILINE):
            score -= 15
        
        if not re.search(r'^---\s*\n.*?\n---', content, re.DOTALL):
            score -= 10
        
        if not re.search(r'##\s*📝\s*维护记录', content):
            score -= 10
        
        if not re.search(r'##\s*🔗\s*相关文档', content):
            score -= 10
        
        return max(0, score)
    
    def _check_content(self, content: str) -> float:
        score = 100.0
        
        word_count = len(content.split())
        if word_count < 100:
            score -= 30
        elif word_count < 300:
            score -= 15
        
        if not re.search(r'职责|功能|目标|范围', content):
            score -= 20
        
        if not re.search(r'\*\*[^*]+\*\*', content):
            score -= 10
        
        if not re.search(r'`[^`]+`', content):
            score -= 5
        
        if not re.search(r'\[([^\]]+)\]\(([^)]+)\)', content):
            score -= 10
        
        return max(0, score)
    
    def _check_format(self, content: str) -> float:
        score = 100.0
        
        if re.search(r'^[^#\s]', content, re.MULTILINE):
            pass
        else:
            if not re.search(r'^#\s+', content, re.MULTILINE):
                score -= 20
        
        if re.search(r'\s{2,}', content):
            score -= 5
        
        if re.search(r'\t', content):
            score -= 5
        
        if not re.search(r'\n\n', content):
            score -= 10
        
        return max(0, score)
    
    def _check_completeness(self, content: str, md_file: Path) -> float:
        score = 100.0
        
        if md_file.name == 'INDEX.md':
            if not re.search(r'##\s*📁\s*目录概要', content):
                score -= 15
            if not re.search(r'##\s*📊\s*统计', content):
                score -= 15
        
        if not re.search(r'module_id:', content):
            score -= 10
        
        if not re.search(r'version:', content):
            score -= 10
        
        if not re.search(r'status:', content):
            score -= 10
        
        if not re.search(r'created_date:', content):
            score -= 10
        
        return max(0, score)
    
    def _identify_issues(self, content: str, md_file: Path) -> List[Dict]:
        issues = []
        
        if not re.search(r'^#\s+.+$', content, re.MULTILINE):
            issues.append({
                'type': 'missing_title',
                'severity': 'high',
                'message': '缺少文档标题'
            })
        
        if not re.search(r'^---\s*\n.*?\n---', content, re.DOTALL):
            issues.append({
                'type': 'missing_frontmatter',
                'severity': 'medium',
                'message': '缺少YAML前置信息'
            })
        
        if len(content.split()) < 100:
            issues.append({
                'type': 'content_too_short',
                'severity': 'medium',
                'message': '文档内容过短'
            })
        
        if not re.search(r'##\s*📝\s*维护记录', content):
            issues.append({
                'type': 'missing_maintenance_section',
                'severity': 'low',
                'message': '缺少维护记录章节'
            })
        
        return issues
    
    def _calculate_statistics(self) -> Dict:
        if not self.scores:
            return {}
        
        total_scores = [s.total_score for s in self.scores]
        structure_scores = [s.structure_score for s in self.scores]
        content_scores = [s.content_score for s in self.scores]
        format_scores = [s.format_score for s in self.scores]
        completeness_scores = [s.completeness_score for s in self.scores]
        
        return {
            'total_documents': len(self.scores),
            'average_score': sum(total_scores) / len(total_scores),
            'score_distribution': {
                'excellent': len([s for s in total_scores if s >= 90]),
                'good': len([s for s in total_scores if 80 <= s < 90]),
                'fair': len([s for s in total_scores if 60 <= s < 80]),
                'poor': len([s for s in total_scores if s < 60])
            },
            'dimension_scores': {
                'structure': sum(structure_scores) / len(structure_scores),
                'content': sum(content_scores) / len(content_scores),
                'format': sum(format_scores) / len(format_scores),
                'completeness': sum(completeness_scores) / len(completeness_scores)
            },
            'total_issues': sum(len(s.issues) for s in self.scores)
        }
    
    def _generate_recommendations(self) -> List[Dict]:
        recommendations = []
        
        low_score_docs = [s for s in self.scores if s.total_score < 80]
        if low_score_docs:
            recommendations.append({
                'priority': 'high',
                'category': 'quality_improvement',
                'action': f'提升{len(low_score_docs)}个低质量文档',
                'impact': f'可提升整体质量评分{(len(self.scores) - len(low_score_docs)) / len(self.scores) * 10:.1f}分'
            })
        
        missing_title_docs = [s for s in self.scores if any(i['type'] == 'missing_title' for i in s.issues)]
        if missing_title_docs:
            recommendations.append({
                'priority': 'high',
                'category': 'structure',
                'action': f'为{len(missing_title_docs)}个文档添加标题',
                'impact': '提升文档结构完整性'
            })
        
        short_content_docs = [s for s in self.scores if any(i['type'] == 'content_too_short' for i in s.issues)]
        if short_content_docs:
            recommendations.append({
                'priority': 'medium',
                'category': 'content',
                'action': f'扩充{len(short_content_docs)}个内容过短的文档',
                'impact': '提升文档内容质量'
            })
        
        return recommendations
    
    def _generate_report(self, stats: Dict, recommendations: List[Dict]) -> Dict:
        return {
            'summary': {
                'audit_date': datetime.now().isoformat(),
                'total_documents': stats['total_documents'],
                'average_score': round(stats['average_score'], 2),
                'quality_level': self._get_quality_level(stats['average_score'])
            },
            'statistics': stats,
            'recommendations': recommendations,
            'detailed_scores': [
                {
                    'file': str(md_file.relative_to(self.docs_dir)),
                    'total_score': round(score.total_score, 2),
                    'structure_score': round(score.structure_score, 2),
                    'content_score': round(score.content_score, 2),
                    'format_score': round(score.format_score, 2),
                    'completeness_score': round(score.completeness_score, 2),
                    'issues': score.issues
                }
                for md_file, score in zip(self.docs_dir.rglob("*.md"), self.scores)
            ][:20]
        }
    
    def _get_quality_level(self, score: float) -> str:
        if score >= 90:
            return '优秀'
        elif score >= 80:
            return '良好'
        elif score >= 60:
            return '一般'
        else:
            return '较差'
    
    def save_report(self, report: Dict, output_file: Path):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n报告已保存: {output_file}")

def main():
    docs_dir = Path("D:/ZephyrAlpha/docs")
    auditor = DocumentQualityAuditor(docs_dir)
    
    report = auditor.audit_all_documents()
    
    print(f"\n=== 质量审查结果 ===")
    print(f"总文档数: {report['summary']['total_documents']}")
    print(f"平均得分: {report['summary']['average_score']}")
    print(f"质量等级: {report['summary']['quality_level']}")
    
    print(f"\n评分分布:")
    for level, count in report['statistics']['score_distribution'].items():
        print(f"  {level}: {count}个")
    
    print(f"\n维度得分:")
    for dimension, score in report['statistics']['dimension_scores'].items():
        print(f"  {dimension}: {score:.2f}")
    
    output_file = docs_dir.parent / "docs/09_AUDIT/REPORTS/document_quality_audit_report.json"
    auditor.save_report(report, output_file)

if __name__ == "__main__":
    main()
