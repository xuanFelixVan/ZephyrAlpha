# [BLUEPRINT] MOD-GOV_CHECK_ALGO_FLOW | docs/03_modules/_cross_layer/gov_scripts/blueprint.md | §
# [MODULE] scripts.governance.d7_code.compare_pytest_configs
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib（pathlib/re/configparser）
# [CONSUMERS] .pre-commit-config.yaml（建议挂点）/ CI 批量兜底 / 人工排查
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 纯 stdlib 只读；比较对象=pyproject.toml [tool.pytest.ini_options] vs .runtime/tmp/pytest_min.ini；
#   漂移三类：markers 键集不相等 / pyproject 有 timeout 而 ini 缺失或值不同 / ini 含 cache_dir（与
#   -p no:cacheprovider 组合 INTERNALERROR 陷阱，P1-4 注记）；比较仅对齐"精简配置应继承的语义"，
#   不要求全量等值（ini 刻意省略 addopts -v/--tb/filterwarnings）；
#   pytest_min.ini 不存在视为漂移（交接文档跑法依赖它）；exit 0=一致 / 1=漂移 / 2=error
# [MODIFY-GUARD] 无
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 永不抛异常——解析失败降级 exit 2 + stderr 提示
# [TESTS] tests/governance/d7_code/test_compare_pytest_configs.py
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 校验器 CLI（pre-commit/CI 按需事件触发，非常驻服务）
"""compare_pytest_configs.py — pytest 双配置漂移看守（2026-09-15 外审遗留②）。

病根：同一测试域存在两套 pytest 配置——pyproject.toml（全量跑法）与
.runtime/tmp/pytest_min.ini（交接文档精简跑法）。历史上精简版缺
--strict-markers/timeout/markers 注册，与全量跑法语义漂移：同测试两配置判定
不一致 = "换配置就绿/红" 的 flaky 温床（外审 P1-4 复验期实证：
-p no:cacheprovider × pyproject cache_dir 组合直接 INTERNALERROR）。

本器看守三类漂移（对齐"精简配置应继承的语义"，不要求全量等值）：
  A. markers 键集：两边注册的 marker 名集合必须相等（strict-markers 下
     未注册 marker 会硬失败——集合不一致=某配置下测试必红）；
  B. timeout：pyproject 设了 timeout 时 ini 必须存在且同值（假挂起兜底双配置生效）；
  C. cache_dir 禁入 ini：ini 面向 -p no:cacheprovider 跑法，写 cache_dir 必炸。

Usage::

    python scripts/governance/d7_code/compare_pytest_configs.py          # 校验，exit 0/1/2
    python scripts/governance/d7_code/compare_pytest_configs.py --json   # 结构化输出（CI）
"""

from __future__ import annotations

import argparse
import configparser
import json
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS  # noqa: E402

_PYPROJECT = Path("pyproject.toml")
_PYTEST_MIN = Path(".runtime/tmp/pytest_min.ini")

_MARKERS_KEY_RE = re.compile(r'^([A-Za-z0-9_]+)\s*:', re.MULTILINE)
_TIMEOUT_KEY_RE = re.compile(r'^timeout\s*=\s*(\d+)', re.MULTILINE)


def _parse_pyproject_markers(text: str) -> tuple[set[str], int | None]:
    """从 pyproject [tool.pytest.ini_options] 提取 marker 名集合与 timeout。

    TOML 数组跨行：只取 ini_options 段，逐行匹配 `"name: ..."` 条目。
    """
    m = re.search(r"\[tool\.pytest\.ini_options\](.*?)(?=^\[|\Z)", text, re.S | re.M)
    if not m:
        return set(), None
    section = m.group(1)
    markers: set[str] = set()
    mm = re.search(r"^markers\s*=\s*\[(.*?)\]", section, re.S | re.M)
    if mm:
        for entry in re.finditer(r'"([^":]+)\s*:', mm.group(1)):
            markers.add(entry.group(1).strip())
    tm = _TIMEOUT_KEY_RE.search(section)
    return markers, (int(tm.group(1)) if tm else None)


def _parse_ini(cfg_path: Path) -> tuple[set[str], int | None, bool]:
    """解析 pytest_min.ini：markers 名集合 / timeout / 是否含 cache_dir。

    pytest ini 的 markers 支持分号单行写法（2026-09-15 对齐后格式），configparser
    按 ';' 分隔逐条再按首个 ':' 切名。
    """
    cp = configparser.ConfigParser(interpolation=None, delimiters=("=",), comment_prefixes=("#",))
    cp.read(cfg_path, encoding="utf-8")
    if not cp.has_section("pytest"):
        return set(), None, False
    sec = cp["pytest"]
    markers: set[str] = set()
    raw = sec.get("markers", "") or ""
    for part in raw.split(";"):
        part = part.strip()
        if not part:
            continue
        name = part.split(":", 1)[0].strip().strip("'\"")
        if name:
            markers.add(name)
    timeout = sec.getint("timeout", fallback=None)
    has_cache_dir = "cache_dir" in sec
    return markers, timeout, has_cache_dir


def compare(repo_root: Path) -> tuple[list[str], dict]:
    """执行三类漂移比较。返回 (findings, detail)。"""
    findings: list[str] = []
    detail: dict = {"markers_pyproject": [], "markers_ini": [], "timeout_pyproject": None, "timeout_ini": None, "cache_dir_in_ini": False}

    py_toml = repo_root / _PYPROJECT
    ini = repo_root / _PYTEST_MIN
    if not py_toml.exists():
        return ["pyproject.toml 不存在（异常仓库状态）"], detail
    if not ini.exists():
        # 交接文档跑法（-c .runtime/tmp/pytest_min.ini）依赖此文件；缺失=跑法断裂
        findings.append(f"pytest_min.ini 缺失: {_PYTEST_MIN.as_posix()}（交接精简跑法断裂）")
        return findings, detail

    py_markers, py_timeout = _parse_pyproject_markers(py_toml.read_text(encoding="utf-8", errors="replace"))
    ini_markers, ini_timeout, has_cache = _parse_ini(ini)
    detail["markers_pyproject"] = sorted(py_markers)
    detail["markers_ini"] = sorted(ini_markers)
    detail["timeout_pyproject"] = py_timeout
    detail["timeout_ini"] = ini_timeout
    detail["cache_dir_in_ini"] = has_cache

    # A. markers 键集相等（strict-markers 双配置语义一致的前提）
    only_py = py_markers - ini_markers
    only_ini = ini_markers - py_markers
    if only_py:
        findings.append(f"markers 仅 pyproject 注册（ini 缺，strict 下该 marker 测试必红）: {sorted(only_py)}")
    if only_ini:
        findings.append(f"markers 仅 ini 注册（pyproject 缺，全量跑法语义缺失）: {sorted(only_ini)}")

    # B. timeout 继承
    if py_timeout is not None and ini_timeout != py_timeout:
        findings.append(f"timeout 漂移: pyproject={py_timeout}s, pytest_min={ini_timeout}（B1 假挂起兜底须双配置生效）")

    # C. cache_dir 禁入 ini（× -p no:cacheprovider = INTERNALERROR）
    if has_cache:
        findings.append("pytest_min.ini 含 cache_dir——与 -p no:cacheprovider 组合必 INTERNALERROR（pyproject P1-4 注记）")

    return findings, detail


def main(argv: list[str] | None = None, repo_root: Path | None = None) -> int:
    """Entry point: parse args, run comparison, return exit code.

    repo_root 可注入（测试隔离）；缺省取脚本所在仓根。
    """
    try:
        parser = argparse.ArgumentParser(description="pytest 双配置漂移看守")
        parser.add_argument("--json", action="store_true", help="结构化 JSON 输出（CI 消费）")
        args = parser.parse_args(argv)
        root = repo_root or _SCRIPT_DIR.parents[3]
        findings, detail = compare(root)
        if args.json:
            print(json.dumps({"ok": not findings, "findings": findings, "detail": detail}, ensure_ascii=False, indent=2))
        else:
            if findings:
                print(f"[DRIFT] pytest 双配置漂移 {len(findings)} 项:", file=sys.stderr)
                for f in findings:
                    print(f"  - {f}", file=sys.stderr)
                print("  修复: 同步 pyproject [tool.pytest.ini_options] 与 .runtime/tmp/pytest_min.ini（markers/timeout，ini 禁 cache_dir）", file=sys.stderr)
            else:
                print("[OK] pytest 双配置语义对齐（markers 集合相等 / timeout 继承 / ini 无 cache_dir）", file=sys.stderr)
        return EXIT_FINDINGS if findings else EXIT_PASS
    except Exception as e:  # noqa: BLE001 — 校验器永不抛
        print(f"[ERR] compare_pytest_configs 运行异常: {type(e).__name__}: {e}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
