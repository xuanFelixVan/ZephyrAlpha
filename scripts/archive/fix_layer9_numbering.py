#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
Layer 9蓝图编号重复修复脚本
功能：修复BLUEPRINT.md中的编号重复问题
"""
import re
from pathlib import Path
from datetime import datetime

class Layer9NumberingFixer:
    """Layer 9蓝图编号修复器"""
    
    def __init__(self):
        self.blueprint_path = Path("docs/09_RESEARCH_INNOVATION/BLUEPRINT.md")
        self.fix_count = 0
        self.fix_log = []
        
        # 编号映射：旧编号 -> 新编号
        self.numbering_map = {
            # 第二次出现的模块重新编号
            ('2.39', '研究模型解释系统'): '2.49',
            ('2.41', '研究路线图规划系统'): '2.50',
            ('2.43', '跨领域创新发现系统'): '2.52',
            ('2.45', '研究风险管理系统'): '2.54',
            ('2.47', '研究知识图谱系统'): '2.56',
        }
    
    def fix_all(self):
        """修复所有编号重复问题"""
        print("=" * 80)
        print("Layer 9蓝图编号重复修复")
        print("=" * 80)
        print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"修复文件: {self.blueprint_path}")
        print()
        
        # 读取文件
        with open(self.blueprint_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # 记录每个编号出现的次数
        numbering_count = {}
        
        # 第一次扫描：统计每个编号出现的次数
        pattern = r'### (2\.\d+) (.+?) ⭐'
        matches = re.findall(pattern, content)
        
        for number, title in matches:
            key = (number, title)
            if number not in numbering_count:
                numbering_count[number] = []
            numbering_count[number].append(title)
        
        # 输出重复编号
        print("发现的重复编号：")
        for number, titles in numbering_count.items():
            if len(titles) > 1:
                print(f"  {number}: {titles}")
        print()
        
        # 第二次扫描：修复重复编号
        # 我们需要找到第二次出现的编号并替换
        lines = content.split('\n')
        numbering_occurrence = {}  # 记录每个编号出现的次数
        
        for i, line in enumerate(lines):
            match = re.match(r'### (2\.\d+) (.+?) ⭐', line)
            if match:
                number = match.group(1)
                title = match.group(2)
                
                # 记录这个编号出现的次数
                if number not in numbering_occurrence:
                    numbering_occurrence[number] = 0
                numbering_occurrence[number] += 1
                
                # 如果是第二次出现，需要重新编号
                if numbering_occurrence[number] > 1:
                    key = (number, title)
                    if key in self.numbering_map:
                        new_number = self.numbering_map[key]
                        old_line = line
                        new_line = line.replace(f'### {number}', f'### {new_number}')
                        lines[i] = new_line
                        
                        self.fix_count += 1
                        self.fix_log.append({
                            'line': i + 1,
                            'old_number': number,
                            'new_number': new_number,
                            'title': title,
                            'old_line': old_line,
                            'new_line': new_line
                        })
                        
                        print(f"✅ 第{i+1}行: {number} → {new_number} ({title})")
        
        # 写回文件
        new_content = '\n'.join(lines)
        with open(self.blueprint_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # 输出修复结果
        print()
        print("=" * 80)
        print("修复结果汇总")
        print("=" * 80)
        print(f"修复编号数: {self.fix_count}")
        print()
        
        # 保存修复日志
        self.save_fix_log()
    
    def save_fix_log(self):
        """保存修复日志"""
        import json
        
        log_path = Path("docs/09_AUDIT/STATE/layer9_numbering_fix_log.json")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump({
                'fix_time': datetime.now().isoformat(),
                'fix_count': self.fix_count,
                'fix_log': self.fix_log
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 修复日志已保存: {log_path}")

if __name__ == "__main__":
    fixer = Layer9NumberingFixer()
    fixer.fix_all()
