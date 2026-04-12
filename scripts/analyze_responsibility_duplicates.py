#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
职责描述重复分析脚本
分析舆情分析层所有文件的职责描述，找出重复的职责描述
"""

import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

class ResponsibilityAnalyzer:
    """职责描述分析器"""
    
    def __init__(self):
        self.responsibility_map = defaultdict(list)
        self.total_count = 0
    
    def extract_responsibility(self, file_path: Path) -> List[str]:
        """提取文件的职责描述"""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            content = content.lstrip('\ufeff')
            
            yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if not yaml_match:
                return []
            
            yaml_content = yaml_match.group(1)
            
            responsibility_match = re.search(r'responsibility:\s*\n((?:  - .*\n)+)', yaml_content)
            if not responsibility_match:
                return []
            
            responsibility_text = responsibility_match.group(1)
            responsibilities = []
            for line in responsibility_text.split('\n'):
                line = line.strip()
                if line.startswith('- '):
                    responsibilities.append(line[2:])
            
            return responsibilities
            
        except Exception as e:
            print(f"  [ERROR] 提取失败: {file_path.name} - {e}")
            return []
    
    def analyze(self, docs_dir: Path) -> Dict[str, List[str]]:
        """分析所有文件的职责描述"""
        print("=== 开始分析职责描述重复 ===\n")
        
        md_files = list(docs_dir.glob("**/*.md"))
        
        for md_file in md_files:
            if any(keyword in str(md_file) for keyword in ['06_ARCHIVE', '09_ARCHIVE', '99_ARCHIVE', 'archive']):
                continue
            
            self.total_count += 1
            
            responsibilities = self.extract_responsibility(md_file)
            
            for resp in responsibilities:
                self.responsibility_map[resp].append(md_file.name)
        
        print(f"总文件数: {self.total_count}")
        print(f"唯一职责描述数: {len(self.responsibility_map)}")
        
        duplicates = {k: v for k, v in self.responsibility_map.items() if len(v) > 1}
        
        print(f"重复的职责描述数: {len(duplicates)}")
        
        print("\n=== 重复的职责描述详情 ===\n")
        
        sorted_duplicates = sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)
        
        for resp, files in sorted_duplicates:
            print(f"职责描述: {resp}")
            print(f"  出现次数: {len(files)}")
            print(f"  文件列表:")
            for file in files:
                print(f"    - {file}")
            print()
        
        return duplicates

def main():
    """主函数"""
    docs_dir = Path("D:/ZephyrAlpha/docs/10_AI_WORKFLOW")
    analyzer = ResponsibilityAnalyzer()
    duplicates = analyzer.analyze(docs_dir)
    
    print(f"\n=== 分析完成 ===")
    print(f"需要优化的文件数: {sum(len(files) for files in duplicates.values())}")

if __name__ == "__main__":
    main()
