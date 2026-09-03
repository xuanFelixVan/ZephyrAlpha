# [BLUEPRINT] MOD-GOV_DRIFT_WATCHDOG | docs/01_policies_and_standards/sop/industry_chain_data_audit_sop.md | §#ARCH-308 B1 工作区脏文件判读器
# [MODULE] scripts.governance.classify_workspace_wip
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.security.access_control.session_concurrency (SessionRegistry); stdlib (json/os/subprocess/argparse)
# [CONSUMERS] AI 会话启动/中途判读工作区（AGENTS.md RULE-WORKSPACE-WIP 铁律指定入口）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读判读（永不改 git 状态/文件内容）；分类优先级 active_wip > runtime_telemetry(C类) > derived_sync(B类) > auto_sync > 陈旧/新鲜二分；零会话归属的未分类项才进"需人工关注"；exit 0 恒 informational
# [MODIFY-GUARD] 分类优先级顺序与各类处置建议文案（AGENTS.md RULE-WORKSPACE-WIP 引用的行为契约）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] git 不可达→退出码 2 + 错误信息；单文件判读异常→归 manual_review 不中断
# [TESTS] tests/scripts/test_classify_workspace_wip.py
# [TTL] permanent
# M10豁免: 按需手动诊断工具（manual STARTUP），无 cron/定时触发——非 m10 检测对象，此处仅备注

"""
classify_workspace_wip.py — 工作区脏文件判读器（#ARCH-308 B1，2026-09-03）。

治本动机
--------
2026-09-03 实证：新 AI 会话见 git status 200+ 脏文件 → 无判读规则 → 误报"孤儿 WIP"
→ 诱发危险清理冲动。根因是四类性质完全不同的脏文件在肉眼看来一模一样：

  1. 活跃会话的在途施工（合法 WIP，动了=踩他人工作）
  2. 后台派生缓存再生（非 WIP，watchdog 自动收敛/随下次提交吸收）
  3. 运行时遥测追加（tracked 存量债，CAND-GATEMECH-009）
  4. 死会话遗留的陈旧回退（真正的垃圾，但处置须走 lock+审计）

本工具一条命令输出四分类报告+每类处置建议，是 AGENTS.md RULE-WORKSPACE-WIP
铁律的指定入口——AI 见工作区脏 MUST 先跑本工具，禁止肉眼猜测后报警。

Usage::

    python scripts/governance/classify_workspace_wip.py            # 人类可读报告
    python scripts/governance/classify_workspace_wip.py --json     # 机读 JSON
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

__manifest__ = """
args: []
description: >
  工作区脏文件判读器（#ARCH-308 B1）——git status 脏文件四分类
  （活跃WIP/派生同步/运行时遥测/待人工判读）+每类处置建议。
  AGENTS.md RULE-WORKSPACE-WIP 铁律指定入口：AI 见工作区脏 MUST 先跑本工具，
  禁止肉眼猜测"孤儿WIP"后报警或擅动。
dimensions:
- D1
- D5
priority: P1
timeout_seconds: 30
warn_only: true
"""

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

_ALLOWLIST_REL = "docs/01_policies_and_standards/_registry/catalogs/gate_tracked_write_allowlist.yaml"
_GIT_TIMEOUT = 15

# 分类常量（顺序即判读优先级）
CAT_ACTIVE_WIP = "active_wip"          # 活跃会话 claim 的在途施工
CAT_RUNTIME_TELEMETRY = "runtime_telemetry"  # C 类运行时遥测（存量债）
CAT_DERIVED_SYNC = "derived_sync"      # B 类派生缓存再生（非孤儿 WIP）
CAT_AUTO_SYNC = "auto_sync"            # workspace_hygiene post-commit 还原对象
CAT_STALE_ROLLBACK = "stale_rollback"  # 疑似死会话陈旧回退（mtime < HEAD 时间）
CAT_FRESH_CHANGE = "fresh_change"      # 新鲜写入（mtime >= HEAD 时间）
CAT_UNTRACKED = "untracked_new"        # 未跟踪新文件

_RECOMMENDATIONS: dict[str, str] = {
    CAT_ACTIVE_WIP: "在途施工（活跃会话 claim）——勿动勿报，等该会话自己提交/释放",
    CAT_RUNTIME_TELEMETRY: "运行时遥测 tracked 存量债（CAND-GATEMECH-009）——应 untrack+gitignore，非 WIP 噪音",
    CAT_DERIVED_SYNC: "后台派生缓存再生，非孤儿 WIP——watchdog 自动收敛（#ARCH-308 A2）/随下次提交吸收；禁报警禁擅动",
    CAT_AUTO_SYNC: "auto-sync 产物（GATE-WORKSPACE-HYGIENE post-commit 还原对象）——非 WIP 噪音，勿动",
    CAT_STALE_ROLLBACK: "疑似死会话陈旧回退——watchdog 死会话清扫（#ARCH-308 A1）自动卸载 staged；人工处置须 lock+审计，禁裸 git checkout --",
    CAT_FRESH_CHANGE: "新鲜写入——确认写入方归属（本会话→claim+commit；不明→报 Owner 判读）",
    CAT_UNTRACKED: "新文件——判读归属：施工产物 claim+commit；运行时产物 gitignore 登记",
}


def _git(root: Path, args: list[str]) -> tuple[int, str]:
    """只读 git 命令（fail-open：失败返回 (rc, '')）。"""
    try:
        r = subprocess.run(  # noqa: S603 — 只读 git 白名单参数，无用户输入拼接
            ["git", *args],
            capture_output=True,
            text=True,
            cwd=str(root),
            timeout=_GIT_TIMEOUT,
        )
        return r.returncode, r.stdout or ""
    except (subprocess.TimeoutExpired, OSError):
        return 2, ""


def _porcelain(root: Path) -> list[tuple[str, str, bool]]:
    """解析 porcelain：返回 [(path, XY, is_untracked)]。"""
    rc, out = _git(root, ["status", "--porcelain=v1"])
    if rc != 0:
        return []
    entries: list[tuple[str, str, bool]] = []
    for line in out.splitlines():
        if len(line) < 4:
            continue
        xy = line[:2]
        path = line[3:].rstrip("\r")
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        path = path.strip().strip('"').replace("\\", "/")
        entries.append((path, xy, xy == "??"))
    return entries


def _load_allowlist(root: Path, allowlist_path: Path | None = None) -> tuple[set[str], list[str], set[str], list[str]]:
    """加载白名单，返回 (B类exact, B类patterns, C类exact, C类patterns)。"""
    path = allowlist_path or (root / _ALLOWLIST_REL)
    b_exact: set[str] = set()
    b_pats: list[str] = []
    c_exact: set[str] = set()
    c_pats: list[str] = []
    try:
        import yaml  # noqa: PLC0415

        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for entry in data.get("entries", []) or []:
            cls = str(entry.get("class", "")).strip().upper()
            if cls not in ("B", "C"):
                continue
            if entry.get("path"):
                target = b_exact if cls == "B" else c_exact
                target.add(str(entry["path"]).replace("\\", "/"))
            elif entry.get("pattern"):
                (b_pats if cls == "B" else c_pats).append(str(entry["pattern"]))
        return b_exact, b_pats, c_exact, c_pats
    except Exception:  # noqa: BLE001 — 白名单不可读=分类降级为无白名单（fail-open 只读工具）
        return set(), [], set(), []


def _match(rel: str, exact: set[str], patterns: list[str]) -> bool:
    import fnmatch  # noqa: PLC0415

    return rel in exact or any(fnmatch.fnmatch(rel, p) for p in patterns)


def _active_sessions_and_claims(root: Path) -> tuple[list[str], dict[str, str]]:
    """活跃会话 + claim 归属（与 drift watchdog 同口径的轻量复刻）。"""
    sessions: list[str] = []
    try:
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        sessions = [s.session_id for s in SessionRegistry(root).list_active()]
    except Exception:  # noqa: BLE001 — registry 故障降级空清单（只读工具不阻断）
        pass
    claimed: dict[str, str] = {}
    snap_dir = root / ".runtime" / "claim_snapshots"
    if snap_dir.is_dir():
        active = set(sessions)
        for snap in snap_dir.glob("*.json"):
            sid = snap.stem
            if sid.endswith("_adopted") or sid not in active:
                continue
            try:
                data = json.loads(snap.read_text(encoding="utf-8"))
                files = data.get("files")
                if files is None:
                    files = [
                        os.path.relpath(str(k), str(root)).replace(os.sep, "/")
                        for k in data.get("snapshots", {})
                    ]
                for f in files:
                    claimed[str(f).replace("\\", "/")] = sid
            except Exception:  # noqa: BLE001 — 单快照损坏跳过
                continue
    return sessions, claimed


def _auto_sync_matcher():
    """workspace_hygiene auto-sync 产物判定（重模块懒加载，失败降级 None）。"""
    try:
        from zephyr.governance.audit.workspace_hygiene_reconciler import _is_auto_sync_product

        return _is_auto_sync_product
    except Exception:  # noqa: BLE001 — 重模块导入失败降级跳过该分类（fail-open 只读工具）
        return None


def classify(root: Path, allowlist_path: Path | None = None) -> dict:
    """主判读：返回 {categories: {cat: [entries]}, sessions, head, ...}。

    entry 结构：{path, staged, note}——staged=True 表示 index 有暂存内容
    （#ARCH-308 A1 死会话清扫的 unstage 对象提示）。
    """
    root = root.resolve()
    rc, head_sha = _git(root, ["rev-parse", "HEAD"])
    if rc != 0:
        raise RuntimeError("git 不可达（非 git 仓库？）")
    rc, out = _git(root, ["log", "-1", "--format=%ct"])
    head_ts = float(out.strip()) if rc == 0 and out.strip() else 0.0

    sessions, claimed = _active_sessions_and_claims(root)
    b_exact, b_pats, c_exact, c_pats = _load_allowlist(root, allowlist_path)
    auto_sync = _auto_sync_matcher()

    categories: dict[str, list[dict]] = {c: [] for c in _RECOMMENDATIONS}
    for path, xy, is_untracked in _porcelain(root):
        staged = xy[0] not in (" ", "?")
        try:
            if is_untracked:
                categories[CAT_UNTRACKED].append({"path": path, "staged": False, "note": ""})
                continue
            if path in claimed:
                categories[CAT_ACTIVE_WIP].append(
                    {"path": path, "staged": staged, "note": f"claim={claimed[path]}"}
                )
            elif _match(path, c_exact, c_pats):
                categories[CAT_RUNTIME_TELEMETRY].append({"path": path, "staged": staged, "note": "C类白名单"})
            elif _match(path, b_exact, b_pats):
                categories[CAT_DERIVED_SYNC].append({"path": path, "staged": staged, "note": "B类白名单"})
            elif auto_sync is not None and auto_sync(path):
                categories[CAT_AUTO_SYNC].append({"path": path, "staged": staged, "note": "auto-sync清单"})
            else:
                mtime = os.path.getmtime(root / path)
                if head_ts and mtime < head_ts:
                    categories[CAT_STALE_ROLLBACK].append({"path": path, "staged": staged, "note": "mtime<HEAD"})
                else:
                    categories[CAT_FRESH_CHANGE].append({"path": path, "staged": staged, "note": "mtime>=HEAD"})
        except Exception:  # noqa: BLE001 — 单文件异常归人工判读
            categories[CAT_FRESH_CHANGE].append({"path": path, "staged": staged, "note": "判读异常"})

    total = sum(len(v) for v in categories.values())
    needs_attention = (
        len(categories[CAT_STALE_ROLLBACK])
        + len(categories[CAT_FRESH_CHANGE])
        + len(categories[CAT_UNTRACKED])
    )
    orphan_wip = 0 if needs_attention == 0 else needs_attention
    return {
        "head": head_sha.strip()[:8],
        "active_sessions": sessions,
        "total_dirty": total,
        "categories": categories,
        "needs_attention": needs_attention,
        "orphan_wip_estimate": orphan_wip,
        "conclusion": (
            f"孤儿WIP=0（全部可归因）；需人工关注 {needs_attention} 件"
            if needs_attention == 0
            else f"待归因 {needs_attention} 件（陈旧回退/新修改/新文件）——只有这三类才值得汇报"
        ),
    }


def _render_human(result: dict, display_cap: int = 20) -> None:
    print("== 工作区脏文件判读报告（classify_workspace_wip，#ARCH-308 B1）==")
    print(
        f"基线: HEAD {result['head']} | 活跃会话: {len(result['active_sessions'])}"
        f"（{', '.join(result['active_sessions']) or '无'}） | 脏文件: {result['total_dirty']}"
    )
    for cat, entries in result["categories"].items():
        if not entries:
            continue
        print(f"\n[{cat}] {len(entries)} 件 —— {_RECOMMENDATIONS[cat]}")
        for e in entries[:display_cap]:
            flag = "（staged）" if e["staged"] else ""
            note = f"  [{e['note']}]" if e["note"] else ""
            print(f"  - {e['path']}{flag}{note}")
        if len(entries) > display_cap:
            print(f"  ... 其余 {len(entries) - display_cap} 件省略")
    print(f"\n结论: {result['conclusion']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="工作区脏文件判读器（#ARCH-308 B1）")
    parser.add_argument("--root", default=".", help="仓库根（默认 cwd）")
    parser.add_argument("--allowlist", default=None, help="白名单路径覆盖（测试用）")
    parser.add_argument("--json", action="store_true", dest="as_json", help="机读 JSON 输出")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    allowlist = Path(args.allowlist).resolve() if args.allowlist else None
    try:
        result = classify(root, allowlist)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _render_human(result)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
