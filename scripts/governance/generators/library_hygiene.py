# [BLUEPRINT] MOD-LIB-003 | docs/03_modules/_domain_library/blueprint.md | §3
# [MODULE] scripts.governance.generators.library_hygiene
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] Owner 月度卫生批（只出候选清单，处置=Owner 机械判定月批）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读盘点零删除（Owner 机械判定铁律：候选清单禁自动处置）；四类候选=①docs/_working 30 天+临期文档 ②.runtime/tmp 7 天+临时件 ③logs/ 30 天+未在册日志 ④data/cache 30 天+缓存；报告自带索书号入 docs/_working/ultimate_library/HYGIENE.md；阈值常量模块级（thresholds 纪律）
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 盘点异常折叠进报告 warn 区，退出码 0/1（有候选=0，无候选=0；异常=2）
# [TESTS] tests/library/test_library_hygiene.py
# [A_module] module_id=MOD-LIB-003 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""library_hygiene.py — 图书馆月度卫生命令（ulib3 T9）：一条命令出候选清单，Owner 月批。

Usage::

    python scripts/governance/generators/library_hygiene.py
# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/generators/library_hygiene.yaml
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Final

from zephyr.shared.io.paths import REPO_ROOT

__all__: Final[list[str]] = ["run_hygiene"]

_OUT: Final[Path] = Path("docs/_working/ultimate_library/HYGIENE.md")
_DOCS_WORKING_DAYS: Final[int] = 30
_RUNTIME_TMP_DAYS: Final[int] = 7
_LOGS_DAYS: Final[int] = 30
_LOG_REGISTRY_REL: Final[str] = (
    "docs/01_policies_and_standards/_registry/catalogs/registry_of_logs.yaml"
)


def _scan_dir_candidates(repo: Path, rel_dir: str, days: int, now: float, exclude_prefixes: list[str] | None = None) -> list[str]:
    """单目录 mtime 超龄扫描（可选前缀排除），返回仓内相对路径列表。"""
    out: list[str] = []
    base = repo / rel_dir
    if not base.is_dir():
        return out
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        try:
            aged = (now - p.stat().st_mtime) > days * 86400
        except OSError:
            continue
        if not aged:
            continue
        rel_posix = str(p.relative_to(repo)).replace("\\", "/")
        if exclude_prefixes and any(rel_posix.startswith(pre) for pre in exclude_prefixes):
            continue
        out.append(rel_posix)
    return out


def _collect_logs_unregistered(repo: Path, days: int, now: float, warn: list[str]) -> list[str]:
    """logs/ 超龄且不命中任何日志抽屉前缀（未在册=编外日志）。"""
    import yaml  # noqa: PLC0415

    patterns: list[str] = []
    reg = repo / _LOG_REGISTRY_REL
    if reg.exists():
        try:
            data = yaml.safe_load(reg.read_text(encoding="utf-8")) or {}
            for e in data.get("logs") or []:
                path = str(e.get("path") or "").strip()
                if path:
                    patterns.append(path)
        except Exception as exc:  # noqa: BLE001 — 索引不可读降级全量候选
            warn.append(f"registry_of_logs 不可读（{exc}），日志候选可能虚高")
    return _scan_dir_candidates(repo, "logs", days, now, exclude_prefixes=[p.rstrip("*") for p in patterns])


def run_hygiene(root: str = ".") -> dict[str, Any]:
    """四类候选盘点：临期文档/临时件/未在册日志/缓存（零删除，只出清单）。

    Args:
        root: 仓库根。

    Returns:
        {docs_working, runtime_tmp, logs_unregistered, data_cache, warn}。
    """
    from zephyr.shared.utils.time_utils import now_utc  # noqa: PLC0415 — 生成器禁 datetime.now/time.time，SSoT 时钟

    repo = Path(root)
    now = now_utc().timestamp()
    warn: list[str] = []
    docs_working = _scan_dir_candidates(repo, "docs/_working", _DOCS_WORKING_DAYS, now)
    runtime_tmp = _scan_dir_candidates(repo, ".runtime/tmp", _RUNTIME_TMP_DAYS, now)
    logs_unregistered = _collect_logs_unregistered(repo, _LOGS_DAYS, now, warn)
    data_cache = _scan_dir_candidates(repo, "data/cache", _LOGS_DAYS, now)
    result = {
        "docs_working": sorted(docs_working),
        "runtime_tmp": sorted(runtime_tmp),
        "logs_unregistered": sorted(logs_unregistered),
        "data_cache": sorted(data_cache),
        "warn": warn,
    }
    _write_report(repo, result)
    return result


def _write_report(repo: Path, result: dict[str, Any]) -> None:
    """写候选清单报告（零处置，Owner 月批）。"""
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    lines = [
        "---",
        'asset_id: "DOC:docs/_working/ultimate_library/HYGIENE.md"',
        'ttl: "task_bound"',
        'doc_type: "audit_report"',
        "---",
        "",
        "# 图书馆月度卫生候选清单（零处置，Owner 月批）",
        "",
        f"- 盘点时戳（UTC）：{stamp}",
        "- 铁律：本清单只列候选，不自动删除；处置=Owner 机械判定后按死亡证明制执行（08 §3.1）。",
        "",
        f"## ① docs/_working 30 天+ 临期文档：{len(result['docs_working'])}",
        "",
    ]
    lines += [f"- {x}" for x in result["docs_working"][:100]]
    lines += ["", f"## ② .runtime/tmp 7 天+ 临时件：{len(result['runtime_tmp'])}", ""]
    lines += [f"- {x}" for x in result["runtime_tmp"][:100]]
    lines += ["", f"## ③ logs/ 30 天+ 未在册日志：{len(result['logs_unregistered'])}", ""]
    lines += [f"- {x}" for x in result["logs_unregistered"][:100]]
    lines += ["", f"## ④ data/cache 30 天+ 缓存：{len(result['data_cache'])}", ""]
    lines += [f"- {x}" for x in result["data_cache"][:100]]
    if result["warn"]:
        lines += ["", "## 盘点警告", ""]
        lines += [f"- {w}" for w in result["warn"]]
    out = repo / _OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    """CLI 入口：打印摘要。"""
    result = run_hygiene(str(REPO_ROOT))
    print(
        f"hygiene: docs_working={len(result['docs_working'])} runtime_tmp={len(result['runtime_tmp'])} "
        f"logs_unregistered={len(result['logs_unregistered'])} data_cache={len(result['data_cache'])} report={_OUT}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
