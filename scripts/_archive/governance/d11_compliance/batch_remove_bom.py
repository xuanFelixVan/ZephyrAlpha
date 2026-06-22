"""DM-200817: 批量去除UTF-8 BOM
使用与validate_no_utf8_bom.py相同的扫描逻辑，确保一致性。
"""

import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(r"D:\ZephyrAlpha")
BOM = b"\xef\xbb\xbf"
TARGET_EXTENSIONS = {".yaml", ".md", ".py"}
EXCLUDE_DIRS = {
    ".git",
    ".ailocks",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".pytest_cache",
    ".mypy_cache",
    "_DO_NOT_USE_old_tree",
}


def scan_for_bom(root: Path) -> list[Path]:
    """与validate_no_utf8_bom.py相同的扫描逻辑"""
    bom_files = []
    for f in root.rglob("*"):
        if any(part in EXCLUDE_DIRS for part in f.parts):
            continue
        if f.is_file() and f.suffix in TARGET_EXTENSIONS:
            try:
                with open(f, "rb") as fh:
                    if fh.read(3) == BOM:
                        bom_files.append(f)
            except OSError:
                continue
    return bom_files


def remove_bom(fpath: Path) -> tuple[Path, bool, str]:
    """去除单个文件的BOM（原子写入）"""
    try:
        with open(fpath, "rb") as f:
            content = f.read()
        if content[:3] == BOM:
            tmp_path = fpath.with_suffix(fpath.suffix + ".tmp")
            with open(tmp_path, "wb") as f:
                f.write(content[3:])
            os.replace(tmp_path, fpath)
            return (fpath, True, "BOM removed")
        return (fpath, False, "No BOM")
    except Exception as e:
        return (fpath, False, f"ERROR: {e}")


def main():
    print("扫描含BOM的文件...")
    bom_files = scan_for_bom(REPO_ROOT)
    print(f"找到 {len(bom_files)} 个含BOM文件")

    if not bom_files:
        print("无需修复")
        return 0

    success = 0
    failed = 0
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(remove_bom, f): f for f in bom_files}
        for future in as_completed(futures):
            fpath, ok, msg = future.result()
            if ok:
                success += 1
            else:
                failed += 1
                if "ERROR" in msg:
                    print(f"  FAIL: {fpath} - {msg}")

    print(f"\n完成: {success} 个文件去除BOM, {failed} 个失败")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
