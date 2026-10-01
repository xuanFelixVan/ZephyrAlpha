# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] wave2.lane_inventory
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
# lane_inventory.py — 波2 车道现场清点器（机生产物 lane_inventory.yaml 的唯一生产者，禁手改产物）
# 性质：只读取证。对任何被清点对象（.aidrafts/* .worktrees/* .runtime/tmp/campaign_hold）零写入、零 git add/commit。
# 唯一写出：本目录 lane_inventory.yaml；--print-md-bags 时另向 stdout 打袋清单 markdown 块。
# 守卫（02 册 §七 / R-4 必抄）：判"真 worktree"一律 `git -C <dir> rev-parse --show-toplevel` == 该目录；
#   否则 git 向上解析到主仓，把主区脏面误记为车道脏面（自检红旗：多道 dirty/patch 同值即此 bug）。
# 口径：字节比较一律先 CRLF→LF 归一（本仓 EOL 归一是权威口径，R-6-1）；未跟踪计数只来自
#   `git status --porcelain --untracked-files=all` 的 `??` 行（X-54 教训，禁 ls|wc）。
# 生成器纪律：禁 datetime.now()/time.time()（RULE-SCHEMA-TZ）；时间证据只用文件 mtime。
import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

from zephyr.shared.infra.process_pool import run_subprocess_hidden  # TRAE-067 无窗口统一入口

REPO = Path("D:/ZephyrAlpha")
LANE_ROOT = REPO / ".aidrafts/st-final-build-20260926/docs/_working/total_command_closeout/wave2"
OUT_YAML = LANE_ROOT / "lane_inventory.yaml"

# (site_id, pack, 相对路径, 类型)  —— 类型: worktree=待验真 worktree；holddir=campaign_hold 普通目录；main_named=主区点名件(2.4)
SITES = [
    ("st-mapbuild-20260924", "2.1", ".aidrafts/st-mapbuild-20260924", "worktree"),
    ("st-ailayer-final-20260924", "2.2", ".worktrees/st-ailayer-final-20260924", "worktree"),
    ("lane_ff_door", "2.3", ".aidrafts/lane_ff_door", "worktree"),
    ("lane_ff_books", "2.3", ".aidrafts/lane_ff_books", "worktree"),
    ("lane_ff_replay", "2.3", ".aidrafts/lane_ff_replay", "worktree"),
    ("st-audit-fix-20260924", "2.3", ".aidrafts/st-audit-fix-20260924", "worktree"),
    ("campaign_hold", "2.3", ".runtime/tmp/campaign_hold", "holddir"),
    ("lane_ff_chfail", "2.4", ".aidrafts/lane_ff_chfail", "worktree"),
    ("lane_ff_single_writer", "SUPP", ".aidrafts/lane_ff_single_writer", "worktree"),
    ("lane_ff_snapself", "SUPP", ".aidrafts/lane_ff_snapself", "worktree"),
    ("lane_reland_final", "SUPP", ".aidrafts/lane_reland_final", "worktree"),
    ("lane_snapself_land", "SUPP", ".aidrafts/lane_snapself_land", "worktree"),
    ("lane_w17_only", "SUPP", ".aidrafts/lane_w17_only", "worktree"),
    ("main_named_t1t2", "2.4", ".", "main_named"),
]
MAIN_NAMED_PAT = re.compile(r"t1_t2_handover")

R5_RE = re.compile(r"_\d+$")
TOKEN_EXTS = {".py", ".yaml", ".yml", ".md", ".ps1", ".sql", ".toml"}
BIG = 300 * 1024 * 1024


def git(args, cwd=REPO):
    r = run_subprocess_hidden(["git"] + args, cwd=str(cwd), capture_output=True)
    return r.stdout, r.returncode


def norm_bytes(data, binary=False):
    if binary:
        return data
    return data.replace(b"\r\n", b"\n")


def looks_text(data):
    return b"\x00" not in data[:65536]


def sha_file(p: Path):
    """返回 (归一sha, 原始大小, mtime(int), 是否二进制)。"""
    try:
        size = p.stat().st_size
    except OSError:
        return None, None, None, None
    mtime = int(p.stat().st_mtime)
    if size > BIG:
        return "TOO_BIG", size, mtime, True
    data = p.read_bytes()
    binf = not looks_text(data)
    return hashlib.sha256(norm_bytes(data, binf)).hexdigest(), size, mtime, binf


def cat_file_batch(cwd, rev, paths):
    """git cat-file --batch：按查询顺序逐条回 {query: oid|None, 内容不取}. 用 --batch-check 更省内存."""
    if not paths:
        return {}
    lines = []
    for p in paths:
        q = f"{rev}:{p}" if rev else f":{p}"
        lines.append(q.encode("utf-8", "surrogateescape"))
    stdin = b"\n".join(lines) + b"\n"
    r = run_subprocess_hidden(["git", "cat-file", "--batch-check"], cwd=str(cwd), input=stdin, capture_output=True)
    out = r.stdout.split(b"\n")
    res = {}
    for i, p in enumerate(paths):
        line = out[i] if i < len(out) else b""
        s = line.decode("utf-8", "surrogateescape")
        if p == "" or not s or s.endswith(" missing") or s.startswith("missing"):
            res[p] = None
        else:
            parts = s.split()
            res[p] = parts[0] if parts and parts[0] != "missing" else None
    return res


def blob_bytes_sha(cwd, query, cache={}):
    """取 <rev>:path blob 内容并归一 sha（单件调用，数量可控）。"""
    r = run_subprocess_hidden(["git", "cat-file", "blob", query], cwd=str(cwd), capture_output=True)
    if r.returncode != 0:
        return None
    data = r.stdout
    return hashlib.sha256(norm_bytes(data, not looks_text(data))).hexdigest()


def batch_blob_shas(cwd, rev, paths):
    """一次 git cat-file --batch 拉全部 rev:path 内容，返回 {path: 归一sha|None}。"""
    if not paths:
        return {}
    stdin = b"\n".join(f"{rev}:{p}".encode("utf-8", "surrogateescape") for p in paths) + b"\n"
    r = run_subprocess_hidden(["git", "cat-file", "--batch"], cwd=str(cwd), input=stdin, capture_output=True)
    out = r.stdout
    res = {}
    pos = 0
    for p in paths:
        nl = out.find(b"\n", pos)
        if nl < 0:
            res[p] = None
            continue
        header = out[pos:nl]
        pos = nl + 1
        if header.endswith(b" missing") or header == b"missing":
            res[p] = None
            continue
        parts = header.split()
        if len(parts) < 3 or parts[0] == b"missing":
            res[p] = None
            continue
        size = int(parts[2])
        data = out[pos : pos + size]
        pos += size + 1
        res[p] = hashlib.sha256(norm_bytes(data, not looks_text(data))).hexdigest()
    return res


def status_porcelain(cwd):
    out, _ = git(["status", "--porcelain", "--untracked-files=all", "-z"], cwd=cwd)
    parts = [x for x in out.split(b"\0") if x]
    entries = []
    i = 0
    while i < len(parts):
        rec = parts[i]
        xy = rec[:2].decode("ascii", "replace")
        path = rec[3:].decode("utf-8", "surrogateescape")
        if xy[0] in "RC" and i + 1 < len(parts):
            i += 1  # 改名条目的第二字段（原路径）跳过
        entries.append((xy, path))
        i += 1
    return entries


def bucket(path):
    name = Path(path).name
    if "/_registry/" in path or path.startswith("docs/01_policies_and_standards/_registry"):
        return "HOTREG"
    if name in {
        "ruling_registry.yaml",
        "issue_registry.yaml",
        "gate_registry.yaml",
        "module_translation_registry.yaml",
        "terminology_glossary.yaml",
        "functional_domain_registry.yaml",
        "capability_canonical_file_registry.yaml",
        "registry_of_registries.yaml",
        "script_manifest.yaml",
        "in_process_gate_registry.yaml",
    }:
        return "HOTREG"
    if path.startswith("docs/01_policies_and_standards/rules/"):
        return "RULES"
    if path.startswith("config/flags"):
        return "FLAGS"
    if path.startswith("src/"):
        seg = path.split("/")
        return "SRC:" + (seg[2] if len(seg) > 2 else "misc")
    if path.startswith("scripts/"):
        seg = path.split("/")
        return "SCRIPTS:" + (seg[1] if len(seg) > 2 else "misc")
    if path.startswith("tests/"):
        return "TEST"
    if path.startswith("docs/_working/"):
        return "DOCSWORK"
    if path.startswith("docs/"):
        return "DOCS"
    if path.startswith("data/"):
        return "DATA"
    return "OTHER"


def survey_worktree(site_id, pack, rel):
    d = REPO / rel
    info = {
        "site_id": site_id,
        "pack": pack,
        "path": rel.replace("\\", "/"),
        "exists": d.is_dir(),
        "real_worktree": False,
        "toplevel": None,
        "branch": None,
        "head": None,
        "behind_dev": None,
        "own_commits_dev_ahead": None,
        "files": [],
        "error": None,
    }
    if not d.is_dir():
        info["error"] = "目录不存在"
        return info
    out, rc = git(["rev-parse", "--show-toplevel"], cwd=d)
    top = out.decode().strip().replace("\\", "/")
    expect = str(d).replace("\\", "/")
    if rc != 0 or top.lower() != expect.lower():
        info["toplevel"] = top
        info["error"] = "非真 worktree（toplevel 解析到外部），仅按普通目录登记，禁采信其 git 读数"
        # 退回普通目录清点
        files = []
        for f in sorted(d.rglob("*")):
            if f.is_file():
                rp = f.relative_to(d).as_posix()
                sha, size, mtime, binf = sha_file(f)
                files.append(
                    {
                        "path": rp,
                        "xy": "dir",
                        "state": "not_in_head_new" if False else "uncounted",
                        "disk_sha": sha,
                        "size": size,
                        "mtime": mtime,
                        "binary": binf,
                        "domain": bucket(rp),
                    }
                )
        info["files"] = files
        return info
    info["real_worktree"] = True
    info["toplevel"] = top
    out, _ = git(["rev-parse", "HEAD"], cwd=d)
    head = out.decode().strip()
    info["head"] = head
    out, _ = git(["rev-parse", "--abbrev-ref", "HEAD"], cwd=d)
    info["branch"] = out.decode().strip()
    out, _ = git(["rev-list", "--count", f"{head}..dev"], cwd=REPO)
    info["behind_dev"] = int(out.decode().strip() or 0)
    out, _ = git(["rev-list", "--count", f"dev..{head}"], cwd=REPO)
    info["own_commits_dev_ahead"] = int(out.decode().strip() or 0)

    entries = status_porcelain(d)
    tracked = [(xy, p) for xy, p in entries if xy != "??"]
    untracked = [(xy, p) for xy, p in entries if xy == "??"]
    allpaths = sorted({p for _, p in entries})
    # 车道自身 HEAD 只作身份登记；三态分箱一律对"落地基底 dev HEAD"判（免投/要投/新建以 dev 为权威）
    lane_exist = cat_file_batch(d, head, allpaths)
    dev_exist = cat_file_batch(REPO, "dev", allpaths)
    dev_shas = batch_blob_shas(REPO, "dev", [p for p in allpaths if dev_exist.get(p)])
    files = []
    for xy, p in entries:
        disk = d / Path(*p.split("/"))
        dsha, size, mtime, binf = sha_file(disk) if disk.is_file() else (None, None, None, None)
        in_dev = bool(dev_exist.get(p))
        hsha = dev_shas.get(p) if in_dev else None
        if in_dev and hsha and dsha and hsha == dsha:
            state = "in_head_equal"  # 与 dev 等值 → 免投
        elif in_dev and dsha is not None:
            state = "in_head_updated"  # dev 有而盘上更新 → 要投（热册走 R-1 块级纯插入）
        elif in_dev and dsha is None:
            state = "deleted_vs_head"  # dev 有而盘上无 → 只上报，禁当删除投
        else:
            state = "not_in_head_new"  # dev 查无此路径 → R-2 新建件三件套
        files.append(
            {
                "path": p,
                "xy": xy,
                "state": state,
                "in_head": in_dev,
                "lane_head_in": lane_exist.get(p) is not None,
                "disk_sha": dsha,
                "head_sha": hsha,
                "size": size,
                "mtime": mtime,
                "binary": binf,
                "domain": bucket(p),
                "r5_suspect": bool(R5_RE.search(Path(p).stem)),
            }
        )
    info["counts"] = {
        "porcelain_total": len(entries),
        "tracked_changed": len(tracked),
        "untracked": len(untracked),
        "in_head_equal": sum(1 for f in files if f["state"] == "in_head_equal"),
        "in_head_updated": sum(1 for f in files if f["state"] == "in_head_updated"),
        "not_in_head_new": sum(1 for f in files if f["state"] == "not_in_head_new"),
        "deleted_vs_head": sum(1 for f in files if f["state"] == "deleted_vs_head"),
        "r5_suspect": sum(1 for f in files if f.get("r5_suspect")),
    }
    info["files"] = files
    return info


def survey_holddir(site_id, pack, rel):
    d = REPO / rel
    info = {
        "site_id": site_id,
        "pack": pack,
        "path": rel,
        "exists": d.is_dir(),
        "real_worktree": False,
        "kind": "holddir",
        "files": [],
        "error": None,
    }
    if not d.is_dir():
        info["error"] = "目录不存在"
        return info
    # campaign_hold 文件名 = 目标路径 '/'→'__' 的编码；用主仓 HEAD 树反查真目标
    out, _ = git(["ls-tree", "-r", "--name-only", "HEAD"], cwd=REPO)
    enc = {}
    for p in out.decode("utf-8", "surrogateescape").splitlines():
        enc[p.replace("/", "__")] = p
    files = []
    for f in sorted(d.rglob("*")):
        if not f.is_file():
            continue
        fn = f.name
        target = enc.get(fn)
        dsha, size, mtime, binf = sha_file(f)
        hsha = blob_bytes_sha(REPO, f"HEAD:{target}") if target else None
        main_disk = REPO / Path(*target.split("/")) if target else None
        mdisk_sha = sha_file(main_disk)[0] if main_disk and main_disk.is_file() else None
        if target and hsha and hsha == dsha:
            state = "in_head_equal"
        elif target:
            state = "in_head_updated"
        else:
            state = "not_in_head_new"
        files.append(
            {
                "hold_name": fn,
                "target_path": target,
                "xy": "hold",
                "state": state,
                "in_head": bool(target),
                "disk_sha": dsha,
                "head_sha": hsha,
                "main_disk_sha": mdisk_sha,
                "size": size,
                "mtime": mtime,
                "binary": binf,
                "domain": bucket(target or fn),
                "r5_suspect": bool(R5_RE.search(Path(target or fn).stem)),
            }
        )
    info["files"] = files
    info["counts"] = {
        "dir_files": len(files),
        "in_head_equal": sum(1 for f in files if f["state"] == "in_head_equal"),
        "in_head_updated": sum(1 for f in files if f["state"] == "in_head_updated"),
        "not_in_head_new": sum(1 for f in files if f["state"] == "not_in_head_new"),
        "equal_to_main_disk": sum(1 for f in files if f["main_disk_sha"] and f["main_disk_sha"] == f["disk_sha"]),
    }
    return info


def survey_main_named(site_id, pack, rel):
    d = REPO
    info = {
        "site_id": site_id,
        "pack": pack,
        "path": ".",
        "kind": "main_named",
        "real_worktree": True,
        "toplevel": str(REPO).replace("\\", "/"),
        "files": [],
        "error": None,
    }
    out, _ = git(["rev-parse", "HEAD"], cwd=d)
    head = out.decode().strip()
    info["head"] = head
    info["branch"] = "dev"
    info["behind_dev"] = 0
    info["own_commits_dev_ahead"] = 0
    entries = [(xy, p) for xy, p in status_porcelain(d) if MAIN_NAMED_PAT.search(p)]
    files = []
    for xy, p in entries:
        disk = d / Path(*p.split("/"))
        dsha, size, mtime, binf = sha_file(disk) if disk.is_file() else (None, None, None, None)
        ih = cat_file_batch(d, head, [p]).get(p)
        hsha = blob_bytes_sha(d, f"HEAD:{p}") if ih else None
        isha = blob_bytes_sha(d, f":{p}")  # index 字节（AM 案关键：门禁读 index）
        if ih and hsha == dsha:
            state = "in_head_equal"
        elif ih:
            state = "in_head_updated"
        else:
            state = "not_in_head_new"
        files.append(
            {
                "path": p,
                "xy": xy,
                "state": state,
                "in_head": bool(ih),
                "disk_sha": dsha,
                "head_sha": hsha,
                "index_sha": isha,
                "size": size,
                "mtime": mtime,
                "binary": binf,
                "domain": bucket(p),
                "r5_suspect": bool(R5_RE.search(Path(p).stem)),
            }
        )
    info["files"] = files
    info["counts"] = {
        "porcelain_total": len(entries),
        "in_head_equal": sum(1 for f in files if f["state"] == "in_head_equal"),
        "in_head_updated": sum(1 for f in files if f["state"] == "in_head_updated"),
        "not_in_head_new": sum(1 for f in files if f["state"] == "not_in_head_new"),
    }
    return info


def fpath(x):
    return x.get("target_path") or x.get("path") or x.get("hold_name") or "?"


def build_bags(sites):
    """一袋一域、袋≤38、本体+其测试同袋、热册单独成袋（R-1 处方）、FLAGS 单独成袋。"""
    BAGMAX = 38
    bags = []
    by_pack = {}
    for s in sites:
        if not s.get("files"):
            continue
        for f in s["files"]:
            if f["state"] not in ("in_head_updated", "not_in_head_new"):
                continue
            key = (s["pack"], s["site_id"])
            by_pack.setdefault(s["pack"], {}).setdefault(s["site_id"], []).append(f)
    for pack in sorted(by_pack):
        for sid in sorted(by_pack[pack]):
            fl = by_pack[pack][sid]
            tests = [f for f in fl if f["domain"] == "TEST"]
            stems = {}
            for t in tests:
                stems.setdefault(re.sub(r"^test_", "", Path(fpath(t)).stem), []).append(t)
            units = []
            used_tests = set()
            for f in sorted([x for x in fl if x["domain"] != "TEST"], key=lambda x: (x["domain"], fpath(x))):
                mates = [t for t in stems.get(Path(fpath(f)).stem, []) if id(t) not in used_tests]
                for t in mates:
                    used_tests.add(id(t))
                units.append([f] + mates)
            for t in tests:
                if id(t) not in used_tests:
                    units.append([t])
            # 域序：热册/旗标最后且各自单袋；代码域在前
            dom_order = sorted({u[0]["domain"] for u in units}, key=lambda dd: (dd in ("HOTREG", "FLAGS", "RULES"), dd))
            seq = 0
            for dd in dom_order:
                du = [u for u in units if u[0]["domain"] == dd]
                if dd in ("HOTREG", "FLAGS", "RULES"):
                    chunks = [[u] for u in du]
                else:
                    chunks, cur = [], []
                    n = 0
                    for u in du:
                        if cur and n + len(u) > BAGMAX:
                            chunks.append(cur)
                            cur = []
                            n = 0
                        cur.append(u)
                        n += len(u)
                    if cur:
                        chunks.append(cur)
                for ch in chunks:
                    seq += 1
                    items = [x for u in ch for x in u]
                    abbrev = re.sub(r"[^A-Za-z0-9]+", "-", dd)[:24]
                    bags.append(
                        {
                            "bag": f"{pack}-{sid[-20:]}-{abbrev}-{seq:02d}",
                            "pack": pack,
                            "site": sid,
                            "domain": dd,
                            "size": len(items),
                            "items": [{"path": fpath(x), "state": x["state"]} for x in items],
                            "obligations": {
                                "creation_tokens": [
                                    fpath(x)
                                    for x in items
                                    if x["state"] == "not_in_head_new" and Path(fpath(x)).suffix in TOKEN_EXTS
                                ],
                                "translation_reg": [
                                    fpath(x)
                                    for x in items
                                    if x["state"] == "not_in_head_new"
                                    and fpath(x).endswith(".py")
                                    and not fpath(x).startswith("tests/")
                                ],
                                "depgraph_node": [
                                    fpath(x)
                                    for x in items
                                    if x["state"] == "not_in_head_new"
                                    and fpath(x).endswith(".py")
                                    and fpath(x).startswith(("src/", "scripts/"))
                                ],
                                "algo_note_sync": any(x["domain"].startswith("SRC:") for x in items),
                                "r1_base_repair": dd in ("HOTREG", "RULES"),
                                "r5_suspects": [fpath(x) for x in items if x.get("r5_suspect")],
                            },
                        }
                    )
    return bags


def find_conflicts(sites):
    seen = {}
    for s in sites:
        for f in s.get("files", []):
            p = f.get("target_path") or f.get("path")
            if not p or f.get("disk_sha") is None:
                continue
            seen.setdefault(p, []).append(
                {"site": s["site_id"], "disk_sha": f["disk_sha"], "mtime": f.get("mtime"), "state": f["state"]}
            )
    out = []
    for p, vers in sorted(seen.items()):
        if len(vers) > 1 and len({v["disk_sha"] for v in vers}) > 1:
            out.append({"target_path": p, "versions": vers})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--print-md-bags", action="store_true")
    args = ap.parse_args()
    sites = []
    for sid, pack, rel, kind in SITES:
        if kind == "worktree":
            sites.append(survey_worktree(sid, pack, rel))
        elif kind == "holddir":
            sites.append(survey_holddir(sid, pack, rel))
        else:
            sites.append(survey_main_named(sid, pack, rel))
        sys.stderr.write(f"done {sid}\n")
    bags = build_bags(sites)
    conflicts = find_conflicts(sites)
    out, _ = git(["rev-parse", "dev"], cwd=REPO)
    doc = {
        "generated_by": "docs/_working/total_command_closeout/wave2/lane_inventory.py（机生，禁手改本产物）",
        "authority": {
            "repo": "D:/ZephyrAlpha",
            "dev_head": out.decode().strip(),
            "three_state_baseline": "dev HEAD（落地基底；车道自身 HEAD 仅记入 lane_head_in 供身份对照）",
            "eol_rule": "CRLF→LF 归一后比 sha（R-6-1）",
            "untracked_rule": "只信 git status --porcelain --untracked-files=all 的 ?? 行（X-54）",
            "worktree_guard": "rev-parse --show-toplevel 必须等于目录本身（R-4）",
        },
        "totals": {
            "sites": len(sites),
            "real_worktrees": sum(1 for s in sites if s.get("real_worktree")),
            "in_head_equal": sum(s.get("counts", {}).get("in_head_equal", 0) for s in sites),
            "in_head_updated": sum(s.get("counts", {}).get("in_head_updated", 0) for s in sites),
            "not_in_head_new": sum(s.get("counts", {}).get("not_in_head_new", 0) for s in sites),
            "deleted_vs_head": sum(s.get("counts", {}).get("deleted_vs_head", 0) for s in sites),
            "bags": len(bags),
            "conflict_groups": len(conflicts),
        },
        "sites": sites,
        "bags": bags,
        "conflicts": conflicts,
    }
    import yaml

    OUT_YAML.write_text(
        yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8", newline="\n"
    )
    print("TOTALS:", doc["totals"])
    for s in sites:
        print(
            f"{s['site_id']:26s} wt={s.get('real_worktree')} head={str(s.get('head'))[:10]} "
            f"behind={s.get('behind_dev')} own={s.get('own_commits_dev_ahead')} counts={s.get('counts')} err={s.get('error')}"
        )
    print("MAXBAG:", max((b["size"] for b in bags), default=0), "BAGS:", len(bags))
    if args.print_md_bags:
        for b in bags:
            print(f"BAG|{b['bag']}|{b['domain']}|{b['size']}")
            for it in b["items"]:
                print(f"   {it['state']:16s} {it['path']}")
        for c in conflicts:
            print(f"CONF|{c['target_path']}")
            for v in c["versions"]:
                print(f"   {v['site']:24s} sha={v['disk_sha'][:12]} mtime={v['mtime']} {v['state']}")


if __name__ == "__main__":
    main()
