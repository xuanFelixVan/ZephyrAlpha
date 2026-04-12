# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
旧架构命名文件归档脚本
用途：将包含LAYER关键词的审计报告移动到归档目录
创建时间：2026-04-07
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
ARCHIVE_DIR = DOCS_DIR / "06_ARCHIVE" / "20260407_old_layer_audit_reports"

def create_archive_structure():
    """创建归档目录结构"""
    print("创建归档目录结构...")
    
    layers = ["layer5_reports", "layer6_reports", "layer9_reports", "layer10_reports", "layer11_reports"]
    
    for layer in layers:
        layer_dir = ARCHIVE_DIR / layer
        layer_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ 创建目录: {layer_dir}")
    
    print("归档目录结构创建完成\n")

def move_layer_files():
    """移动旧架构命名文件到归档目录"""
    print("移动旧架构命名文件...")
    
    audit_dirs = [
        DOCS_DIR / "05_IMPLEMENTATION" / "04_OPERATIONS" / "audit_state",
        DOCS_DIR / "05_IMPLEMENTATION" / "07_OPERATIONS" / "audit_state"
    ]
    
    moved_count = 0
    
    for audit_dir in audit_dirs:
        if not audit_dir.exists():
            continue
        
        for file_path in audit_dir.glob("LAYER*.md"):
            file_name = file_path.name
            
            if file_name.startswith("LAYER5"):
                target_dir = ARCHIVE_DIR / "layer5_reports"
            elif file_name.startswith("LAYER6"):
                target_dir = ARCHIVE_DIR / "layer6_reports"
            elif file_name.startswith("LAYER9"):
                target_dir = ARCHIVE_DIR / "layer9_reports"
            elif file_name.startswith("LAYER10"):
                target_dir = ARCHIVE_DIR / "layer10_reports"
            elif file_name.startswith("LAYER11"):
                target_dir = ARCHIVE_DIR / "layer11_reports"
            else:
                continue
            
            target_path = target_dir / file_name
            
            shutil.move(str(file_path), str(target_path))
            print(f"  ✅ 移动: {file_path.relative_to(DOCS_DIR)} -> {target_path.relative_to(DOCS_DIR)}")
            moved_count += 1
    
    print(f"\n移动完成: {moved_count}个文件\n")
    return moved_count

def create_archive_index():
    """创建归档索引文件"""
    print("创建归档索引文件...")
    
    index_content = f"""---
module_id: ARCHIVE_OLD_LAYER_REPORTS_001
version: 1.0.0
status: Archived
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档治理团队
standard_type: 专业量化机构归档文档
applicable_scope: 旧架构命名审计报告归档
compliance_level: 专业标准
responsibility:
  - 文档归档、历史追溯
---

# 旧架构命名审计报告归档索引

## 📋 归档概要

**归档时间**: 2026-04-07  
**归档原因**: 文件名包含旧架构命名（LAYER*），不符合专业量化机构命名规范  
**归档标准**: 专业量化机构文档治理五大原则 - 版本隔离原则

## 📊 归档内容统计

| Layer分类 | 文件数量 | 原始位置 |
|-----------|----------|----------|
| Layer 5报告 | {len(list((ARCHIVE_DIR / 'layer5_reports').glob('*.md')))}个 | docs/05_IMPLEMENTATION/*/audit_state/ |
| Layer 6报告 | {len(list((ARCHIVE_DIR / 'layer6_reports').glob('*.md')))}个 | docs/05_IMPLEMENTATION/*/audit_state/ |
| Layer 9报告 | {len(list((ARCHIVE_DIR / 'layer9_reports').glob('*.md')))}个 | docs/05_IMPLEMENTATION/*/audit_state/ |
| Layer 10报告 | {len(list((ARCHIVE_DIR / 'layer10_reports').glob('*.md')))}个 | docs/05_IMPLEMENTATION/*/audit_state/ |
| Layer 11报告 | {len(list((ARCHIVE_DIR / 'layer11_reports').glob('*.md')))}个 | docs/05_IMPLEMENTATION/*/audit_state/ |

## 📁 归档文件清单

### Layer 5报告

"""
    
    layer5_files = sorted((ARCHIVE_DIR / "layer5_reports").glob("*.md"))
    for i, file_path in enumerate(layer5_files, 1):
        index_content += f"{i}. [{file_path.name}](./layer5_reports/{file_path.name})\n"
    
    index_content += "\n### Layer 6报告\n\n"
    layer6_files = sorted((ARCHIVE_DIR / "layer6_reports").glob("*.md"))
    for i, file_path in enumerate(layer6_files, 1):
        index_content += f"{i}. [{file_path.name}](./layer6_reports/{file_path.name})\n"
    
    index_content += "\n### Layer 9报告\n\n"
    layer9_files = sorted((ARCHIVE_DIR / "layer9_reports").glob("*.md"))
    for i, file_path in enumerate(layer9_files, 1):
        index_content += f"{i}. [{file_path.name}](./layer9_reports/{file_path.name})\n"
    
    index_content += "\n### Layer 10报告\n\n"
    layer10_files = sorted((ARCHIVE_DIR / "layer10_reports").glob("*.md"))
    for i, file_path in enumerate(layer10_files, 1):
        index_content += f"{i}. [{file_path.name}](./layer10_reports/{file_path.name})\n"
    
    index_content += "\n### Layer 11报告\n\n"
    layer11_files = sorted((ARCHIVE_DIR / "layer11_reports").glob("*.md"))
    for i, file_path in enumerate(layer11_files, 1):
        index_content += f"{i}. [{file_path.name}](./layer11_reports/{file_path.name})\n"
    
    index_content += f"""

## 🔄 追溯路径

### Git历史追溯

所有归档文件可通过Git历史追溯至原始位置：

```bash
# 查看文件历史
git log --all --full-history -- "docs/05_IMPLEMENTATION/*/audit_state/LAYER*.md"

# 恢复文件到原始位置
git checkout <commit_hash> -- docs/05_IMPLEMENTATION/*/audit_state/<filename>
```

### 归档映射

| 归档文件 | 原始位置 |
|----------|----------|
"""
    
    all_files = layer5_files + layer6_files + layer9_files + layer10_files + layer11_files
    for file_path in all_files[:10]:
        index_content += f"| {file_path.name} | docs/05_IMPLEMENTATION/*/audit_state/ |\n"
    
    if len(all_files) > 10:
        index_content += f"| ... | ... (共{len(all_files)}个文件) |\n"
    
    index_content += """

## 📝 归档说明

### 归档原因

根据专业量化机构文档治理五大原则：

1. **命名规范原则**: 文件名应清晰表达其内容和职责，遵循统一命名规范
   - 旧命名: `LAYER5_DEEP_AUDIT_REPORT_v4_20260407.md`
   - 新规范: `audit_layer5_deep_report_v4_20260407.md`

2. **版本隔离原则**: 历史版本统一归档到`06_ARCHIVE/`
   - 活跃目录只保留最新版本
   - 历史版本统一归档管理

### 归档标准

- ✅ 文件名包含旧架构命名（LAYER*）
- ✅ 文件内容为审计报告（临时文件）
- ✅ Git有完整备份，可随时恢复
- ✅ 归档后不影响当前系统运行

### 后续处理

1. **活跃目录**: 清理旧架构命名文件，符合命名规范
2. **归档目录**: 保留历史版本，建立追溯路径
3. **合规率提升**: 活跃目录符合专业量化机构标准

---

**归档执行**: 文档治理优化系统  
**归档标准**: 专业量化机构五大原则 + 三层审计标准  
**归档时间**: 2026-04-07
"""
    
    index_file = ARCHIVE_DIR / "INDEX.md"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"  ✅ 创建索引: {index_file.relative_to(DOCS_DIR)}\n")

def main():
    print("=" * 80)
    print("旧架构命名文件归档脚本")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    create_archive_structure()
    moved_count = move_layer_files()
    create_archive_index()
    
    print("=" * 80)
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"归档文件: {moved_count}个")
    print("=" * 80)

if __name__ == "__main__":
    main()
