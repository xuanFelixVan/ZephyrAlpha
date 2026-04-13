#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
清风量化系统 - 文档债务评估工具

功能: 评估文档债务，检查文档完整性、时效性、一致性、可读性
版本: v1.0
创建日期: 2026-04-01
维护者: 蓝图架构师智能体

使用方法:
    python scripts/documentation_debt_assessor.py [--verbose] [--report] [--category CATEGORY]

参数:
    --verbose    : 显示详细评估过程
    --report     : 生成HTML评估报告
    --category CATEGORY : 只检查指定类别 (completeness, timeliness, consistency, readability)
    --all        : 检查所有类别
    --help       : 显示帮助信息
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import yaml

@dataclass
class DocumentMetric:
    """文档指标"""
    document_path: Path
    category: str  # 完整性、时效性、一致性、可读性
    metric_name: str
    value: float  # 0-100分数
    weight: float  # 权重
    issues: List[str] = field(default_factory=list)
    
@dataclass
class DocumentationDebt:
    """文档债务"""
    document_path: Path
    total_score: float  # 总体评分 (0-100)
    completeness_score: float  # 完整性评分
    timeliness_score: float  # 时效性评分
    consistency_score: float  # 一致性评分
    readability_score: float  # 可读性评分
    metrics: List[DocumentMetric] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

class DocumentationDebtAssessor:
    """文档债务评估器"""
    
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.debts: Dict[Path, DocumentationDebt] = {}
        self.issues: List[Dict[str, Any]] = []
        
    def assess_documentation_debt(self) -> bool:
        """评估文档债务"""
        if self.verbose:
            print("🔍 开始文档债务评估...")
        
        # 获取所有文档文件
        docs_path = self.project_root / "docs"
        if not docs_path.exists():
            self._add_issue("P0", "docs目录缺失", "项目缺少docs目录")
            return False
        
        # 收集所有文档文件
        document_files = self._collect_document_files(docs_path)
        
        if self.verbose:
            print(f"   找到 {len(document_files)} 个文档文件")
        
        # 评估每个文档
        for doc_path in document_files:
            debt = self._assess_single_document(doc_path)
            if debt:
                self.debts[doc_path] = debt
        
        # 生成总体报告
        overall_score = self._calculate_overall_score()
        
        if self.verbose:
            print(f"✅ 文档债务评估完成")
            print(f"   评估了 {len(self.debts)} 个文档")
            print(f"   总体评分: {overall_score:.1f}/100")
        
        return True
    
    def _collect_document_files(self, docs_path: Path) -> List[Path]:
        """收集所有文档文件"""
        document_files = []
        
        # 包含的扩展名
        included_extensions = {'.md', '.txt', '.rst', '.yaml', '.yml', '.json'}
        
        for root, dirs, files in os.walk(docs_path):
            # 跳过某些目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in included_extensions:
                    document_files.append(file_path)
        
        return document_files
    
    def _assess_single_document(self, doc_path: Path) -> Optional[DocumentationDebt]:
        """评估单个文档"""
        try:
            if not doc_path.exists():
                return None
            
            metrics = []
            
            # 评估完整性
            completeness_metrics = self._assess_completeness(doc_path)
            metrics.extend(completeness_metrics)
            
            # 评估时效性
            timeliness_metrics = self._assess_timeliness(doc_path)
            metrics.extend(timeliness_metrics)
            
            # 评估一致性
            consistency_metrics = self._assess_consistency(doc_path)
            metrics.extend(consistency_metrics)
            
            # 评估可读性
            readability_metrics = self._assess_readability(doc_path)
            metrics.extend(readability_metrics)
            
            # 计算各项评分
            completeness_score = self._calculate_category_score(metrics, "completeness")
            timeliness_score = self._calculate_category_score(metrics, "timeliness")
            consistency_score = self._calculate_category_score(metrics, "consistency")
            readability_score = self._calculate_category_score(metrics, "readability")
            
            # 计算总体评分
            total_score = (
                completeness_score * 0.3 +
                timeliness_score * 0.25 +
                consistency_score * 0.25 +
                readability_score * 0.2
            )
            
            # 生成改进建议
            recommendations = self._generate_recommendations(metrics)
            
            return DocumentationDebt(
                document_path=doc_path,
                total_score=total_score,
                completeness_score=completeness_score,
                timeliness_score=timeliness_score,
                consistency_score=consistency_score,
                readability_score=readability_score,
                metrics=metrics,
                recommendations=recommendations
            )
            
        except Exception as e:
            if self.verbose:
                print(f"  警告: 评估文档 {doc_path} 时出错: {e}")
            return None
    
    def _assess_completeness(self, doc_path: Path) -> List[DocumentMetric]:
        """评估文档完整性"""
        metrics = []
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查文档长度
            line_count = len(content.splitlines())
            word_count = len(content.split())
            
            line_metric = DocumentMetric(
                document_path=doc_path,
                category="completeness",
                metric_name="文档长度",
                value=min(line_count / 50 * 100, 100),  # 50行为基准
                weight=0.3,
                issues=["文档过短"] if line_count < 20 else []
            )
            metrics.append(line_metric)
            
            # 检查章节结构
            section_count = len(re.findall(r'^#+\s+', content, re.MULTILINE))
            section_metric = DocumentMetric(
                document_path=doc_path,
                category="completeness",
                metric_name="章节结构",
                value=min(section_count / 5 * 100, 100),  # 5个章节为基准
                weight=0.3,
                issues=["缺少章节结构"] if section_count < 2 else []
            )
            metrics.append(section_metric)
            
            # 检查代码示例
            code_block_count = len(re.findall(r'```', content))
            code_metric = DocumentMetric(
                document_path=doc_path,
                category="completeness",
                metric_name="代码示例",
                value=min(code_block_count / 2 * 100, 100),  # 2个代码块为基准
                weight=0.2,
                issues=["缺少代码示例"] if code_block_count == 0 else []
            )
            metrics.append(code_metric)
            
            # 检查链接
            link_count = len(re.findall(r'\[.*?\]\(.*?\)', content))
            link_metric = DocumentMetric(
                document_path=doc_path,
                category="completeness",
                metric_name="内部链接",
                value=min(link_count / 3 * 100, 100),  # 3个链接为基准
                weight=0.2,
                issues=["缺少内部链接"] if link_count == 0 else []
            )
            metrics.append(link_metric)
            
        except Exception as e:
            if self.verbose:
                print(f"  警告: 评估完整性时出错: {e}")
        
        return metrics
    
    def _assess_timeliness(self, doc_path: Path) -> List[DocumentMetric]:
        """评估文档时效性"""
        metrics = []
        
        try:
            # 获取文件修改时间
            stat = doc_path.stat()
            last_modified = datetime.fromtimestamp(stat.st_mtime)
            days_since_modified = (datetime.now() - last_modified).days
            
            # 时效性评分
            timeliness_value = max(0, 100 - days_since_modified * 2)  # 每天减2分
            timeliness_metric = DocumentMetric(
                document_path=doc_path,
                category="timeliness",
                metric_name="修改时间",
                value=timeliness_value,
                weight=0.6,
                issues=["文档已过期"] if days_since_modified > 90 else []
            )
            metrics.append(timeliness_metric)
            
            # 检查文档中的日期信息
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找版本号
            version_matches = re.findall(r'version\s*[:=]\s*["\']?([0-9.]+)["\']?', content, re.IGNORECASE)
            version_metric = DocumentMetric(
                document_path=doc_path,
                category="timeliness",
                metric_name="版本标识",
                value=100 if version_matches else 30,
                weight=0.4,
                issues=["缺少版本标识"] if not version_matches else []
            )
            metrics.append(version_metric)
            
        except Exception as e:
            if self.verbose:
                print(f"  警告: 评估时效性时出错: {e}")
        
        return metrics
    
    def _assess_consistency(self, doc_path: Path) -> List[DocumentMetric]:
        """评估文档一致性"""
        metrics = []
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查标题格式一致性
            headings = re.findall(r'^(#+)\s+(.*)$', content, re.MULTILINE)
            if headings:
                heading_levels = [len(h[0]) for h in headings]
                consistent_headings = all(level == heading_levels[0] for level in heading_levels[:3])
                
                consistency_metric = DocumentMetric(
                    document_path=doc_path,
                    category="consistency",
                    metric_name="标题格式",
                    value=100 if consistent_headings else 50,
                    weight=0.4,
                    issues=["标题格式不一致"] if not consistent_headings else []
                )
                metrics.append(consistency_metric)
            
            # 检查命名规范
            chinese_filename = self._contains_chinese(str(doc_path.name))
            naming_metric = DocumentMetric(
                document_path=doc_path,
                category="consistency",
                metric_name="命名规范",
                value=0 if chinese_filename else 100,
                weight=0.3,
                issues=["中文文件名"] if chinese_filename else []
            )
            metrics.append(naming_metric)
            
            # 检查引用完整性
            link_matches = re.findall(r'\[.*?\]\((.*?)\)', content)
            broken_links = []
            for link in link_matches:
                if link.startswith('http'):
                    continue  # 跳过外部链接
                # 检查内部链接
                link_path = doc_path.parent / link
                if not link_path.exists():
                    broken_links.append(link)
            
            link_metric = DocumentMetric(
                document_path=doc_path,
                category="consistency",
                metric_name="链接完整性",
                value=100 if not broken_links else max(0, 100 - len(broken_links) * 20),
                weight=0.3,
                issues=[f"失效链接: {broken_links[:3]}"] if broken_links else []
            )
            metrics.append(link_metric)
            
        except Exception as e:
            if self.verbose:
                print(f"  警告: 评估一致性时出错: {e}")
        
        return metrics
    
    def _assess_readability(self, doc_path: Path) -> List[DocumentMetric]:
        """评估文档可读性"""
        metrics = []
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 计算平均句长
            sentences = re.split(r'[。！？.!?]', content)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if sentences:
                avg_sentence_length = sum(len(s) for s in sentences) / len(sentences)
                readability_metric = DocumentMetric(
                    document_path=doc_path,
                    category="readability",
                    metric_name="句长可读性",
                    value=max(0, 100 - (avg_sentence_length - 20) * 2),  # 20字为基准
                    weight=0.4,
                    issues=["句子过长"] if avg_sentence_length > 40 else []
                )
                metrics.append(readability_metric)
            
            # 检查段落长度
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            if paragraphs:
                avg_paragraph_length = sum(len(p) for p in paragraphs) / len(paragraphs)
                paragraph_metric = DocumentMetric(
                    document_path=doc_path,
                    category="readability",
                    metric_name="段落长度",
                    value=max(0, 100 - (avg_paragraph_length - 200) * 0.2),  # 200字为基准
                    weight=0.3,
                    issues=["段落过长"] if avg_paragraph_length > 500 else []
                )
                metrics.append(paragraph_metric)
            
            # 检查代码注释比例（针对代码文件）
            if doc_path.suffix in ['.py', '.js', '.java', '.cpp']:
                code_lines = content.splitlines()
                comment_lines = [line for line in code_lines if line.strip().startswith('#') or '//' in line]
                comment_ratio = len(comment_lines) / len(code_lines) if code_lines else 0
                
                comment_metric = DocumentMetric(
                    document_path=doc_path,
                    category="readability",
                    metric_name="代码注释",
                    value=min(comment_ratio * 300, 100),  # 33%注释率为满分
                    weight=0.3,
                    issues=["缺少代码注释"] if comment_ratio < 0.1 else []
                )
                metrics.append(comment_metric)
            
        except Exception as e:
            if self.verbose:
                print(f"  警告: 评估可读性时出错: {e}")
        
        return metrics
    
    def _calculate_category_score(self, metrics: List[DocumentMetric], category: str) -> float:
        """计算类别评分"""
        category_metrics = [m for m in metrics if m.category == category]
        if not category_metrics:
            return 0.0
        
        total_weight = sum(m.weight for m in category_metrics)
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(m.value * m.weight for m in category_metrics)
        return weighted_sum / total_weight
    
    def _calculate_overall_score(self) -> float:
        """计算总体评分"""
        if not self.debts:
            return 0.0
        
        total_scores = [debt.total_score for debt in self.debts.values()]
        return sum(total_scores) / len(total_scores)
    
    def _generate_recommendations(self, metrics: List[DocumentMetric]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        for metric in metrics:
            if metric.value < 60 and metric.issues:
                for issue in metric.issues[:2]:  # 每个指标最多2个建议
                    recommendations.append(f"{metric.metric_name}: {issue}")
        
        return recommendations[:5]  # 最多5个建议
    
    def _contains_chinese(self, text: str) -> bool:
        """检查是否包含中文"""
        return bool(re.search(r'[\u4e00-\u9fff]', text))
    
    def _add_issue(self, priority: str, title: str, description: str):
        """添加问题"""
        self.issues.append({
            "priority": priority,
            "title": title,
            "description": description
        })
        
        if self.verbose:
            print(f"  {priority}: {title}")
    
    def generate_report(self, output_path: Optional[Path] = None) -> str:
        """生成文档债务评估报告"""
        report = []
        
        # 报告头
        report.append("# 文档债务评估报告")
        report.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"> 系统版本: v5.2")
        report.append(f"> 评估工具: documentation_debt_assessor.py v1.0")
        report.append("")
        
        # 概要统计
        total_documents = len(self.debts)
        overall_score = self._calculate_overall_score()
        
        # 按评分分类
        excellent_count = len([d for d in self.debts.values() if d.total_score >= 80])
        good_count = len([d for d in self.debts.values() if 60 <= d.total_score < 80])
        poor_count = len([d for d in self.debts.values() if d.total_score < 60])
        
        report.append("## 📊 概要统计")
        report.append("")
        report.append("| 指标 | 数量 |")
        report.append("|------|------|")
        report.append(f"| 评估文档数 | {total_documents} |")
        report.append(f"| 总体评分 | {overall_score:.1f}/100 |")
        report.append(f"| 优秀文档 (≥80分) | {excellent_count} |")
        report.append(f"| 良好文档 (60-79分) | {good_count} |")
        report.append(f"| 需改进文档 (<60分) | {poor_count} |")
        report.append("")
        
        # 按类别统计
        report.append("## 📈 按类别统计")
        report.append("")
        report.append("| 类别 | 平均分 | 说明 |")
        report.append("|------|--------|------|")
        
        categories = ["completeness", "timeliness", "consistency", "readability"]
        category_names = {"completeness": "完整性", "timeliness": "时效性", "consistency": "一致性", "readability": "可读性"}
        
        for category in categories:
            category_scores = []
            for debt in self.debts.values():
                if category == "completeness":
                    category_scores.append(debt.completeness_score)
                elif category == "timeliness":
                    category_scores.append(debt.timeliness_score)
                elif category == "consistency":
                    category_scores.append(debt.consistency_score)
                elif category == "readability":
                    category_scores.append(debt.readability_score)
            
            avg_score = sum(category_scores) / len(category_scores) if category_scores else 0
            report.append(f"| {category_names[category]} | {avg_score:.1f}/100 | {'需改进' if avg_score < 60 else '良好'} |")
        
        report.append("")
        
        # 详细文档列表
        report.append("## 📄 文档详情")
        report.append("")
        report.append("| 文档 | 总体评分 | 完整性 | 时效性 | 一致性 | 可读性 | 状态 |")
        report.append("|------|----------|--------|--------|--------|--------|------|")
        
        sorted_debts = sorted(self.debts.items(), key=lambda x: x[1].total_score)
        
        for doc_path, debt in sorted_debts[:20]:  # 显示前20个文档
            relative_path = doc_path.relative_to(self.project_root)
            
            status = "✅ 优秀" if debt.total_score >= 80 else "⚠️ 良好" if debt.total_score >= 60 else "❌ 需改进"
            
            report.append(f"| [{relative_path}]({relative_path}) | {debt.total_score:.1f} | {debt.completeness_score:.1f} | {debt.timeliness_score:.1f} | {debt.consistency_score:.1f} | {debt.readability_score:.1f} | {status} |")
        
        if len(sorted_debts) > 20:
            report.append(f"| ... 和其他 {len(sorted_debts) - 20} 个文档 | ... | ... | ... | ... | ... | ... |")
        
        report.append("")
        
        # 改进建议
        report.append("## 💡 改进建议")
        report.append("")
        
        all_recommendations = []
        for debt in self.debts.values():
            all_recommendations.extend(debt.recommendations)
        
        if all_recommendations:
            unique_recommendations = list(set(all_recommendations))[:10]  # 去重后取前10个
            for i, rec in enumerate(unique_recommendations, 1):
                report.append(f"{i}. {rec}")
        else:
            report.append("所有文档都处于良好状态，无需特别改进。")
        
        report.append("")
        
        report_content = "\n".join(report)
        
        # 保存报告
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            if self.verbose:
                print(f"📄 报告已保存到: {output_path}")
        
        return report_content
    
    def run_assessment(self, category: Optional[str] = None) -> bool:
        """运行评估"""
        if self.verbose:
            print(f"🔍 开始文档债务评估...")
            print(f"项目根目录: {self.project_root}")
            print("-" * 60)
        
        success = self.assess_documentation_debt()
        
        print("-" * 60)
        if success:
            overall_score = self._calculate_overall_score()
            if overall_score >= 80:
                print(f"✅ 文档债务评估完成，总体评分: {overall_score:.1f}/100 (优秀)")
            elif overall_score >= 60:
                print(f"⚠️ 文档债务评估完成，总体评分: {overall_score:.1f}/100 (良好)")
            else:
                print(f"❌ 文档债务评估完成，总体评分: {overall_score:.1f}/100 (需改进)")
        else:
            print("❌ 文档债务评估失败")
        
        return success

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="清风量化系统 - 文档债务评估工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
    # 完整评估
    python scripts/documentation_debt_assessor.py
    
    # 详细输出
    python scripts/documentation_debt_assessor.py --verbose
    
    # 生成HTML报告
    python scripts/documentation_debt_assessor.py --report
    
    # 只检查完整性
    python scripts/documentation_debt_assessor.py --category completeness
    
    # 所有检查
    python scripts/documentation_debt_assessor.py --all
        """
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细评估过程"
    )
    
    parser.add_argument(
        "--report",
        action="store_true",
        help="生成HTML评估报告"
    )
    
    parser.add_argument(
        "--category",
        type=str,
        choices=["completeness", "timeliness", "consistency", "readability", "all"],
        help="只检查指定类别"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="检查所有方面"
    )
    
    args = parser.parse_args()
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    
    # 创建评估器
    assessor = DocumentationDebtAssessor(
        project_root=project_root,
        verbose=args.verbose
    )
    
    # 运行评估
    try:
        success = assessor.run_assessment(category=args.category)
        
        # 生成报告
        if args.report:
            report_path = project_root / "docs" / "09_AUDIT" / "DOCUMENTATION_DEBT_REPORT.md"
            assessor.generate_report(report_path)
        
        # 显示问题概要
        if assessor.issues:
            print("\n📋 问题概要:")
            for issue in assessor.issues[:10]:  # 只显示前10个
                print(f"  {issue['priority']}: {issue['title']}")
            
            if len(assessor.issues) > 10:
                print(f"  ... 和其他 {len(assessor.issues) - 10} 个问题")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n用户中断评估操作")
        return 1
    except Exception as e:
        print(f"评估过程中发生错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())