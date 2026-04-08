"""
P2级问题修复脚本
用途：处理目录漂移、补充变更记录、规范module_id
创建时间：2026-04-07
"""

import re
from pathlib import Path
from typing import Dict, List

BLUEPRINTS_DIR = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS")
CONSTRUCTION_DOCS_DIR = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS")


def read_document(filepath: Path) -> str:
    """读取文档内容"""
    encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'latin-1']
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue
    return ""


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


def analyze_directory_drift():
    """分析目录漂移"""
    print("="*80)
    print("分析目录漂移")
    print("="*80)
    
    # 预期的目录结构
    expected_dirs = {
        '01_BLUEPRINTS': '蓝图文档',
    }
    
    # 检查实际目录
    actual_dirs = []
    for item in CONSTRUCTION_DOCS_DIR.iterdir():
        if item.is_dir():
            file_count = len(list(item.glob("**/*.md")))
            actual_dirs.append({
                "name": item.name,
                "path": str(item),
                "file_count": file_count,
                "is_expected": item.name in expected_dirs
            })
    
    # 分析漂移目录
    drift_dirs = [d for d in actual_dirs if not d['is_expected']]
    
    print(f"\n预期目录: {list(expected_dirs.keys())}")
    print(f"实际目录: {[d['name'] for d in actual_dirs]}")
    print(f"漂移目录: {len(drift_dirs)}个")
    
    for dir_info in drift_dirs:
        print(f"\n  - {dir_info['name']}: {dir_info['file_count']}个文件")
        print(f"    路径: {dir_info['path']}")
    
    return drift_dirs


def fix_change_history():
    """补充变更记录"""
    print("\n" + "="*80)
    print("补充变更记录")
    print("="*80)
    
    # 需要补充变更记录的文档列表
    docs_need_history = [
        "AUTO_REPAIR_ENGINE_BLUEPRINT.md",
        "DATA_COST_MANAGEMENT_BLUEPRINT.md",
        "DATA_FABRIC_BLUEPRINT.md",
        "DATA_GOVERNANCE_PLATFORM_BLUEPRINT.md",
        "DATA_LIFECYCLE_MANAGEMENT_BLUEPRINT.md",
        "DATA_MESH_BLUEPRINT.md",
        "DATA_OBSERVABILITY_BLUEPRINT.md",
        "DATA_SECURITY_COMPLIANCE_BLUEPRINT.md",
        "DATA_SOURCE_MANAGEMENT_BLUEPRINT.md",
        "HIGH_PERFORMANCE_DATA_PIPELINE_BLUEPRINT.md",
        "QUALITY_REPORT_AUTOMATION_BLUEPRINT.md",
        "QUALITY_SCORING_SYSTEM_BLUEPRINT.md",
        "REALTIME_DATA_LAKE_BLUEPRINT.md",
    ]
    
    fixed_count = 0
    
    for filename in docs_need_history:
        filepath = BLUEPRINTS_DIR / filename
        if not filepath.exists():
            continue
        
        content = read_document(filepath)
        if not content:
            continue
        
        # 检查是否已有变更历史
        if '变更历史' in content or '版本历史' in content:
            continue
        
        yaml_header = extract_yaml_header(content)
        created_date = yaml_header.get('created_date', '2026-04-07')
        
        # 添加变更历史章节
        change_history = f"""

## 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {created_date} | 初始版本创建 | 实施团队 |
"""
        
        # 在文档末尾添加变更历史
        content = content.rstrip()
        if content.endswith('---'):
            content = content[:-3].rstrip()
        
        content = content + change_history + "\n\n---\n\n**蓝图版本**: v1.0.0 | **创建日期**: " + created_date + " | **状态**: Active\n"
        
        # 保存文件
        with open(filepath, 'w', encoding='utf-8-sig') as f:
            f.write(content)
        
        fixed_count += 1
        print(f"✅ {filename}")
    
    print(f"\n修复统计: {fixed_count}个文档")
    
    return fixed_count


def fix_module_id():
    """规范module_id"""
    print("\n" + "="*80)
    print("规范module_id")
    print("="*80)
    
    fixed_count = 0
    
    for filepath in BLUEPRINTS_DIR.glob("*.md"):
        if filepath.name == "INDEX.md":
            continue
        
        content = read_document(filepath)
        if not content:
            continue
        
        yaml_header = extract_yaml_header(content)
        module_id = yaml_header.get('module_id', '')
        
        # 检查module_id是否符合规范
        if not module_id:
            continue
        
        # 检查是否符合 [A-Z_]+_\d{3} 格式
        if not re.match(r'^[A-Z_]+_\d{3}$', module_id):
            # 生成规范的module_id
            # 从文件名生成
            filename_base = filepath.stem.replace('_BLUEPRINT', '').replace('_blueprint', '')
            parts = filename_base.split('_')
            
            # 取前3个部分作为module_id前缀
            if len(parts) >= 2:
                prefix = '_'.join(parts[:3]).upper()
                # 限制长度
                if len(prefix) > 30:
                    prefix = prefix[:30]
                
                new_module_id = f"{prefix}_001"
            else:
                new_module_id = f"{filename_base.upper()}_001"
            
            # 替换module_id
            content = re.sub(
                r'module_id:\s*' + re.escape(module_id),
                f'module_id: {new_module_id}',
                content
            )
            
            # 保存文件
            with open(filepath, 'w', encoding='utf-8-sig') as f:
                f.write(content)
            
            fixed_count += 1
            print(f"✅ {filepath.name}: {module_id} → {new_module_id}")
    
    print(f"\n修复统计: {fixed_count}个文档")
    
    return fixed_count


def main():
    """主函数"""
    print("="*80)
    print("P2级问题修复")
    print("="*80)
    print(f"修复时间: 2026-04-07")
    print("="*80)
    
    # 1. 分析目录漂移
    drift_dirs = analyze_directory_drift()
    
    # 2. 补充变更记录
    fixed_history = fix_change_history()
    
    # 3. 规范module_id
    fixed_ids = fix_module_id()
    
    print("\n" + "="*80)
    print("修复完成")
    print("="*80)
    print(f"目录漂移分析: {len(drift_dirs)}个目录")
    print(f"变更记录补充: {fixed_history}个文档")
    print(f"module_id规范: {fixed_ids}个文档")


if __name__ == "__main__":
    main()
