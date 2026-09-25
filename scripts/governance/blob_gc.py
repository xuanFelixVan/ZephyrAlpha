# [BLUEPRINT] MOD-QCURE-BLOBS | scripts/governance/blob_gc.py | §blobs 退役通道（归档式 GC，归档不删除）
# [MODULE] scripts.governance.blob_gc
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] stdlib；scripts.commit_queue.resolve_queue_root（队列根解析唯一真源，经 importlib 文件加载复用，禁第二解析器）
# [CONSUMERS] QMine 战役总包（st-qmine-20260925 M4 落地执行人）；AI session 按需 CLI；queue_health 可选只读 import 扫描函数
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 默认 dry-run 零写（--archive 才动盘、--restore 才逆向，二者缺一不可显式）；
#              四层竞态防护=mtime 宽限(默认 7d=done TTL 同节奏)/动前二次重扫取交集/内容寻址自愈(挪走后同 sha 再入队时
#              _store_blob exists 检查失败→从 worktree 重落新 blob，零丢失仅一副本)/全程不持 SerializerLease；
#              只归档不删除（归档=同卷 os.rename 原子；删除需 FORCE_ENV+Owner 门位另走裁定，本命令永久无删除域）；
#              候选集恒=孤儿∧mtime 超宽限——A 活引用/B 仅 dead/hold 引用永不入候选（dead 永不清理=66 号 §8 不变量），
#              C 类不动等 cleanup_done 自然消化，D 类仅归档引用本轮禁碰（phase2 挂起待裁定）；
#              归档史(dead_archive_*/dead_purged_*/dead_triage*.jsonl)只读计入引用集；动作必留 blobs_archive/manifest.jsonl
#              审计（对齐 purge_audit 先例，相对路径锚定，还原=按 manifest 反向 rename）；测试全 tmp_path 隔离禁触生产队列
# [MODIFY-GUARD] none（独立子系统，零改动 commit_queue/landing；候选口径变更须同步 QMine M4 簿 §2④ 与本头 INVARIANTS）
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 队列根缺 blobs/ → exit 2 拒绝；--restore manifest 缺失 → exit 2；manifest 坏行跳过计数不中断；
#                  单袋 JSON 损坏 → 跳过计入 skipped；archive 遇 dst 已存在 → 跳过留痕不覆盖
# [TESTS] tests/governance/test_blob_gc.py
# [A_module] module_id=MOD-QCURE-BLOBS | layer=script | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""blob_gc.py — blobs 内容寻址存储的归档式 GC（QMine M4 承重件；默认 dry-run，归档不删除）。

背景：QMine 04_blobs_gc 矿簿 §1⑥ 实测 blobs 20504 个/3.42GB，其中零引用孤儿 5251 个/1.08GB——
主生成机制=cleanup_done 删 done JSON（TTL 7d）后其 blob 失引用。blob 唯二读者=落地 _apply_snapshot
与 requeue --from-bag；归档袋（dead_archive_*）机械上不可 from-bag 取回 ⇒ 孤儿当前零读者。
业界同构（git gc/Borg/restic 三家一致）：引用计数+宽限期+归档先于删除。

四态引用扫描口径（对齐矿簿 §1⑥ 台账）：
    live    = pending/processing + hold_* 引用            → A 类，禁碰
    dead    = dead/ 引用                                  → B 类独占=活死信回放面，禁碰
    done    = done/ 引用                                  → C2 独占等 cleanup_done 消化，不动
    archive = dead_archive_*/dead_purged_*/dead_triage*.jsonl 引用 → D 类独占 phase2 挂起，禁碰
    orphan  = 无任何 JSON 引用                            → Z 类，本轮唯一处置对象（归档不删）

用法（仓库根，Python 3.12）：
    python scripts/governance/blob_gc.py                       # dry-run 分桶报告（零写）
    python scripts/governance/blob_gc.py --json                # 机器输出（stdout，永不落盘 .runtime）
    python scripts/governance/blob_gc.py --archive             # 执行：孤儿∧mtime>7d → 挪 blobs_archive/+manifest
    python scripts/governance/blob_gc.py --archive --grace-days 14
    python scripts/governance/blob_gc.py --restore .runtime/commit_queue/blobs_archive/manifest.jsonl
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT  # noqa: PLC0415 — SSOT canonical（禁第二真源）

BLOBS_DIR = "blobs"
ARCHIVE_DIR = "blobs_archive"
MANIFEST_NAME = "manifest.jsonl"
DEFAULT_GRACE_DAYS = 7.0  # = done TTL 同节奏（矿簿 §2④ 定案；<1d 的 53 个是入队竞态窗，mtime 宽限天然覆盖）

# 引用四态（扫描分类唯一 vocabulary）
LIVE, DONE, DEAD, ARCHIVE = "live", "done", "dead", "archive"

_HEX = frozenset("0123456789abcdef")
_SHA_LEN = 64

BUCKET_LABELS = {
    "live": "A 活引用(pending/processing/hold)",
    "dead_only": "B 仅dead引用(回放面,禁碰)",
    "done_only": "C2 仅done引用(等cleanup消化)",
    "done_archive_mix": "C1 done+归档混引",
    "archive_only": "D 仅归档引用(phase2挂起,禁碰)",
    "orphan": "Z 零引用孤儿(本轮处置对象)",
    "mixed": "多类混引(罕见,禁碰)",
}
_SINGLETON_BUCKET = {DEAD: "dead_only", DONE: "done_only", ARCHIVE: "archive_only"}


def _is_sha(value: object) -> bool:
    """64 位小写 hex 才认作 blob sha（内容寻址命名约定，CQ _store_blob 同款）。"""
    return isinstance(value, str) and len(value) == _SHA_LEN and set(value) <= _HEX


def load_queue_resolver():
    """importlib 文件加载 scripts/commit_queue.py，复用 resolve_queue_root（禁第二解析器）。"""
    cq_path = REPO_ROOT / "scripts" / "commit_queue.py"
    spec = importlib.util.spec_from_file_location("_blob_gc_cq", cq_path)
    if spec is None or spec.loader is None:  # pragma: no cover — 路径恒存在，防御性
        raise RuntimeError(f"无法加载队列根解析真源: {cq_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod.resolve_queue_root


def _classify_entry(entry: Path) -> tuple[str, str] | None:
    """队列根一级条目 → (kind, 引用类)；不识别的条目（blobs/serializer/purge_audit 等）返回 None 跳过。"""
    name = entry.name
    if name in (BLOBS_DIR, ARCHIVE_DIR):  # blob 库自身与归档库都不是引用源
        return None
    if entry.is_dir():
        if name in ("pending", "processing") or name.startswith("hold"):
            return "dir", LIVE
        if name == "done":
            return "dir", DONE
        if name == "dead":
            return "dir", DEAD
        if name.startswith(("dead_archive", "dead_purged")):
            return "dir", ARCHIVE
        return None
    if entry.is_file() and entry.suffix == ".jsonl" and name.startswith("dead_triage"):
        return "file", ARCHIVE  # triage jsonl=归档史（袋逐行，files[].blob_sha256）
    return None


def _bag_shas(obj: object) -> list[str]:
    """提取袋对象 files[].blob_sha256（64-hex 校验；files 缺失/异型=空列表）。"""
    if not isinstance(obj, dict):
        return []
    files = obj.get("files")
    if not isinstance(files, list):
        return []
    return [f["blob_sha256"] for f in files if isinstance(f, dict) and _is_sha(f.get("blob_sha256"))]


def _read_json(path: Path) -> object | None:
    """读单袋 JSON；损坏/不可读返回 None（调用方计 skipped，不中断）。"""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def _absorb_jsonl(path: Path, sink: set[str], skipped: dict[str, int]) -> None:
    """逐行吸收 jsonl 账本（triage/hold manifest，袋逐行）；坏行跳过计数。"""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        skipped["jsonl_lines"] += 1
        return
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            skipped["jsonl_lines"] += 1
            continue
        sink.update(_bag_shas(obj))


def _scan_refs(queue_root: Path) -> tuple[dict[str, set[str]], dict[str, int]]:
    """全队列一级只读扫描：引用类 → sha 集合。损坏账本降级跳过计数，绝不中断。"""
    refs: dict[str, set[str]] = {LIVE: set(), DONE: set(), DEAD: set(), ARCHIVE: set()}
    skipped = {"bags": 0, "jsonl_lines": 0}
    for entry in sorted(queue_root.iterdir()):
        classified = _classify_entry(entry)
        if classified is None:
            continue
        kind, ref_class = classified
        if kind == "dir":
            targets = sorted([*entry.glob("*.json"), *entry.glob("*.jsonl")])
        else:
            targets = [entry]
        for path in targets:
            if path.suffix == ".jsonl":
                _absorb_jsonl(path, refs[ref_class], skipped)
                continue
            obj = _read_json(path)
            if obj is None:
                skipped["bags"] += 1
                continue
            refs[ref_class].update(_bag_shas(obj))
    return refs, skipped


def _disk_blobs(queue_root: Path) -> dict[str, Path]:
    """blobs/ 在盘清单：文件名=64-hex 才认作 blob；目录缺失=队列根不对，raise FileNotFoundError。"""
    blobs_dir = queue_root / BLOBS_DIR
    if not blobs_dir.is_dir():
        raise FileNotFoundError(f"队列 blobs 目录缺失: {blobs_dir}")
    return {p.name: p for p in blobs_dir.iterdir() if p.is_file() and _is_sha(p.name)}


def _bucket_of(ref_classes: set[str]) -> str:
    """有引用的 sha → 分桶键（live 优先；单一独占；done+archive 混引单独成桶 C1；其余=mixed）。"""
    if LIVE in ref_classes:
        return "live"
    present = ref_classes & {DEAD, DONE, ARCHIVE}
    if len(present) == 1:
        return _SINGLETON_BUCKET[next(iter(present))]
    if present == {DONE, ARCHIVE}:
        return "done_archive_mix"
    return "mixed"


def build_report(queue_root: Path, *, now: datetime, grace_days: float = DEFAULT_GRACE_DAYS) -> dict:
    """四态扫描+分桶报告（纯只读；孤儿候选=orphan∧mtime 超宽限期）。"""
    refs, skipped = _scan_refs(queue_root)
    disk = _disk_blobs(queue_root)
    referenced: set[str] = set()
    for shas in refs.values():
        referenced |= shas
    buckets = {key: {"label": label, "count": 0, "bytes": 0} for key, label in BUCKET_LABELS.items()}
    phantom = sorted(referenced - disk.keys())
    cutoff = (now - timedelta(days=grace_days)).timestamp()
    candidates: list[str] = []
    candidate_bytes = 0
    for sha, path in sorted(disk.items()):
        ref_classes = {cls for cls, shas in refs.items() if sha in shas}
        bucket = "orphan" if not ref_classes else _bucket_of(ref_classes)
        size = path.stat().st_size
        buckets[bucket]["count"] += 1
        buckets[bucket]["bytes"] += size
        if bucket == "orphan" and path.stat().st_mtime < cutoff:
            candidates.append(sha)
            candidate_bytes += size
    return {
        "mode": "dry-run",
        "generated_at": now.isoformat(timespec="seconds"),
        "queue_root": str(queue_root),
        "grace_days": grace_days,
        "buckets": buckets,
        "orphan_candidates": {"count": len(candidates), "bytes": candidate_bytes, "shas": candidates},
        "phantom_refs": phantom,
        "scanned": {"blobs_on_disk": len(disk), "referenced_shas": len(referenced)},
        "skipped": skipped,
        "notes": [
            "删除不在本命令域：归档优于删除（矿簿裁定），删除需 FORCE_ENV+Owner 门位另走裁定",
            "D 类（仅归档引用）phase2 挂起待裁定，本轮禁碰；B 类 dead 永不清理（66 号 §8 不变量）",
            "四层竞态防护：mtime 宽限/动前二次重扫取交集/内容寻址自愈/不持 SerializerLease",
        ],
    }


def run_archive(queue_root: Path, *, now: datetime, grace_days: float = DEFAULT_GRACE_DAYS) -> dict:
    """执行归档：候选集 → 动前二次重扫取交集（竞态第 2 层）→ 同卷 os.rename → manifest 追加留痕。

    不做任何删除；blobs_archive/ 仅在确有搬迁时创建（无事发生=零落盘）。
    """
    plan = build_report(queue_root, now=now, grace_days=grace_days)
    candidates = set(plan["orphan_candidates"]["shas"])
    refs, _ = _scan_refs(queue_root)  # 二次重扫：关掉"扫描后袋刚入队"竞态窗
    still_referenced: set[str] = set()
    for shas in refs.values():
        still_referenced |= shas
    race_skipped = sorted(candidates & still_referenced)
    to_move = sorted(candidates - still_referenced)
    moved: list[str] = []
    dst_exists: list[str] = []
    manifest_path = ""
    if to_move:
        archive_dir = queue_root / ARCHIVE_DIR
        archive_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = str(archive_dir / MANIFEST_NAME)
        run_id = f"blobgc-{now.strftime('%Y%m%dT%H%M%S%z')}-{os.getpid()}"
        for sha in to_move:
            src = queue_root / BLOBS_DIR / sha
            dst = archive_dir / sha
            if dst.exists():  # 上轮残留/他途已归档：跳过不覆盖
                dst_exists.append(sha)
                continue
            stat = src.stat()
            os.rename(src, dst)  # 同分区原子改名，无拷贝窗口
            record = {
                "action": "archive",
                "run_id": run_id,
                "sha": sha,
                "size_bytes": stat.st_size,
                "mtime": datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec="seconds"),
                "class": "orphan",
                "src_verdict": f"orphan&mtime>{grace_days:g}d",
                "grace_days": grace_days,
                "src_path": f"{BLOBS_DIR}/{sha}",
                "dst_path": f"{ARCHIVE_DIR}/{sha}",
                "archived_at": now.isoformat(timespec="seconds"),
            }
            with (archive_dir / MANIFEST_NAME).open("a", encoding="utf-8") as fh:  # 审计 jsonl 追加先例=purge_audit
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            moved.append(sha)
    plan["mode"] = "archive"
    plan["run"] = {
        "moved": moved,
        "skipped_race_refs": race_skipped,
        "skipped_dst_exists": dst_exists,
        "manifest": manifest_path,
    }
    return plan


def run_restore(manifest_path: Path, *, now: datetime) -> dict:
    """逆向恢复：按 manifest 反向 rename（blobs_archive/<sha> → blobs/<sha>），队列根锚定 manifest 自身位置。

    dst 已存在 → 跳过（内容寻址同 sha 同内容，覆盖无益）；两侧皆缺 → 计 missing（幻影先例，不中断）。
    """
    manifest_path = Path(manifest_path)
    if not manifest_path.is_file():
        raise FileNotFoundError(f"manifest 不存在: {manifest_path}")
    queue_root = manifest_path.resolve().parent.parent
    restored: list[str] = []
    already: list[str] = []
    missing: list[str] = []
    bad_lines = 0
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            bad_lines += 1
            continue
        sha = record.get("sha") if isinstance(record, dict) else None
        if not isinstance(record, dict) or record.get("action") != "archive" or not _is_sha(sha):
            bad_lines += 1
            continue
        src = queue_root / ARCHIVE_DIR / sha
        dst = queue_root / BLOBS_DIR / sha
        if dst.exists():
            already.append(sha)
        elif src.exists():
            os.rename(src, dst)
            restored.append(sha)
        else:
            missing.append(sha)
    audit_path = manifest_path.with_name(MANIFEST_NAME + ".restore.jsonl")
    summary = {
        "restored": restored,
        "already_at_source": already,
        "missing": missing,
        "bad_lines": bad_lines,
        "queue_root": str(queue_root),
    }
    record_out = {
        "action": "restore",
        "manifest": str(manifest_path),
        "restored_at": now.isoformat(timespec="seconds"),
        **summary,
    }
    with audit_path.open("a", encoding="utf-8") as fh:  # 还原动作同样留痕（旁挂文件，不污染原始 manifest 追加序）
        fh.write(json.dumps(record_out, ensure_ascii=False) + "\n")
    return record_out


def _fmt_mb(num_bytes: int) -> str:
    return f"{num_bytes / (1024 * 1024):.1f}MB"


def _print_human(report: dict) -> None:
    """人读输出（stdout；缺省永不落盘 .runtime）。"""
    print(
        f"[blob-gc] blobs GC 报告 — mode={report['mode']}  时点={report['generated_at']}  宽限期={report.get('grace_days', '-')}d"
    )
    print(f"[blob-gc] 队列根: {report['queue_root']}")
    buckets = report.get("buckets")
    if buckets:
        print("[blob-gc] 分桶（计数 / 字节）:")
        for key, item in buckets.items():
            if item["count"]:
                print(f"  {item['label']:<36} {item['count']:>6}  {_fmt_mb(item['bytes']):>10}")
        cand = report["orphan_candidates"]
        print(
            f"[blob-gc] 孤儿候选（orphan∧mtime>{report['grace_days']:g}d）: {cand['count']} 个 / {_fmt_mb(cand['bytes'])} — --archive 后挪 {ARCHIVE_DIR}/"
        )
    run = report.get("run")
    if run:
        print(
            f"[blob-gc] 已归档 {len(run['moved'])} 个；竞态重扫跳过 {len(run['skipped_race_refs'])}；dst 已存在跳过 {len(run['skipped_dst_exists'])}"
        )
        print(f"[blob-gc] manifest: {run['manifest'] or '(无搬迁未创建)'}")
    if "restored" in report:
        print(
            f"[blob-gc] 还原 {len(report['restored'])} 个；已在源位 {len(report['already_at_source'])}；两侧皆缺 {len(report['missing'])}；坏行 {report['bad_lines']}"
        )
        print(f"[blob-gc] 还原审计: {report['queue_root']}/{ARCHIVE_DIR}/{MANIFEST_NAME}.restore.jsonl")
    phantom = report.get("phantom_refs")
    if phantom is not None:
        print(f"[blob-gc] 幻影引用（JSON 引 blob 缺盘）: {len(phantom)} 个")
        scanned = report["scanned"]
        skipped = report["skipped"]
        print(
            f"[blob-gc] 扫描: 在盘 blob {scanned['blobs_on_disk']} | 被引 sha {scanned['referenced_shas']} | 坏袋 {skipped['bags']} / 坏行 {skipped['jsonl_lines']}"
        )
        for note in report["notes"]:
            print(f"[blob-gc] 注: {note}")


def main(argv: list[str] | None = None, *, queue_root: str | os.PathLike | None = None) -> int:
    """CLI 入口。默认 dry-run 零写；--archive 执行归档；--restore 逆向恢复。"""
    parser = argparse.ArgumentParser(description="blobs 归档式 GC（默认 dry-run；归档不删除）")
    parser.add_argument(
        "--archive", action="store_true", help="执行归档：孤儿∧mtime>宽限期 → 挪 blobs_archive/ + manifest 留痕"
    )
    parser.add_argument(
        "--grace-days",
        type=float,
        default=DEFAULT_GRACE_DAYS,
        help=f"mtime 宽限天数（默认 {DEFAULT_GRACE_DAYS:g}=done TTL 同节奏）",
    )
    parser.add_argument("--restore", metavar="MANIFEST", help="按 manifest 反向 rename 逆向恢复（互斥于 --archive）")
    parser.add_argument("--json", action="store_true", help="机器 JSON 输出（stdout，永不落盘 .runtime）")
    args = parser.parse_args(argv)
    if args.grace_days < 0:
        parser.error("--grace-days 必须 >= 0")
    now = datetime.now().astimezone()
    try:
        if args.restore:
            report = run_restore(Path(args.restore), now=now)
        else:
            root = Path(queue_root) if queue_root is not None else load_queue_resolver()(queue_root)
            report = (
                run_archive(root, now=now, grace_days=args.grace_days)
                if args.archive
                else build_report(root, now=now, grace_days=args.grace_days)
            )
    except FileNotFoundError as exc:
        print(f"[blob-gc] {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
