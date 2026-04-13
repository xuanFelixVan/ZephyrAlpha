# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
自动化文档审计工具
提供链接检查、版本检查、分类检查功能

功能:
    - 检查文档内部链接有效性
    - 检查版本号格式和一致性
    - 检查文档分类规范性
    - 生成审计报告

使用方式:
    python scripts/document_auditor.py --check-links
    python scripts/document_auditor.py --check-versions
    python scripts/document_auditor.py --check-classification
    python scripts/document_auditor.py --all
"""
import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class AuditIssue:
    """审计问题"""
    file_path: str
    issue_type: str
    severity: str  # 'error', 'warning', 'info'
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


class DocumentAuditor:
    """
    文档审计器
    
    审计类型:
        1. 链接检查: 检查内部链接有效性
        2. 版本检查: 检查版本号格式和一致性
        3. 分类检查: 检查文档分类规范性
    """
    
    # 版本号正则表达式
    VERSION_PATTERN = re.compile(r'version:\s*["\']?(\d+\.\d+\.\d+)["\']?', re.IGNORECASE)
    SYSTEM_VERSION_PATTERN = re.compile(r'v(\d+\.\d+\.\d+)')
    
    # 文档分类标准
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
    
    # 必需的元数据字段
    REQUIRED_METADATA = {
        'module_id',
        'version',
        'status',
        'created_date',
        'last_updated',
        'owner',
    }
    
    # 推荐的元数据字段
    RECOMMENDED_METADATA = {
        'standard_type',
        'applicable_scope',
        'compliance_level',
        'parent_document',
        'implementation_status',
    }
    
    def __init__(self, project_root: str):
        """
        初始化审计器
        
        参数:
            project_root: 项目根目录路径
        """
        self.project_root = Path(project_root)
        self.issues: List[AuditIssue] = []
        self.scanned_files: int = 0
        
    def scan_markdown_files(self) -> List[Path]:
        """扫描所有Markdown文件"""
        logger.info(f"开始扫描Markdown文件: {self.project_root}")
        
        files = []
        for root, dirs, filenames in os.walk(self.project_root):
            # 过滤排除目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {'A股数据', 'node_modules'}]
            
            for filename in filenames:
                if filename.endswith('.md'):
                    file_path = Path(root) / filename
                    files.append(file_path)
        
        logger.info(f"扫描完成，共找到 {len(files)} 个Markdown文件")
        return files
    
    def check_links(self, files: Optional[List[Path]] = None) -> List[AuditIssue]:
        """
        检查文档内部链接有效性
        
        参数:
            files: 待检查的文件列表 (可选)
        
        返回:
            List[AuditIssue]: 链接问题列表
        """
        if files is None:
            files = self.scan_markdown_files()
        
        logger.info("开始检查文档链接...")
        link_issues = []
        
        # Markdown链接正则: [text](path)
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    matches = link_pattern.findall(line)
                    for text, link in matches:
                        # 跳过外部链接和锚点链接
                        if link.startswith(('http://', 'https://', '#', 'mailto:')):
                            continue
                        
                        # 检查相对路径链接
                        if not link.startswith('/'):
                            target_path = (file_path.parent / link).resolve()
                        else:
                            target_path = (self.project_root / link.lstrip('/')).resolve()
                        
                        # 检查文件是否存在
                        if not target_path.exists():
                            link_issues.append(AuditIssue(
                                file_path=str(file_path.relative_to(self.project_root)),
                                issue_type='broken_link',
                                severity='warning',
                                message=f'链接目标不存在: {link}',
                                line_number=line_num,
                                suggestion=f'检查链接路径是否正确: {link}'
                            ))
            
            except Exception as e:
                logger.error(f"检查链接失败: {file_path}, {e}")
        
        self.issues.extend(link_issues)
        logger.info(f"链接检查完成，发现 {len(link_issues)} 个问题")
        return link_issues
    
    def check_versions(self, files: Optional[List[Path]] = None) -> List[AuditIssue]:
        """
        检查版本号格式和一致性
        
        参数:
            files: 待检查的文件列表 (可选)
        
        返回:
            List[AuditIssue]: 版本问题列表
        """
        if files is None:
            files = self.scan_markdown_files()
        
        logger.info("开始检查版本号...")
        version_issues = []
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查版本号格式
                version_matches = self.VERSION_PATTERN.findall(content)
                for version in version_matches:
                    # 验证语义化版本格式
                    parts = version.split('.')
                    if len(parts) != 3:
                        version_issues.append(AuditIssue(
                            file_path=str(file_path.relative_to(self.project_root)),
                            issue_type='invalid_version_format',
                            severity='error',
                            message=f'版本号格式不正确: {version}',
                            suggestion='使用语义化版本格式: X.Y.Z (如 1.0.0)'
                        ))
                    else:
                        # 检查各部分是否为数字
                        try:
                            major, minor, patch = map(int, parts)
                            if major < 0 or minor < 0 or patch < 0:
                                raise ValueError("版本号不能为负数")
                        except ValueError as e:
                            version_issues.append(AuditIssue(
                                file_path=str(file_path.relative_to(self.project_root)),
                                issue_type='invalid_version_number',
                                severity='error',
                                message=f'版本号包含非数字: {version}',
                                suggestion='版本号各部分必须是非负整数'
                            ))
            
            except Exception as e:
                logger.error(f"检查版本失败: {file_path}, {e}")
        
        self.issues.extend(version_issues)
        logger.info(f"版本检查完成，发现 {len(version_issues)} 个问题")
        return version_issues
    
    def check_classification(self, files: Optional[List[Path]] = None) -> List[AuditIssue]:
        """
        检查文档分类规范性
        
        参数:
            files: 待检查的文件列表 (可选)
        
        返回:
            List[AuditIssue]: 分类问题列表
        """
        if files is None:
            files = self.scan_markdown_files()
        
        logger.info("开始检查文档分类...")
        classification_issues = []
        
        for file_path in files:
            try:
                relative_path = file_path.relative_to(self.project_root)
                path_parts = relative_path.parts
                
                # 检查是否在标准分类目录下
                if len(path_parts) >= 2 and path_parts[0] == 'docs':
                    category = path_parts[1]
                    
                    # 检查是否为标准分类
                    if category not in self.STANDARD_CATEGORIES and not category.startswith('design'):
                        classification_issues.append(AuditIssue(
                            file_path=str(relative_path),
                            issue_type='non_standard_category',
                            severity='info',
                            message=f'文档不在标准分类目录下: {category}',
                            suggestion=f'建议将文档移至标准分类目录: {", ".join(self.STANDARD_CATEGORIES)}'
                        ))
                
                # 检查元数据完整性
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取YAML元数据
                if content.startswith('---'):
                    metadata_end = content.find('---', 3)
                    if metadata_end != -1:
                        metadata_text = content[3:metadata_end]
                        
                        # 检查必需字段
                        for field in self.REQUIRED_METADATA:
                            if f'{field}:' not in metadata_text:
                                classification_issues.append(AuditIssue(
                                    file_path=str(relative_path),
                                    issue_type='missing_metadata',
                                    severity='warning',
                                    message=f'缺少必需的元数据字段: {field}',
                                    suggestion=f'在文档元数据中添加 {field} 字段'
                                ))
                        
                        # 检查推荐字段
                        for field in self.RECOMMENDED_METADATA:
                            if f'{field}:' not in metadata_text:
                                classification_issues.append(AuditIssue(
                                    file_path=str(relative_path),
                                    issue_type='missing_recommended_metadata',
                                    severity='info',
                                    message=f'缺少推荐的元数据字段: {field}',
                                    suggestion=f'建议在文档元数据中添加 {field} 字段'
                                ))
            
            except Exception as e:
                logger.error(f"检查分类失败: {file_path}, {e}")
        
        self.issues.extend(classification_issues)
        logger.info(f"分类检查完成，发现 {len(classification_issues)} 个问题")
        return classification_issues
    
    def run_full_audit(self) -> Dict:
        """
        执行完整审计
        
        返回:
            Dict: 审计报告
        """
        logger.info("开始执行完整审计...")
        
        files = self.scan_markdown_files()
        self.scanned_files = len(files)
        
        # 执行所有检查
        link_issues = self.check_links(files)
        version_issues = self.check_versions(files)
        classification_issues = self.check_classification(files)
        
        # 统计问题
        issues_by_type = defaultdict(list)
        issues_by_severity = defaultdict(int)
        
        for issue in self.issues:
            issues_by_type[issue.issue_type].append(issue)
            issues_by_severity[issue.severity] += 1
        
        # 生成报告
        report = {
            'summary': {
                'scan_time': datetime.now().isoformat(),
                'scanned_files': self.scanned_files,
                'total_issues': len(self.issues),
                'issues_by_severity': dict(issues_by_severity),
                'issues_by_type': {k: len(v) for k, v in issues_by_type.items()},
            },
            'details': {
                'link_issues': [asdict(issue) for issue in link_issues],
                'version_issues': [asdict(issue) for issue in version_issues],
                'classification_issues': [asdict(issue) for issue in classification_issues],
            },
            'recommendations': self._generate_recommendations(),
        }
        
        logger.info(f"审计完成，共发现 {len(self.issues)} 个问题")
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 根据问题类型生成建议
        issue_types = set(issue.issue_type for issue in self.issues)
        
        if 'broken_link' in issue_types:
            recommendations.append('修复损坏的链接，确保所有内部链接指向有效文件')
        
        if 'invalid_version_format' in issue_types or 'invalid_version_number' in issue_types:
            recommendations.append('统一版本号格式，使用语义化版本 (X.Y.Z)')
        
        if 'missing_metadata' in issue_types:
            recommendations.append('完善文档元数据，添加所有必需字段')
        
        if 'non_standard_category' in issue_types:
            recommendations.append('将文档移至标准分类目录，提高文档组织性')
        
        return recommendations
    
    def save_report(self, report: Dict, output_path: str) -> None:
        """
        保存审计报告
        
        参数:
            report: 审计报告
            output_path: 输出文件路径
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"审计报告已保存到: {output_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='自动化文档审计工具')
    parser.add_argument(
        '--project-root',
        default='d:/ZephyrAlpha',
        help='项目根目录路径'
    )
    parser.add_argument(
        '--output',
        default='docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/document_audit_report.json',
        help='输出审计报告路径'
    )
    parser.add_argument(
        '--check-links',
        action='store_true',
        help='仅检查链接'
    )
    parser.add_argument(
        '--check-versions',
        action='store_true',
        help='仅检查版本'
    )
    parser.add_argument(
        '--check-classification',
        action='store_true',
        help='仅检查分类'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='执行完整审计'
    )
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建审计器
    auditor = DocumentAuditor(project_root=args.project_root)
    
    # 执行审计
    if args.all or (not args.check_links and not args.check_versions and not args.check_classification):
        report = auditor.run_full_audit()
    else:
        files = auditor.scan_markdown_files()
        
        issues = []
        if args.check_links:
            issues.extend(auditor.check_links(files))
        if args.check_versions:
            issues.extend(auditor.check_versions(files))
        if args.check_classification:
            issues.extend(auditor.check_classification(files))
        
        report = {
            'summary': {
                'scan_time': datetime.now().isoformat(),
                'scanned_files': len(files),
                'total_issues': len(issues),
            },
            'issues': [asdict(issue) for issue in issues],
        }
    
    # 保存报告
    auditor.save_report(report, args.output)
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("文档审计报告")
    print("=" * 60)
    print(f"扫描文件数: {report['summary']['scanned_files']}")
    print(f"发现问题数: {report['summary']['total_issues']}")
    
    if 'issues_by_severity' in report['summary']:
        print("\n问题严重性分布:")
        for severity, count in report['summary']['issues_by_severity'].items():
            print(f"  {severity}: {count}")
    
    if 'issues_by_type' in report['summary']:
        print("\n问题类型分布:")
        for issue_type, count in report['summary']['issues_by_type'].items():
            print(f"  {issue_type}: {count}")
    
    if report.get('recommendations'):
        print("\n改进建议:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    print("=" * 60)


if __name__ == '__main__':
    main()
