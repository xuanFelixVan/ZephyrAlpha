#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
YAML字段补充修复脚本
为舆情分析层所有文件补充缺失的YAML字段
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class YAMLFieldFixer:
    """YAML字段修复器"""
    
    def __init__(self):
        self.fixed_count = 0
        self.total_count = 0
        self.required_fields = {
            'module_id': None,
            'version': '1.0.0',
            'status': 'Active',
            'created_date': '2026-04-07',
            'last_updated': '2026-04-07',
            'owner': '实施团队',
            'responsibility': None
        }
    
    def generate_module_id(self, file_name: str) -> str:
        """根据文件名生成module_id"""
        name_without_ext = file_name.replace('.md', '')
        module_id = name_without_ext.upper()
        return f"{module_id}_001"
    
    def generate_responsibility(self, file_name: str) -> List[str]:
        """根据文件名生成职责描述"""
        name_upper = file_name.upper()
        
        if 'INDEX' in name_upper:
            return ['AI工作流与舆情分析综合层索引管理']
        
        elif 'BLUEPRINT' in name_upper:
            return [f'{file_name.replace("_BLUEPRINT.md", "").replace("_", " ")} module blueprint design']
        
        elif 'TECHNICAL_SPECIFICATION' in name_upper:
            return [f'{file_name.replace("_TECHNICAL_SPECIFICATION.md", "").replace("_", " ")} technical specification']
        
        elif 'REPORT' in name_upper:
            return [f'{file_name.replace("_REPORT.md", "").replace("_", " ")} report']
        
        else:
            return [f'{file_name.replace(".md", "").replace("_", " ")} document']
    
    def fix_yaml_fields(self, file_path: Path) -> bool:
        """修复单个文件的YAML字段"""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            content = content.lstrip('\ufeff')
            
            yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if not yaml_match:
                return False
            
            yaml_content = yaml_match.group(1)
            yaml_lines = yaml_content.split('\n')
            
            existing_fields = {}
            for line in yaml_lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    existing_fields[key.strip()] = value.strip()
            
            new_yaml_lines = []
            added_fields = []
            
            for field, default_value in self.required_fields.items():
                if field in existing_fields:
                    new_yaml_lines.append(f"{field}: {existing_fields[field]}")
                else:
                    if default_value is None:
                        if field == 'module_id':
                            generated_value = self.generate_module_id(file_path.name)
                            new_yaml_lines.append(f"{field}: {generated_value}")
                        elif field == 'responsibility':
                            responsibilities = self.generate_responsibility(file_path.name)
                            new_yaml_lines.append(f"{field}:")
                            for resp in responsibilities:
                                new_yaml_lines.append(f"  - {resp}")
                    else:
                        new_yaml_lines.append(f"{field}: {default_value}")
                    added_fields.append(field)
            
            for field, value in existing_fields.items():
                if field not in self.required_fields:
                    new_yaml_lines.append(f"{field}: {value}")
            
            new_yaml_content = '\n'.join(new_yaml_lines)
            
            new_content = '---\n' + new_yaml_content + '\n---' + content[yaml_match.end():]
            
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                f.write(new_content)
            
            if added_fields:
                print(f"  [OK] {file_path.name}: added {len(added_fields)} fields ({', '.join(added_fields)})")
                return True
            else:
                return False
            
        except Exception as e:
            print(f"  [ERROR] fix failed: {file_path.name} - {e}")
            return False
    
    def run(self, docs_dir: Path):
        """执行修复"""
        print("=== Starting YAML Field Fix ===\n")
        
        md_files = list(docs_dir.glob("**/*.md"))
        
        for md_file in md_files:
            if any(keyword in str(md_file) for keyword in ['06_ARCHIVE', '09_ARCHIVE', '99_ARCHIVE', 'archive']):
                continue
            
            self.total_count += 1
            
            if self.fix_yaml_fields(md_file):
                self.fixed_count += 1
        
        print(f"\n=== Fix Complete ===")
        print(f"Total files: {self.total_count}")
        print(f"Fixed files: {self.fixed_count}")
        if self.total_count > 0:
            print(f"Fix rate: {self.fixed_count/self.total_count*100:.2f}%")

def main():
    """主函数"""
    docs_dir = Path("D:/ZephyrAlpha/docs/10_AI_WORKFLOW")
    fixer = YAMLFieldFixer()
    fixer.run(docs_dir)

if __name__ == "__main__":
    main()
