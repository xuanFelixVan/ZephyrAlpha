# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/check_encoding.py | §
# [MODULE] scripts.governance.d7_code.check_encoding
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d7_code.__init__
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
# [TTL] task_bound
"""check_encoding.py — 编码合规校验（INJ-007）

对标：GOV-MOD-ALPHA_SIGNAL_DOMAIN INJ-007（编码合规）

检测内容：
- --file: 检查指定文件的编码合规性（UTF-8 BOM/无BOM、无 CRLF、无 autoGuessEncoding）
- 包装 scripts/governance/d7_code/detect_missing_encoding.py 的功能

语义说明（2026-06-25, OPS-2026062501 修复）：
- BOM/autoGuessEncoding/mojibake = FAIL 级（阻断提交）
- CRLF = WARNING 级（不阻断提交，靠 .gitattributes + git add --renormalize 在仓库层解决）

exit codes: 0=pass, 1=findings(FAIL级), 2=error
"""

from __future__ import annotations

__manifest__ = """
args:
- {flag: --file, type: str, description: "检查指定文件的编码合规性"}
- {flag: --dir, type: str, description: "检查指定目录下所有文件的编码合规性"}
description: >
  编码合规校验（INJ-007）——UTF-8 编码、无 CRLF、无 autoGuessEncoding。
  对标 GOV-MOD-ALPHA_SIGNAL_DOMAIN module-injection-rules-policy.md。
dimensions:
- D7
priority: P1
timeout_seconds: 15
warn_only: false
"""

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

BOM = b"\xef\xbb\xbf"
CRLF = b"\r\n"
AUTO_GUESS_PATTERNS = [b"autoGuessEncoding", b"auto_guess_encoding", b"files.autoGuessEncoding"]
MOJIBAKE_MARKERS = [
    "\u9516\u65a4\u62f7",  # 锟斤拷 — classic GBK mojibake (impossible in normal text)
    "\u93d4\u63d2\u53c2",  # 镹插叆 — extremely rare in normal text
    "\u93d4\u659c\u7280\u6362",  # 镹斜犺换
    "\u93d4\u529c\u00b0\u20ac",  # 镹宁°€
    "\u94c6\u003f",  # 锆?
]


def _detect_mojibake_bytes(raw: bytes) -> bool:
    """Detect GBK-as-UTF-8 double-encoding mojibake at byte level.

    GBK mojibake occurs when UTF-8 bytes are misread as GBK and re-encoded as UTF-8.
    Detection strategy:
    1. Known mojibake character sequences that are impossible in normal Chinese
    2. Round-trip via GBK on CJK segments: encode to GBK, decode as UTF-8 —
       if the result has higher CJK density, the original is mojibake
    3. U+FFFD in CJK context: replacement chars adjacent to CJK = mojibake signal
    4. Statistical fallback: abnormal CJK distribution (only if round-trip also fails)
    """
    if not raw.strip():
        return False
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        return False

    if not content.strip():
        return False

    # Method 1: known mojibake character sequences (highest confidence)
    # Only markers that are IMPOSSIBLE in normal Chinese text
    if any(m in content for m in MOJIBAKE_MARKERS):
        return True

    # Method 2: round-trip via GBK (CJK segments only)
    # Key insight: if content is GBK-as-UTF-8 mojibake, then:
    #   content.encode('gbk') produces the original UTF-8 bytes
    #   which decode to the correct Chinese text
    # We extract CJK segments and test them individually
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
                                return True
                except UnicodeDecodeError:
                    # Round-trip decode failed — but partial decode may still reveal mojibake
                    # Try decoding with errors='replace' and check if partial result
                    # contains valid CJK that differs from original
                    try:
                        partial_rt = gbk_bytes.decode("utf-8", errors="replace")
                        # If partial round-trip produces ANY common CJK, it's mojibake
                        # because normal Chinese -> GBK -> UTF-8 should fail completely
                        # (not produce partial valid CJK)
                        partial_cjk = sum(1 for c in partial_rt if 0x4E00 <= ord(c) <= 0x9FFF and c != "\ufffd")
                        if partial_cjk >= 3:
                            return True
                    except Exception:
                        pass
            except UnicodeEncodeError:
                pass

    # 2b: test segments WITH U+FFFD — split at U+FFFD and test sub-segments
    # U+FFFD appears when UTF-8 bytes are not valid GBK sequences
    if "\ufffd" in content:
        cjk_with_replacement = _re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf\ufffd]+", content)
        for seg in cjk_with_replacement:
            if "\ufffd" not in seg:
                continue  # already tested in 2a
            # Split at U+FFFD and test each sub-segment
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
                                    return True
                    except UnicodeDecodeError:
                        pass
                except UnicodeEncodeError:
                    pass

    # Method 3: U+FFFD in CJK context — replacement chars adjacent to CJK
    # Normal UTF-8 files should NOT contain U+FFFD next to CJK characters
    # This is a strong mojibake signal
    if "\ufffd" in content:
        # Check if U+FFFD appears within or adjacent to CJK text
        cjk_context = _re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf]\ufffd|\ufffd[\u4e00-\u9fff\u3400-\u4dbf]", content)
        if len(cjk_context) >= 2:
            return True

    # Method 4: Statistical fallback — only if round-trip failed for all segments
    # AND the file has significant CJK content with abnormal distribution
    # This catches files where mojibake chars happen to round-trip identically
    # Normal Chinese: >80% of CJK chars in U+4E00-U+77FF range
    # GBK mojibake: <40% in U+4E00-U+77FF, >40% in U+9400-U+9FFF
    total_cjk = sum(1 for c in content if 0x4E00 <= ord(c) <= 0x9FFF)
    if total_cjk < 50:
        return False
    common_cjk = sum(1 for c in content if 0x4E00 <= ord(c) <= 0x77FF)
    gbk_ext_cjk = sum(1 for c in content if 0x9400 <= ord(c) <= 0x9FFF)
    # Both conditions must be true AND common ratio must be very low
    if gbk_ext_cjk / total_cjk > 0.50 and common_cjk / total_cjk < 0.30:
        return True

    return False


def _detect_mojibake(content: str) -> bool:
    """Detect GBK-as-UTF-8 double-encoding mojibake (string input)."""
    return _detect_mojibake_bytes(content.encode("utf-8"))


def check_file_encoding(filepath: str) -> tuple[list[str], list[str]]:
    """Check compliance and report findings and warnings separately.

    Returns:
        (findings, warnings) — findings are FAIL-level (block commit),
        warnings are WARNING-level (do not block commit).

    语义修复（2026-06-25, OPS-2026062501）：
        原 CRLF 标记为 WARNING 文本但走 exit(1) 硬阻断，语义不一致。
        现 CRLF 改为真正的 WARNING（不阻断），保留 BOM/mojibake 的硬阻断。
        CRLF 应靠 .gitattributes + git add --renormalize 在仓库层解决，
        不靠每次提交时检查阻断（对标 GitHub/Linux/Google 实践）。
    """
    findings = []  # FAIL 级别，阻断提交
    warnings = []  # WARNING 级别，不阻断提交
    p = Path(filepath)
    if not p.exists():
        findings.append(f"INJ-007 FAIL: file '{filepath}' does not exist")
        return findings, warnings
    if p.is_dir():
        findings.append(f"INJ-007 FAIL: '{filepath}' is a directory, use --dir instead")
        return findings, warnings
    raw = p.read_bytes()
    if raw.startswith(BOM):
        findings.append(f"INJ-007 FAIL: file '{filepath}' has UTF-8 BOM — must be UTF-8 without BOM")
    if CRLF in raw:
        crlf_count = raw.count(CRLF)
        warnings.append(f"INJ-007 WARNING: file '{filepath}' has {crlf_count} CRLF line endings — should use LF")
    # 规则文件豁免：docs/01_policies_and_standards/rules/ 下的文件描述规则时
    # 引用 autoGuessEncoding 属合理引用，非违规（如 trae_028 描述 files.autoGuessEncoding=false）
    _filepath_norm = str(p).replace("\\", "/")
    _is_rules_file = "docs/01_policies_and_standards/rules/" in _filepath_norm
    if not _is_rules_file:
        for pattern in AUTO_GUESS_PATTERNS:
            if pattern in raw:
                findings.append(
                    f"INJ-007 FAIL: file '{filepath}' contains '{pattern.decode()}' — autoGuessEncoding must be false"
                )
    try:
        content = raw.decode("utf-8")
        if _detect_mojibake(content):
            findings.append(
                f"INJ-007 FAIL: file '{filepath}' contains GBK-as-UTF-8 mojibake — double-encoded garbled text detected"
            )
    except UnicodeDecodeError:
        pass
    return findings, warnings


def check_dir_encoding(dirpath: str) -> tuple[list[str], list[str]]:
    """Check compliance and report findings and warnings separately."""
    findings = []
    warnings = []
    p = Path(dirpath)
    if not p.exists():
        findings.append(f"INJ-007 FAIL: directory '{dirpath}' does not exist")
        return findings, warnings
    for f in p.rglob("*"):
        if f.suffix in (".py", ".md", ".yaml", ".yml", ".json", ".toml"):
            f_findings, f_warnings = check_file_encoding(str(f))
            findings.extend(f_findings)
            warnings.extend(f_warnings)
    return findings, warnings


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Encoding compliance check (INJ-007)")
    parser.add_argument("--file", type=str, help="Check encoding of a specific file")
    parser.add_argument("--dir", type=str, help="Check encoding of all files in directory")
    parser.add_argument("--scan", action="store_true", help="Scan entire project for mojibake")
    parser.add_argument("--warn-only", action="store_true", help="Only warn, do not fail")
    args = parser.parse_args()

    all_findings: list[str] = []  # FAIL 级别，阻断提交
    all_warnings: list[str] = []  # WARNING 级别，不阻断提交

    if args.file:
        f_findings, f_warnings = check_file_encoding(args.file)
        all_findings.extend(f_findings)
        all_warnings.extend(f_warnings)

    if args.dir:
        d_findings, d_warnings = check_dir_encoding(args.dir)
        all_findings.extend(d_findings)
        all_warnings.extend(d_warnings)

    if args.scan:
        mojibake_count = 0
        for f in REPO_ROOT.rglob("*"):
            if f.suffix not in (".py", ".md", ".yaml", ".yml", ".json", ".toml"):
                continue
            if "__pycache__" in str(f) or ".git" in str(f):
                continue
            try:
                content = f.read_text(encoding="utf-8")
                if _detect_mojibake(content):
                    rel = f.relative_to(REPO_ROOT)
                    all_findings.append(f"INJ-007 MOJIBAKE: {rel}")
                    mojibake_count += 1
            except (UnicodeDecodeError, OSError):
                pass
        if mojibake_count > 0:
            print(f"\nTotal mojibake files: {mojibake_count}")

    if not any([args.file, args.dir, args.scan]):
        print("Usage: check_encoding.py --file <path> | --dir <path> | --scan")
        sys.exit(EXIT_ERROR)

    for finding in all_findings:
        print(finding)
    for warning in all_warnings:
        print(warning)

    # 只有 findings 阻断，warnings 不阻断（语义修复 OPS-2026062501）
    if all_findings and not args.warn_only:
        sys.exit(EXIT_FINDINGS)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
