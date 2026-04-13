#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
INDEX.md自动生成工具

功能：
1. 扫描目录结构
2. 自动生成INDEX.md文件
3. 支持多种文档类型分类
4. 生成标准化的索引格式

使用方法：
    python generate_index.py [目录路径] [--output INDEX.md]

示例：
    python generate_index.py docs/05_IMPLEMENTATION/
    python generate_index.py docs/ --output docs/INDEX.md
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class IndexGenerator:
    """INDEX.md自动生成器"""
    
    def __init__(self, root_dir: str, output_file: Optional[str] = None):
        self.root_dir = Path(root_dir)
        self.output_file = Path(output_file) if output_file else self.root_dir / "INDEX.md"
        self.files = []
        self.directories = []
        
    def scan_directory(self):
        """扫描目录结构"""
        print(f"正在扫描目录: {self.root_dir}")
        
        for item in self.root_dir.iterdir():
            if item.is_file():
                # 跳过隐藏文件和INDEX.md本身
                if item.name.startswith('.') or item.name == 'INDEX.md':
                    continue
                
                # 跳过非文档文件
                if item.suffix.lower() not in ['.md', '.yaml', '.yml', '.json']:
                    continue
                
                self.files.append(item)
            
            elif item.is_dir():
                # 跳过隐藏目录
                if item.name.startswith('.'):
                    continue
                
                self.directories.append(item)
        
        # 排序
        self.files.sort(key=lambda x: x.name)
        self.directories.sort(key=lambda x: x.name)
        
        print(f"扫描完成: 找到 {len(self.files)} 个文件, {len(self.directories)} 个目录")
    
    def extract_file_info(self, file_path: Path) -> Dict:
        """提取文件信息"""
        info = {
            'name': file_path.name,
            'stem': file_path.stem,
            'suffix': file_path.suffix,
            'path': file_path.name,
            'type': self.classify_file_type(file_path),
            'importance': self.estimate_importance(file_path)
        }
        
        return info
    
    def classify_file_type(self, file_path: Path) -> str:
        """分类文件类型"""
        name = file_path.stem.upper()
        
        if 'BLUEPRINT' in name:
            return '蓝图文档'
        elif 'TECHNICAL_SPECIFICATION' in name or 'SPEC' in name:
            return '技术规格'
        elif 'DESIGN' in name:
            return '设计文档'
        elif 'GUIDE' in name or 'MANUAL' in name:
            return '指南手册'
        elif 'README' in name:
            return '说明文档'
        elif 'INDEX' in name:
            return '索引文档'
        else:
            return '其他文档'
    
    def estimate_importance(self, file_path: Path) -> str:
        """估算文档重要性"""
        name = file_path.stem.upper()
        
        if any(keyword in name for keyword in ['README', 'INDEX', 'BLUEPRINT', 'ARCHITECTURE']):
            return '⭐⭐⭐⭐⭐'
        elif any(keyword in name for keyword in ['SPECIFICATION', 'DESIGN', 'GUIDE']):
            return '⭐⭐⭐⭐'
        elif any(keyword in name for keyword in ['MANUAL', 'TUTORIAL']):
            return '⭐⭐⭐'
        else:
            return '⭐⭐'
    
    def generate_index_content(self) -> str:
        """生成INDEX.md内容"""
        content = []
        
        # YAML头部
        content.append("---")
        content.append(f"module_id: INDEX_{self.root_dir.name.upper()}_001")
        content.append("version: 1.0.0")
        content.append("status: Active")
        content.append(f"created_date: {datetime.now().strftime('%Y-%m-%d')}")
        content.append(f"last_updated: {datetime.now().strftime('%Y-%m-%d')}")
        content.append("owner: 文档架构师")
        content.append("standard_type: 专业量化机构目录索引")
        content.append(f"applicable_scope: {self.root_dir.name}目录")
        content.append("compliance_level: 专业标准")
        content.append("parent_document: ../INDEX.md")
        content.append("---")
        content.append("")
        
        # 标题
        content.append(f"# {self.root_dir.name}目录索引")
        content.append("")
        content.append(f"> **版本**: v1.0  ")
        content.append(f"> **最后更新**: {datetime.now().strftime('%Y-%m-%d')}  ")
        content.append(f"> **维护者**: 文档架构师")
        content.append("")
        
        # 目录职责
        content.append("## 🎯 目录职责")
        content.append("")
        content.append(f"本目录存放{self.root_dir.name}相关文档。")
        content.append("")
        
        # 子目录
        if self.directories:
            content.append("## 🗂️ 子目录")
            content.append("")
            content.append("| 目录名称 | 说明 | 文档数量 |")
            content.append("|---------|------|---------|")
            
            for directory in self.directories:
                # 统计目录中的文件数量
                file_count = len([f for f in directory.rglob('*') if f.is_file() and f.suffix.lower() in ['.md', '.yaml', '.yml', '.json']])
                content.append(f"| [{directory.name}/](./{directory.name}/) | {self.get_directory_description(directory.name)} | {file_count} |")
            
            content.append("")
        
        # 核心文档
        if self.files:
            content.append("## 📚 核心文档")
            content.append("")
            content.append("| 文档名称 | 说明 | 重要性 |")
            content.append("|---------|------|--------|")
            
            for file_path in self.files:
                info = self.extract_file_info(file_path)
                content.append(f"| [{info['stem']}](./{info['path']}) | {info['type']} | {info['importance']} |")
            
            content.append("")
        
        # 快速导航
        content.append("## 📖 快速导航")
        content.append("")
        content.append("### 新手入门")
        content.append("")
        content.append("1. 阅读 [README.md](./README.md) - 概述")
        content.append("2. 浏览核心文档 - 了解主要内容")
        content.append("3. 查看子目录 - 深入了解各个模块")
        content.append("")
        
        # 文档统计
        content.append("## 📊 文档统计")
        content.append("")
        content.append("| 统计项 | 数量 |")
        content.append("|--------|------|")
        content.append(f"| **文件总数** | {len(self.files)} |")
        content.append(f"| **目录总数** | {len(self.directories)} |")
        content.append("")
        
        # 相关链接
        content.append("## 🔗 相关链接")
        content.append("")
        content.append("- [系统主索引](../INDEX.md)")
        content.append("")
        
        # 页脚
        content.append("---")
        content.append("")
        content.append(f"**索引版本**: v1.0.0 | **创建日期**: {datetime.now().strftime('%Y-%m-%d')} | **维护者**: 文档架构师")
        
        return "\n".join(content)
    
    def get_directory_description(self, dir_name: str) -> str:
        """获取目录描述"""
        descriptions = {
            '01_BLUEPRINTS': '蓝图文档',
            '02_IMPLEMENTATION_GUIDES': '实施指南',
            '03_OPERATION_MANUALS': '运维手册',
            '04_CONFIG_TEMPLATES': '配置模板',
            '05_PROGRESS_TRACKING': '进度跟踪',
            '06_CHECKLISTS': '检查清单',
            'design': '设计文档',
            'database': '数据库设计',
            'web_interface': 'Web界面设计',
            'data_consistency': '数据一致性设计',
            'trading_costs': '交易成本设计',
            'a_stock_rules': 'A股规则设计'
        }
        
        return descriptions.get(dir_name, '其他文档')
    
    def save_index(self):
        """保存INDEX.md文件"""
        content = self.generate_index_content()
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"INDEX.md已生成: {self.output_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='INDEX.md自动生成工具')
    parser.add_argument('directory', help='要生成索引的目录路径')
    parser.add_argument('--output', '-o', help='输出文件路径（默认为目录下的INDEX.md）')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"错误: 目录不存在: {args.directory}")
        sys.exit(1)
    
    # 创建生成器
    generator = IndexGenerator(args.directory, args.output)
    
    # 扫描目录
    generator.scan_directory()
    
    # 生成索引
    generator.save_index()
    
    print("索引生成完成！")


if __name__ == '__main__':
    main()
