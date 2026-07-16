"""分析M02违规的分布与触发模式"""
import re
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

# 读取违规列表
violations = (REPO_ROOT / "tmp_m02_violations.txt").read_text(encoding="utf-8").splitlines()
violations = [v for v in violations if v.strip()]

# 按目录分组
dir_counter = Counter()
for v in violations:
    parts = v.split("/")
    if len(parts) >= 3:
        # scripts/governance/XXX/...
        subdir = parts[2] if len(parts) > 3 else "_root"
        dir_counter[subdir] += 1
    else:
        dir_counter["_root"] += 1

print("=== M02违规按子目录分布 ===")
for d, c in sorted(dir_counter.items(), key=lambda x: -x[1]):
    print(f"  {d}: {c}")

# 检查 src/zephyr/ 下是否有 [STARTUP]=manual + [TTL]=permanent 组合
print("\n=== src/zephyr/ 下的 manual+permanent 组合 ===")
_STARTUP_RE = re.compile(r"^#\s*\[STARTUP\]\s*(\S+)", re.MULTILINE)
_TTL_RE = re.compile(r"^#\s*\[TTL\]\s*(\S+)", re.MULTILINE)
EXCLUDE = {".git", ".aidrafts", "__pycache__", "node_modules", ".venv", "venv", "build", "dist", "_archive", "tests"}
src_zephyr = REPO_ROOT / "src" / "zephyr"
src_violations = []
for fp in src_zephyr.rglob("*.py"):
    if any(ex in fp.parts for ex in EXCLUDE):
        continue
    try:
        source = fp.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        continue
    sm = _STARTUP_RE.search(source)
    tm = _TTL_RE.search(source)
    if not sm or not tm:
        continue
    startup = sm.group(1).strip()
    ttl = tm.group(1).strip()
    if startup.lower() == "manual" and ttl.lower() == "permanent":
        src_violations.append(str(fp.relative_to(REPO_ROOT)).replace("\\", "/"))

print(f"src/zephyr/ 下 manual+permanent 组合数: {len(src_violations)}")
for v in src_violations[:10]:
    print(f"  {v}")

# 检查脚本类型分布（CLI入口 vs 库模块）
print("\n=== scripts/governance/ 脚本特征分析 ===")
cli_count = 0
lib_count = 0
for v in violations:
    fp = REPO_ROOT / v
    try:
        source = fp.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        continue
    # CLI 入口特征：if __name__ == "__main__"
    has_main = 'if __name__ == "__main__"' in source or "if __name__ == '__main__'" in source
    # argparse 特征
    has_argparse = "argparse" in source or "__manifest__" in source
    if has_main or has_argparse:
        cli_count += 1
    else:
        lib_count += 1

print(f"  CLI入口脚本（有 __main__ 或 argparse/manifest）: {cli_count}")
print(f"  库模块（无入口）: {lib_count}")

# 列出无入口的库模块
print("\n=== 无入口的库模块列表 ===")
for v in violations:
    fp = REPO_ROOT / v
    try:
        source = fp.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        continue
    has_main = 'if __name__ == "__main__"' in source or "if __name__ == '__main__'" in source
    has_argparse = "argparse" in source or "__manifest__" in source
    if not (has_main or has_argparse):
        print(f"  {v}")
