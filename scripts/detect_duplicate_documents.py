#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
重复文档检测工具

功能：
1. 检测文件名相似的文档
2. 检测内容相似的文档
3. 检测BLUEPRINT与TECHNICAL_SPECIFICATION重复
4. 生成重复文档检测报告

使用方法：
    python detect_duplicate_documents.py [目录路径]

示例：
    python detect_duplicate_documents.py docs/
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from collections import defaultdict
import hashlib


class DuplicateDocumentDetector:
    """重复文档检测器"""
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.duplicates = []
        self.stats = {
            'total_files': 0,
            'duplicate_pairs': 0,
            'blueprint_spec_pairs': 0,
            'similar_name_pairs': 0
        }
        
    def get_file_hash(self, file_path: Path) -> str:
        """计算文件内容的哈希值"""
        hasher = hashlib.md5()
        
        try:
            with open(file_path, 'rb') as f:
                buf = f.read()
                hasher.update(buf)
            return hasher.hexdigest()
        except Exception as e:
            print(f"无法读取文件 {file_path}: {e}")
            return ""
    
    def extract_module_name(self, filename: str) -> str:
        """
        从文件名中提取模块名称
        
        示例：
        - REINFORCEMENT_LEARNING_BLUEPRINT.md -> REINFORCEMENT_LEARNING
        - REINFORCEMENT_LEARNING_TECHNICAL_SPECIFICATION.md -> REINFORCEMENT_LEARNING
        """
        name = Path(filename).stem
        
        # 移除常见后缀
        suffixes = [
            '_BLUEPRINT',
            '_TECHNICAL_SPECIFICATION',
            '_SPECIFICATION',
            '_SPEC',
            '_DESIGN',
            '_IMPLEMENTATION',
            '_GUIDE',
            '_MANUAL'
        ]
        
        for suffix in suffixes:
            if name.endswith(suffix):
                return name[:-len(suffix)]
        
        return name
    
    def detect_blueprint_spec_duplicates(self, files: List[Path]):
        """
        检测BLUEPRINT与TECHNICAL_SPECIFICATION重复
        
        规则：如果同一模块同时存在BLUEPRINT和TECHNICAL_SPECIFICATION，
        则认为是重复
        """
        module_files = defaultdict(list)
        
        for file_path in files:
            if file_path.suffix.lower() != '.md':
                continue
            
            filename = file_path.name
            module_name = self.extract_module_name(filename)
            
            # 判断文件类型
            file_type = None
            if 'BLUEPRINT' in filename:
                file_type = 'BLUEPRINT'
            elif 'TECHNICAL_SPECIFICATION' in filename or 'SPECIFICATION' in filename:
                file_type = 'SPECIFICATION'
            
            if file_type:
                module_files[module_name].append({
                    'path': file_path,
                    'type': file_type
                })
        
        # 检查重复
        for module_name, files in module_files.items():
            types = [f['type'] for f in files]
            
            if 'BLUEPRINT' in types and 'SPECIFICATION' in types:
                blueprint_files = [f for f in files if f['type'] == 'BLUEPRINT']
                spec_files = [f for f in files if f['type'] == 'SPECIFICATION']
                
                for bp_file in blueprint_files:
                    for spec_file in spec_files:
                        self.duplicates.append({
                            'type': 'BLUEPRINT_SPEC_DUPLICATE',
                            'module': module_name,
                            'files': [
                                str(bp_file['path'].relative_to(self.root_dir)),
                                str(spec_file['path'].relative_to(self.root_dir))
                            ],
                            'suggestion': f'保留BLUEPRINT，归档SPECIFICATION'
                        })
                        self.stats['blueprint_spec_pairs'] += 1
    
    def detect_similar_names(self, files: List[Path]):
        """
        检测文件名相似的文档
        
        规则：如果两个文件名的相似度超过80%，则认为是相似
        """
        # 简单实现：检查是否有相同的前缀
        name_groups = defaultdict(list)
        
        for file_path in files:
            if file_path.suffix.lower() != '.md':
                continue
            
            name = Path(file_path).stem
            
            # 提取前缀（前20个字符或第一个下划线之前）
            prefix = name.split('_')[0] if '_' in name else name[:20]
            name_groups[prefix].append(file_path)
        
        # 检查重复
        for prefix, group_files in name_groups.items():
            if len(group_files) > 1:
                # 检查是否已经在BLUEPRINT_SPEC_DUPLICATE中
                for i, file1 in enumerate(group_files):
                    for file2 in group_files[i+1:]:
                        module1 = self.extract_module_name(file1.name)
                        module2 = self.extract_module_name(file2.name)
                        
                        if module1 == module2:
                            # 已经在BLUEPRINT_SPEC_DUPLICATE中处理
                            continue
                        
                        self.duplicates.append({
                            'type': 'SIMILAR_NAME',
                            'files': [
                                str(file1.relative_to(self.root_dir)),
                                str(file2.relative_to(self.root_dir))
                            ],
                            'suggestion': '检查是否为重复文档'
                        })
                        self.stats['similar_name_pairs'] += 1
    
    def scan_directory(self):
        """扫描目录中的所有文件"""
        print(f"正在扫描目录: {self.root_dir}")
        
        files = []
        
        for file_path in self.root_dir.rglob('*'):
            if file_path.is_file():
                # 跳过隐藏文件和特定目录
                if file_path.name.startswith('.') or \
                   any(part.startswith('.') for part in file_path.parts):
                    continue
                
                # 跳过非文档文件
                if file_path.suffix.lower() not in ['.md', '.yaml', '.yml', '.json']:
                    continue
                
                # 跳过归档目录
                if 'ARCHIVE' in file_path.parts or 'archive' in file_path.parts:
                    continue
                
                files.append(file_path)
                self.stats['total_files'] += 1
        
        print(f"扫描完成: 共检查 {self.stats['total_files']} 个文件")
        
        # 检测重复
        print("正在检测BLUEPRINT与SPECIFICATION重复...")
        self.detect_blueprint_spec_duplicates(files)
        
        print("正在检测相似文件名...")
        self.detect_similar_names(files)
        
        self.stats['duplicate_pairs'] = len(self.duplicates)
    
    def generate_report(self) -> str:
        """生成重复文档检测报告"""
        report = []
        report.append("=" * 80)
        report.append("重复文档检测报告")
        report.append("=" * 80)
        report.append(f"检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"检测目录: {self.root_dir}")
        report.append("")
        
        # 统计信息
        report.append("## 统计信息")
        report.append("-" * 80)
        report.append(f"总文件数: {self.stats['total_files']}")
        report.append(f"重复文档对数: {self.stats['duplicate_pairs']}")
        report.append(f"BLUEPRINT-SPEC重复对数: {self.stats['blueprint_spec_pairs']}")
        report.append(f"相似文件名对数: {self.stats['similar_name_pairs']}")
        report.append("")
        
        # 问题详情
        if self.duplicates:
            report.append("## 重复详情")
            report.append("-" * 80)
            
            for i, dup in enumerate(self.duplicates, 1):
                report.append(f"\n{i}. 类型: {dup['type']}")
                
                if 'module' in dup:
                    report.append(f"   模块: {dup['module']}")
                
                report.append("   文件:")
                for file_path in dup['files']:
                    report.append(f"     - {file_path}")
                
                report.append(f"   建议: {dup['suggestion']}")
        
        # 建议修复
        report.append("\n## 修复建议")
        report.append("-" * 80)
        
        if self.stats['blueprint_spec_pairs'] > 0:
            report.append(f"1. 归档 {self.stats['blueprint_spec_pairs']} 对BLUEPRINT-SPEC重复文档")
        
        if self.stats['similar_name_pairs'] > 0:
            report.append(f"2. 检查 {self.stats['similar_name_pairs']} 对相似文件名文档")
        
        report.append("\n" + "=" * 80)
        report.append("检测完成")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_report(self, output_file: str):
        """保存报告到文件"""
        report = self.generate_report()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"报告已保存到: {output_file}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python detect_duplicate_documents.py [目录路径]")
        print("示例: python detect_duplicate_documents.py docs/")
        sys.exit(1)
    
    root_dir = sys.argv[1]
    
    if not os.path.exists(root_dir):
        print(f"错误: 目录不存在: {root_dir}")
        sys.exit(1)
    
    # 创建检测器
    detector = DuplicateDocumentDetector(root_dir)
    
    # 扫描目录
    detector.scan_directory()
    
    # 生成报告
    report = detector.generate_report()
    print(report)
    
    # 保存报告
    output_file = f"duplicate_detection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    detector.save_report(output_file)
    
    # 返回退出码
    if detector.duplicates:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
