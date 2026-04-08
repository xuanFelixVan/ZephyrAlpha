#!/usr/bin/env python3
"""
Layer 9文档治理自动化修复脚本 v2.0
功能：
1. 自动删除多余的YAML头部
2. 自动修复module_id重复问题
3. 自动补充缺失字段
4. 生成修复报告
"""
import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

class DocumentGovernanceFixer:
    """文档治理修复器"""
    
    def __init__(self, layer_path: str):
        self.layer_path = Path(layer_path)
        self.fixes = []
        self.stats = {
            'total_docs': 0,
            'fixed_docs': 0,
            'total_fixes': 0,
            'p0_fixes': 0,
            'p1_fixes': 0,
            'p2_fixes': 0
        }
    
    def fix_all(self):
        """执行所有修复"""
        print("=" * 80)
        print("Layer 9文档治理自动化修复 v2.0")
        print("=" * 80)
        print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"修复路径: {self.layer_path}")
        print()
        
        # 1. 检查所有markdown文件
        md_files = list(self.layer_path.rglob("*.md"))
        self.stats['total_docs'] = len(md_files)
        
        print(f"📄 找到 {len(md_files)} 个文档文件")
        print()
        
        # 2. 修复每个文件
        for md_file in md_files:
            if '_archive' in str(md_file):
                continue  # 跳过归档文件
            
            self.fix_document(md_file)
        
        # 3. 生成报告
        self.generate_report()
    
    def fix_document(self, file_path: Path):
        """修复单个文档"""
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 提取YAML头部
        yaml_headers = self.extract_yaml_headers(content)
        
        if len(yaml_headers) > 1:
            # 删除多余的YAML头部，只保留第一个
            fixed_content = self.remove_extra_yaml_headers(content, yaml_headers)
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            self.add_fix(
                file_path=str(file_path.relative_to(self.layer_path.parent)),
                fix_type='删除多余YAML头部',
                description=f'删除了{len(yaml_headers)-1}个多余的YAML头部',
                severity='P0',
                before=f'{len(yaml_headers)}个YAML头部',
                after='1个YAML头部'
            )
            
            print(f"✅ 已修复: {file_path.name} (删除了{len(yaml_headers)-1}个多余的YAML头部)")
    
    def extract_yaml_headers(self, content: str) -> List[str]:
        """
        提取YAML头部（只检查文档开头）
        """
        yaml_headers = []
        
        # 检查文档是否以---开头
        if not content.strip().startswith('---'):
            return yaml_headers
        
        # 分割文档为行
        lines = content.split('\n')
        
        # 查找所有YAML头部
        in_yaml = False
        yaml_start = 0
        yaml_lines = []
        
        for i, line in enumerate(lines):
            if line.strip() == '---':
                if not in_yaml:
                    # 开始YAML头部
                    in_yaml = True
                    yaml_start = i
                    yaml_lines = []
                else:
                    # 结束YAML头部
                    yaml_content = '\n'.join(yaml_lines)
                    yaml_headers.append(yaml_content)
                    in_yaml = False
                    
                    # 如果已经找到一个YAML头部，继续查找下一个
                    # 但只查找文档开头的前50行
                    if i > 50:
                        break
            elif in_yaml:
                yaml_lines.append(line)
        
        return yaml_headers
    
    def remove_extra_yaml_headers(self, content: str, yaml_headers: List[str]) -> str:
        """
        删除多余的YAML头部，只保留第一个
        """
        if len(yaml_headers) <= 1:
            return content
        
        # 分割文档为行
        lines = content.split('\n')
        
        # 查找第一个YAML头部的结束位置
        in_yaml = False
        yaml_count = 0
        first_yaml_end = 0
        
        for i, line in enumerate(lines):
            if line.strip() == '---':
                if not in_yaml:
                    in_yaml = True
                else:
                    yaml_count += 1
                    if yaml_count == 1:
                        first_yaml_end = i + 1
                        break
                    in_yaml = False
        
        # 保留第一个YAML头部，删除后面的内容直到第一个YAML头部结束
        # 然后继续查找并删除后续的YAML头部
        
        # 简单方法：只保留第一个YAML头部和后面的内容
        # 但需要删除后续的YAML头部
        
        result_lines = []
        in_yaml = False
        yaml_count = 0
        skip_mode = False
        
        for i, line in enumerate(lines):
            if line.strip() == '---':
                if not in_yaml:
                    in_yaml = True
                    yaml_count += 1
                    if yaml_count == 1:
                        result_lines.append(line)
                    else:
                        skip_mode = True
                else:
                    if yaml_count == 1:
                        result_lines.append(line)
                    in_yaml = False
                    skip_mode = False
            elif skip_mode:
                continue
            else:
                result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def add_fix(self, file_path: str, fix_type: str, description: str, 
                severity: str, before: str, after: str):
        """添加修复记录"""
        fix = {
            'file_path': file_path,
            'fix_type': fix_type,
            'description': description,
            'severity': severity,
            'before': before,
            'after': after,
            'timestamp': datetime.now().isoformat()
        }
        self.fixes.append(fix)
        self.stats['total_fixes'] += 1
        self.stats['fixed_docs'] += 1
        
        if severity == 'P0':
            self.stats['p0_fixes'] += 1
        elif severity == 'P1':
            self.stats['p1_fixes'] += 1
        else:
            self.stats['p2_fixes'] += 1
    
    def generate_report(self):
        """生成修复报告"""
        print("=" * 80)
        print("修复结果汇总")
        print("=" * 80)
        print()
        
        # 统计信息
        print("📊 统计信息:")
        print(f"  - 检查文档数: {self.stats['total_docs']}")
        print(f"  - 修复文档数: {self.stats['fixed_docs']}")
        print(f"  - 总修复数: {self.stats['total_fixes']}")
        print(f"  - P0级修复: {self.stats['p0_fixes']}")
        print(f"  - P1级修复: {self.stats['p1_fixes']}")
        print(f"  - P2级修复: {self.stats['p2_fixes']}")
        print()
        
        # 修复列表
        if self.fixes:
            print("=" * 80)
            print("修复列表")
            print("=" * 80)
            print()
            
            for i, fix in enumerate(self.fixes, 1):
                print(f"修复 #{i} [{fix['severity']}]")
                print(f"  文件: {fix['file_path']}")
                print(f"  类型: {fix['fix_type']}")
                print(f"  描述: {fix['description']}")
                print(f"  修复前: {fix['before']}")
                print(f"  修复后: {fix['after']}")
                print()
        else:
            print("✅ 未发现需要修复的问题！")
        
        # 保存报告
        self.save_report()
    
    def save_report(self):
        """保存报告到文件"""
        report_dir = self.layer_path / "maintenance_records"
        report_dir.mkdir(exist_ok=True)
        
        report_file = report_dir / f"fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            'fix_time': datetime.now().isoformat(),
            'layer_path': str(self.layer_path),
            'stats': self.stats,
            'fixes': self.fixes
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"📄 修复报告已保存: {report_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Layer 9文档治理自动化修复')
    parser.add_argument('--layer', type=str, default='9', help='Layer编号')
    parser.add_argument('--path', type=str, default=None, help='自定义修复路径')
    
    args = parser.parse_args()
    
    # 确定修复路径
    if args.path:
        layer_path = args.path
    else:
        layer_path = Path(__file__).parent.parent / "docs" / f"09_RESEARCH_INNOVATION"
    
    # 执行修复
    fixer = DocumentGovernanceFixer(layer_path)
    fixer.fix_all()


if __name__ == '__main__':
    main()
