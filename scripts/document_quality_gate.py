# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
文档质量门禁检查工具
确保新增和修改的文档符合质量标准

功能:
    - P0阻断级检查: 元数据完整性、版本号格式、文档ID唯一性
    - P1警告级检查: 推荐字段、内部链接、文档分类
    - P2提示级检查: 文档结构、代码示例
    - 生成质量门禁报告

使用方式:
    python scripts/document_quality_gate.py --file docs/example.md
    python scripts/document_quality_gate.py --files docs/file1.md docs/file2.md
    python scripts/document_quality_gate.py --changed
"""
import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class QualityCheckResult:
    """质量检查结果"""
    file_path: str
    check_time: str
    passed: bool
    p0_checks: Dict[str, bool]
    p1_checks: Dict[str, bool]
    p2_checks: Dict[str, bool]
    issues: List[Dict]
    warnings: List[Dict]
    suggestions: List[Dict]


class DocumentQualityGate:
    """
    文档质量门禁检查器
    
    检查级别:
        P0 (阻断): 必须通过，否则不允许提交
        P1 (警告): 建议修复，允许临时绕过
        P2 (提示): 优化建议，不影响提交
    """
    
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
    
    # 版本号正则表达式
    VERSION_PATTERN = re.compile(r'^v?\d+\.\d+\.\d+$')
    
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
    
    def __init__(self, project_root: str):
        """
        初始化质量门禁检查器
        
        参数:
            project_root: 项目根目录路径
        """
        self.project_root = Path(project_root)
        self.module_ids: Dict[str, str] = {}  # module_id -> file_path
        
    def check_file(self, file_path: str) -> QualityCheckResult:
        """
        检查单个文件
        
        参数:
            file_path: 文件路径
        
        返回:
            QualityCheckResult: 检查结果
        """
        file_path = Path(file_path)
        
        # 如果是相对路径，转换为绝对路径
        if not file_path.is_absolute():
            file_path = self.project_root / file_path
        
        relative_path = str(file_path.relative_to(self.project_root))
        
        logger.info(f"检查文件: {relative_path}")
        
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return QualityCheckResult(
                file_path=relative_path,
                check_time=datetime.now().isoformat(),
                passed=False,
                p0_checks={'file_readable': False},
                p1_checks={},
                p2_checks={},
                issues=[{
                    'level': 'P0',
                    'type': 'file_not_readable',
                    'message': f'文件无法读取: {e}',
                }],
                warnings=[],
                suggestions=[],
            )
        
        # 提取元数据
        metadata = self._extract_metadata(content)
        
        # 执行检查
        p0_checks, p0_issues = self._check_p0(relative_path, metadata, content)
        p1_checks, p1_warnings = self._check_p1(relative_path, metadata, content)
        p2_checks, p2_suggestions = self._check_p2(relative_path, content)
        
        # 判断是否通过
        passed = all(p0_checks.values())
        
        return QualityCheckResult(
            file_path=relative_path,
            check_time=datetime.now().isoformat(),
            passed=passed,
            p0_checks=p0_checks,
            p1_checks=p1_checks,
            p2_checks=p2_checks,
            issues=p0_issues,
            warnings=p1_warnings,
            suggestions=p2_suggestions,
        )
    
    def _extract_metadata(self, content: str) -> Dict[str, str]:
        """提取YAML元数据"""
        metadata = {}
        
        if content.startswith('---'):
            metadata_end = content.find('---', 3)
            if metadata_end != -1:
                metadata_text = content[3:metadata_end]
                
                # 解析元数据
                for line in metadata_text.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip().strip('"\'')
        
        return metadata
    
    def _check_p0(
        self,
        file_path: str,
        metadata: Dict[str, str],
        content: str
    ) -> Tuple[Dict[str, bool], List[Dict]]:
        """P0阻断级检查"""
        checks = {}
        issues = []
        
        # 检查元数据完整性
        missing_fields = self.REQUIRED_METADATA - set(metadata.keys())
        checks['metadata_complete'] = len(missing_fields) == 0
        if missing_fields:
            issues.append({
                'level': 'P0',
                'type': 'missing_metadata',
                'message': f'缺少必需字段: {", ".join(missing_fields)}',
                'suggestion': '在文档元数据中添加这些必需字段',
            })
        
        # 检查版本号格式
        version = metadata.get('version', '')
        checks['version_format'] = bool(self.VERSION_PATTERN.match(version))
        if not checks['version_format']:
            issues.append({
                'level': 'P0',
                'type': 'invalid_version_format',
                'message': f'版本号格式不正确: {version}',
                'suggestion': '使用语义化版本格式: X.Y.Z (如 1.0.0)',
            })
        
        # 检查文档ID唯一性
        module_id = metadata.get('module_id', '')
        if module_id:
            if module_id in self.module_ids:
                checks['module_id_unique'] = False
                issues.append({
                    'level': 'P0',
                    'type': 'duplicate_module_id',
                    'message': f'文档ID重复: {module_id} (已存在于 {self.module_ids[module_id]})',
                    'suggestion': '使用唯一的module_id',
                })
            else:
                checks['module_id_unique'] = True
                self.module_ids[module_id] = file_path
        else:
            checks['module_id_unique'] = False
        
        return checks, issues
    
    def _check_p1(
        self,
        file_path: str,
        metadata: Dict[str, str],
        content: str
    ) -> Tuple[Dict[str, bool], List[Dict]]:
        """P1警告级检查"""
        checks = {}
        warnings = []
        
        # 检查推荐元数据字段
        missing_recommended = self.RECOMMENDED_METADATA - set(metadata.keys())
        checks['recommended_metadata'] = len(missing_recommended) <= 2
        if missing_recommended:
            warnings.append({
                'level': 'P1',
                'type': 'missing_recommended_metadata',
                'message': f'缺少推荐字段: {", ".join(missing_recommended)}',
                'suggestion': '建议添加这些字段以提高文档质量',
            })
        
        # 检查内部链接有效性
        broken_links = self._check_internal_links(content, Path(file_path))
        checks['internal_links'] = len(broken_links) == 0
        if broken_links:
            warnings.append({
                'level': 'P1',
                'type': 'broken_internal_links',
                'message': f'发现损坏的内部链接: {len(broken_links)}个',
                'suggestion': '修复或移除损坏的链接',
            })
        
        # 检查文档分类规范性
        path_parts = Path(file_path).parts
        if len(path_parts) >= 2 and path_parts[0] == 'docs':
            category = path_parts[1]
            checks['classification'] = category in self.STANDARD_CATEGORIES or category == 'design'
            if not checks['classification']:
                warnings.append({
                    'level': 'P1',
                    'type': 'non_standard_category',
                    'message': f'文档不在标准分类目录下: {category}',
                    'suggestion': f'建议将文档移至标准分类目录',
                })
        else:
            checks['classification'] = True
        
        return checks, warnings
    
    def _check_p2(self, file_path: str, content: str) -> Tuple[Dict[str, bool], List[Dict]]:
        """P2提示级检查"""
        checks = {}
        suggestions = []
        
        # 检查文档结构完整性
        has_overview = any(keyword in content.lower() for keyword in ['概述', '简介', 'overview', 'introduction'])
        has_principles = any(keyword in content.lower() for keyword in ['原则', '设计原则', 'principle'])
        has_examples = '```' in content or '示例' in content or 'example' in content.lower()
        
        checks['document_structure'] = has_overview or has_principles
        if not checks['document_structure']:
            suggestions.append({
                'level': 'P2',
                'type': 'incomplete_structure',
                'message': '文档结构可能不完整',
                'suggestion': '建议添加概述、设计原则等章节',
            })
        
        checks['code_examples'] = has_examples
        
        return checks, suggestions
    
    def _check_internal_links(self, content: str, file_path: Path) -> List[str]:
        """检查内部链接有效性"""
        broken_links = []
        
        # Markdown链接正则: [text](path)
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        
        for text, link in link_pattern.findall(content):
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
                broken_links.append(link)
        
        return broken_links
    
    def check_files(self, file_paths: List[str]) -> List[QualityCheckResult]:
        """
        检查多个文件
        
        参数:
            file_paths: 文件路径列表
        
        返回:
            List[QualityCheckResult]: 检查结果列表
        """
        results = []
        
        for file_path in file_paths:
            result = self.check_file(file_path)
            results.append(result)
        
        return results
    
    def generate_report(self, results: List[QualityCheckResult]) -> Dict:
        """
        生成质量门禁报告
        
        参数:
            results: 检查结果列表
        
        返回:
            Dict: 报告数据
        """
        total_files = len(results)
        passed_files = sum(1 for r in results if r.passed)
        
        # 统计问题
        total_issues = sum(len(r.issues) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)
        total_suggestions = sum(len(r.suggestions) for r in results)
        
        report = {
            'summary': {
                'check_time': datetime.now().isoformat(),
                'total_files': total_files,
                'passed_files': passed_files,
                'failed_files': total_files - passed_files,
                'pass_rate': round(passed_files / total_files * 100, 2) if total_files > 0 else 0,
                'total_issues': total_issues,
                'total_warnings': total_warnings,
                'total_suggestions': total_suggestions,
            },
            'results': [asdict(r) for r in results],
        }
        
        return report
    
    def save_report(self, report: Dict, output_path: str) -> None:
        """
        保存质量门禁报告
        
        参数:
            report: 报告数据
            output_path: 输出文件路径
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"质量门禁报告已保存到: {output_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='文档质量门禁检查工具')
    parser.add_argument(
        '--project-root',
        default='d:/ZephyrAlpha',
        help='项目根目录路径'
    )
    parser.add_argument(
        '--file',
        help='检查单个文件'
    )
    parser.add_argument(
        '--files',
        nargs='+',
        help='检查多个文件'
    )
    parser.add_argument(
        '--changed',
        action='store_true',
        help='检查所有修改的文件 (需要git)'
    )
    parser.add_argument(
        '--output',
        default='docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/quality_gate_report.json',
        help='输出报告路径'
    )
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建检查器
    gate = DocumentQualityGate(project_root=args.project_root)
    
    # 确定要检查的文件
    file_paths = []
    
    if args.file:
        file_paths = [args.file]
    elif args.files:
        file_paths = args.files
    elif args.changed:
        # 获取git修改的文件
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', '--cached'],
                cwd=args.project_root,
                capture_output=True,
                text=True
            )
            changed_files = result.stdout.strip().split('\n')
            file_paths = [f for f in changed_files if f.endswith('.md')]
        except Exception as e:
            logger.error(f"获取git修改文件失败: {e}")
            return
    else:
        logger.error("请指定要检查的文件 (--file, --files, 或 --changed)")
        return
    
    # 执行检查
    results = gate.check_files(file_paths)
    
    # 生成报告
    report = gate.generate_report(results)
    
    # 保存报告
    gate.save_report(report, args.output)
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("文档质量门禁报告")
    print("=" * 60)
    print(f"检查文件数: {report['summary']['total_files']}")
    print(f"通过文件数: {report['summary']['passed_files']}")
    print(f"失败文件数: {report['summary']['failed_files']}")
    print(f"通过率: {report['summary']['pass_rate']}%")
    print(f"\n问题统计:")
    print(f"  P0问题: {report['summary']['total_issues']}")
    print(f"  P1警告: {report['summary']['total_warnings']}")
    print(f"  P2建议: {report['summary']['total_suggestions']}")
    
    # 显示失败的文件
    failed_files = [r for r in results if not r.passed]
    if failed_files:
        print("\n未通过检查的文件:")
        for result in failed_files:
            print(f"  - {result.file_path}")
            for issue in result.issues:
                print(f"    [{issue['level']}] {issue['message']}")
    
    print("=" * 60)
    
    # 返回退出码
    return 0 if report['summary']['failed_files'] == 0 else 1


if __name__ == '__main__':
    exit(main())
