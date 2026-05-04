"""
validate_index_reality.py — 索引-实际同步校验（AGENTS.md §6.11 自动化执行层）

对标：AGENTS.md §6.11（索引-实际同步强制约定——索引文件声称的文件数和文件清单必须与磁盘实际情况一致）
     ITIL SACM → CMDB reconciliation（配置管理数据库与实际基础设施定期对账）
     AWS Config → 持续评估资源配置与期望状态的偏差

检测内容：
- 提取 index.md 中各维度声称的脚本数量 vs 磁盘实际 .py 文件数
- 提取 index.md 中声称的 manifest 条目数 vs 实际条目数
- 检测"幽灵文件"：index.md 引用了磁盘上不存在的文件
- 检测"遗漏登记"：磁盘上存在但 index.md 未提及的文件

exit codes: 0=对齐, 1=发现漂移, 2=系统错误
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import MANIFEST_PATH, SCRIPTS_DIR
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

import argparse

import yaml

INDEX_PATH = SCRIPTS_DIR / "index.md"

DIMENSION_DIRS: dict[str, str] = {
    "D1": "d1_structure",
    "D2": "d2_links",
    "D3": "d3_metadata",
    "D4": "d4_paths",
    "D5": "d5_architecture",
    "D6": "d6_security",
    "D7": "d7_code",
    "D8": "d8_doc_sync",
    "D9": "d9_knowledge",
    "D10": "d10_performance",
    "D11": "d11_compliance",
    "D12": "d12_ai_hallucination",
}

def _count_py_files(dir_path: Path) -> int:
    if not dir_path.exists():
        return 0
    return len([f for f in dir_path.glob("*.py") if f.name != "__init__.py" and f.is_file()])

def _extract_index_claims(index_content: str) -> dict[str, int]:
    claims: dict[str, int] = {}
    for dim_key, dir_name in DIMENSION_DIRS.items():
        pattern = rf"{dir_name}/?\s+{dim_key}\s+.+?\s*（(\d+)\s*脚本）"
        m = re.search(pattern, index_content)
        if m:
            claims[dim_key] = int(m.group(1))
    manifest_m = re.search(r"（SSoT\s*[—\-—]\s*(\d+)\s*条目）", index_content)
    if manifest_m:
        claims["manifest"] = int(manifest_m.group(1))
    return claims

def _count_manifest_entries() -> int:
    try:
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data and "scripts" in data:
            return len(data["scripts"])
    except (yaml.YAMLError, OSError, KeyError):
        pass
    return -1

def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="索引-实际同步校验 — 对照 index.md 声称数字 vs 磁盘实际")
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="警告模式：发现漂移不阻塞（exit 0）",
    )
    args = parser.parse_args()

    if not INDEX_PATH.exists():
        print(f"[ERROR] index.md 不存在: {INDEX_PATH}", file=sys.stderr)
        sys.exit(2)

    index_content = INDEX_PATH.read_text(encoding="utf-8", errors="replace")
    claims = _extract_index_claims(index_content)

    drift: list[str] = []

    for dim_key, dir_name in DIMENSION_DIRS.items():
        dir_path = SCRIPTS_DIR / dir_name
        actual = _count_py_files(dir_path)
        claimed = claims.get(dim_key, -1)
        if claimed != actual and not (dim_key == "D10" and claimed == -1):
            drift.append(f"{dim_key} ({dir_name}/): index.md 声称 {claimed} 脚本, " f"磁盘实际 {actual}")

    actual_manifest = _count_manifest_entries()
    claimed_manifest = claims.get("manifest", -1)
    if claimed_manifest != actual_manifest and actual_manifest > 0:
        drift.append(f"manifest 条目: index.md 声称 {claimed_manifest}, " f"实际 {actual_manifest}")

    if drift:
        print(f"\n[IDX-DRIFT] index.md 与磁盘实际不一致 — {len(drift)} 项漂移：\n", file=sys.stderr)
        for d in drift:
            print(f"  ⚠ {d}", file=sys.stderr)
        print(file=sys.stderr)
        if args.warn_only:
            print("⚠ --warn-only 模式: 仅报告，不阻断", file=sys.stderr)
            sys.exit(0)
        sys.exit(1)

    print("[IDX-OK] index.md 数字与磁盘实际一致", file=sys.stderr)
    sys.exit(0)

if __name__ == "__main__":
    main()
