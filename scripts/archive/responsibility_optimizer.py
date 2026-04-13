#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
职责优化建议工具

功能:
- 分析现有职责描述的质量
- 识别改进点
- 提供优化建议
- 生成优化后的职责描述
- 生成详细的优化报告
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class QualityDimension(Enum):
    SPECIFICITY = "具体性"
    UNIQUENESS = "独特性"
    PROFESSIONALISM = "专业性"
    READABILITY = "可读性"


class IssueType(Enum):
    TOO_SHORT = "过于简短"
    TOO_LONG = "过于冗长"
    TOO_GENERIC = "过于通用"
    MISSING_KEYWORDS = "缺少关键词"
    MISSING_FEATURES = "缺少功能点"
    POOR_STRUCTURE = "结构不佳"
    REDUNDANT_PHRASES = "冗余表达"
    MISSING_TECHNICAL_DETAILS = "缺少技术细节"


@dataclass
class QualityScore:
    dimension: QualityDimension
    score: float
    issues: List[str]
    suggestions: List[str]


@dataclass
class OptimizationResult:
    filepath: str
    filename: str
    original_responsibility: str
    optimized_responsibility: str
    quality_scores: List[QualityScore]
    overall_score: float
    issues: List[IssueType]
    suggestions: List[str]
    improvements: List[str]


class ResponsibilityOptimizer:
    def __init__(self):
        self.blueprints_dir = 'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS'
        self.blueprint_files = []
        self.results = []
        
        self.min_length = 50
        self.max_length = 200
        self.optimal_length_range = (80, 150)
        
        self.required_keywords = self._load_required_keywords()
        self.professional_terms = self._load_professional_terms()
        self.generic_patterns = self._load_generic_patterns()
        self.redundant_patterns = self._load_redundant_patterns()
        
    def _load_required_keywords(self) -> List[str]:
        """加载必需关键词"""
        return [
            "负责", "支持", "提供", "实现", "包括", "功能",
            "优化", "监控", "管理", "处理", "计算", "分析"
        ]
    
    def _load_professional_terms(self) -> Dict[str, List[str]]:
        """加载专业术语"""
        return {
            "portfolio_optimization": [
                "均值方差", "风险平价", "Black-Litterman", "有效前沿",
                "夏普比率", "约束条件", "投资组合权重"
            ],
            "risk_management": [
                "VaR", "ES", "CVaR", "风险价值", "预期损失",
                "风险归因", "风险因子", "风险暴露"
            ],
            "trading_execution": [
                "TWAP", "VWAP", "POV", "市场冲击", "执行成本",
                "订单路由", "智能执行"
            ],
            "data_governance": [
                "数据血缘", "元数据", "数据质量", "数据目录",
                "数据生命周期", "数据资产"
            ],
            "ai_ml": [
                "LSTM", "Transformer", "深度学习", "强化学习",
                "因子挖掘", "特征工程", "模式识别"
            ],
        }
    
    def _load_generic_patterns(self) -> List[str]:
        """加载通用模式"""
        return [
            r'XX模块，负责XX相关功能',
            r'负责.+相关功能',
            r'负责.+等功能',
            r'.+模块，负责.+',
            r'负责数据处理',
            r'负责系统管理',
            r'负责功能实现',
        ]
    
    def _load_redundant_patterns(self) -> List[str]:
        """加载冗余模式"""
        return [
            r'本模块',
            r'该模块',
            r'此模块',
            r'主要功能包括',
            r'核心功能包括',
            r'等.*?功能',
        ]
    
    def scan_blueprint_files(self):
        """扫描蓝图文件"""
        blueprints_path = Path(self.blueprints_dir)
        if not blueprints_path.exists():
            print(f'❌ 蓝图目录不存在: {self.blueprints_dir}')
            return
        
        self.blueprint_files = list(blueprints_path.glob('**/*.md'))
        print(f'  ✅ 找到{len(self.blueprint_files)}个蓝图文件')
    
    def analyze_responsibility(self, filepath: str) -> OptimizationResult:
        """分析职责描述"""
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        filename = os.path.basename(filepath)
        responsibility = self._extract_responsibility(content)
        
        if not responsibility:
            return OptimizationResult(
                filepath=str(filepath),
                filename=filename,
                original_responsibility="",
                optimized_responsibility="",
                quality_scores=[],
                overall_score=0.0,
                issues=[IssueType.MISSING_KEYWORDS],
                suggestions=["未找到职责描述，请添加'核心定位'章节"],
                improvements=[]
            )
        
        quality_scores = self._evaluate_quality(responsibility)
        issues = self._identify_issues(responsibility)
        suggestions = self._generate_suggestions(responsibility, issues)
        optimized_responsibility = self._optimize_responsibility(responsibility, issues)
        improvements = self._identify_improvements(responsibility, optimized_responsibility)
        
        overall_score = sum(score.score for score in quality_scores) / len(quality_scores)
        
        return OptimizationResult(
            filepath=str(filepath),
            filename=filename,
            original_responsibility=responsibility,
            optimized_responsibility=optimized_responsibility,
            quality_scores=quality_scores,
            overall_score=overall_score,
            issues=issues,
            suggestions=suggestions,
            improvements=improvements
        )
    
    def _extract_responsibility(self, content: str) -> Optional[str]:
        """提取职责描述"""
        patterns = [
            r'##\s+核心定位\s*\n\n(.+?)(?=\n##|\Z)',
            r'核心定位[：:]\s*(.+?)(?:\n\n|\n#)',
            r'职责描述[：:]\s*(.+?)(?:\n\n|\n#)',
            r'核心职责[：:]\s*(.+?)(?:\n\n|\n#)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                responsibility = match.group(1).strip()
                responsibility = re.sub(r'\s+', ' ', responsibility)
                return responsibility
        
        return None
    
    def _evaluate_quality(self, responsibility: str) -> List[QualityScore]:
        """评估质量"""
        scores = []
        
        scores.append(self._evaluate_specificity(responsibility))
        scores.append(self._evaluate_uniqueness(responsibility))
        scores.append(self._evaluate_professionalism(responsibility))
        scores.append(self._evaluate_readability(responsibility))
        
        return scores
    
    def _evaluate_specificity(self, responsibility: str) -> QualityScore:
        """评估具体性"""
        issues = []
        suggestions = []
        score = 100.0
        
        if len(responsibility) < self.min_length:
            issues.append(f"职责描述过短（{len(responsibility)}字），建议至少{self.min_length}字")
            suggestions.append("添加更多具体功能点和技术细节")
            score -= 30
        
        if len(responsibility) > self.max_length:
            issues.append(f"职责描述过长（{len(responsibility)}字），建议不超过{self.max_length}字")
            suggestions.append("精简内容，保留核心信息")
            score -= 20
        
        for pattern in self.generic_patterns:
            if re.search(pattern, responsibility):
                issues.append("使用了通用模板，缺乏具体性")
                suggestions.append("替换为具体的职责描述，避免使用通用模板")
                score -= 40
                break
        
        feature_count = len(re.findall(r'[、，].*?(?:功能|支持|提供|实现)', responsibility))
        if feature_count < 2:
            issues.append("缺少具体功能点")
            suggestions.append("添加3-5个具体功能点")
            score -= 20
        
        return QualityScore(
            dimension=QualityDimension.SPECIFICITY,
            score=max(0, score),
            issues=issues,
            suggestions=suggestions
        )
    
    def _evaluate_uniqueness(self, responsibility: str) -> QualityScore:
        """评估独特性"""
        issues = []
        suggestions = []
        score = 100.0
        
        unique_indicators = [
            "均值方差", "风险平价", "Black-Litterman",
            "VaR", "ES", "TWAP", "VWAP",
            "LSTM", "Transformer", "强化学习"
        ]
        
        unique_count = sum(1 for indicator in unique_indicators if indicator in responsibility)
        
        if unique_count == 0:
            issues.append("缺少独特性标识")
            suggestions.append("添加体现模块独特价值的关键词")
            score -= 30
        
        if "相关功能" in responsibility:
            issues.append("使用了模糊表达'相关功能'")
            suggestions.append("替换为具体的功能描述")
            score -= 20
        
        return QualityScore(
            dimension=QualityDimension.UNIQUENESS,
            score=max(0, score),
            issues=issues,
            suggestions=suggestions
        )
    
    def _evaluate_professionalism(self, responsibility: str) -> QualityScore:
        """评估专业性"""
        issues = []
        suggestions = []
        score = 100.0
        
        professional_term_count = 0
        for domain_terms in self.professional_terms.values():
            professional_term_count += sum(1 for term in domain_terms if term in responsibility)
        
        if professional_term_count == 0:
            issues.append("缺少专业术语")
            suggestions.append("添加专业术语以体现技术深度")
            score -= 30
        elif professional_term_count < 2:
            issues.append("专业术语较少")
            suggestions.append("增加更多专业术语")
            score -= 10
        
        required_keyword_count = sum(1 for keyword in self.required_keywords if keyword in responsibility)
        if required_keyword_count < 3:
            issues.append("缺少关键动词")
            suggestions.append("添加'负责'、'支持'、'实现'等关键动词")
            score -= 20
        
        return QualityScore(
            dimension=QualityDimension.PROFESSIONALISM,
            score=max(0, score),
            issues=issues,
            suggestions=suggestions
        )
    
    def _evaluate_readability(self, responsibility: str) -> QualityScore:
        """评估可读性"""
        issues = []
        suggestions = []
        score = 100.0
        
        sentences = re.split(r'[。！？]', responsibility)
        if len(sentences) > 3:
            issues.append("句子过多，建议合并")
            suggestions.append("将职责描述合并为1-2个完整句子")
            score -= 15
        
        for pattern in self.redundant_patterns:
            if re.search(pattern, responsibility):
                issues.append("存在冗余表达")
                suggestions.append("删除冗余词汇，使表达更简洁")
                score -= 10
        
        if not responsibility.startswith(tuple(self.required_keywords[:3])):
            issues.append("开头不够明确")
            suggestions.append("以模块名称或'负责'开头")
            score -= 10
        
        return QualityScore(
            dimension=QualityDimension.READABILITY,
            score=max(0, score),
            issues=issues,
            suggestions=suggestions
        )
    
    def _identify_issues(self, responsibility: str) -> List[IssueType]:
        """识别问题"""
        issues = []
        
        if len(responsibility) < self.min_length:
            issues.append(IssueType.TOO_SHORT)
        elif len(responsibility) > self.max_length:
            issues.append(IssueType.TOO_LONG)
        
        for pattern in self.generic_patterns:
            if re.search(pattern, responsibility):
                issues.append(IssueType.TOO_GENERIC)
                break
        
        required_keyword_count = sum(1 for keyword in self.required_keywords if keyword in responsibility)
        if required_keyword_count < 3:
            issues.append(IssueType.MISSING_KEYWORDS)
        
        feature_count = len(re.findall(r'[、，].*?(?:功能|支持|提供|实现)', responsibility))
        if feature_count < 2:
            issues.append(IssueType.MISSING_FEATURES)
        
        for pattern in self.redundant_patterns:
            if re.search(pattern, responsibility):
                issues.append(IssueType.REDUNDANT_PHRASES)
                break
        
        professional_term_count = 0
        for domain_terms in self.professional_terms.values():
            professional_term_count += sum(1 for term in domain_terms if term in responsibility)
        
        if professional_term_count == 0:
            issues.append(IssueType.MISSING_TECHNICAL_DETAILS)
        
        return issues
    
    def _generate_suggestions(self, responsibility: str, issues: List[IssueType]) -> List[str]:
        """生成建议"""
        suggestions = []
        
        if IssueType.TOO_SHORT in issues:
            suggestions.append(f"扩展职责描述长度至{self.optimal_length_range[0]}-{self.optimal_length_range[1]}字")
        
        if IssueType.TOO_LONG in issues:
            suggestions.append(f"精简职责描述长度至{self.optimal_length_range[0]}-{self.optimal_length_range[1]}字")
        
        if IssueType.TOO_GENERIC in issues:
            suggestions.append("替换通用模板为具体的职责描述")
        
        if IssueType.MISSING_KEYWORDS in issues:
            suggestions.append("添加关键动词：负责、支持、提供、实现、包括等")
        
        if IssueType.MISSING_FEATURES in issues:
            suggestions.append("添加3-5个具体功能点")
        
        if IssueType.REDUNDANT_PHRASES in issues:
            suggestions.append("删除冗余表达，如'本模块'、'该模块'等")
        
        if IssueType.MISSING_TECHNICAL_DETAILS in issues:
            suggestions.append("添加专业技术术语和实现细节")
        
        return suggestions
    
    def _optimize_responsibility(self, responsibility: str, issues: List[IssueType]) -> str:
        """优化职责描述"""
        optimized = responsibility
        
        for pattern in self.redundant_patterns:
            optimized = re.sub(pattern, '', optimized)
        
        optimized = re.sub(r'\s+', ' ', optimized)
        optimized = optimized.strip()
        
        if IssueType.TOO_GENERIC in issues:
            optimized = re.sub(r'XX模块，负责XX相关功能', '模块，负责核心功能', optimized)
            optimized = re.sub(r'负责(.+?)相关功能', r'负责\1相关功能，包括具体功能点', optimized)
        
        if IssueType.MISSING_KEYWORDS in issues:
            if '负责' not in optimized:
                optimized = f"负责{optimized}"
        
        if IssueType.MISSING_FEATURES in issues:
            if '包括' not in optimized and '支持' not in optimized:
                optimized = f"{optimized}，支持核心功能"
        
        return optimized
    
    def _identify_improvements(self, original: str, optimized: str) -> List[str]:
        """识别改进点"""
        improvements = []
        
        if len(optimized) > len(original):
            improvements.append(f"长度增加: {len(original)}字 → {len(optimized)}字")
        elif len(optimized) < len(original):
            improvements.append(f"长度减少: {len(original)}字 → {len(optimized)}字")
        
        for pattern in self.redundant_patterns:
            if re.search(pattern, original) and not re.search(pattern, optimized):
                improvements.append("删除了冗余表达")
                break
        
        original_keywords = sum(1 for keyword in self.required_keywords if keyword in original)
        optimized_keywords = sum(1 for keyword in self.required_keywords if keyword in optimized)
        if optimized_keywords > original_keywords:
            improvements.append("增加了关键动词")
        
        return improvements
    
    def generate_report(self, output_file: Optional[str] = None):
        """生成报告"""
        report_lines = []
        
        report_lines.append('# 职责优化建议报告')
        report_lines.append('')
        report_lines.append(f'> **生成日期**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        report_lines.append(f'> **检测范围**: {self.blueprints_dir}')
        report_lines.append(f'> **检测标准**: 专业量化机构文档治理五大原则')
        report_lines.append('')
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 📊 一、优化概要')
        report_lines.append('')
        report_lines.append(f'**分析文件数**: {len(self.results)}个')
        
        avg_score = sum(r.overall_score for r in self.results) / len(self.results) if self.results else 0
        report_lines.append(f'**平均质量得分**: {avg_score:.1f}分')
        
        excellent_count = sum(1 for r in self.results if r.overall_score >= 90)
        good_count = sum(1 for r in self.results if 70 <= r.overall_score < 90)
        need_improvement_count = sum(1 for r in self.results if r.overall_score < 70)
        
        report_lines.append(f'**优秀（≥90分）**: {excellent_count}个')
        report_lines.append(f'**良好（70-89分）**: {good_count}个')
        report_lines.append(f'**需改进（<70分）**: {need_improvement_count}个')
        report_lines.append('')
        
        report_lines.append('### 1.1 质量分布')
        report_lines.append('')
        report_lines.append('| 质量等级 | 数量 | 占比 |')
        report_lines.append('|----------|------|------|')
        total = len(self.results) if self.results else 1
        report_lines.append(f'| 优秀（≥90分） | {excellent_count} | {excellent_count/total*100:.1f}% |')
        report_lines.append(f'| 良好（70-89分） | {good_count} | {good_count/total*100:.1f}% |')
        report_lines.append(f'| 需改进（<70分） | {need_improvement_count} | {need_improvement_count/total*100:.1f}% |')
        report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        if self.results:
            sorted_results = sorted(self.results, key=lambda x: x.overall_score)
            
            report_lines.append('## 🔍 二、需优化文档列表')
            report_lines.append('')
            
            need_optimization = [r for r in sorted_results if r.overall_score < 90]
            
            for i, result in enumerate(need_optimization[:20], 1):
                report_lines.append(f'### 文档 {i}: {result.filename}')
                report_lines.append('')
                report_lines.append(f'**质量得分**: {result.overall_score:.1f}分')
                report_lines.append('')
                
                report_lines.append('**质量维度评分**:')
                for score in result.quality_scores:
                    report_lines.append(f'- {score.dimension.value}: {score.score:.1f}分')
                report_lines.append('')
                
                if result.issues:
                    report_lines.append('**识别的问题**:')
                    for issue in result.issues:
                        report_lines.append(f'- {issue.value}')
                    report_lines.append('')
                
                if result.suggestions:
                    report_lines.append('**优化建议**:')
                    for suggestion in result.suggestions:
                        report_lines.append(f'- {suggestion}')
                    report_lines.append('')
                
                report_lines.append('**原始职责描述**:')
                report_lines.append(f'```')
                report_lines.append(result.original_responsibility)
                report_lines.append('```')
                report_lines.append('')
                
                if result.optimized_responsibility != result.original_responsibility:
                    report_lines.append('**优化后职责描述**:')
                    report_lines.append(f'```')
                    report_lines.append(result.optimized_responsibility)
                    report_lines.append('```')
                    report_lines.append('')
                
                if result.improvements:
                    report_lines.append('**改进点**:')
                    for improvement in result.improvements:
                        report_lines.append(f'- {improvement}')
                    report_lines.append('')
                
                report_lines.append('---')
                report_lines.append('')
        
        report_lines.append('## 📈 三、质量评估')
        report_lines.append('')
        
        if avg_score >= 90:
            report_lines.append('✅ **整体质量优秀，继续保持**')
        elif avg_score >= 70:
            report_lines.append('⚠️ **整体质量良好，仍有改进空间**')
        else:
            report_lines.append('❌ **整体质量需改进，建议优化**')
        
        report_lines.append('')
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 🎯 四、改进建议')
        report_lines.append('')
        
        if need_improvement_count > 0:
            report_lines.append('### 4.1 立即处理')
            report_lines.append('')
            critical_results = [r for r in self.results if r.overall_score < 50]
            if critical_results:
                for result in critical_results[:5]:
                    report_lines.append(f'- 优化: {result.filename}')
            else:
                report_lines.append('- 无严重问题需要立即处理')
            report_lines.append('')
        
        report_lines.append('### 4.2 近期改进')
        report_lines.append('')
        report_lines.append('- 运行职责描述自动生成工具')
        report_lines.append('- 运行职责冲突自动检测工具')
        report_lines.append('- 参考职责描述最佳实践')
        report_lines.append('')
        
        report_lines.append('### 4.3 长期优化')
        report_lines.append('')
        report_lines.append('- 建立职责审查机制')
        report_lines.append('- 定期运行优化建议工具')
        report_lines.append('- 持续改进职责描述质量')
        report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        report_lines.append(f'**报告生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        report_lines.append(f'**工具版本**: v1.0.0')
        
        report_content = '\n'.join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f'  ✅ 报告已生成: {output_file}')
        else:
            print(report_content)
    
    def run(self, filepath: Optional[str] = None, output_file: Optional[str] = None):
        """运行优化器"""
        print('=' * 80)
        print('职责优化建议工具')
        print('=' * 80)
        print()
        
        if filepath:
            result = self.analyze_responsibility(filepath)
            self.results = [result]
            
            print(f'文档: {result.filename}')
            print(f'质量得分: {result.overall_score:.1f}分')
            print()
            
            print('质量维度评分:')
            for score in result.quality_scores:
                print(f'  {score.dimension.value}: {score.score:.1f}分')
            print()
            
            if result.issues:
                print('识别的问题:')
                for issue in result.issues:
                    print(f'  - {issue.value}')
                print()
            
            if result.suggestions:
                print('优化建议:')
                for suggestion in result.suggestions:
                    print(f'  - {suggestion}')
                print()
            
            print('原始职责描述:')
            print(f'  {result.original_responsibility}')
            print()
            
            if result.optimized_responsibility != result.original_responsibility:
                print('优化后职责描述:')
                print(f'  {result.optimized_responsibility}')
                print()
        else:
            print('1. 扫描蓝图文件...')
            self.scan_blueprint_files()
            print()
            
            print('2. 分析职责描述...')
            for i, blueprint_file in enumerate(self.blueprint_files[:20], 1):
                print(f'  处理 [{i}/{min(20, len(self.blueprint_files))}]: {blueprint_file.name}')
                result = self.analyze_responsibility(str(blueprint_file))
                self.results.append(result)
            print()
            
            print('3. 生成优化报告...')
            self.generate_report(output_file)
            print()
        
        print('=' * 80)
        print('优化完成')
        print('=' * 80)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='职责优化建议工具')
    parser.add_argument('--file', help='单个文件路径')
    parser.add_argument('--output', help='输出报告文件路径')
    
    args = parser.parse_args()
    
    optimizer = ResponsibilityOptimizer()
    optimizer.run(filepath=args.file, output_file=args.output)


if __name__ == '__main__':
    main()
