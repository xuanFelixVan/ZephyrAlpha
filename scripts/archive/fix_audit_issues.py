#!/usr/bin/env python3
"""
七维审计问题一键修复脚本 v2.0
功能：自动修复双YAML、双module_id、补全Frontmatter、修复闭合标记粘合、
      修复字段间空行、修复列表类型Frontmatter、检测编码损坏
版本：2.0.0
日期：2026-04-13
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

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
REPORT_FILE = PROJECT_ROOT / "audit_fix_report.log"
BACKUP_DIR = PROJECT_ROOT / ".audit_fix_backup"

REQUIRED_FIELDS = {"module_id", "version", "status", "owner"}
OPTIONAL_FIELDS = {"last_updated", "layer", "responsibility", "standard_type", "applicable_scope"}

MOJIBAKE_PATTERN = re.compile(r'[ÒÓÔÕÖÙÚÛÜÝàáâãäåèéêëìíîïòóôõöùúûüýÿĂăĄąĆćČčĎďĐđĘęĚěĹĺĽľŁłŃńŇňŐőŘřŚśŞşŠšŤťŮůŰűŹźŻżŽžƒȘșȚț]')

@dataclass
class FixStats:
    total_files: int = 0
    double_yaml_fixed: int = 0
    double_module_id_fixed: int = 0
    frontmatter_enhanced: int = 0
    closed_tag_glue_fixed: int = 0
    blank_line_frontmatter_fixed: int = 0
    list_frontmatter_fixed: int = 0
    encoding_corrupted: int = 0
    errors: List[str] = field(default_factory=list)
    modified_files: List[str] = field(default_factory=list)
    skipped_files: List[str] = field(default_factory=list)

stats = FixStats()

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
            f.write("审计修复报告 v2.0\n")
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
            f.write(f"闭合标记粘合修复: {stats.closed_tag_glue_fixed}\n")
            f.write(f"字段间空行修复: {stats.blank_line_frontmatter_fixed}\n")
            f.write(f"列表类型Frontmatter修复: {stats.list_frontmatter_fixed}\n")
            f.write(f"编码损坏文件: {stats.encoding_corrupted}\n")
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

def create_backup(file_path: Path) -> bool:
    try:
        rel_path = file_path.relative_to(PROJECT_ROOT)
        backup_path = BACKUP_DIR / rel_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        if not backup_path.exists():
            shutil.copy2(file_path, backup_path)
        return True
    except Exception as e:
        logger.log("ERROR", f"备份失败: {e}", str(file_path))
        return False

def is_mojibake(text: str) -> bool:
    if MOJIBAKE_PATTERN.search(text):
        return True
    try:
        sample = text[:500]
        latin1_count = sum(1 for c in sample if ord(c) > 127 and ord(c) < 0x400)
        cjk_count = sum(1 for c in sample if ord(c) >= 0x4E00 and ord(c) <= 0x9FFF)
        if latin1_count > 5 and cjk_count == 0:
            return True
    except Exception:
        pass
    return False

def extract_raw_frontmatter(content: str) -> Tuple[Optional[str], str]:
    if not content.startswith('---'):
        return None, content
    lines = content.split('\n')
    end_idx = None
    for i in range(1, len(lines)):
        stripped = lines[i].rstrip()
        if stripped == '---':
            end_idx = i
            break
    if end_idx is None:
        for i in range(1, len(lines)):
            stripped = lines[i].rstrip()
            if stripped.endswith('---'):
                end_idx = i
                break
    if end_idx is None:
        return None, content
    yaml_text = '\n'.join(lines[1:end_idx])
    body = '\n'.join(lines[end_idx + 1:])
    return yaml_text, body

def fix_closed_tag_glue(yaml_text: str) -> Tuple[str, bool]:
    fixed = False
    lines = yaml_text.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.rstrip()
        if stripped.endswith('---') and stripped != '---':
            value_part = stripped[:-3].rstrip()
            if value_part:
                new_lines.append(value_part)
            fixed = True
        else:
            new_lines.append(line)
    return '\n'.join(new_lines), fixed

def fix_blank_lines_in_frontmatter(yaml_text: str) -> Tuple[str, bool]:
    lines = yaml_text.split('\n')
    if not any(line.strip() == '' for line in lines):
        return yaml_text, False
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped == '':
            continue
        new_lines.append(line)
    result = '\n'.join(new_lines)
    if result != yaml_text:
        return result, True
    return yaml_text, False

def fix_list_frontmatter(yaml_text: str) -> Tuple[str, bool]:
    lines = yaml_text.split('\n')
    list_items = [l for l in lines if l.strip().startswith('- ')]
    if not list_items:
        return yaml_text, False
    non_list = [l for l in lines if not l.strip().startswith('- ') and l.strip() != '']
    if not non_list and list_items:
        new_lines = []
        for item in list_items:
            stripped = item.strip()[2:].strip()
            if ':' in stripped:
                new_lines.append(stripped)
            else:
                new_lines.append(item)
        return '\n'.join(new_lines), True
    return yaml_text, False

def extract_yaml_key_value_lines(yaml_text: str) -> Tuple[str, bool]:
    lines = yaml_text.split('\n')
    clean_lines = []
    fixed = False
    for line in lines:
        stripped = line.strip()
        if stripped == '':
            continue
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*:', stripped):
            parts = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*:\s*[^\s]*(?:\s+(?![a-zA-Z_][a-zA-Z0-9_]*:)[^\s]*)*)', stripped)
            if len(parts) > 1:
                for part in parts:
                    clean_lines.append(part.strip())
                fixed = True
            else:
                clean_lines.append(line)
        elif stripped.startswith('- ') and clean_lines and (clean_lines[-1].rstrip().endswith(':') or clean_lines[-1].startswith(' ')):
            clean_lines.append(line)
        elif stripped.startswith('  '):
            clean_lines.append(line)
        else:
            fixed = True
    result = '\n'.join(clean_lines)
    if fixed:
        return result, True
    return yaml_text, False

def parse_yaml_safe(yaml_text: str) -> Tuple[Optional[Dict], bool]:
    try:
        data = yaml.safe_load(yaml_text)
        if isinstance(data, dict):
            return data, True
        if isinstance(data, list):
            merged = {}
            for item in data:
                if isinstance(item, dict):
                    merged.update(item)
                elif isinstance(item, str) and ':' in item:
                    key, _, val = item.partition(':')
                    merged[key.strip()] = val.strip()
            if merged:
                return merged, True
            return None, False
        if isinstance(data, str) and ':' in data:
            result = {}
            for line in data.split('\n'):
                if ':' in line:
                    key, _, val = line.partition(':')
                    result[key.strip()] = val.strip()
            if result:
                return result, True
        return None, False
    except Exception:
        return None, False

def parse_frontmatter_robust(content: str) -> Tuple[List[Dict], str]:
    yaml_blocks = []
    body = content

    pattern = r'^---\s*\n(.*?)\n---\s*[\n]?'
    matches = list(re.finditer(pattern, content, re.MULTILINE | re.DOTALL))

    if matches:
        for match in matches:
            yaml_content = match.group(1)
            data, ok = parse_yaml_safe(yaml_content)
            if ok and data:
                yaml_blocks.append(data)
        last_end = matches[-1].end()
        body = content[last_end:]
        return yaml_blocks, body

    raw_yaml, body = extract_raw_frontmatter(content)
    if raw_yaml is not None:
        yaml_cleaned, _ = fix_closed_tag_glue(raw_yaml)
        yaml_cleaned, _ = fix_blank_lines_in_frontmatter(yaml_cleaned)
        yaml_cleaned, _ = fix_list_frontmatter(yaml_cleaned)
        data, ok = parse_yaml_safe(yaml_cleaned)
        if ok and data:
            yaml_blocks.append(data)
        return yaml_blocks, body

    return yaml_blocks, body

def fix_frontmatter_structural(file_path: Path) -> bool:
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        if not content.startswith('---'):
            return False

        raw_yaml, body = extract_raw_frontmatter(content)
        if raw_yaml is None:
            return False

        if is_mojibake(raw_yaml):
            stats.encoding_corrupted += 1
            logger.log("WARN", "检测到编码损坏(mojibake)，跳过自动修复", str(file_path))
            stats.skipped_files.append(str(file_path))
            return False

        any_fixed = False
        yaml_text = raw_yaml

        yaml_text, glue_fixed = fix_closed_tag_glue(yaml_text)
        if glue_fixed:
            any_fixed = True
            stats.closed_tag_glue_fixed += 1
            logger.log("FIXED", "修复闭合标记粘合", str(file_path))

        yaml_text, blank_fixed = fix_blank_lines_in_frontmatter(yaml_text)
        if blank_fixed:
            any_fixed = True
            stats.blank_line_frontmatter_fixed += 1
            logger.log("FIXED", "修复字段间空行", str(file_path))

        yaml_text, list_fixed = fix_list_frontmatter(yaml_text)
        if list_fixed:
            any_fixed = True
            stats.list_frontmatter_fixed += 1
            logger.log("FIXED", "修复列表类型Frontmatter", str(file_path))

        yaml_text, kv_fixed = extract_yaml_key_value_lines(yaml_text)
        if kv_fixed:
            any_fixed = True
            logger.log("FIXED", "清理Frontmatter中混入的非YAML内容", str(file_path))

        data, ok = parse_yaml_safe(yaml_text)
        if not ok or not data:
            if any_fixed:
                logger.log("WARN", "结构修复后仍无法解析YAML，尝试强制重建", str(file_path))
                data = rebuild_frontmatter(yaml_text, file_path)
                if data:
                    any_fixed = True
                else:
                    return False

        if not any_fixed:
            data, ok = parse_yaml_safe(yaml_text)
            if ok and isinstance(data, dict):
                return False
            data = rebuild_frontmatter(yaml_text, file_path)
            if not data:
                return False
            any_fixed = True
            logger.log("FIXED", "强制重建损坏的Frontmatter", str(file_path))

        if not create_backup(file_path):
            return False

        new_yaml = yaml.dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
        new_content = f"---\n{new_yaml}---\n{body}"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        if str(file_path) not in stats.modified_files:
            stats.modified_files.append(str(file_path))
        return True

    except Exception as e:
        logger.log("ERROR", f"结构修复失败: {e}", str(file_path))
        stats.errors.append(f"{file_path}: {e}")
        return False

def rebuild_frontmatter(yaml_text: str, file_path: Path) -> Optional[Dict]:
    data = {}
    lines = yaml_text.split('\n')
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        m = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)', stripped)
        if not m:
            continue
        key = m.group(1)
        val = m.group(2).strip()
        if val.startswith("'") and val.endswith("'"):
            val = val[1:-1]
        elif val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        if key in data:
            continue
        if key == 'responsibility' and re.search(r'[a-zA-Z_][a-zA-Z0-9_]*:', val):
            continue
        if is_mojibake(val):
            continue
        data[key] = val
    if not data:
        return None
    rel_path = file_path.relative_to(DOCS_DIR)
    if 'module_id' not in data or not data['module_id'] or '[' in str(data.get('module_id', '')):
        suggested_id = str(rel_path).replace('/', '_').replace('\\', '_').replace('.', '_').upper()
        if len(suggested_id) > 50:
            suggested_id = suggested_id[:50]
        data['module_id'] = f"{suggested_id}_001"
    if 'version' not in data:
        data['version'] = '1.0.0'
    if 'status' not in data:
        data['status'] = 'Active'
    if 'owner' not in data:
        data['owner'] = '待指定'
    if 'last_updated' not in data:
        data['last_updated'] = datetime.now().strftime('%Y-%m-%d')
    if 'layer' not in data:
        rel_str = str(rel_path)
        layer_match = re.search(r'layer[_\s]*(\d+)', rel_str, re.IGNORECASE)
        if layer_match:
            data['layer'] = f"layer_{layer_match.group(1)}"
    return data

def parse_frontmatter(content: str) -> Tuple[List[Dict], str]:
    return parse_frontmatter_robust(content)

def merge_yaml_blocks(blocks: List[Dict]) -> Dict:
    merged = {}
    for block in blocks:
        if isinstance(block, dict):
            merged.update(block)
    return merged

def fix_double_yaml(file_path: Path) -> bool:
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        yaml_blocks, body = parse_frontmatter(content)

        if len(yaml_blocks) <= 1:
            return False

        if not yaml_blocks:
            logger.log("SKIP", "无法解析任何YAML块", str(file_path))
            stats.skipped_files.append(str(file_path))
            return False

        if not create_backup(file_path):
            return False

        merged = merge_yaml_blocks(yaml_blocks)

        new_yaml = yaml.dump(merged, allow_unicode=True, sort_keys=False, default_flow_style=False)
        new_content = f"---\n{new_yaml}---\n{body}"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        stats.double_yaml_fixed += 1
        if str(file_path) not in stats.modified_files:
            stats.modified_files.append(str(file_path))
        logger.log("FIXED", f"合并了 {len(yaml_blocks)} 个YAML块", str(file_path))
        return True

    except Exception as e:
        logger.log("ERROR", f"修复双YAML失败: {e}", str(file_path))
        stats.errors.append(f"{file_path}: {e}")
        return False

def fix_double_module_id(file_path: Path) -> bool:
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        module_ids = re.findall(r'^module_id:\s*(.+)$', content, re.MULTILINE)

        if len(module_ids) <= 1:
            return False

        yaml_blocks, body = parse_frontmatter(content)

        if len(yaml_blocks) == 1:
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
                        continue
                else:
                    new_lines.append(line)

            new_content = '\n'.join(new_lines)
        else:
            valid_module_ids = [mid for mid in module_ids
                               if not mid.startswith('[') and 'PLACEHOLDER' not in mid]

            if valid_module_ids:
                keep_module_id = valid_module_ids[0]
            else:
                keep_module_id = module_ids[0]

            fix_double_yaml(file_path)

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

def enhance_frontmatter(file_path: Path) -> bool:
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        yaml_blocks, body = parse_frontmatter(content)

        if not yaml_blocks:
            return False

        data = yaml_blocks[0]
        if not isinstance(data, dict):
            logger.log("WARN", f"Frontmatter解析为{type(data).__name__}而非dict，跳过", str(file_path))
            stats.skipped_files.append(str(file_path))
            return False

        modified = False

        if 'module_id' not in data or not data['module_id'] or '[' in str(data.get('module_id', '')):
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

        if 'last_updated' not in data:
            data['last_updated'] = datetime.now().strftime('%Y-%m-%d')
            modified = True

        if 'layer' not in data:
            rel_path = str(file_path.relative_to(DOCS_DIR))
            layer_match = re.search(r'layer[_\s]*(\d+)', rel_path, re.IGNORECASE)
            if layer_match:
                data['layer'] = f"layer_{layer_match.group(1)}"
            modified = True

        if not modified:
            return False

        if not create_backup(file_path):
            return False

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

def process_file(file_path: Path) -> bool:
    try:
        stats.total_files += 1

        if file_path.suffix.lower() != '.md':
            return False

        rel_path = str(file_path.relative_to(DOCS_DIR))
        if 'archive' in rel_path.lower() and '06_ARCHIVE' not in rel_path:
            return False

        fixed = False

        if fix_frontmatter_structural(file_path):
            fixed = True

        if fix_double_yaml(file_path):
            fixed = True

        if fix_double_module_id(file_path):
            fixed = True

        if enhance_frontmatter(file_path):
            fixed = True

        return fixed

    except Exception as e:
        logger.log("ERROR", f"处理文件失败: {e}", str(file_path))
        stats.errors.append(f"{file_path}: {e}")
        return False

def main():
    print("=" * 80)
    print("七维审计问题一键修复工具 v2.0")
    print("=" * 80)
    print(f"项目根目录: {PROJECT_ROOT}")
    print(f"文档目录: {DOCS_DIR}")
    print(f"备份目录: {BACKUP_DIR}")
    print(f"报告文件: {REPORT_FILE}")
    print("=" * 80)
    print()

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    md_files = list(DOCS_DIR.rglob("*.md"))
    total = len(md_files)

    print(f"发现 {total} 个 Markdown 文件")
    print("开始处理...")
    print()

    for i, file_path in enumerate(md_files, 1):
        if i % 100 == 0:
            print(f"进度: {i}/{total} ({i/total*100:.1f}%)")

        try:
            process_file(file_path)
        except Exception as e:
            logger.log("ERROR", f"未捕获的异常: {e}", str(file_path))
            stats.errors.append(f"{file_path}: {e}")
            continue

    print()
    print("=" * 80)
    print("处理完成")
    print("=" * 80)

    logger.save()

    print(f"\n统计摘要:")
    print(f"  总扫描文件: {stats.total_files}")
    print(f"  双YAML修复: {stats.double_yaml_fixed}")
    print(f"  双module_id修复: {stats.double_module_id_fixed}")
    print(f"  Frontmatter增强: {stats.frontmatter_enhanced}")
    print(f"  闭合标记粘合修复: {stats.closed_tag_glue_fixed}")
    print(f"  字段间空行修复: {stats.blank_line_frontmatter_fixed}")
    print(f"  列表类型Frontmatter修复: {stats.list_frontmatter_fixed}")
    print(f"  编码损坏文件: {stats.encoding_corrupted}")
    print(f"  错误数: {len(stats.errors)}")
    print(f"  修改文件数: {len(stats.modified_files)}")
    print(f"\n详细报告已保存至: {REPORT_FILE}")
    print(f"备份文件位于: {BACKUP_DIR}")

    return 0 if len(stats.errors) < 10 else 1

if __name__ == "__main__":
    sys.exit(main())
