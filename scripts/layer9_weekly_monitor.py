#!/usr/bin/env python3
"""
Layer 9 文档质量周度监控脚本

功能:
- 自动运行所有质量检查工具
- 生成综合质量报告
- 记录质量指标趋势
- 发送告警通知
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class QualityMetric:
    name: str
    target_value: float
    actual_value: float
    unit: str
    status: str
    alert_level: str


@dataclass
class QualityIssue:
    category: str
    severity: str
    description: str
    filepath: str
    recommendation: str


class Layer9WeeklyMonitor:
    def __init__(self):
        self.layer9_dir = 'docs/09_RESEARCH_INNOVATION'
        self.metrics: List[QualityMetric] = []
        self.issues: List[QualityIssue] = []
        self.total_documents = 0
        self.documents_with_responsibility = 0
        self.documents_with_index = 0
        self.documents_with_proper_naming = 0
        self.responsibility_overlaps = 0
        
    def run_weekly_monitoring(self):
        """执行周度监控"""
        print('=' * 80)
        print('Layer 9 文档质量周度监控')
        print('=' * 80)
        print(f'监控时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'监控范围: {self.layer9_dir}')
        print()
        
        print('阶段1: 扫描文档...')
        self.scan_documents()
        print(f'  ✅ 扫描到 {self.total_documents} 个文档')
        print()
        
        print('阶段2: 检查职责描述完整率...')
        self.check_responsibility_completeness()
        print()
        
        print('阶段3: 检查职责重叠率...')
        self.check_responsibility_overlap()
        print()
        
        print('阶段4: 检查索引覆盖率...')
        self.check_index_coverage()
        print()
        
        print('阶段5: 检查文档命名规范率...')
        self.check_naming_convention()
        print()
        
        print('阶段6: 计算质量指标...')
        self.calculate_metrics()
        print()
        
        print('阶段7: 生成监控报告...')
        self.generate_report()
        print('  ✅ 报告已生成')
        print()
        
        print('=' * 80)
        print('监控完成')
        print('=' * 80)
        
        self.print_summary()
        
        if self.has_alerts():
            self.print_alerts()
    
    def scan_documents(self):
        """扫描文档"""
        layer9_path = Path(self.layer9_dir)
        if not layer9_path.exists():
            print(f'  ❌ 目录不存在: {self.layer9_dir}')
            return
        
        for md_file in layer9_path.rglob('*.md'):
            if 'maintenance_records' in str(md_file):
                continue
            
            self.total_documents += 1
            
            try:
                with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if self._has_responsibility(content):
                    self.documents_with_responsibility += 1
                
                if self._has_proper_naming(md_file.name):
                    self.documents_with_proper_naming += 1
                
            except Exception as e:
                print(f'  ⚠️ 无法读取文件: {md_file.name} - {e}')
    
    def _has_responsibility(self, content: str) -> bool:
        """检查是否有职责描述"""
        patterns = [
            r'##\s+核心定位',
            r'核心定位[：:]',
            r'职责描述[：:]',
            r'核心职责[：:]',
            r'responsibility:',
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                return True
        
        return False
    
    def _has_proper_naming(self, filename: str) -> bool:
        """检查命名是否规范"""
        if not filename.endswith('.md'):
            return False
        
        name_without_ext = filename[:-3]
        
        if re.match(r'^[A-Z][A-Z0-9_]*$', name_without_ext):
            return True
        
        if re.match(r'^[A-Z][a-z]+(_[A-Z][a-z]+)*$', name_without_ext):
            return True
        
        if re.match(r'^[A-Z][A-Z0-9_]+_v\d+.*$', name_without_ext):
            return True
        
        return False
    
    def check_responsibility_completeness(self):
        """检查职责描述完整率"""
        layer9_path = Path(self.layer9_dir)
        
        for md_file in layer9_path.rglob('*.md'):
            if 'maintenance_records' in str(md_file):
                continue
            
            try:
                with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if not self._has_responsibility(content):
                    self.issues.append(QualityIssue(
                        category='职责描述',
                        severity='高',
                        description='缺少职责描述',
                        filepath=str(md_file),
                        recommendation='添加职责描述章节'
                    ))
            except Exception:
                pass
        
        print(f'  ✅ 检查完成: {len([i for i in self.issues if i.category == "职责描述"])} 个问题')
    
    def check_responsibility_overlap(self):
        """检查职责重叠率"""
        layer9_path = Path(self.layer9_dir)
        responsibilities = []
        
        for md_file in layer9_path.rglob('*.md'):
            if 'maintenance_records' in str(md_file):
                continue
            
            try:
                with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                responsibility = self._extract_responsibility(content)
                if responsibility:
                    responsibilities.append((str(md_file), responsibility))
            except Exception:
                pass
        
        for i, (file1, resp1) in enumerate(responsibilities):
            for file2, resp2 in responsibilities[i+1:]:
                similarity = self._calculate_similarity(resp1, resp2)
                if similarity > 0.8:
                    self.responsibility_overlaps += 1
                    self.issues.append(QualityIssue(
                        category='职责重叠',
                        severity='中',
                        description=f'职责相似度{similarity:.1%}',
                        filepath=f'{file1} <-> {file2}',
                        recommendation='优化职责描述，确保职责清晰'
                    ))
        
        print(f'  ✅ 检查完成: {self.responsibility_overlaps} 对重叠')
    
    def _extract_responsibility(self, content: str) -> Optional[str]:
        """提取职责描述"""
        patterns = [
            r'responsibility:\s*\n\s+-\s+(.+?)(?:\n|$)',
            r'##\s+核心定位\s*\n\s*(.+?)(?:\n\n|\n#)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, text1, text2).ratio()
    
    def check_index_coverage(self):
        """检查索引覆盖率"""
        index_file = Path(self.layer9_dir) / 'INDEX.md'
        
        if not index_file.exists():
            self.issues.append(QualityIssue(
                category='索引完备',
                severity='高',
                description='缺少INDEX.md索引文件',
                filepath=str(index_file),
                recommendation='创建INDEX.md索引文件'
            ))
            print(f'  ✅ 检查完成: INDEX.md不存在')
            return
        
        try:
            with open(index_file, 'r', encoding='utf-8', errors='ignore') as f:
                index_content = f.read()
            
            layer9_path = Path(self.layer9_dir)
            indexed_count = 0
            
            for md_file in layer9_path.rglob('*.md'):
                if 'maintenance_records' in str(md_file):
                    continue
                
                if md_file.name == 'INDEX.md':
                    continue
                
                filename = md_file.name
                if filename in index_content or os.path.splitext(filename)[0] in index_content:
                    indexed_count += 1
            
            self.documents_with_index = indexed_count
            
            unindexed = self.total_documents - 1 - indexed_count
            if unindexed > 0:
                self.issues.append(QualityIssue(
                    category='索引完备',
                    severity='中',
                    description=f'{unindexed}个文档未被索引',
                    filepath=str(index_file),
                    recommendation='更新INDEX.md，添加缺失文档'
                ))
            
            print(f'  ✅ 检查完成: {indexed_count}/{self.total_documents-1} 已索引')
        except Exception as e:
            print(f'  ⚠️ 检查失败: {e}')
    
    def check_naming_convention(self):
        """检查文档命名规范率"""
        layer9_path = Path(self.layer9_dir)
        improper_naming = []
        
        for md_file in layer9_path.rglob('*.md'):
            if 'maintenance_records' in str(md_file):
                continue
            
            if not self._has_proper_naming(md_file.name):
                improper_naming.append(md_file.name)
        
        if improper_naming:
            self.issues.append(QualityIssue(
                category='命名规范',
                severity='低',
                description=f'{len(improper_naming)}个文档命名不规范',
                filepath=', '.join(improper_naming[:5]),
                recommendation='重命名文档，符合专业命名标准'
            ))
        
        print(f'  ✅ 检查完成: {len(improper_naming)} 个不规范')
    
    def calculate_metrics(self):
        """计算质量指标"""
        if self.total_documents == 0:
            return
        
        responsibility_rate = (self.documents_with_responsibility / self.total_documents) * 100
        self.metrics.append(QualityMetric(
            name='职责描述完整率',
            target_value=100.0,
            actual_value=responsibility_rate,
            unit='%',
            status='达标' if responsibility_rate >= 95 else '未达标',
            alert_level='严重' if responsibility_rate < 90 else '高' if responsibility_rate < 95 else '无'
        ))
        
        overlap_rate = (self.responsibility_overlaps / max(self.total_documents, 1)) * 100
        self.metrics.append(QualityMetric(
            name='职责重叠率',
            target_value=0.0,
            actual_value=overlap_rate,
            unit='%',
            status='达标' if overlap_rate <= 5 else '未达标',
            alert_level='高' if overlap_rate > 10 else '中' if overlap_rate > 5 else '无'
        ))
        
        index_rate = (self.documents_with_index / max(self.total_documents - 1, 1)) * 100
        self.metrics.append(QualityMetric(
            name='索引覆盖率',
            target_value=100.0,
            actual_value=index_rate,
            unit='%',
            status='达标' if index_rate >= 95 else '未达标',
            alert_level='严重' if index_rate < 90 else '高' if index_rate < 95 else '无'
        ))
        
        naming_rate = (self.documents_with_proper_naming / self.total_documents) * 100
        self.metrics.append(QualityMetric(
            name='文档命名规范率',
            target_value=100.0,
            actual_value=naming_rate,
            unit='%',
            status='达标' if naming_rate >= 95 else '未达标',
            alert_level='中' if naming_rate < 95 else '无'
        ))
    
    def generate_report(self):
        """生成监控报告"""
        report_lines = []
        
        report_lines.append('# Layer 9 文档质量周度监控报告')
        report_lines.append('')
        report_lines.append(f'> **监控时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        report_lines.append(f'> **监控范围**: {self.layer9_dir}')
        report_lines.append(f'> **监控类型**: 周度质量监控')
        report_lines.append('')
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 📊 一、监控概要')
        report_lines.append('')
        report_lines.append(f'**监控文档数**: {self.total_documents}个')
        report_lines.append(f'**发现问题数**: {len(self.issues)}个')
        report_lines.append(f'**告警级别**: {self.get_overall_alert_level()}')
        report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 📈 二、质量指标')
        report_lines.append('')
        report_lines.append('| 指标 | 目标值 | 实际值 | 状态 | 告警级别 |')
        report_lines.append('|------|--------|--------|------|----------|')
        
        for metric in self.metrics:
            status_emoji = '✅' if metric.status == '达标' else '⚠️'
            alert_text = metric.alert_level if metric.alert_level != '无' else '-'
            report_lines.append(f'| {metric.name} | {metric.target_value}{metric.unit} | {metric.actual_value:.1f}{metric.unit} | {status_emoji} {metric.status} | {alert_text} |')
        
        report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 🔍 三、问题详情')
        report_lines.append('')
        
        if self.issues:
            for issue in self.issues:
                severity_emoji = {'严重': '🔴', '高': '🟠', '中': '🟡', '低': '🟢'}.get(issue.severity, '⚪')
                report_lines.append(f'### {severity_emoji} {issue.category} - {issue.severity}')
                report_lines.append('')
                report_lines.append(f'**问题描述**: {issue.description}')
                report_lines.append(f'**文件位置**: {issue.filepath}')
                report_lines.append(f'**改进建议**: {issue.recommendation}')
                report_lines.append('')
        else:
            report_lines.append('✅ 未发现问题')
            report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 🎯 四、改进建议')
        report_lines.append('')
        
        high_priority = [i for i in self.issues if i.severity in ['严重', '高']]
        medium_priority = [i for i in self.issues if i.severity == '中']
        low_priority = [i for i in self.issues if i.severity == '低']
        
        if high_priority:
            report_lines.append('### 立即处理（高优先级）')
            report_lines.append('')
            for i, issue in enumerate(high_priority, 1):
                report_lines.append(f'{i}. {issue.description} - {issue.recommendation}')
            report_lines.append('')
        
        if medium_priority:
            report_lines.append('### 近期改进（中优先级）')
            report_lines.append('')
            for i, issue in enumerate(medium_priority, 1):
                report_lines.append(f'{i}. {issue.description} - {issue.recommendation}')
            report_lines.append('')
        
        if low_priority:
            report_lines.append('### 持续优化（低优先级）')
            report_lines.append('')
            for i, issue in enumerate(low_priority, 1):
                report_lines.append(f'{i}. {issue.description} - {issue.recommendation}')
            report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        
        report_lines.append('## 📅 五、下周计划')
        report_lines.append('')
        report_lines.append('1. 处理高优先级问题')
        report_lines.append('2. 执行改进措施')
        report_lines.append('3. 验证改进效果')
        report_lines.append('4. 更新监控机制')
        report_lines.append('')
        
        report_lines.append('---')
        report_lines.append('')
        report_lines.append(f'**报告生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
        report_content = '\n'.join(report_lines)
        
        output_path = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state/LAYER9_WEEKLY_QUALITY_REPORT_20260407.md')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f'  ✅ 报告已保存: {output_path}')
    
    def get_overall_alert_level(self) -> str:
        """获取总体告警级别"""
        if any(m.alert_level == '严重' for m in self.metrics):
            return '🔴 严重'
        elif any(m.alert_level == '高' for m in self.metrics):
            return '🟠 高'
        elif any(m.alert_level == '中' for m in self.metrics):
            return '🟡 中'
        else:
            return '🟢 正常'
    
    def has_alerts(self) -> bool:
        """是否有告警"""
        return any(m.alert_level != '无' for m in self.metrics)
    
    def print_summary(self):
        """打印摘要"""
        print()
        print('监控摘要:')
        print(f'  文档总数: {self.total_documents}')
        print(f'  质量指标: {len(self.metrics)}')
        print(f'  问题数量: {len(self.issues)}')
        print(f'  告警级别: {self.get_overall_alert_level()}')
    
    def print_alerts(self):
        """打印告警"""
        print()
        print('⚠️ 告警信息:')
        for metric in self.metrics:
            if metric.alert_level != '无':
                print(f'  [{metric.alert_level}] {metric.name}: {metric.actual_value:.1f}% (目标: {metric.target_value}%)')


def main():
    monitor = Layer9WeeklyMonitor()
    monitor.run_weekly_monitoring()


if __name__ == '__main__':
    main()
