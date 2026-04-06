"""
修复YAML头部缺失问题脚本
用途：为缺少YAML头部的文档添加标准头部
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from typing import Tuple
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

def has_yaml_header(content: str) -> bool:
    return bool(re.match(r'^---\s*\n.*?\n---', content, re.DOTALL))

def infer_module_id(file_path: Path) -> str:
    file_name = file_path.stem
    file_name = re.sub(r'[^a-zA-Z0-9_]', '_', file_name)
    file_name = re.sub(r'_+', '_', file_name)
    file_name = file_name.strip('_').upper()
    
    if not file_name:
        file_name = "MODULE"
    
    return f"{file_name}_001"

def infer_responsibility(content: str, file_path: str) -> list:
    responsibilities = []
    content_lower = content.lower()
    
    keywords_map = {
        "数据质量": ["数据质量", "数据验证", "数据清洗", "数据监控"],
        "风险预算": ["风险预算", "风险分配", "风险控制", "风险管理"],
        "市场状态识别": ["市场状态", "市场识别", "regime"],
        "因子计算": ["因子", "factor", "alpha", "信号"],
        "组合优化": ["组合优化", "portfolio", "权重分配"],
        "交易执行": ["交易", "执行", "订单", "order"],
        "回测系统": ["回测", "backtest"],
        "数据源": ["数据源", "数据接口", "api"],
        "特征工程": ["特征", "feature"],
        "机器学习": ["机器学习", "ml", "模型", "model"],
        "风险模型": ["风险模型", "risk model"],
        "绩效分析": ["绩效", "performance"],
        "系统架构": ["架构", "architecture"],
        "文档治理": ["文档", "document", "索引"],
        "审计系统": ["审计", "audit"],
        "配置管理": ["配置", "config"],
        "日志系统": ["日志", "log"],
        "测试系统": ["测试", "test"],
        "部署系统": ["部署", "deploy"],
        "安全系统": ["安全", "security"]
    }
    
    for resp, keywords in keywords_map.items():
        for keyword in keywords:
            if keyword.lower() in content_lower:
                if resp not in responsibilities:
                    responsibilities.append(resp)
                break
    
    if not responsibilities:
        path_lower = file_path.lower()
        if "factor" in path_lower or "alpha" in path_lower:
            responsibilities.append("因子计算")
        elif "risk" in path_lower:
            responsibilities.append("风险预算")
        elif "data" in path_lower:
            responsibilities.append("数据质量")
        elif "portfolio" in path_lower:
            responsibilities.append("组合优化")
        elif "backtest" in path_lower:
            responsibilities.append("回测系统")
        elif "trade" in path_lower:
            responsibilities.append("交易执行")
        elif "audit" in path_lower:
            responsibilities.append("审计系统")
        elif "doc" in path_lower:
            responsibilities.append("文档治理")
        else:
            responsibilities.append("系统架构")
    
    return responsibilities[:3]

def create_yaml_header(file_path: Path, content: str) -> str:
    module_id = infer_module_id(file_path)
    responsibilities = infer_responsibility(content, str(file_path))
    
    yaml_header = f"""---
module_id: {module_id}
version: 1.0.0
status: Active
created_date: {datetime.now().strftime('%Y-%m-%d')}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
"""
    
    for resp in responsibilities:
        yaml_header += f"  - {resp}\n"
    
    yaml_header += "---\n\n"
    
    return yaml_header

def process_file(file_path: Path) -> Tuple[bool, str]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if has_yaml_header(content):
            return True, "已有YAML头部"
        
        yaml_header = create_yaml_header(file_path, content)
        new_content = yaml_header + content
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, "已添加YAML头部"
        
    except UnicodeDecodeError as e:
        return False, f"编码错误: {str(e)}"
    except Exception as e:
        return False, f"处理失败: {str(e)}"

def main():
    print("=" * 80)
    print("修复YAML头部缺失问题")
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
    print(f"已有YAML头部: {stats['already_has']}")
    print(f"已修复: {stats['fixed']}")
    print(f"失败: {stats['failed']}")
    
    if failed_files:
        print("\n失败文件列表:")
        for file_path, message in failed_files[:10]:
            print(f"  - {file_path}: {message}")
    
    print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
