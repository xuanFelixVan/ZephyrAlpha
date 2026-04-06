#!/usr/bin/env python3
"""
职责冲突自动检测器

功能:
- 检测职责描述之间的相似度
- 识别潜在的冲突类型
- 评估冲突严重程度
- 生成解决建议
- 生成详细的冲突报告
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import difflib
from datetime import datetime


class ConflictType(Enum):
    EXACT_DUPLICATE = "完全重复"
    HIGH_SIMILARITY = "高度相似"
    FUNCTIONAL_OVERLAP = "功能重叠"
    DOMAIN_CONFLICT = "领域冲突"
    SCOPE_AMBIGUITY = "范围模糊"


class ConflictSeverity(Enum):
    CRITICAL = "严重"
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


@dataclass
class ConflictInfo:
    file1: str
    file2: str
    filename1: str
    filename2: str
    responsibility1: str
    responsibility2: str
    similarity: float
    conflict_type: ConflictType
    severity: ConflictSeverity
    common_keywords: List[str]
    unique_keywords1: List[str]
    unique_keywords2: List[str]
    suggestions: List[str]


class ResponsibilityConflictDetector:
    def __init__(self, threshold: float = 0.8):
        self.blueprints_dir = 'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS'
        self.threshold = threshold
        self.blueprint_files = []
        self.responsibilities = {}
        self.conflicts = []
        
        self.important_keywords = self._load_important_keywords()
        self.domain_keywords = self._load_domain_keywords()
        
    def _load_important_keywords(self) -> List[str]:
        """加载重要关键词"""
        return [
            "负责", "支持", "提供", "实现", "包括", "功能",
            "优化", "监控", "管理", "处理", "计算", "分析",
            "投资组合", "风险", "交易", "数据", "AI", "机器学习",
            "均值方差", "风险平价", "Black-Litterman", "VaR", "ES",
            "TWAP", "VWAP", "LSTM", "Transformer"
        ]
    
    def _load_domain_keywords(self) -> Dict[str, List[str]]:
        """加载领域关键词"""
        return {
            "portfolio_optimization": [
                "投资组合", "优化", "权重", "配置", "均值方差", "风险平价"
            ],
            "risk_management": [
                "风险", "VaR", "ES", "监控", "归因", "止损"
            ],
            "trading_execution": [
                "交易", "执行", "订单", "路由", "TWAP", "VWAP"
            ],
            "data_governance": [
                "数据", "目录", "血缘", "元数据", "质量"
            ],
            "ai_ml": [
                "AI", "机器学习", "深度学习", "LSTM", "Transformer"
            ],
        }
    
    def scan_blueprint_files(self):
        """扫描蓝图文件"""
        blueprints_path = Path(self.blueprints_dir)
        if not blueprints_path.exists():
            print(f'❌ 蓝图目录不存在: {self.blueprints_dir}')
            return
        
        self.blueprint_files = list(blueprints_path.glob('**/*.md'))
        print(f'  ✅ 找到{len(self.blueprint_files)}个蓝图文件')
    
    def extract_responsibilities(self):
        """提取职责描述"""
        for filepath in self.blueprint_files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                responsibility = self._extract_responsibility(content)
                
                if responsibility:
                    self.responsibilities[str(filepath)] = {
                        'filename': os.path.basename(filepath),
                        'responsibility': responsibility,
                        'keywords': self._extract_keywords(responsibility),
                        'domain': self._detect_domain(responsibility)
                    }
            except Exception as e:
                print(f'  ⚠️ 无法处理文件: {filepath} - {e}')
        
        print(f'  ✅ 提取了{len(self.responsibilities)}个职责描述')
    
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
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        keywords = []
        
        for keyword in self.important_keywords:
            if keyword.lower() in text.lower():
                keywords.append(keyword)
        
        return keywords
    
    def _detect_domain(self, text: str) -> str:
        """检测领域"""
        domain_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text.lower())
            domain_scores[domain] = score
        
        if domain_scores:
            best_domain = max(domain_scores.items(), key=lambda x: x[1])
            if best_domain[1] > 0:
                return best_domain[0]
        
        return "unknown"
    
    def detect_conflicts(self):
        """检测冲突"""
        filepaths = list(self.responsibilities.keys())
        
        for i in range(len(filepaths)):
            for j in range(i + 1, len(filepaths)):
                file1 = filepaths[i]
                file2 = filepaths[j]
                
                resp1 = self.responsibilities[file1]['responsibility']
                resp2 = self.responsibilities[file2]['responsibility']
                
                similarity = self._calculate_similarity(resp1, resp2)
                
                if similarity > self.threshold:
                    conflict = self._analyze_conflict(file1, file2, similarity)
                    self.conflicts.append(conflict)
        
        print(f'  ⚠️ 发现{len(self.conflicts)}个职责冲突')
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算相似度"""
        return difflib.SequenceMatcher(None, text1, text2).ratio()
    
    def _analyze_conflict(self, file1: str, file2: str, similarity: float) -> ConflictInfo:
        """分析冲突"""
        resp1 = self.responsibilities[file1]['responsibility']
        resp2 = self.responsibilities[file2]['responsibility']
        
        keywords1 = set(self.responsibilities[file1]['keywords'])
        keywords2 = set(self.responsibilities[file2]['keywords'])
        
        common_keywords = list(keywords1 & keywords2)
        unique_keywords1 = list(keywords1 - keywords2)
        unique_keywords2 = list(keywords2 - keywords1)
        
        conflict_type = self._determine_conflict_type(similarity, common_keywords)
        severity = self._determine_severity(similarity, conflict_type)
        suggestions = self._generate_suggestions(conflict_type, severity, 
                                                  resp1, resp2, 
                                                  unique_keywords1, unique_keywords2)
        
        return ConflictInfo(
            file1=file1,
            file2=file2,
            filename1=self.responsibilities[file1]['filename'],
            filename2=self.responsibilities[file2]['filename'],
            responsibility1=resp1,
            responsibility2=resp2,
            similarity=similarity,
            conflict_type=conflict_type,
            severity=severity,
            common_keywords=common_keywords,
            unique_keywords1=unique_keywords1,
            unique_keywords2=unique_keywords2,
            suggestions=suggestions
        )
    
    def _determine_conflict_type(self, similarity: float, common_keywords: List[str]) -> ConflictType:
        """确定冲突类型"""
        if similarity > 0.95:
            return ConflictType.EXACT_DUPLICATE
        elif similarity > 0.90:
            return ConflictType.HIGH_SIMILARITY
        elif len(common_keywords) > 5:
            return ConflictType.FUNCTIONAL_OVERLAP
        elif len(common_keywords) > 3:
            return ConflictType.DOMAIN_CONFLICT
        else:
            return ConflictType.SCOPE_AMBIGUITY
    
    def _determine_severity(self, similarity: float, conflict_type: ConflictType) -> ConflictSeverity:
        """确定严重程度"""
        if conflict_type == ConflictType.EXACT_DUPLICATE:
            return ConflictSeverity.CRITICAL
        elif conflict_type == ConflictType.HIGH_SIMILARITY:
            return ConflictSeverity.HIGH
        elif similarity > 0.85:
            return ConflictSeverity.MEDIUM
        else:
            return ConflictSeverity.LOW
    
    def _generate_suggestions(self, conflict_type: ConflictType, severity: ConflictSeverity,
                              resp1: str, resp2: str,
                              unique_keywords1: List[str], unique_keywords2: List[str]) -> List[str]:
        """生成解决建议"""
        suggestions = []
        
        if conflict_type == ConflictType.EXACT_DUPLICATE:
            suggestions.append("建议合并这两个文档或明确区分职责范围")
            suggestions.append("检查是否为重复创建的文档")
        
        elif conflict_type == ConflictType.HIGH_SIMILARITY:
            suggestions.append("建议重新定义职责边界，明确各自的核心功能")
            if unique_keywords1:
                suggestions.append(f"文档1应强调: {', '.join(unique_keywords1)}")
            if unique_keywords2:
                suggestions.append(f"文档2应强调: {', '.join(unique_keywords2)}")
        
        elif conflict_type == ConflictType.FUNCTIONAL_OVERLAP:
            suggestions.append("建议明确功能边界，避免职责重叠")
            suggestions.append("考虑将重叠功能提取到独立模块")
        
        elif conflict_type == ConflictType.DOMAIN_CONFLICT:
            suggestions.append("建议明确领域归属，避免跨领域职责")
            suggestions.append("检查模块划分是否合理")
        
        else:
            suggestions.append("建议进一步细化职责描述")
            suggestions.append("添加更多具体功能点以区分模块")
        
        if severity == ConflictSeverity.CRITICAL:
            suggestions.insert(0, "⚠️ 严重冲突，需要立即处理")
        elif severity == ConflictSeverity.HIGH:
            suggestions.insert(0, "⚠️ 高优先级冲突，建议尽快处理")
        
        return suggestions
    
    def generate_report(self, output_file: Optional[str] = None):
        """生成报告"""
        report_lines = []
        
        report_lines.append('# 职责冲突检测报告')
        report_lines.append('')
        report_lines.append(f'> **检测日期**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        report_lines.append(f'> **相似度阈值**: {self.threshold * 100}%')
        report_lines.append(f'> **检测范围**: {self.blueprints_dir}')
        report_lines.append(f'> **检测标准**: 专业量化机构文档治理五大原则')
        report_lines.append('')
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 📊 一、检测概要')
        report_lines.append('')
        report_lines.append(f'**检测文件数**: {len(self.blueprint_files)}个')
        report_lines.append(f'**提取职责数**: {len(self.responsibilities)}个')
        report_lines.append(f'**发现冲突数**: {len(self.conflicts)}个')
        report_lines.append('')
        
        if self.conflicts:
            report_lines.append('### 1.1 冲突分布')
            report_lines.append('')
            
            severity_counts = {}
            for conflict in self.conflicts:
                severity = conflict.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            report_lines.append('| 严重程度 | 数量 | 占比 |')
            report_lines.append('|----------|------|------|')
            for severity in ['严重', '高', '中', '低']:
                count = severity_counts.get(severity, 0)
                percentage = (count / len(self.conflicts) * 100) if self.conflicts else 0
                report_lines.append(f'| {severity} | {count} | {percentage:.1f}% |')
            report_lines.append('')
            
            type_counts = {}
            for conflict in self.conflicts:
                conflict_type = conflict.conflict_type.value
                type_counts[conflict_type] = type_counts.get(conflict_type, 0) + 1
            
            report_lines.append('### 1.2 冲突类型分布')
            report_lines.append('')
            report_lines.append('| 冲突类型 | 数量 | 占比 |')
            report_lines.append('|----------|------|------|')
            for conflict_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(self.conflicts) * 100) if self.conflicts else 0
                report_lines.append(f'| {conflict_type} | {count} | {percentage:.1f}% |')
            report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        if self.conflicts:
            report_lines.append('## 🔍 二、详细冲突列表')
            report_lines.append('')
            
            sorted_conflicts = sorted(self.conflicts, key=lambda x: x.similarity, reverse=True)
            
            for i, conflict in enumerate(sorted_conflicts, 1):
                report_lines.append(f'### 冲突 {i}: {conflict.filename1} vs {conflict.filename2}')
                report_lines.append('')
                report_lines.append(f'**冲突类型**: {conflict.conflict_type.value}')
                report_lines.append(f'**严重程度**: {conflict.severity.value}')
                report_lines.append(f'**相似度**: {conflict.similarity * 100:.1f}%')
                report_lines.append('')
                
                report_lines.append('**职责描述1**:')
                report_lines.append(f'```')
                report_lines.append(conflict.responsibility1)
                report_lines.append('```')
                report_lines.append('')
                
                report_lines.append('**职责描述2**:')
                report_lines.append(f'```')
                report_lines.append(conflict.responsibility2)
                report_lines.append('```')
                report_lines.append('')
                
                if conflict.common_keywords:
                    report_lines.append(f'**共同关键词**: {", ".join(conflict.common_keywords)}')
                    report_lines.append('')
                
                if conflict.unique_keywords1:
                    report_lines.append(f'**文档1独特关键词**: {", ".join(conflict.unique_keywords1)}')
                    report_lines.append('')
                
                if conflict.unique_keywords2:
                    report_lines.append(f'**文档2独特关键词**: {", ".join(conflict.unique_keywords2)}')
                    report_lines.append('')
                
                report_lines.append('**解决建议**:')
                for suggestion in conflict.suggestions:
                    report_lines.append(f'- {suggestion}')
                report_lines.append('')
                report_lines.append('---')
                report_lines.append('')
        
        report_lines.append('## 📈 三、质量评估')
        report_lines.append('')
        
        total_pairs = len(self.responsibilities) * (len(self.responsibilities) - 1) // 2
        conflict_rate = (len(self.conflicts) / total_pairs * 100) if total_pairs > 0 else 0
        
        report_lines.append(f'**职责冲突率**: {conflict_rate:.2f}%')
        report_lines.append(f'**职责唯一性**: {100 - conflict_rate:.2f}%')
        report_lines.append('')
        
        if self.conflicts:
            critical_count = sum(1 for c in self.conflicts if c.severity == ConflictSeverity.CRITICAL)
            high_count = sum(1 for c in self.conflicts if c.severity == ConflictSeverity.HIGH)
            
            if critical_count > 0:
                report_lines.append(f'⚠️ **发现{critical_count}个严重冲突，需要立即处理**')
            if high_count > 0:
                report_lines.append(f'⚠️ **发现{high_count}个高优先级冲突，建议尽快处理**')
        else:
            report_lines.append('✅ **未发现职责冲突，文档质量良好**')
        
        report_lines.append('')
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 🎯 四、改进建议')
        report_lines.append('')
        
        if self.conflicts:
            report_lines.append('### 4.1 立即处理')
            report_lines.append('')
            critical_conflicts = [c for c in self.conflicts if c.severity == ConflictSeverity.CRITICAL]
            if critical_conflicts:
                for conflict in critical_conflicts[:3]:
                    report_lines.append(f'- 处理冲突: {conflict.filename1} vs {conflict.filename2}')
            else:
                report_lines.append('- 无严重冲突需要立即处理')
            report_lines.append('')
            
            report_lines.append('### 4.2 近期改进')
            report_lines.append('')
            high_conflicts = [c for c in self.conflicts if c.severity == ConflictSeverity.HIGH]
            if high_conflicts:
                for conflict in high_conflicts[:5]:
                    report_lines.append(f'- 优化职责: {conflict.filename1} vs {conflict.filename2}')
            else:
                report_lines.append('- 无高优先级冲突需要近期改进')
            report_lines.append('')
            
            report_lines.append('### 4.3 长期优化')
            report_lines.append('')
            report_lines.append('- 建立职责审查机制')
            report_lines.append('- 定期运行冲突检测')
            report_lines.append('- 优化职责描述模板')
        else:
            report_lines.append('### 4.1 持续保持')
            report_lines.append('')
            report_lines.append('- 继续保持当前文档质量')
            report_lines.append('- 定期运行冲突检测')
            report_lines.append('- 建立预防机制')
        
        report_lines.append('')
        report_lines.append('---')
        report_lines.append('')
        report_lines.append(f'**报告生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        report_lines.append(f'**检测工具版本**: v1.0.0')
        
        report_content = '\n'.join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f'  ✅ 报告已生成: {output_file}')
        else:
            print(report_content)
    
    def run(self, output_file: Optional[str] = None):
        """运行检测器"""
        print('=' * 80)
        print('职责冲突自动检测器')
        print('=' * 80)
        print(f'相似度阈值: {self.threshold * 100}%')
        print()
        
        print('1. 扫描蓝图文件...')
        self.scan_blueprint_files()
        print()
        
        print('2. 提取职责描述...')
        self.extract_responsibilities()
        print()
        
        print('3. 检测职责冲突...')
        self.detect_conflicts()
        print()
        
        print('4. 生成检测报告...')
        self.generate_report(output_file)
        print()
        
        print('=' * 80)
        print('检测完成')
        print('=' * 80)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='职责冲突自动检测器')
    parser.add_argument('--threshold', type=float, default=0.8, help='相似度阈值 (默认: 0.8)')
    parser.add_argument('--output', help='输出报告文件路径')
    
    args = parser.parse_args()
    
    detector = ResponsibilityConflictDetector(threshold=args.threshold)
    detector.run(output_file=args.output)


if __name__ == '__main__':
    main()
