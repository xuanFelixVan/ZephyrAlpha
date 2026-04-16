#!/usr/bin/env python3
"""
版本元数据迁移工具 v1.0
迁移文件名中的版本信息到元数据头部
"""

import os
import re
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import argparse
from datetime import datetime

class VersionMetadataMigrator:
    """版本元数据迁移器"""

    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.docs_dir = os.path.join(self.project_root, "docs")

        # 版本提取模式
        self.version_patterns = [
            re.compile(r'_v(\d+)\.(\d+)\.(\d+)'),      # _v1.2.3
            re.compile(r'_v(\d+)\.(\d+)'),            # _v1.2
            re.compile(r'[-_](\d+)\.(\d+)\.(\d+)'),   # -1.2.3
            re.compile(r'[-_](\d+)\.(\d+)'),          # -1.2
            re.compile(r'[-_]v?(\d+)(\d{2})(\d{2})'), # _20260401
        ]

        # 模块ID前缀映射
        self.module_prefixes = {
            "00_OVERVIEW": "OVERVIEW",
            "01_FRAMEWORK": "FRAMEWORK",
            "02_FACTOR_LIBRARY": "FACTOR",
            "03_TRADING_TACTICS": "TACTICS",
            "04_EXECUTION": "EXECUTION",
            "05_IMPLEMENTATION": "IMPL",
            "06_ARCHIVE": "ARCHIVE",
            "07_RESEARCH": "RESEARCH",
            "08_USER_EXPERIENCE": "UX",
            "09_AUDIT": "AUDIT",
        }

        # 文档类型映射
        self.doc_type_mapping = {
            "README.md": "README",
            "BLUEPRINT.md": "BLUEPRINT",
            "ARCHITECTURE.md": "ARCH",
            "CHANGELOG.md": "CHANGELOG",
            "API_Contract.md": "API_CONTRACT",
            "System_Manifest.md": "SYSTEM_MANIFEST",
            "VERSIONING.md": "VERSIONING",
            "CONFIG": "CONFIG",
            "REPORT": "REPORT",
            "GUIDE": "GUIDE",
            "STANDARD": "STANDARD",
            "TEMPLATE": "TEMPLATE",
        }

    def extract_version_from_filename(self, filename: str) -> Optional[str]:
        """从文件名中提取版本信息"""
        for pattern in self.version_patterns:
            match = pattern.search(filename)
            if match:
                if len(match.groups()) == 3:  # _v1.2.3
                    return f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
                elif len(match.groups()) == 2:  # _v1.2
                    return f"{match.group(1)}.{match.group(2)}.0"
                elif len(match.groups()) == 3 and len(match.group(1)) == 4:  # _20260401
                    year = match.group(1)
                    month = match.group(2)
                    day = match.group(3)
                    # 日期版本转换为语义版本
                    return f"1.0.0-date{year}{month}{day}"

        return None

    def extract_version_from_content(self, content: str) -> Optional[str]:
        """从内容中提取版本信息"""
        # 查找版本模式
        version_patterns = [
            r'版本[:：]\s*v?(\d+\.\d+(?:\.\d+)?)',
            r'Version[:：]\s*v?(\d+\.\d+(?:\.\d+)?)',
            r'v(\d+\.\d+(?:\.\d+)?)',
            r'version[:：]\s*["\']?(\d+\.\d+(?:\.\d+)?)["\']?',
        ]

        for pattern in version_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                version = match.group(1)
                # 确保是三段式版本号
                parts = version.split('.')
                if len(parts) == 2:
                    return f"{parts[0]}.{parts[1]}.0"
                elif len(parts) == 3:
                    return version

        return None

    def generate_module_id(self, file_path: str) -> str:
        """生成模块ID"""
        rel_path = os.path.relpath(file_path, self.docs_dir)
        path_parts = rel_path.split(os.sep)

        # 确定前缀
        prefix = "DOC"
        for key, value in self.module_prefixes.items():
            if rel_path.startswith(key):
                prefix = value
                break

        # 确定文档类型
        doc_type = "DOC"
        filename = os.path.basename(file_path)

        # 检查文件名映射
        for key, value in self.doc_type_mapping.items():
            if filename == key:
                doc_type = value
                break
        else:
            # 根据文件名特征判断
            if "README" in filename:
                doc_type = "README"
            elif "BLUEPRINT" in filename:
                doc_type = "BLUEPRINT"
            elif "AUDIT" in filename or "REPORT" in filename:
                doc_type = "REPORT"
            elif "STANDARD" in filename or "GUIDE" in filename:
                doc_type = "GUIDE"
            elif "CONFIG" in filename or "CONF" in filename:
                doc_type = "CONFIG"
            elif "API" in filename:
                doc_type = "API"

        # 生成序列号（简化版，实际应根据已有ID生成唯一编号）
        seq_num = "001"

        return f"{prefix}_{doc_type}_{seq_num}"

    def parse_existing_metadata(self, content: str) -> Tuple[Dict, str]:
        """解析现有的元数据头部"""
        lines = content.split('\n')

        if len(lines) > 2 and lines[0] == '---' and '---' in lines[1:]:
            # 提取元数据部分
            metadata_lines = []
            body_lines = []
            in_metadata = False
            metadata_end = False

            for line in lines:
                if line == '---' and not in_metadata:
                    in_metadata = True
                    metadata_lines.append(line)
                elif line == '---' and in_metadata:
                    metadata_lines.append(line)
                    metadata_end = True
                elif in_metadata and not metadata_end:
                    metadata_lines.append(line)
                else:
                    body_lines.append(line)

            # 解析YAML元数据
            metadata_content = '\n'.join(metadata_lines[1:-1])  # 去掉前后的---
            try:
                metadata = yaml.safe_load(metadata_content) or {}
            except yaml.YAMLError:
                metadata = {}

            body = '\n'.join(body_lines)
            return metadata, body
        else:
            # 无元数据头部
            return {}, content

    def generate_metadata(self, file_path: str, filename: str, existing_metadata: Dict, content: str) -> Dict:
        """生成元数据"""
        metadata = existing_metadata.copy()

        # 提取版本信息
        version_from_filename = self.extract_version_from_filename(filename)
        version_from_content = self.extract_version_from_content(content)

        # 确定版本
        if 'version' in metadata and metadata['version']:
            # 已有元数据中的版本优先
            pass
        elif version_from_filename:
            metadata['version'] = version_from_filename
        elif version_from_content:
            metadata['version'] = version_from_content
        else:
            metadata['version'] = '1.0.0'  # 默认版本

        # 确保版本号是语义化版本
        version = metadata['version']
        parts = version.split('.')
        if len(parts) == 2:
            metadata['version'] = f"{parts[0]}.{parts[1]}.0"

        # 设置必选字段
        if 'module_id' not in metadata:
            metadata['module_id'] = self.generate_module_id(file_path)

        if 'status' not in metadata:
            metadata['status'] = 'Active'

        if 'last_updated' not in metadata:
            metadata['last_updated'] = datetime.now().strftime('%Y-%m-%d')

        # 添加推荐字段（如果不存在）
        if 'created_date' not in metadata:
            # 尝试从文件名中提取日期
            date_match = re.search(r'_(\d{4})(\d{2})(\d{2})', filename)
            if date_match:
                metadata['created_date'] = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
            else:
                metadata['created_date'] = datetime.now().strftime('%Y-%m-%d')

        if 'owner' not in metadata:
            metadata['owner'] = '首席文档架构师'

        # 清理None值
        metadata = {k: v for k, v in metadata.items() if v is not None}

        return metadata

    def simplify_filename(self, filename: str) -> str:
        """简化文件名，移除版本信息"""
        simplified = filename

        # 移除版本后缀
        for pattern in self.version_patterns:
            simplified = pattern.sub('', simplified)

        # 移除日期后缀
        simplified = re.sub(r'_(\d{8})(?=\.)', '', simplified)
        simplified = re.sub(r'[-_](\d{4}-\d{2}-\d{2})(?=\.)', '', simplified)

        # 确保扩展名不变
        if not simplified.endswith('.md') and filename.endswith('.md'):
            simplified += '.md'

        # 如果简化后为空或与原始相同，返回原始
        if not simplified or simplified == filename:
            return filename

        return simplified

    def update_references(self, file_path: str, old_filename: str, new_filename: str) -> List[str]:
        """更新相关文件中的引用链接"""
        updated_files = []

        if old_filename == new_filename:
            return updated_files

        # 查找所有Markdown文件
        markdown_files = []
        for root, dirs, files in os.walk(self.docs_dir):
            for file in files:
                if file.endswith('.md'):
                    markdown_files.append(os.path.join(root, file))

        # 更新引用
        old_basename = os.path.basename(old_filename)
        new_basename = os.path.basename(new_filename)

        for md_file in markdown_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 查找并替换引用
                old_ref_pattern = re.escape(old_basename)
                new_content = re.sub(old_ref_pattern, new_basename, content)

                if new_content != content:
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    updated_files.append(os.path.relpath(md_file, self.project_root))

            except Exception as e:
                print(f"更新引用时出错 {md_file}: {e}")

        return updated_files

    def migrate_file(self, file_path: str, dry_run: bool = False, update_references: bool = True) -> Dict:
        """迁移单个文件"""
        result = {
            'file': os.path.relpath(file_path, self.project_root),
            'old_filename': os.path.basename(file_path),
            'new_filename': None,
            'metadata_added': False,
            'filename_simplified': False,
            'references_updated': [],
            'errors': []
        }

        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析现有元数据
            existing_metadata, body = self.parse_existing_metadata(content)

            # 生成新的元数据
            metadata = self.generate_metadata(file_path, result['old_filename'], existing_metadata, content)

            # 简化文件名
            new_filename = self.simplify_filename(result['old_filename'])
            result['new_filename'] = new_filename

            # 构建新的内容
            metadata_yaml = yaml.dump(metadata, allow_unicode=True, default_flow_style=False)
            new_content = f"---\n{metadata_yaml}---\n\n{body}"

            # 检查是否有变化
            metadata_changed = new_content != content
            filename_changed = new_filename != result['old_filename']

            if metadata_changed or filename_changed:
                result['metadata_added'] = metadata_changed
                result['filename_simplified'] = filename_changed

                if not dry_run:
                    # 写入新内容
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

                    # 如果需要重命名文件
                    if filename_changed:
                        dir_path = os.path.dirname(file_path)
                        new_file_path = os.path.join(dir_path, new_filename)

                        # 备份旧文件
                        backup_path = file_path + '.bak'
                        os.rename(file_path, backup_path)

                        # 重命名文件
                        os.rename(backup_path, new_file_path)

                        # 更新引用
                        if update_references:
                            updated_files = self.update_references(new_file_path, result['old_filename'], new_filename)
                            result['references_updated'] = updated_files

                        result['file'] = os.path.relpath(new_file_path, self.project_root)
                    else:
                        # 只更新内容，不重命名
                        if update_references:
                            updated_files = self.update_references(file_path, result['old_filename'], new_filename)
                            result['references_updated'] = updated_files

            return result

        except Exception as e:
            result['errors'].append(str(e))
            return result

    def validate_migration(self, file_path: str) -> Dict:
        """验证迁移结果"""
        result = {
            'file': os.path.relpath(file_path, self.project_root),
            'has_metadata': False,
            'metadata_valid': False,
            'version_valid': False,
            'filename_simplified': False,
            'issues': []
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查是否有元数据头部
            if content.startswith('---\n'):
                result['has_metadata'] = True

                # 解析元数据
                metadata, _ = self.parse_existing_metadata(content)

                if metadata:
                    result['metadata_valid'] = True

                    # 检查必选字段
                    required_fields = ['module_id', 'version', 'status', 'last_updated']
                    missing_fields = [field for field in required_fields if field not in metadata]

                    if missing_fields:
                        result['issues'].append(f"缺少必选字段: {', '.join(missing_fields)}")
                    else:
                        # 检查版本格式
                        version = metadata['version']
                        version_pattern = re.compile(r'^\d+\.\d+\.\d+')
                        if version_pattern.match(version):
                            result['version_valid'] = True
                        else:
                            result['issues'].append(f"版本格式无效: {version}")

            # 检查文件名是否简化
            filename = os.path.basename(file_path)
            simplified = self.simplify_filename(filename)
            if simplified == filename:
                # 检查是否还有版本信息
                if self.extract_version_from_filename(filename):
                    result['issues'].append("文件名中仍包含版本信息")
                else:
                    result['filename_simplified'] = True
            else:
                result['issues'].append(f"文件名可进一步简化: {filename} -> {simplified}")

            return result

        except Exception as e:
            result['issues'].append(f"验证时出错: {str(e)}")
            return result

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='迁移文件名中的版本信息到元数据头部')
    parser.add_argument('target', help='目标文件或目录')
    parser.add_argument('--recursive', '-r', action='store_true', help='递归处理目录')
    parser.add_argument('--dry-run', '-d', action='store_true', help='试运行，不实际修改文件')
    parser.add_argument('--validate-only', '-v', action='store_true', help='仅验证，不迁移')
    parser.add_argument('--update-references', '-u', action='store_true', default=True,
                       help='更新引用链接（默认开启）')
    parser.add_argument('--no-update-references', action='store_false', dest='update_references',
                       help='不更新引用链接')

    args = parser.parse_args()

    migrator = VersionMetadataMigrator()

    # 确定目标路径
    target_path = args.target
    if not os.path.isabs(target_path):
        target_path = os.path.join(migrator.project_root, target_path)

    if not os.path.exists(target_path):
        print(f"错误: 路径不存在: {target_path}")
        sys.exit(1)

    # 收集要处理的文件
    files_to_process = []

    if os.path.isfile(target_path):
        files_to_process.append(target_path)
    elif os.path.isdir(target_path):
        for root, dirs, files in os.walk(target_path):
            for file in files:
                if file.endswith('.md'):
                    files_to_process.append(os.path.join(root, file))

            if not args.recursive:
                break  # 只处理一级目录

    print(f"找到 {len(files_to_process)} 个Markdown文件需要处理")

    if args.validate_only:
        # 验证模式
        validation_results = []
        for file_path in files_to_process:
            result = migrator.validate_migration(file_path)
            validation_results.append(result)

        # 打印验证结果
        print("\n验证结果:")
        print("=" * 80)

        valid_count = 0
        issues_count = 0

        for result in validation_results:
            if not result['issues']:
                valid_count += 1
                print(f"✅ {result['file']}")
            else:
                issues_count += 1
                print(f"❌ {result['file']}")
                for issue in result['issues']:
                    print(f"   - {issue}")

        print(f"\n总计: {len(files_to_process)} 个文件")
        print(f"通过: {valid_count} 个文件")
        print(f"问题: {issues_count} 个文件")

        sys.exit(0 if issues_count == 0 else 1)

    else:
        # 迁移模式
        migration_results = []

        for file_path in files_to_process:
            print(f"处理: {os.path.relpath(file_path, migrator.project_root)}")
            result = migrator.migrate_file(
                file_path,
                dry_run=args.dry_run,
                update_references=args.update_references
            )
            migration_results.append(result)

            if result['errors']:
                print(f"  错误: {', '.join(result['errors'])}")
            else:
                if result['metadata_added']:
                    print(f"  ✓ 添加/更新元数据")
                if result['filename_simplified']:
                    print(f"  ✓ 简化文件名: {result['old_filename']} -> {result['new_filename']}")
                if result['references_updated']:
                    print(f"  ✓ 更新 {len(result['references_updated'])} 个引用")

        # 打印摘要
        print("\n迁移摘要:")
        print("=" * 80)

        metadata_added = sum(1 for r in migration_results if r['metadata_added'])
        filename_simplified = sum(1 for r in migration_results if r['filename_simplified'])
        references_updated = sum(len(r['references_updated']) for r in migration_results)
        errors = sum(1 for r in migration_results if r['errors'])

        print(f"处理文件数: {len(migration_results)}")
        print(f"添加/更新元数据: {metadata_added}")
        print(f"简化文件名: {filename_simplified}")
        print(f"更新引用链接: {references_updated}")
        print(f"错误: {errors}")

        if args.dry_run:
            print("\n⚠️  试运行模式，未实际修改文件")
            print("使用 --dry-run false 进行实际迁移")

        sys.exit(0 if errors == 0 else 1)

if __name__ == "__main__":
    main()
