# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_static_manifest_drift
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
validate_static_manifest_drift.py — GATE-21 静态清单漂移阻断

顺序运行所有静态清单生成器的 --check 模式。自动生成版与磁盘版任何不一致
均触发硬失败（exit 1）。

权威依据：AGENTS.md 运维红线「静态清单禁手工维护」——任何"条目列表 + 计数"清单
必须由生成器产出（Type A：从代码/配置派生）或以 schema 为输入（Type B），
禁止手工维护条目（手工维护必然与真源漂移）。

检查清单：
  1. script_manifest.yaml — via generate_script_manifest.py --check
  2. gate_registry.yaml   — via generate_gate_registry.py --check

治本（2026-07-17）：
  - 清理代码退化结构（双 docstring / 重复 import / 游离 shebang / __manifest__ 块）
  - CHECKS 补齐 gate_registry.yaml（原仅 script_manifest.yaml，漏检门禁登记表漂移）
  - 输出消息 GATE-19 → GATE-21（2026-06-30 簇3合并重命名后消息未同步）
  - §6.16 断头引用 → §6.2 → §6.3（AGENTS.md 原无 §6.16，2026-07-17 治本补建 §6.2，2026-07-20 因新增临时文件分类存放铁律顺延为 §6.3）
  - 自举 sys.path 含 src/ + 子进程注入 PYTHONPATH=src，消除对调用方环境的依赖
    （原 validator 在未设 PYTHONPATH=src 的环境下崩溃 ModuleNotFoundError: No module named 'zephyr'）

Usage:
    python validate_static_manifest_drift.py --check
    python validate_static_manifest_drift.py --auto-fix
    python validate_static_manifest_drift.py --heal-derived-totals   # 只刷派生标量（单行）
"""

from __future__ import annotations

__manifest__ = """
args:
- {flag: --check, type: bool, description: "检测漂移，不一致时 exit 1"}
- {flag: --auto-fix, type: bool, description: "先跑各台 fix 通道再复判定（生成器台重生成 + 自洽台只刷派生标量）"}
- {flag: --heal-derived-totals, type: bool, description: "只把各自洽台的声明标量按段长度就地刷正（单行改写，不再生整册）"}
description: GATE-21 静态清单漂移阻断——顺序运行所有静态清单生成器的 --check 模式，自动生成版与磁盘版不一致即硬失败
dimensions:
- D1
- D5
priority: P1
timeout_seconds: 120
warn_only: false
"""

import os
import subprocess
import sys
from pathlib import Path

# 自举 sys.path（顺序敏感）：
#   1. scripts/governance/ —— import _shared.*
#   2. <repo_root>/src      —— _shared.constants 内部 import zephyr.*（治本：原缺此行）
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists())
_REPO_ROOT = _GOV_DIR.parent.parent  # scripts/governance -> scripts -> <repo_root>
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))
_SRC_DIR = _REPO_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from _shared.constants import EXIT_FINDINGS, EXIT_PASS  # noqa: E402
from _shared.encoding import ensure_utf8_stdout  # noqa: E402

ensure_utf8_stdout()

# 子进程环境：生成器 import _shared.constants → import zephyr，需 src/ 在 PYTHONPATH。
# 治本：原 subprocess.run 未传 env，子进程在未设 PYTHONPATH=src 的环境下崩溃。
_pp_parts = [str(_SRC_DIR)]
if os.environ.get("PYTHONPATH"):
    _pp_parts.append(os.environ["PYTHONPATH"])
_SUBPROCESS_ENV = {**os.environ, "PYTHONPATH": os.pathsep.join(_pp_parts)}

GENERATORS_DIR = _GOV_DIR / "generators"
SYNCERS_DIR = _GOV_DIR / "d5_architecture" / "syncers"

CHECKS = [
    {
        "name": "script_manifest.yaml",
        "cmd": [sys.executable, str(GENERATORS_DIR / "generate_script_manifest.py"), "--check"],
        "fix": [sys.executable, str(GENERATORS_DIR / "generate_script_manifest.py")],
    },
    {
        "name": "gate_registry.yaml",
        "cmd": [sys.executable, str(GENERATORS_DIR / "generate_gate_registry.py"), "--check"],
        "fix": [sys.executable, str(GENERATORS_DIR / "generate_gate_registry.py")],
    },
    # 注（2026-08-19 退库终态跟进）：原 blueprint_registry.yaml 检查已摘除——
    # 该文件经 #ARCH-BP-REGISTRY-DELETION-001 后续裁定正式派生退库（commit 03df6215e8：
    # 100% 可由 frontmatter 重生成=派生物，盘文件删除+.gitignore 入列+
    # check_no_commit_derived 扩列防重新跟踪）。文件缺失从"事故"翻转为"决策终态"，
    # dry-run 缺文件即 exit 2 的防删检测已过时（防重新跟踪由 check_no_commit_derived 承接）；
    # triple_alignment 消费侧已改 frontmatter 现算回退（同批治本）。
    {
        "name": ".importlinter forbidden_modules",
        "cmd": [sys.executable, str(GENERATORS_DIR / "generate_importlinter.py"), "--check"],
        "fix": [sys.executable, str(GENERATORS_DIR / "generate_importlinter.py")],
    },
    # 册内自洽（2026-09-24 本包补，真源=docs/_working/audit_fix/lanes/L4_registry_counts/）：
    # 上面 gate_registry 的 --check 只比对"声明计数 vs 生成器算出的计数"，从不比对
    # "声明计数 vs 在册段实际长度"⇒ 队列落地把条目推进了、标量钉在旧值时检测器全盲
    # （实测 total_gates=174 而 gates 实 180 带病 2 天，GATE-21 在册却报不出）。
    # 现按 audit 尺Q 的口径把自洽检查立成常驻闸。作用域先只点两台（含尺Q 实测出的
    # 两台失真），扩到全 catalogs 扫是加文件名一行的事——本轮不扩面，避免在其他会话
    # 批次在飞时把无关提交打红（判读见 L4 挖矿簿 §3）。
    {
        "name": "gate_registry.yaml (declared total == section length)",
        "selfcheck": {
            "path": "docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml",
            "pairs": {"total_gates": "gates"},
        },
        # fix 通道改指"标量就地自愈"（lane_derived_books 20260925）：原先直指整册生成器，
        # 而热册的生成器重跑必然连带条目块换位（实测 gate_registry 143 增/143 删），
        # 与"只修一个派生标量"的判据不成比例——判据与通道必须同口径，否则 --auto-fix
        # 每触发一次就往热册里搅一次他人条目（EVAP 病形）。条目内容漂移由上一条
        # 生成器台（gate_registry.yaml）的 fix 负责，两半各修各的、互不越界。
        "fix": [sys.executable, str(_SCRIPT_DIR), "--heal-derived-totals"],
    },
    {
        "name": "rule_catalog_registry.yaml (declared total == section length)",
        "selfcheck": {
            "path": "docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml",
            "pairs": {"total_files": "files"},
        },
        "fix": [sys.executable, str(_SCRIPT_DIR), "--heal-derived-totals"],
    },
    # 2026-09-27 st-chief6-20260927：in_process 门禁名册点名入检（与落地侧配对表同源，
    # 由 test_landing_pairs_agree_with_gate21_selfcheck 强制相等）。上面"本轮不扩面"的决定
    # 针对的是"扫全 catalogs"，本条是个案定点：该册正被每条加门车道频繁追加条目，而它的
    # 标量两投皆零效果（dev 实测 declared 103 vs gates 实长 104，FMS 38168467d1 同型），
    # 不点名=常驻盲区。代价已知：本袋与后续册修复袋之间数分钟内，触发本台的提交会见到该册红，
    # 由紧随的册触碰袋经自愈消解。
    {
        "name": "in_process_gate_registry.yaml (declared total == section length)",
        "selfcheck": {
            "path": "docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml",
            "pairs": {"total_gates": "gates"},
        },
        "fix": [sys.executable, str(_SCRIPT_DIR), "--heal-derived-totals"],
    },
]


def derived_total_pairs() -> dict[str, dict[str, str]]:
    """册名 → {声明标量: 集合段}——GATE-21 自洽台的配对对外读口。

    存在的唯一理由＝让"检测口径"与"落地侧自愈口径"可被一把尺直接比对
    （见 tests/governance/test_audit_fix_lanes_rulers.py 的配对一致性尺）。
    """
    out: dict[str, dict[str, str]] = {}
    for chk in CHECKS:
        sc = chk.get("selfcheck") or {}
        pairs = sc.get("pairs")
        if pairs:
            out[Path(str(sc.get("path", ""))).name] = dict(pairs)
    return out


def heal_derived_totals(root: Path | None = None) -> list[str]:
    """把各 selfcheck 台的派生计数标量按同名段实际长度**就地**刷正，返回逐台读数。

    为什么单独立一条通道而不是"重跑生成器"（lane_derived_books 20260925 实测定性）：
    派生标量有两个失真来源，都要求"只改那一行"——
    ① 队列条目级合并器对标量/头部行恒取 ours（防陈旧快照吃热册头部的正确设计），
       于是标量永远进不来（audit_fix_ledger S-24 三次独立实证）；
    ② 生成器重跑会连带条目块换位/条目内容再生，在热册上是百行级 churn
       （gate_registry 实测 143 增/143 删），拿它当"修一个数字"的通道不成比例。
    现口径：检测判据（selfcheck 台）、落地自愈（commit_queue_landing._heal_derived_totals）、
    修复通道（本函数）三者共用一份配对表 `derived_total_pairs()` 与一个行级改写真源
    `zephyr.shared.io.yaml_utils.heal_derived_scalars`——两份配置各写一次必漂移。

    保守面与落地侧逐条同源（真源已收敛到共享件）：顶层同键必须恰好一行、段必须是集合、
    标量必须是整数、已一致不动；改不了的情况返回读数交调用方判红，绝不静默放行。
    """
    from zephyr.shared.io.file_utils import safe_write_text  # noqa: PLC0415
    from zephyr.shared.io.yaml_utils import heal_derived_scalars  # noqa: PLC0415

    base = Path(root or _REPO_ROOT)
    notes: list[str] = []
    seen: set[str] = set()
    for chk in CHECKS:
        sc = chk.get("selfcheck") or {}
        rel = str(sc.get("path", ""))
        pairs = sc.get("pairs") or {}
        if not rel or not pairs or rel in seen:
            continue
        seen.add(rel)
        p = base / rel
        name = p.name
        if not p.is_file():
            notes.append(f"SKIP {name}: 册不存在（无从自愈）")
            continue
        with p.open("r", encoding="utf-8", newline="") as f:
            text = f.read()
        out, changes = heal_derived_scalars(text, pairs)
        if not changes:
            drift = _run_selfcheck(chk)
            notes.append(f"NOOP {name}: " + ("一致" if drift is None else f"仍失真且保守面挡下——{drift}"))
            continue
        res = safe_write_text(p, out, newline="")
        if not res:
            notes.append(f"FAIL {name}: safe_write_text 拒绝/冲突（CAS），未写盘: {res}")
            continue
        notes.append(
            f"HEALED {name}: " + "；".join(f"{s} {o} → {n}（按段实际长度重算，仅此 1 行）" for s, o, n in changes)
        )
    return notes


def _pairs_drift(text: str, name: str, pairs: dict[str, str]) -> str | None:
    """一份字节 → 声明计数 vs 同名段实际长度；失真返回描述，一致返回 None。"""
    import yaml  # noqa: PLC0415

    try:
        data = yaml.safe_load(text) or {}
    except Exception as exc:  # noqa: BLE001 — 解析失败=失真，不得静默放行
        return f"{name} YAML 解析失败: {type(exc).__name__}: {exc}"
    if not isinstance(data, dict):
        return f"{name} 顶层非映射（自洽键漂移）"
    for key, section in pairs.items():
        declared = data.get(key)
        actual = data.get(section)
        if declared is None or not isinstance(actual, (list, dict)):
            return f"{name} 缺 {key} 或段 {section} 非集合（自洽键漂移）"
        try:
            declared_n = int(declared)
        except (TypeError, ValueError):
            return f"{name} 声明 {key}={declared!r} 不是整数（自洽键漂移）"
        if declared_n != len(actual):
            return f"DRIFT: {name} 声明 {key}={declared} ≠ {section} 实际 {len(actual)}"
    return None


def _git_show_text(rel_path: str, ref: str) -> str | None:
    """``git show <ref>:<path>`` 取字节；ref="" 即暂存面（``:path``）。取不到返回 None。"""
    from zephyr.governance.audit._git_helpers import git_show_file  # noqa: PLC0415

    return git_show_file(str(_REPO_ROOT), rel_path.replace("\\", "/"), ref)


def _git_probe(args: list[str]) -> tuple[int, str]:
    """跑一条只读 git 命令，返回 (rc, stdout+stderr 小写)。异常按探测失败返回 (-1, ...)。"""
    try:
        fr = subprocess.run(  # noqa: bare-subprocess  git 只读探测，非 Python spawn
            ["git", *args],
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=_SUBPROCESS_ENV,
            timeout=30,
        )
    except Exception as exc:  # noqa: BLE001 — 探测失败要能被调用方判红，不在此处放行
        return -1, f"{type(exc).__name__}: {exc}"
    return fr.returncode, ((fr.stdout or "") + (fr.stderr or "")).lower()


def _book_surface(rel_path: str) -> tuple[str, str | None]:
    """提交绑定面字节：暂存面优先，其次在册面（HEAD）。返回 (口径, 文本或 None)。

    F-AUDITFIX-SELFREAD-01（2026-09-26）：本台此前只读工作树字节，主区的脏盘会把"在册面失真"
    读成 PASS（实测：dev 上 gate_registry 声明 174 而 gates 段 180 时，主区 --check 绿、
    干净树 rc=1）——检测器犯了自己要抓的病，与 registry_alignment 的 HEAD 锚同族。
    暂存面优先是为了不自锁死：修册那一笔在门禁时刻字节只存在于 index，
    只认 HEAD 会让"在册面失真"既拦不住也修不掉。
    口径 ∈ staged / head / untracked / no-book / probe-fail（后两态无文本）。
    """
    rc, out = _git_probe(["rev-parse", "--verify", "--quiet", "HEAD"])
    if rc != 0:
        if "not a git repository" in out or rc == 1:
            return "no-book", None
        return "probe-fail", None
    staged = _git_show_text(rel_path, "")
    if staged is not None:
        return "staged", staged
    head = _git_show_text(rel_path, "HEAD")
    if head is not None:
        return "head", head
    rc, out = _git_probe(["ls-files", "--error-unmatch", "--", rel_path.replace("\\", "/")])
    if rc == 0:
        # 已跟踪却取不到字节＝探测失败，不得当成"册里没有"放行
        return "probe-fail", None
    if "did not match" in out or "error: pathspec" in out:
        return "untracked", None
    return "probe-fail", None


def _run_selfcheck(item: dict) -> str | None:
    """声明计数 vs 同名段实际长度；不一致返回漂移描述，一致返回 None。

    刻意独立于生成器实现（生成器 --check 的口径是"磁盘 vs 生成"，本函数是
    "册内自洽"——两半合起来才是完整的静态清单失真定义）。
    判两面：工作树面（本包将写进暂存区的字节）+ 提交绑定面（暂存/index 优先，否则 HEAD）。
    提交绑定面不适用时（非仓库/册外新件）显式打 NOTE，禁把"无从判定"读成"已判定为绿"。
    """
    rel = str(item["selfcheck"]["path"])
    p = _REPO_ROOT / rel
    if not p.is_file():
        return f"{p.name} 不存在（自洽检查无从判定）"
    try:
        disk_text = p.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 — 读不到字节=失真，不得静默放行
        return f"{p.name} 工作树字节读取失败: {type(exc).__name__}: {exc}"
    msg = _pairs_drift(disk_text, p.name, item["selfcheck"]["pairs"])
    if msg:
        return msg
    surface, book_text = _book_surface(rel)
    if book_text is not None:
        book_msg = _pairs_drift(book_text, p.name, item["selfcheck"]["pairs"])
        if book_msg:
            return f"[{'暂存' if surface == 'staged' else '在册'}面] {book_msg}"
        return None
    if surface == "probe-fail":
        return f"{p.name} 提交绑定面取数失败（探测失败）——自洽台不得因取不到字节而放行"
    print(f"NOTE[自洽台] {p.name}: 提交绑定面不适用（{surface}），本轮只判工作树面")
    return None


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    # --check=只判定（pre-commit 正门用）；--auto-fix=先跑各台的 fix 命令再复判定
    # （post-commit reconciler 的 D5_static_manifest 通道用，reconciler._fix_yaml_append
    #  一直按这个契约传旗，本脚本此前"忽略其他参数"＝映射到空操作，故漂移能带病两天）。
    # --heal-derived-totals=只刷派生标量（各 selfcheck 台的 fix 命令即此模式；先于判定循环
    #  处理并退出，故 --auto-fix 经子进程调它不会自递归）。
    if "--heal-derived-totals" in sys.argv and "--auto-fix" not in sys.argv and "--check" not in sys.argv:
        notes = heal_derived_totals()
        for n in notes:
            print(n)
        bad = [n for n in notes if n.startswith(("SKIP", "FAIL", "NOOP")) and "一致" not in n]
        print(f"\nheal-derived-totals: {len(notes)} 台，未刷正 {len(bad)} 台")
        sys.exit(EXIT_PASS if not bad else EXIT_FINDINGS)
    auto_fix = "--auto-fix" in sys.argv
    failures = []
    for check in CHECKS:
        if auto_fix and check.get("fix"):
            fr = subprocess.run(
                check["fix"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=_SUBPROCESS_ENV,
                cwd=str(_REPO_ROOT),
            )
            tail = (fr.stdout + fr.stderr).strip().splitlines()
            print(f"AUTO-FIX [{check['name']}] rc={fr.returncode}: {(tail[-1] if tail else '')[:160]}")
        if "selfcheck" in check:
            drift = _run_selfcheck(check)
            if drift:
                failures.append(f"FAIL [{check['name']}]: {drift}")
            else:
                print(f"PASS [{check['name']}]")
            continue
        result = subprocess.run(
            check["cmd"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=_SUBPROCESS_ENV,
            cwd=str(_REPO_ROOT),
        )
        if result.returncode != 0:
            msg = (result.stdout + result.stderr).strip()
            failures.append(f"FAIL [{check['name']}]: {msg}")
        else:
            print(f"PASS [{check['name']}]: {result.stdout.strip()}")

    if not failures:
        print("\nGATE-21 PASS: all static manifests are consistent with their sources.")
        sys.exit(EXIT_PASS)

    print(f"\nGATE-21 FAIL: {len(failures)} static manifest(s) have drifted:\n")
    for f in failures:
        print(f"  - {f}")
    print("修复（本包补的通道）：python " + __file__.replace(chr(92), "/") + " --auto-fix")
    print("\nFix: 运行对应生成器（不带 --check）重新生成，例如：")
    print("  python scripts/governance/generators/generate_script_manifest.py")
    print("  python scripts/governance/generators/generate_gate_registry.py")
    print("  python scripts/governance/d5_architecture/syncers/sync_registry_from_blueprints.py --write")
    sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()
