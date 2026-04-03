"""
文档元数据完善工具
自动为文档添加推荐的元数据字段

功能:
    - 扫描文档元数据
    - 自动推断推荐字段值
    - 批量添加元数据
    - 生成完善报告

使用方式:
    python scripts/metadata_enhancer.py --scan
    python scripts/metadata_enhancer.py --enhance
    python scripts/metadata_enhancer.py --report
"""
import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class MetadataGap:
    """元数据缺失"""
    file_path: str
    missing_fields: List[str]
    suggested_values: Dict[str, str]
    auto_fillable: bool


class MetadataEnhancer:
    """
    元数据完善器
    
    推荐字段:
        - standard_type: 标准类型
        - applicable_scope: 适用范围
        - compliance_level: 合规级别
        - parent_document: 父文档
        - implementation_status: 实现状态
    """
    
    # 推荐的元数据字段
    RECOMMENDED_FIELDS = {
        'standard_type',
        'applicable_scope',
        'compliance_level',
        'parent_document',
        'implementation_status',
    }
    
    # 必需的元数据字段
    REQUIRED_FIELDS = {
        'owner',
        'version',
        'module_id',
        'created_date',
        'last_updated',
    }
    
    # 所有需要检查的字段
    ALL_FIELDS = RECOMMENDED_FIELDS | REQUIRED_FIELDS
    
    # 标准类型映射
    STANDARD_TYPE_MAP = {
        'BLUEPRINT': '蓝图标准',
        'SPECIFICATION': '技术规范',
        'STANDARD': '管理标准',
        'GUIDE': '实施指南',
        'TEMPLATE': '模板文档',
        'REPORT': '审计报告',
        'DESIGN': '设计文档',
    }
    
    # 目录到适用范围的映射
    SCOPE_MAP = {
        '01_FRAMEWORK': '系统架构',
        '02_FACTOR_LIBRARY': '因子库',
        '03_TRADING_TACTICS': '交易策略',
        '04_EXECUTION': '交易执行',
        '05_IMPLEMENTATION': '系统实施',
        '06_ARCHIVE': '归档文档',
        '07_RESEARCH': '研究实验',
        '08_AI_GOVERNANCE': 'AI治理',
        '09_AUDIT': '审计质量',
        'design': '设计文档',
    }
    
    def __init__(self, project_root: str):
        """
        初始化元数据完善器
        
        参数:
            project_root: 项目根目录路径
        """
        self.project_root = Path(project_root)
        self.metadata_gaps: List[MetadataGap] = []
    
    def extract_metadata(self, content: str) -> Tuple[Dict[str, str], int]:
        """
        提取YAML元数据
        
        参数:
            content: 文档内容
        
        返回:
            Tuple[Dict, int]: (元数据字典, 元数据结束位置)
        """
        metadata = {}
        metadata_end = 0
        
        if content.startswith('---'):
            metadata_end = content.find('---', 3)
            if metadata_end != -1:
                metadata_text = content[3:metadata_end]
                
                # 解析元数据
                for line in metadata_text.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip().strip('"\'')
        
        return metadata, metadata_end
    
    def infer_standard_type(self, file_path: Path, metadata: Dict) -> str:
        """推断标准类型"""
        filename = file_path.name
        
        if 'BLUEPRINT' in filename.upper():
            return '蓝图标准'
        elif 'SPECIFICATION' in filename.upper() or 'TECHNICAL_SPEC' in filename.upper():
            return '技术规范'
        elif 'STANDARD' in filename.upper():
            return '管理标准'
        elif 'GUIDE' in filename.upper() or 'GUIDELINE' in filename.upper():
            return '实施指南'
        elif 'TEMPLATE' in filename.upper():
            return '模板文档'
        elif 'REPORT' in filename.upper():
            return '审计报告'
        elif 'DESIGN' in str(file_path).upper():
            return '设计文档'
        else:
            return '技术文档'
    
    def infer_applicable_scope(self, file_path: Path, metadata: Dict) -> str:
        """推断适用范围"""
        path_parts = file_path.parts
        
        # 查找标准分类目录
        for part in path_parts:
            if part in self.SCOPE_MAP:
                return self.SCOPE_MAP[part]
        
        return '全系统'
    
    def infer_compliance_level(self, file_path: Path, metadata: Dict) -> str:
        """推断合规级别"""
        status = metadata.get('status', '').lower()
        
        if status == 'stable':
            return '正式标准'
        elif status == 'active':
            return '初始标准'
        elif status == 'archived':
            return '归档标准'
        else:
            return '初始标准'
    
    def infer_parent_document(self, file_path: Path, metadata: Dict) -> str:
        """推断父文档"""
        # 查找上级目录的INDEX.md
        parent_dir = file_path.parent
        index_file = parent_dir / 'INDEX.md'
        
        if index_file.exists():
            # 计算相对路径
            relative_path = os.path.relpath(index_file, file_path.parent)
            return relative_path.replace('\\', '/')
        
        # 如果没有INDEX.md，查找上级目录
        if len(file_path.parts) > 2:
            parent_parent = parent_dir.parent
            parent_index = parent_parent / 'INDEX.md'
            
            if parent_index.exists():
                relative_path = os.path.relpath(parent_index, file_path.parent)
                return relative_path.replace('\\', '/')
        
        return '../INDEX.md'
    
    def infer_implementation_status(self, file_path: Path, metadata: Dict) -> str:
        """推断实现状态"""
        status = metadata.get('status', '').lower()
        
        if status == 'archived':
            return '已归档'
        elif status == 'stable':
            return '已完成'
        elif status == 'active':
            filename = file_path.name
            if 'BLUEPRINT' in filename.upper():
                return '设计阶段'
            else:
                return '进行中'
        else:
            return '设计阶段'
    
    def infer_owner(self, file_path: Path, metadata: Dict) -> str:
        """推断文档所有者"""
        if 'owner' in metadata:
            return metadata['owner']
        
        path_str = str(file_path)
        
        if '01_FRAMEWORK' in path_str:
            return '首席架构师'
        elif '02_FACTOR_LIBRARY' in path_str:
            return '因子库负责人'
        elif '03_TRADING_TACTICS' in path_str:
            return '策略层负责人'
        elif '04_EXECUTION' in path_str:
            return '执行层负责人'
        elif '05_IMPLEMENTATION' in path_str:
            return '实施负责人'
        elif '09_AUDIT' in path_str:
            return '首席审计官'
        elif 'design' in path_str.lower():
            return '设计负责人'
        else:
            return '文档维护者'
    
    def infer_version(self, file_path: Path, metadata: Dict) -> str:
        """推断文档版本"""
        if 'version' in metadata:
            return metadata['version']
        
        return '1.0.0'
    
    def infer_module_id(self, file_path: Path, metadata: Dict) -> str:
        """推断模块ID"""
        if 'module_id' in metadata:
            return metadata['module_id']
        
        filename = file_path.stem
        path_parts = file_path.parts
        
        for i, part in enumerate(path_parts):
            if part.startswith(('LAYER_', 'L0_', 'L1_', 'L2_', 'L3_', 'L4_', 'L5_', 'L6_', 'L7_', 'L8_', 'L9_', 'L10_', 'L11_')):
                return f"{part}_{filename.upper()[:20]}"
        
        if '01_FRAMEWORK' in str(file_path):
            return f"DOC_{filename.upper()[:20]}"
        elif '02_FACTOR_LIBRARY' in str(file_path):
            return f"FAC_{filename.upper()[:20]}"
        elif '03_TRADING_TACTICS' in str(file_path):
            return f"TAC_{filename.upper()[:20]}"
        elif '04_EXECUTION' in str(file_path):
            return f"EXE_{filename.upper()[:20]}"
        elif '05_IMPLEMENTATION' in str(file_path):
            return f"IMP_{filename.upper()[:20]}"
        else:
            return f"DOC_{filename.upper()[:20]}"
    
    def infer_created_date(self, file_path: Path, metadata: Dict) -> str:
        """推断创建日期"""
        if 'created_date' in metadata:
            return metadata['created_date']
        
        stat = file_path.stat()
        created_time = datetime.fromtimestamp(stat.st_ctime)
        return created_time.strftime('%Y-%m-%d')
    
    def infer_last_updated(self, file_path: Path, metadata: Dict) -> str:
        """推断最后更新时间"""
        if 'last_updated' in metadata:
            return metadata['last_updated']
        
        stat = file_path.stat()
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        return modified_time.strftime('%Y-%m-%d')
    
    def scan_metadata_gaps(self, file_path: Path) -> Optional[MetadataGap]:
        """
        扫描文件的元数据缺失
        
        参数:
            file_path: 文件路径
        
        返回:
            Optional[MetadataGap]: 元数据缺失信息 (如果没有缺失则返回None)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取元数据
            metadata, _ = self.extract_metadata(content)
            
            # 检查缺失字段（包括推荐字段和必需字段）
            missing_fields = self.ALL_FIELDS - set(metadata.keys())
            
            if not missing_fields:
                return None
            
            # 推断建议值
            suggested_values = {}
            
            # 推荐字段
            if 'standard_type' in missing_fields:
                suggested_values['standard_type'] = self.infer_standard_type(file_path, metadata)
            
            if 'applicable_scope' in missing_fields:
                suggested_values['applicable_scope'] = self.infer_applicable_scope(file_path, metadata)
            
            if 'compliance_level' in missing_fields:
                suggested_values['compliance_level'] = self.infer_compliance_level(file_path, metadata)
            
            if 'parent_document' in missing_fields:
                suggested_values['parent_document'] = self.infer_parent_document(file_path, metadata)
            
            if 'implementation_status' in missing_fields:
                suggested_values['implementation_status'] = self.infer_implementation_status(file_path, metadata)
            
            # 必需字段
            if 'owner' in missing_fields:
                suggested_values['owner'] = self.infer_owner(file_path, metadata)
            
            if 'version' in missing_fields:
                suggested_values['version'] = self.infer_version(file_path, metadata)
            
            if 'module_id' in missing_fields:
                suggested_values['module_id'] = self.infer_module_id(file_path, metadata)
            
            if 'created_date' in missing_fields:
                suggested_values['created_date'] = self.infer_created_date(file_path, metadata)
            
            if 'last_updated' in missing_fields:
                suggested_values['last_updated'] = self.infer_last_updated(file_path, metadata)
            
            return MetadataGap(
                file_path=str(file_path.relative_to(self.project_root)),
                missing_fields=list(missing_fields),
                suggested_values=suggested_values,
                auto_fillable=True,
            )
        
        except Exception as e:
            logger.error(f"扫描元数据失败: {file_path}, {e}")
            return None
    
    def scan_all_files(self) -> List[MetadataGap]:
        """
        扫描所有Markdown文件
        
        返回:
            List[MetadataGap]: 所有元数据缺失列表
        """
        logger.info("开始扫描所有文件...")
        
        self.metadata_gaps = []
        
        for root, dirs, files in os.walk(self.project_root):
            # 过滤排除目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {'A股数据', 'node_modules'}]
            
            for filename in files:
                if filename.endswith('.md'):
                    file_path = Path(root) / filename
                    gap = self.scan_metadata_gaps(file_path)
                    if gap:
                        self.metadata_gaps.append(gap)
        
        logger.info(f"扫描完成，共发现 {len(self.metadata_gaps)} 个文件缺少推荐字段")
        return self.metadata_gaps
    
    def generate_enhancement_report(self) -> Dict:
        """
        生成完善报告
        
        返回:
            Dict: 完善报告
        """
        # 统计缺失字段
        field_counts = defaultdict(int)
        for gap in self.metadata_gaps:
            for field in gap.missing_fields:
                field_counts[field] += 1
        
        report = {
            'summary': {
                'scan_time': datetime.now().isoformat(),
                'total_files_with_gaps': len(self.metadata_gaps),
                'auto_fillable': sum(1 for g in self.metadata_gaps if g.auto_fillable),
                'field_statistics': dict(field_counts),
            },
            'gaps': [asdict(gap) for gap in self.metadata_gaps],
        }
        
        return report
    
    def save_report(self, report: Dict, output_path: str) -> None:
        """
        保存完善报告
        
        参数:
            report: 完善报告
            output_path: 输出文件路径
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"完善报告已保存到: {output_file}")
    
    def enhance_metadata(self, dry_run: bool = True) -> Dict:
        """
        完善元数据
        
        参数:
            dry_run: 是否为演练模式 (不实际修改文件)
        
        返回:
            Dict: 完善结果
        """
        logger.info(f"开始完善元数据 (dry_run={dry_run})...")
        
        results = {
            'total_attempted': 0,
            'successful': 0,
            'failed': 0,
            'details': [],
        }
        
        for gap in self.metadata_gaps:
            if not gap.auto_fillable:
                continue
            
            results['total_attempted'] += 1
            
            try:
                file_path = self.project_root / gap.file_path
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取元数据和位置
                metadata, metadata_end = self.extract_metadata(content)
                
                # 构建新的元数据字段
                new_fields = []
                for field, value in gap.suggested_values.items():
                    if field not in metadata:
                        new_fields.append(f"{field}: {value}")
                
                if not new_fields:
                    continue
                
                # 插入新字段
                if metadata_end > 0:
                    # 在现有元数据后添加
                    before = content[:metadata_end]
                    after = content[metadata_end:]
                    
                    # 在最后一个字段后添加新字段
                    new_metadata_text = '\n'.join(new_fields)
                    enhanced_content = before + new_metadata_text + '\n' + after
                else:
                    # 没有元数据，创建新的元数据块
                    metadata_block = '---\n' + '\n'.join(new_fields) + '\n---\n'
                    enhanced_content = metadata_block + content
                
                # 写入文件（如果不是演练模式）
                if not dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(enhanced_content)
                    
                    logger.info(f"已完善元数据: {gap.file_path}")
                
                results['successful'] += 1
                results['details'].append({
                    'file': gap.file_path,
                    'added_fields': list(gap.suggested_values.keys()),
                    'status': 'success',
                })
            
            except Exception as e:
                logger.error(f"完善元数据失败: {gap.file_path}, {e}")
                results['failed'] += 1
                results['details'].append({
                    'file': gap.file_path,
                    'status': 'failed',
                    'error': str(e),
                })
        
        logger.info(f"完善完成: 成功 {results['successful']}, 失败 {results['failed']}")
        return results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='文档元数据完善工具')
    parser.add_argument(
        '--project-root',
        default='d:/ZephyrAlpha',
        help='项目根目录路径'
    )
    parser.add_argument(
        '--scan',
        action='store_true',
        help='扫描元数据缺失'
    )
    parser.add_argument(
        '--enhance',
        action='store_true',
        help='完善元数据'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='演练模式，不实际修改文件'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='生成完善报告'
    )
    parser.add_argument(
        '--output',
        default='docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/metadata_enhancement_report.json',
        help='输出报告路径'
    )
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建元数据完善器
    enhancer = MetadataEnhancer(project_root=args.project_root)
    
    # 扫描元数据缺失
    if args.scan or args.enhance or args.report:
        gaps = enhancer.scan_all_files()
    
    # 生成报告
    if args.report:
        report = enhancer.generate_enhancement_report()
        enhancer.save_report(report, args.output)
        
        # 打印摘要
        print("\n" + "=" * 60)
        print("元数据完善报告")
        print("=" * 60)
        print(f"缺少推荐字段的文件数: {report['summary']['total_files_with_gaps']}")
        print(f"可自动完善: {report['summary']['auto_fillable']}")
        print("\n字段缺失统计:")
        for field, count in report['summary']['field_statistics'].items():
            print(f"  {field}: {count}")
        print("=" * 60)
    
    # 完善元数据
    if args.enhance:
        results = enhancer.enhance_metadata(dry_run=args.dry_run)
        
        print("\n" + "=" * 60)
        print("元数据完善结果")
        print("=" * 60)
        print(f"尝试完善: {results['total_attempted']}")
        print(f"完善成功: {results['successful']}")
        print(f"完善失败: {results['failed']}")
        print("=" * 60)


if __name__ == '__main__':
    main()
