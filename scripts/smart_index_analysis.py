#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
智能索引完整性分析脚本
识别专门的索引文件，并检查文件是否在专门的索引中被索引
"""

import re
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import json

class SmartIndexAnalyzer:
    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.results = {
            'total_files': 0,
            'indexed_files': 0,
            'unindexed_files': 0,
            'index_completeness': 0.0,
            'file_categories': defaultdict(list),
            'recommendations': [],
            'specialized_indexes': {
                'blueprint': [],
                'audit': [],
                'other': []
            }
        }
    
    def find_all_md_files(self) -> Dict[str, List[Path]]:
        """查找所有Markdown文件"""
        all_files = {'active': [], 'archive': []}
        
        for md_file in self.docs_root.rglob("*.md"):
            if md_file.name == 'INDEX.md':
                continue
            
            if '06_ARCHIVE' in str(md_file) or '99_ARCHIVE' in str(md_file):
                all_files['archive'].append(md_file)
            else:
                all_files['active'].append(md_file)
        
        return all_files
    
    def find_all_index_files(self) -> Dict[str, List[Path]]:
        """查找所有索引文件，并分类为专门索引和常规索引"""
        indexes = {
            'specialized': [],  # 专门索引（蓝图索引、审计报告索引等）
            'regular': []       # 常规索引
        }
        
        for index_file in self.docs_root.rglob("INDEX.md"):
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 识别专门索引
                if '蓝图索引' in content or 'BLUEPRINT_INDEX' in content or '蓝图文档总索引' in content:
                    indexes['specialized'].append(index_file)
                    self.results['specialized_indexes']['blueprint'].append(str(index_file))
                elif '审计报告索引' in content or 'REPORTS' in str(index_file).upper():
                    indexes['specialized'].append(index_file)
                    self.results['specialized_indexes']['audit'].append(str(index_file))
                else:
                    indexes['regular'].append(index_file)
                    
            except Exception as e:
                indexes['regular'].append(index_file)
        
        return indexes
    
    def extract_indexed_files(self, index_files: List[Path]) -> Set[str]:
        """提取所有被索引的文件"""
        indexed_files = set()
        
        for index_file in index_files:
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                matches = re.findall(link_pattern, content)
                
                for link_text, link_url in matches:
                    if link_url.startswith('http://') or link_url.startswith('https://') or link_url.startswith('#'):
                        continue
                    
                    if link_url.startswith('./'):
                        target_path = index_file.parent / link_url[2:]
                    elif link_url.startswith('../'):
                        target_path = index_file.parent / link_url
                    else:
                        target_path = index_file.parent / link_url
                    
                    try:
                        target_path = target_path.resolve()
                        indexed_files.add(str(target_path))
                    except:
                        pass
                        
            except Exception as e:
                pass
        
        return indexed_files
    
    def categorize_file(self, file_path: Path) -> str:
        """对文件进行分类"""
        file_name = file_path.name.lower()
        file_path_str = str(file_path).lower()
        
        if 'blueprint' in file_name or '蓝图' in file_name:
            return '蓝图文件'
        
        if 'audit' in file_name or 'report' in file_name or '审计' in file_name or '报告' in file_name:
            return '审计报告'
        
        if 'config' in file_name or '配置' in file_name or file_name.startswith('config_'):
            return '配置文件'
        
        if 'specification' in file_name or 'spec' in file_name or '规格' in file_name:
            return '技术规格'
        
        if 'implementation' in file_name or 'guide' in file_name or '实施' in file_name or '指南' in file_name:
            return '实施指南'
        
        if 'design' in file_name or '设计' in file_name:
            return '设计文档'
        
        if 'template' in file_name or '模板' in file_name:
            return '模板文件'
        
        if 'case' in file_name or '案例' in file_name:
            return '案例研究'
        
        if 'training' in file_name or '培训' in file_name:
            return '培训材料'
        
        if file_name == 'readme.md':
            return 'README文件'
        
        return '其他文档'
    
    def should_be_indexed(self, file_path: Path, category: str, indexed_files: Set[str]) -> tuple:
        """判断文件是否应该被索引，返回(是否需要索引, 原因)"""
        # 检查文件是否已经在任何索引中
        file_str = str(file_path.resolve())
        if file_str in indexed_files:
            return (False, "已在索引中")
        
        # README文件通常不需要在主索引中索引
        if category == 'README文件':
            return (False, "README文件通常不需要在主索引中索引")
        
        # 蓝图文件 - 检查是否在专门的蓝图索引中
        if category == '蓝图文件':
            # 检查是否有专门的蓝图索引
            blueprint_indexes = self.results['specialized_indexes']['blueprint']
            if blueprint_indexes:
                # 检查是否在蓝图索引中
                for bp_index in blueprint_indexes:
                    bp_index_path = Path(bp_index)
                    try:
                        with open(bp_index_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        if file_path.name in content or str(file_path.relative_to(bp_index_path.parent)) in content:
                            return (False, "已在专门的蓝图索引中")
                    except:
                        pass
            return (False, "蓝图文件有专门的蓝图索引，不需要在主索引中重复索引")
        
        # 审计报告 - 检查是否在专门的审计报告索引中
        if category == '审计报告':
            audit_indexes = self.results['specialized_indexes']['audit']
            if audit_indexes:
                for audit_index in audit_indexes:
                    audit_index_path = Path(audit_index)
                    try:
                        with open(audit_index_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        if file_path.name in content or str(file_path.relative_to(audit_index_path.parent)) in content:
                            return (False, "已在专门的审计报告索引中")
                    except:
                        pass
            return (False, "审计报告有专门的审计报告索引，不需要在主索引中重复索引")
        
        # 配置文件通常不需要索引
        if category == '配置文件':
            return (False, "配置文件通常不需要索引")
        
        # 其他类型的文件应该被索引
        return (True, "需要在主索引中索引")
    
    def analyze_index_completeness(self):
        """分析索引完整性"""
        print("=" * 80)
        print("智能索引完整性分析")
        print("=" * 80)
        print(f"文档根目录: {self.docs_root}")
        print()
        
        # 查找所有文件
        all_files = self.find_all_md_files()
        active_files = all_files['active']
        archive_files = all_files['archive']
        
        print(f"活跃文件数: {len(active_files)}")
        print(f"归档文件数: {len(archive_files)}")
        print()
        
        # 查找所有索引文件
        indexes = self.find_all_index_files()
        specialized_indexes = indexes['specialized']
        regular_indexes = indexes['regular']
        
        print(f"专门索引数: {len(specialized_indexes)}")
        print(f"常规索引数: {len(regular_indexes)}")
        print()
        
        # 显示专门索引
        print("=" * 80)
        print("专门索引列表")
        print("=" * 80)
        for idx_type, idx_list in self.results['specialized_indexes'].items():
            if idx_list:
                print(f"\n{idx_type.upper()}索引:")
                for idx in idx_list:
                    print(f"  - {Path(idx).relative_to(self.docs_root)}")
        print()
        
        # 提取被索引的文件
        all_indexes = specialized_indexes + regular_indexes
        indexed_files = self.extract_indexed_files(all_indexes)
        
        print(f"被索引的文件数: {len(indexed_files)}")
        print()
        
        # 检查活跃文件是否被索引
        print("=" * 80)
        print("检查活跃文件索引完整性")
        print("=" * 80)
        
        unindexed_active = []
        truly_unindexed = []
        
        for active_file in active_files:
            file_str = str(active_file.resolve())
            if file_str not in indexed_files:
                unindexed_active.append(active_file)
                category = self.categorize_file(active_file)
                self.results['file_categories'][category].append(active_file)
                
                # 检查是否真的需要索引
                should_index, reason = self.should_be_indexed(active_file, category, indexed_files)
                if should_index:
                    truly_unindexed.append({
                        'file': active_file,
                        'category': category,
                        'reason': reason
                    })
        
        print(f"总活跃文件数: {len(active_files)}")
        print(f"已索引文件数: {len(active_files) - len(unindexed_active)}")
        print(f"未索引文件数: {len(unindexed_active)}")
        print(f"真正需要索引的文件数: {len(truly_unindexed)}")
        print(f"索引完整率: {(len(active_files) - len(unindexed_active)) / len(active_files) * 100:.1f}%")
        print(f"调整后索引完整率: {(len(active_files) - len(truly_unindexed)) / len(active_files) * 100:.1f}%")
        print()
        
        # 分析未索引文件分类
        print("=" * 80)
        print("未索引文件分类统计")
        print("=" * 80)
        
        for category, files in sorted(self.results['file_categories'].items(), key=lambda x: len(x[1]), reverse=True):
            percentage = len(files) / len(unindexed_active) * 100
            print(f"{category}: {len(files)}个 ({percentage:.1f}%)")
        
        print()
        
        # 显示真正需要索引的文件
        if truly_unindexed:
            print("=" * 80)
            print("真正需要索引的文件")
            print("=" * 80)
            
            for item in truly_unindexed:
                print(f"  - {item['file'].relative_to(self.docs_root)} ({item['category']})")
        
        print()
        print("=" * 80)
        print("总结")
        print("=" * 80)
        print(f"索引完整率: {(len(active_files) - len(unindexed_active)) / len(active_files) * 100:.1f}%")
        print(f"调整后索引完整率: {(len(active_files) - len(truly_unindexed)) / len(active_files) * 100:.1f}%")
        print(f"真正需要补充索引的文件数: {len(truly_unindexed)}")
        
        # 保存结果到JSON
        output_file = self.docs_root.parent / 'scripts' / 'smart_index_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            results_serializable = {
                'total_files': len(active_files),
                'indexed_files': len(active_files) - len(unindexed_active),
                'unindexed_files': len(unindexed_active),
                'truly_unindexed': len(truly_unindexed),
                'index_completeness': (len(active_files) - len(unindexed_active)) / len(active_files) * 100,
                'adjusted_index_completeness': (len(active_files) - len(truly_unindexed)) / len(active_files) * 100,
                'file_categories': {k: [str(f) for f in v] for k, v in self.results['file_categories'].items()},
                'specialized_indexes': self.results['specialized_indexes'],
                'truly_unindexed_files': [{'file': str(item['file']), 'category': item['category']} for item in truly_unindexed]
            }
            json.dump(results_serializable, f, ensure_ascii=False, indent=2)
        
        print(f"\n分析结果已保存到: {output_file}")

if __name__ == "__main__":
    analyzer = SmartIndexAnalyzer()
    analyzer.analyze_index_completeness()
