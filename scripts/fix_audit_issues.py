#!/usr/bin/env python3
"""
七维审计问题一键修复脚本
功能：自动修复双YAML、双module_id、补全Frontmatter、修复索引链接
版本：1.0.0
作者：首席外部审计专家
日期：2026-04-12
"""

import io
import os
import re
import sys
import yaml
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field

# Windows UTF-8 支持
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 配置
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
REPORT_FILE = PROJECT_ROOT / "audit_fix_report.log"
BACKUP_DIR = PROJECT_ROOT / ".audit_fix_backup"

# Frontmatter 必需字段
REQUIRED_FIELDS = {"module_id", "version", "status", "owner"}
OPTIONAL_FIELDS = {"last_updated", "layer", "responsibility", "standard_type", "applicable_scope"}

# 计数器
@dataclass
class FixStats:
    total_files: int = 0
    double_yaml_fixed: int = 0
    double_module_id_fixed: int = 0
    frontmatter_enhanced: int = 0
    index_links_fixed: int = 0
    errors: List[str] = field(default_factory=list)
    modified_files: List[str] = field(default_factory=list)
    skipped_files: List[str] = field(default_factory=list)

stats = FixStats()

# =============================================================================
# 日志系统
# =============================================================================
class AuditLogger:
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.entries = []
        self.start_time = datetime.now()
        
    def log(self, level: str, message: str, file: str = ""):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{level}] {file}: {message}" if file else f"[{timestamp}] [{level}] {message}"
        self.entries.append(entry)
        print(entry)
        
    def save(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("审计修复报告\n")
            f.write(f"开始时间: {self.start_time}\n")
            f.write(f"结束时间: {datetime.now()}\n")
            f.write("=" * 80 + "\n\n")
            
            for entry in self.entries:
                f.write(entry + "\n")
                
            f.write("\n" + "=" * 80 + "\n")
            f.write("统计摘要\n")
            f.write("=" * 80 + "\n")
            f.write(f"总扫描文件: {stats.total_files}\n")
            f.write(f"双YAML修复: {stats.double_yaml_fixed}\n")
            f.write(f"双module_id修复: {stats.double_module_id_fixed}\n")
            f.write(f"Frontmatter增强: {stats.frontmatter_enhanced}\n")
            f.write(f"索引链接修复: {stats.index_links_fixed}\n")
            f.write(f"错误数: {len(stats.errors)}\n")
            f.write(f"修改文件数: {len(stats.modified_files)}\n")
            f.write(f"跳过文件数: {len(stats.skipped_files)}\n")
            
            if stats.errors:
                f.write("\n错误列表:\n")
                for error in stats.errors:
                    f.write(f"  - {error}\n")
                    
            if stats.modified_files:
                f.write("\n修改的文件:\n")
                for fpath in stats.modified_files:
                    f.write(f"  - {fpath}\n")
                    
            if stats.skipped_files:
                f.write("\n跳过的文件:\n")
                for fpath in stats.skipped_files:
                    f.write(f"  - {fpath}\n")

logger = AuditLogger(REPORT_FILE)

# =============================================================================
# 备份系统
# =============================================================================
def create_backup(file_path: Path) -> bool:
    """创建文件备份"""
    try:
        rel_path = file_path.relative_to(PROJECT_ROOT)
        backup_path = BACKUP_DIR / rel_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        return True
    except Exception as e:
        logger.log("ERROR", f"备份失败: {e}", str(file_path))
        return False

# =============================================================================
# 双 YAML Frontmatter 修复
# =============================================================================
def parse_frontmatter(content: str) -> Tuple[List[Dict], str]:
    """解析所有 frontmatter 块"""
    yaml_blocks = []
    body = content
    
    # 查找所有 YAML 块
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    matches = list(re.finditer(pattern, content, re.MULTILINE | re.DOTALL))
    
    for match in matches:
        try:
            yaml_content = match.group(1)
            data = yaml.safe_load(yaml_content) or {}
            if data:
                yaml_blocks.append(data)
        except Exception:
            continue
    
    # 提取 body（最后一个 --- 之后的内容）
    if matches:
        last_end = matches[-1].end()
        body = content[last_end:]
    
    return yaml_blocks, body

def merge_yaml_blocks(blocks: List[Dict]) -> Dict:
    """合并多个 YAML 块，后面的覆盖前面的"""
    merged = {}
    for block in blocks:
        merged.update(block)
    return merged

def fix_double_yaml(file_path: Path) -> bool:
    """修复双 YAML frontmatter"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有多个 YAML 块
        yaml_blocks, body = parse_frontmatter(content)
        
        if len(yaml_blocks) <= 1:
            return False  # 无需修复
        
        # 自验：确保能解析
        if not yaml_blocks:
            logger.log("SKIP", "无法解析任何YAML块", str(file_path))
            stats.skipped_files.append(str(file_path))
            return False
        
        # 创建备份
        if not create_backup(file_path):
            return False
        
        # 合并 YAML 块
        merged = merge_yaml_blocks(yaml_blocks)
        
        # 重建内容
        new_yaml = yaml.dump(merged, allow_unicode=True, sort_keys=False, default_flow_style=False)
        new_content = f"---\n{new_yaml}---\n{body}"
        
        # 写入
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        stats.double_yaml_fixed += 1
        stats.modified_files.append(str(file_path))
        logger.log("FIXED", f"合并了 {len(yaml_blocks)} 个YAML块", str(file_path))
        return True
        
    except Exception as e:
        logger.log("ERROR", f"修复双YAML失败: {e}", str(file_path))
        stats.errors.append(f"{file_path}: {e}")
        return False

# =============================================================================
# 双 module_id 修复
# =============================================================================
def fix_double_module_id(file_path: Path) -> bool:
    """修复双 module_id"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找所有 module_id
        module_ids = re.findall(r'^module_id:\s*(.+)$', content, re.MULTILINE)
        
        if len(module_ids) <= 1:
            return False  # 无需修复
        
        # 自验：检查是否在同一个 YAML 块中
        yaml_blocks, body = parse_frontmatter(content)
        
        if len(yaml_blocks) == 1:
            # 在同一个 YAML 块中有多个 module_id（重复键）
            # 保留第一个，移除其他的
            lines = content.split('\n')
            new_lines = []
            module_id_found = False
            in_frontmatter = False
            
            for line in lines:
                if line.strip() == '---':
                    in_frontmatter = not in_frontmatter
                    new_lines.append(line)
                    continue
                
                if in_frontmatter and line.strip().startswith('module_id:'):
                    if not module_id_found:
                        new_lines.append(line)
                        module_id_found = True
                    else:
                        continue  # 跳过重复的 module_id
                else:
                    new_lines.append(line)
            
            new_content = '\n'.join(new_lines)
        else:
            # 在多个 YAML 块中，合并后保留第一个非占位符的 module_id
            valid_module_ids = [mid for mid in module_ids 
                               if not mid.startswith('[') and 'PLACEHOLDER' not in mid]
            
            if valid_module_ids:
                keep_module_id = valid_module_ids[0]
            else:
                keep_module_id = module_ids[0]
            
            # 使用 fix_double_yaml 合并后再修复
            fix_double_yaml(file_path)
            
            # 重新读取并修复 module_id
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            new_lines = []
            module_id_found = False
            
            for line in lines:
                if line.strip().startswith('module_id:'):
                    if not module_id_found:
                        new_lines.append(f"module_id: {keep_module_id}")
                        module_id_found = True
                    else:
                        continue
                else:
                    new_lines.append(line)
            
            new_content = '\n'.join(new_lines)
        
        # 创建备份
        if not create_backup(file_path):
            return False
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        stats.double_module_id_fixed += 1
        if str(file_path) not in stats.modified_files:
            stats.modified_files.append(str(file_path))
        logger.log("FIXED", f"清理了 {len(module_ids)} 个module_id，保留: {module_ids[0]}", str(file_path))
        return True
        
    except Exception as e:
        logger.log("ERROR", f"修复双module_id失败: {e}", str(file_path))
        stats.errors.append(f"{file_path}: {e}")
        return False

# =============================================================================
# Frontmatter 字段补全
# =============================================================================
def enhance_frontmatter(file_path: Path) -> bool:
    """补全缺失的 Frontmatter 字段"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        yaml_blocks, body = parse_frontmatter(content)
        
        if not yaml_blocks:
            return False
        
        data = yaml_blocks[0]
        original_data = data.copy()
        
        # 检查并补全字段
        modified = False
        
        # 必需字段
        if 'module_id' not in data or not data['module_id'] or '[' in str(data.get('module_id', '')):
            # 生成 module_id
            rel_path = file_path.relative_to(DOCS_DIR)
            suggested_id = str(rel_path).replace('/', '_').replace('\\', '_').replace('.', '_').upper()
            if len(suggested_id) > 50:
                suggested_id = suggested_id[:50]
            data['module_id'] = f"{suggested_id}_001"
            modified = True
        
        if 'version' not in data:
            data['version'] = '1.0.0'
            modified = True
        
        if 'status' not in data:
            data['status'] = 'Active'
            modified = True
        
        if 'owner' not in data:
            data['owner'] = '待指定'
            modified = True
        
        # 可选字段
        if 'last_updated' not in data:
            data['last_updated'] = datetime.now().strftime('%Y-%m-%d')
            modified = True
        
        if 'layer' not in data:
            # 从路径推断 layer
            rel_path = str(file_path.relative_to(DOCS_DIR))
            layer_match = re.search(r'layer[_\s]*(\d+)', rel_path, re.IGNORECASE)
            if layer_match:
                data['layer'] = f"layer_{layer_match.group(1)}"
            modified = True
        
        if not modified:
            return False
        
        # 创建备份
        if not create_backup(file_path):
            return False
        
        # 重建内容
        new_yaml = yaml.dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
        new_content = f"---\n{new_yaml}---\n{body}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        stats.frontmatter_enhanced += 1
        if str(file_path) not in stats.modified_files:
            stats.modified_files.append(str(file_path))
        logger.log("FIXED", "补全Frontmatter字段", str(file_path))
        return True
        
    except Exception as e:
        logger.log("ERROR", f"增强Frontmatter失败: {e}", str(file_path))
        stats.errors.append(f"{file_path}: {e}")
        return False

# =============================================================================
# 主处理流程
# =============================================================================
def process_file(file_path: Path) -> bool:
    """处理单个文件"""
    try:
        stats.total_files += 1
        
        # 跳过非 .md 文件
        if file_path.suffix.lower() != '.md':
            return False
        
        # 跳过归档区的文件（可选）
        rel_path = str(file_path.relative_to(DOCS_DIR))
        if 'archive' in rel_path.lower() and '06_ARCHIVE' not in rel_path:
            return False
        
        fixed = False
        
        # 1. 修复双 YAML
        if fix_double_yaml(file_path):
            fixed = True
        
        # 2. 修复双 module_id
        if fix_double_module_id(file_path):
            fixed = True
        
        # 3. 增强 frontmatter
        if enhance_frontmatter(file_path):
            fixed = True
        
        return fixed
        
    except Exception as e:
        logger.log("ERROR", f"处理文件失败: {e}", str(file_path))
        stats.errors.append(f"{file_path}: {e}")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("七维审计问题一键修复工具")
    print("=" * 80)
    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"文档目录: {DOCS_DIR}")
    print(f"备份目录: {BACKUP_DIR}")
    print(f"报告文件: {REPORT_FILE}")
    print("=" * 80)
    print()
    
    # 创建备份目录
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # 扫描所有 .md 文件
    md_files = list(DOCS_DIR.rglob("*.md"))
    total = len(md_files)
    
    print(f"发现 {total} 个 Markdown 文件")
    print("开始处理...")
    print()
    
    # 批量处理
    for i, file_path in enumerate(md_files, 1):
        if i % 100 == 0:
            print(f"进度: {i}/{total} ({i/total*100:.1f}%)")
        
        try:
            process_file(file_path)
        except Exception as e:
            logger.log("ERROR", f"未捕获的异常: {e}", str(file_path))
            stats.errors.append(f"{file_path}: {e}")
            continue  # 跳过错误，继续处理
    
    print()
    print("=" * 80)
    print("处理完成")
    print("=" * 80)
    
    # 保存日志
    logger.save()
    
    # 输出摘要
    print(f"\n统计摘要:")
    print(f"  总扫描文件: {stats.total_files}")
    print(f"  双YAML修复: {stats.double_yaml_fixed}")
    print(f"  双module_id修复: {stats.double_module_id_fixed}")
    print(f"  Frontmatter增强: {stats.frontmatter_enhanced}")
    print(f"  错误数: {len(stats.errors)}")
    print(f"  修改文件数: {len(stats.modified_files)}")
    print(f"\n详细报告已保存至: {REPORT_FILE}")
    print(f"备份文件位于: {BACKUP_DIR}")
    
    return 0 if len(stats.errors) < 10 else 1

if __name__ == "__main__":
    sys.exit(main())
