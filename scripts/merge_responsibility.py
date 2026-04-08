#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
职责合并修复脚本
为舆情分析层文件合并职责，确保每个文件不超过3个职责
"""

import re
from pathlib import Path
from typing import List

class ResponsibilityMerger:
    """职责合并器"""
    
    def __init__(self):
        self.max_responsibilities = 3
        self.merged_count = 0
        self.total_count = 0
    
    def merge_responsibilities(self, responsibilities: List[str]) -> List[str]:
        """合并职责描述"""
        if len(responsibilities) <= self.max_responsibilities:
            return responsibilities
        
        merged = []
        
        for i in range(0, len(responsibilities), 2):
            if i + 1 < len(responsibilities):
                merged_resp = f"{responsibilities[i]} and {responsibilities[i+1]}"
                merged.append(merged_resp)
            else:
                merged.append(responsibilities[i])
        
        if len(merged) > self.max_responsibilities:
            return self.merge_responsibilities(merged)
        
        return merged
    
    def merge_file_responsibilities(self, file_path: Path) -> bool:
        """合并单个文件的职责"""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            content = content.lstrip('\ufeff')
            
            yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if not yaml_match:
                return False
            
            yaml_content = yaml_match.group(1)
            
            responsibility_match = re.search(r'responsibility:\s*\n((?:  - .*\n)+)', yaml_content)
            if not responsibility_match:
                return False
            
            responsibility_text = responsibility_match.group(1)
            responsibilities = []
            
            for line in responsibility_text.split('\n'):
                line = line.strip()
                if line.startswith('- '):
                    responsibilities.append(line[2:])
            
            if len(responsibilities) <= self.max_responsibilities:
                return False
            
            merged_responsibilities = self.merge_responsibilities(responsibilities)
            
            new_responsibility_str = '\n'.join([f'  - {r}' for r in merged_responsibilities])
            
            new_yaml = re.sub(
                r'responsibility:\s*\n(  - .*\n)+',
                f'responsibility:\n{new_responsibility_str}\n',
                yaml_content
            )
            
            new_content = content.replace(yaml_content, new_yaml, 1)
            
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                f.write(new_content)
            
            return True
            
        except Exception as e:
            print(f"  [ERROR] merge failed: {file_path.name} - {e}")
            return False
    
    def run(self, docs_dir: Path):
        """执行合并"""
        print("=== Starting Responsibility Merge ===\n")
        
        md_files = list(docs_dir.glob("**/*.md"))
        
        for md_file in md_files:
            if any(keyword in str(md_file) for keyword in ['06_ARCHIVE', '09_ARCHIVE', '99_ARCHIVE', 'archive']):
                continue
            
            self.total_count += 1
            
            if self.merge_file_responsibilities(md_file):
                self.merged_count += 1
                print(f"  [OK] merged: {md_file.name}")
        
        print(f"\n=== Merge Complete ===")
        print(f"Total files: {self.total_count}")
        print(f"Merged files: {self.merged_count}")
        if self.total_count > 0:
            print(f"Merge rate: {self.merged_count/self.total_count*100:.2f}%")

def main():
    """主函数"""
    docs_dir = Path("D:/ZephyrAlpha/docs/10_AI_WORKFLOW")
    merger = ResponsibilityMerger()
    merger.run(docs_dir)

if __name__ == "__main__":
    main()
