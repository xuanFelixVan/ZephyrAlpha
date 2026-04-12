# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
文档分类优化工具
分析非标准分类文档并建议移动方案

功能:
    - 扫描非标准分类文档
    - 分析文档内容，推断合适的分类
    - 生成移动方案
    - 执行文档移动（可选）

使用方式:
    python scripts/document_classifier.py --scan
    python scripts/document_classifier.py --analyze
    python scripts/document_classifier.py --report
"""
import os
import re
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class ClassificationSuggestion:
    """分类建议"""
    file_path: str
    current_location: str
    suggested_category: str
    suggested_path: str
    confidence: float
    reason: str


class DocumentClassifier:
    """
    文档分类器
    
    标准分类:
        - 01_FRAMEWORK: 系统架构
        - 02_FACTOR_LIBRARY: 因子库
        - 03_TRADING_TACTICS: 交易策略
        - 04_EXECUTION: 交易执行
        - 05_IMPLEMENTATION: 系统实施
        - 06_ARCHIVE: 归档文档
        - 07_RESEARCH: 研究实验
        - 08_AI_GOVERNANCE: AI治理
        - 09_AUDIT: 审计质量
    """
    
    # 标准分类目录
    STANDARD_CATEGORIES = {
        '01_FRAMEWORK',
        '02_FACTOR_LIBRARY',
        '03_TRADING_TACTICS',
        '04_EXECUTION',
        '05_IMPLEMENTATION',
        '06_ARCHIVE',
        '07_RESEARCH',
        '08_AI_GOVERNANCE',
        '09_AUDIT',
    }
    
    # 关键词到分类的映射
    KEYWORD_CATEGORY_MAP = {
        '01_FRAMEWORK': ['架构', '框架', 'framework', 'architecture', '系统设计', '整体设计'],
        '02_FACTOR_LIBRARY': ['因子', 'factor', '因子库', 'factor library', '特征工程'],
        '03_TRADING_TACTICS': ['策略', 'tactics', 'strategy', '交易策略', '风控', 'risk'],
        '04_EXECUTION': ['执行', 'execution', '交易执行', '撮合', '订单', 'order', '模拟交易', 'simulation'],
        '05_IMPLEMENTATION': ['实施', 'implementation', '开发', 'development', '部署', 'deployment', '技术规范', 'specification'],
        '06_ARCHIVE': ['归档', 'archive', '历史', 'history', '备份', 'backup'],
        '07_RESEARCH': ['研究', 'research', '实验', 'experiment', '探索', 'exploration'],
        '08_AI_GOVERNANCE': ['AI治理', 'AI governance', 'AI监督', 'supervision', 'AI权限', 'permission'],
        '09_AUDIT': ['审计', 'audit', '质量', 'quality', '监控', 'monitoring', '检查', 'check'],
    }
    
    # 文件名关键词到分类的映射
    FILENAME_CATEGORY_MAP = {
        '01_FRAMEWORK': ['FRAMEWORK', 'ARCHITECTURE'],
        '02_FACTOR_LIBRARY': ['FACTOR', 'FEATURE'],
        '03_TRADING_TACTICS': ['TACTICS', 'STRATEGY', 'RISK'],
        '04_EXECUTION': ['EXECUTION', 'ORDER', 'SIMULATION', 'MONITORING'],
        '05_IMPLEMENTATION': ['IMPLEMENTATION', 'SPECIFICATION', 'TECHNICAL_SPEC', 'DEVELOPMENT'],
        '06_ARCHIVE': ['ARCHIVE', 'BACKUP', 'OLD'],
        '07_RESEARCH': ['RESEARCH', 'EXPERIMENT'],
        '08_AI_GOVERNANCE': ['AI', 'GOVERNANCE', 'SUPERVISION', 'PERMISSION'],
        '09_AUDIT': ['AUDIT', 'QUALITY', 'MONITORING'],
    }
    
    def __init__(self, project_root: str):
        """
        初始化文档分类器
        
        参数:
            project_root: 项目根目录路径
        """
        self.project_root = Path(project_root)
        self.non_standard_docs: List[Path] = []
        self.suggestions: List[ClassificationSuggestion] = []
    
    def scan_non_standard_docs(self) -> List[Path]:
        """
        扫描非标准分类文档
        
        返回:
            List[Path]: 非标准分类文档列表
        """
        logger.info("扫描非标准分类文档...")
        
        self.non_standard_docs = []
        
        # 扫描docs根目录下的文件
        docs_root = self.project_root / 'docs'
        
        for item in docs_root.iterdir():
            if item.is_file() and item.suffix == '.md':
                # 检查是否在标准分类目录下
                # docs根目录下的文件都是非标准分类
                self.non_standard_docs.append(item)
        
        logger.info(f"扫描完成，发现 {len(self.non_standard_docs)} 个非标准分类文档")
        return self.non_standard_docs
    
    def analyze_document(self, file_path: Path) -> ClassificationSuggestion:
        """
        分析文档，推断合适的分类
        
        参数:
            file_path: 文档路径
        
        返回:
            ClassificationSuggestion: 分类建议
        """
        # 读取文档内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"读取文档失败: {file_path}, {e}")
            return ClassificationSuggestion(
                file_path=str(file_path.relative_to(self.project_root)),
                current_location='docs/',
                suggested_category='06_ARCHIVE',
                suggested_path='docs/06_ARCHIVE/',
                confidence=0.3,
                reason='无法读取文档内容，默认归档'
            )
        
        # 提取文档元数据
        metadata = self._extract_metadata(content)
        
        # 分析文件名
        filename = file_path.name.upper()
        filename_scores = defaultdict(float)
        
        for category, keywords in self.FILENAME_CATEGORY_MAP.items():
            for keyword in keywords:
                if keyword in filename:
                    filename_scores[category] += 1.0
        
        # 分析文档内容
        content_lower = content.lower()
        content_scores = defaultdict(float)
        
        for category, keywords in self.KEYWORD_CATEGORY_MAP.items():
            for keyword in keywords:
                count = content_lower.count(keyword.lower())
                content_scores[category] += count * 0.1
        
        # 合并分数
        total_scores = defaultdict(float)
        for category in self.STANDARD_CATEGORIES:
            total_scores[category] = filename_scores[category] + content_scores[category]
        
        # 选择最高分的分类
        if total_scores:
            best_category = max(total_scores.keys(), key=lambda k: total_scores[k])
            confidence = min(total_scores[best_category] / 5.0, 1.0)  # 归一化到0-1
        else:
            best_category = '06_ARCHIVE'
            confidence = 0.3
        
        # 生成建议路径
        suggested_path = f"docs/{best_category}/{file_path.name}"
        
        # 生成理由
        reason = self._generate_reason(filename_scores, content_scores, best_category)
        
        return ClassificationSuggestion(
            file_path=str(file_path.relative_to(self.project_root)),
            current_location='docs/',
            suggested_category=best_category,
            suggested_path=suggested_path,
            confidence=confidence,
            reason=reason
        )
    
    def _extract_metadata(self, content: str) -> Dict[str, str]:
        """提取YAML元数据"""
        metadata = {}
        
        if content.startswith('---'):
            metadata_end = content.find('---', 3)
            if metadata_end != -1:
                metadata_text = content[3:metadata_end]
                
                for line in metadata_text.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip().strip('"\'')
        
        return metadata
    
    def _generate_reason(
        self,
        filename_scores: Dict[str, float],
        content_scores: Dict[str, float],
        best_category: str
    ) -> str:
        """生成分类理由"""
        reasons = []
        
        if filename_scores[best_category] > 0:
            reasons.append(f"文件名包含{best_category}相关关键词")
        
        if content_scores[best_category] > 0:
            reasons.append(f"文档内容包含{best_category}相关主题")
        
        if not reasons:
            reasons.append("基于综合分析推断")
        
        return '; '.join(reasons)
    
    def analyze_all_documents(self) -> List[ClassificationSuggestion]:
        """
        分析所有非标准分类文档
        
        返回:
            List[ClassificationSuggestion]: 分类建议列表
        """
        logger.info("开始分析所有非标准分类文档...")
        
        self.suggestions = []
        
        for doc_path in self.non_standard_docs:
            suggestion = self.analyze_document(doc_path)
            self.suggestions.append(suggestion)
        
        logger.info(f"分析完成，共生成 {len(self.suggestions)} 个分类建议")
        return self.suggestions
    
    def generate_classification_report(self) -> Dict:
        """
        生成分类报告
        
        返回:
            Dict: 分类报告
        """
        # 统计分类分布
        category_counts = defaultdict(int)
        for suggestion in self.suggestions:
            category_counts[suggestion.suggested_category] += 1
        
        # 按置信度分组
        high_confidence = [s for s in self.suggestions if s.confidence >= 0.7]
        medium_confidence = [s for s in self.suggestions if 0.4 <= s.confidence < 0.7]
        low_confidence = [s for s in self.suggestions if s.confidence < 0.4]
        
        report = {
            'summary': {
                'scan_time': datetime.now().isoformat(),
                'total_non_standard_docs': len(self.non_standard_docs),
                'category_distribution': dict(category_counts),
                'confidence_distribution': {
                    'high': len(high_confidence),
                    'medium': len(medium_confidence),
                    'low': len(low_confidence),
                },
            },
            'suggestions': [asdict(s) for s in self.suggestions],
        }
        
        return report
    
    def save_report(self, report: Dict, output_path: str) -> None:
        """
        保存分类报告
        
        参数:
            report: 分类报告
            output_path: 输出文件路径
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"分类报告已保存到: {output_file}")
    
    def move_documents(self, dry_run: bool = True) -> Dict:
        """
        移动文档到标准分类目录
        
        参数:
            dry_run: 是否为演练模式 (不实际移动文件)
        
        返回:
            Dict: 移动结果
        """
        logger.info(f"开始移动文档 (dry_run={dry_run})...")
        
        results = {
            'total_attempted': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'details': [],
        }
        
        for suggestion in self.suggestions:
            # 只移动高置信度的文档
            if suggestion.confidence < 0.5:
                results['skipped'] += 1
                results['details'].append({
                    'file': suggestion.file_path,
                    'status': 'skipped',
                    'reason': f"置信度过低: {suggestion.confidence:.2f}",
                })
                continue
            
            results['total_attempted'] += 1
            
            try:
                source_path = self.project_root / suggestion.file_path
                target_path = self.project_root / suggestion.suggested_path
                
                if not source_path.exists():
                    results['failed'] += 1
                    results['details'].append({
                        'file': suggestion.file_path,
                        'status': 'failed',
                        'reason': '源文件不存在',
                    })
                    continue
                
                # 创建目标目录
                if not dry_run:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 移动文件
                    shutil.move(str(source_path), str(target_path))
                    
                    logger.info(f"已移动: {suggestion.file_path} -> {suggestion.suggested_path}")
                
                results['successful'] += 1
                results['details'].append({
                    'file': suggestion.file_path,
                    'target': suggestion.suggested_path,
                    'status': 'success',
                })
            
            except Exception as e:
                logger.error(f"移动文档失败: {suggestion.file_path}, {e}")
                results['failed'] += 1
                results['details'].append({
                    'file': suggestion.file_path,
                    'status': 'failed',
                    'reason': str(e),
                })
        
        logger.info(f"移动完成: 成功 {results['successful']}, 失败 {results['failed']}, 跳过 {results['skipped']}")
        return results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='文档分类优化工具')
    parser.add_argument(
        '--project-root',
        default='d:/ZephyrAlpha',
        help='项目根目录路径'
    )
    parser.add_argument(
        '--scan',
        action='store_true',
        help='扫描非标准分类文档'
    )
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='分析文档分类'
    )
    parser.add_argument(
        '--move',
        action='store_true',
        help='移动文档到标准分类目录'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='演练模式，不实际移动文件'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='生成分类报告'
    )
    parser.add_argument(
        '--output',
        default='docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/document_classification_report.json',
        help='输出报告路径'
    )
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建文档分类器
    classifier = DocumentClassifier(project_root=args.project_root)
    
    # 扫描非标准分类文档
    if args.scan or args.analyze or args.move or args.report:
        classifier.scan_non_standard_docs()
    
    # 分析文档分类
    if args.analyze or args.move or args.report:
        classifier.analyze_all_documents()
    
    # 生成报告
    if args.report:
        report = classifier.generate_classification_report()
        classifier.save_report(report, args.output)
        
        # 打印摘要
        print("\n" + "=" * 60)
        print("文档分类报告")
        print("=" * 60)
        print(f"非标准分类文档数: {report['summary']['total_non_standard_docs']}")
        print("\n分类分布:")
        for category, count in report['summary']['category_distribution'].items():
            print(f"  {category}: {count}")
        print("\n置信度分布:")
        for level, count in report['summary']['confidence_distribution'].items():
            print(f"  {level}: {count}")
        print("=" * 60)
    
    # 移动文档
    if args.move:
        results = classifier.move_documents(dry_run=args.dry_run)
        
        print("\n" + "=" * 60)
        print("文档移动结果")
        print("=" * 60)
        print(f"尝试移动: {results['total_attempted']}")
        print(f"移动成功: {results['successful']}")
        print(f"移动失败: {results['failed']}")
        print(f"跳过: {results['skipped']}")
        print("=" * 60)


if __name__ == '__main__':
    main()
