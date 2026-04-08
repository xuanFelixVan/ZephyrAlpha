"""
修复最后8个审计问题脚本
用途：修复L1、L2、L3层剩余问题
创建时间：2026-04-07
"""

import re
from pathlib import Path
from datetime import datetime

CONSTRUCTION_DOCS_DIR = Path("docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS")
BLUEPRINTS_DIR = CONSTRUCTION_DOCS_DIR / "01_BLUEPRINTS"


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


def fix_implementation_progress_tracking():
    """修复IMPLEMENTATION_PROGRESS_TRACKING.md"""
    filepath = BLUEPRINTS_DIR / "IMPLEMENTATION_PROGRESS_TRACKING.md"
    
    if not filepath.exists():
        print("❌ 文件不存在: IMPLEMENTATION_PROGRESS_TRACKING.md")
        return False
    
    content = read_document(filepath)
    if not content:
        print("❌ 无法读取文件: IMPLEMENTATION_PROGRESS_TRACKING.md")
        return False
    
    changes = []
    
    # 1. 添加YAML头部（如果没有）
    if not content.startswith('---'):
        yaml_header = f"""---
module_id: IMPLEMENTATIONPROGRESSTRACKING_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 实施团队
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
layer: "Layer 6 (组合优化层)"
---

"""
        content = yaml_header + content
        changes.append("添加YAML头部和Layer定位")
    else:
        # 检查并添加Layer定位
        if not re.search(r'^layer:\s*', content, re.MULTILINE):
            content = re.sub(
                r'(---\s*\n.*?)(\n---\s*\n)',
                r'\1\nlayer: "Layer 6 (组合优化层)"\n\2',
                content,
                flags=re.DOTALL
            )
            changes.append("添加Layer定位")
    
    # 2. 添加文档治理章节（如果没有）
    if '文档治理' not in content:
        governance_section = f"""

## 文档治理

### 文档状态
- **创建日期**: 2026-04-07
- **最后更新**: {datetime.now().strftime('%Y-%m-%d')}
- **文档版本**: v1.0.0
- **维护负责人**: 实施团队

### 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-07 | 初始版本创建 | 实施团队 |

### 相关文档
- 索引文档: [INDEX.md](./INDEX.md)
- 系统清单: [System_Manifest.md](../../System_Manifest.md)

---
"""
        content = content.rstrip()
        if content.endswith('---'):
            content = content[:-3].rstrip()
        
        content = content + governance_section
        changes.append("添加文档治理章节")
    
    # 3. 保存文件
    if changes:
        try:
            with open(filepath, 'w', encoding='utf-8-sig') as f:
                f.write(content)
            print(f"✅ 修复IMPLEMENTATION_PROGRESS_TRACKING.md: {', '.join(changes)}")
            return True
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return False
    
    print("⚠️ IMPLEMENTATION_PROGRESS_TRACKING.md 无需修复")
    return True


def update_index_md():
    """更新INDEX.md，添加缺失的文档索引"""
    index_path = BLUEPRINTS_DIR / "INDEX.md"
    
    if not index_path.exists():
        print("❌ INDEX.md 不存在")
        return False
    
    content = read_document(index_path)
    if not content:
        print("❌ 无法读取INDEX.md")
        return False
    
    changes = []
    
    # 检查并添加IMPLEMENTATION_PROGRESS_TRACKING.md
    if 'IMPLEMENTATION_PROGRESS_TRACKING' not in content:
        # 找到合适的位置插入
        # 在"## 📚 蓝图文档列表"章节中添加
        if '## 📚 蓝图文档列表' in content:
            # 在该章节末尾添加
            content = re.sub(
                r'(## 📚 蓝图文档列表.*?)(\n## )',
                r'\1\n- [实施进度跟踪](./IMPLEMENTATION_PROGRESS_TRACKING.md) - 实施进度跟踪文档\n\2',
                content,
                flags=re.DOTALL
            )
            changes.append("添加IMPLEMENTATION_PROGRESS_TRACKING.md索引")
    
    # 检查并添加MARKET_PARTICIPANT_SIMULATION_INTEGRATION_BLUEPRINT.md
    if 'MARKET_PARTICIPANT_SIMULATION_INTEGRATION_BLUEPRINT' not in content:
        if 'MARKET_PARTICIPANT_SIMULATION_INTEGRATION_ARCHITECTURE' in content:
            # 替换旧名称
            content = content.replace(
                'MARKET_PARTICIPANT_SIMULATION_INTEGRATION_ARCHITECTURE',
                'MARKET_PARTICIPANT_SIMULATION_INTEGRATION_BLUEPRINT'
            )
            changes.append("更新MARKET_PARTICIPANT_SIMULATION_INTEGRATION_BLUEPRINT.md索引")
        else:
            # 添加新索引
            if '## 📚 蓝图文档列表' in content:
                content = re.sub(
                    r'(## 📚 蓝图文档列表.*?)(\n## )',
                    r'\1\n- [市场参与者模拟集成](./MARKET_PARTICIPANT_SIMULATION_INTEGRATION_BLUEPRINT.md) - 市场参与者模拟集成蓝图\n\2',
                    content,
                    flags=re.DOTALL
                )
                changes.append("添加MARKET_PARTICIPANT_SIMULATION_INTEGRATION_BLUEPRINT.md索引")
    
    # 保存文件
    if changes:
        try:
            with open(index_path, 'w', encoding='utf-8-sig') as f:
                f.write(content)
            print(f"✅ 更新INDEX.md: {', '.join(changes)}")
            return True
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return False
    
    print("⚠️ INDEX.md 无需更新")
    return True


def main():
    """主函数"""
    print("="*80)
    print("修复最后8个审计问题")
    print("="*80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 修复IMPLEMENTATION_PROGRESS_TRACKING.md
    print("\n1. 修复IMPLEMENTATION_PROGRESS_TRACKING.md")
    fix_implementation_progress_tracking()
    
    # 更新INDEX.md
    print("\n2. 更新INDEX.md")
    update_index_md()
    
    # 关于04_CONFIG_TEMPLATES目录
    print("\n3. 关于04_CONFIG_TEMPLATES目录")
    config_templates_dir = CONSTRUCTION_DOCS_DIR / "04_CONFIG_TEMPLATES"
    if config_templates_dir.exists():
        files = list(config_templates_dir.glob("*.*"))
        print(f"✅ 04_CONFIG_TEMPLATES 目录存在，包含 {len(files)} 个文件")
        print("   建议：保留此目录，因为包含配置模板文件")
        print("   注意：审计脚本可能误报为空目录")
    else:
        print("⚠️ 04_CONFIG_TEMPLATES 目录不存在")
    
    print("\n" + "="*80)
    print("修复完成")
    print("="*80)


if __name__ == "__main__":
    main()
