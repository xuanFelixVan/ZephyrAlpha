#!/usr/bin/env python3
"""
版本元数据验证工具 v1.0
验证文档元数据是否符合专业量化机构标准
"""

import os
import re
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import argparse
from datetime import datetime

class VersionMetadataValidator:
    """版本元数据验证器"""

    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.docs_dir = os.path.join(self.project_root, "docs")

        # 版本号验证模式
        self.semver_pattern = re.compile(r'^\d+\.\d+\.\d+')
        self.prerelease_pattern = re.compile(r'^\d+\.\d+\.\d+-(alpha|beta|rc)\.\d+')

        # 必选字段
        self.required_fields = ['module_id', 'version', 'status', 'last_updated']

        # 推荐字段
        self.recommended_fields = [
            'created_date', 'owner', 'standard_type',
            'applicable_scope', 'compliance_level'
        ]

        # 状态枚举
        self.valid_statuses = ['Planning', 'Draft', 'Review', 'Active', 'Deprecated', 'Archived']

        # 日期格式
        self.date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')

    def parse_metadata(self, content: str) -> Tuple[Dict, str, bool]:
        """解析元数据头部"""
        lines = content.split('\n')

        # 查找第一个 ---
        if len(lines) < 2 or lines[0] != '---':
            return {}, content, False

        # 查找第二个 ---
        second_dash_index = -1
        for i in range(1, len(lines)):
            if lines[i] == '---':
                second_dash_index = i
                break

        if second_dash_index == -1:
            return {}, content, False

        # 提取元数据内容（第一个和第二个 --- 之间的行）
        metadata_lines = lines[1:second_dash_index]
        body_lines = lines[second_dash_index + 1:]

        # 解析YAML元数据
        metadata_content = '\n'.join(metadata_lines)
        try:
            metadata = yaml.safe_load(metadata_content) or {}
            return metadata, '\n'.join(body_lines), True
        except yaml.YAMLError as e:
            return {'_parse_error': str(e)}, '\n'.join(body_lines), True

    def validate_metadata(self, metadata: Dict) -> List[str]:
        """验证元数据"""
        issues = []

        # 检查必选字段
        missing_fields = [field for field in self.required_fields if field not in metadata]
        if missing_fields:
            issues.append(f"缺少必选字段: {', '.join(missing_fields)}")

        # 检查字段值
        if 'module_id' in metadata:
            module_id = metadata['module_id']
            if not isinstance(module_id, str) or not module_id:
                issues.append(f"module_id无效: {module_id}")
            elif not re.match(r'^[A-Z_]+_[A-Z_]+_\d{3}$', module_id):
                issues.append(f"module_id格式错误，应为: PREFIX_TYPE_NNN")

        if 'version' in metadata:
            version = str(metadata['version'])
            if not (self.semver_pattern.match(version) or self.prerelease_pattern.match(version)):
                issues.append(f"版本号格式无效，应为语义化版本: {version}")

        if 'status' in metadata:
            status = metadata['status']
            if status not in self.valid_statuses:
                issues.append(f"状态值无效，应为: {', '.join(self.valid_statuses)}")

        if 'last_updated' in metadata:
            date_str = metadata['last_updated']
            if not self.date_pattern.match(str(date_str)):
                issues.append(f"last_updated日期格式无效，应为YYYY-MM-DD: {date_str}")
            else:
                # 验证日期是否合理
                try:
                    date_obj = datetime.strptime(str(date_str), '%Y-%m-%d')
                    if date_obj > datetime.now():
                        issues.append(f"last_updated日期不能是未来日期: {date_str}")
                except ValueError:
                    issues.append(f"last_updated日期无效: {date_str}")

        # 检查推荐字段
        missing_recommended = [field for field in self.recommended_fields
                              if field not in metadata]
        if missing_recommended:
            issues.append(f"缺少推荐字段: {', '.join(missing_recommended)}")

        # 检查created_date格式
        if 'created_date' in metadata:
            date_str = metadata['created_date']
            if not self.date_pattern.match(str(date_str)):
                issues.append(f"created_date日期格式无效，应为YYYY-MM-DD: {date_str}")

        # 检查版本与状态的兼容性
        if 'version' in metadata and 'status' in metadata:
            version = str(metadata['version'])
            status = metadata['status']

            # 预发布版本应为Planning/Draft/Review状态
            if self.prerelease_pattern.match(version) and status not in ['Planning', 'Draft', 'Review']:
                issues.append(f"预发布版本{version}的状态应为Planning/Draft/Review，当前为{status}")

            # 正式版本应为Active/Deprecated/Archived状态
            if self.semver_pattern.match(version) and status in ['Planning', 'Draft', 'Review']:
                issues.append(f"正式版本{version}的状态应为Active/Deprecated/Archived，当前为{status}")

        return issues

    def validate_filename(self, filename: str) -> List[str]:
        """验证文件名"""
        issues = []

        # 检查是否包含版本信息
        version_patterns = [
            re.compile(r'_v\d+\.\d+(?:\.\d+)?'),
            re.compile(r'[-_]v?\d+\.\d+(?:\.\d+)?'),
            re.compile(r'[-_]\d{8}'),
            re.compile(r'[-_]\d{4}-\d{2}-\d{2}'),
        ]

        for pattern in version_patterns:
            if pattern.search(filename):
                issues.append(f"文件名中包含版本信息: {filename}")
                break

        # 检查命名规范
        if not filename.endswith('.md'):
            issues.append(f"文件名应以.md结尾: {filename}")

        # 检查特殊字符
        if re.search(r'[<>:"|?*]', filename):
            issues.append(f"文件名包含非法字符: {filename}")

        # 检查空格
        if ' ' in filename:
            issues.append(f"文件名包含空格，建议使用下划线: {filename}")

        # 检查中文
        if re.search(r'[\u4e00-\u9fff]', filename):
            issues.append(f"文件名包含中文字符，应使用英文命名: {filename}")

        return issues

    def validate_content_consistency(self, metadata: Dict, content: str, filename: str) -> List[str]:
        """验证内容一致性"""
        issues = []

        if 'version' not in metadata:
            return issues  # 没有元数据版本，跳过一致性检查

        metadata_version = str(metadata['version'])

        # 改进的版本识别逻辑 - 区分文档自身版本与其他文档版本引用

        # 1. 首先查找明确的文档自身版本引用
        # 这些模式通常表示文档自身的版本
        self_version_patterns = [
            # 中文模式 - 带有明确上下文表明是本文档版本
            r'(?:本文档|当前|最新)[版本]*[:：]\s*v?(\d+\.\d+(?:\.\d+)?)',
            r'文档[版本]*[:：]\s*v?(\d+\.\d+(?:\.\d+)?)\s+(?:版本|版)',
            r'^#+\s*(?:.*版本.*\s+v?(\d+\.\d+(?:\.\d+)?))',  # 标题中的版本
            r'版本号[:：]\s*v?(\d+\.\d+(?:\.\d+)?)',
            r'Version\s*[:：]\s*v?(\d+\.\d+(?:\.\d+)?)\s+(?:of\s+(?:this\s+)?document|here|current)',

            # 带有特定上下文的关键词
            r'(?:更新于|发布于|创建于)\s*(?:v?(\d+\.\d+(?:\.\d+)?)|.*版本\s*v?(\d+\.\d+(?:\.\d+)?))',
            r'(?:最后更新|最近更新).*v?(\d+\.\d+(?:\.\d+)?)',
        ]

        # 2. 查找通用版本引用（需要上下文分析）
        generic_version_patterns = [
            r'版本[:：]\s*v?(\d+\.\d+(?:\.\d+)?)',
            r'Version[:：]\s*v?(\d+\.\d+(?:\.\d+)?)',
            r'v(\d+\.\d+(?:\.\d+)?)',
        ]

        # 3. 查找对其他文档的版本引用（应忽略）
        # 这些模式通常引用其他文档或外部资源
        other_doc_patterns = [
            r'(?:参考|引用|依据|基于).*v?(\d+\.\d+(?:\.\d+)?)',  # 引用其他文档
            r'(?:参见|查看).*v?(\d+\.\d+(?:\.\d+)?)',  # 参见其他文档
            r'API.*v?(\d+\.\d+(?:\.\d+)?)',  # API版本引用
            r'v?(\d+\.\d+(?:\.\d+)?)\s+(?:及|和|与)\s+',  # 与其他版本并列
            r'从.*v?(\d+\.\d+(?:\.\d+)?)\s+升级',  # 升级说明
        ]

        # 收集所有版本引用
        all_version_matches = []

        # 查找自身版本引用
        self_version_matches = []
        for pattern in self_version_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # 提取版本号（可能有多个捕获组）
                for group in match.groups():
                    if group:
                        context = content[max(0, match.start()-50):min(len(content), match.end()+50)]
                        self_version_matches.append({
                            'version': group,
                            'context': context,
                            'type': 'self'
                        })
                        break

        # 查找通用版本引用
        generic_version_matches = []
        for pattern in generic_version_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if match.groups():
                    version = match.group(1) if match.group(1) else match.group()
                    if version:
                        context = content[max(0, match.start()-100):min(len(content), match.end()+50)]
                        generic_version_matches.append({
                            'version': version,
                            'context': context,
                            'type': 'generic'
                        })

        # 查找其他文档版本引用
        other_doc_matches = []
        for pattern in other_doc_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if match.groups():
                    version = match.group(1) if match.group(1) else match.group()
                    if version:
                        context = content[max(0, match.start()-100):min(len(content), match.end()+50)]
                        other_doc_matches.append({
                            'version': version,
                            'context': context,
                            'type': 'other'
                        })

        # 分析自身版本引用
        for match in self_version_matches:
            content_version = match['version']
            # 比较主版本和次版本（忽略补丁版本）
            metadata_base = metadata_version.split('.')[0:2]
            content_base = content_version.split('.')[0:2]

            if len(content_base) >= 2 and content_base != metadata_base:
                # 这是文档自身的版本，应该与元数据一致
                issues.append(f"文档内容中明确声明的版本({content_version})与元数据版本({metadata_version})不一致")

        # 分析通用版本引用（需要进一步上下文判断）
        for match in generic_version_matches:
            content_version = match['version']
            context = match['context'].lower()

            # 检查上下文是否表明这是文档自身版本
            is_self_reference = False
            self_keywords = ['本文档', '当前文档', '此文档', '本文件', '这个文档', 'this document', 'current document']
            for keyword in self_keywords:
                if keyword in context:
                    is_self_reference = True
                    break

            # 检查是否在标题中
            if re.search(r'^#+\s+.*' + re.escape(content_version), match['context'], re.MULTILINE):
                is_self_reference = True

            if is_self_reference:
                metadata_base = metadata_version.split('.')[0:2]
                content_base = content_version.split('.')[0:2]

                if len(content_base) >= 2 and content_base != metadata_base:
                    issues.append(f"内容中可能为文档自身版本的引用({content_version})与元数据版本({metadata_version})不一致")

        # 其他文档的版本引用不检查一致性（忽略）

        # 检查文件名与内容的关联性
        if 'title' in metadata and metadata['title']:
            title = metadata['title']
            # 简单检查文件名是否包含标题关键词
            filename_lower = filename.lower()
            title_lower = str(title).lower()

            # 提取标题中的关键词
            title_keywords = re.findall(r'\b\w+\b', title_lower)
            relevant_keywords = [kw for kw in title_keywords if len(kw) > 3]

            if relevant_keywords:
                matches = sum(1 for kw in relevant_keywords if kw in filename_lower)
                if matches == 0:
                    issues.append(f"文件名与标题关联性弱，标题: {title}")

        return issues

    def validate_file(self, file_path: str) -> Dict:
        """验证单个文件"""
        result = {
            'file': os.path.relpath(file_path, self.project_root),
            'has_metadata': False,
            'metadata_valid': False,
            'filename_valid': False,
            'consistency_valid': False,
            'issues': [],
            'metadata': {},
            'score': 0,
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            filename = os.path.basename(file_path)

            # 解析元数据
            metadata, body, metadata_parsed = self.parse_metadata(content)
            result['has_metadata'] = metadata_parsed
            result['metadata'] = metadata

            # 验证元数据
            if metadata_parsed:
                # 检查是否有解析错误
                if '_parse_error' in metadata:
                    parse_error = metadata['_parse_error']
                    result['issues'].append(f"元数据解析错误: {parse_error}")
                    result['metadata_valid'] = False
                else:
                    metadata_issues = self.validate_metadata(metadata)
                    result['issues'].extend(metadata_issues)
                    result['metadata_valid'] = len(metadata_issues) == 0
            else:
                result['issues'].append("缺少元数据头部")

            # 验证文件名
            filename_issues = self.validate_filename(filename)
            result['issues'].extend(filename_issues)
            result['filename_valid'] = len(filename_issues) == 0

            # 验证内容一致性
            if metadata_parsed:
                consistency_issues = self.validate_content_consistency(metadata, content, filename)
                result['issues'].extend(consistency_issues)
                result['consistency_valid'] = len(consistency_issues) == 0

            # 计算分数
            max_score = 100
            score = max_score

            # 扣分规则
            if not result['has_metadata']:
                score -= 30
            if not result['metadata_valid']:
                score -= 30
            if not result['filename_valid']:
                score -= 20
            if not result['consistency_valid']:
                score -= 20

            # 额外问题扣分
            score -= min(20, len(result['issues']) * 5)

            result['score'] = max(0, score)

            return result

        except Exception as e:
            result['issues'].append(f"验证时出错: {str(e)}")
            return result

    def validate_directory(self, directory_path: str, recursive: bool = True) -> List[Dict]:
        """验证目录下的所有文件"""
        results = []

        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    result = self.validate_file(file_path)
                    results.append(result)

            if not recursive:
                break

        return results

    def generate_report(self, results: List[Dict], output_format: str = 'text') -> str:
        """生成验证报告"""
        if output_format == 'json':
            return json.dumps(results, ensure_ascii=False, indent=2)

        # 文本格式报告
        report_lines = []

        # 统计信息
        total_files = len(results)
        files_with_metadata = sum(1 for r in results if r['has_metadata'])
        files_valid_metadata = sum(1 for r in results if r['metadata_valid'])
        files_valid_filename = sum(1 for r in results if r['filename_valid'])
        files_valid_consistency = sum(1 for r in results if r['consistency_valid'])

        # 计算平均分
        avg_score = sum(r['score'] for r in results) / total_files if total_files > 0 else 0

        # 分类统计
        score_distribution = {
            '优秀 (90-100)': 0,
            '良好 (70-89)': 0,
            '一般 (50-69)': 0,
            '较差 (0-49)': 0,
        }

        for result in results:
            score = result['score']
            if score >= 90:
                score_distribution['优秀 (90-100)'] += 1
            elif score >= 70:
                score_distribution['良好 (70-89)'] += 1
            elif score >= 50:
                score_distribution['一般 (50-69)'] += 1
            else:
                score_distribution['较差 (0-49)'] += 1

        # 生成报告头部
        report_lines.append("=" * 80)
        report_lines.append("版本元数据验证报告")
        report_lines.append("=" * 80)
        report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"验证文件数: {total_files}")
        report_lines.append("")

        # 统计信息
        report_lines.append("📊 统计概览")
        report_lines.append("-" * 40)
        report_lines.append(f"有元数据文件: {files_with_metadata}/{total_files} ({files_with_metadata/total_files*100:.1f}%)")
        report_lines.append(f"元数据有效: {files_valid_metadata}/{files_with_metadata} ({files_valid_metadata/max(1, files_with_metadata)*100:.1f}%)")
        report_lines.append(f"文件名有效: {files_valid_filename}/{total_files} ({files_valid_filename/total_files*100:.1f}%)")
        report_lines.append(f"内容一致: {files_valid_consistency}/{files_with_metadata} ({files_valid_consistency/max(1, files_with_metadata)*100:.1f}%)")
        report_lines.append(f"平均分数: {avg_score:.1f}/100")
        report_lines.append("")

        # 分数分布
        report_lines.append("📈 分数分布")
        report_lines.append("-" * 40)
        for category, count in score_distribution.items():
            percentage = count / total_files * 100 if total_files > 0 else 0
            bar = '█' * int(percentage / 5)
            report_lines.append(f"{category:15} {count:3} 文件 {percentage:5.1f}% {bar}")
        report_lines.append("")

        # 问题分类
        issue_categories = {}
        for result in results:
            for issue in result['issues']:
                # 分类问题
                category = "其他"
                if "缺少必选字段" in issue or "缺少推荐字段" in issue:
                    category = "字段缺失"
                elif "版本号格式无效" in issue or "状态值无效" in issue:
                    category = "格式错误"
                elif "日期格式无效" in issue:
                    category = "日期格式"
                elif "文件名中包含版本信息" in issue:
                    category = "文件名版本"
                elif "文件名包含" in issue:
                    category = "文件名规范"
                elif "不一致" in issue:
                    category = "一致性"
                elif "缺少元数据头部" in issue:
                    category = "无元数据"

                issue_categories[category] = issue_categories.get(category, 0) + 1

        if issue_categories:
            report_lines.append("⚠️ 问题分类")
            report_lines.append("-" * 40)
            for category, count in sorted(issue_categories.items(), key=lambda x: x[1], reverse=True):
                report_lines.append(f"{category:15} {count:3} 个问题")
            report_lines.append("")

        # 详细问题列表
        problematic_files = [r for r in results if r['issues']]
        if problematic_files:
            report_lines.append("🔴 问题文件详情")
            report_lines.append("-" * 40)

            for result in problematic_files[:20]:  # 只显示前20个问题文件
                report_lines.append(f"\n📄 {result['file']} (分数: {result['score']}/100)")
                for issue in result['issues']:
                    report_lines.append(f"  • {issue}")

            if len(problematic_files) > 20:
                report_lines.append(f"\n... 还有 {len(problematic_files) - 20} 个问题文件未显示")
            report_lines.append("")

        # 优秀文件示例
        excellent_files = [r for r in results if r['score'] >= 90]
        if excellent_files:
            report_lines.append("🟢 优秀文件示例")
            report_lines.append("-" * 40)
            for result in excellent_files[:5]:  # 只显示前5个优秀文件
                report_lines.append(f"✅ {result['file']} (分数: {result['score']}/100)")
                if result['metadata']:
                    metadata_preview = {k: v for k, v in result['metadata'].items() if k in ['module_id', 'version', 'status']}
                    report_lines.append(f"   元数据: {metadata_preview}")
            report_lines.append("")

        # 改进建议
        report_lines.append("💡 改进建议")
        report_lines.append("-" * 40)

        if files_with_metadata < total_files * 0.9:
            report_lines.append("1. 为缺少元数据的文件添加元数据头部")

        if files_valid_metadata < files_with_metadata * 0.8:
            report_lines.append("2. 修复元数据中的格式错误和字段缺失")

        if files_valid_filename < total_files * 0.8:
            report_lines.append("3. 简化文件名，移除版本信息")

        if avg_score < 70:
            report_lines.append("4. 使用迁移工具批量修复问题")

        report_lines.append("5. 将验证工具集成到CI/CD流程中，确保持续合规")
        report_lines.append("")

        report_lines.append("=" * 80)
        report_lines.append("验证完成")
        report_lines.append("=" * 80)

        return '\n'.join(report_lines)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='验证文档元数据是否符合专业量化机构标准')
    parser.add_argument('target', help='目标文件或目录')
    parser.add_argument('--recursive', '-r', action='store_true', help='递归处理目录')
    parser.add_argument('--format', '-f', choices=['text', 'json'], default='text',
                       help='输出格式，text或json')
    parser.add_argument('--output', '-o', help='输出文件路径，默认输出到控制台')
    parser.add_argument('--threshold', '-t', type=float, default=70.0,
                       help='合格分数线，默认70分')

    args = parser.parse_args()

    validator = VersionMetadataValidator()

    # 确定目标路径
    target_path = args.target
    if not os.path.isabs(target_path):
        target_path = os.path.join(validator.project_root, target_path)

    if not os.path.exists(target_path):
        print(f"错误: 路径不存在: {target_path}")
        sys.exit(1)

    # 收集要验证的文件
    files_to_validate = []

    if os.path.isfile(target_path):
        files_to_validate.append(target_path)
    elif os.path.isdir(target_path):
        for root, dirs, files in os.walk(target_path):
            for file in files:
                if file.endswith('.md'):
                    files_to_validate.append(os.path.join(root, file))

            if not args.recursive:
                break

    print(f"找到 {len(files_to_validate)} 个Markdown文件需要验证")

    # 验证文件
    results = []
    for i, file_path in enumerate(files_to_validate):
        print(f"验证: {os.path.relpath(file_path, validator.project_root)}", end='')
        result = validator.validate_file(file_path)
        results.append(result)

        if result['issues']:
            print(f" ❌ ({len(result['issues'])}个问题)")
        else:
            print(f" ✅ ({result['score']}分)")

    # 生成报告
    report = validator.generate_report(results, args.format)

    # 输出报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n报告已保存到: {args.output}")
    else:
        print("\n" + report)

    # 检查是否通过
    avg_score = sum(r['score'] for r in results) / len(results) if results else 0
    passing_files = sum(1 for r in results if r['score'] >= args.threshold)
    passing_rate = passing_files / len(results) if results else 0

    print(f"\n验证总结:")
    print(f"  平均分数: {avg_score:.1f}/100")
    print(f"  合格文件: {passing_files}/{len(results)} ({passing_rate*100:.1f}%)")
    print(f"  合格标准: ≥{args.threshold}分")

    if avg_score >= args.threshold and passing_rate >= 0.8:
        print("✅ 验证通过")
        sys.exit(0)
    else:
        print("❌ 验证未通过")
        sys.exit(1)

if __name__ == "__main__":
    main()
