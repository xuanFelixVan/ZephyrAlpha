# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
分层抽样工具
用于大规模文件系统审计中的智能抽样

功能:
    - 根据文件重要性分层进行抽样
    - 支持自定义抽样比例
    - 生成抽样报告和审计清单

使用方式:
    from scripts.stratified_sampler import StratifiedSampler
    
    sampler = StratifiedSampler(scores_file='file_importance_scores.json')
    sample = sampler.generate_sample()
    sampler.save_audit_list(sample, output_path='audit_list.json')
"""
import json
import logging
import random
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SampledFile:
    """抽样文件"""
    file_path: str
    layer: str
    score: float
    sample_reason: str
    audit_priority: int  # 1-4, 1最高


class StratifiedSampler:
    """
    分层抽样器
    
    抽样策略:
        - 核心文件 (≥80分): 100%抽样
        - 重要文件 (60-79分): 80%抽样
        - 一般文件 (40-59分): 50%抽样
        - 临时文件 (<40分): 10%抽样
    
    抽样原则:
        1. 确保每个层级都有代表性样本
        2. 优先选择分数高的文件
        3. 随机性保证无偏抽样
        4. 支持自定义抽样比例
    """
    
    # 默认抽样比例
    DEFAULT_SAMPLE_RATES = {
        'core': 1.0,       # 核心文件100%抽样
        'important': 0.8,  # 重要文件80%抽样
        'general': 0.5,    # 一般文件50%抽样
        'temporary': 0.1,  # 临时文件10%抽样
    }
    
    # 审计优先级
    AUDIT_PRIORITIES = {
        'core': 1,        # 最高优先级
        'important': 2,   # 高优先级
        'general': 3,     # 中优先级
        'temporary': 4,   # 低优先级
    }
    
    def __init__(
        self,
        scores_file: str,
        sample_rates: Optional[Dict[str, float]] = None,
        random_seed: Optional[int] = None
    ):
        """
        初始化抽样器
        
        参数:
            scores_file: 文件评分结果JSON文件路径
            sample_rates: 自定义抽样比例 (可选)
            random_seed: 随机种子 (可选，用于可重复抽样)
        """
        self.scores_file = Path(scores_file)
        self.sample_rates = sample_rates or self.DEFAULT_SAMPLE_RATES.copy()
        
        if random_seed is not None:
            random.seed(random_seed)
        
        self.scores_data: Dict = {}
        self.files_by_layer: Dict[str, List[Dict]] = {}
        
        self._load_scores()
    
    def _load_scores(self) -> None:
        """加载文件评分数据"""
        if not self.scores_file.exists():
            raise FileNotFoundError(f"评分文件不存在: {self.scores_file}")
        
        with open(self.scores_file, 'r', encoding='utf-8') as f:
            self.scores_data = json.load(f)
        
        # 按层级分组文件
        for layer, files in self.scores_data.get('files_by_layer', {}).items():
            self.files_by_layer[layer] = files
        
        logger.info(f"已加载评分数据，共 {self.scores_data['summary']['total_files']} 个文件")
    
    def _sample_layer(
        self,
        layer: str,
        files: List[Dict],
        sample_rate: float
    ) -> List[SampledFile]:
        """
        对单个层级进行抽样
        
        参数:
            layer: 层级名称
            files: 该层级的文件列表
            sample_rate: 抽样比例
        
        返回:
            List[SampledFile]: 抽样结果列表
        """
        if not files:
            return []
        
        # 按分数排序
        sorted_files = sorted(files, key=lambda x: x['total_score'], reverse=True)
        
        # 计算抽样数量
        sample_size = int(len(sorted_files) * sample_rate)
        
        # 确保至少抽取1个文件（如果该层级有文件）
        if sample_size == 0 and len(sorted_files) > 0:
            sample_size = 1
        
        # 分数优先 + 随机抽样混合策略
        # 前50%按分数优先，后50%随机抽样
        priority_count = sample_size // 2
        random_count = sample_size - priority_count
        
        sampled = []
        
        # 分数优先部分
        for i in range(min(priority_count, len(sorted_files))):
            file_data = sorted_files[i]
            sampled.append(SampledFile(
                file_path=file_data['file_path'],
                layer=layer,
                score=file_data['total_score'],
                sample_reason='分数优先',
                audit_priority=self.AUDIT_PRIORITIES[layer]
            ))
        
        # 随机抽样部分
        remaining_files = sorted_files[priority_count:]
        if remaining_files and random_count > 0:
            random_sample = random.sample(
                remaining_files,
                min(random_count, len(remaining_files))
            )
            for file_data in random_sample:
                sampled.append(SampledFile(
                    file_path=file_data['file_path'],
                    layer=layer,
                    score=file_data['total_score'],
                    sample_reason='随机抽样',
                    audit_priority=self.AUDIT_PRIORITIES[layer]
                ))
        
        return sampled
    
    def generate_sample(
        self,
        custom_rates: Optional[Dict[str, float]] = None
    ) -> List[SampledFile]:
        """
        生成分层抽样结果
        
        参数:
            custom_rates: 自定义抽样比例 (可选，覆盖默认设置)
        
        返回:
            List[SampledFile]: 抽样文件列表
        """
        rates = custom_rates or self.sample_rates
        
        logger.info("开始分层抽样...")
        logger.info(f"抽样比例: {rates}")
        
        all_samples = []
        
        for layer, files in self.files_by_layer.items():
            sample_rate = rates.get(layer, 0.5)
            layer_samples = self._sample_layer(layer, files, sample_rate)
            all_samples.extend(layer_samples)
            
            logger.info(
                f"层级 {layer}: 总数 {len(files)}, "
                f"抽样 {len(layer_samples)} ({len(layer_samples)/len(files)*100:.1f}%)"
            )
        
        # 按审计优先级和分数排序
        all_samples.sort(key=lambda x: (x.audit_priority, -x.score))
        
        logger.info(f"抽样完成，共抽样 {len(all_samples)} 个文件")
        return all_samples
    
    def generate_audit_list(
        self,
        sample: List[SampledFile],
        batch_size: int = 50
    ) -> Dict:
        """
        生成审计清单
        
        参数:
            sample: 抽样文件列表
            batch_size: 每批审计的文件数量
        
        返回:
            Dict: 审计清单数据
        """
        # 按优先级分组
        priority_groups = {}
        for sampled_file in sample:
            priority = sampled_file.audit_priority
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(asdict(sampled_file))
        
        # 分批
        batches = []
        current_batch = []
        batch_number = 1
        
        for priority in sorted(priority_groups.keys()):
            for file_data in priority_groups[priority]:
                file_data['batch'] = batch_number
                current_batch.append(file_data)
                
                if len(current_batch) >= batch_size:
                    batches.append({
                        'batch_number': batch_number,
                        'files': current_batch.copy(),
                        'file_count': len(current_batch),
                    })
                    current_batch = []
                    batch_number += 1
        
        # 添加最后一批
        if current_batch:
            batches.append({
                'batch_number': batch_number,
                'files': current_batch,
                'file_count': len(current_batch),
            })
        
        audit_list = {
            'summary': {
                'total_files': len(sample),
                'total_batches': len(batches),
                'batch_size': batch_size,
                'priority_distribution': {
                    f'P{priority}': len(files)
                    for priority, files in priority_groups.items()
                },
            },
            'batches': batches,
            'timestamp': datetime.now().isoformat(),
        }
        
        return audit_list
    
    def save_audit_list(
        self,
        sample: List[SampledFile],
        output_path: str,
        batch_size: int = 50
    ) -> None:
        """
        保存审计清单到文件
        
        参数:
            sample: 抽样文件列表
            output_path: 输出文件路径
            batch_size: 每批审计的文件数量
        """
        audit_list = self.generate_audit_list(sample, batch_size)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(audit_list, f, ensure_ascii=False, indent=2)
        
        logger.info(f"审计清单已保存到: {output_file}")
    
    def generate_report(self, sample: List[SampledFile]) -> Dict:
        """
        生成抽样报告
        
        参数:
            sample: 抽样文件列表
        
        返回:
            Dict: 报告数据
        """
        # 统计各层级抽样情况
        layer_stats = {}
        for layer in ['core', 'important', 'general', 'temporary']:
            layer_files = [f for f in sample if f.layer == layer]
            total_in_layer = len(self.files_by_layer.get(layer, []))
            
            layer_stats[layer] = {
                'total_files': total_in_layer,
                'sampled_files': len(layer_files),
                'sample_rate': round(len(layer_files) / total_in_layer * 100, 2) if total_in_layer > 0 else 0,
                'avg_score': round(sum(f.score for f in layer_files) / len(layer_files), 2) if layer_files else 0,
                'audit_priority': self.AUDIT_PRIORITIES[layer],
            }
        
        report = {
            'summary': {
                'total_files_in_system': self.scores_data['summary']['total_files'],
                'total_sampled_files': len(sample),
                'overall_sample_rate': round(
                    len(sample) / self.scores_data['summary']['total_files'] * 100, 2
                ),
            },
            'layer_statistics': layer_stats,
            'sampled_files': [asdict(f) for f in sample],
            'timestamp': datetime.now().isoformat(),
        }
        
        return report


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='分层抽样工具')
    parser.add_argument(
        '--scores-file',
        default='docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/file_importance_scores.json',
        help='文件评分结果JSON文件路径'
    )
    parser.add_argument(
        '--output',
        default='docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/audit_list.json',
        help='输出审计清单路径'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=50,
        help='每批审计的文件数量'
    )
    parser.add_argument(
        '--random-seed',
        type=int,
        default=None,
        help='随机种子 (用于可重复抽样)'
    )
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 执行抽样
    sampler = StratifiedSampler(
        scores_file=args.scores_file,
        random_seed=args.random_seed
    )
    sample = sampler.generate_sample()
    sampler.save_audit_list(sample, output_path=args.output, batch_size=args.batch_size)
    
    # 生成报告
    report = sampler.generate_report(sample)
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("分层抽样报告")
    print("=" * 60)
    print(f"系统总文件数: {report['summary']['total_files_in_system']}")
    print(f"抽样文件数: {report['summary']['total_sampled_files']}")
    print(f"总体抽样率: {report['summary']['overall_sample_rate']}%")
    print("\n各层级抽样情况:")
    for layer, stats in report['layer_statistics'].items():
        print(f"  {layer:12} - 总数: {stats['total_files']:4}, "
              f"抽样: {stats['sampled_files']:4} ({stats['sample_rate']}%), "
              f"平均分: {stats['avg_score']}, "
              f"优先级: P{stats['audit_priority']}")
    print("=" * 60)


if __name__ == '__main__':
    main()
