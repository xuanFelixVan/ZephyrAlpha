# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
生成稀疏目录整合建议报告
用途：为稀疏目录整合提供详细的操作指南
创建时间：2026-04-07
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_DIR = PROJECT_ROOT / "docs/09_AUDIT/STATE"

def analyze_sparse_directories() -> List[Dict]:
    sparse_dirs = []
    
    for root, dirs, files in os.walk(DOCS_DIR):
        md_files = [f for f in files if f.endswith('.md')]
        
        if len(md_files) < 3 and len(md_files) > 0:
            rel_path = os.path.relpath(root, DOCS_DIR)
            
            parent_path = os.path.dirname(root)
            parent_rel_path = os.path.relpath(parent_path, DOCS_DIR)
            
            sparse_dirs.append({
                "path": rel_path,
                "file_count": len(md_files),
                "files": md_files,
                "parent": parent_rel_path,
                "depth": rel_path.count(os.sep)
            })
    
    return sparse_dirs

def generate_integration_guide(sparse_dirs: List[Dict]) -> Dict:
    guide = {
        "merge_to_parent": [],
        "keep_as_is": [],
        "manual_review": []
    }
    
    for sparse_dir in sparse_dirs:
        if sparse_dir["depth"] >= 3:
            guide["merge_to_parent"].append({
                "sparse_dir": sparse_dir["path"],
                "target_dir": sparse_dir["parent"],
                "reason": f"深度{sparse_dir['depth']}层，建议合并到父目录",
                "files": sparse_dir["files"],
                "risk": "低",
                "steps": [
                    f"1. 检查 {sparse_dir['path']} 下的所有文件",
                    f"2. 更新文件中的相对路径引用",
                    f"3. 移动文件到 {sparse_dir['parent']}",
                    f"4. 删除空目录 {sparse_dir['path']}",
                    f"5. 更新父目录的 INDEX.md"
                ]
            })
        elif sparse_dir["file_count"] == 1:
            guide["merge_to_parent"].append({
                "sparse_dir": sparse_dir["path"],
                "target_dir": sparse_dir["parent"],
                "reason": "仅1个文件，建议合并到父目录",
                "files": sparse_dir["files"],
                "risk": "低",
                "steps": [
                    f"1. 检查 {sparse_dir['path']} 下的文件",
                    f"2. 移动文件到 {sparse_dir['parent']}",
                    f"3. 删除空目录 {sparse_dir['path']}",
                    f"4. 更新父目录的 INDEX.md"
                ]
            })
        else:
            guide["keep_as_is"].append({
                "sparse_dir": sparse_dir["path"],
                "reason": f"有{sparse_dir['file_count']}个文件，暂不整合",
                "files": sparse_dir["files"]
            })
    
    return guide

def generate_report(sparse_dirs: List[Dict], guide: Dict):
    report_path = OUTPUT_DIR / f"sparse_directory_integration_guide_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 稀疏目录整合指南\n\n")
        f.write(f"> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"> **稀疏目录总数**: {len(sparse_dirs)}\n")
        f.write(f"> **建议合并**: {len(guide['merge_to_parent'])}\n")
        f.write(f"> **保持现状**: {len(guide['keep_as_is'])}\n\n")
        
        f.write("## 📋 整合优先级\n\n")
        f.write("### 高优先级（建议立即整合）\n\n")
        f.write(f"**数量**: {len([d for d in guide['merge_to_parent'] if d['risk'] == '低'])}\n\n")
        
        for i, item in enumerate(guide['merge_to_parent'][:10], 1):
            f.write(f"#### {i}. {item['sparse_dir']}\n\n")
            f.write(f"- **目标目录**: {item['target_dir']}\n")
            f.write(f"- **原因**: {item['reason']}\n")
            f.write(f"- **文件数**: {len(item['files'])}\n")
            f.write(f"- **风险等级**: {item['risk']}\n")
            f.write(f"- **操作步骤**:\n")
            for step in item['steps']:
                f.write(f"  - {step}\n")
            f.write("\n")
        
        if len(guide['merge_to_parent']) > 10:
            f.write(f"... 还有 {len(guide['merge_to_parent']) - 10} 个目录建议合并\n\n")
        
        f.write("### 低优先级（保持现状）\n\n")
        f.write(f"**数量**: {len(guide['keep_as_is'])}\n\n")
        
        for i, item in enumerate(guide['keep_as_is'][:5], 1):
            f.write(f"{i}. **{item['sparse_dir']}**\n")
            f.write(f"   - 原因: {item['reason']}\n")
            f.write(f"   - 文件: {', '.join(item['files'])}\n\n")
        
        if len(guide['keep_as_is']) > 5:
            f.write(f"... 还有 {len(guide['keep_as_is']) - 5} 个目录保持现状\n\n")
        
        f.write("## ⚠️ 注意事项\n\n")
        f.write("1. **备份**: 整合前请确保已提交Git备份\n")
        f.write("2. **路径更新**: 移动文件后需要更新所有相对路径引用\n")
        f.write("3. **索引更新**: 移动文件后需要更新父目录的INDEX.md\n")
        f.write("4. **测试验证**: 整合后运行监控脚本验证合规率\n")
        f.write("5. **分批操作**: 建议分批整合，每次整合5-10个目录\n\n")
        
        f.write("## 🔧 整合命令示例\n\n")
        f.write("```bash\n")
        f.write("# 示例：整合单个目录\n")
        f.write("# 1. 移动文件\n")
        f.write("mv docs/03_TRADING_TACTICS/05_STRATEGY_POOL/index.md docs/03_TRADING_TACTICS/\n")
        f.write("# 2. 删除空目录\n")
        f.write("rmdir docs/03_TRADING_TACTICS/05_STRATEGY_POOL\n")
        f.write("# 3. 更新INDEX.md\n")
        f.write("# 手动编辑 docs/03_TRADING_TACTICS/INDEX.md\n")
        f.write("# 4. 验证\n")
        f.write("python scripts/continuous_monitoring.py\n")
        f.write("```\n\n")
        
        f.write("## 📊 整合效果预估\n\n")
        f.write(f"- **整合前稀疏目录数**: {len(sparse_dirs)}\n")
        f.write(f"- **整合后稀疏目录数**: {len(guide['keep_as_is'])}\n")
        f.write(f"- **减少目录数**: {len(guide['merge_to_parent'])}\n")
        f.write(f"- **目录结构优化率**: {round(len(guide['merge_to_parent']) / len(sparse_dirs) * 100, 2) if sparse_dirs else 0}%\n\n")
        
        f.write("---\n\n")
        f.write(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    return report_path

def main():
    print("=" * 80)
    print("生成稀疏目录整合指南")
    print("=" * 80)
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    print("\n分析稀疏目录...")
    sparse_dirs = analyze_sparse_directories()
    print(f"发现 {len(sparse_dirs)} 个稀疏目录")
    
    print("\n生成整合建议...")
    guide = generate_integration_guide(sparse_dirs)
    print(f"- 建议合并: {len(guide['merge_to_parent'])}")
    print(f"- 保持现状: {len(guide['keep_as_is'])}")
    
    print("\n生成整合指南报告...")
    report_path = generate_report(sparse_dirs, guide)
    print(f"报告已保存至: {report_path}")
    
    print("\n" + "=" * 80)
    print("生成完成")
    print("=" * 80)
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
