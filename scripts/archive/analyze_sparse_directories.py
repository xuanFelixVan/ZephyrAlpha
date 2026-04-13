# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
稀疏目录分析脚本
用途：分析稀疏目录并生成整合建议
创建时间：2026-04-07
"""

import os
from pathlib import Path
from typing import List, Dict
from datetime import datetime

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

def generate_integration_suggestions(sparse_dirs: List[Dict]) -> Dict:
    suggestions = {
        "merge_to_parent": [],
        "merge_to_sibling": [],
        "keep_as_is": []
    }
    
    for sparse_dir in sparse_dirs:
        if sparse_dir["depth"] >= 3:
            suggestions["merge_to_parent"].append({
                "sparse_dir": sparse_dir["path"],
                "target_dir": sparse_dir["parent"],
                "reason": f"深度{sparse_dir['depth']}层，建议合并到父目录",
                "files": sparse_dir["files"]
            })
        elif sparse_dir["file_count"] == 1:
            suggestions["merge_to_parent"].append({
                "sparse_dir": sparse_dir["path"],
                "target_dir": sparse_dir["parent"],
                "reason": "仅1个文件，建议合并到父目录",
                "files": sparse_dir["files"]
            })
        else:
            suggestions["keep_as_is"].append({
                "sparse_dir": sparse_dir["path"],
                "reason": f"有{sparse_dir['file_count']}个文件，暂不整合",
                "files": sparse_dir["files"]
            })
    
    return suggestions

def generate_report(sparse_dirs: List[Dict], suggestions: Dict):
    report_path = OUTPUT_DIR / f"sparse_directory_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 稀疏目录分析报告\n\n")
        f.write(f"> **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"> **分析范围**: {DOCS_DIR}\n")
        f.write(f"> **稀疏目录定义**: 文件数<3的目录\n\n")
        
        f.write("## 📊 分析统计\n\n")
        f.write(f"- **稀疏目录总数**: {len(sparse_dirs)}\n")
        f.write(f"- **建议合并到父目录**: {len(suggestions['merge_to_parent'])}\n")
        f.write(f"- **建议合并到兄弟目录**: {len(suggestions['merge_to_sibling'])}\n")
        f.write(f"- **建议保持现状**: {len(suggestions['keep_as_is'])}\n\n")
        
        f.write("## 🔍 稀疏目录列表\n\n")
        f.write("| 目录路径 | 文件数 | 文件列表 |\n")
        f.write("|----------|--------|----------|\n")
        for sparse_dir in sparse_dirs[:50]:
            files_str = ", ".join(sparse_dir["files"][:3])
            if len(sparse_dir["files"]) > 3:
                files_str += "..."
            f.write(f"| {sparse_dir['path']} | {sparse_dir['file_count']} | {files_str} |\n")
        f.write("\n")
        
        f.write("## 💡 整合建议\n\n")
        
        f.write("### 建议合并到父目录\n\n")
        f.write(f"**数量**: {len(suggestions['merge_to_parent'])}\n\n")
        for suggestion in suggestions["merge_to_parent"][:20]:
            f.write(f"- **{suggestion['sparse_dir']}**\n")
            f.write(f"  - 目标目录: {suggestion['target_dir']}\n")
            f.write(f"  - 原因: {suggestion['reason']}\n")
            f.write(f"  - 文件: {', '.join(suggestion['files'])}\n\n")
        
        f.write("### 建议保持现状\n\n")
        f.write(f"**数量**: {len(suggestions['keep_as_is'])}\n\n")
        for suggestion in suggestions["keep_as_is"][:20]:
            f.write(f"- **{suggestion['sparse_dir']}**\n")
            f.write(f"  - 原因: {suggestion['reason']}\n")
            f.write(f"  - 文件: {', '.join(suggestion['files'])}\n\n")
        
        f.write("## 📝 整合步骤\n\n")
        f.write("1. **备份当前状态**: `git checkout -b backup/sparse-directory-integration`\n")
        f.write("2. **手动整合目录**: 根据建议手动移动文件\n")
        f.write("3. **更新引用**: 更新相关文档中的链接引用\n")
        f.write("4. **验证整合效果**: 运行深度审计验证\n")
        f.write("5. **提交整合成果**: `git add -A; git commit -m 'feat: 整合稀疏目录'`\n\n")
        
        f.write("## ⚠️ 注意事项\n\n")
        f.write("1. **谨慎操作**: 目录整合会影响大量文件引用\n")
        f.write("2. **测试验证**: 整合后需要全面测试\n")
        f.write("3. **文档更新**: 需要更新所有相关文档的链接\n")
        f.write("4. **团队沟通**: 如有团队协作，需要提前沟通\n")
    
    return report_path

def main():
    print("=" * 80)
    print("稀疏目录分析")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"分析目录: {DOCS_DIR}")
    print("=" * 80)
    
    print("\n分析稀疏目录...")
    sparse_dirs = analyze_sparse_directories()
    
    print(f"发现 {len(sparse_dirs)} 个稀疏目录")
    
    print("\n生成整合建议...")
    suggestions = generate_integration_suggestions(sparse_dirs)
    
    print(f"- 建议合并到父目录: {len(suggestions['merge_to_parent'])}")
    print(f"- 建议保持现状: {len(suggestions['keep_as_is'])}")
    
    print("\n生成分析报告...")
    report_path = generate_report(sparse_dirs, suggestions)
    
    print(f"报告已保存至: {report_path}")
    
    print("\n" + "=" * 80)
    print("分析完成")
    print("=" * 80)
    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
