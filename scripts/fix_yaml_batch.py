#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YAML字段批量修复脚本
自动修复蓝图文件的YAML头部字段和变更历史

使用方法:
    python fix_yaml_batch.py [--dry-run] [--limit N]

参数:
    --dry-run: 只预览修复内容，不实际修改文件
    --limit N: 只处理前N个文件（用于测试）
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass

@dataclass
class FixResult:
    """修复结果"""
    file_path: str
    module_id: str
    yaml_fixed: bool = False
    history_added: bool = False
    encoding_fixed: bool = False
    error: str = ""

class YAMLBatchFixer:
    """YAML批量修复器"""
    
    def __init__(self, blueprints_dir: str):
        self.blueprints_dir = Path(blueprints_dir)
        self.results: List[FixResult] = []
        
        # 标准YAML字段模板
        self.standard_fields = {
            "status": "Active",
            "standard_type": "专业量化机构蓝图",
            "compliance_level": "专业标准",
            "parent_document": "../INDEX.md",
            "implementation_status": "设计阶段"
        }
        
        # 推荐字段默认值
        self.recommended_defaults = {
            "open_source_dependency": "待补充",
            "estimated_effort": "待评估",
            "priority": "P1"
        }
    
    def fix_yaml_syntax(self, yaml_content: str) -> str:
        """修复YAML语法问题"""
        lines = yaml_content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 修复包含 | 的字段值（需要加引号）
            if ':' in line and '|' in line and not line.strip().startswith('#'):
                # 检查是否已经有引号
                if '"' not in line and "'" not in line:
                    # 分割键值
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0]
                        value = parts[1].strip()
                        # 如果值包含特殊字符，添加引号
                        if any(char in value for char in ['|', ':', '#', '{', '}', '[', ']']):
                            line = f'{key}: "{value}"'
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def extract_yaml_block(self, content: str) -> Tuple[Optional[str], str, str]:
        """提取YAML头部块，返回(yaml_block, remaining_content, original_yaml)"""
        yaml_pattern = r'^---\s*\n(.*?)\n---'
        match = re.match(yaml_pattern, content, re.DOTALL)
        if match:
            return match.group(1), content[match.end():], match.group(0)
        return None, content, ""
    
    def read_file_with_encoding(self, file_path: Path) -> Tuple[Optional[str], str]:
        """尝试多种编码读取文件"""
        encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                return content, encoding
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        return None, ""
    
    def fix_file(self, file_path: Path, dry_run: bool = False) -> FixResult:
        """修复单个文件"""
        result = FixResult(file_path=str(file_path), module_id="UNKNOWN")
        
        try:
            # 读取文件
            content, encoding = self.read_file_with_encoding(file_path)
            if content is None:
                result.error = "无法读取文件"
                return result
            
            # 提取YAML块
            yaml_block, remaining_content, original_yaml = self.extract_yaml_block(content)
            
            if yaml_block is None:
                result.error = "未找到YAML头部块"
                return result
            
            # 修复YAML语法
            fixed_yaml_block = self.fix_yaml_syntax(yaml_block)
            
            # 解析YAML
            try:
                yaml_data = yaml.safe_load(fixed_yaml_block)
                if not isinstance(yaml_data, dict):
                    result.error = "YAML格式错误"
                    return result
            except yaml.YAMLError as e:
                result.error = f"YAML解析错误: {str(e)}"
                return result
            
            # 提取module_id
            result.module_id = yaml_data.get('module_id', 'UNKNOWN')
            
            # 补充缺失的标准字段
            yaml_modified = False
            for field, default_value in self.standard_fields.items():
                if field not in yaml_data or not yaml_data[field]:
                    yaml_data[field] = default_value
                    yaml_modified = True
            
            # 补充推荐字段
            for field, default_value in self.recommended_defaults.items():
                if field not in yaml_data:
                    yaml_data[field] = default_value
                    yaml_modified = True
            
            # 更新last_updated
            yaml_data['last_updated'] = datetime.now().strftime('%Y-%m-%d')
            yaml_modified = True
            
            if yaml_modified:
                result.yaml_fixed = True
            
            # 检查并添加变更历史
            history_patterns = [
                r'##\s*\d+\.\s*变更历史',
                r'##\s*变更历史',
                r'##\s*版本历史'
            ]
            
            has_history = any(
                re.search(pattern, remaining_content) 
                for pattern in history_patterns
            )
            
            if not has_history:
                # 添加变更历史
                history_section = self.generate_change_history(yaml_data)
                remaining_content = remaining_content.rstrip() + "\n\n" + history_section
                result.history_added = True
            
            # 重新生成YAML
            new_yaml = "---\n" + yaml.dump(yaml_data, allow_unicode=True, sort_keys=False) + "---\n"
            
            # 组合新内容
            new_content = new_yaml + remaining_content
            
            # 写入文件
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                result.encoding_fixed = (encoding != 'utf-8')
            
        except Exception as e:
            result.error = f"处理错误: {str(e)}"
        
        return result
    
    def generate_change_history(self, yaml_data: Dict) -> str:
        """生成变更历史章节"""
        created_date = yaml_data.get('created_date', datetime.now().strftime('%Y-%m-%d'))
        owner = yaml_data.get('owner', '负责人')
        
        return f"""## 变更历史

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | {created_date} | 初始版本创建 | {owner} |
| v1.0.1 | {datetime.now().strftime('%Y-%m-%d')} | 补充YAML头部字段和变更历史 | 审计系统 |

---

**蓝图版本**: v1.0.1 | **创建日期**: {created_date} | **状态**: Active
"""
    
    def fix_all(self, dry_run: bool = False, limit: Optional[int] = None) -> List[FixResult]:
        """批量修复所有文件"""
        blueprint_files = list(self.blueprints_dir.glob("*_BLUEPRINT.md"))
        
        if limit:
            blueprint_files = blueprint_files[:limit]
        
        print(f"[INFO] 找到 {len(blueprint_files)} 个蓝图文件")
        if dry_run:
            print("[INFO] 预览模式：不会实际修改文件")
        
        for i, file_path in enumerate(blueprint_files, 1):
            print(f"\n[{i}/{len(blueprint_files)}] 处理: {file_path.name}")
            result = self.fix_file(file_path, dry_run)
            self.results.append(result)
            
            if result.error:
                error_msg = result.error.encode('gbk', errors='ignore').decode('gbk')
                print(f"  [ERROR] 错误: {error_msg}")
            else:
                fixes = []
                if result.yaml_fixed:
                    fixes.append("YAML字段已补充")
                if result.history_added:
                    fixes.append("变更历史已添加")
                if result.encoding_fixed:
                    fixes.append("编码已转换为UTF-8")
                
                if fixes:
                    print(f"  [OK] {'; '.join(fixes)}")
                else:
                    print(f"  [INFO] 无需修复")
        
        return self.results
    
    def generate_summary(self) -> str:
        """生成修复摘要"""
        total = len(self.results)
        yaml_fixed = sum(1 for r in self.results if r.yaml_fixed)
        history_added = sum(1 for r in self.results if r.history_added)
        encoding_fixed = sum(1 for r in self.results if r.encoding_fixed)
        errors = sum(1 for r in self.results if r.error)
        
        summary = [
            "\n" + "="*60,
            "修复摘要",
            "="*60,
            f"总文件数: {total}",
            f"YAML字段已补充: {yaml_fixed}",
            f"变更历史已添加: {history_added}",
            f"编码已转换: {encoding_fixed}",
            f"处理失败: {errors}",
            "="*60
        ]
        
        return "\n".join(summary)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='YAML字段批量修复工具')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不实际修改文件')
    parser.add_argument('--limit', type=int, help='只处理前N个文件')
    
    args = parser.parse_args()
    
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    blueprints_dir = project_root / "docs" / "05_IMPLEMENTATION" / "06_CONSTRUCTION_DOCS" / "01_BLUEPRINTS"
    
    print(f"[INFO] 开始批量修复YAML字段...")
    print(f"[INFO] 蓝图目录: {blueprints_dir}")
    
    fixer = YAMLBatchFixer(str(blueprints_dir))
    results = fixer.fix_all(dry_run=args.dry_run, limit=args.limit)
    
    print(fixer.generate_summary())
    
    if args.dry_run:
        print("\n[INFO] 提示: 这是预览模式。要实际修复文件，请去掉 --dry-run 参数")

if __name__ == "__main__":
    main()
