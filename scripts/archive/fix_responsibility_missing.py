# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
修复职责描述缺失脚本
用途：为缺少职责描述的文档添加职责字段
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from typing import Tuple, List
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

RESPONSIBILITY_KEYWORDS = {
    "因子计算": ["factor", "alpha", "ic", "ir", "因子", "alpha"],
    "风险预算": ["risk", "var", "es", "风险", "budget", "预算"],
    "数据质量": ["data", "数据", "quality", "质量", "clean", "清洗"],
    "组合优化": ["portfolio", "组合", "optimization", "优化", "rebalance", "再平衡"],
    "回测系统": ["backtest", "回测", "test", "测试", "simulation", "模拟"],
    "交易执行": ["trade", "交易", "execute", "执行", "order", "订单"],
    "审计系统": ["audit", "审计", "check", "检查", "monitor", "监控"],
    "文档治理": ["doc", "文档", "index", "索引", "governance", "治理"],
    "系统架构": ["architecture", "架构", "design", "设计", "blueprint", "蓝图"],
    "机器学习": ["ml", "machine learning", "机器学习", "model", "模型", "train", "训练"],
    "市场状态识别": ["market", "市场", "regime", "状态", "state", "识别"],
    "策略研究": ["strategy", "策略", "research", "研究", "signal", "信号"],
}

def has_responsibility(content: str) -> bool:
    return bool(re.search(r'^responsibility:', content, re.MULTILINE))

def infer_responsibility(file_path: Path, content: str) -> List[str]:
    responsibilities = []
    content_lower = content.lower()
    path_str = str(file_path).lower()
    
    for responsibility, keywords in RESPONSIBILITY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in content_lower or keyword.lower() in path_str:
                if responsibility not in responsibilities:
                    responsibilities.append(responsibility)
                break
    
    if not responsibilities:
        if 'factor' in path_str or 'alpha' in path_str:
            responsibilities.append('因子计算')
        elif 'risk' in path_str:
            responsibilities.append('风险预算')
        elif 'data' in path_str:
            responsibilities.append('数据质量')
        elif 'portfolio' in path_str:
            responsibilities.append('组合优化')
        elif 'backtest' in path_str:
            responsibilities.append('回测系统')
        elif 'trade' in path_str:
            responsibilities.append('交易执行')
        elif 'audit' in path_str:
            responsibilities.append('审计系统')
        elif 'doc' in path_str:
            responsibilities.append('文档治理')
        else:
            responsibilities.append('系统架构')
    
    return responsibilities[:3]

def add_responsibility_to_yaml(content: str, responsibilities: List[str]) -> str:
    yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    
    if not yaml_match:
        return content
    
    yaml_content = yaml_match.group(1)
    
    if re.search(r'^responsibility:', yaml_content, re.MULTILINE):
        return content
    
    resp_yaml = 'responsibility:\n' + '\n'.join([f"  - {r}" for r in responsibilities])
    
    if re.search(r'^---\s*$', yaml_content, re.MULTILINE):
        yaml_content = resp_yaml + '\n' + yaml_content
    else:
        yaml_content = resp_yaml + '\n\n' + yaml_content
    
    return f"---\n{yaml_content}\n---" + content[yaml_match.end():]

def process_file(file_path: Path) -> Tuple[bool, str]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if has_responsibility(content):
            return True, "已有职责描述"
        
        responsibilities = infer_responsibility(file_path, content)
        new_content = add_responsibility_to_yaml(content, responsibilities)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, f"已添加职责: {', '.join(responsibilities)}"
        
    except Exception as e:
        return False, f"处理失败: {str(e)}"

def main():
    print("=" * 80)
    print("修复职责描述缺失")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"扫描目录: {DOCS_DIR}")
    print("=" * 80)
    
    stats = {
        "total_files": 0,
        "already_has": 0,
        "fixed": 0,
        "failed": 0
    }
    
    failed_files = []
    
    for root, dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = Path(root) / file
            rel_path = file_path.relative_to(DOCS_DIR)
            
            stats["total_files"] += 1
            
            success, message = process_file(file_path)
            
            if success:
                if "已有" in message:
                    stats["already_has"] += 1
                else:
                    stats["fixed"] += 1
                    print(f"✓ {rel_path}: {message}")
            else:
                stats["failed"] += 1
                failed_files.append((str(rel_path), message))
                print(f"✗ {rel_path}: {message}")
    
    print("\n" + "=" * 80)
    print("处理完成")
    print("=" * 80)
    print(f"总文件数: {stats['total_files']}")
    print(f"已有职责描述: {stats['already_has']}")
    print(f"已修复: {stats['fixed']}")
    print(f"失败: {stats['failed']}")
    
    if failed_files:
        print("\n失败文件列表:")
        for file_path, message in failed_files[:10]:
            print(f"  - {file_path}: {message}")
    
    print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
