#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
文档质量综合报告生成器
整合所有检查结果，生成综合质量报告
"""

import json
from pathlib import Path
from datetime import datetime

class QualityReportGenerator:
    def __init__(self):
        self.docs_root = Path('docs')
        self.audit_dir = self.docs_root / '09_AUDIT' / 'STATE'
        self.results = {
            'scan_time': datetime.now().isoformat(),
            'reports': {},
            'summary': {}
        }

    def load_latest_reports(self):
        """加载最新的检查报告"""
        print("📂 加载最新检查报告...")

        report_types = [
            ('link_check', 'CI_CD_LINK_CHECK_*.json'),
            ('yaml_metadata', 'YAML_VERSION_ADDITION_REPORT_*.json'),
            ('quality_check', 'QUALITY_REPORT_*.json')
        ]

        for report_type, pattern in report_types:
            files = list(self.audit_dir.glob(pattern))
            if files:
                latest_file = max(files, key=lambda x: x.stat().st_mtime)
                try:
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        self.results['reports'][report_type] = json.load(f)
                    print(f"  ✓ 加载 {report_type}: {latest_file.name}")
                except Exception as e:
                    print(f"  ✗ 加载失败 {report_type}: {e}")

    def calculate_comprehensive_score(self):
        """计算综合质量分数"""
        print("📊 计算综合质量分数...")

        score = 0
        max_score = 100

        # 链接有效性 (25分)
        link_report = self.results['reports'].get('link_check', {})
        if link_report:
            total_links = link_report.get('total_links', 1)
            valid_links = link_report.get('valid_links', 0)
            link_score = (valid_links / max(total_links, 1)) * 100
            score += link_score * 0.25

        # YAML元数据完整性 (25分)
        yaml_report = self.results['reports'].get('yaml_metadata', {})
        if yaml_report:
            yaml_completeness = yaml_report.get('files_with_version', 0) / max(yaml_report.get('total_files', 1), 1) * 100
            score += yaml_completeness * 0.25

        # 文档质量总分 (50分)
        quality_report = self.results['reports'].get('quality_check', {})
        if quality_report:
            quality_score = quality_report.get('summary', {}).get('quality_score', 0)
            score += quality_score * 0.5

        self.results['summary'] = {
            'comprehensive_score': round(score, 2),
            'grade': self._get_grade(score),
            'timestamp': datetime.now().isoformat()
        }

        print(f"  ✓ 综合质量分数: {score:.2f}/100")
        print(f"  ✓ 质量等级: {self._get_grade(score)}")

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

    def generate_comprehensive_report(self):
        """生成综合报告"""
        output_dir = self.audit_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d')
        report_file = output_dir / f'COMPREHENSIVE_QUALITY_REPORT_{timestamp}.md'
        json_file = output_dir / f'COMPREHENSIVE_QUALITY_REPORT_{timestamp}.json'

        # 生成Markdown报告
        report_lines = [
            "# 文档质量综合报告",
            "",
            f"> **报告时间**: {self.results['scan_time']}",
            "",
            "## 🎯 综合质量评估",
            "",
            f"### 总体得分: {self.results['summary']['comprehensive_score']}/100",
            "",
            f"**质量等级**: {self.results['summary']['grade']}",
            "",
            "---",
            "",
            "## 📊 分项评估",
            ""
        ]

        # 链接有效性
        link_report = self.results['reports'].get('link_check', {})
        if link_report:
            total_links = link_report.get('total_links', 1)
            valid_links = link_report.get('valid_links', 0)
            invalid_links = link_report.get('invalid_links', 0)
            link_rate = (valid_links / max(total_links, 1)) * 100

            report_lines.extend([
                "### 1. 链接有效性 (权重25%)",
                "",
                f"- **总链接数**: {total_links}",
                f"- **有效链接数**: {valid_links}",
                f"- **无效链接数**: {invalid_links}",
                f"- **有效率**: {link_rate:.2f}%",
                f"- **得分**: {link_rate * 0.25:.2f}/25",
                ""
            ])

        # YAML元数据
        yaml_report = self.results['reports'].get('yaml_metadata', {})
        if yaml_report:
            total_files = yaml_report.get('total_files', 1)
            files_with_version = yaml_report.get('files_with_version', 0)
            yaml_rate = (files_with_version / max(total_files, 1)) * 100

            report_lines.extend([
                "### 2. YAML元数据完整性 (权重25%)",
                "",
                f"- **扫描文件数**: {total_files}",
                f"- **包含版本号文件数**: {files_with_version}",
                f"- **完整率**: {yaml_rate:.2f}%",
                f"- **得分**: {yaml_rate * 0.25:.2f}/25",
                ""
            ])

        # 文档质量
        quality_report = self.results['reports'].get('quality_check', {})
        if quality_report:
            quality_score = quality_report.get('summary', {}).get('quality_score', 0)
            quality_grade = quality_report.get('summary', {}).get('grade', 'N/A')

            report_lines.extend([
                "### 3. 文档质量总分 (权重50%)",
                "",
                f"- **质量分数**: {quality_score}/100",
                f"- **质量等级**: {quality_grade}",
                f"- **得分**: {quality_score * 0.5:.2f}/50",
                ""
            ])

        # 改进建议
        report_lines.extend([
            "---",
            "",
            "## 💡 改进建议",
            "",
            "### 立即行动",
            ""
        ])

        if link_report and link_report.get('invalid_links', 0) > 100:
            report_lines.append("- 运行智能链接修复工具修复无效链接")

        if yaml_report and yaml_report.get('files_without_version', 0) > 50:
            report_lines.append("- 为缺少版本号的文档添加YAML元数据")

        report_lines.extend([
            "",
            "### 短期行动",
            "",
            "- 定期运行质量检查工具",
            "- 建立文档更新提醒机制",
            "- 优化文档结构和内容",
            "",
            "### 长期行动",
            "",
            "- 建立CI/CD自动化检查流程",
            "- 制定文档版本号命名规范",
            "- 开发自动化质量监控工具",
            "",
            "---",
            "",
            "## 📈 趋势分析",
            "",
            "### 历史对比",
            "",
            "建议每周运行此报告，对比历史数据，观察质量趋势。",
            "",
            "### 关键指标",
            "",
            "- 链接有效率目标: > 95%",
            "- YAML完整率目标: > 95%",
            "- 综合质量分数目标: > 85分",
            "",
            "---",
            f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        # 保存JSON结果
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 综合报告已生成: {report_file}")
        print(f"✅ JSON已保存: {json_file}")

        return report_file

    def run(self):
        """运行报告生成"""
        print("=" * 60)
        print("文档质量综合报告生成器")
        print("=" * 60)

        self.load_latest_reports()
        self.calculate_comprehensive_score()

        print("\n" + "=" * 60)
        print("报告生成完成!")
        print("=" * 60)

        self.generate_comprehensive_report()

if __name__ == '__main__':
    generator = QualityReportGenerator()
    generator.run()
