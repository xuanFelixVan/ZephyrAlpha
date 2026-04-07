"""
重新扫描剩余稀疏目录
用途：扫描所有文件数<3的目录，深度分析可整合性
创建时间：2026-04-07
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

def scan_sparse_directories() -> List[Dict]:
    sparse_dirs = []
    
    for root, dirs, files in os.walk(DOCS_DIR):
        root_path = Path(root)
        
        md_files = list(root_path.glob("*.md"))
        
        if len(md_files) < 3:
            all_files = list(root_path.glob("*"))
            all_dirs = [f for f in all_files if f.is_dir()]
            
            depth = len(root_path.relative_to(DOCS_DIR).parts)
            
            has_index = (root_path / "INDEX.md").exists() or (root_path / "index.md").exists()
            has_readme = (root_path / "README.md").exists() or (root_path / "readme.md").exists()
            has_blueprint = any('BLUEPRINT' in f.name.upper() for f in md_files)
            
            non_index_files = [f for f in md_files if f.name.lower() not in ['index.md', 'readme.md']]
            
            sparse_dirs.append({
                "path": str(root_path.relative_to(DOCS_DIR)),
                "depth": depth,
                "md_count": len(md_files),
                "total_count": len(all_files),
                "dir_count": len(all_dirs),
                "has_index": has_index,
                "has_readme": has_readme,
                "has_blueprint": has_blueprint,
                "non_index_files": [f.name for f in non_index_files]
            })
    
    return sparse_dirs

def deep_analyze_for_integration(sparse_dir: Dict) -> Dict:
    can_integrate = False
    reason = ""
    action = "keep"
    priority = "low"
    
    if sparse_dir['dir_count'] > 0:
        can_integrate = False
        reason = f"包含{sparse_dir['dir_count']}个子目录，必须保留"
        action = "skip"
        priority = "none"
    
    elif sparse_dir['has_blueprint']:
        can_integrate = False
        reason = "蓝图文件，代表系统模块，必须保留"
        action = "keep_blueprint"
        priority = "none"
    
    elif sparse_dir['depth'] >= 3:
        if len(sparse_dir['non_index_files']) == 0:
            can_integrate = True
            reason = f"深度{sparse_dir['depth']}层，仅有INDEX/README，可删除"
            action = "delete_empty"
            priority = "high"
        
        elif len(sparse_dir['non_index_files']) == 1:
            file_name = sparse_dir['non_index_files'][0]
            
            if 'backup' in file_name.lower() or 'archived' in file_name.lower():
                can_integrate = True
                reason = f"深度{sparse_dir['depth']}层，备份/归档文件，可合并"
                action = "merge_backup"
                priority = "medium"
            
            elif 'blueprint' not in file_name.lower():
                can_integrate = True
                reason = f"深度{sparse_dir['depth']}层，单文件可合并"
                action = "merge_single"
                priority = "medium"
            
            else:
                can_integrate = False
                reason = "蓝图文件，必须保留"
                action = "keep_blueprint"
                priority = "none"
        
        elif len(sparse_dir['non_index_files']) == 2:
            can_integrate = False
            reason = f"深度{sparse_dir['depth']}层，但有2个文件，保留观察"
            action = "keep"
            priority = "low"
        
        else:
            can_integrate = False
            reason = f"深度{sparse_dir['depth']}层，但文件较多"
            action = "keep"
            priority = "low"
    
    else:
        can_integrate = False
        reason = f"深度{sparse_dir['depth']}层，根级目录，保留"
        action = "keep"
        priority = "none"
    
    return {
        **sparse_dir,
        "can_integrate": can_integrate,
        "reason": reason,
        "action": action,
        "priority": priority
    }

def main():
    print("=" * 80)
    print("重新扫描剩余稀疏目录")
    print("=" * 80)
    print(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    sparse_dirs = scan_sparse_directories()
    
    print(f"\n发现 {len(sparse_dirs)} 个稀疏目录（文件数<3）")
    
    analyzed_dirs = []
    integrate_dirs = []
    keep_dirs = []
    
    for sparse_dir in sparse_dirs:
        analyzed = deep_analyze_for_integration(sparse_dir)
        analyzed_dirs.append(analyzed)
        
        if analyzed['can_integrate']:
            integrate_dirs.append(analyzed)
        else:
            keep_dirs.append(analyzed)
    
    integrate_dirs.sort(key=lambda x: (
        {'high': 0, 'medium': 1, 'low': 2}.get(x['priority'], 3),
        -x['depth']
    ))
    
    print("\n" + "=" * 80)
    print("可以整合的目录（按优先级排序）")
    print("=" * 80)
    
    for i, d in enumerate(integrate_dirs, 1):
        print(f"\n{i}. {d['path']}")
        print(f"   深度: {d['depth']}")
        print(f"   文件数: {d['md_count']}")
        print(f"   非索引文件: {', '.join(d['non_index_files']) if d['non_index_files'] else '无'}")
        print(f"   原因: {d['reason']}")
        print(f"   操作: {d['action']}")
        print(f"   优先级: {d['priority']}")
    
    print("\n" + "=" * 80)
    print("统计结果")
    print("=" * 80)
    print(f"总稀疏目录: {len(sparse_dirs)}")
    print(f"可以整合: {len(integrate_dirs)}")
    print(f"建议保留: {len(keep_dirs)}")
    
    high_priority = len([d for d in integrate_dirs if d['priority'] == 'high'])
    medium_priority = len([d for d in integrate_dirs if d['priority'] == 'medium'])
    
    print(f"\n高优先级整合: {high_priority}")
    print(f"中优先级整合: {medium_priority}")
    
    report_path = PROJECT_ROOT / "docs/09_AUDIT/STATE" / f"remaining_sparse_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total": len(sparse_dirs),
            "can_integrate": len(integrate_dirs),
            "should_keep": len(keep_dirs),
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "integrate_dirs": integrate_dirs,
            "keep_dirs": keep_dirs
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n扫描报告已保存至: {report_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()
