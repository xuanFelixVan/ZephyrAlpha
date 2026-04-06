"""
修复Layer 8文档双YAML头部问题
"""

import re
from pathlib import Path
from datetime import datetime

LAYER8_DIR = Path("docs/08_human_ai_interface")


def fix_double_yaml():
    """修复双YAML头部"""
    stats = {"fixed": 0, "errors": []}
    
    md_files = list(LAYER8_DIR.glob("**/*_BLUEPRINT.md"))
    
    for filepath in md_files:
        try:
            encodings = ['utf-8-sig', 'utf-8', 'gbk']
            content = None
            for encoding in encodings:
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except:
                    continue
            
            if not content:
                continue
            
            pattern = r'^---\s*\n(.*?)\n---\s*\n\s*\ufeff?---\s*\n(.*?)\n---\s*\n'
            match = re.match(pattern, content, re.DOTALL)
            
            if match:
                first_yaml = match.group(1)
                second_yaml = match.group(2)
                rest_content = content[match.end():]
                
                merged_yaml = first_yaml + "\n" + second_yaml
                merged_yaml = re.sub(r'layer:\s*Layer\s*\d+\s*\([^)]+\)', 'layer: Layer 8 (人机交互层)', merged_yaml)
                
                new_content = f"---\n{merged_yaml}\n---\n" + rest_content
                
                with open(filepath, 'w', encoding='utf-8-sig') as f:
                    f.write(new_content)
                
                print(f"✅ 修复: {filepath.name}")
                stats['fixed'] += 1
            else:
                pattern2 = r'^---\s*\n(.*?)\n---\s*---\s*\n(.*?)\n---\s*\n'
                match2 = re.match(pattern2, content, re.DOTALL)
                if match2:
                    first_yaml = match2.group(1)
                    second_yaml = match2.group(2)
                    rest_content = content[match2.end():]
                    
                    merged_yaml = first_yaml + "\n" + second_yaml
                    merged_yaml = re.sub(r'layer:\s*Layer\s*\d+\s*\([^)]+\)', 'layer: Layer 8 (人机交互层)', merged_yaml)
                    
                    new_content = f"---\n{merged_yaml}\n---\n" + rest_content
                    
                    with open(filepath, 'w', encoding='utf-8-sig') as f:
                        f.write(new_content)
                    
                    print(f"✅ 修复: {filepath.name}")
                    stats['fixed'] += 1
        
        except Exception as e:
            print(f"❌ 错误 {filepath.name}: {e}")
            stats['errors'].append(f"{filepath.name}: {e}")
    
    print(f"\n总计修复: {stats['fixed']} 个文件")
    return stats


if __name__ == "__main__":
    fix_double_yaml()
