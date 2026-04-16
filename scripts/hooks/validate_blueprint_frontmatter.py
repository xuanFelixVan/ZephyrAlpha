#!/usr/bin/env python3
# AI-generated: pre-commit hook - 校验蓝图 frontmatter 完整性和子系统路径合法性
"""
Blueprint Frontmatter Validator (pre-commit hook)

在 git commit 时对修改的 .md 文件执行以下检查：
  1. Active 蓝图必须有 module_id, version, status, layer, priority 字段
  2. status 值必须在允许集合内
  3. Retired 蓝图必须有 value_extracted_to 字段
  4. 新建 docs/ 子目录必须在 subsystem-registry.yaml 中登记
  5. 文件编码必须是 UTF-8（无阿拉伯文乱码）

用法（通常由 pre-commit 自动调用）:
    python scripts/hooks/validate_blueprint_frontmatter.py [files...]

如果无文件参数，从 git status 读取修改的文件。
"""

import io
import sys
import os
import re
import subprocess
import yaml
from pathlib import Path
from typing import Optional

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


REPO_ROOT = Path(__file__).resolve().parent.parent.parent

VALID_STATUSES = {"Draft", "Review", "Active", "Superseded", "Deprecated", "Retired", "AUDITED"}
REQUIRED_ACTIVE_FIELDS = ["module_id", "version", "status", "layer", "priority"]
VALID_PRIORITIES = {"P0", "P1", "P2"}
VALID_LAYERS = {f"layer_{i:02d}" for i in range(12)} | {"cross_layer", "cross-layer"}

# 不校验的目录
SKIP_DIRS = {
    "docs/06_ARCHIVE", "docs/09_ARCHIVE", "docs/99_ARCHIVE",
    ".audit_fix_backup", "scripts",
    # 运营类文档目录——非蓝图，不需要 layer/priority 字段
    "docs/09_AUDIT/STATE/SESSION_LOGS",
    "docs/09_AUDIT/STATE/DAILY",
    "docs/09_AUDIT/STATE/MILESTONE",
    "docs/09_AUDIT/REPORTS",
    # 施工/规划文档——非蓝图
    "docs/04_CONSTRUCTION/PLANS",
    "docs/04_CONSTRUCTION/LEDGER",
}

# 跳过文件名模式：INDEX.md 是导航文件，*-template.md 是模板文件，均不是蓝图
SKIP_FILENAMES = {"INDEX.md", "index.md", "README.md"}
SKIP_FILENAME_SUFFIXES = ("-template.md", "-template-example.md")

# 阿拉伯/波斯字符检测正则
ARABIC_PATTERN = re.compile(r"[\u0600-\u06ff\u0750-\u077f\ufb00-\ufdff]")


def get_staged_files() -> list[Path]:
    """获取当前 git 暂存区中修改的 .md 文件。"""
    try:
        result = subprocess.run(
            # 只对新建（A）和复制（C）的文件强制 frontmatter——修改已有文件不触发
            # 避免链接修复、内容更新等操作被历史遗留的 frontmatter 问题所阻塞
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AC"],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        files = [
            REPO_ROOT / f.strip()
            for f in result.stdout.strip().split("\n")
            if f.strip().endswith(".md")
        ]
        return [f for f in files if f.exists()]
    except Exception:
        return []


def extract_frontmatter(filepath: Path) -> Optional[dict]:
    """提取 YAML frontmatter。"""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
        if not content.startswith("---"):
            return None
        end_idx = content.find("---", 3)
        if end_idx == -1:
            return None
        return yaml.safe_load(content[3:end_idx].strip())
    except Exception:
        return None


def check_encoding(filepath: Path) -> list[str]:
    """检查文件是否有编码损坏（阿拉伯文乱码）。"""
    errors = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
        if ARABIC_PATTERN.search(content):
            count = len(ARABIC_PATTERN.findall(content))
            errors.append(f"ENCODING_CORRUPTION: {count} 个可疑字符（阿拉伯/波斯文），疑似编码损坏")
    except Exception as e:
        errors.append(f"READ_ERROR: {e}")
    return errors


def check_blueprint_frontmatter(filepath: Path, fm: dict) -> list[str]:
    """校验蓝图 frontmatter。"""
    errors = []
    status = fm.get("status", "")

    # 检查 status 合法性
    if status and status not in VALID_STATUSES:
        errors.append(f"INVALID_STATUS: '{status}'，允许值: {sorted(VALID_STATUSES)}")

    # Active/AUDITED 蓝图必须有所有必填字段
    if status in ("Active", "AUDITED"):
        for field in REQUIRED_ACTIVE_FIELDS:
            if field not in fm or fm[field] in (None, "", "TBD"):
                errors.append(f"MISSING_FIELD: '{field}' 对 Active 蓝图是必填项")

        # priority 校验
        priority = str(fm.get("priority", ""))
        if priority and priority not in VALID_PRIORITIES:
            errors.append(f"INVALID_PRIORITY: '{priority}'，允许值: P0/P1/P2")

        # layer 校验
        layer = str(fm.get("layer", "")).lower()
        if layer and layer not in VALID_LAYERS:
            errors.append(f"INVALID_LAYER: '{layer}'，允许值: layer_00~layer_11 或 cross_layer")

    # Retired 蓝图必须有 value_extracted_to
    if status == "Retired" and "value_extracted_to" not in fm:
        errors.append("MISSING_RETIREMENT_FIELD: Retired 蓝图必须有 'value_extracted_to' 字段")

    return errors


def check_new_directory(filepath: Path) -> list[str]:
    """检查新建的 docs/ 子目录是否在 subsystem-registry.yaml 中登记。"""
    errors = []
    registry_path = REPO_ROOT / "docs/subsystem-registry.yaml"

    # 只检查 docs/ 直接子目录
    try:
        rel = filepath.relative_to(REPO_ROOT)
    except ValueError:
        rel = filepath.resolve().relative_to(REPO_ROOT.resolve())
    parts = rel.parts
    if len(parts) < 2 or parts[0] != "docs":
        return errors

    subdir = f"docs/{parts[1]}"

    if not registry_path.exists():
        return errors

    try:
        with open(registry_path, encoding="utf-8") as f:
            registry = yaml.safe_load(f) or {}

        registered_paths = set()
        for ss in registry.get("subsystems", []):
            p = ss.get("canonical_path", "").rstrip("/")
            if p:
                registered_paths.add(p)

        if subdir not in registered_paths:
            errors.append(
                f"UNREGISTERED_SUBSYSTEM: '{subdir}' 未在 docs/subsystem-registry.yaml 中登记。"
                f"请先登记再创建文件。"
            )
    except Exception:
        pass

    return errors


def is_blueprint_file(filepath: Path, fm: Optional[dict]) -> bool:
    """判断是否需要校验 frontmatter。"""
    name = filepath.name.lower()
    if "blueprint" in name or "technical-specification" in name:
        return True
    if fm and fm.get("module_id"):
        return True
    return False


def get_newly_added_files() -> set[str]:
    """返回本次 commit 中新建（A）文件的相对路径集合（小写）。"""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=A"],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        return {f.strip().lower() for f in result.stdout.strip().split("\n") if f.strip()}
    except Exception:
        return set()


def main(files: Optional[list[str]] = None) -> int:
    newly_added = get_newly_added_files()
    if files:
        # pre-commit 通过 pass_filenames 传入所有 staged 文件（含 M/D）
        # 只对新建文件（A）强制 frontmatter——修改已有文件的行为不触发，避免被历史债务阻塞
        target_files = [
            Path(f) for f in files
            if f.endswith(".md") and Path(f).exists()
            and f.replace("\\", "/").lower() in newly_added
        ]
    else:
        target_files = get_staged_files()

    if not target_files:
        print("No .md files to validate.")
        return 0

    all_errors = {}

    for filepath in target_files:
        errors = []
        try:
            rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
        except ValueError:
            # Windows 路径大小写不一致时 fallback
            rel = str(filepath.resolve().relative_to(REPO_ROOT.resolve())).replace("\\", "/")

        # 跳过归档目录和施工/规划目录
        if any(rel.startswith(skip) for skip in SKIP_DIRS):
            continue
        # 跳过导航文件（INDEX.md / README.md）和模板文件——不是蓝图
        if filepath.name in SKIP_FILENAMES:
            continue
        if any(filepath.name.endswith(s) for s in SKIP_FILENAME_SUFFIXES):
            continue

        # 1. 编码检查（所有 .md 文件）
        errors.extend(check_encoding(filepath))

        # 2. 子系统注册检查（新建文件）
        errors.extend(check_new_directory(filepath))

        # 3. Frontmatter 校验（蓝图文件）
        fm = extract_frontmatter(filepath)
        if fm and is_blueprint_file(filepath, fm):
            errors.extend(check_blueprint_frontmatter(filepath, fm))

        if errors:
            all_errors[rel] = errors

    if not all_errors:
        print(f"[OK] Blueprint frontmatter validation passed ({len(target_files)} files checked)")
        return 0

    print(f"\n[FAIL] Blueprint frontmatter validation failed:\n")
    for filepath, errors in sorted(all_errors.items()):
        print(f"  {filepath}:")
        for err in errors:
            print(f"    ✗ {err}")
    print(f"\nTotal: {sum(len(e) for e in all_errors.values())} issues in {len(all_errors)} files")
    print("Fix the above issues before committing.")
    return 1


if __name__ == "__main__":
    files = sys.argv[1:] if len(sys.argv) > 1 else None
    sys.exit(main(files))
