#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
未索引文件分析脚本
分析未索引文件，生成索引改进建议
"""

import re
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict
import json

class UnindexedFileAnalyzer:
    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.results = {
            'total_files': 0,
            'indexed_files': 0,
            'unindexed_files': 0,
            'index_completeness': 0.0,
            'file_categories': defaultdict(list),
            'recommendations': []
        }
    
    def find_all_md_files(self) -> Dict[str, List[Path]]:
        """查找所有Markdown文件"""
        all_files = {'active': [], 'archive': []}
        
        for md_file in self.docs_root.rglob("*.md"):
            # 跳过INDEX.md文件
            if md_file.name == 'INDEX.md':
                continue
            
            # 分类为活跃文件或归档文件
            if '06_ARCHIVE' in str(md_file) or '99_ARCHIVE' in str(md_file):
                all_files['archive'].append(md_file)
            else:
                all_files['active'].append(md_file)
        
        return all_files
    
    def find_all_index_files(self) -> List[Path]:
        """查找所有INDEX.md文件"""
        index_files = []
        for index_file in self.docs_root.rglob("INDEX.md"):
            index_files.append(index_file)
        return index_files
    
    def extract_indexed_files(self, index_files: List[Path]) -> Set[str]:
        """提取所有被索引的文件"""
        indexed_files = set()
        
        for index_file in index_files:
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取所有相对路径链接
                link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                matches = re.findall(link_pattern, content)
                
                for link_text, link_url in matches:
                    # 跳过外部链接和锚点链接
                    if link_url.startswith('http://') or link_url.startswith('https://') or link_url.startswith('#'):
                        continue
                    
                    # 处理相对路径
                    if link_url.startswith('./'):
                        target_path = index_file.parent / link_url[2:]
                    elif link_url.startswith('../'):
                        target_path = index_file.parent / link_url
                    else:
                        target_path = index_file.parent / link_url
                    
                    # 规范化路径
                    try:
                        target_path = target_path.resolve()
                        indexed_files.add(str(target_path))
                    except:
                        pass
                        
            except Exception as e:
                print(f"处理索引文件 {index_file} 时出错: {str(e)}")
        
        return indexed_files
    
    def categorize_file(self, file_path: Path) -> str:
        """对文件进行分类"""
        file_name = file_path.name.lower()
        file_path_str = str(file_path).lower()
        
        # 蓝图文件
        if 'blueprint' in file_name or '蓝图' in file_name:
            return '蓝图文件'
        
        # 审计报告
        if 'audit' in file_name or 'report' in file_name or '审计' in file_name or '报告' in file_name:
            return '审计报告'
        
        # 配置文件
        if 'config' in file_name or '配置' in file_name or file_name.startswith('config_'):
            return '配置文件'
        
        # 技术规格
        if 'specification' in file_name or 'spec' in file_name or '规格' in file_name:
            return '技术规格'
        
        # 实施指南
        if 'implementation' in file_name or 'guide' in file_name or '实施' in file_name or '指南' in file_name:
            return '实施指南'
        
        # 设计文档
        if 'design' in file_name or '设计' in file_name:
            return '设计文档'
        
        # 模板文件
        if 'template' in file_name or '模板' in file_name:
            return '模板文件'
        
        # 案例研究
        if 'case' in file_name or '案例' in file_name:
            return '案例研究'
        
        # 培训材料
        if 'training' in file_name or '培训' in file_name:
            return '培训材料'
        
        # README文件
        if file_name == 'readme.md':
            return 'README文件'
        
        # 其他
        return '其他文档'
    
    def should_be_indexed(self, file_path: Path, category: str) -> bool:
        """判断文件是否应该被索引"""
        # README文件通常不需要在主索引中索引
        if category == 'README文件':
            return False
        
        # 蓝图文件通常有专门的蓝图索引
        if category == '蓝图文件':
            return False
        
        # 审计报告有专门的审计报告索引
        if category == '审计报告':
            return False
        
        # 配置文件通常不需要索引
        if category == '配置文件':
            return False
        
        # 其他类型的文件应该被索引
        return True
    
    def analyze_unindexed_files(self):
        """分析未索引文件"""
        print("=" * 80)
        print("未索引文件分析")
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
        index_files = self.find_all_index_files()
        print(f"索引文件数: {len(index_files)}")
        print()
        
        # 提取被索引的文件
        indexed_files = self.extract_indexed_files(index_files)
        print(f"被索引的文件数: {len(indexed_files)}")
        print()
        
        # 检查活跃文件是否被索引
        print("=" * 80)
        print("检查活跃文件索引完整性")
        print("=" * 80)
        
        unindexed_active = []
        
        for active_file in active_files:
            # 检查是否被索引
            if str(active_file.resolve()) not in indexed_files:
                unindexed_active.append(active_file)
                category = self.categorize_file(active_file)
                self.results['file_categories'][category].append(active_file)
        
        print(f"总活跃文件数: {len(active_files)}")
        print(f"已索引文件数: {len(active_files) - len(unindexed_active)}")
        print(f"未索引文件数: {len(unindexed_active)}")
        print(f"索引完整率: {(len(active_files) - len(unindexed_active)) / len(active_files) * 100:.1f}%")
        print()
        
        # 分析未索引文件分类
        print("=" * 80)
        print("未索引文件分类统计")
        print("=" * 80)
        
        for category, files in sorted(self.results['file_categories'].items(), key=lambda x: len(x[1]), reverse=True):
            percentage = len(files) / len(unindexed_active) * 100
            print(f"{category}: {len(files)}个 ({percentage:.1f}%)")
        
        print()
        
        # 生成改进建议
        print("=" * 80)
        print("索引改进建议")
        print("=" * 80)
        
        recommendations = []
        
        for category, files in self.results['file_categories'].items():
            should_index_count = sum(1 for f in files if self.should_be_indexed(f, category))
            
            if should_index_count > 0:
                recommendation = {
                    'category': category,
                    'total_files': len(files),
                    'should_index': should_index_count,
                    'priority': 'high' if should_index_count > 20 else 'medium' if should_index_count > 10 else 'low'
                }
                recommendations.append(recommendation)
                
                print(f"\n{category}:")
                print(f"  总文件数: {len(files)}")
                print(f"  建议索引: {should_index_count}")
                print(f"  优先级: {recommendation['priority']}")
        
        self.results['recommendations'] = recommendations
        
        print()
        print("=" * 80)
        print("总结")
        print("=" * 80)
        print(f"索引完整率: {(len(active_files) - len(unindexed_active)) / len(active_files) * 100:.1f}%")
        print(f"需要补充索引的文件数: {sum(r['should_index'] for r in recommendations)}")
        print(f"高优先级类别: {sum(1 for r in recommendations if r['priority'] == 'high')}")
        print(f"中优先级类别: {sum(1 for r in recommendations if r['priority'] == 'medium')}")
        print(f"低优先级类别: {sum(1 for r in recommendations if r['priority'] == 'low')}")
        
        # 保存结果到JSON
        output_file = self.docs_root.parent / 'scripts' / 'unindexed_files_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            # 将Path对象转换为字符串
            results_serializable = {
                'total_files': len(active_files),
                'indexed_files': len(active_files) - len(unindexed_active),
                'unindexed_files': len(unindexed_active),
                'index_completeness': (len(active_files) - len(unindexed_active)) / len(active_files) * 100,
                'file_categories': {k: [str(f) for f in v] for k, v in self.results['file_categories'].items()},
                'recommendations': recommendations
            }
            json.dump(results_serializable, f, ensure_ascii=False, indent=2)
        
        print(f"\n分析结果已保存到: {output_file}")

if __name__ == "__main__":
    analyzer = UnindexedFileAnalyzer()
    analyzer.analyze_unindexed_files()
