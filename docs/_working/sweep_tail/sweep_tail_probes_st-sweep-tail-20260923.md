---
ttl: task_bound
title: 取证探针件附录·清扫班 st-sweep-tail-20260923（防 .runtime/tmp TTL 清理吃掉复核工具）
created: 2026-09-23
sid: st-sweep-tail-20260923
lane: sweep_tail
---

# 取证探针件附录

台账 `sweep_tail_ledger_st-sweep-tail-20260923.md` §3 复核命令所列脚本的字节级存档。
原落点 `.runtime/tmp/sweep_tail/` 受 TTL 清理，故随批入库；跑法：把对应代码块另存为 .py 后按台账命令执行。

## verify_bmbuy05_v2.py

```python
# [TTL] permanent
"""BM-BUY-05 复核 v2：只按"同 section 同 step_id"这一机械真键判，
并逐字段列出穷/富对照（含长度与是否字面包含），供 Owner/Max 复核"⊇"口径。
"""
import subprocess
from collections import Counter

import yaml

REPO = r"D:\ZephyrAlpha"
REG = "docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml"


def show(ref):
    r = subprocess.run(["git", "show", f"{ref}:{REG}"], cwd=REPO,
                       capture_output=True, text=True, encoding="utf-8")
    return r.stdout


def doc(text):
    return yaml.safe_load(text)


def sec_ids(entries, key="step_id"):
    c = Counter(e.get(key) for e in entries if isinstance(e, dict))
    return {k: v for k, v in c.items() if v > 1}


pre = doc(show("360468501e^"))
post = doc(show("HEAD"))

for name, d in (("术前 360468501e^", pre), ("术后 HEAD", post)):
    bms = d.get("battle_map_steps") or []
    dup = sec_ids(bms)
    print(f"[{name}] battle_map_steps 条数={len(bms)} 同段重复 step_id={dup}")

bms_pre = pre["battle_map_steps"]
pairs = [e for e in bms_pre if e.get("step_id") == "BM-BUY-05"]
pairs.sort(key=lambda e: sum(len(str(v)) for v in e.values()))
poor, rich = pairs


def bulk(e):
    return sum(len(str(v)) for v in e.values())


print(f"\n穷版 {bulk(poor)} 字符 / 富版 {bulk(rich)} 字符")
print(f"字段集 穷={sorted(poor)}\n字段集 富={sorted(rich)}")
print(f"字段集相等（无信息维度丢失）= {sorted(poor) == sorted(rich)}")
print("\n逐字段对照：")
for k in sorted(poor):
    pv, rv = str(poor[k]), str(rich[k])
    print(f"  - {k}: 穷 {len(pv)} → 富 {len(rv)} 字包含={pv.strip() in rv.strip()}")

print("\n===== 穷版全文（术前，已被摘除）=====")
print(yaml.safe_dump(poor, allow_unicode=True, sort_keys=False, width=200))
print("===== 富版 plain_zh/name_zh（术后幸存）=====")
print(f"name_zh: {rich['name_zh']}")
print(f"plain_zh: {rich['plain_zh']}")
```

## probe_dead_item.py

```python
# [TTL] permanent
"""死信件三态探针 v2（只读）。

files[] 字段实测={action, base_blob, blob_ref(相对队列根), blob_sha256, path}。
三态：
  LANDED   快照内容 == HEAD 内容（已落地，落地侧会静默剔除）
  PENDING  快照内容 != HEAD 内容（真需落地）
  NOBAG    快照袋文件缺失（无法判定）
用法：probe_dead_item.py <item.json> [...]
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(r"D:\ZephyrAlpha")
QROOT = REPO / ".runtime" / "commit_queue"


def git_bytes(*args: str) -> bytes | None:
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True)
    return r.stdout if r.returncode == 0 else None


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def check(item_path: Path) -> dict:
    j = json.loads(item_path.read_text(encoding="utf-8"))
    files = j.get("files") or []
    stat = {"LANDED": 0, "PENDING": 0, "NEW": 0, "NOBAG": 0}
    detail = []
    for f in files:
        rel = f.get("path") or ""
        ref = f.get("blob_ref") or ""
        want = f.get("blob_sha256") or ""
        bag = QROOT / ref if ref else None
        if not bag or not bag.exists():
            stat["NOBAG"] += 1
            detail.append(("NOBAG", rel, ref))
            continue
        snap = bag.read_bytes()
        if sha(snap) != want:
            stat["NOBAG"] += 1
            detail.append(("BAGSHA-MISMATCH", rel, f"{sha(snap)[:12]}!={want[:12]}"))
            continue
        head = git_bytes("show", f"HEAD:{rel}")
        if head is None:
            stat["PENDING"] += 1
            detail.append(("NEW-不在HEAD", rel, ""))
        elif sha(head) == want:
            stat["LANDED"] += 1
        else:
            stat["PENDING"] += 1
            wt = REPO / rel
            tag = "工作区同快照" if wt.exists() and sha(wt.read_bytes()) == want else "工作区又异"
            detail.append(("PENDING", rel, tag))
    return {"qid": j.get("qid") or item_path.stem, "session": j.get("session_id"),
            "dead_reason": str(j.get("dead_reason") or "").replace("\n", " ")[:150],
            "n": len(files), "stat": stat, "detail": detail}


def main():
    for p in [Path(x) for x in sys.argv[1:]]:
        if not p.exists():
            print(f"!! 不存在: {p}")
            continue
        r = check(p)
        print(f"\n### {r['qid']}  n={r['n']}  {r['stat']}")
        print(f"    dead_reason: {r['dead_reason']}")
        for st, rel, extra in r["detail"]:
            print(f"    {st:16} {rel} {extra}")


if __name__ == "__main__":
    main()
```

## triage_stale_index.py

```python
# [TTL] permanent
"""merge 前置排雷（只读）：INDEX-vs-HEAD 方向分判。

判据（2026-09-19 实证口径）：Δ=INDEX-HEAD。
  负＝回退炸弹（merge finalize 会被强制全量提交，旧稿覆盖已交付内容）→ 必须先清；
  正＝他人在途前进工作 → 别碰；
  零＝干净。
另附"工作区是否已 == HEAD"（决定清理动作是否零风险：是→git add 即归位）。
"""
import subprocess
from pathlib import Path

REPO = Path(r"D:\ZephyrAlpha")


def git(*a, binary=False):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True)
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")


staged = [l for l in git("diff", "--cached", "--name-only").splitlines() if l.strip()]
print(f"暂存条目数 = {len(staged)}")
neg, pos, zero = [], [], []
for rel in staged:
    ib = git("rev-parse", "--verify", f":{rel}") .strip()
    hb = git("rev-parse", "--verify", f"HEAD:{rel}").strip() if \
        subprocess.run(["git", "rev-parse", "--verify", f"HEAD:{rel}"], cwd=REPO,
                       capture_output=True).returncode == 0 else ""
    if not hb:
        pos.append((rel, "HEAD-无此件(新建)", "", ""))
        continue
    if ib == hb:
        zero.append(rel)
        continue
    ilen = len(git("cat-file", "blob", ib, binary=True))
    hlen = len(git("cat-file", "blob", hb, binary=True))
    wt = REPO / rel
    wt_same_head = wt.exists() and wt.read_bytes() == git("cat-file", "blob", hb, binary=True)
    rec = (rel, f"INDEX {ilen}B vs HEAD {hlen}B  Δ={ilen-hlen:+d}B",
           "工作区==HEAD" if wt_same_head else "工作区另有内容")
    (neg if ilen < hlen else pos).append(rec + (wt_same_head,))

print(f"\n干净(INDEX==HEAD) = {len(zero)}")
print(f"回退炸弹(INDEX<HEAD) = {len(neg)}   ← merge 前必须处置")
for rel, d, wtag, _ in neg:
    print(f"  NEG  {rel}\n        {d}  [{wtag}]")
print(f"\n在途前进(INDEX>HEAD 或新建) = {len(pos)}   ← 按宪法不碰")
for rel, d, *_ in pos[:15]:
    print(f"  POS  {rel}  {d}")
if len(pos) > 15:
    print(f"  ...另 {len(pos)-15} 条")
```

## demine_index.py

```python
# [TTL] permanent
"""主区 index 排弹（Max 批 2026-09-23「最小排弹：7 add + 21 reset」）。

可逆性设计（2026-09-19 playbook）：
  第 0 步 落快照：逐条记 index blob SHA + 工作区字节 sha256 + 大小 → JSON
  第 1 步 工作区已==HEAD 者 → git add（index 归位，内容零改动）
  第 2 步 其余 INDEX<HEAD 者 → git reset -- <file>（mixed，工作区零改动）
  第 3 步 复核：工作区 sha256 与快照全等 + 这些路径 INDEX==HEAD
绝不碰 INDEX>HEAD（他人前进中的在途工作）。
"""
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(r"D:\ZephyrAlpha")
SNAP = REPO / ".runtime" / "tmp" / "sweep_tail" / f"index_snapshot_{time.strftime('%Y%m%d_%H%M%S')}.json"


def git(*a, binary=False):
    for attempt in range(6):
        r = subprocess.run(["git", *a], cwd=REPO, capture_output=True)
        if r.returncode == 0 or b"index.lock" not in r.stderr:
            return r
        time.sleep(2 + attempt)
    return r


def blob_of(spec):
    r = git("rev-parse", "--verify", spec)
    return r.stdout.decode().strip() if r.returncode == 0 else None


def cat(blob):
    return git("cat-file", "blob", blob).stdout


def main():
    staged = [l for l in git("diff", "--cached", "--name-only").stdout.decode(
        "utf-8", "replace").splitlines() if l.strip()]
    add_list, reset_list, keep = [], [], []
    for rel in staged:
        ib = blob_of(f":{rel}")
        hb = blob_of(f"HEAD:{rel}")
        if hb is None:
            keep.append((rel, "HEAD 无此件（他人新建在途）——不碰"))
            continue
        if ib == hb:
            continue
        if ib is None:
            # 暂存删除：INDEX 无条目而 HEAD 有 = 负向 Δ，merge finalize 会真删已交付件
            wt = REPO / rel
            hc = cat(hb)
            wtc = wt.read_bytes() if wt.exists() else None
            rec = {"path": rel, "index_blob": None, "head_blob": hb,
                   "index_len": 0, "head_len": len(hc),
                   "worktree_sha256": hashlib.sha256(wtc).hexdigest() if wtc is not None else None,
                   "worktree_len": len(wtc) if wtc is not None else None,
                   "head_sha256": hashlib.sha256(hc).hexdigest()}
            if wtc is not None and rec["worktree_sha256"] == rec["head_sha256"]:
                rec["action"] = "add(撤销暂存删除，盘已==HEAD)"
                add_list.append(rec)
            else:
                rec["action"] = "reset(仅退 index，盘态归其 Owner)"
                reset_list.append(rec)
            continue
        ic, hc = cat(ib), cat(hb)
        wt = REPO / rel
        wtc = wt.read_bytes() if wt.exists() else None
        rec = {"path": rel, "index_blob": ib, "head_blob": hb,
               "index_len": len(ic), "head_len": len(hc),
               "worktree_sha256": hashlib.sha256(wtc).hexdigest() if wtc is not None else None,
               "worktree_len": len(wtc) if wtc is not None else None,
               "head_sha256": hashlib.sha256(hc).hexdigest()}
        if len(ic) >= len(hc):
            keep.append((rel, f"前进中 Δ={len(ic)-len(hc):+d}B——不碰"))
            continue
        if wtc is not None and hashlib.sha256(wtc).hexdigest() == rec["head_sha256"]:
            add_list.append(rec)
        else:
            reset_list.append(rec)
        (SNAP.parent / "snap_rows.jsonl").parent.mkdir(parents=True, exist_ok=True)
        rec["action"] = "add" if rec in add_list else "reset"

    SNAP.write_text(json.dumps({"add": add_list, "reset": reset_list,
                                "untouched": [k[0] for k in keep]},
                               ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"快照落盘: {SNAP.name}  add={len(add_list)} reset={len(reset_list)} 不碰={len(keep)}")
    if "--dry" in sys.argv:
        for r in add_list:
            print("  ADD   ", r["path"])
        for r in reset_list:
            print("  RESET ", r["path"], f'Δ={r["index_len"]-r["head_len"]}B',
                  f'wt={str(r["worktree_sha256"])[:8]}')
        return 0

    for r in add_list:
        git("add", "--", r["path"])
    paths = [r["path"] for r in reset_list]
    if paths:
        plist = SNAP.parent / "reset_paths.txt"
        plist.write_text("\n".join(paths) + "\n", encoding="utf-8")
        git("reset", "-q", "--pathspec-from-file=" + str(plist).replace("\\", "/"))

    bad_wt, bad_idx = [], []
    for r in add_list + reset_list:
        wt = REPO / r["path"]
        now = wt.read_bytes() if wt.exists() else b""
        if hashlib.sha256(now).hexdigest() != r["worktree_sha256"]:
            bad_wt.append(r["path"])
        if blob_of(f":{r['path']}") != blob_of(f"HEAD:{r['path']}"):
            bad_idx.append(r["path"])
    print(f"复核: 工作区字节被改动 = {len(bad_wt)} {bad_wt[:5]}")
    print(f"复核: 处置后仍 INDEX!=HEAD = {len(bad_idx)} {bad_idx[:5]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## fire_requeue_wave.py

```python
# [TTL] permanent
"""requeue 波次发射器（逐封、落地一发再发下一发；压测在飞即拒发）。

用法：
  python fire_requeue_wave.py --dry            # 只做排雷与计划，不动队列
  python fire_requeue_wave.py                  # 实发全波
  python fire_requeue_wave.py --only 0013      # 只发匹配 qid 子串的件
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(r"D:\ZephyrAlpha")
Q = REPO / ".runtime" / "commit_queue"

# 顺序＝任务书序：解锁链在前
WAVE = [
    "st-ibt-remedy-cf-20260923-0013",
    "st-emomine-20260923-0005",
    "st-combine-20260923-0017",
    "st-tdm20-20260923-0026",
    "st-xhs-full-20260922-0041",
    "st-xhs-full-20260922-0042",
    "st-xhs-full-20260922-0043",
]


def sh(*args, timeout=180):
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def stress_running() -> int:
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "@(Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*stress*' } | "
         "Where-Object { $_.CommandLine -notlike '*fire_requeue_wave*' }).Count"],
        cwd=REPO, capture_output=True, text=True, timeout=120)
    try:
        return int(r.stdout.strip().splitlines()[-1])
    except Exception:
        return -1


def find_item(token: str) -> Path | None:
    for d in [Q / "dead"] + [p for p in Q.rglob("*") if p.is_dir() and "dead" in p.name]:
        for f in d.glob(f"*{token}*.json"):
            return f
    return None


def pending_count(item: Path) -> tuple[int, int]:
    j = json.loads(item.read_text(encoding="utf-8"))
    files = j.get("files") or []
    pend = 0
    for f in files:
        rel, ref, want = f.get("path", ""), f.get("blob_ref", ""), f.get("blob_sha256", "")
        bag = Q / ref
        if not bag.exists():
            continue
        if hashlib.sha256(bag.read_bytes()).hexdigest() != want:
            continue
        h = subprocess.run(["git", "cat-file", "blob", f"HEAD:{rel}"], cwd=REPO,
                           capture_output=True)
        head_sha = hashlib.sha256(h.stdout).hexdigest() if h.returncode == 0 else None
        if head_sha != want:
            pend += 1
    return pend, len(files)


def qid_of(path: Path) -> str:
    return json.loads(path.read_text(encoding="utf-8")).get("qid") or path.stem


def status_counts() -> dict:
    out = {}
    for d in ("pending", "dead", "done"):
        p = Q / d
        out[d] = len(list(p.glob("*.json"))) if p.exists() else 0
    return out


def wait_landing(new_qid: str, minutes: int = 12) -> str:
    """轮询**新项自身**的去向。

    坑：原死信项 requeue 后仍留在 dead/（追加 requeued 标注），
    按原 qid 查 dead/ 会秒判"又死了"——只认新 qid 落在 done/ 还是 dead/。
    """
    deadline = time.time() + minutes * 60
    while time.time() < deadline:
        if (Q / "done" / f"{new_qid}.json").exists():
            return "done"
        dead = Q / "dead" / f"{new_qid}.json"
        if dead.exists():
            try:
                j = json.loads(dead.read_text(encoding="utf-8"))
                return "dead: " + str(j.get("dead_reason")).replace("\n", " ")[:200]
            except Exception:
                return "dead: unreadable"
        time.sleep(25)
    return "timeout(仍在 pending/processing)"


def wait_gate(minutes: int, need_streak: int = 3) -> bool:
    """家规"压测广播时暂停入队"的让位闸：连续 need_streak 轮 0 进程才放行。

    单轮 0 不算——压测是分批发射的（实测 8→4 的间歇态），瞬时空档会误判。
    """
    deadline = time.time() + minutes * 60
    streak = 0
    while time.time() < deadline:
        n = stress_running()
        if n == 0:
            streak += 1
            print(f"[压测闸] 0 进程（连续 {streak}/{need_streak}）", flush=True)
            if streak >= need_streak:
                return True
        else:
            streak = 0
            print(f"[压测闸] stress 进程={n}，等待", flush=True)
        time.sleep(60)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--wait-gate", type=int, default=0, help="等压测静默最多 N 分钟")
    args = ap.parse_args()

    n = stress_running()
    print(f"[压测闸] stress 进程数={n}（>0 即按家规拒发）", flush=True)
    if n > 0 and not args.dry:
        if args.wait_gate <= 0 or not wait_gate(args.wait_gate):
            print("PAUSE: 压测在飞（或等窗超时），本波不入队。")
            return 2
        print("GATE OPEN: 压测已静默，开火。")

    print(f"[队列面] {status_counts()}")
    for token in WAVE:
        if args.only and args.only not in token:
            continue
        src = find_item(token)
        if not src:
            print(f"\n!! {token}: 队列全域找不到，跳过（可能已落地）")
            continue
        qid = qid_of(src)
        pend, total = pending_count(src)
        print(f"\n### {qid}  源={src.parent.name}  件数={total} 待落地={pend}")
        if pend == 0:
            print("    SKIP: 快照内容已全部在 HEAD（requeue 只会造空 diff）")
            continue
        if args.dry:
            print("    DRY: 将执行 copy→dead/ + requeue --from-bag + 轮询")
            continue
        if src.parent.name != "dead":
            tgt = Q / "dead" / src.name
            shutil.copy2(src, tgt)
            print(f"    归档件已复制回 dead/（原件留在 {src.parent.name}/）")
        before = {p.name for p in (Q / "pending").glob("*.json")}
        before |= {p.name for p in (Q / "processing").glob("*.json")} if (Q / "processing").exists() else set()
        r = sh(sys.executable, str(REPO / "scripts" / "commit_queue.py"),
               "requeue", qid, "--from-bag", timeout=900)
        print("    requeue rc=", r.returncode, (r.stdout or r.stderr)[-260:])
        after = {p.name for p in (Q / "pending").glob("*.json")}
        after |= {p.name for p in (Q / "processing").glob("*.json")} if (Q / "processing").exists() else set()
        delta = sorted(after - before)
        if not delta:
            print("    !! 未差分到新项（可能已直接落地或 requeue 失败），人工核 status")
            continue
        new_id = delta[-1].replace(".json", "")
        outcome = wait_landing(new_id)
        print(f"    新项 {new_id} → {outcome}")
        if outcome == "done":
            lg = sh("git", "log", "-1", "--format=%h %s")
            print("    HEAD:", lg.stdout[:200])
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## secbuild_relay_registers.py

```python
# [TTL] permanent
"""secbuild 代投前置 S1：向 scratch worktree 的两本热册 CAS 补登 token 与翻译条目。

Max 令「本班 CAS 手写补登后代投」。字段全部取自该车道文件自带锚与其自述文档，
不造新语义；created_by 保留真作者 st-secbuild-20260923，代登事实写进 note。
"""
import hashlib
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(r"D:\ZephyrAlpha")
WT = REPO / ".runtime/tmp/sweep_tail/wt_sec"
BR = "ai/st-secbuild-20260923/sector-line-construction"
CAP = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"
TRA = "docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml"
DATE = "20260923"
NOTE = ("代登 by st-sweep-tail-20260923（该车道晨报自报 token/翻译已被 5b6ee808a6 吸收，"
        "经 git log --all -S 全历史零命中证伪=从未入册；Max 2026-09-23 令 CAS 补登后代投）")

CAPABILITY = {
    "src/zephyr/data/sector_state_pipeline.py": "sector_state_pipeline",
    "src/zephyr/signal_ashare/sector/sector_state_aggregator.py": "sector_state_aggregator",
    "scripts/backtest/sector_prereg_exam_runner.py": "sector_prereg_exam",
    "schemas/categories/sector_state.py": "sector_state",
    "schemas/categories/sector_preference.py": "sector_preference",
    "docs/03_modules/_domain_data/algo_flow/sector_line/sector_state_pipeline.yaml": "sector_state_pipeline",
    "docs/03_modules/_domain_signal/algo_flow/sector_state_aggregator.yaml": "sector_state_aggregator",
    "docs/_working/sector_line/MORNING_REPORT_st-secbuild_20260923.md": "sector_line",
    "docs/_working/sector_line/batch2_consumer_wiring_patch.md": "sector_line",
    "docs/_working/sector_line/sector_prereg_exam_cards_v1_frozen.md": "sector_prereg_exam",
    "docs/_working/sector_line/exam/prereg_exam_report_v1.md": "sector_prereg_exam",
    "docs/_working/sector_line/exam/prereg_exam_results_v1.yaml": "sector_prereg_exam",
}

# (module_path, domain_id, name_zh, plain_zh 大白话, responsibility_layer)
TRANS = [
    ("src/zephyr/data/sector_state_pipeline.py", "D_DATA", "板块状态落库编排器",
     "每天收盘后把板块的体检结果写进两张表的跑腿员：它自己去读板块行情面板、算好状态，再落库。"
     "算法一律不自己重写，全交给板块状态聚合器那个纯函数件；收盘定格档在 15:10 出真值，"
     "次日 09:15 的盘前档只是把前一天的定格复制一份再按盘前口径重映射，保证盘前也有数可用。",
     "infrastructure"),
    ("src/zephyr/signal_ashare/sector/sector_state_aggregator.py", "D_ASHARE_SIGNAL", "板块状态聚合器",
     "把五路板块体检指标捏成一份板块状态的算法件：动量、相对强弱四象限、涨停家数与梯队强度、"
     "资金净流入分位、市场级五状态。它只做计算不碰数据库，喂进来的表格自己出结果，"
     "所以能在考试跑批里反复重放。五路算法全部沿用 22 号设计稿已定的公式与权重，不另起炉灶。",
     "business"),
    ("scripts/backtest/sector_prereg_exam_runner.py", "D_ASHARE_SIGNAL", "板块预注册考试跑批器",
     "给板块状态这套尺子做考前承诺、考后对账的跑批件：先按冻结卡把判档标准钉死，再用历史数据"
     "一格一格算出结果，够证据就判成立、不够就老实写样本不足。当天信号只准用当天收盘前的数，"
     "收益往后错一天算，所有多重检验格子全部披露，禁写全绿。",
     "business"),
    ("schemas/categories/sector_state.py", "D_ASHARE_SIGNAL", "板块状态表结构定义",
     "板块状态这张表的结构真源：表怎么建、按什么排序、版本列怎么取舍，都以这份文件为准。"
     "用 ReplacingMergeTree 以入仓时间做版本列，读时带 FINAL 保证写后能立刻读到最新一条，"
     "避免刚写完就读到旧行的竞态。",
     "infrastructure"),
    ("schemas/categories/sector_preference.py", "D_ASHARE_SIGNAL", "板块偏好表结构定义",
     "板块偏好这张表的结构真源：记录每天给每个板块打的偏好标签、仓位倾斜幅度和禁入象限。"
     "同样以入仓时间做版本列并带 FINAL 读，消费方是 L2 门与选股漏斗（读禁入象限和倾斜幅度）。",
     "infrastructure"),
]


def git(*a, cwd=None):
    return subprocess.run(["git", *a], cwd=cwd or WT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def new_files():
    base = git("merge-base", "dev", BR, cwd=REPO).stdout.strip()
    out = git("diff", "--name-only", base, BR, cwd=REPO).stdout.split()
    res = []
    for f in out:
        if f.startswith("tests/"):
            continue
        r = subprocess.run(["git", "rev-parse", "--verify", f"HEAD:{f}"],
                           cwd=REPO, capture_output=True)
        if r.returncode != 0:
            res.append(f)
    return set(res)


def next_top_key(lines, start):
    for i in range(start + 1, len(lines)):
        if lines[i] and not lines[i][0].isspace() and lines[i][0] != "#" and ":" in lines[i]:
            return i
    return len(lines)


def insert_before(path_text, at, block):
    lines = path_text.split("\n")
    return "\n".join(lines[:at] + block + lines[at:])


def main():
    nset = new_files()
    missing = [f for f in CAPABILITY if f not in nset]
    if missing:
        print("!! 预期新建件与实算不符，放弃：", missing)
        return 1
    cap_txt = (WT / CAP).read_text(encoding="utf-8")
    tra_txt = (WT / TRA).read_text(encoding="utf-8")
    cap_d = yaml.safe_load(cap_txt)
    tra_d = yaml.safe_load(tra_txt)
    existing = {e.get("file") for e in (cap_d.get("creation_tokens") or [])}
    dup = [f for f in CAPABILITY if f in existing]
    if dup:
        print("!! 已有 token，勿双登：", dup)
        return 1
    have_mp = {e.get("module_path") for e in (tra_d.get("entries") or [])}
    tdup = [m for m, *_ in TRANS if m in have_mp]
    if tdup:
        print("!! 翻译条目已存在，勿双登：", tdup)
        return 1

    tok_block = []
    for f in CAPABILITY:
        stem = Path(f).stem.replace("_", "-")
        tok_block += [
            f"- file: {f}",
            f"  token: secbuild-{stem}-{DATE}",
            "  created_by: st-secbuild-20260923",
            f"  capability: {CAPABILITY[f]}",
            f'  merge_evaluation: "secbuild 板块线批0-批3 交付件，随代投首次入册；'
            f'同真源唯一件不并（{CAPABILITY[f]} 域内无第二件）"',
            f'  note: "{NOTE}"',
        ]
    tr_block = []
    for mp, dom, nzh, plain, layer in TRANS:
        tr_block += [
            f"- module_path: {mp}",
            f"  domain_id: {dom}",
            f"  name_zh: {nzh}",
            f"  plain_zh: {plain}",
            f"  responsibility_layer: {layer}",
        ]

    cidx = next_top_key(cap_txt.split("\n"), cap_txt.split("\n").index("creation_tokens:"))
    new_cap = insert_before(cap_txt, cidx, tok_block)
    tid = tra_txt.split("\n").index("entries:")
    # battle_map_steps 是 entries 之后的第一个顶层键
    tend = next_top_key(tra_txt.split("\n"), tid)
    new_tra = insert_before(tra_txt, tend, tr_block)

    for rel, txt in ((CAP, new_cap), (TRA, new_tra)):
        p = WT / rel
        before = hashlib.sha256(p.read_bytes()).hexdigest()
        data = yaml.safe_load(txt)
        # 断言
        if rel == CAP:
            assert len(data["creation_tokens"]) == len(cap_d["creation_tokens"]) + len(CAPABILITY)
        else:
            assert len(data["entries"]) == len(tra_d["entries"]) + len(TRANS)
        p.write_text(txt, encoding="utf-8", newline="\n")
        print(f"落盘 {rel.split('/')[-1]}  base={before[:10]} 新={hashlib.sha256(p.read_bytes()).hexdigest()[:10]}")

    # 纯插入机证
    for rel in (CAP, TRA):
        d = subprocess.run(["git", "diff", "--numstat", "HEAD", "--", rel],
                           cwd=WT, capture_output=True, text=True)
        print("numstat", rel.split("/")[-1], "→", d.stdout.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
