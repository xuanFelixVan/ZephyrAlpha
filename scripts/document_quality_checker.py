#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档质量定期检查工具
定期扫描文档系统，生成质量报告
"""

import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

class DocumentQualityChecker:
    def __init__(self):
        self.docs_root = Path('docs')
        self.results = {
            'scan_time': datetime.now().isoformat(),
            'summary': {},
            'details': {}
        }
    
    def check_yaml_metadata(self):
        """检查YAML元数据完整性"""
        print("🔍 检查YAML元数据完整性...")
        
        stats = {
            'total_files': 0,
            'files_with_yaml': 0,
            'files_without_yaml': 0,
            'yaml_fields': defaultdict(int),
            'missing_fields': defaultdict(int)
        }
        
        required_fields = ['version', 'module_id', 'responsibility_boundary', 'layer']
        
        for md_file in self.docs_root.rglob('*.md'):
            stats['total_files'] += 1
            
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue
            
            # 检查YAML头部
            if content.strip().startswith('---'):
                stats['files_with_yaml'] += 1
                
                # 提取YAML字段
                yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                    
                    for field in required_fields:
                        if re.search(rf'^{field}:', yaml_content, re.MULTILINE):
                            stats['yaml_fields'][field] += 1
                        else:
                            stats['missing_fields'][field] += 1
            else:
                stats['files_without_yaml'] += 1
                for field in required_fields:
                    stats['missing_fields'][field] += 1
        
        stats['yaml_completeness'] = stats['files_with_yaml'] / max(stats['total_files'], 1) * 100
        self.results['details']['yaml_metadata'] = stats
        
        print(f"  ✓ 扫描文件: {stats['total_files']}")
        print(f"  ✓ YAML完整率: {stats['yaml_completeness']:.2f}%")
        
        return stats
    
    def check_document_structure(self):
        """检查文档结构规范性"""
        print("🔍 检查文档结构规范性...")
        
        stats = {
            'total_files': 0,
            'files_with_title': 0,
            'files_with_toc': 0,
            'files_with_sections': 0,
            'files_with_links': 0,
            'avg_sections': 0,
            'avg_links': 0
        }
        
        total_sections = 0
        total_links = 0
        
        for md_file in self.docs_root.rglob('*.md'):
            stats['total_files'] += 1
            
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue
            
            # 检查标题
            if re.search(r'^#\s+', content, re.MULTILINE):
                stats['files_with_title'] += 1
            
            # 检查目录
            if re.search(r'##\s+目录|##\s+Table of Contents', content, re.IGNORECASE):
                stats['files_with_toc'] += 1
            
            # 检查章节
            sections = len(re.findall(r'^##\s+', content, re.MULTILINE))
            if sections > 0:
                stats['files_with_sections'] += 1
                total_sections += sections
            
            # 检查链接
            links = len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content))
            if links > 0:
                stats['files_with_links'] += 1
                total_links += links
        
        stats['avg_sections'] = total_sections / max(stats['total_files'], 1)
        stats['avg_links'] = total_links / max(stats['total_files'], 1)
        
        self.results['details']['document_structure'] = stats
        
        print(f"  ✓ 标题覆盖率: {stats['files_with_title'] / max(stats['total_files'], 1) * 100:.2f}%")
        print(f"  ✓ 平均章节数: {stats['avg_sections']:.2f}")
        print(f"  ✓ 平均链接数: {stats['avg_links']:.2f}")
        
        return stats
    
    def check_document_freshness(self):
        """检查文档新鲜度"""
        print("🔍 检查文档新鲜度...")
        
        stats = {
            'total_files': 0,
            'recent_files': 0,  # 30天内修改
            'stale_files': 0,   # 90天以上未修改
            'very_stale_files': 0,  # 180天以上未修改
            'oldest_file': None,
            'newest_file': None
        }
        
        now = datetime.now()
        oldest_time = now
        newest_time = datetime(1970, 1, 1)
        
        for md_file in self.docs_root.rglob('*.md'):
            stats['total_files'] += 1
            
            try:
                mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                age_days = (now - mtime).days
                
                if age_days <= 30:
                    stats['recent_files'] += 1
                elif age_days > 90:
                    stats['stale_files'] += 1
                    if age_days > 180:
                        stats['very_stale_files'] += 1
                
                if mtime < oldest_time:
                    oldest_time = mtime
                    stats['oldest_file'] = str(md_file.relative_to(self.docs_root))
                
                if mtime > newest_time:
                    newest_time = mtime
                    stats['newest_file'] = str(md_file.relative_to(self.docs_root))
            
            except Exception:
                continue
        
        stats['freshness_rate'] = stats['recent_files'] / max(stats['total_files'], 1) * 100
        stats['stale_rate'] = stats['stale_files'] / max(stats['total_files'], 1) * 100
        
        self.results['details']['document_freshness'] = stats
        
        print(f"  ✓ 新鲜度: {stats['freshness_rate']:.2f}%")
        print(f"  ✓ 过期率: {stats['stale_rate']:.2f}%")
        
        return stats
    
    def check_index_completeness(self):
        """检查索引完整性"""
        print("🔍 检查索引完整性...")
        
        stats = {
            'total_directories': 0,
            'directories_with_index': 0,
            'directories_without_index': 0,
            'missing_index_dirs': []
        }
        
        for directory in self.docs_root.rglob('*'):
            if directory.is_dir():
                stats['total_directories'] += 1
                
                has_index = any(
                    (directory / idx).exists()
                    for idx in ['INDEX.md', 'index.md', 'README.md']
                )
                
                if has_index:
                    stats['directories_with_index'] += 1
                else:
                    stats['directories_without_index'] += 1
                    stats['missing_index_dirs'].append(
                        str(directory.relative_to(self.docs_root))
                    )
        
        stats['index_coverage'] = stats['directories_with_index'] / max(stats['total_directories'], 1) * 100
        
        self.results['details']['index_completeness'] = stats
        
        print(f"  ✓ 索引覆盖率: {stats['index_coverage']:.2f}%")
        print(f"  ✓ 缺少索引目录: {stats['directories_without_index']}")
        
        return stats
    
    def calculate_quality_score(self):
        """计算文档质量总分"""
        print("📊 计算文档质量总分...")
        
        score = 0
        max_score = 100
        
        # YAML元数据完整性 (30分)
        yaml_completeness = self.results['details'].get('yaml_metadata', {}).get('yaml_completeness', 0)
        score += yaml_completeness * 0.3
        
        # 文档结构规范性 (20分)
        structure_stats = self.results['details'].get('document_structure', {})
        title_coverage = structure_stats.get('files_with_title', 0) / max(structure_stats.get('total_files', 1), 1) * 100
        score += title_coverage * 0.2
        
        # 文档新鲜度 (20分)
        freshness_stats = self.results['details'].get('document_freshness', {})
        freshness_rate = freshness_stats.get('freshness_rate', 0)
        score += freshness_rate * 0.2
        
        # 索引完整性 (30分)
        index_stats = self.results['details'].get('index_completeness', {})
        index_coverage = index_stats.get('index_coverage', 0)
        score += index_coverage * 0.3
        
        self.results['summary'] = {
            'quality_score': round(score, 2),
            'grade': self._get_grade(score),
            'yaml_completeness': round(yaml_completeness, 2),
            'title_coverage': round(title_coverage, 2),
            'freshness_rate': round(freshness_rate, 2),
            'index_coverage': round(index_coverage, 2)
        }
        
        print(f"  ✓ 质量总分: {score:.2f}/100")
        print(f"  ✓ 质量等级: {self._get_grade(score)}")
        
        return score
    
    def _get_grade(self, score):
        """获取质量等级"""
        if score >= 90:
            return 'A+ (优秀)'
        elif score >= 80:
            return 'A (良好)'
        elif score >= 70:
            return 'B (中等)'
        elif score >= 60:
            return 'C (及格)'
        else:
            return 'D (需改进)'
    
    def generate_report(self):
        """生成质量报告"""
        output_dir = Path('docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d')
        report_file = output_dir / f'QUALITY_REPORT_{timestamp}.md'
        json_file = output_dir / f'QUALITY_REPORT_{timestamp}.json'
        
        # 生成Markdown报告
        report_lines = [
            "# 文档质量定期检查报告",
            "",
            f"> **检查时间**: {self.results['scan_time']}",
            "",
            "## 📊 质量总评",
            "",
            f"- **质量总分**: {self.results['summary']['quality_score']}/100",
            f"- **质量等级**: {self.results['summary']['grade']}",
            "",
            "### 分项得分",
            "",
            f"- **YAML元数据完整性**: {self.results['summary']['yaml_completeness']}% (权重30%)",
            f"- **文档结构规范性**: {self.results['summary']['title_coverage']}% (权重20%)",
            f"- **文档新鲜度**: {self.results['summary']['freshness_rate']}% (权重20%)",
            f"- **索引完整性**: {self.results['summary']['index_coverage']}% (权重30%)",
            "",
            "---",
            "",
            "## 📋 详细检查结果",
            ""
        ]
        
        # YAML元数据
        yaml_stats = self.results['details'].get('yaml_metadata', {})
        report_lines.extend([
            "### 1. YAML元数据完整性",
            "",
            f"- **扫描文件数**: {yaml_stats.get('total_files', 0)}",
            f"- **包含YAML文件数**: {yaml_stats.get('files_with_yaml', 0)}",
            f"- **缺少YAML文件数**: {yaml_stats.get('files_without_yaml', 0)}",
            f"- **YAML完整率**: {yaml_stats.get('yaml_completeness', 0):.2f}%",
            "",
            "**必需字段覆盖率**:",
            ""
        ])
        
        for field, count in yaml_stats.get('yaml_fields', {}).items():
            coverage = count / max(yaml_stats.get('total_files', 1), 1) * 100
            report_lines.append(f"- {field}: {coverage:.2f}%")
        
        # 文档结构
        structure_stats = self.results['details'].get('document_structure', {})
        report_lines.extend([
            "",
            "### 2. 文档结构规范性",
            "",
            f"- **标题覆盖率**: {structure_stats.get('files_with_title', 0) / max(structure_stats.get('total_files', 1), 1) * 100:.2f}%",
            f"- **目录覆盖率**: {structure_stats.get('files_with_toc', 0) / max(structure_stats.get('total_files', 1), 1) * 100:.2f}%",
            f"- **平均章节数**: {structure_stats.get('avg_sections', 0):.2f}",
            f"- **平均链接数**: {structure_stats.get('avg_links', 0):.2f}",
            ""
        ])
        
        # 文档新鲜度
        freshness_stats = self.results['details'].get('document_freshness', {})
        report_lines.extend([
            "### 3. 文档新鲜度",
            "",
            f"- **最近30天修改**: {freshness_stats.get('recent_files', 0)} ({freshness_stats.get('freshness_rate', 0):.2f}%)",
            f"- **超过90天未修改**: {freshness_stats.get('stale_files', 0)} ({freshness_stats.get('stale_rate', 0):.2f}%)",
            f"- **超过180天未修改**: {freshness_stats.get('very_stale_files', 0)}",
            f"- **最旧文件**: {freshness_stats.get('oldest_file', 'N/A')}",
            f"- **最新文件**: {freshness_stats.get('newest_file', 'N/A')}",
            ""
        ])
        
        # 索引完整性
        index_stats = self.results['details'].get('index_completeness', {})
        report_lines.extend([
            "### 4. 索引完整性",
            "",
            f"- **总目录数**: {index_stats.get('total_directories', 0)}",
            f"- **包含索引目录数**: {index_stats.get('directories_with_index', 0)}",
            f"- **缺少索引目录数**: {index_stats.get('directories_without_index', 0)}",
            f"- **索引覆盖率**: {index_stats.get('index_coverage', 0):.2f}%",
            ""
        ])
        
        if index_stats.get('missing_index_dirs'):
            report_lines.extend([
                "**缺少索引的目录** (前10个):",
                ""
            ])
            for dir_path in index_stats['missing_index_dirs'][:10]:
                report_lines.append(f"- {dir_path}")
        
        report_lines.extend([
            "",
            "---",
            "",
            "## 💡 改进建议",
            "",
            "### 高优先级",
            ""
        ])
        
        # 根据检查结果生成建议
        if self.results['summary']['yaml_completeness'] < 90:
            report_lines.append("- 补充缺失的YAML元数据字段")
        
        if self.results['summary']['index_coverage'] < 95:
            report_lines.append("- 为缺少索引的目录创建INDEX.md文件")
        
        if self.results['summary']['freshness_rate'] < 50:
            report_lines.append("- 审查和更新过期文档")
        
        report_lines.extend([
            "",
            "### 中优先级",
            "",
            "- 优化文档结构，增加目录章节",
            "- 定期运行质量检查工具",
            "- 建立文档更新提醒机制",
            "",
            "---",
            f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        # 保存JSON结果
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        # 创建最新报告的软链接
        latest_file = output_dir / 'QUALITY_REPORT_LATEST.md'
        try:
            if latest_file.exists():
                latest_file.unlink()
            latest_file.write_text('\n'.join(report_lines))
        except Exception:
            pass
        
        print(f"\n✅ 报告已生成: {report_file}")
        print(f"✅ JSON已保存: {json_file}")
        
        return report_file
    
    def run(self):
        """运行完整检查"""
        print("=" * 60)
        print("文档质量定期检查工具")
        print("=" * 60)
        
        self.check_yaml_metadata()
        self.check_document_structure()
        self.check_document_freshness()
        self.check_index_completeness()
        self.calculate_quality_score()
        
        print("\n" + "=" * 60)
        print("检查完成!")
        print("=" * 60)
        
        self.generate_report()

if __name__ == '__main__':
    checker = DocumentQualityChecker()
    checker.run()
