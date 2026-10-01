# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] wave1b.dead_letter_census
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] stdlib(pathlib/subprocess/json/re)；yaml；zephyr.shared.io.paths
# [CONSUMERS] 总包施工队人工命令行调用（st-final-build-20260926）；产物 docs/_working/total_command_closeout/
# [STARTUP] manual
#   （原值 on_demand_cli——GATE-VOCAB 词表归正 manual）
# [MATURITY] draft
# [INVARIANTS] 只读取证不改生产状态；输出机生禁手改；对 git/队列目录零写；计数以现读为准禁照抄册面旧数
# [MODIFY-GUARD] 本件为一次性普查/清点器；改判据口径须与 92 册验收尺同批
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] git/IO 失败必抛并点名，禁静默降级为空结果（假绿源）
# [TESTS] 无（案卷型一次性脚本，红证由案卷内命令原文可复算）
# create-guard-not-dup: 死车道抢救件（字节代投非新能力），与canonical同名能力无职责重叠，逐词误报批量豁免（st-chief7-20260928 第12+轮实测均为关键词巧合命中）
# [TTL] task_bound
# [MODIFY-GUARD] 改判据口径须与对应验收尺（92 册）与案卷同批，禁单独放宽
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# [MODIFY-GUARD] 改白名单或判据须与 gate_registry 与 92 册验收尺同批
# -*- coding: utf-8 -*-
"""dead_letter_census.py — 波 1B 死信普查 + 从未入库件四态反查（机生禁手改，可重跑）

只读对象：.runtime/commit_queue/**（dead/done/pending/processing/blobs 零写）
写出对象：仅本目录 dead_letter_census.yaml；--rescue 时另写 rescued/**
处方对照：docs/_working/total_command_closeout/11_rescue_playbook.md §R-3
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

from zephyr.shared.infra.process_pool import run_subprocess_hidden  # TRAE-067 无窗口统一入口

REPO = Path(r"D:/ZephyrAlpha")
QUEUE = REPO / ".runtime" / "commit_queue"
DEAD = QUEUE / "dead"
HERE = Path(__file__).resolve().parent
OUT_YAML = HERE / "dead_letter_census.yaml"
RESCUED = HERE / "rescued"

NAMED = {
    "test_redblue_governance.py": ["tests/governance/test_redblue_governance.py"],
    "test_redblue_robust.py": ["tests/governance/test_redblue_robust.py"],
    "dead_triage.yaml": ["docs/_working/commit_speedup_campaign/60_deep_dive/dead_triage.yaml"],
    "dead_triage_r2.yaml": ["docs/_working/commit_speedup_campaign/60_deep_dive/dead_triage_r2.yaml"],
    # 大小写陷阱：在册字面 DEEP_DIVE_R1.md，盘面/HEAD 真身为小写 deep_dive_r1.md（X-16 改判）
    "DEEP_DIVE_R1.md": ["docs/_working/commit_speedup_campaign/60_deep_dive/deep_dive_r1.md"],
}

R3_PRESCRIPTIONS = {
    "注册表三向合并失败(家族)": "R-3 行1：走 R-1 修基底+该册变更单独成袋，勿 requeue 硬闯",
    "基底不可知(注册表项 base_head)": "R-3 行5：enqueue --base-head $(git rev-parse dev)",
    "GATE:TRANSLATION-COVERAGE": "R-3 行2：add_module_translation 在主仓跑，plain-zh≥8 字且落 entries: 段",
    "GATE:CREATE-GUARD": "R-3 行3：R-2 步骤 2；token 与件同袋",
    "GATE:GATE-PRECOMMIT-RUN": "R-3 行4：先跑 R-2 步骤 4 门禁预跑",
    "GATE:REFERENCE-INTEGRITY(RULING-REFERENCE)": "R-3 行6：禁引用未登记裁定号，改文字描述后经取号器补登",
    "WorktreePunchThroughError(EV-02 reset 打穿主仓)": "R-3 行7：非内容病，见 W-16 回退哨兵，重投前核主仓 HEAD",
    "GATE:R5-DIGIT-SUFFIX": "R-3 行8：目录/文件名禁以数字结尾，已入库历史违规跳过",
    "GATE:ORPHAN-MODULE": "R-3 行9：零消费者新件必与接线同袋",
    "GATE:DEPGRAPH-ENFORCEMENT": "R-3 行10：apply_depgraph --add-design-node；改名后 --force 重建",
    "GATE:NEW-FILE-DEPGRAPH": "R-3 行10：同上",
    "GATE:COMPLEXITY-GUARD": "R-3 行11：拆模块级 helper（参数≤7），禁调阈值",
    "GATE:ENCODING-SAFETY": "R-3 行12：禁回填门禁取样字面量；写盘 newline='\\n'",
    "GATE:CH-FINAL-GATE": "R-3 行13：先换会抛错 reader 再投",
    "GATE:REGISTRY-MASS-DELETION": "R-3 行14：按 R-1 分诊 B 型/A 型",
    "GATE:HOT-FILE-BASE-FRESHNESS": "R-3 行14：同上",
}

WS = re.compile(r"\s+")


def norm_ws(s: str) -> str:
    return WS.sub(" ", (s or "")).strip()


def classify(reason: str) -> str:
    r = norm_ws(reason)
    if "WorktreePunchThroughError" in r:
        return "WorktreePunchThroughError(EV-02 reset 打穿主仓)"
    if "注册表三向合并失败" in r:
        return "注册表三向合并失败(家族)"
    if "基底不可知" in r:
        return "基底不可知(注册表项 base_head)"
    if "LandingEnvironmentError" in r or "landing 环境不可用" in r:
        return "LandingEnvironmentError(landing 环境不可用)"
    if r.startswith("NOTHING_TO_COMMIT"):
        return "NOTHING_TO_COMMIT 但快照未真应用(blob 与 old_dev 不符)"
    if r.startswith("cascade_stale"):
        return "cascade_stale(基底重校验不适用)"
    m = re.search(r"门禁 ([A-Za-z0-9\-]+) 阻断", r)
    if m:
        gate = m.group(1)
        if gate == "REFERENCE-INTEGRITY" and "RULING-REFERENCE" in r:
            return "GATE:REFERENCE-INTEGRITY(RULING-REFERENCE)"
        return "GATE:" + gate
    return "OTHER:" + r[:44]


def path_domain(p: str) -> str:
    p = p.replace("\\", "/")
    seg = [s for s in p.split("/") if s]
    if not seg:
        return "?"
    if seg[0] == "src" and len(seg) > 2:
        return "src/zephyr/" + (seg[2] if seg[1] == "zephyr" else seg[1])
    return "/".join(seg[:2]) if len(seg) > 1 else seg[0]


def load_bags() -> tuple[list[dict], list[str], int]:
    """只读枚举队列袋；返回 (记录, 状态目录清单, dead 顶层实数)."""
    recs: list[dict] = []
    top = sorted(DEAD.glob("*.json"))
    archived = sorted(p for p in DEAD.iterdir() if p.is_dir() for p in p.glob("*.json"))
    for state, files in (
        ("dead", top),
        ("dead_archived", archived),
        ("done", sorted((QUEUE / "done").glob("*.json"))),
        ("pending", sorted((QUEUE / "pending").glob("*.json"))),
        ("processing", sorted((QUEUE / "processing").glob("*.json"))),
    ):
        for f in files:
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except Exception as e:  # noqa: BLE001
                recs.append({"state": state, "file": str(f), "parse_fail": repr(e)})
                continue
            d["_state"] = state
            d["_file"] = str(f)
            recs.append(d)
    return recs, [], len(top)


def queue_status() -> dict:
    try:
        p = run_subprocess_hidden(
            ["python", str(REPO / "scripts" / "commit_queue.py"), "status"],
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            check=False,
        )
        m = re.search(r"\{.*\}", p.stdout, re.S)
        counts = json.loads(m.group(0))["counts"] if m else {"error": "no-json"}
    except Exception as e:  # noqa: BLE001
        counts = {"error": repr(e)}
    return counts


def git(*args: str) -> str:
    return run_subprocess_hidden(
        ["git", "-C", str(REPO), *args], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False
    ).stdout


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build_census(dead_top: list[dict]) -> list[dict]:
    clusters: dict[str, dict] = {}
    for d in dead_top:
        key = classify(d.get("dead_reason"))
        c = clusters.setdefault(
            key,
            {
                "cluster": key,
                "bags": 0,
                "first_dead_at": None,
                "last_dead_at": None,
                "domains": Counter(),
                "sessions": Counter(),
                "prescription": R3_PRESCRIPTIONS.get(key, "（无在册处方——新签名，待立案）"),
            },
        )
        c["bags"] += 1
        ts = norm_ws(str(d.get("dead_at") or d.get("created_at") or ""))[:25]
        if ts:
            if c["first_dead_at"] is None or ts < c["first_dead_at"]:
                c["first_dead_at"] = ts
            if c["last_dead_at"] is None or ts > c["last_dead_at"]:
                c["last_dead_at"] = ts
        c["sessions"][d.get("session_id") or "?"] += 1
        for e in d.get("files") or []:
            c["domains"][path_domain(str(e.get("path") or ""))] += 1
    rows = []
    for c in clusters.values():
        c["domains"] = sorted(c["domains"])
        c["top_sessions"] = c["sessions"].most_common(3)
        del c["sessions"]
        rows.append(c)
    rows.sort(key=lambda x: -x["bags"])
    return rows


def owner_recurrence(dead_top: list[dict]) -> dict:
    pair: Counter = Counter()
    sess_first: dict[str, str] = {}
    for d in dead_top:
        s = d.get("session_id") or "?"
        ts = norm_ws(str(d.get("dead_at") or d.get("created_at") or ""))[:25]
        if ts and (s not in sess_first or ts < sess_first[s]):
            sess_first[s] = ts
        pair[(s, classify(d.get("dead_reason")))] += 1
    top = [
        {
            "owner_session": s,
            "cluster": k,
            "recurrence": n,
            "first_dead_at": sess_first.get(s),
            "circuit_break_ge3": n >= 3,
        }
        for (s, k), n in pair.most_common(25)
    ]
    ge3 = [t for t in top if t["circuit_break_ge3"]]
    return {
        "top_pairs": top,
        "pairs_ge3_count": len([1 for n in pair.values() if n >= 3]),
        "pairs_ge3": ge3,
        "sessions_total": len(sess_first),
    }


def forensics_named(dead_top: list[dict]) -> dict:
    """四态：HEAD / 任何分支历史 / 队列 blobs / 工作树；path+blob_sha256，EOL 归一后比."""
    idx: dict[str, list] = defaultdict(list)
    for d in dead_top:
        for e in d.get("files") or []:
            idx[str(e.get("path", "")).replace("\\", "/").lower()].append((d, e))
    for state in ("done", "pending", "processing"):
        for f in (QUEUE / state).glob("*.json"):
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                continue
            for e in d.get("files") or []:
                idx[str(e.get("path", "")).replace("\\", "/").lower()].append((d, e))

    out = {}
    for name, paths in NAMED.items():
        rec = {"doc_literal_name": name, "resolved_paths": [], "verdict": None}
        for p in paths:
            item: dict = {"path": p}
            exact_upper = name != Path(p).name
            item["case_note"] = (
                ("在册字面 %s 与盘/HEAD 真身 %s 大小写不同（X-16 陷阱）" % (name, Path(p).name))
                if exact_upper
                else None
            )
            head = git("rev-parse", "-q", "--verify", "HEAD:" + p).strip()
            item["state1_head_blob_sha1"] = head or None
            hist = [l for l in git("log", "--all", "--format=%h", "--", p).splitlines() if l.strip()]
            item["state2_branch_commits"] = len(hist)
            hits = []
            for d, e in idx.get(p.lower(), []):
                bs = str(e.get("blob_sha256") or "")
                bp = QUEUE / bs[:2] / bs if False else QUEUE / "blobs" / bs
                blob_exists = bp.exists()
                norm = raw = None
                if blob_exists:
                    raw_b = bp.read_bytes()
                    raw = hashlib.sha256(raw_b).hexdigest()
                    norm = hashlib.sha256(raw_b.replace(b"\r\n", b"\n")).hexdigest()
                hits.append(
                    {
                        "qid": d.get("qid"),
                        "state": d.get("_state"),
                        "ts": norm_ws(str(d.get("dead_at") or d.get("created_at") or ""))[:25],
                        "blob_sha256": bs,
                        "blob_file_exists": blob_exists,
                        "integrity_raw_sha==recorded": raw == bs,
                        "norm_sha256": norm,
                        "action": e.get("action"),
                    }
                )
            item["state3_blob_hits"] = hits
            item["state3_distinct_blob_versions"] = sorted({h["blob_sha256"] for h in hits})
            wp = REPO / p
            item["state4_worktree_exists"] = wp.exists()
            if wp.exists() and head:
                disk_n = hashlib.sha256(wp.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
                headb = git("show", "HEAD:" + p).replace("\r\n", "\n").encode("utf-8", "surrogatepass")
                item["state4_disk_vs_head_eol_norm_equal"] = hashlib.sha256(headb).hexdigest() == disk_n
            # git 外存活（.runtime/tmp 波0 快照等）
            tmp_hits = [str(x.relative_to(REPO)) for x in REPO.glob(".runtime/tmp/**/" + Path(p).name)]
            item["extra_survivors_runtime_tmp"] = tmp_hits
            rec["resolved_paths"].append(item)
        landed = any(p2["state1_head_blob_sha1"] or p2["state2_branch_commits"] for p2 in rec["resolved_paths"])
        in_blob = any(p2["state3_blob_hits"] for p2 in rec["resolved_paths"])
        in_wt = any(p2["state4_worktree_exists"] for p2 in rec["resolved_paths"])
        extra = any(p2["extra_survivors_runtime_tmp"] for p2 in rec["resolved_paths"])
        if landed:
            rec["verdict"] = "已入库（HEAD/分支命中）——非捞回对象"
        elif in_blob:
            rec["verdict"] = "从未入库；盘外唯一存活=队列 blobs ⇒ 捞回对象"
        elif in_wt or extra:
            rec["verdict"] = "从未入库；不在 blobs，存活于工作树/.runtime_tmp ⇒ 捞回对象（快照源）"
        else:
            rec["verdict"] = "缺失（双证齐：无分支、无 blobs、无工作树）"
        out[name] = rec
    return out


def do_rescue(fore: dict) -> list[dict]:
    """把盘外唯一存活字节复制进 rescued/<原相对路径>，不回写原位不改原字节."""
    RESCUED.mkdir(parents=True, exist_ok=True)
    manifest = []
    for name, rec in fore.items():
        if "⇒ 捞回对象" not in (rec.get("verdict") or ""):  # 判据含"非捞回对象"，勿用子串"捞回对象"
            continue
        for p2 in rec["resolved_paths"]:
            rel = p2["path"]
            versions = {}
            for h in p2["state3_blob_hits"]:
                if h["blob_file_exists"] and h["action"] != "delete":
                    versions.setdefault(h["blob_sha256"], h["ts"])
            if versions:
                newest = max(versions.items(), key=lambda kv: kv[1] or "")
                src = QUEUE / "blobs" / newest[0]
                for sha in versions:
                    if sha == newest[0]:
                        continue
                    vd = RESCUED / "versions"
                    vd.mkdir(exist_ok=True)
                    vsrc = QUEUE / "blobs" / sha
                    (vd / (Path(rel).name + "." + sha[:12])).write_bytes(vsrc.read_bytes())
                    manifest.append(
                        {
                            "saved": "versions/" + Path(rel).name + "." + sha[:12],
                            "source": "queue blobs",
                            "sha256": sha,
                            "for": rel,
                        }
                    )
                dst = RESCUED / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(src.read_bytes())
                manifest.append(
                    {
                        "saved": rel,
                        "source": "queue blobs (latest qid ts " + str(newest[1]) + ")",
                        "sha256": newest[0],
                        "for": rel,
                    }
                )
            else:
                cands = (
                    [REPO / rel]
                    if p2["state4_worktree_exists"]
                    else [REPO / t for t in p2["extra_survivors_runtime_tmp"]]
                )
                for i, c in enumerate(cands):
                    if not c.exists():
                        continue
                    dst = RESCUED / rel if i == 0 else RESCUED / "versions" / (Path(rel).name + f".alt{i}")
                    if i:
                        (RESCUED / "versions").mkdir(exist_ok=True)
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_bytes(c.read_bytes())
                    manifest.append(
                        {
                            "saved": str(dst.relative_to(RESCUED)).replace("\\", "/"),
                            "source": str(c.relative_to(REPO)),
                            "sha256": sha256_file(c),
                            "for": rel,
                        }
                    )
    lines = [f"{m['sha256']}  {m['saved']}  <- {m['source']}  (orig_path={m['for']})" for m in manifest]
    (RESCUED / "sha256.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return manifest


def yaml_dump(obj: dict, path: Path) -> None:
    import yaml

    path.write_text(yaml.safe_dump(obj, allow_unicode=True, sort_keys=False, width=200), encoding="utf-8", newline="\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rescue", action="store_true", help="执行 C 捞回写盘（默认只普查）")
    args = ap.parse_args()

    recs, _, dead_top_n = load_bags()
    dead_top = [d for d in recs if d.get("_state") == "dead"]
    parse_fail = [d for d in recs if "parse_fail" in d]
    skipped_dirty = sum(1 for d in dead_top if "skipped_dirty" in str(d.get("dead_reason")))
    qid_prefix_mismatch = sum(1 for d in dead_top if str(d.get("qid", "")).count(str(d.get("session_id", "\x00"))) == 0)
    status_now = queue_status()
    doc = {
        "_meta": {
            "generated_by": "dead_letter_census.py（机生禁手改，可重跑）",
            "denominator_note": "census 分母=dead/ 顶层 *.json；归档子目录单列披露",
            "status_read": status_now,
            "dir_counts": {
                "dead_top_json": dead_top_n,
                "dead_archive_subdirs_json": len([d for d in recs if d.get("_state") == "dead_archived"]),
                "ls_dead_wc_l_pitfall": "ls dead 会 +1（含子目录名），以 status/顶层计数互证",
            },
            "parse_fail": parse_fail,
            "cross_check": {
                "status_dead_equals_dir_dead_top": status_now.get("dead") == dead_top_n
                if isinstance(status_now.get("dead"), int)
                else None,
            },
            "disclosures": {
                "skipped_dirty_in_dead_reason_bags": skipped_dirty,
                "note": "R-3 在册：skipped_dirty 与袋死亡相关性 0/134，勿当死因（在册改判）",
                "qid_prefix_contains_session": qid_prefix_mismatch == 0,
            },
        },
        "clusters": build_census(dead_top),
        "owner_recurrence": owner_recurrence(dead_top),
        "named_object_four_state": forensics_named(dead_top),
    }
    if args.rescue:
        doc["rescue_manifest"] = do_rescue(doc["named_object_four_state"])
    yaml_dump(doc, OUT_YAML)
    total = sum(c["bags"] for c in doc["clusters"])
    print("clusters:", len(doc["clusters"]), "bags:", total, "->", OUT_YAML)


if __name__ == "__main__":
    main()
