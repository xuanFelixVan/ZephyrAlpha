# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/pre_write_gate.py | §
# [MODULE] scripts.governance.d5_architecture.pre_write_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.gov_enforcement.rule_enforcement.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""AI写入前强制门禁钩子: lock协议检查+GateEngine Phase评估+注册完整性验证

RULE-ZERO 硬执行器——AI 在调用 Write/SearchReplace 之前 MUST 先通过此门禁。
exit 0 = CLEAN（允许写入）, exit 1 = BLOCKED（拒绝写入）。

用法:
    python scripts/governance/d5_architecture/pre_write_gate.py <file_path> [--create]

设计原则:
    - 零副作用: 只读检查，不修改任何文件
    - 硬阻断: RED → exit 1，AI 无法绕过
    - 快速: 目标 <3s，不阻塞 AI 工作流
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 'AI写入前强制门禁钩子: lock协议检查+GateEngine Phase评估+注册完整性验证'
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import re
import subprocess
import sys
from pathlib import Path

# Bootstrap：CLI 直接运行时 sys.path[0]=本文件所在目录，找不到上级 _shared。
# 沿用 generate_path_tree.py L53-56 的 _GOV_DIR 模式（治本批次4b迁移遗留 import 断裂）。
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT  # noqa: E402

_PROJECT_ROOT = REPO_ROOT
_SCRIPTS_DIR = _PROJECT_ROOT / "scripts"
_LOCK_SCRIPT = _SCRIPTS_DIR / "lock_files.py"

_ILLEGAL_ROOT_PATTERNS = [
    r"^_temp",
    r"^_check",
    r"^_fix",
    r"^_phase_",
    r"^_deep",
    r"^_construction",
    r"^_rebuild",
    r"^_audit",
]


def _check_lock(file_path: str) -> tuple[bool, str]:
    """_check_lock implementation."""
    result = subprocess.run(
        [sys.executable, str(_LOCK_SCRIPT), "check", file_path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
        cwd=str(_PROJECT_ROOT),
    )
    output = result.stdout.strip()
    if "FREE" in output:
        return True, "OK"
    if "LOCKED" in output:
        return False, output
    return True, f"LOCK_CHECK_WARN: {output[:200]}"


def _check_session_overlap(file_path: str, session_id: str) -> tuple[bool, str]:
    """检测目标文件是否被其他活跃 session 持有（claim 前移协议防线）。

    复用 SessionRegistry.find_session_by_file（只读，无写副作用）。
    fail-open：registry 读取异常或无 session_id 时降级 PASS（对标 held_overlap_gate）。
    """
    if not session_id:
        return True, "OK (no --session, skip overlap check)"
    try:
        from zephyr.security.access_control.session_concurrency import SessionRegistry
        reg = SessionRegistry(_PROJECT_ROOT)
        holder = reg.find_session_by_file(file_path)
        if holder is not None and holder.session_id != session_id:
            rel = Path(file_path)
            try:
                rel = rel.resolve().relative_to(_PROJECT_ROOT.resolve())
            except ValueError:
                rel = file_path
            return False, (
                f"HELD_BY_OTHER: {rel} 被 session '{holder.session_id}' 持有"
                f"（claim 前移协议，AGENTS.md §8 L301）。"
                f"协调方式：等对方 release / 用 --allow-overlap 逃生通道 / 切 StagingArea 模式 B。"
            )
        return True, "OK"
    except Exception as e:
        return True, f"OVERLAP_WARN: 检测异常 ({e})——降级通过（对标 held_overlap_gate fail-open）"


def _check_root_pollution(file_path: str) -> tuple[bool, str]:
    """_check_root_pollution implementation."""
    rel = Path(file_path)
    try:
        rel = rel.resolve().relative_to(_PROJECT_ROOT.resolve())
    except ValueError:
        return True, "OK"

    parts = rel.parts
    if len(parts) == 1:
        for pat in _ILLEGAL_ROOT_PATTERNS:
            if re.match(pat, parts[0]):
                return False, f"ILLEGAL_ROOT: {file_path} 匹配禁止前缀 {pat!r}——临时文件不得落盘到根目录（RULE-FIVE）"
    return True, "OK"


def _check_phase_health() -> tuple[bool, str]:
    """_check_phase_health implementation."""
    try:
        from zephyr.gov_enforcement.rule_enforcement.phase_manager import GateResult, session_startup

        result = session_startup(quick=True)
        if result["ready"]:
            return True, f"PHASE_OK: {result['green']}G/{result['yellow']}Y/{result['red']}R"
        return False, f"PHASE_BLOCKED: {result['next_action']}"
    except ImportError as e:
        return True, f"PHASE_WARN: 无法加载 phase_manager ({e})——降级通过"
    except Exception as e:
        return True, f"PHASE_WARN: phase_manager 异常 ({e})——降级通过"


def _check_registered(file_path: str, is_create: bool) -> tuple[bool, str]:
    """_check_registered implementation."""
    if not is_create:
        return True, "OK"
    rel = Path(file_path)
    try:
        rel = rel.resolve().relative_to(_PROJECT_ROOT.resolve())
    except ValueError:
        return True, "OK"
    parts = rel.parts
    allowed_dirs = {"src", "scripts", "tests", "docs", "config", "data", ".trae"}
    if parts and parts[0] not in allowed_dirs:
        return (
            False,
            f"UNREGISTERED_DIR: {parts[0]!r} 不在允许目录 {allowed_dirs}——新建文件 MUST 走 scaffold.py（RULE-FOUR）",
        )
    return True, "OK"


def _check_encoding_safety(file_path: str) -> tuple[bool, str]:
    """Check that existing file has no mojibake, and warn about encoding safety."""
    p = Path(file_path)
    if not p.exists():
        return True, "OK (new file)"
    if p.suffix not in (".py", ".md", ".yaml", ".yml", ".json", ".toml"):
        return True, "OK (non-text file)"
    try:
        raw = p.read_bytes()
    except OSError:
        return True, "OK (cannot read)"
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError:
        return False, f"ENCODING_BLOCK: {file_path} is not valid UTF-8 — writing may corrupt the file further"
    # Mojibake detection
    try:
        content = raw.decode("utf-8")
        # Method 1: known markers
        MOJIBAKE_MARKERS = [
            "\u9516\u65a4\u62f7",  # 锟斤拷
            "\u93d4\u63d2\u53c2",
            "\u93d4\u659c\u7280\u6362",
            "\u93d4\u529c\u00b0\u20ac",
            "\u94c6\u003f",
        ]
        if any(m in content for m in MOJIBAKE_MARKERS):
            return (
                False,
                f"MOJIBAKE_BLOCK: {file_path} contains known mojibake markers — fix encoding before modifying (DM-378)",
            )
        # Method 2: round-trip via GBK (CJK segments only)
        import re as _re

        # 2a: test segments WITHOUT U+FFFD
        clean_content = content.replace("\ufffd", "")
        if clean_content.strip():
            cjk_segments = _re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf]+", clean_content)
            for seg in cjk_segments:
                if len(seg) < 2:
                    continue
                try:
                    gbk_bytes = seg.encode("gbk")
                    try:
                        roundtrip = gbk_bytes.decode("utf-8")
                        if roundtrip != seg:
                            orig_cjk = sum(1 for c in seg if 0x4E00 <= ord(c) <= 0x9FFF)
                            rt_cjk = sum(1 for c in roundtrip if 0x4E00 <= ord(c) <= 0x9FFF)
                            if rt_cjk > 0 and orig_cjk > 0:
                                rt_cjk_density = rt_cjk / len(roundtrip)
                                orig_cjk_density = orig_cjk / len(seg)
                                if rt_cjk_density >= orig_cjk_density:
                                    return (
                                        False,
                                        f"MOJIBAKE_BLOCK: {file_path} contains GBK-as-UTF-8 mojibake (round-trip detected) — fix encoding before modifying (DM-378)",
                                    )
                    except UnicodeDecodeError:
                        # Partial decode may reveal mojibake
                        try:
                            partial_rt = gbk_bytes.decode("utf-8", errors="replace")
                            partial_cjk = sum(1 for c in partial_rt if 0x4E00 <= ord(c) <= 0x9FFF and c != "\ufffd")
                            if partial_cjk >= 3:
                                return (
                                    False,
                                    f"MOJIBAKE_BLOCK: {file_path} contains GBK-as-UTF-8 mojibake (partial round-trip) — fix encoding before modifying (DM-378)",
                                )
                        except Exception:
                            pass
                except UnicodeEncodeError:
                    pass
        # 2b: test segments WITH U+FFFD — split at U+FFFD and test sub-segments
        if "\ufffd" in content:
            cjk_with_replacement = _re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf\ufffd]+", content)
            for seg in cjk_with_replacement:
                if "\ufffd" not in seg:
                    continue
                sub_segs = [s for s in seg.split("\ufffd") if len(s) >= 2]
                for sub in sub_segs:
                    try:
                        gbk_bytes = sub.encode("gbk")
                        try:
                            roundtrip = gbk_bytes.decode("utf-8")
                            if roundtrip != sub:
                                orig_cjk = sum(1 for c in sub if 0x4E00 <= ord(c) <= 0x9FFF)
                                rt_cjk = sum(1 for c in roundtrip if 0x4E00 <= ord(c) <= 0x9FFF)
                                if rt_cjk > 0 and orig_cjk > 0:
                                    rt_cjk_density = rt_cjk / len(roundtrip)
                                    orig_cjk_density = orig_cjk / len(sub)
                                    if rt_cjk_density >= orig_cjk_density:
                                        return (
                                            False,
                                            f"MOJIBAKE_BLOCK: {file_path} contains GBK-as-UTF-8 mojibake (round-trip with U+FFFD) — fix encoding before modifying (DM-378)",
                                        )
                        except UnicodeDecodeError:
                            pass
                    except UnicodeEncodeError:
                        pass
        # Method 3: U+FFFD in CJK context
        if "\ufffd" in content:
            cjk_context = _re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf]\ufffd|\ufffd[\u4e00-\u9fff\u3400-\u4dbf]", content)
            if len(cjk_context) >= 2:
                return (
                    False,
                    f"MOJIBAKE_BLOCK: {file_path} has U+FFFD replacement chars in CJK context — likely mojibake (DM-378)",
                )
        # Method 4: statistical fallback
        total_cjk = sum(1 for c in content if 0x4E00 <= ord(c) <= 0x9FFF)
        if total_cjk >= 50:
            common_cjk = sum(1 for c in content if 0x4E00 <= ord(c) <= 0x77FF)
            gbk_ext_cjk = sum(1 for c in content if 0x9400 <= ord(c) <= 0x9FFF)
            if gbk_ext_cjk / total_cjk > 0.50 and common_cjk / total_cjk < 0.30:
                return False, f"MOJIBAKE_BLOCK: {file_path} has abnormal CJK distribution — likely mojibake (DM-378)"
    except UnicodeDecodeError:
        pass
    return True, "OK"


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(
        description="AI 写入前强制门禁——不通过则拒绝写入",
    )
    parser.add_argument("file_path", help="要写入的文件路径（相对或绝对）")
    parser.add_argument("--create", action="store_true", help="是否创建新文件")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--session", default="", help="AI session 标识（启用 session overlap 检测；未提供则跳过）")
    args = parser.parse_args()

    checks: list[dict] = []

    ok, msg = _check_phase_health()
    checks.append({"check": "phase_health", "pass": ok, "message": msg})

    ok, msg = _check_lock(args.file_path)
    checks.append({"check": "lock_protocol", "pass": ok, "message": msg})

    ok, msg = _check_root_pollution(args.file_path)
    checks.append({"check": "root_pollution", "pass": ok, "message": msg})

    ok, msg = _check_registered(args.file_path, args.create)
    checks.append({"check": "registration", "pass": ok, "message": msg})

    ok, msg = _check_encoding_safety(args.file_path)
    checks.append({"check": "encoding_safety", "pass": ok, "message": msg})

    ok, msg = _check_session_overlap(args.file_path, args.session)
    checks.append({"check": "session_overlap", "pass": ok, "message": msg})

    blocked = [c for c in checks if not c["pass"]]

    if args.json:
        import json

        print(
            json.dumps(
                {
                    "allowed": len(blocked) == 0,
                    "checks": checks,
                    "file": args.file_path,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for c in checks:
            icon = "  PASS" if c["pass"] else "  BLOCK"
            print(f"{icon}  {c['check']}: {c['message']}")

        if blocked:
            print(f"\n  BLOCKED ({len(blocked)}/{len(checks)} checks failed)")
            print(f"  File: {args.file_path}")
            print("  Action required: 修复以上 BLOCK 项后重试")
        else:
            print(f"\n  ALL CLEAR ({len(checks)}/{len(checks)}) — 允许写入 {args.file_path}")

    return 0 if len(blocked) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
