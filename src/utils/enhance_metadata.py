#!/usr/bin/env python3
"""
元数据增强工具 v1.0
为文档添加缺失的推荐元数据字段
"""

import os
import re
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
from datetime import datetime

class MetadataEnhancer:
    """元数据增强器"""
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.docs_dir = os.path.join(self.project_root, "docs")
        
        # 推荐字段的默认值映射
        self.recommended_fields_defaults = {
            'owner': '首席文档架构师',
            'standard_type': '专业量化机构文档',
            'applicable_scope': '全系统',
            'compliance_level': '专业标准'
        }
        
        # 根据路径的模式映射
        self.path_patterns = {
            # 蓝图文档
            r'.*BLUEPRINT.*\.md$': {
                'standard_type': '专业量化机构蓝图',
                'applicable_scope': '全系统架构设计',
                'compliance_level': '架构标准'
            },
            # 审计文档
            r'.*AUDIT.*\.md$': {
                'standard_type': '专业量化机构审计标准',
                'applicable_scope': '全系统质量监控',
                'compliance_level': '审计标准'
            },
            # 因子库文档
            r'.*FACTOR.*\.md$': {
                'standard_type': '专业量化机构因子标准',
                'applicable_scope': '因子研究与管理',
                'compliance_level': '研究标准'
            },
            # 实施文档
            r'.*IMPLEMENTATION.*\.md$': {
                'standard_type': '专业量化机构实施标准',
                'applicable_scope': '系统实施与部署',
                'compliance_level': '实施标准'
            },
            # 执行文档
            r'.*EXECUTION.*\.md$': {
                'standard_type': '专业量化机构交易执行标准',
                'applicable_scope': '交易执行与监控',
                'compliance_level': '执行标准'
            },
            # 研究文档
            r'.*RESEARCH.*\.md$': {
                'standard_type': '专业量化机构研究标准',
                'applicable_scope': '量化研究实验',
                'compliance_level': '研究标准'
            },
            # 模板文档
            r'.*TEMPLATE.*\.md$': {
                'standard_type': '专业量化机构模板标准',
                'applicable_scope': '文档模板与规范',
                'compliance_level': '模板标准'
            },
            # 标准文档
            r'.*STANDARD.*\.md$': {
                'standard_type': '专业量化机构标准',
                'applicable_scope': '全系统标准规范',
                'compliance_level': '标准规范'
            }
        }
    
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
        except yaml.YAMLError:
            # 解析错误，返回原始内容
            return {}, content, False
    
    def determine_field_values(self, file_path: str, metadata: Dict) -> Dict:
        """确定字段值"""
        # 使用推荐字段默认值作为基础
        field_values = self.recommended_fields_defaults.copy()
        relative_path = os.path.relpath(file_path, self.project_root)
        
        # 根据文件路径确定字段值，覆盖默认值
        for pattern, defaults in self.path_patterns.items():
            if re.match(pattern, relative_path, re.IGNORECASE):
                field_values.update(defaults)
                break
        
        # 根据现有元数据调整
        if 'version' in metadata:
            version = str(metadata['version'])
            if version.startswith('1.'):
                field_values['compliance_level'] = '初始标准'
            elif 'alpha' in version or 'beta' in version or 'rc' in version:
                field_values['compliance_level'] = '预发布标准'
        
        return field_values
    
    def enhance_metadata(self, metadata: Dict, field_values: Dict) -> Dict:
        """增强元数据"""
        enhanced = metadata.copy()
        
        # 添加缺失的推荐字段
        for field, default_value in field_values.items():
            if field not in enhanced:
                enhanced[field] = default_value
        
        # 确保created_date存在
        if 'created_date' not in enhanced and 'last_updated' in enhanced:
            enhanced['created_date'] = enhanced['last_updated']
        
        # 如果还没有创建日期，使用今天
        if 'created_date' not in enhanced:
            enhanced['created_date'] = datetime.now().strftime('%Y-%m-%d')
        
        # 更新最后更新日期
        enhanced['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        
        return enhanced
    
    def format_metadata(self, metadata: Dict) -> str:
        """格式化元数据为YAML字符串"""
        # 确保字段顺序
        ordered_fields = [
            'module_id', 'version', 'status', 'created_date', 'last_updated',
            'owner', 'standard_type', 'applicable_scope', 'compliance_level'
        ]
        
        lines = ['---']
        for field in ordered_fields:
            if field in metadata:
                value = metadata[field]
                if isinstance(value, str) and ':' in value:
                    # 字符串包含冒号，需要引号
                    lines.append(f'{field}: "{value}"')
                else:
                    lines.append(f'{field}: {value}')
        
        lines.append('---')
        return '\n'.join(lines)
    
    def enhance_file(self, file_path: str, dry_run: bool = False) -> Dict:
        """增强单个文件的元数据"""
        result = {
            'file': os.path.relpath(file_path, self.project_root),
            'has_metadata': False,
            'enhanced': False,
            'fields_added': [],
            'errors': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析元数据
            metadata, body, metadata_parsed = self.parse_metadata(content)
            result['has_metadata'] = metadata_parsed
            
            if not metadata_parsed:
                result['errors'].append("无元数据头部，跳过")
                return result
            
            # 确定要添加的字段值
            field_values = self.determine_field_values(file_path, metadata)
            
            # 检查哪些字段缺失
            missing_fields = [field for field in field_values.keys() 
                             if field not in metadata]
            
            if not missing_fields:
                result['enhanced'] = False
                result['fields_added'] = []
                return result
            
            # 增强元数据
            enhanced_metadata = self.enhance_metadata(metadata, field_values)
            
            # 生成新的内容
            new_metadata = self.format_metadata(enhanced_metadata)
            new_content = f"{new_metadata}\n{body}"
            
            # 保存文件
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            
            result['enhanced'] = True
            result['fields_added'] = missing_fields
            result['new_metadata'] = enhanced_metadata
            
            return result
        
        except Exception as e:
            result['errors'].append(str(e))
            return result
    
    def enhance_directory(self, directory_path: str, recursive: bool = True, 
                         dry_run: bool = False) -> List[Dict]:
        """增强目录下的所有文件"""
        results = []
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    result = self.enhance_file(file_path, dry_run)
                    results.append(result)
            
            if not recursive:
                break
        
        return results
    
    def generate_report(self, results: List[Dict]) -> str:
        """生成增强报告"""
        total_files = len(results)
        files_with_metadata = sum(1 for r in results if r['has_metadata'])
        files_enhanced = sum(1 for r in results if r['enhanced'])
        total_fields_added = sum(len(r['fields_added']) for r in results)
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("元数据增强报告")
        report_lines.append("=" * 80)
        report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"处理文件数: {total_files}")
        report_lines.append(f"有元数据文件: {files_with_metadata}/{total_files} ({files_with_metadata/total_files*100:.1f}%)")
        report_lines.append(f"增强文件数: {files_enhanced}/{files_with_metadata} ({files_enhanced/max(1, files_with_metadata)*100:.1f}%)")
        report_lines.append(f"添加字段总数: {total_fields_added}")
        report_lines.append("")
        
        # 字段添加统计
        field_stats = {}
        for result in results:
            for field in result['fields_added']:
                field_stats[field] = field_stats.get(field, 0) + 1
        
        if field_stats:
            report_lines.append("📊 字段添加统计")
            report_lines.append("-" * 40)
            for field, count in sorted(field_stats.items(), key=lambda x: x[1], reverse=True):
                report_lines.append(f"{field:20} {count:3} 次")
            report_lines.append("")
        
        # 增强的文件列表
        enhanced_files = [r for r in results if r['enhanced']]
        if enhanced_files:
            report_lines.append("🟢 增强文件列表")
            report_lines.append("-" * 40)
            for result in enhanced_files[:20]:  # 只显示前20个
                fields_str = ', '.join(result['fields_added'])
                report_lines.append(f"✅ {result['file']} (+{fields_str})")
            
            if len(enhanced_files) > 20:
                report_lines.append(f"... 还有 {len(enhanced_files) - 20} 个文件未显示")
            report_lines.append("")
        
        # 错误文件列表
        error_files = [r for r in results if r['errors']]
        if error_files:
            report_lines.append("🔴 错误文件列表")
            report_lines.append("-" * 40)
            for result in error_files[:10]:  # 只显示前10个
                errors_str = '; '.join(result['errors'])
                report_lines.append(f"❌ {result['file']}: {errors_str}")
            
            if len(error_files) > 10:
                report_lines.append(f"... 还有 {len(error_files) - 10} 个错误文件未显示")
            report_lines.append("")
        
        report_lines.append("=" * 80)
        report_lines.append("增强完成")
        report_lines.append("=" * 80)
        
        return '\n'.join(report_lines)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='为文档添加缺失的推荐元数据字段')
    parser.add_argument('target', help='目标文件或目录')
    parser.add_argument('--recursive', '-r', action='store_true', help='递归处理目录')
    parser.add_argument('--dry-run', '-d', action='store_true', help='试运行，不实际修改文件')
    parser.add_argument('--output', '-o', help='输出报告文件路径，默认输出到控制台')
    
    args = parser.parse_args()
    
    enhancer = MetadataEnhancer()
    
    # 确定目标路径
    target_path = args.target
    if not os.path.isabs(target_path):
        target_path = os.path.join(enhancer.project_root, target_path)
    
    if not os.path.exists(target_path):
        print(f"错误: 路径不存在: {target_path}")
        sys.exit(1)
    
    # 执行增强
    if os.path.isfile(target_path):
        results = [enhancer.enhance_file(target_path, args.dry_run)]
    else:
        results = enhancer.enhance_directory(target_path, args.recursive, args.dry_run)
    
    # 生成报告
    report = enhancer.generate_report(results)
    
    # 输出报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"报告已保存到: {args.output}")
    else:
        print(report)
    
    # 退出码
    error_files = sum(1 for r in results if r['errors'])
    if error_files > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()