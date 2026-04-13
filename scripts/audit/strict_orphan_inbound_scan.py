#!/usr/bin/env python3
"""
严格孤儿入链扫描器 (Strict Orphan Inbound Scanner)
计算每个.md文件的入度(in-degree)，识别孤儿文件
版本: 1.0.0
日期: 2026-04-13
"""

import io
import os
import re
import sys
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Windows UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "09_AUDIT" / "STATE"

def extract_links(content: str) -> list:
    """提取markdown中的所有内部链接"""
    # [text](path) 格式
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, content)
    
    links = []
    for text, path in matches:
        # 跳过外部链接、锚点、空链接
        if path.startswith(('http', 'https', '#', 'mailto:')):
            continue
        if not path or path.strip() == '':
            continue
        links.append(path)
    
    return links

def resolve_link(link: str, base_path: Path) -> str:
    """解析相对链接为目标文件路径"""
    # 移除锚点
    link = link.split('#')[0]
    
    # 绝对路径
    if link.startswith('/'):
        target = DOCS_DIR / link.lstrip('/')
    else:
        # 相对路径
        target = base_path.parent / link
    
    # 规范化路径
    try:
        target = target.resolve().relative_to(DOCS_DIR.resolve())
        return str(target).replace('\\', '/')
    except (ValueError, OSError):
        return None

def scan_orphans():
    """扫描孤儿文件"""
    print("=" * 70)
    print("严格孤儿入链扫描器")
    print("=" * 70)
    print(f"扫描目录: {DOCS_DIR}")
    print(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 收集所有.md文件
    print("[1/4] 收集所有 Markdown 文件...")
    all_files = list(DOCS_DIR.rglob("*.md"))
    file_set = set(str(f.relative_to(DOCS_DIR)).replace('\\', '/') for f in all_files)
    print(f"      发现 {len(all_files)} 个 Markdown 文件")
    
    # 2. 统计入度
    print("[2/4] 分析文件引用关系...")
    in_degree = defaultdict(int)
    link_map = defaultdict(list)  # 记录谁链接了该文件
    
    for i, md_file in enumerate(all_files, 1):
        if i % 500 == 0:
            print(f"      进度: {i}/{len(all_files)}")
        
        try:
            with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            links = extract_links(content)
            source_rel = str(md_file.relative_to(DOCS_DIR)).replace('\\', '/')
            
            for link in links:
                target = resolve_link(link, md_file)
                if target and target in file_set:
                    in_degree[target] += 1
                    link_map[target].append({
                        'source': source_rel,
                        'link_text': link
                    })
        except Exception as e:
            print(f"      警告: 无法读取 {md_file}: {e}")
            continue
    
    # 3. 找出孤儿文件(入度=0)
    print("[3/4] 识别孤儿文件...")
    orphans = []
    for md_file in all_files:
        rel_path = str(md_file.relative_to(DOCS_DIR)).replace('\\', '/')
        
        if in_degree[rel_path] == 0:
            # 获取文件信息
            stat = md_file.stat()
            layer = rel_path.split('/')[0] if '/' in rel_path else 'root'
            
            orphans.append({
                'path': rel_path,
                'layer': layer,
                'size_bytes': stat.st_size,
                'size_kb': round(stat.st_size / 1024, 2),
                'in_degree': 0,
                'out_links': len(extract_links(open(md_file, 'r', encoding='utf-8', errors='ignore').read()))
            })
    
    print(f"      发现 {len(orphans)} 个孤儿文件")
    
    # 4. 按层分类
    print("[4/4] 生成分类报告...")
    layer_stats = defaultdict(lambda: {'total': 0, 'orphans': 0})
    
    for f in all_files:
        rel = str(f.relative_to(DOCS_DIR)).replace('\\', '/')
        layer = rel.split('/')[0] if '/' in rel else 'root'
        layer_stats[layer]['total'] += 1
    
    for o in orphans:
        layer_stats[o['layer']]['orphans'] += 1
    
    # 生成报告
    report = {
        'scan_time': datetime.now().isoformat(),
        'total_files': len(all_files),
        'orphan_files': len(orphans),
        'orphan_rate': round(len(orphans) / len(all_files) * 100, 2),
        'layer_breakdown': dict(layer_stats),
        'orphans_by_layer': {}
    }
    
    # 按层分组孤儿文件
    for layer in sorted(layer_stats.keys()):
        layer_orphans = [o for o in orphans if o['layer'] == layer]
        report['orphans_by_layer'][layer] = layer_orphans
    
    # 保存JSON报告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_path = OUTPUT_DIR / f"orphan_scan_result_{timestamp}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 生成Markdown报告
    md_path = OUTPUT_DIR / f"orphan_governance_inventory_{timestamp}.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# 孤儿文件治理清单\n\n")
        f.write(f"**扫描时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**总文件数**: {len(all_files)}\n\n")
        f.write(f"**孤儿文件数**: {len(orphans)}\n\n")
        f.write(f"**孤儿率**: {report['orphan_rate']}%\n\n")
        
        f.write("## 按层统计\n\n")
        f.write("| 层级 | 总文件 | 孤儿数 | 孤儿率 |\n")
        f.write("|------|--------|--------|--------|\n")
        
        for layer in sorted(layer_stats.keys()):
            stats = layer_stats[layer]
            rate = round(stats['orphans'] / stats['total'] * 100, 2) if stats['total'] > 0 else 0
            f.write(f"| {layer} | {stats['total']} | {stats['orphans']} | {rate}% |\n")
        
        f.write("\n## 孤儿文件清单 (按层分组)\n\n")
        
        for layer in sorted(report['orphans_by_layer'].keys()):
            layer_orphans = report['orphans_by_layer'][layer]
            if layer_orphans:
                f.write(f"### {layer} ({len(layer_orphans)}个)\n\n")
                f.write("| 文件路径 | 大小(KB) | 出链数 | 建议处理 |\n")
                f.write("|---------|---------|--------|---------|\n")
                
                for o in layer_orphans[:50]:  # 每类只显示前50个
                    # 自动分类建议
                    if layer.startswith(('00_', '01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_', '11_')):
                        suggestion = "A类-补充INDEX入链"
                    elif layer in ['06_ARCHIVE', '09_ARCHIVE']:
                        suggestion = "C/D类-归档评估"
                    else:
                        suggestion = "B类-评估价值"
                    
                    f.write(f"| {o['path']} | {o['size_kb']} | {o['out_links']} | {suggestion} |\n")
                
                if len(layer_orphans) > 50:
                    f.write(f"| ... 还有 {len(layer_orphans) - 50} 个 | - | - | - |\n")
                
                f.write("\n")
    
    # 打印摘要
    print()
    print("=" * 70)
    print("扫描完成")
    print("=" * 70)
    print(f"总文件数: {len(all_files)}")
    print(f"孤儿文件: {len(orphans)} ({report['orphan_rate']}%)")
    print()
    print("按层统计:")
    for layer in sorted(layer_stats.keys()):
        stats = layer_stats[layer]
        rate = round(stats['orphans'] / stats['total'] * 100, 2) if stats['total'] > 0 else 0
        print(f"  {layer}: {stats['orphans']}/{stats['total']} ({rate}%)")
    print()
    print(f"JSON报告: {json_path}")
    print(f"Markdown清单: {md_path}")
    
    return report

if __name__ == "__main__":
    report = scan_orphans()
    
    # 如果孤儿率过高，返回非零退出码
    if report['orphan_rate'] > 50:
        print("\n⚠️  警告: 孤儿率超过50%，建议立即启动治理专项")
        sys.exit(1)
    else:
        sys.exit(0)
