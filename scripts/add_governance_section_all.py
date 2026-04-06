"""
批量添加文档治理章节脚本（全目录版）
用途：为所有蓝图文档添加文档治理章节
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from typing import List, Tuple
from collections import defaultdict

DOCS_DIR = Path("docs")

GOVERNANCE_TEMPLATE = """
---

## {section_num}. 文档治理

### {section_num}.1 System_Manifest.md索引

```markdown
#### Layer {layer_num}: {layer_name}
##### {module_index}. {module_name}
- **模块ID**: {module_id}
- **蓝图文档**: [{blueprint_filename}](./{relative_path})
- **技术规格书**: 待创建
- **职责**: {responsibility}
- **状态**: {status}
```

### {section_num}.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **{module_name}** | {responsibility} | **核心模块** |

### {section_num}.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {created_date} | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: {created_date} | **状态**: {status}
"""


def extract_yaml_header(content: str) -> dict:
    """提取YAML头部信息"""
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


def get_last_section_number(content: str) -> int:
    """获取最后一个章节编号"""
    sections = re.findall(r'^## (\d+)\.', content, re.MULTILINE)
    if sections:
        return int(sections[-1])
    return 0


def has_governance_section(content: str) -> bool:
    """检查是否已有文档治理章节"""
    return '文档治理' in content


def get_layer_info(layer_str: str) -> Tuple[str, str]:
    """解析Layer信息"""
    if not layer_str:
        return "0", "系统架构"
    
    match = re.search(r'Layer (\d+)', layer_str)
    if match:
        layer_num = match.group(1)
        layer_name = layer_str.split('(')[-1].split(')')[0] if '(' in layer_str else "系统架构"
        return layer_num, layer_name
    
    return "0", "系统架构"


def get_module_index(module_id: str) -> str:
    """从module_id提取模块索引"""
    if not module_id:
        return "0.1"
    
    parts = module_id.split('_')
    if len(parts) >= 2:
        return f"0.{parts[-1]}"
    
    return "0.1"


def get_module_name_from_id(module_id: str) -> str:
    """从module_id提取模块名称"""
    if not module_id:
        return "未知模块"
    
    name_parts = module_id.split('_')[:-1]
    return ' '.join(name_parts).title() if name_parts else "未知模块"


def get_responsibility_from_scope(scope: str) -> str:
    """从applicable_scope提取职责"""
    if not scope:
        return "核心功能实现"
    return scope


def process_blueprint_file(filepath: Path) -> bool:
    """处理单个蓝图文件"""
    try:
        # 尝试多种编码
        encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'latin-1']
        content = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    content = f.read()
                used_encoding = encoding
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if content is None:
            print(f"  ❌ 无法读取文件（编码问题）: {filepath.name}")
            return False
        
        if has_governance_section(content):
            print(f"  ✓ 已有文档治理章节: {filepath.name}")
            return False
        
        yaml_header = extract_yaml_header(content)
        last_section = get_last_section_number(content)
        next_section = last_section + 1
        
        layer_str = yaml_header.get('layer', 'Layer 0 (系统架构)')
        layer_num, layer_name = get_layer_info(layer_str)
        
        module_id = yaml_header.get('module_id', 'UNKNOWN_001')
        module_name = get_module_name_from_id(module_id)
        module_index = get_module_index(module_id)
        
        responsibility = get_responsibility_from_scope(yaml_header.get('applicable_scope', ''))
        status = yaml_header.get('status', 'Active')
        created_date = yaml_header.get('created_date', '2026-04-07')
        
        relative_path = filepath.relative_to(DOCS_DIR)
        
        governance_section = GOVERNANCE_TEMPLATE.format(
            section_num=next_section,
            layer_num=layer_num,
            layer_name=layer_name,
            module_index=module_index,
            module_name=module_name,
            module_id=module_id,
            blueprint_filename=filepath.name,
            relative_path=str(relative_path),
            responsibility=responsibility,
            status=status,
            created_date=created_date
        )
        
        new_content = content.rstrip() + governance_section
        
        # 使用UTF-8-sig编码保存
        with open(filepath, 'w', encoding='utf-8-sig') as f:
            f.write(new_content)
        
        print(f"  ✅ 已添加文档治理章节: {filepath.name}")
        return True
    
    except Exception as e:
        print(f"  ❌ 处理失败 {filepath.name}: {e}")
        return False


def main():
    """主函数"""
    print("=" * 80)
    print("批量添加文档治理章节（全目录版）")
    print("=" * 80)
    
    if not DOCS_DIR.exists():
        print(f"❌ 目录不存在: {DOCS_DIR}")
        return
    
    blueprint_files = list(DOCS_DIR.rglob("*BLUEPRINT.md"))
    print(f"\n找到 {len(blueprint_files)} 个蓝图文档")
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for filepath in blueprint_files:
        if process_blueprint_file(filepath):
            success_count += 1
        else:
            skip_count += 1
    
    print("\n" + "=" * 80)
    print(f"处理完成:")
    print(f"  ✅ 成功添加: {success_count} 个")
    print(f"  ✓ 已有章节: {skip_count} 个")
    print(f"  ❌ 处理失败: {fail_count} 个")
    print("=" * 80)


if __name__ == "__main__":
    main()
