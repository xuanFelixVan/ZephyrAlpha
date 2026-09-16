# [BLUEPRINT] MOD-GOV_CHECK_ALGO_FLOW | docs/03_modules/_cross_layer/gov_scripts/blueprint.md | §
# [MODULE] scripts.governance.d7_code.compare_pytest_configs
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib（pathlib/re/configparser）
# [CONSUMERS] .pre-commit-config.yaml（建议挂点）/ CI 批量兜底 / 人工排查
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 纯 stdlib 只读；比较对象=pyproject.toml [tool.pytest.ini_options] vs py.ini [pytest] 段
#   （精简跑法寄居根目录既有纳管件 py.ini——独立件 pytest_min.ini 需 .gitignore 单点放行，
#   而 .gitignore 是 PROTECTED-PATHS 须 Owner 审批，永久产物生命周期里不嵌人工闸，裁定#278）；
#   漂移四类：markers 键集不相等 / pyproject 有 timeout 而 ini 缺失或值不同 / ini 含 cache_dir（与
#   -p no:cacheprovider 组合 INTERNALERROR 陷阱，P1-4 注记）/ ini 段名非 [pytest]（pytest 对 .ini
#   只读 [pytest]，误写 [tool:pytest] 时 configfile 照打而选项零生效=静默放宽，比缺失更危险）；
#   比较仅对齐"精简配置应继承的语义"，不要求全量等值（ini 刻意省略 addopts -v/--tb/filterwarnings）；
#   markers 按 pytest linelist 语义逐行解析（单行分号写法 pytest 只注册第一个→本器判为漂移，不做宽容）；
#   py.ini 或其 [pytest] 段不存在视为漂移（交接文档跑法依赖它；永久产物禁入 .runtime/tmp TTL 区，
#   2026-09-16 外审遗留㉑→裁定#275→#278 三轮定址）；exit 0=一致 / 1=漂移 / 2=error
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
根目录 py.ini 的 ``[pytest]`` 段（交接文档精简跑法）。历史上精简版缺
--strict-markers/timeout/markers 注册，与全量跑法语义漂移：同测试两配置判定
不一致 = "换配置就绿/红" 的 flaky 温床（外审 P1-4 复验期实证：
-p no:cacheprovider × pyproject cache_dir 组合直接 INTERNALERROR）。
（位置沿革：原驻 .runtime/tmp/（TTL 清扫区，cleanup 会扫走→交接跑法断裂）→
 裁定#275 迁根目录独立件 pytest_min.ini（config/ 收不下 .ini：DCR-005 只允许
 .yaml/.yml/.json；``-c <ini>`` 的 rootdir=ini 所在目录）→ 落地时 .gitignore
 单点放行撞 PROTECTED-PATHS（Owner 闸，无 CLI 逃生旗）→ 裁定#278 改寄居已在
 root_directory_whitelist 且未被忽略的既有纳管件 py.ini，零 protected-path、
 零合同变更。）

本器看守四类漂移（对齐"精简配置应继承的语义"，不要求全量等值）：
  A. markers 键集：两边注册的 marker 名集合必须相等（strict-markers 下
     未注册 marker 会硬失败——集合不一致=某配置下测试必红）。ini 侧按 pytest
     真实语义解析：markers 是 linelist，**每行一个**，单行分号写法只注册第一个
     （历史静默失效根因，故本器不宽容该写法）；
  B. timeout：pyproject 设了 timeout 时 ini 必须存在且同值（假挂起兜底双配置生效）；
  C. cache_dir 禁入 ini：ini 面向 -p no:cacheprovider 跑法，写 cache_dir 必炸；
  D. 段名与 strict-markers：pytest 对 .ini 只读 ``[pytest]`` 段（``[tool:pytest]``
     仅 .cfg 生效，见 _pytest/config/findpaths.py 按后缀分支）。误段名时 pytest
     照样打印 ``configfile: py.ini`` 却零配置落地——markers/--strict-markers/
     timeout/norecursedirs 全失效，是比"文件缺失"更危险的静默放宽（2026-09-16
     移植当日探针实证：Unknown pytest.mark.slow + 3 passed）。同理 addopts 丢
     --strict-markers 会让 A 类漂移在精简跑法下不可见。

Usage::

    python scripts/governance/d7_code/compare_pytest_configs.py          # 校验，exit 0/1/2
    python scripts/governance/d7_code/compare_pytest_configs.py --json   # 结构化输出（CI）

    # 本段的消费方（两轮测试协议第 1 轮，见 pyproject P1-4 注记）：
    python -m pytest -c py.ini <目标目录>
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
# 永久产物禁入 TTL 区（原 .runtime/tmp/ 被 cleanup 扫走→交接跑法断裂，外审遗留㉑）。
# 裁定#278：寄居根目录既有纳管件 py.ini 的 [pytest] 段——独立件 pytest_min.ini 需
# .gitignore 单点放行，而 .gitignore 属 PROTECTED-PATHS（Owner 闸、无 CLI 逃生旗）。
_MIN_INI = Path("py.ini")

_MARKERS_KEY_RE = re.compile(r'^([A-Za-z0-9_]+)\s*:', re.MULTILINE)
_TIMEOUT_KEY_RE = re.compile(r'^timeout\s*=\s*(\d+)', re.MULTILINE)
_STRICT_MARKERS_RE = re.compile(r'--strict-markers\b')


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


def _parse_ini(cfg_path: Path) -> tuple[set[str], int | None, bool, bool, str | None]:
    """解析 py.ini：markers 名集合 / timeout / 是否含 cache_dir / 是否带 strict-markers / 段名。

    段名是第 5 返回值，且是**语义判据**而非装饰：pytest 对 ``.ini`` 只读 ``[pytest]`` 段
    （``[tool:pytest]`` 仅对 ``.cfg`` 生效——findpaths.load_config_dict_from_file 按后缀
    分支）。误段名下 pytest 仍打印 ``configfile:`` 却零配置落地，故本器把"只有
    [tool:pytest]"判为无有效段（值照解析，供调用方比对差异）。

    markers 按 pytest 真实语义取值——pytest 把它声明为 type="linelist"，
    `_getini` 仅按 **换行** 切分（configparser 对多行 markers 块正是以 '\\n' 连接），
    故一行一个 marker；单行分号写法在 pytest 眼里整体是一条（只注册第一个名字），
    本器同样只认第一个→与 pyproject 集合不等即报漂移（不宽容历史失效写法）。
    """
    cp = configparser.ConfigParser(interpolation=None, delimiters=("=",), comment_prefixes=("#",))
    cp.read(cfg_path, encoding="utf-8")
    section = "pytest" if cp.has_section("pytest") else ("tool:pytest" if cp.has_section("tool:pytest") else None)
    if section is None:
        return set(), None, False, False, None
    sec = cp[section]
    markers: set[str] = set()
    raw = sec.get("markers", "") or ""
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        name = line.split(":", 1)[0].strip().strip("'\"")
        if name:
            markers.add(name)
    timeout = sec.getint("timeout", fallback=None)
    has_cache_dir = "cache_dir" in sec
    has_strict = bool(_STRICT_MARKERS_RE.search(sec.get("addopts", "") or ""))
    return markers, timeout, has_cache_dir, has_strict, section


def compare(repo_root: Path) -> tuple[list[str], dict]:
    """执行四类漂移比较。返回 (findings, detail)。"""
    findings: list[str] = []
    detail: dict = {
        "markers_pyproject": [], "markers_ini": [], "timeout_pyproject": None, "timeout_ini": None,
        "cache_dir_in_ini": False, "ini_section": None, "strict_markers_in_ini": False,
    }

    py_toml = repo_root / _PYPROJECT
    ini = repo_root / _MIN_INI
    if not py_toml.exists():
        return ["pyproject.toml 不存在（异常仓库状态）"], detail
    if not ini.exists():
        # 交接文档跑法（-c py.ini）依赖此文件；缺失=跑法断裂
        findings.append(f"{_MIN_INI.name} 缺失: {_MIN_INI.as_posix()}（交接精简跑法断裂）")
        return findings, detail

    py_markers, py_timeout = _parse_pyproject_markers(py_toml.read_text(encoding="utf-8", errors="replace"))
    ini_markers, ini_timeout, has_cache, has_strict, ini_section = _parse_ini(ini)
    detail["markers_pyproject"] = sorted(py_markers)
    detail["markers_ini"] = sorted(ini_markers)
    detail["timeout_pyproject"] = py_timeout
    detail["timeout_ini"] = ini_timeout
    detail["cache_dir_in_ini"] = has_cache
    detail["ini_section"] = ini_section
    detail["strict_markers_in_ini"] = has_strict

    # D. 段名：pytest 对 .ini 只读 [pytest]，误段名=configfile 照打而选项零生效（静默放宽）
    if ini_section != "pytest":
        why = "只有 [tool:pytest]（该段名仅 .cfg 生效，pytest 对本文件整体忽略）" if ini_section else "无 [pytest] 段"
        findings.append(f"{_MIN_INI.name} {why}→精简跑法零配置（markers/timeout/strict 全失效）")
        return findings, detail
    if not has_strict:
        findings.append(f"{_MIN_INI.name} addopts 缺 --strict-markers→markers 集漂移在精简跑法下不可见")

    # A. markers 键集相等（strict-markers 双配置语义一致的前提）
    only_py = py_markers - ini_markers
    only_ini = ini_markers - py_markers
    if only_py:
        findings.append(f"markers 仅 pyproject 注册（ini 缺，strict 下该 marker 测试必红）: {sorted(only_py)}")
    if only_ini:
        findings.append(f"markers 仅 ini 注册（pyproject 缺，全量跑法语义缺失）: {sorted(only_ini)}")

    # B. timeout 继承
    if py_timeout is not None and ini_timeout != py_timeout:
        findings.append(f"timeout 漂移: pyproject={py_timeout}s, {ini.name}={ini_timeout}（B1 假挂起兜底须双配置生效）")

    # C. cache_dir 禁入 ini（× -p no:cacheprovider = INTERNALERROR）
    if has_cache:
        findings.append(f"{ini.name} 含 cache_dir——与 -p no:cacheprovider 组合必 INTERNALERROR（pyproject P1-4 注记）")

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
                print(
                    "  修复: 同步 pyproject [tool.pytest.ini_options] 与 py.ini [pytest] 段"
                    "（段名必须是 [pytest]·.ini 中 [tool:pytest] 被忽略 / markers 逐行注册·每行一个 /"
                    " timeout 同值 / addopts 保 --strict-markers / 禁 cache_dir）",
                    file=sys.stderr,
                )
            else:
                print("[OK] pytest 双配置语义对齐（ini 段名 [pytest] / markers 集合相等 / timeout 继承 /"
                      " addopts 带 --strict-markers / ini 无 cache_dir）", file=sys.stderr)
        return EXIT_FINDINGS if findings else EXIT_PASS
    except Exception as e:  # noqa: BLE001 — 校验器永不抛
        print(f"[ERR] compare_pytest_configs 运行异常: {type(e).__name__}: {e}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
