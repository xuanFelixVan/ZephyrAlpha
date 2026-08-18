# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/domain_header_maint.py | §
# [MODULE] scripts.governance.d3_metadata.domain_header_maint
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib only (argparse/json/os/re/subprocess/sys/time/pathlib/collections/ctypes)
# [CONSUMERS] AI 维护 [DOMAIN] header 时调用；孤儿锁排查时调用 clean-lock 子命令
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读扫描+校验（scan/verify 不修改文件）；clean-lock 仅清理已确认死亡的孤儿锁（PID 不存活）；--force 强制清理需人工确认
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""domain_header_maint.py — [DOMAIN] header 维护 + 孤儿锁清理工具

整合三个维护功能（源自 2026-08-03 批量补全 382 个 [DOMAIN] header 的实践）：

1. scan      — 全项目扫描缺失 [DOMAIN] header 的 .py 文件，按目录/域分类统计
2. verify    — 校验指定 commit 或文件列表的 [DOMAIN] header 位置和格式规范性
3. clean-lock — 检测和清理孤儿 git commit 锁（PID 已死亡的残留锁文件）

用法::

    # 全项目扫描缺失 [DOMAIN] 的文件
    python scripts/governance/d3_metadata/domain_header_maint.py scan

    # 校验某个 commit 中所有文件的 header 格式
    python scripts/governance/d3_metadata/domain_header_maint.py verify --commit <hash>

    # 校验指定文件列表
    python scripts/governance/d3_metadata/domain_header_maint.py verify --files f1.py,f2.py

    # 检测孤儿锁（只报告，不清理）
    python scripts/governance/d3_metadata/domain_header_maint.py clean-lock

    # 清理已确认死亡的孤儿锁
    python scripts/governance/d3_metadata/domain_header_maint.py clean-lock --remove

    # 强制清理（即使 PID 存活也清理，慎用）
    python scripts/governance/d3_metadata/domain_header_maint.py clean-lock --force

退出码: 0=成功/无问题, 1=发现问题(缺失/格式错误/孤儿锁), 2=参数错误

分类边界处理规则（classify_file / _verify_file 共用）
===================================================

扫描只读取文件头部前 50 行（``_HEADER_LINES``），避免模板字符串里的 ``[MODULE]``
干扰判定。基于这前 50 行，文件被归入下列五种状态之一：

  - ``ok``          : 有 [MODULE] 且有 [DOMAIN]
  - ``missing``     : 有 [MODULE] 但无 [DOMAIN]（需补全）
  - ``no_module``   : 前 50 行内无 [MODULE] header
  - ``domain_only`` : 有 [DOMAIN] 但无 [MODULE]（异常/旧格式）
  - ``read_error``  : 读取失败（IO 异常，*非空文件*）

关键边界（曾踩坑，新增测试覆盖 ``TestClassifyFile``/``TestVerifyFile``）：

  1. **空文件 → ``no_module``，绝不是 ``read_error``**
     ``_read_head`` 用 ``None`` 表示 IO 异常（权限/锁定），用空串表示空文件。
     空文件没有 header，按"无 [MODULE]"归类为 ``no_module``。历史上空 ``__init__.py``
     曾被误判为 ``read_error``，现以 ``not head`` 显式分支纠正。

  2. **只有注释/docstring、无 [MODULE] header → ``no_module``**
     纯 docstring、纯注释、纯空白行文件都归 ``no_module``（它们没有 header，但能正常读取）。
     ``read_error`` 仅留给真正的 IO 异常。

  3. **[MODULE] 出现在第 50 行之后 → ``no_module``**
     只读前 50 行，超出范围的 header 视为不存在。边界值：[MODULE] 在第 49 行、
     [DOMAIN] 在第 50 行仍判 ``ok``。

  4. **[DOMAIN] 值为空或 ``#`` → ``empty_domain``（scan）/ ``empty_value``（verify）**
     scan 把这类从 ``ok`` 中扣除单独统计；verify 直接报 ``empty_value``。

  5. **classify_file 不检查位置，_verify_file 检查位置**
     [DOMAIN] 出现在 docstring 之后（50 行内）``classify_file`` 仍判 ``ok``；
     ``_verify_file`` 会检查 [DOMAIN] 是否在 [MODULE] 之后、两者之间是否有其它内容，
     位置错乱报 ``position_error``，中间有内容报 ``ok_with_warn``。

  6. **``#[MODULE]foo`` 无空格也能匹配**
     正则用 ``^#\\s*\\[MODULE\\]``，``#`` 与 ``[`` 之间、``]`` 与值之间的空格均可省。
"""

from __future__ import annotations

__manifest__ = """
args: []
description: domain_header_maint.py — [DOMAIN] header 维护 + 孤儿锁清理工具
dimensions:
- D3
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

REPO = _PROJECT_ROOT
AILocks_DIR = REPO / ".ailocks"
COMMIT_LOCK_FILE = AILocks_DIR / "git_commit_global.lock"

# header 正则——只扫描文件头部前 50 行，避免模板字符串干扰
_HEADER_LINES = 50
MODULE_RE = re.compile(r"^#\s*\[MODULE\]\s*(.+)$", re.MULTILINE)
DOMAIN_RE = re.compile(r"^#\s*\[DOMAIN\]\s*(\S+)", re.MULTILINE)

# 扫描范围
SCAN_DIRS = [REPO / "src", REPO / "tests", REPO / "scripts"]

# 排除目录
EXCLUDE_DIRS = {
    "__pycache__", ".venv", ".runtime", "node_modules", "build", "dist",
    ".git", ".pytest_cache", ".mypy_cache", ".ruff_cache",
}


# ---------------------------------------------------------------------------
# 进程存活检测（跨平台）
# ---------------------------------------------------------------------------

def is_process_alive(pid: int) -> bool:
    """检查进程是否存活（跨平台）。

    Windows 优先用 ctypes OpenProcess（最可靠），fallback 到 os.kill。
    Unix 用 os.kill(pid, 0)。
    """
    if pid <= 0:
        return False
    if os.name == "nt":
        try:
            import ctypes

            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000  # noqa: gate-vocab Win32 API 常量名为平台既定术语非治理词表违规
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.OpenProcess(
                PROCESS_QUERY_LIMITED_INFORMATION, False, pid
            )
            if handle:
                kernel32.CloseHandle(handle)
                return True
            return False
        except Exception:
            pass  # fallback 到 os.kill
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False
    except OSError:
        return False


# ---------------------------------------------------------------------------
# 文件分类
# ---------------------------------------------------------------------------

def _should_skip(path: Path) -> bool:
    """是否跳过该文件。"""
    if path.suffix != ".py":
        return True
    parts = set(path.parts)
    if parts & EXCLUDE_DIRS:
        return True
    return False


def _read_head(path: Path) -> str | None:
    """读取文件头部前 N 行。返回 None 表示 IO 异常（权限/锁定），空串表示空文件。"""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None
    return "\n".join(text.split("\n")[:_HEADER_LINES])


def classify_file(path: Path) -> tuple[str, str | None]:
    """分类文件：(状态, domain_id)。

    状态:
      - "ok"         : 有 [MODULE] 且有 [DOMAIN]
      - "missing"    : 有 [MODULE] 但无 [DOMAIN]（需补全）
      - "no_module"  : 无 [MODULE] header（空文件/无 header）
      - "domain_only": 有 [DOMAIN] 但无 [MODULE]（异常/旧格式）
      - "read_error" : 读取失败（IO 异常，非空文件）
    """
    head = _read_head(path)
    if head is None:
        return ("read_error", None)
    if not head:
        # 空文件——无 header，归类为 no_module（非 read_error）
        return ("no_module", None)

    has_module = bool(MODULE_RE.search(head))
    m_dom = DOMAIN_RE.search(head)
    domain_id = m_dom.group(1) if m_dom else None

    if has_module and domain_id:
        return ("ok", domain_id)
    if has_module and not domain_id:
        return ("missing", None)
    if not has_module and domain_id:
        return ("domain_only", domain_id)
    return ("no_module", None)


def _top_dir(path: Path) -> str:
    """获取文件的顶层目录归类（如 src/zephyr, tests/governance）。"""
    try:
        rel = path.relative_to(REPO)
        return "/".join(rel.parts[:2]) if len(rel.parts) >= 2 else rel.parts[0]
    except ValueError:
        return path.parent.name


# ---------------------------------------------------------------------------
# 子命令: scan
# ---------------------------------------------------------------------------

def cmd_scan(args: argparse.Namespace) -> int:
    """全项目扫描缺失 [DOMAIN] header 的文件。"""
    stats = Counter()
    missing_files: list[Path] = []
    domain_only_files: list[Path] = []
    empty_domain_files: list[Path] = []  # [DOMAIN] 值为 # 或空
    ok_domain_dist = Counter()
    missing_by_dir: dict[str, list[Path]] = defaultdict(list)
    ok_by_dir = Counter()

    total = 0
    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for p in scan_dir.rglob("*.py"):
            if _should_skip(p):
                continue
            total += 1
            status, dom = classify_file(p)
            stats[status] += 1
            top = _top_dir(p)

            if status == "ok":
                # 检测 [DOMAIN] 值是否为 # (空值格式错误)
                if dom and dom.startswith("#"):
                    empty_domain_files.append(p)
                    stats["ok"] -= 1
                    stats["empty_domain"] += 1
                else:
                    ok_domain_dist[dom] += 1
                    ok_by_dir[top] += 1
            elif status == "missing":
                missing_files.append(p)
                missing_by_dir[top].append(p)
            elif status == "domain_only":
                domain_only_files.append(p)

    print("=" * 70)
    print("全项目 [DOMAIN] header 扫描报告")
    print("=" * 70)
    scan_dir_names = ", ".join(
        str(d.relative_to(REPO)) for d in SCAN_DIRS if d.exists()
    )
    print(f"\n[1] 扫描范围: {scan_dir_names}")
    print(f"    扫描 .py 文件总数: {total}")

    print(f"\n[2] 分类统计:")
    print(f"    OK（有 MODULE 且有 DOMAIN）:     {stats['ok']:5d}")
    print(f"    MISSING（有 MODULE 无 DOMAIN）:   {stats['missing']:5d}  ← 需补全")
    print(f"    EMPTY_DOMAIN（DOMAIN 值为空/#）:  {stats['empty_domain']:5d}  ← 格式错误")
    print(f"    NO_MODULE（无 MODULE header）:    {stats['no_module']:5d}  ← 可能不需要")
    print(f"    DOMAIN_ONLY（有 DOMAIN 无 MODULE）: {stats['domain_only']:5d}  ← 异常/旧格式")
    print(f"    READ_ERROR:                       {stats['read_error']:5d}")

    print(f"\n[3] 已有 [DOMAIN] 的域分布:")
    for dom, cnt in ok_domain_dist.most_common():
        print(f"    {cnt:5d}  {dom}")

    if missing_files:
        print(f"\n[4] 缺失 [DOMAIN] 的文件（共 {len(missing_files)} 个），按目录分组:")
        for d in sorted(missing_by_dir.keys()):
            files = missing_by_dir[d]
            print(f"\n  [{d}] {len(files)} 个:")
            for f in files[:20]:
                try:
                    rel = f.relative_to(REPO)
                except ValueError:
                    rel = f
                print(f"    - {rel}")
            if len(files) > 20:
                print(f"    ... 还有 {len(files) - 20} 个")
    else:
        print(f"\n[4] 缺失 [DOMAIN] 的文件: 无 ✅")

    if empty_domain_files:
        print(f"\n[5] [DOMAIN] 空值文件（共 {len(empty_domain_files)} 个，需补全域名）:")
        for f in empty_domain_files[:20]:
            try:
                rel = f.relative_to(REPO)
            except ValueError:
                rel = f
            print(f"    - {rel}")
    else:
        print(f"\n[5] [DOMAIN] 空值文件: 无 ✅")

    if domain_only_files:
        print(f"\n[6] 异常（有 DOMAIN 无 MODULE）文件（共 {len(domain_only_files)} 个）:")
        for f in domain_only_files[:20]:
            try:
                rel = f.relative_to(REPO)
            except ValueError:
                rel = f
            print(f"    - {rel}")
    else:
        print(f"\n[6] 异常文件: 无 ✅")

    print(f"\n[7] OK 文件按顶层目录分布:")
    for d, cnt in ok_by_dir.most_common():
        print(f"    {cnt:5d}  {d}")

    print(f"\n{'=' * 70}")
    has_issues = stats["missing"] > 0 or stats["empty_domain"] > 0
    if not has_issues:
        print("✅ 结论：无缺失/格式错误文件，所有有 [MODULE] header 的文件均已补全 [DOMAIN]。")
    else:
        print(
            f"⚠️  结论：{stats['missing']} 个缺失 + {stats['empty_domain']} 个空值，需处理。"
        )
    print("=" * 70)

    return 0 if not has_issues else 1


# ---------------------------------------------------------------------------
# 子命令: verify
# ---------------------------------------------------------------------------

def _verify_file(rel: str) -> tuple[str, str | None]:
    """校验单个文件的 header 格式。返回 (状态, 详情)。

    状态: ok / ok_with_warn / missing / position_error / empty_value / no_module / not_exist / read_error
    """
    filepath = REPO / rel
    if not filepath.exists():
        return ("not_exist", None)

    head = _read_head(filepath)
    if head is None:
        return ("read_error", "IO 读取失败")
    if not head:
        return ("no_module", None)  # 空文件

    m_mod = MODULE_RE.search(head)
    m_dom = DOMAIN_RE.search(head)

    if not m_mod:
        return ("no_module", None)
    if not m_dom:
        return ("missing", None)

    # 检查 DOMAIN 是否在 MODULE 之后
    if m_dom.start() < m_mod.start():
        return ("position_error", f"DOMAIN 在 MODULE 之前")

    # 检查 DOMAIN 值是否为空/#
    domain_id = m_dom.group(1)
    if domain_id.startswith("#") or not domain_id.strip():
        return ("empty_value", f"DOMAIN 值为 '{domain_id}'")

    # 检查 MODULE 和 DOMAIN 之间是否有其他内容
    between = head[m_mod.end():m_dom.start()].strip()
    if between:
        return ("ok_with_warn", f"MODULE 和 DOMAIN 之间有内容: '{between[:60]}'")

    return ("ok", domain_id)


def cmd_verify(args: argparse.Namespace) -> int:
    """校验指定 commit 或文件列表的 header 格式。"""
    # 获取文件列表
    if args.commit:
        result = subprocess.run(
            ["git", "show", "--name-only", "--pretty=", args.commit],
            capture_output=True, text=True, cwd=str(REPO),
        )
        if result.returncode != 0:
            print(f"ERROR: 无法获取 commit {args.commit}: {result.stderr.strip()}")
            return 2
        files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        # 只校验 .py 文件
        files = [f for f in files if f.endswith(".py")]
        print(f"[1] commit {args.commit[:8]} 中的 .py 文件数: {len(files)}")
    elif args.files:
        files = [f.strip() for f in args.files.split(",") if f.strip()]
        print(f"[1] 指定文件数: {len(files)}")
    else:
        print("ERROR: 必须指定 --commit 或 --files")
        return 2

    if not files:
        print("无文件可校验")
        return 0

    errors: list[str] = []
    warnings: list[str] = []
    ok_count = 0
    domain_dist = Counter()

    for rel in files:
        status, detail = _verify_file(rel)
        if status == "ok":
            ok_count += 1
            domain_dist[detail] += 1
        elif status == "ok_with_warn":
            ok_count += 1
            domain_dist[detail.split("'")[1] if "'" in detail else "?"] += 1
            warnings.append(f"{rel}: {detail}")
        elif status == "not_exist":
            errors.append(f"{rel}: 文件不存在")
        elif status == "no_module":
            errors.append(f"{rel}: 无 [MODULE] header")
        elif status == "missing":
            errors.append(f"{rel}: 无 [DOMAIN] header")
        elif status == "position_error":
            errors.append(f"{rel}: {detail}")
        elif status == "empty_value":
            errors.append(f"{rel}: {detail}")
        elif status == "read_error":
            errors.append(f"{rel}: {detail}")

    print(f"\n[2] 校验结果:")
    print(f"    OK:    {ok_count}")
    print(f"    WARN:  {len(warnings)}")
    print(f"    ERROR: {len(errors)}")

    if warnings:
        print(f"\n[3] 警告（不影响功能）:")
        for w in warnings[:20]:
            print(f"  {w}")

    if errors:
        print(f"\n[4] 错误:")
        for e in errors[:30]:
            print(f"  {e}")
        if len(errors) > 30:
            print(f"  ... 还有 {len(errors) - 30} 条")
    else:
        print(f"\n[4] 无错误 ✅")

    print(f"\n[5] 域分布统计:")
    for dom, cnt in domain_dist.most_common():
        print(f"    {cnt:4d}  {dom}")

    return 0 if not errors else 1


# ---------------------------------------------------------------------------
# 子命令: clean-lock
# ---------------------------------------------------------------------------

def cmd_clean_lock(args: argparse.Namespace) -> int:
    """检测和清理孤儿 git commit 锁。"""
    if not COMMIT_LOCK_FILE.exists():
        print("✅ 无 git_commit_global.lock 文件，无需清理。")
        return 0

    try:
        content = COMMIT_LOCK_FILE.read_text(encoding="utf-8")
        lock_data = json.loads(content)
    except (json.JSONDecodeError, Exception) as e:
        print(f"⚠️  锁文件解析失败: {e}")
        print(f"    内容: {content!r}")
        if args.force:
            COMMIT_LOCK_FILE.unlink()
            print("    --force 已清理损坏的锁文件。")
            return 0
        return 1

    pid = lock_data.get("pid")
    acquired_at = lock_data.get("acquired_at")

    print("=" * 60)
    print("git commit 全局锁检测")
    print("=" * 60)
    print(f"\n  锁文件: {COMMIT_LOCK_FILE.relative_to(REPO)}")
    print(f"  PID:    {pid}")
    if acquired_at:
        age = time.time() - acquired_at
        print(f"  获取时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(acquired_at))}")
        print(f"  持续时间: {age:.1f}s ({age/60:.1f}min)")

    if pid is None:
        print("\n  ⚠️  锁文件无 PID 字段（损坏）")
        if args.force or args.remove:
            COMMIT_LOCK_FILE.unlink()
            print("  已清理损坏的锁文件。")
            return 0
        print("  使用 --force 清理。")
        return 1

    alive = is_process_alive(pid)
    print(f"\n  进程存活: {'是 🔴' if alive else '否（孤儿锁）✅'}")

    if alive and not args.force:
        print(f"\n  ⚠️  PID {pid} 仍在运行——锁可能是活跃的，不建议清理。")
        print("  如确认需强制清理，使用 --force。")
        return 1

    if alive and args.force:
        print(f"\n  ⚠️  --force 模式：强制清理活跃锁（PID {pid} 仍在运行）！")
        print("  这可能导致 PID {pid} 的 commit 流程异常。")

    # 清理锁
    if args.remove or args.force:
        try:
            COMMIT_LOCK_FILE.unlink()
            print(f"\n  ✅ 已清理锁文件: {COMMIT_LOCK_FILE.relative_to(REPO)}")
            return 0
        except Exception as e:
            print(f"\n  ❌ 清理失败: {e}")
            return 1
    else:
        if not alive:
            print(f"\n  孤儿锁已确认（PID {pid} 已死亡），使用 --remove 清理。")
            return 1
        return 0


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(
        description="[DOMAIN] header 维护 + 孤儿锁清理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
示例:
  scan        全项目扫描缺失 [DOMAIN] 的文件
  verify      校验 commit 中文件的 header 格式
  clean-lock  检测/清理孤儿 git commit 锁
""",
    )
    sub = parser.add_subparsers(dest="command", help="子命令")

    # scan
    sub.add_parser("scan", help="全项目扫描缺失 [DOMAIN] header 的文件")

    # verify
    p_verify = sub.add_parser("verify", help="校验 header 格式规范性")
    p_verify.add_argument("--commit", help="校验指定 commit 中的文件")
    p_verify.add_argument("--files", help="校验指定文件列表（逗号分隔）")

    # clean-lock
    p_lock = sub.add_parser("clean-lock", help="检测/清理孤儿 git commit 锁")
    p_lock.add_argument("--remove", action="store_true", help="清理已确认死亡的孤儿锁")
    p_lock.add_argument("--force", action="store_true", help="强制清理（即使 PID 存活）")

    args = parser.parse_args()

    if args.command == "scan":
        return cmd_scan(args)
    elif args.command == "verify":
        return cmd_verify(args)
    elif args.command == "clean-lock":
        return cmd_clean_lock(args)
    else:
        parser.print_help()
        return 2


if __name__ == "__main__":
    sys.exit(main())
