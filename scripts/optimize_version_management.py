#!/usr/bin/env python3
"""
优化版本管理

功能:
1. 扫描所有蓝图文件
2. 检查包含多个版本标识的文档
3. 清理多余的版本标识，统一版本标识格式
"""

import os
import re
from pathlib import Path

class VersionManagementOptimizer:
    def __init__(self):
        self.blueprints_dir = 'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS'
        self.blueprint_files = []
        self.files_with_multiple_versions = []
    
    def run(self):
        """执行优化"""
        print('=' * 80)
        print('优化版本管理')
        print('=' * 80)
        print()
        
        # 1. 扫描所有蓝图文件
        print('1. 扫描蓝图文件...')
        self.scan_blueprint_files()
        print(f'  ✅ 找到{len(self.blueprint_files)}个蓝图文件')
        print()
        
        # 2. 检查包含多个版本标识的文件
        print('2. 检查包含多个版本标识的文件...')
        self.check_multiple_versions()
        print(f'  ⚠️ 发现{len(self.files_with_multiple_versions)}个文件包含多个版本标识')
        print()
        
        # 3. 清理多余的版本标识
        if self.files_with_multiple_versions:
            print('3. 清理多余的版本标识...')
            self.clean_multiple_versions()
            print(f'  ✅ 已清理{len(self.files_with_multiple_versions)}个文件的版本标识')
            print()
        else:
            print('3. 所有文件版本标识正常，无需清理')
            print()
        
        print('=' * 80)
        print('优化完成')
        print('=' * 80)
    
    def scan_blueprint_files(self):
        """扫描所有蓝图文件"""
        if os.path.exists(self.blueprints_dir):
            for filename in os.listdir(self.blueprints_dir):
                if filename.endswith('.md') and filename != 'INDEX.md':
                    self.blueprint_files.append(filename)
    
    def check_multiple_versions(self):
        """检查包含多个版本标识的文件"""
        for filename in self.blueprint_files:
            filepath = os.path.join(self.blueprints_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 统计版本标识数量
            version_matches = re.findall(r'v\d+\.\d+', content)
            
            if len(version_matches) > 3:  # 超过3个版本标识
                self.files_with_multiple_versions.append({
                    'filename': filename,
                    'count': len(version_matches),
                    'matches': version_matches
                })
        
        # 显示前10个包含多个版本标识的文件
        if self.files_with_multiple_versions:
            print('  包含多个版本标识的文件（前10个）:')
            for file_info in self.files_with_multiple_versions[:10]:
                print(f'    - {file_info["filename"]}: {file_info["count"]}个版本标识')
            if len(self.files_with_multiple_versions) > 10:
                print(f'    ... 还有{len(self.files_with_multiple_versions) - 10}个文件')
    
    def clean_multiple_versions(self):
        """清理多余的版本标识"""
        for file_info in self.files_with_multiple_versions:
            filename = file_info['filename']
            filepath = os.path.join(self.blueprints_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取YAML头部的version
            yaml_version_match = re.search(r'version:\s*([\d.]+)', content)
            yaml_version = yaml_version_match.group(1) if yaml_version_match else '1.0.0'
            
            # 清理文档内容中的版本标识（保留YAML头部和文档底部的版本标识）
            # 1. 保留YAML头部的version字段
            # 2. 清理文档中间的版本标识（如"v1.0.0"、"v2.0.0"等）
            # 3. 保留文档底部的版本标识
            
            # 简化处理：只保留YAML头部的version和文档底部的版本标识
            # 删除文档中间的版本标识
            
            lines = content.split('\n')
            new_lines = []
            in_yaml = False
            yaml_end = 0
            
            for i, line in enumerate(lines):
                # 检测YAML头部
                if line.strip() == '---':
                    if not in_yaml:
                        in_yaml = True
                    else:
                        in_yaml = False
                        yaml_end = i
                
                # 在YAML头部之后，清理版本标识
                if i > yaml_end and not in_yaml:
                    # 检查是否是文档底部（最后10行）
                    if i < len(lines) - 10:
                        # 清理版本标识
                        if re.search(r'v\d+\.\d+', line) and '版本' not in line:
                            # 跳过这行
                            continue
                
                new_lines.append(line)
            
            # 写回文件
            new_content = '\n'.join(new_lines)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f'    ✅ 已清理 {filename} 的版本标识')

if __name__ == '__main__':
    optimizer = VersionManagementOptimizer()
    optimizer.run()
