# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §pattern_code_fingerprint 扫描器（REG-PAT-001 #ARCH-BREG-002 配套）
# [MODULE] scripts.governance.d3_metadata.pattern_code_fingerprint
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib（argparse/ast/hashlib/pathlib/re）；yaml；zephyr.shared.io.file_utils
# [CONSUMERS] tests/governance/test_chart_pattern_registry_integrity.py（常设漂移蓝测）；#ARCH-BREG-002 门禁A（存在性）/门禁B（指纹对账）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读扫描默认零写入；--apply 显式授权才写注册表（CAS+写后 parse 校验+失败回滚）；
#   指纹=code_symbol 锚定符号所在实现模块整源 sha256（CRLF→LF 归一后）前 16 hex，
#   语义=模块级漂移覆盖（单函数指纹对规则级改动全盲，模块整源才让对账有真实覆盖力）；
#   幂等（已同指纹条目跳过）
# [MODIFY-GUARD] 写入锚点=条目块内 code_fingerprint 字段行（段内锚定，禁盲改）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 注册表不可读/parse 失败 → exit 1（fail-closed）；写后校验失败回滚写前字节并 exit 1；
#   --check 模式发现漂移/缺失 → exit 2（EXIT_FINDINGS）
# [TESTS] tests/governance/d3_metadata/test_pattern_code_fingerprint.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: AI 会话按需调用的 permanent CLI runner（code_fingerprint 扫描/回填通道，非 cron/非 daemon/非常驻服务；漂移常设执法由 tests 蓝测承载，本 CLI 仅 --apply 显式触发）
"""pattern_code_fingerprint — REG-PAT-001 code_fingerprint 扫描器（#ARCH-BREG-002 门禁A/B）。

schema v2.1 裁定：code_symbol 代码符号锚点 / code_fingerprint 实现指纹——库↔代码
双向索引与漂移对账。本工具补齐指纹半场：

- 门禁A（存在性）：code_symbol 指向的文件与符号必须真实存在（ast 解析验证）；
- 门禁B（漂移对账）：注册表 code_fingerprint vs 实现模块整源 sha256 比对，
  代码改动未回写指纹 → 漂移 finding（tests 蓝测常设执法，gate 接线留后续）。

用法::

    python scripts/governance/d3_metadata/pattern_code_fingerprint.py --check     # 只读对账
    python scripts/governance/d3_metadata/pattern_code_fingerprint.py --apply    # 回填/更新指纹
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import re
import sys
from pathlib import Path

import yaml

_SCRIPT_DIR = Path(__file__).resolve()
_REPO = _SCRIPT_DIR.parents[3]
_REGISTRY = (
    _REPO
    / "docs/01_policies_and_standards/_registry/catalogs/chart_pattern_registry.yaml"
)

_FP_PREFIX = "sha256:"


def module_fingerprint(py_path: Path) -> str:
    """实现模块整源指纹：rb 读 → CRLF→LF 归一 → sha256 前 16 hex（带前缀）。"""
    raw = py_path.read_bytes()
    text = raw.decode("utf-8").replace("\r\n", "\n")
    return _FP_PREFIX + hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def symbol_exists(py_path: Path, symbol: str) -> bool:
    """门禁A：文件内是否存在同名函数/类（ast 遍历，含类方法）。"""
    try:
        tree = ast.parse(py_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == symbol:
            return True
    return False


def parse_code_symbol(code_symbol: str) -> tuple[Path, str]:
    """"src/.../file.py::symbol" → (绝对 Path, symbol)。格式非法抛 ValueError。"""
    if "::" not in code_symbol:
        raise ValueError(f"code_symbol 缺 '::' 锚点: {code_symbol}")
    rel, sym = code_symbol.split("::", 1)
    return _REPO / rel, sym.strip()


def scan() -> tuple[list[str], dict[str, str]]:
    """门禁A+B 扫描。返回 (findings, {pattern_id: 应写指纹})。"""
    data = yaml.safe_load(_REGISTRY.read_text(encoding="utf-8"))
    findings: list[str] = []
    wanted: dict[str, str] = {}
    cache: dict[str, str] = {}
    for e in data.get("chart_patterns", []):
        sym = e.get("code_symbol")
        if not sym:
            continue
        pid = e.get("pattern_id", "?")
        try:
            py_path, symbol = parse_code_symbol(sym)
        except ValueError as exc:
            findings.append(f"{pid}: {exc}")
            continue
        if not py_path.exists():
            findings.append(f"{pid}: 实现文件不存在 {py_path.name}")
            continue
        if sym not in cache:
            cache[sym] = module_fingerprint(py_path)
        fp = cache[sym]
        if not symbol_exists(py_path, symbol):
            findings.append(f"{pid}: 符号 {symbol} 不存在于 {py_path.name}（门禁A）")
            continue
        cur = e.get("code_fingerprint")
        if cur != fp:
            kind = "未回填" if not cur else "漂移"
            findings.append(f"{pid}: code_fingerprint {kind}（门禁B）应={fp} 现={cur}")
            wanted[pid] = fp
    return findings, wanted


def apply_fingerprints() -> int:
    """把 scan() 的应写指纹回填注册表（单趟块重建 + CAS + 写后 parse 校验回滚）。

    2026-09-15 红蓝自纠：首版用"原文本偏移切片+累进替换"——首个块替换使文本长度
    变化后，后续块的 stale 偏移切错位（写后校验网兜住回滚，实弹实证防线有效）。
    治本=单趟 finditer 块重建（同 annotate_series 模式）：每个块独立变换后按原文
    分隔拼接，偏移不可能失效。
    """
    from zephyr.shared.io.file_utils import safe_write_text

    findings, wanted = scan()
    if not wanted:
        print("OK: 全部 code_fingerprint 已对账（零回填）")
        return 0

    # 单次 CAS：冲突即失败退出（工具幂等，重跑 --apply 即重试；无 sleep 轮询以守 M10 铁律）
    import hashlib

    raw = _REGISTRY.read_bytes()
    text = raw.decode("utf-8").replace("\r\n", "\n")
    base = hashlib.sha256(text.encode("utf-8")).hexdigest()
    pre_count = len(yaml.safe_load(text).get("chart_patterns", []))
    parts: list[str] = []
    last = 0
    replaced = 0
    for m in re.finditer(r'  - pattern_id: "([^"]+)"\n', text):
        block_start, pid = m.start(), m.group(1)
        nxt = text.find("  - pattern_id:", m.end())
        block_end = nxt if nxt >= 0 else len(text)
        if pid not in wanted:
            continue
        parts.append(text[last:block_start])
        last = block_end
        block = text[block_start:block_end]
        fp = wanted[pid]
        new_block, n = re.subn(
            r"^(\s*code_fingerprint:)\s*\S+.*$",
            lambda mm, fp=fp: f"{mm.group(1)} \"{fp}\"",
            block,
            count=1,
            flags=re.M,
        )
        if n == 0:
            # 无字段行则紧跟 code_symbol 插入（v1 老条目形态）
            new_block, n = re.subn(
                r"^(\s*code_symbol:\s*\"[^\"]+\")\s*$",
                lambda mm, fp=fp: f"{mm.group(1)}\n    code_fingerprint: \"{fp}\"",
                block,
                count=1,
                flags=re.M,
            )
        if n == 0:
            parts.append(block)
            continue
        parts.append(new_block)
        replaced += n
    parts.append(text[last:])
    new_text = "".join(parts)
    try:
        res = safe_write_text(_REGISTRY, new_text, expected_base_sha256=base, newline="")
        print(f"落盘: {res.written}")
    except Exception as exc:  # noqa: BLE001 — CAS 冲突=磁盘已被推进，重跑即重试（幂等）
        print(f"FAIL: CAS 冲突 ({type(exc).__name__})——重跑 --apply 即重试", file=sys.stderr)
        return 1
    # 写后校验：parse 过 + 逐条落位 + 条目数不变，失败回滚
    try:
        data = yaml.safe_load(_REGISTRY.read_text(encoding="utf-8"))
        entries = data.get("chart_patterns", [])
        if len(entries) != pre_count:
            raise ValueError(f"条目数漂移 {len(entries)}（写前 {pre_count}）")
        landed = {e["pattern_id"]: e.get("code_fingerprint") for e in entries}
        missing = [pid for pid, fp in wanted.items() if landed.get(pid) != fp]
        if missing:
            raise ValueError(f"{len(missing)} 条未落位: {missing[:3]}")
    except Exception as exc:  # noqa: BLE001
        from zephyr.shared.io.file_utils import atomic_write

        atomic_write(_REGISTRY, raw.decode("utf-8"), newline="")
        print(f"FAIL: 写后自检不过，已回滚写前字节: {exc}", file=sys.stderr)
        return 1
    print(f"OK: 回填 {replaced} 条指纹")
    return 0


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="REG-PAT-001 code_fingerprint 扫描器（门禁A/B）")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true", help="只读对账（默认）")
    g.add_argument("--apply", action="store_true", help="回填/更新指纹（显式授权写入）")
    args = ap.parse_args()

    if not _REGISTRY.exists():
        print(f"FAIL: 注册表不可达 {_REGISTRY}", file=sys.stderr)
        return 1

    findings, wanted = scan()
    for f in findings:
        print(f"  - {f}")
    if args.apply:
        return apply_fingerprints()
    if findings:
        print(f"DRIFT: {len(findings)} 条 finding（--apply 回填）")
        return 2
    print("OK: 门禁A/B 全过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
