#!/usr/bin/env python
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md | §quarantine_pack
# [MODULE] scripts.ops.quarantine_packer
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.io.audit_jsonl_writer (append_audit_jsonl 同款机制: 打包台账统一写面);
#                zephyr.shared.io.file_utils (safe_write_text, INDEX.md CAS 写);
#                zephyr.shared.utils.time_utils (now_utc, RULE-SCHEMA-TZ: 禁 datetime.now()/time.time() 生成时间戳)
# [CONSUMERS] process_reaper 既有扫描循环 wire（subprocess --once, 禁 cron/新常驻）; 人工手动触发
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 零删除语义=先 tar+gz 落 packs/ →逐文件 sha256 压前/压内比对全等（任一不符=删自建
#              pack 件零 rmtree，fail-closed）→才许移除原目录并留 README 指针（解压即复活）;
#              候选=一级子目录 mtime 超 mtime_days（出厂 90）——总量超 threshold_gib 但无候选时
#              只发 escalated 告警零动作（不动活跃面）; packs/ 自身与已 packed 的 README 指针壳
#              永不打包; INDEX.md 记 pack sha256+原/压体积（机生追加，safe_write_text CAS）;
#              逐 run manifest jsonl 留逐文件证据; 单目录失败不反噬整轮（errors 行内继续）;
#              enabled:false=全零动作（只报读数）
# [MODIFY-GUARD] config/flags.yaml flags.quarantine_pack（阈值真源，本件只读禁改）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] run_once 永不抛（OSError/tar 失败收入 errors 单目录跳过）;
#                  exit 0=完成（含零候选/禁用）; exit 1=超阈值无候选告警已发; exit 2=设施故障
#                  （quarantine 面不可读）
# [TESTS] tests/scripts/test_quarantine_packer.py（假 quarantine 树实测 pack 搬迁/校验失败回滚/候选两侧/禁用/dry-run）
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: one-shot 由 reaper 既有扫描循环/人工事件驱动（与 runtime_hygiene wire 同宿），
#                         非 cron/Timer/raw sleep-loop，本件零等待零轮询
# noqa: m11-perm-manual-legitimate  M11豁免: one-shot CLI 由 reaper wire/人工按需触发，非常驻服务/非 daemon/非自启
#
# create-guard-not-dup: 本模块只做 tar/文件字节面操作，不解析任何文件内容结构——命中词 parse 系
#                       INDEX.md markdown 表格行追加的散文碰撞，非 algo_flow_parse/file_header_parser
#                       的第二实现；_dir_size_bytes 与 nine_face_watch 内联版非同源（scripts/ 非
#                       import 面，os.walk 实现），提取级共享待有 src 宿主时收敛
"""quarantine_packer — .runtime/quarantine 陈旧子目录 tar+gz 归仓（st-diskp0 裁定③，零删除语义）。

病灶：.runtime/quarantine 只进不出（nine_face ⑤面），drift_* 取证目录沉积数十枚；
物理删除=NL-6 Owner 门位，但"陈旧证据整体搬 packs/ 仓+原位 README 指针"是**零信息损失**
的搬运（裁定③）：pack 内逐文件 sha256 与原件比对全等后才移除原目录，解压即复活。

触发与候选（config/flags.yaml flags.quarantine_pack：enabled 出厂 ON，threshold_gib=1.5，
mtime_days=90）：
    一级子目录 mtime 超 mtime_days → 打包候选（reason=mtime_over）；
    quarantine 总量 > threshold_gib 且无候选 → escalated 告警零动作（不动活跃面，Owner 门位）。

打包序（单目录，任一步败=该目录零动作）：
    ① packs/<name>.tar.gz 落盘（tmp 名→原子改名，arcname=<name>/... 解压得原目录）；
    ② 校验：成员集==原文件集（正斜杠相对路径）且逐文件 sha256(压缩包内解出)==sha256(原文件)；
    ③ 校验全等 → 移除原目录 → 原位留 <name>/README.md 指针（pack 名/sha256/原体积/复活命令）；
    ④ packs/pack_run_<utc>.manifest.jsonl 逐文件证据 + packs/INDEX.md packs 表/运行台账双追加。

部署：reaper wire（subprocess `--once`，dry_run 轮透传 `--dry-run`）或人工即时
    `python scripts/ops/quarantine_packer.py --once [--dry-run]`；禁 cron/新常驻。

# [ALGO_FLOW] external: docs/03_modules/_domain_infrastructure_operations/algo_flow/quarantine_packer.yaml
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tarfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from zephyr.shared.io.audit_jsonl_writer import append_audit_jsonl  # noqa: E402
from zephyr.shared.io.file_utils import safe_write_text  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

QUARANTINE_REL = Path(".runtime") / "quarantine"
AUDIT_DIR_REL = Path(".runtime") / "audit"
ALERT_DIR_REL = Path(".runtime") / "workspace_alerts"
LEDGER_FILENAME = "quarantine_packer.jsonl"
PACKS_DIRNAME = "packs"
INDEX_FILENAME = "INDEX.md"
README_FILENAME = "README.md"
README_MARKER = "quarantine-pack pointer"
STUB_SKIP_ENTRIES = frozenset({README_FILENAME})
_GIB = 1024**3


def read_quarantine_pack_config(repo_root: Path | str | None = None) -> tuple[bool, float, float]:
    """flags.quarantine_pack 配置读取唯一点（(enabled, threshold_gib, mtime_days)；缺=出厂 (True, 1.5, 90)）。

    单一真源=config/flags.yaml flags.quarantine_pack.*；缺席键回出厂值（禁复制字面量到消费方）。
    """
    root = Path(repo_root) if repo_root else _REPO_ROOT
    try:
        import yaml

        doc = yaml.safe_load((root / "config" / "flags.yaml").read_text(encoding="utf-8")) or {}
        cfg = (doc.get("flags") or {}).get("quarantine_pack") or {}
        return (
            bool(cfg.get("enabled", True)),
            float(cfg.get("threshold_gib") or 1.5),
            float(cfg.get("mtime_days") or 90.0),
        )
    except Exception:  # noqa: BLE001 — 配置设施异常回出厂值（fail-closed：缺配置不豁免触发闸）
        return True, 1.5, 90.0


def _dir_size_bytes(path: Path) -> int:
    """目录递归体积字节数（条目级 OSError 跳过不计——测量永不抛）。"""
    total = 0
    for dirpath, _dirnames, filenames in os.walk(path):
        for fn in filenames:
            try:
                total += (Path(dirpath) / fn).stat().st_size
            except OSError:
                continue
    return total


def _fmt_size(n: int) -> str:
    """字节数 → INDEX.md 人读格式（>1MiB 用 M，否则 K；与既有 compaction 台账同风格）。"""
    if n >= 1024 * 1024:
        return f"{n / 1024 / 1024:.2f}M"
    return f"{n / 1024:.2f}K"


def _sha256_file(path: Path) -> str:
    """文件 sha256（流式 1MiB 块）。"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _is_packed_stub(dir_path: Path) -> bool:
    """已打包指针壳判定：目录仅含 README.md 且内容含指针标记（再跑不重打包）。"""
    try:
        with os.scandir(dir_path) as it:
            entries = [e.name for e in it]
    except OSError:
        return False
    if not set(entries) <= STUB_SKIP_ENTRIES or README_FILENAME not in entries:
        return False
    try:
        return README_MARKER in (dir_path / README_FILENAME).read_text(encoding="utf-8")
    except OSError:
        return False


def scan_candidates(
    quarantine_dir: Path,
    *,
    threshold_gib: float,
    mtime_days: float,
    now_ts: float | None = None,
) -> dict:
    """quarantine 面只读扫描（总量/超阈值/超龄候选；errors 行内继续，永不抛）。"""
    ts = now_ts if now_ts is not None else now_utc().timestamp()
    errors: list[str] = []
    total = _dir_size_bytes(quarantine_dir) if quarantine_dir.exists() else 0
    candidates: list[dict] = []
    overview: dict = {
        "total_bytes": total,
        "total_gib": round(total / _GIB, 3),
        "over_threshold": (total / _GIB) > threshold_gib,
        "candidates": candidates,
        "errors": errors,
    }
    try:
        with os.scandir(quarantine_dir) as it:
            entries = sorted(it, key=lambda e: e.name)
    except OSError as e:
        overview["errors"] = errors + [f"quarantine_unreadable: {e}"]
        return overview
    for entry in entries:
        if not entry.is_dir(follow_symlinks=False) or entry.name == PACKS_DIRNAME:
            continue
        dpath = Path(entry.path)
        if _is_packed_stub(dpath):
            continue
        try:
            mtime = entry.stat(follow_symlinks=False).st_mtime
        except OSError as e:
            errors.append(f"stat_failed: {entry.name}: {e}")
            continue
        age_days = max(0.0, (ts - mtime) / 86400.0)
        if age_days > mtime_days:
            candidates.append(
                {
                    "name": entry.name,
                    "path": str(dpath),
                    "age_days": round(age_days, 2),
                    "size_bytes": _dir_size_bytes(dpath),
                    "reason": "mtime_over",
                }
            )
    return overview


def _verify_pack(pack_path: Path, src_dir: Path, name: str) -> tuple[bool, str | None]:
    """零删除核心闸：pack 成员集==原文件集 且 逐文件 sha256 压内解出==原文件（全等才放行）。"""
    src_files: dict[str, Path] = {}
    for dirpath, _dirnames, filenames in os.walk(src_dir):
        for fn in filenames:
            fpath = Path(dirpath) / fn
            rel = fpath.relative_to(src_dir).as_posix()
            src_files[f"{name}/{rel}"] = fpath
    try:
        with tarfile.open(pack_path, "r:gz") as tf:
            members = {m.name for m in tf.getmembers() if m.isfile()}
            if members != set(src_files):
                missing = sorted(set(src_files) - members)[:5]
                extra = sorted(members - set(src_files))[:5]
                return False, f"成员集不符（缺 {missing} 多 {extra}）"
            for arcname, fpath in src_files.items():
                src_hash = _sha256_file(fpath)
                inner = tf.extractfile(arcname)
                if inner is None:
                    return False, f"{arcname}: 成员不可读"
                h = hashlib.sha256()
                for chunk in iter(lambda: inner.read(1024 * 1024), b""):
                    h.update(chunk)
                if h.hexdigest() != src_hash:
                    return False, f"{arcname}: sha256 压前/压内不符"
    except (tarfile.TarError, OSError) as e:
        return False, f"pack 读验失败: {e}"
    return True, None


def _write_pointer_readme(dir_path: Path, info: dict) -> bool:
    """原位 README 指针（解压即复活语义；零删除的另一半=入口永不消失）。"""
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        lines = [
            f"<!-- {README_MARKER}: packed={info['pack_name']} sha256={info['pack_sha256']} -->",
            "",
            f"# 本目录已归仓：{info['pack_name']}",
            "",
            f"- 原路径: {info['orig_rel']}",
            f"- 打包时间: {info['ts']}",
            f"- 原体积: {_fmt_size(info['orig_bytes'])}（{info['file_count']} 文件）",
            f"- 压后体积: {_fmt_size(info['pack_bytes'])}",
            f"- pack sha256: `{info['pack_sha256']}`",
            f"- 逐文件证据: {info['manifest_name']}",
            "",
            "复活命令（在仓库根执行）：",
            "",
            "```",
            f"tar -xzf .runtime/quarantine/packs/{info['pack_name']} -C .runtime/quarantine",
            "```",
            "",
            "零删除语义：pack 已逐文件 sha256 比对全等后才移除原目录；本 README 为机生指针，勿手改。",
            "",
        ]
        (dir_path / README_FILENAME).write_text("\n".join(lines), encoding="utf-8")
        return True
    except OSError:
        return False


_INDEX_HEADER = """# quarantine packs INDEX（机生，勿手改）

- generator: scripts/ops/quarantine_packer.py（st-diskp0-20261015 裁定③ 接线）
- policy: 一级子目录 mtime 超 flags.quarantine_pack.mtime_days（出厂 90 天）→ 整体 tar+gz 归入
  packs/，原目录留 README 指针；零删除（pack 前逐文件 sha256 压前/压内比对全等），解压即可复活。
- 触发补充：quarantine 总量超 threshold_gib（出厂 1.5GiB）但无超龄候选时只发告警零动作。

## packs（pack 名 | 原路径 | 原体积 | 压后体积 | sha256）

| pack | 原路径 | 原体积 | 压后体积 | sha256 |
|---|---|---|---|---|
_(空——尚无超龄目录满足 pack 条件；后续运行由生成器追加)_

## 运行台账（机生追加）

| run | 动作 | 对象 | 文件数 | 原体积 | 压后体积 | 压缩比 | 明细 |
|---|---|---|---|---|---|---|---|
"""


def _insert_table_row(lines: list[str], header_prefix: str, row: str, errors: list[str]) -> list[str]:
    """markdown 表格行机生追加（定位 header→分隔线→吞既有行后插入；占位行删除；找不到=报错不动）。"""
    for i, ln in enumerate(lines):
        if not ln.startswith(header_prefix):
            continue
        j = i + 1
        if j < len(lines) and lines[j].startswith("|--"):
            j += 1  # 分隔线
        k = j
        while k < len(lines) and lines[k].lstrip().startswith("|"):
            k += 1  # 既有数据行
        kept = [x for x in lines if not x.lstrip().startswith("_（空——尚无")]
        at = k - (len(lines) - len(kept))  # 占位删除后的插入位平移
        return kept[:at] + [row] + kept[at:]
    errors.append(f"INDEX.md 表定位失败（{header_prefix[:20]}…），行未追加（pack 本体与 manifest 已留证）")
    return lines


def _append_index(index_path: Path, pack_rows: list[str], run_rows: list[str], errors: list[str]) -> bool:
    """INDEX.md packs 表+运行台账双追加（safe_write_text CAS；缺文件=按标准头初始化）。永不抛。"""
    try:
        if index_path.exists():
            content = index_path.read_text(encoding="utf-8")
            base: str | None = hashlib.sha256(content.encode("utf-8")).hexdigest()
        else:
            index_path.parent.mkdir(parents=True, exist_ok=True)
            content = _INDEX_HEADER
            base = None  # 新件无 base 可校验（非热区，CAS 从本轮读面起算）
        lines = content.splitlines()
        for row in pack_rows:
            lines = _insert_table_row(lines, "| pack | 原路径 |", row, errors)
        for row in run_rows:
            lines = _insert_table_row(lines, "| run | 动作 |", row, errors)
        new_content = "\n".join(lines).rstrip("\n") + "\n"
        if new_content == content:
            return True  # 幂等重入
        return bool(safe_write_text(index_path, new_content, expected_base_sha256=base))
    except Exception as e:  # noqa: BLE001 — INDEX 写失败不反噬搬运本体（pack+manifest 已留证）
        errors.append(f"INDEX_write_failed: {e}")
        return False


def pack_one(
    quarantine_dir: Path,
    name: str,
    *,
    dry_run: bool = False,
    run_stamp: str | None = None,
) -> dict:
    """单目录打包（tar+gz→校验→移除→指针→manifest；任一步败=原目录零动作）。永不抛。"""
    out: dict = {"name": name, "action": "packed", "dry_run": bool(dry_run)}
    try:
        src_dir = quarantine_dir / name
        packs_dir = quarantine_dir / PACKS_DIRNAME
        pack_path = packs_dir / f"{name}.tar.gz"
        out["pack"] = str(pack_path)
        if pack_path.exists():
            out["action"] = "skipped_already_packed"
            return out
        files: list[Path] = [p for p in sorted(src_dir.rglob("*")) if p.is_file()]
        orig_bytes = sum(p.stat().st_size for p in files)
        out.update(orig_bytes=orig_bytes, file_count=len(files))
        if dry_run:
            out["action"] = "would_pack"
            return out
        packs_dir.mkdir(parents=True, exist_ok=True)
        stamp = run_stamp or now_utc().strftime("%Y%m%dT%H%M%SZ")
        manifest_path = packs_dir / f"pack_run_{stamp}.manifest.jsonl"
        tmp_pack = packs_dir / f".{name}.tar.gz.tmp"
        try:
            with tarfile.open(tmp_pack, "w:gz") as tf:
                for fpath in files:
                    tf.add(fpath, arcname=f"{name}/{fpath.relative_to(src_dir).as_posix()}")
            os.replace(tmp_pack, pack_path)
        except (tarfile.TarError, OSError) as e:
            tmp_pack.unlink(missing_ok=True)
            out["action"] = "failed_create"
            out["error"] = str(e)[:200]
            return out
        ok, verr = _verify_pack(pack_path, src_dir, name)
        if not ok:
            pack_path.unlink(missing_ok=True)  # 自建坏件清场（原目录从未动）
            out["action"] = "failed_verify"
            out["error"] = verr
            return out
        pack_bytes = pack_path.stat().st_size
        pack_sha = _sha256_file(pack_path)
        try:  # manifest 逐文件证据（写失败不阻断搬运——pack 已验真，损失记 error 由调用方上报）
            rows = [
                json.dumps(
                    {
                        "run": stamp,
                        "pack": f"{name}.tar.gz",
                        "pack_sha256": pack_sha,
                        "orig_rel": f".runtime/quarantine/{name}",
                        "orig_bytes": orig_bytes,
                        "file_count": len(files),
                    },
                    ensure_ascii=False,
                )
            ]
            rows.extend(
                json.dumps(
                    {"path": p.relative_to(src_dir).as_posix(), "size": p.stat().st_size, "sha256": _sha256_file(p)},
                    ensure_ascii=False,
                )
                for p in files
            )
            manifest_path.write_text("\n".join(rows) + "\n", encoding="utf-8")
        except OSError as e:
            out["error"] = f"manifest_write_failed: {e}"
        try:
            shutil.rmtree(src_dir)
        except OSError as e:
            out["action"] = "failed_remove"
            out["error"] = (out.get("error") or "") + f" rmtree 失败（原目录保留+pack 已归仓=双份零损失）: {e}"
            return out
        info = {
            "pack_name": f"{name}.tar.gz",
            "pack_sha256": pack_sha,
            "orig_rel": f".runtime/quarantine/{name}",
            "ts": now_utc().isoformat(),
            "orig_bytes": orig_bytes,
            "file_count": len(files),
            "pack_bytes": pack_bytes,
            "manifest_name": manifest_path.name,
        }
        if not _write_pointer_readme(src_dir, info):
            out["error"] = (out.get("error") or "") + " README 指针写失败（pack 已归仓，入口暂缺需人工补）"
        out.update(pack_bytes=pack_bytes, pack_sha256=pack_sha, manifest=str(manifest_path))
        return out
    except Exception as e:  # noqa: BLE001 — 单目录任何意外=该目录零动作，不反噬整轮
        out["action"] = "failed_exception"
        out["error"] = f"{type(e).__name__}: {e}"[:300]
        return out


def run_once(
    *,
    repo_root: Path | str | None = None,
    dry_run: bool = False,
    quarantine_dir: Path | None = None,
    audit_dir: Path | None = None,
    alert_dir: Path | None = None,
    mtime_days: float | None = None,
    threshold_gib: float | None = None,
    note: str | None = None,
) -> tuple[dict, list[str]]:
    """一轮 quarantine 打包器（默认入口）：配置→扫描→逐候选打包→超阈值无候选告警。永不抛。"""
    root = Path(repo_root) if repo_root else _REPO_ROOT
    qdir = Path(quarantine_dir) if quarantine_dir else root / QUARANTINE_REL
    audits = Path(audit_dir) if audit_dir else root / AUDIT_DIR_REL
    alerts = Path(alert_dir) if alert_dir else root / ALERT_DIR_REL
    errors: list[str] = []
    enabled, cfg_threshold, cfg_days = read_quarantine_pack_config(root)
    days_gate = float(mtime_days) if mtime_days is not None else cfg_days
    threshold = float(threshold_gib) if threshold_gib is not None else cfg_threshold
    summary: dict = {
        "action": "patrolled",
        "enabled": enabled,
        "threshold_gib": threshold,
        "mtime_days": days_gate,
        "total_gib": None,
        "over_threshold": False,
        "candidates": 0,
        "packed": 0,
        "alerted": 0,
        "errors": errors,
        "dry_run": bool(dry_run),
        "alert_file": None,
    }
    if note:
        summary["note"] = note
    scan = scan_candidates(qdir, threshold_gib=threshold, mtime_days=days_gate)
    errors.extend(scan["errors"])
    summary["total_gib"] = scan["total_gib"]
    summary["over_threshold"] = scan["over_threshold"]
    summary["candidates"] = len(scan["candidates"])
    if "quarantine_unreadable" in " ".join(scan["errors"]):
        summary["action"] = "error"
        return summary, errors
    if not enabled:
        summary["action"] = "disabled"
        return summary, errors
    stamp = now_utc().strftime("%Y%m%dT%H%M%SZ")
    pack_rows: list[str] = []
    run_rows: list[str] = []
    for cand in scan["candidates"]:
        r = pack_one(qdir, cand["name"], dry_run=dry_run, run_stamp=stamp)
        if r["action"] == "packed":
            summary["packed"] += 1
            pack_rows.append(
                f"| {cand['name']}.tar.gz | .runtime/quarantine/{cand['name']} "
                f"| {_fmt_size(r['orig_bytes'])} | {_fmt_size(r['pack_bytes'])} | {r['pack_sha256']} |"
            )
            run_rows.append(
                f"| {stamp} | pack+migrate | .runtime/quarantine/{cand['name']} | {r['file_count']} "
                f"| {_fmt_size(r['orig_bytes'])} | {_fmt_size(r['pack_bytes'])} "
                f"| {r['orig_bytes'] / max(1, r['pack_bytes']):.1f}x | {Path(r['manifest']).name} |"
            )
        if r.get("error"):
            errors.append(f"{cand['name']}: {r['error']}")
        row = {
            "ts": now_utc().isoformat(),
            "by": "scripts.ops.quarantine_packer",
            "event": "quarantine_dir_packed" if r["action"] == "packed" else r["action"],
            "dir": cand["name"],
            "age_days": cand["age_days"],
            "orig_bytes": r.get("orig_bytes"),
            "pack_bytes": r.get("pack_bytes"),
            "pack_sha256": r.get("pack_sha256"),
            "dry_run": bool(dry_run),
        }
        if not dry_run and not append_audit_jsonl(Path(audits), LEDGER_FILENAME, row):
            errors.append(f"{cand['name']} 台账写失败")
    if scan["over_threshold"] and not scan["candidates"]:
        summary["alerted"] = 1
        if not dry_run:
            record = {
                "ts": now_utc().isoformat(),
                "by": "scripts.ops.quarantine_packer",
                "event": "quarantine_over_threshold_no_candidate",
                "severity": "escalated",
                "total_gib": scan["total_gib"],
                "threshold_gib": threshold,
                "mtime_days": days_gate,
                "note": "quarantine 超阈值但零超龄候选——活跃面不动（零动作）；处置=Owner 门位",
                "recover": "核对活跃取证面后人工决定：tar 归仓或按裁定放行退役",
            }
            try:
                alerts.mkdir(parents=True, exist_ok=True)
                path = alerts / f"quarantine_pack_{stamp}.json"
                path.write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
                summary["alert_file"] = str(path)
            except OSError:
                errors.append("告警件写失败（台账/summary 已留证）")
            append_audit_jsonl(Path(audits), LEDGER_FILENAME, record)
    if pack_rows or run_rows:
        _append_index(qdir / PACKS_DIRNAME / INDEX_FILENAME, pack_rows, run_rows, errors)
    return summary, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="quarantine 陈旧子目录 tar+gz 归仓（零删除语义，解压即复活）")
    parser.add_argument("--once", action="store_true", help="单轮即时执行（reaper wire 调用形态）")
    parser.add_argument("--dry-run", action="store_true", help="只扫零写（零 pack/零 rmtree/零台账/零告警）")
    parser.add_argument("--mtime-days", type=float, default=None, help="覆盖 flags.quarantine_pack.mtime_days（单轮）")
    parser.add_argument(
        "--threshold-gib", type=float, default=None, help="覆盖 flags.quarantine_pack.threshold_gib（单轮）"
    )
    parser.add_argument("--note", dest="note", default=None, help="本轮备注（写入台账行）")
    args = parser.parse_args(argv)
    summary, errors = run_once(
        dry_run=args.dry_run,
        mtime_days=args.mtime_days,
        threshold_gib=args.threshold_gib,
        note=args.note,
    )
    prefix = "[QUARANTINE-PACK] dry-run " if args.dry_run else "[QUARANTINE-PACK] "
    print(
        f"{prefix}action={summary['action']} enabled={summary['enabled']} total={summary['total_gib']}GiB "
        f"over_threshold={summary['over_threshold']} candidates={summary['candidates']} "
        f"packed={summary['packed']} alerted={summary['alerted']} "
        f"mtime_days={summary['mtime_days']} threshold_gib={summary['threshold_gib']}"
    )
    if summary.get("alert_file"):
        print(f"[QUARANTINE-PACK] 超阈值无候选告警件: {summary['alert_file']}")
    for e in errors:
        print(f"[QUARANTINE-PACK] error: {e}", file=sys.stderr)
    if summary["action"] == "error":
        return 2
    return 1 if summary["alerted"] else 0


if __name__ == "__main__":
    sys.exit(main())
