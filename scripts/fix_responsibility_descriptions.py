"""
批量修复职责描述脚本
用途：为缺少职责描述的文档添加职责字段
创建时间：2026-04-07
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

PROJECT_ROOT = Path("D:/ZephyrAlpha")
DOCS_DIR = PROJECT_ROOT / "docs"

RESPONSIBILITY_KEYWORDS = {
    "数据质量": ["数据质量", "数据验证", "数据清洗", "数据监控", "数据完整性", "数据一致性", "异常检测"],
    "风险预算": ["风险预算", "风险分配", "风险控制", "风险管理", "风险约束", "风险限制"],
    "市场状态识别": ["市场状态", "市场识别", "市场分类", "regime", "市场环境"],
    "因子计算": ["因子", "factor", "alpha", "信号", "signal"],
    "组合优化": ["组合优化", "portfolio", "权重分配", "资产配置"],
    "交易执行": ["交易", "执行", "订单", "order", "撮合"],
    "回测系统": ["回测", "backtest", "历史测试", "策略验证"],
    "数据源": ["数据源", "数据接口", "api", "数据获取"],
    "特征工程": ["特征", "feature", "特征提取", "特征工程"],
    "机器学习": ["机器学习", "ml", "模型", "model", "训练", "预测"],
    "风险模型": ["风险模型", "risk model", "协方差", "covariance"],
    "绩效分析": ["绩效", "performance", "收益分析", "归因"],
    "系统架构": ["架构", "architecture", "系统设计", "模块"],
    "文档治理": ["文档", "document", "索引", "index"],
    "审计系统": ["审计", "audit", "检查", "check"],
    "配置管理": ["配置", "config", "参数", "parameter"],
    "日志系统": ["日志", "log", "监控", "monitor"],
    "测试系统": ["测试", "test", "单元测试", "集成测试"],
    "部署系统": ["部署", "deploy", "发布", "release"],
    "安全系统": ["安全", "security", "权限", "permission"]
}

def infer_responsibility(content: str, file_path: str) -> List[str]:
    responsibilities = []
    content_lower = content.lower()
    
    for responsibility, keywords in RESPONSIBILITY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in content_lower:
                if responsibility not in responsibilities:
                    responsibilities.append(responsibility)
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
        elif "test" in path_lower:
            responsibilities.append("测试系统")
        else:
            responsibilities.append("系统架构")
    
    return responsibilities[:3]

def has_responsibility_field(content: str) -> bool:
    yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not yaml_match:
        return False
    
    yaml_content = yaml_match.group(1)
    return bool(re.search(r'^responsibility:', yaml_content, re.MULTILINE))

def add_responsibility_to_yaml(content: str, responsibilities: List[str]) -> str:
    yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    
    if not yaml_match:
        yaml_header = f"""---
module_id: AUTO_GENERATED_001
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
        
        return yaml_header + content
    
    yaml_content = yaml_match.group(1)
    
    if re.search(r'^responsibility:', yaml_content, re.MULTILINE):
        return content
    
    responsibility_section = "responsibility:\n"
    for resp in responsibilities:
        responsibility_section += f"  - {resp}\n"
    
    if re.search(r'^owner:', yaml_content, re.MULTILINE):
        yaml_content = re.sub(
            r'(owner:.*?\n)',
            r'\1' + responsibility_section,
            yaml_content
        )
    elif re.search(r'^standard_type:', yaml_content, re.MULTILINE):
        yaml_content = re.sub(
            r'(standard_type:.*?\n)',
            r'\1' + responsibility_section,
            yaml_content
        )
    else:
        yaml_content += "\n" + responsibility_section
    
    return f"---\n{yaml_content}---\n" + content[yaml_match.end():]

def process_file(file_path: Path) -> Tuple[bool, str]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if has_responsibility_field(content):
            return True, "已有职责描述"
        
        responsibilities = infer_responsibility(content, str(file_path))
        
        if not responsibilities:
            return False, "无法推断职责"
        
        new_content = add_responsibility_to_yaml(content, responsibilities)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, f"已添加职责: {', '.join(responsibilities)}"
        
    except Exception as e:
        return False, f"处理失败: {str(e)}"

def main():
    print("=" * 80)
    print("批量修复职责描述")
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
