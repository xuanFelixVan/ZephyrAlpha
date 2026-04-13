# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
文件重要性评分工具
用于大规模文件系统审计中的文件分层

功能:
    - 根据路径、类型、引用频率等计算文件重要性分数
    - 支持自定义权重配置
    - 生成文件分层报告

使用方式:
    from scripts.file_importance_scorer import FileImportanceScorer
    
    scorer = FileImportanceScorer(project_root="d:/ZephyrAlpha")
    scores = scorer.score_all_files()
    report = scorer.generate_report()
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class FileScore:
    """文件评分结果"""
    file_path: str
    total_score: float
    path_score: float
    type_score: float
    reference_score: float
    modification_score: float
    size_score: float
    layer: str  # 'core', 'important', 'general', 'temporary'
    metadata: Dict


class FileImportanceScorer:
    """
    文件重要性评分器
    
    评分算法:
        总分 = 路径重要性(30分) + 文件类型重要性(25分) + 
               引用频率(20分) + 修改频率(15分) + 文件大小(10分)
        
    分层标准:
        - 核心文件 (≥80分): 100%深度审计
        - 重要文件 (60-79分): 80%抽样审计
        - 一般文件 (40-59分): 50%抽样审计
        - 临时文件 (<40分): 10%抽样审计
    """
    
    # 核心目录权重 (路径重要性)
    CORE_DIRS = {
        'docs/01_FRAMEWORK': 30,
        'docs/System_Manifest.md': 30,
        'src/core': 28,
        'src/modules': 26,
        'docs/02_FACTOR_LIBRARY': 25,
        'docs/03_TRADING_TACTICS': 24,
        'docs/04_EXECUTION': 23,
        'config': 22,
        'scripts': 20,
        'tests': 18,
        'docs/05_IMPLEMENTATION': 15,
        'docs/09_AUDIT': 15,
        'docs': 12,
        'data': 8,
        'logs': 5,
        '.git': 2,
        '__pycache__': 1,
        'node_modules': 1,
    }
    
    # 文件类型权重
    FILE_TYPE_WEIGHTS = {
        # 蓝图文档 (最高权重)
        'BLUEPRINT.md': 25,
        '_BLUEPRINT.md': 25,
        
        # 核心代码
        'base.py': 24,
        'main.py': 23,
        '__init__.py': 5,
        
        # 配置文件
        'system.yaml': 22,
        'config.yaml': 20,
        
        # 文档文件
        'README.md': 18,
        'ARCHITECTURE.md': 22,
        'System_Manifest.md': 25,
        
        # 测试文件
        'test_*.py': 15,
        '*_test.py': 15,
        
        # 数据文件
        '*.csv': 8,
        '*.json': 10,
        
        # 临时文件
        '*.tmp': 2,
        '*.log': 3,
        '*.pyc': 1,
    }
    
    # 排除目录
    EXCLUDE_DIRS = {
        'A股数据',
        '.git',
        '__pycache__',
        'node_modules',
        '.pytest_cache',
        '.mypy_cache',
        'htmlcov',
        '.tox',
        'dist',
        'build',
        '*.egg-info',
    }
    
    def __init__(
        self,
        project_root: str,
        weights: Optional[Dict[str, float]] = None
    ):
        """
        初始化评分器
        
        参数:
            project_root: 项目根目录路径
            weights: 自定义权重配置 (可选)
        """
        self.project_root = Path(project_root)
        self.weights = weights or {
            'path': 0.30,      # 路径重要性权重
            'type': 0.25,      # 文件类型权重
            'reference': 0.20, # 引用频率权重
            'modification': 0.15, # 修改频率权重
            'size': 0.10,      # 文件大小权重
        }
        
        self.file_scores: Dict[str, FileScore] = {}
        self.reference_counts: Dict[str, int] = defaultdict(int)
        
    def scan_files(self) -> List[Path]:
        """
        扫描项目文件
        
        返回:
            List[Path]: 文件路径列表
        """
        logger.info(f"开始扫描项目文件: {self.project_root}")
        
        files = []
        for root, dirs, filenames in os.walk(self.project_root):
            # 过滤排除目录
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS and not d.startswith('.')]
            
            for filename in filenames:
                file_path = Path(root) / filename
                files.append(file_path)
        
        logger.info(f"扫描完成，共找到 {len(files)} 个文件")
        return files
    
    def calculate_path_score(self, file_path: Path) -> float:
        """
        计算路径重要性分数
        
        参数:
            file_path: 文件路径
        
        返回:
            float: 路径分数 (0-30)
        """
        relative_path = file_path.relative_to(self.project_root)
        path_str = str(relative_path).replace('\\', '/')
        
        # 检查是否匹配核心目录
        for core_dir, score in self.CORE_DIRS.items():
            if path_str.startswith(core_dir) or path_str == core_dir:
                return float(score)
        
        # 默认分数
        return 10.0
    
    def calculate_type_score(self, file_path: Path) -> float:
        """
        计算文件类型分数
        
        参数:
            file_path: 文件路径
        
        返回:
            float: 类型分数 (0-25)
        """
        filename = file_path.name
        
        # 精确匹配
        if filename in self.FILE_TYPE_WEIGHTS:
            return float(self.FILE_TYPE_WEIGHTS[filename])
        
        # 模式匹配
        for pattern, score in self.FILE_TYPE_WEIGHTS.items():
            if '*' in pattern:
                import fnmatch
                if fnmatch.fnmatch(filename, pattern):
                    return float(score)
        
        # 根据扩展名
        suffix = file_path.suffix.lower()
        extension_scores = {
            '.md': 12,
            '.py': 15,
            '.yaml': 12,
            '.yml': 12,
            '.json': 10,
            '.csv': 8,
            '.txt': 5,
            '.log': 3,
            '.pyc': 1,
        }
        
        return float(extension_scores.get(suffix, 5))
    
    def calculate_reference_score(self, file_path: Path) -> float:
        """
        计算引用频率分数
        
        参数:
            file_path: 文件路径
        
        返回:
            float: 引用分数 (0-20)
        """
        relative_path = str(file_path.relative_to(self.project_root))
        count = self.reference_counts.get(relative_path, 0)
        
        # 引用次数映射到分数
        # 0次引用: 5分
        # 1-5次: 10分
        # 6-10次: 15分
        # 10+次: 20分
        if count == 0:
            return 5.0
        elif count <= 5:
            return 10.0
        elif count <= 10:
            return 15.0
        else:
            return 20.0
    
    def calculate_modification_score(self, file_path: Path) -> float:
        """
        计算修改频率分数
        
        参数:
            file_path: 文件路径
        
        返回:
            float: 修改分数 (0-15)
        """
        try:
            stat = file_path.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)
            age_days = (datetime.now() - mtime).days
            
            # 近期修改的文件更重要
            if age_days <= 7:
                return 15.0
            elif age_days <= 30:
                return 12.0
            elif age_days <= 90:
                return 8.0
            elif age_days <= 365:
                return 5.0
            else:
                return 2.0
        except Exception as e:
            logger.warning(f"无法获取文件修改时间: {file_path}, {e}")
            return 5.0
    
    def calculate_size_score(self, file_path: Path) -> float:
        """
        计算文件大小分数
        
        参数:
            file_path: 文件路径
        
        返回:
            float: 大小分数 (0-10)
        """
        try:
            size_kb = file_path.stat().st_size / 1024
            
            # 适中的文件更重要
            # < 1KB: 3分 (太小可能不重要)
            # 1-10KB: 8分 (适中)
            # 10-100KB: 10分 (重要)
            # 100KB-1MB: 7分 (较大)
            # > 1MB: 4分 (过大可能包含数据)
            if size_kb < 1:
                return 3.0
            elif size_kb < 10:
                return 8.0
            elif size_kb < 100:
                return 10.0
            elif size_kb < 1024:
                return 7.0
            else:
                return 4.0
        except Exception as e:
            logger.warning(f"无法获取文件大小: {file_path}, {e}")
            return 5.0
    
    def calculate_total_score(self, file_path: Path) -> FileScore:
        """
        计算文件总分数
        
        参数:
            file_path: 文件路径
        
        返回:
            FileScore: 文件评分结果
        """
        path_score = self.calculate_path_score(file_path)
        type_score = self.calculate_type_score(file_path)
        reference_score = self.calculate_reference_score(file_path)
        modification_score = self.calculate_modification_score(file_path)
        size_score = self.calculate_size_score(file_path)
        
        # 加权总分
        # 每个维度的分数需要归一化到0-100分
        # path_score: 0-30分 -> 归一化到0-100分
        # type_score: 0-25分 -> 归一化到0-100分
        # reference_score: 0-20分 -> 归一化到0-100分
        # modification_score: 0-15分 -> 归一化到0-100分
        # size_score: 0-10分 -> 归一化到0-100分
        normalized_path = (path_score / 30.0) * 100
        normalized_type = (type_score / 25.0) * 100
        normalized_reference = (reference_score / 20.0) * 100
        normalized_modification = (modification_score / 15.0) * 100
        normalized_size = (size_score / 10.0) * 100
        
        # 加权求和
        total_score = (
            normalized_path * self.weights['path'] +
            normalized_type * self.weights['type'] +
            normalized_reference * self.weights['reference'] +
            normalized_modification * self.weights['modification'] +
            normalized_size * self.weights['size']
        )
        
        # 分层
        if total_score >= 80:
            layer = 'core'
        elif total_score >= 60:
            layer = 'important'
        elif total_score >= 40:
            layer = 'general'
        else:
            layer = 'temporary'
        
        return FileScore(
            file_path=str(file_path.relative_to(self.project_root)),
            total_score=round(total_score, 2),
            path_score=round(path_score, 2),
            type_score=round(type_score, 2),
            reference_score=round(reference_score, 2),
            modification_score=round(modification_score, 2),
            size_score=round(size_score, 2),
            layer=layer,
            metadata={
                'absolute_path': str(file_path),
                'size_kb': round(file_path.stat().st_size / 1024, 2),
            }
        )
    
    def score_all_files(self) -> Dict[str, FileScore]:
        """
        评分所有文件
        
        返回:
            Dict[str, FileScore]: 文件路径到评分结果的映射
        """
        files = self.scan_files()
        
        logger.info("开始计算文件重要性分数...")
        for i, file_path in enumerate(files, 1):
            if i % 100 == 0:
                logger.info(f"已处理 {i}/{len(files)} 个文件")
            
            try:
                score = self.calculate_total_score(file_path)
                self.file_scores[score.file_path] = score
            except Exception as e:
                logger.error(f"评分失败: {file_path}, {e}")
        
        logger.info(f"评分完成，共评分 {len(self.file_scores)} 个文件")
        return self.file_scores
    
    def generate_report(self, output_path: Optional[str] = None) -> Dict:
        """
        生成评分报告
        
        参数:
            output_path: 报告输出路径 (可选)
        
        返回:
            Dict: 报告数据
        """
        # 统计各层文件数量
        layer_stats = defaultdict(list)
        for score in self.file_scores.values():
            layer_stats[score.layer].append(score)
        
        report = {
            'summary': {
                'total_files': len(self.file_scores),
                'core_files': len(layer_stats['core']),
                'important_files': len(layer_stats['important']),
                'general_files': len(layer_stats['general']),
                'temporary_files': len(layer_stats['temporary']),
                'average_score': round(
                    sum(s.total_score for s in self.file_scores.values()) / len(self.file_scores), 2
                ) if self.file_scores else 0,
            },
            'layer_distribution': {
                layer: {
                    'count': len(scores),
                    'percentage': round(len(scores) / len(self.file_scores) * 100, 2) if self.file_scores else 0,
                    'avg_score': round(sum(s.total_score for s in scores) / len(scores), 2) if scores else 0,
                }
                for layer, scores in layer_stats.items()
            },
            'top_files': [
                asdict(score) for score in sorted(
                    self.file_scores.values(),
                    key=lambda x: x.total_score,
                    reverse=True
                )[:50]
            ],
            'files_by_layer': {
                layer: [asdict(score) for score in sorted(scores, key=lambda x: x.total_score, reverse=True)]
                for layer, scores in layer_stats.items()
            },
            'timestamp': datetime.now().isoformat(),
        }
        
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"报告已保存到: {output_file}")
        
        return report


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='文件重要性评分工具')
    parser.add_argument(
        '--project-root',
        default='d:/ZephyrAlpha',
        help='项目根目录路径'
    )
    parser.add_argument(
        '--output',
        default='docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/file_importance_scores.json',
        help='输出报告路径'
    )
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 执行评分
    scorer = FileImportanceScorer(project_root=args.project_root)
    scorer.score_all_files()
    report = scorer.generate_report(output_path=args.output)
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("文件重要性评分报告")
    print("=" * 60)
    print(f"总文件数: {report['summary']['total_files']}")
    print(f"核心文件: {report['summary']['core_files']} ({report['layer_distribution']['core']['percentage']}%)")
    print(f"重要文件: {report['summary']['important_files']} ({report['layer_distribution']['important']['percentage']}%)")
    print(f"一般文件: {report['summary']['general_files']} ({report['layer_distribution']['general']['percentage']}%)")
    print(f"临时文件: {report['summary']['temporary_files']} ({report['layer_distribution']['temporary']['percentage']}%)")
    print(f"平均分数: {report['summary']['average_score']}")
    print("=" * 60)


if __name__ == '__main__':
    main()
