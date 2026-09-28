# [BLUEPRINT] MOD-LIB-003 | docs/03_modules/_domain_library/blueprint.md | §3
# [MODULE] scripts.governance.generators.library_hygiene
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] Owner 月度卫生批（只出候选清单，处置=Owner 机械判定月批）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读盘点零删除（Owner 机械判定铁律：候选清单禁自动处置）；四类候选=①docs/_working created>30 天 task_bound 件（**判龄轴=frontmatter created，不用 mtime**：案卷 S2 §2.5 实测 mtime>30 天桶=0，git 操作天天碰 mtime，用它＝该类目永久空转）②.runtime/tmp 7 天+临时件 ③logs/ 30 天+未在册日志 ④data/cache 30 天+缓存；报告自带索书号入 docs/_working/ultimate_library/HYGIENE.md；阈值常量模块级（thresholds 纪律）；created 读不得者单列计数，禁静默消失
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

# 同目录治理脚本约定：把 _shared 的父目录挂进 sys.path，再按 `from _shared.x import y` 取共享件
# （直接 `from scripts.governance._shared...` 在作为脚本运行时不可导入）。
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

__all__: Final[list[str]] = ["run_hygiene"]

_OUT: Final[Path] = Path("docs/_working/ultimate_library/HYGIENE.md")
_DOCS_WORKING_DAYS: Final[int] = 30
_RUNTIME_TMP_DAYS: Final[int] = 7
_LOGS_DAYS: Final[int] = 30
# 只有 task_bound 件才是"该陈化"的种群；permanent/无 ttl 另桶上报，不混进候选。
_WORKING_TTL_OF_INTEREST: Final[str] = "task_bound"
_LOG_REGISTRY_REL: Final[str] = "docs/01_policies_and_standards/_registry/catalogs/registry_of_logs.yaml"


def _scan_dir_candidates(
    repo: Path, rel_dir: str, days: int, now: float, exclude_prefixes: list[str] | None = None
) -> list[str]:
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


def _tracked_working_docs(repo: Path) -> list[str]:
    """docs/_working 的 **tracked 面**（仓内相对路径，POSIX 分隔）。

    为什么只取 tracked：本项目有 gitignore 离库派生区与影子车道副本，rglob 盘面会把
    它们一起算进来（案卷 S8 §⑤14 的"untracked-phantom"教训），而候选处置只对在册件成立。
    """
    import subprocess  # noqa: PLC0415 — 仅本函数需要，避免模块级拉入 git 依赖

    try:
        r = subprocess.run(  # noqa: bare-subprocess  只读 git 清单，与全仓治理脚本同口径
            ["git", "ls-files", "--", "docs/_working"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(repo),
        )
    except Exception:  # noqa: BLE001 — git 不可用则本类目降级为空，交调用方记 warn
        return []
    if r.returncode != 0:
        return []
    return [ln.strip().replace("\\", "/") for ln in r.stdout.splitlines() if ln.strip()]


def _created_date(meta: dict | None) -> Any:
    """取 frontmatter `created` 并归一为 date；不可读/类型不对返回 None。

    YAML 会把未加引号的 `created: 2026-09-27` 直接解析成 datetime.date，
    加引号则成 str——两种都得吃下（只吃一种是假空转）。
    """
    import datetime as dt  # noqa: PLC0415

    if not isinstance(meta, dict):
        return None
    raw = meta.get("created")
    if isinstance(raw, dt.datetime):
        return raw.date()
    if isinstance(raw, dt.date):
        return raw
    txt = str(raw or "").strip().strip('"').strip("'")[:10]
    try:
        return dt.date.fromisoformat(txt)
    except ValueError:
        return None


def classify_working_docs(repo: Path, days: int, today: Any, tracked: list[str] | None = None) -> dict[str, list[str]]:
    """按 frontmatter `created` 给 docs/_working 的在册件分陈化三桶。

    判据取向（三条都是本仓踩过的坑，别改回去）：
    - **轴=created 不用 mtime**：案卷 S2 §2.5 实测 mtime>30 天桶=0（git checkout/merge/stash
      天天碰 mtime），用 mtime 判龄＝这个永久空转的类目看着在工作；
    - **ttl 必走 YAML 解析器**：`ttl: "task_bound"`（带引号变体，实测永久区 810 件）用裸正则
      会被判成"未声明 ttl"（反例=doc_lifecycle.py:152），引号变体是现成陷阱；
    - **读不得者单列**：created 缺失/坏日期进 `undated` 计数，禁静默消失——否则陈化存量
      可以靠"字段写坏"躲过盘点。

    Returns:
        {"aged","fresh","permanent","undated","missing_on_disk"}——`missing_on_disk` 必须
        单列：在册但盘上没有＝删除欠账（与"元数据缺失"是两种病，混进 undated 会把下一班
        人引去补字段而真正要处置的是删除事件）。
    """
    import datetime as dt  # noqa: PLC0415

    from _shared.frontmatter import parse_frontmatter_from_file  # noqa: PLC0415  同目录约定：_shared 父目录入 sys.path

    paths = _tracked_working_docs(repo) if tracked is None else tracked
    buckets: dict[str, list[str]] = {
        "aged": [],
        "undated": [],
        "fresh": [],
        "permanent": [],
        "missing_on_disk": [],
    }
    for rel in sorted(set(paths)):
        if not (repo / rel).is_file():
            buckets["missing_on_disk"].append(rel)
            continue
        meta = parse_frontmatter_from_file(repo / rel)
        ttl = str((meta or {}).get("ttl") or "").strip().strip('"').strip("'")
        if ttl and ttl != _WORKING_TTL_OF_INTEREST:
            buckets["permanent"].append(rel)
            continue
        created = _created_date(meta)
        if created is None:
            buckets["undated"].append(rel)
            continue
        age_days = (today - created).days if isinstance(today, dt.date) else 0
        (buckets["aged"] if age_days > days else buckets["fresh"]).append(rel)
    return buckets


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
    tracked_working = _tracked_working_docs(repo)
    if not tracked_working:
        warn.append("docs/_working tracked 面读到 0 件（git 不可用或仓无册件）——陈化类目本次不可信，勿据此判空")
    aging = classify_working_docs(repo, _DOCS_WORKING_DAYS, now_utc().date(), tracked=tracked_working)
    docs_working = aging["aged"]
    runtime_tmp = _scan_dir_candidates(repo, ".runtime/tmp", _RUNTIME_TMP_DAYS, now)
    logs_unregistered = _collect_logs_unregistered(repo, _LOGS_DAYS, now, warn)
    data_cache = _scan_dir_candidates(repo, "data/cache", _LOGS_DAYS, now)
    result = {
        "docs_working": sorted(docs_working),
        "docs_working_undated": sorted(aging["undated"]),
        "docs_working_fresh": sorted(aging["fresh"]),
        "docs_working_other_ttl": sorted(aging["permanent"]),
        "docs_working_missing_on_disk": sorted(aging["missing_on_disk"]),
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
        # 不写 doc_type：docs/_working 的 md 只允许 ttl=permanent|task_bound，多这一行
        # 会被放置/TTL 门整批打回（生成的报告若自带非法字段，等于每次跑都给自己埋雷）。
        "---",
        "",
        "# 图书馆月度卫生候选清单（零处置，Owner 月批）",
        "",
        f"- 盘点时戳（UTC）：{stamp}",
        "- 铁律：本清单只列候选，不自动删除；处置=Owner 机械判定后按死亡证明制执行（08 §3.1）。",
        "",
        f"## ① docs/_working created>{_DOCS_WORKING_DAYS} 天 task_bound 件：{len(result['docs_working'])}",
        "",
        "- 判龄轴=frontmatter `created`（**不用 mtime**：mtime>30 天桶实测=0，git 操作天天碰 mtime，"
        "用它的类目必然永久空转）；作用域=tracked 面（避开 gitignore 离库派生区与影子车道副本）。",
        f"- 同批上报不隐藏：created 读不得 {len(result.get('docs_working_undated') or [])} 件"
        f'（含 ttl 缺失/坏日期，这类件能靠"字段写坏"躲盘点，故必须计数）；'
        f"未到期 {len(result.get('docs_working_fresh') or [])} 件；"
        f"其他 ttl {len(result.get('docs_working_other_ttl') or [])} 件；"
        f"**在册但盘上缺失 {len(result.get('docs_working_missing_on_disk') or [])} 件**"
        "（删除欠账，与元数据缺失两种病，不并入 undated）。",
        "",
    ]
    lines += [f"- {x}" for x in result["docs_working"][:100]]
    undated = result.get("docs_working_undated") or []
    if undated:
        lines += ["", f"### ①.1 created 读不得（{len(undated)} 件，前 100）", ""]
        lines += [f"- {x}" for x in undated[:100]]
    missing = result.get("docs_working_missing_on_disk") or []
    if missing:
        lines += ["", f"### ①.2 在册但盘上缺失（{len(missing)} 件，前 100）＝删除欠账，勿当元数据问题处置", ""]
        lines += [f"- {x}" for x in missing[:100]]
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
    """CLI 入口：打印摘要（退出码契约不变：0=正常，2=异常）。"""
    result = run_hygiene(str(REPO_ROOT))
    print(
        f"hygiene: docs_working_aged={len(result['docs_working'])} "
        f"docs_undated={len(result.get('docs_working_undated') or [])} "
        f"docs_fresh={len(result.get('docs_working_fresh') or [])} "
        f"docs_other_ttl={len(result.get('docs_working_other_ttl') or [])} "
        f"runtime_tmp={len(result['runtime_tmp'])} "
        f"logs_unregistered={len(result['logs_unregistered'])} data_cache={len(result['data_cache'])} report={_OUT}"
    )
    if not result["docs_working"] and not result.get("docs_working_fresh") and not result.get("docs_working_undated"):
        # 三个桶全空＝该类目根本没跑起来（git 不可用/仓无册件），不是"真没有陈化件"。
        # 静默报 0 就是这条尺当年的死法，这里必须出声。
        print("WARN: docs/_working 三桶全空＝陈化盘点未生效，勿据此判空")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
