# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
P2级文档质量问题修复脚本
用途：修复编码问题、补充文档治理章节、清理过多空行
创建时间：2026-04-07
"""

import re
from pathlib import Path
from typing import List, Tuple

BLUEPRINTS_DIR = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS")


def read_document(filepath: Path) -> Tuple[str, str]:
    """读取文档内容，返回内容和使用的编码"""
    encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'latin-1']
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read(), encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    return "", 'utf-8'


def fix_encoding_issues(content: str) -> str:
    """修复编码问题"""
    # 替换常见的乱码字符
    replacements = {
        '\ufffd': '',
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    return content


def remove_excessive_blank_lines(content: str) -> str:
    """移除过多的空行"""
    # 将连续3个以上的空行替换为2个空行
    content = re.sub(r'\n\n\n+', '\n\n', content)
    return content


def has_governance_section(content: str) -> bool:
    """检查是否已有文档治理章节"""
    return '文档治理' in content or '## 文档治理' in content


def get_last_section_number(content: str) -> int:
    """获取最后一个章节编号"""
    sections = re.findall(r'^##\s+(\d+)\.', content, re.MULTILINE)
    if sections:
        return int(sections[-1])
    return 0


def extract_yaml_header(content: str) -> dict:
    """提取YAML头部"""
    yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not yaml_match:
        return {}
    
    yaml_content = yaml_match.group(1)
    yaml_dict = {}
    
    for line in yaml_content.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            yaml_dict[key.strip()] = value.strip().strip('"\'')
    
    return yaml_dict


def get_layer_info(layer_str: str) -> Tuple[int, str]:
    """从layer字段提取层级编号和名称"""
    if not layer_str:
        return (0, "系统架构")
    
    match = re.search(r'Layer\s*(\d+)', layer_str, re.IGNORECASE)
    if match:
        layer_num = int(match.group(1))
        
        cn_match = re.search(r'Layer\s*\d+\s*\(([^)]+)\)', layer_str)
        layer_name = cn_match.group(1) if cn_match else layer_str
        
        return (layer_num, layer_name)
    
    return (0, layer_str)


def get_module_name_from_id(module_id: str) -> str:
    """从module_id提取模块名称"""
    parts = module_id.split('_')
    if len(parts) > 1:
        return '_'.join(parts[:-1])
    return module_id


def get_module_index(module_id: str) -> str:
    """从module_id提取模块索引"""
    parts = module_id.split('_')
    if parts:
        return parts[-1]
    return '001'


def get_responsibility_from_scope(scope: str) -> str:
    """从applicable_scope提取职责"""
    if not scope:
        return "系统核心模块"
    
    if 'Layer' in scope:
        return scope
    
    return scope


GOVERNANCE_TEMPLATE = """

## {section_num}. 文档治理

### {section_num}.1 文档索引

**本文档在系统中的位置**:
- **所属层级**: Layer {layer_num} ({layer_name})
- **模块索引**: {module_index}
- **模块名称**: {module_name}
- **文档路径**: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/{blueprint_filename}

### {section_num}.2 版本管理

**版本历史**:
- v1.0.0 ({created_date}): 初始版本

### {section_num}.3 维护责任

**文档维护**:
- **责任模块**: {module_name}
- **维护周期**: 每季度审查
- **变更流程**: 提交变更申请 → 技术评审 → 更新文档

---

**蓝图版本**: v1.0.0 | **创建日期**: {created_date} | **状态**: Active
"""


def add_governance_section(content: str, yaml_header: dict) -> str:
    """添加文档治理章节"""
    if has_governance_section(content):
        return content
    
    last_section = get_last_section_number(content)
    next_section = last_section + 1
    
    layer_str = yaml_header.get('layer', 'Layer 0 (系统架构)')
    layer_num, layer_name = get_layer_info(layer_str)
    
    module_id = yaml_header.get('module_id', 'UNKNOWN_001')
    module_name = get_module_name_from_id(module_id)
    module_index = get_module_index(module_id)
    
    responsibility = get_responsibility_from_scope(yaml_header.get('applicable_scope', ''))
    created_date = yaml_header.get('created_date', '2026-04-07')
    
    governance_section = GOVERNANCE_TEMPLATE.format(
        section_num=next_section,
        layer_num=layer_num,
        layer_name=layer_name,
        module_index=module_index,
        module_name=module_name,
        blueprint_filename="",
        responsibility=responsibility,
        created_date=created_date
    )
    
    # 移除末尾的---分隔符（如果存在）
    content = re.sub(r'\n---\s*$', '', content.rstrip())
    
    return content + governance_section


def fix_document_quality():
    """修复文档质量问题"""
    print("="*80)
    print("P2级文档质量问题修复")
    print("="*80)
    
    stats = {
        "encoding_fixed": 0,
        "governance_added": 0,
        "blank_lines_cleaned": 0,
        "errors": 0
    }
    
    for filepath in BLUEPRINTS_DIR.glob("*.md"):
        if filepath.name == "INDEX.md":
            continue
        
        try:
            content, encoding = read_document(filepath)
            if not content:
                continue
            
            original_content = content
            yaml_header = extract_yaml_header(content)
            
            # 1. 修复编码问题（U+FFFD 替换字符）
            if '\ufffd' in content:
                content = fix_encoding_issues(content)
                stats["encoding_fixed"] += 1
                print(f"✅ 修复编码问题: {filepath.name}")
            
            # 2. 补充文档治理章节
            if not has_governance_section(content):
                content = add_governance_section(content, yaml_header)
                stats["governance_added"] += 1
                print(f"✅ 补充文档治理章节: {filepath.name}")
            
            # 3. 清理过多空行
            if '\n\n\n\n' in content:
                content = remove_excessive_blank_lines(content)
                stats["blank_lines_cleaned"] += 1
                print(f"✅ 清理过多空行: {filepath.name}")
            
            # 保存修改
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8-sig') as f:
                    f.write(content)
        
        except Exception as e:
            stats["errors"] += 1
            print(f"❌ 处理失败 {filepath.name}: {e}")
    
    print("\n" + "="*80)
    print("修复统计")
    print("="*80)
    print(f"修复编码问题: {stats['encoding_fixed']}个")
    print(f"补充文档治理章节: {stats['governance_added']}个")
    print(f"清理过多空行: {stats['blank_lines_cleaned']}个")
    print(f"错误数: {stats['errors']}个")
    
    return stats


if __name__ == "__main__":
    fix_document_quality()
