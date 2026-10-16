#!/usr/bin/env python
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md | §stash_drift
# [MODULE] scripts.ops.stash_sentinel
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.io.audit_jsonl_writer (append_audit_jsonl 同款机制: 迁移/告警台账统一写面);
#                zephyr.shared.utils.time_utils (now_utc, RULE-SCHEMA-TZ: 禁 datetime.now()/time.time() 生成时间戳)
# [CONSUMERS] process_reaper 既有扫描循环 wire（subprocess --once, 禁 cron/新常驻）; 人工手动触发
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] absorbed 判定=内容级对象比对（正像全集+集合差：stash 侧树枚举 blob 集 ⊆
#              归宿集(HEAD∪refs/quarantine/* 全枚举)——**禁条数估，也禁负向排除**：
#              `rev-list --objects S ^HEAD` 的负向传播在边界提交处截断树遍历，实测会把
#              HEAD 同 blob 误报为独有（2026-10-16 真仓复现），故归宿侧必须正像全枚举
#              （每轮一次缓存）；stash 侧枚举覆盖工作树/index/untracked 三父之树+基树
#              （fail-closed：基树 blob 在 HEAD 改写后可能仅由 stash 保活）; drop 永不越过
#              quarantine ref 核验——update-ref 后必须 rev-parse 回读同 sha、且 stash@{N} 复读
#              同 sha，任一不符=零 drop（fail-closed）+ 已建 ref 回滚删除; 只迁移 absorbed
#              且龄>min_age_days（出厂 30）的 stash，非 absorbed 超龄只写告警件零动作;
#              迁移=纯 ref 操作内容零丢失（同 sha 双侧互推），台账 .runtime/audit/stash_sentinel.jsonl
#              含双侧 sha; 按索引降序处置+逐枚 drop 前复读防并发位移;
#              enabled:false=全零动作（只报扫描数）; 单枚失败不反噬整轮（errors 行内继续）
# [MODIFY-GUARD] config/flags.yaml flags.stash_sentinel（阈值/开关真源，本件只读禁改）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] run_once 永不抛（git 失败/解析失败收入 errors，单枚跳过继续）;
#                  exit 0=完成（含零迁移/禁用）; exit 1=存在超龄非 absorbed 告警; exit 2=设施故障
#                  （stash list 不可用）
# [TESTS] tests/scripts/test_stash_sentinel.py（假 stash 仓实测 absorbed 两态/迁移/fail-closed/降序/禁用/dry-run）
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: one-shot 由 reaper 既有扫描循环/人工事件驱动（与 runtime_hygiene wire 同宿），
#                         非 cron/Timer/raw sleep-loop，本件零等待零轮询
# noqa: m11-perm-manual-legitimate  M11豁免: one-shot CLI 由 reaper wire/人工按需触发，非常驻服务/非 daemon/非自启
#
# create-guard-not-dup: 本模块只做 git ref 面机械操作与对象分类，不解析任何业务文件内容结构——
#                       与 scripts/governance/cleanup_stash.py（按条数保留最新的盲清理）语义不同层：
#                       本件 absorbed 内容判定+quarantine 保底，非其第二实现
"""stash_sentinel — absorbed stash 内容级判定 + quarantine ref 自动迁移（st-diskp0 裁定⑤升级版）。

病灶：git stash 是 reflog 面，30 天不清理即成" sixth 态"沉积（2026-10-16 实测 30 枚）；
盲目按条数 drop 会丢真内容（裁定⑤原版按条数保留最新 3 枚=赌徒语义）。
治本=只对**被 HEAD/quarantine 完全吸收**的陈旧 stash 做纯 ref 迁移：内容一个字节都不丢。

absorbed 判定（内容级，禁条数估，也禁负向排除）：
    归宿集（每轮一次缓存）= `git rev-list --objects HEAD refs/quarantine/*` 全枚举对象 id；
    stash 侧（逐枚）= 对 stash 提交及其基/index/untracked 各父之树跑
        `git rev-list --objects <T_S> <T_P1> <T_P2> <T_P3>`（树参数只走树不走提交史），
    经 `git cat-file --batch-check` 分类出 blob 集；
    **absorbed ⟺ stash 侧 blob 集 ⊆ 归宿集**（sha 即内容身份，集合差即可，归宿侧无需分类）。
    为何禁负向排除：`git rev-list --objects S ^HEAD` 的负向标记在边界提交处截断树遍历，
    实测会把 HEAD 已含的同 blob 误报为独有（假"非 absorbed"= 宁告不迁，方向保守但永无迁移，
    2026-10-16 真仓复现）——归宿侧必须正像全枚举。

处置矩阵（age=stash 提交时间距今天数，单一来源 %ct）：
    absorbed  且 age>min_age_days → 迁移 refs/quarantine/stash/at{N}_<sha12>_<utc>（update-ref
                                      → rev-parse 回读核验同 sha → stash@{N} 复读同 sha →
                                      git stash drop <N> → drop 后 ref 再核验），台账双侧 sha；
    非 absorbed 且 age>min_age_days → 只写 .runtime/workspace_alerts/stash_sentinel_<utc>.json
                                      + 台账告警行（零动作，处置=Owner 门位）；
    其余（未超龄）→ 只计数零动作。

fail-closed 三闸（任一不过=该枚零 drop）：
    ① 目标 quarantine ref 已存在 → 跳过；
    ② update-ref 后回读 ≠ stash sha → 回滚删 ref，零 drop；
    ③ drop 前 stash@{N} 复读 ≠ 原 sha（并发位移）→ 保 ref 零 drop（内容已被 ref 保活）。

部署：reaper wire（subprocess `--once`，dry_run 轮透传 `--dry-run`）或人工即时
    `python scripts/ops/stash_sentinel.py --once [--dry-run]`；禁 cron/新常驻。

配置：config/flags.yaml flags.stash_sentinel（enabled 出厂 ON，min_age_days=30）；
    缺配置=出厂 (True, 30)（fail-closed：缺配置不豁免迁移闸）。

# [ALGO_FLOW] external: docs/03_modules/_domain_infrastructure_operations/algo_flow/stash_sentinel.yaml
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from zephyr.shared.io.audit_jsonl_writer import append_audit_jsonl  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

AUDIT_DIR_REL = Path(".runtime") / "audit"
ALERT_DIR_REL = Path(".runtime") / "workspace_alerts"
LEDGER_FILENAME = "stash_sentinel.jsonl"
QREF_DIR = "refs/quarantine/stash"
GIT_TIMEOUT_S = 60
_DAY_SECONDS = 86400.0
_FIELD_SEP = "\x1f"


def read_stash_sentinel_config(repo_root: Path | str | None = None) -> tuple[bool, float]:
    """flags.stash_sentinel 配置读取唯一点（(enabled, min_age_days)；缺配置=出厂 (True, 30)）。

    单一真源=config/flags.yaml flags.stash_sentinel.*；缺席/类型异常键逐项回出厂
    （非 dict 守卫，整节坏不连坐 enabled）；禁复制字面量到消费方。
    """
    root = Path(repo_root) if repo_root else _REPO_ROOT
    defaults = (True, 30.0)
    try:
        import yaml

        flags = (yaml.safe_load((root / "config" / "flags.yaml").read_text(encoding="utf-8")) or {}).get("flags")
        section = flags.get("stash_sentinel") if isinstance(flags, dict) else None
        if not isinstance(section, dict):
            return defaults
        enabled = section.get("enabled")
        age_raw = section.get("min_age_days")
        return (
            defaults[0] if enabled is None else bool(enabled),
            defaults[1] if age_raw is None else float(age_raw),
        )
    except Exception:  # noqa: BLE001 — 配置设施异常回出厂值（fail-closed：缺配置不豁免迁移闸）
        return defaults


def _git(repo_root: Path, args: list[str], *, timeout: int = GIT_TIMEOUT_S, input_text: str | None = None):
    """git 子命令运行器（-c core.quotepath=false；永不抛，(rc, stdout, stderr)）。"""
    try:
        proc = subprocess.run(  # noqa: bare-subprocess  轻量 git 子命令调用（只读判定+ref 操作），CLI 工具单发无窗口敏感面
            ["git", "-c", "core.quotepath=false", *args],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            input=input_text,
        )
        return proc.returncode, proc.stdout or "", proc.stderr or ""
    except (OSError, subprocess.TimeoutExpired) as e:
        return 127, "", str(e)


def list_stashes(repo_root: Path) -> tuple[list[dict], str | None]:
    """枚举 git stash → [{index:int, sha:str, ts:int}]（%ct 提交时间即 stash 创建时刻；失败=([], err)）。"""
    rc, out, err = _git(repo_root, ["stash", "list", f"--format=%H{_FIELD_SEP}%ct{_FIELD_SEP}%gd"])
    if rc != 0:
        return [], f"git_stash_list_failed: {err.strip()[:200]}"
    stashes: list[dict] = []
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split(_FIELD_SEP)
        if len(parts) != 3:
            return [], f"stash_list_unparsable: {line[:120]}"
        sha, ts_raw, selector = parts
        try:
            ts = int(ts_raw)
        except ValueError:
            return [], f"stash_ts_unparsable: {line[:120]}"
        idx = selector.rfind("{")
        try:
            index = int(selector[idx + 1 : selector.rstrip().rfind("}")])
        except (ValueError, IndexError):
            return [], f"stash_index_unparsable: {selector[:60]}"
        stashes.append({"index": index, "sha": sha.strip(), "ts": ts})
    return stashes, None


def quarantine_refs(repo_root: Path) -> list[str]:
    """现役 refs/quarantine/* 全列（归宿集一侧；失败=[]→rev-list 少一支排除位只会更保守）。"""
    rc, out, _ = _git(repo_root, ["for-each-ref", "--format=%(refname)", "refs/quarantine"])
    if rc != 0:
        return []
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def classify_objects(repo_root: Path, object_ids: list[str]) -> tuple[dict[str, str], str | None]:
    """git cat-file --batch-check 批量分类（{sha: type}；missing/失败=err 行内上报，不猜测）。"""
    if not object_ids:
        return {}, None
    rc, out, err = _git(
        repo_root,
        ["cat-file", "--batch-check=%(objectname) %(objecttype)"],
        input_text="\n".join(object_ids) + "\n",
    )
    if rc != 0:
        return {}, f"cat_file_batch_failed: {err.strip()[:200]}"
    types: dict[str, str] = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1] != "missing":
            types[parts[0]] = parts[1]
    if len(types) != len(set(object_ids)):
        return types, "cat_file_incomplete: 部分对象分类缺失（按未吸收保守处理）"
    return types, None


def reachable_blob_ids(repo_root: Path, tips: list[str]) -> tuple[set[str], str | None]:
    """归宿集全枚举（正像，每轮一次缓存）：tips=HEAD+refs/quarantine/* → 全对象 id 集。

    只取 id 集做成员判定（sha 即内容身份，blob 与 tree/commit 的 sha 空间不相交，
    归宿侧无需分类）；负向排除不可靠（见模块 docstring），必须正像全枚举。
    """
    if not tips:
        return set(), None
    rc, out, err = _git(repo_root, ["rev-list", "--objects", *tips])
    if rc != 0:
        return set(), f"rev_list_homes_failed: {err.strip()[:200]}"
    return {ln.split(" ", 1)[0].strip() for ln in out.splitlines() if ln.strip()}, None


def stash_tree_blob_ids(repo_root: Path, stash_sha: str) -> tuple[list[str], list[str], dict[str, str], str | None]:
    """stash 侧 blob 集（覆盖工作树/基树/index 树/untracked 树；树参数只走树不走提交史）。

    返回 (blob_ids, all_ids, path_of, err)；path_of=oid→路径映射（告警件路径样本用）；
    cat-file batch-check 分类（工作树快照面，小集合，一次调用）。
    """
    rc, out, err = _git(repo_root, ["rev-list", "--parents", "-n1", stash_sha])
    if rc != 0:
        return [], [], {}, f"rev_list_parents_failed: {err.strip()[:200]}"
    family = out.split()
    trees: list[str] = []
    for member in family:  # stash 本体+基/index/untracked 各父（存在才取树）
        rc_t, out_t, err_t = _git(repo_root, ["show", "-s", "--format=%T", member])
        if rc_t != 0:
            return [], [], {}, f"tree_resolve_failed({member[:12]}): {err_t.strip()[:200]}"
        if out_t.strip():
            trees.append(out_t.strip())
    rc, out, err = _git(repo_root, ["rev-list", "--objects", *trees])
    if rc != 0:
        return [], [], {}, f"rev_list_trees_failed: {err.strip()[:200]}"
    all_ids: list[str] = []
    path_of: dict[str, str] = {}
    for ln in out.splitlines():
        parts = ln.split(" ", 1)
        oid = parts[0].strip()
        if not oid:
            continue
        all_ids.append(oid)
        if len(parts) == 2 and parts[1].strip():
            path_of[oid] = parts[1].strip()
    types, cls_err = classify_objects(repo_root, all_ids)
    if cls_err:
        return [], all_ids, path_of, cls_err
    blobs = [oid for oid in all_ids if types.get(oid) == "blob"]
    return blobs, all_ids, path_of, None


def _rev_parse(repo_root: Path, ref: str) -> str | None:
    """rev-parse --verify 静默取 sha（失败/不存在=None）。"""
    rc, out, _ = _git(repo_root, ["rev-parse", "--verify", "--quiet", ref])
    return out.strip() if rc == 0 and out.strip() else None


def write_overage_alert(alert_dir: Path, items: list[dict], *, dry_run: bool = False) -> str | None:
    """超龄非 absorbed 聚合告警件（一轮一件防刷屏；severity=escalated 只升 Owner 零处置）。"""
    if dry_run or not items:
        return None
    stamp = now_utc().strftime("%Y%m%dT%H%M%SZ")
    record = {
        "ts": now_utc().isoformat(),
        "by": "scripts.ops.stash_sentinel",
        "event": "stash_overage_not_absorbed",
        "severity": "escalated",
        "items": items,
        "note": "超龄 stash 含 HEAD/quarantine 之外的独有内容——零自动处置；"
        "逐枚核实归属后人工决定 apply/移植/quarantine（stash_shas 可复核）",
        "recover": "git stash show -p stash@{N} 逐枚核对；确认可弃后 git stash drop <N>",
    }
    try:
        alert_dir = Path(alert_dir)
        alert_dir.mkdir(parents=True, exist_ok=True)
        path = alert_dir / f"stash_sentinel_{stamp}.json"
        path.write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
        return str(path)
    except OSError:
        return None


def migrate_absorbed(repo_root: Path, *, index: int, sha: str, dry_run: bool) -> dict:
    """单枚 absorbed stash 迁移（纯 ref 操作，fail-closed 三闸，返回动作报告零抛）。

    闸序：ref 已存在→跳过｜dry-run→只报｜update-ref→回读核验（败=回滚删 ref 零 drop）
    ｜stash@{N} 复读（败=保 ref 零 drop，内容已被 ref 保活）｜drop→drop 后 ref 终核验。
    """
    stamp = now_utc().strftime("%Y%m%dT%H%M%SZ")
    qref = f"{QREF_DIR}/at{index}_{sha[:12]}_{stamp}"
    out: dict = {"index": index, "stash_sha": sha, "qref": qref, "action": "migrated", "dropped": False}
    if _rev_parse(repo_root, qref) is not None:
        out["action"] = "skipped_ref_exists"
        return out
    if dry_run:
        out["action"] = "would_migrate"
        out["dry_run"] = True
        return out
    rc, _, err = _git(repo_root, ["update-ref", qref, sha])
    if rc != 0:
        out["action"] = "failed_update_ref"
        out["error"] = err.strip()[:200]
        return out
    got = _rev_parse(repo_root, qref)
    if got != sha:
        _git(repo_root, ["update-ref", "-d", qref])  # 回滚自建 ref（零遗留），drop 永不执行
        out["action"] = "failed_ref_verify"
        out["error"] = f"ref 回读 {got} != stash {sha}（ref 已回滚删除，零 drop）"
        return out
    current = _rev_parse(repo_root, f"stash@{{{index}}}")
    if current != sha:
        out["action"] = "failed_index_shifted"
        out["error"] = f"stash@{{{index}}} 已位移为 {current}（quarantine ref 保留保活，零 drop）"
        return out
    rc, _, err = _git(repo_root, ["stash", "drop", f"stash@{{{index}}}"])
    if rc != 0:
        out["action"] = "failed_drop"
        out["error"] = err.strip()[:200]
        return out
    out["dropped"] = True
    got2 = _rev_parse(repo_root, qref)
    if got2 != sha:
        out["action"] = "post_drop_verify_failed"
        out["error"] = f"drop 后 ref 回读 {got2} != {sha}（内容仍被 ref 指面保活，需人工复核）"
    return out


def run_once(
    *,
    repo_root: Path | str | None = None,
    dry_run: bool = False,
    min_age_days: float | None = None,
    audit_dir: Path | None = None,
    alert_dir: Path | None = None,
    note: str | None = None,
) -> tuple[dict, list[str]]:
    """一轮 stash 哨兵（默认入口）：枚举→absorbed 判定→按处置矩阵行动。永不抛。

    Returns:
        (summary, errors)；summary={action, enabled, min_age_days, scanned, young,
        migrated, alerted, errors, dry_run, alert_file}。
    """
    root = Path(repo_root) if repo_root else _REPO_ROOT
    audits = Path(audit_dir) if audit_dir else root / AUDIT_DIR_REL
    alerts = Path(alert_dir) if alert_dir else root / ALERT_DIR_REL
    errors: list[str] = []
    enabled, cfg_age = read_stash_sentinel_config(root)
    age_gate = float(min_age_days) if min_age_days is not None else cfg_age
    summary: dict = {
        "action": "patrolled",
        "enabled": enabled,
        "min_age_days": age_gate,
        "scanned": 0,
        "young": 0,
        "migrated": 0,
        "alerted": 0,
        "errors": errors,
        "dry_run": bool(dry_run),
        "alert_file": None,
    }
    if note:
        summary["note"] = note
    stashes, err = list_stashes(root)
    if err:
        summary["action"] = "error"
        errors.append(err)
        return summary, errors
    summary["scanned"] = len(stashes)
    if not enabled:
        summary["action"] = "disabled"
        return summary, errors
    homes, herr = reachable_blob_ids(root, ["HEAD", *quarantine_refs(root)])
    if herr:
        summary["action"] = "error"
        errors.append(herr)
        return summary, errors
    overage_items: list[dict] = []
    now_ts = now_utc().timestamp()
    for stash in sorted(stashes, key=lambda s: s["index"], reverse=True):
        index, sha, ts = stash["index"], stash["sha"], stash["ts"]
        age_days = max(0.0, (now_ts - ts) / _DAY_SECONDS)
        if age_days <= age_gate:
            summary["young"] += 1
            continue
        blobs, all_ids, path_of, uerr = stash_tree_blob_ids(root, sha)
        if uerr:
            errors.append(f"stash@{{{index}}} {sha[:12]} 判定失败（保守零动作）: {uerr}")
            continue
        missing = [oid for oid in blobs if oid not in homes]
        row = {
            "ts": now_utc().isoformat(),
            "by": "scripts.ops.stash_sentinel",
            "stash_index": index,
            "stash_sha": sha,
            "age_days": round(age_days, 2),
            "unique_blobs": len(missing),
            "unique_trees_commits": len(all_ids) - len(blobs),
        }
        if not missing:
            mig = migrate_absorbed(root, index=index, sha=sha, dry_run=dry_run)
            row["action"] = mig["action"]
            row["quarantine_ref"] = mig["qref"]
            row["quarantine_sha"] = _rev_parse(root, mig["qref"]) if not dry_run else None
            row["dropped"] = mig.get("dropped", False)
            if mig.get("error"):
                row["error"] = mig["error"]
                errors.append(f"stash@{{{index}}}: {mig['error']}")
            if mig["action"] == "migrated" and mig.get("dropped"):
                summary["migrated"] += 1
        else:
            row["action"] = "alert_not_absorbed" if not dry_run else "would_alert_not_absorbed"
            row["unique_blob_paths_sample"] = [f"{oid} {path_of.get(oid, '')}" for oid in missing[:10]]
            overage_items.append(row)
        if not dry_run:
            if not append_audit_jsonl(Path(audits), LEDGER_FILENAME, row):
                errors.append(f"stash@{{{index}}} 台账写失败（动作已执行，审计缺行需人工补记）")
    if overage_items:
        summary["alerted"] = len(overage_items)
        path = write_overage_alert(alerts, overage_items, dry_run=dry_run)
        summary["alert_file"] = path
        if path is None and not dry_run:
            errors.append("告警件写失败（台账行已留证）")
    return summary, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="absorbed stash 内容级判定 + quarantine ref 自动迁移（零内容丢失）")
    parser.add_argument("--once", action="store_true", help="单轮即时执行（reaper wire 调用形态）")
    parser.add_argument("--dry-run", action="store_true", help="只判零写（零 ref/零 drop/零台账/零告警）")
    parser.add_argument(
        "--min-age-days", type=float, default=None, help="覆盖 flags.stash_sentinel.min_age_days（单轮）"
    )
    parser.add_argument("--note", dest="note", default=None, help="本轮备注（写入台账行）")
    args = parser.parse_args(argv)
    summary, errors = run_once(dry_run=args.dry_run, min_age_days=args.min_age_days, note=args.note)
    prefix = "[STASH-SENTINEL] dry-run " if args.dry_run else "[STASH-SENTINEL] "
    print(
        f"{prefix}action={summary['action']} enabled={summary['enabled']} scanned={summary['scanned']} "
        f"young={summary['young']} migrated={summary['migrated']} alerted={summary['alerted']} "
        f"min_age_days={summary['min_age_days']}"
    )
    if summary.get("alert_file"):
        print(f"[STASH-SENTINEL] 超龄非 absorbed 告警件: {summary['alert_file']}")
    for e in errors:
        print(f"[STASH-SENTINEL] error: {e}", file=sys.stderr)
    if summary["action"] == "error":
        return 2
    return 1 if summary["alerted"] else 0


if __name__ == "__main__":
    sys.exit(main())
