"""
修复Layer 8文档双YAML头部问题 v2
"""

import re
from pathlib import Path
from datetime import datetime

LAYER8_DIR = Path("docs/08_human_ai_interface")


def fix_double_yaml_v2():
    """修复双YAML头部 v2"""
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
                
                merged_yaml = merge_yamls(first_yaml, second_yaml)
                
                new_content = f"---\n{merged_yaml}\n---\n" + rest_content
                
                with open(filepath, 'w', encoding='utf-8-sig') as f:
                    f.write(new_content)
                
                print(f"✅ 修复(模式1): {filepath.name}")
                stats['fixed'] += 1
                continue
            
            pattern2 = r'^---\s*\n(.*?compliance_level:[^\n]*)---\s*\n\s*\ufeff?---\s*\n(.*?)\n---\s*\n'
            match2 = re.match(pattern2, content, re.DOTALL)
            
            if match2:
                first_yaml = match2.group(1)
                second_yaml = match2.group(2)
                rest_content = content[match2.end():]
                
                merged_yaml = merge_yamls(first_yaml, second_yaml)
                
                new_content = f"---\n{merged_yaml}\n---\n" + rest_content
                
                with open(filepath, 'w', encoding='utf-8-sig') as f:
                    f.write(new_content)
                
                print(f"✅ 修复(模式2): {filepath.name}")
                stats['fixed'] += 1
                continue
            
            if '---' in content[:500]:
                first_end = content.find('---', 3)
                if first_end > 0:
                    after_first = content[first_end+3:].lstrip()
                    if after_first.startswith('---') or after_first.startswith('\ufeff---'):
                        second_end = after_first.find('\n---', 10)
                        if second_end > 0:
                            first_yaml = content[4:first_end].strip()
                            second_yaml_start = after_first.find('\n') + 1 if after_first.startswith('\ufeff---') else 4
                            second_yaml = after_first[second_yaml_start:second_end].strip()
                            rest_content = after_first[second_end+4:].lstrip()
                            
                            merged_yaml = merge_yamls(first_yaml, second_yaml)
                            
                            new_content = f"---\n{merged_yaml}\n---\n" + rest_content
                            
                            with open(filepath, 'w', encoding='utf-8-sig') as f:
                                f.write(new_content)
                            
                            print(f"✅ 修复(模式3): {filepath.name}")
                            stats['fixed'] += 1
        
        except Exception as e:
            print(f"❌ 错误 {filepath.name}: {e}")
            stats['errors'].append(f"{filepath.name}: {e}")
    
    print(f"\n总计修复: {stats['fixed']} 个文件")
    return stats


def merge_yamls(first: str, second: str) -> str:
    """合并两个YAML头部，保留更完整的信息"""
    lines = []
    seen_keys = set()
    
    for line in second.split('\n'):
        if ':' in line and not line.startswith(' '):
            key = line.split(':')[0].strip()
            seen_keys.add(key)
        lines.append(line)
    
    for line in first.split('\n'):
        if ':' in line and not line.startswith(' '):
            key = line.split(':')[0].strip()
            if key not in seen_keys:
                lines.append(line)
        elif line.startswith(' '):
            lines.append(line)
    
    result = '\n'.join(lines)
    result = re.sub(r'layer:\s*Layer\s*\d+\s*\([^)]+\)', 'layer: Layer 8 (人机交互层)', result)
    
    return result


if __name__ == "__main__":
    fix_double_yaml_v2()
