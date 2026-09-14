# -*- coding: utf-8 -*-
# [A_module] module_id=MOD-GOV_DEAD_QUEUE_RETIREMENT_RECONCILER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_RECONCILIATION_REGISTRY | docs/03_modules/_governance/reconciliation_registry/blueprint.md | §post-commit
# [MODULE] zephyr.governance.audit.dead_queue_retirement_reconciler
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/governance/audit/test_dead_queue_retirement_reconciler.py
# [TTL] permanent
"""dead_queue_retirement_reconciler — dead/ 提交队列死信季度退役审计（C 项，Owner 批准 2026-09-15）。

对账契约（红蓝 v5 报告 §4 设计稿 → 施工）：
- 事件触发：post-commit 链内由 ReconciliationRegistry.reconcile_for 派发（禁 cron/Timer，
  宪法 §9.3 永久系统四要素）；trigger=commit触及 .runtime/commit_queue/** 或本模块。
- 机械三分类（逐 dead 项、逐 file，无人工判读）：
  ① content_landed   — blob_sha256 == git show HEAD:<path> 的 sha256（内容已在 HEAD）
  ② landed_elsewhere — HEAD 后该 path 有晚于 dead_at 的提交记录（后续提交已接管）
  ③ superseded_or_dropped — 其余（文件消失且无后续提交=方案废弃，保留为历史证据）
- 输出：docs/_working/dead_queue/retirement_audit.json（字段化计数+清单，
  宪法 §4.3 禁散文计数）+ ReconcileResult(warn) 摘要。
- 净零预算：本 reconciler 替代手工归因流程，不新增常驻规则（v5 §4.6）。
- 安全边界：只读 git 元数据+读 dead/*.json；不删除、不改队列状态（物理清理归 Owner，
  AI 删除权受限——2026-09-14 Owner 令）。
"""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from zephyr.governance.audit.reconciliation_registry import ReconcileResult, ReconcilerSpec

logger = logging.getLogger(__name__)

_GATE_ID = "DEAD-QUEUE-RETIREMENT"
_PRIORITY = 795  # workspace_hygiene(≈800) 之前、git_performance(≈810) 之后；审计类不抢阻断位
_MAX_DETAIL_ITEMS = 6
_AUDIT_DIR = "docs/_working/dead_queue"
_AUDIT_FILE = "retirement_audit.json"
_TRIGGER_PREFIXES = (".runtime/commit_queue/", "src/zephyr/governance/audit/dead_queue_retirement_reconciler.py")
_REPORT_FRESH_SECONDS = 24 * 3600.0  # 报告新鲜期：24h 内不重跑（季庭审计语义+性能护栏）
_MAX_ITEMS_PER_RUN = 200  # 单次最多审计条数（超限留待下一窗口，防单次 post-commit 长时阻塞）
_DED_CLASSIFIED = ("content_landed", "landed_elsewhere", "superseded_or_dropped")


@dataclass
class _FileVerdict:
    path: str
    verdict: str
    detail: str


def _git_show_head(project_root: Path, path: str) -> bytes | None:
    """HEAD:<path> 内容；路径在 HEAD 不存在返回 None。"""
    try:
        r = subprocess.run(
            ["git", "show", f"HEAD:{path}"],
            cwd=str(project_root),
            capture_output=True,
            timeout=30,
        )
        return r.stdout if r.returncode == 0 else None
    except Exception:  # noqa: BLE001 — git 不可达按未落地处理
        return None


def _git_object_id(project_root: Path, path: str) -> str | None:
    """HEAD:<path> 的 git object id（rev-parse）；免疫 autocrlf/行尾转换，HEAD 无该文件返回 None。"""
    try:
        r = subprocess.run(
            ["git", "rev-parse", f"HEAD:{path}"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=30,
        )
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:  # noqa: BLE001 — git 不可达按未落地处理
        return None


def _worktree_object_id(project_root: Path, path: str) -> str | None:
    """工作区同路径文件的 git object id（hash-object，只读不写对象库）；文件不存在返回 None。"""
    fp = project_root / path
    if not fp.is_file():
        return None
    try:
        r = subprocess.run(
            ["git", "hash-object", path],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=30,
        )
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:  # noqa: BLE001
        return None


def _landed_after(project_root: Path, dead_at: str, path: str) -> bool:
    """dead_at 之后 path 是否有后续提交（内容由其他提交接管=landed_elsewhere 证据）。"""
    try:
        r = subprocess.run(
            ["git", "log", "--oneline", "-1", "--since", (dead_at or "1970-01-01T00:00:00")[:19], "--", path],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        return bool(r.stdout.strip())
    except Exception:  # noqa: BLE001
        return False


def _classify_item(project_root: Path, item: dict) -> list[_FileVerdict]:
    """单 dead 项 → 逐文件三分类判定（机械规则，禁人工判读）。"""
    verdicts: list[_FileVerdict] = []
    dead_at = str(item.get("dead_at") or item.get("created_at") or "")
    for fi in item.get("files") or []:
        path = str(fi.get("path", ""))
        if not path:
            continue
        # 判定链（机械三分类，对齐 v5 报告 §4.3 设计稿）：
        # ① blob_sha256（enqueue 时工作区原始字节 hash，真源口径）== 当前工作区同路径文件字节
        #    → content_landed（死信内容原样在盘，未丢未改）
        # ② HEAD 无该文件 → superseded_or_dropped（文件已出库且死信内容未接管）
        # ③ dead_at 后 path 有后续提交 → landed_elsewhere（内容被后续提交演化接管）
        # ④ 其余 → superseded_or_dropped（diverged）
        # 注：不用「HEAD oid == worktree oid」做 content_landed——那只证明工作区 clean，
        # 不能证明死信内容已落地（死信内容可能已被覆盖，v5 施工诊断 c1_diag_le2 实证）。
        want_sha = str(fi.get("blob_sha256") or "")
        fp = project_root / path
        if want_sha and fp.is_file() and hashlib.sha256(fp.read_bytes()).hexdigest() == want_sha:
            verdicts.append(_FileVerdict(path, "content_landed", "blob_sha256 == worktree bytes"))
            continue
        head_oid = _git_object_id(project_root, path)
        if head_oid is None:
            verdicts.append(_FileVerdict(path, "superseded_or_dropped", "gone at HEAD"))
            continue
        if _landed_after(project_root, dead_at, path):
            verdicts.append(_FileVerdict(path, "landed_elsewhere", "path committed after dead_at"))
        else:
            verdicts.append(_FileVerdict(path, "superseded_or_dropped", "diverged, no post-dead commit"))
    return verdicts


def _report_fresh(project_root: Path, max_age_s: float) -> bool:
    """审计报告在 max_age_s 内生成过 → 本次 skip（季庭审计语义：非每次 commit 都全量跑）。

    护栏理由：956 条 dead 项全量扫描 ≈ O(条目×文件数) 个 git 子进程（v5 施工抽样实测
    40 条 353s，全量推算 2.3h）——无节流会堵塞 post-commit 链。报告 24h 内新鲜即跳过。
    """
    p = project_root / _AUDIT_DIR / _AUDIT_FILE
    if not p.is_file():
        return False
    try:
        age = time.time() - p.stat().st_mtime
        return age < max_age_s
    except OSError:
        return False


def _run_audit(project_root: Path) -> dict:
    """全量扫 dead/*.json → 三分类 → 写 retirement_audit.json（safe_write_text CAS）。"""
    dead_dir = project_root / ".runtime" / "commit_queue" / "dead"
    items: list[dict] = []
    truncated = False
    if dead_dir.is_dir():
        all_paths = sorted(dead_dir.glob("*.json"))
        if len(all_paths) > _MAX_ITEMS_PER_RUN:
            all_paths = all_paths[:_MAX_ITEMS_PER_RUN]
            truncated = True
        for p in all_paths:
            try:
                items.append(json.loads(p.read_text(encoding="utf-8")))
            except Exception:  # noqa: BLE001 — 单条损坏不拖垮整体
                items.append({"qid": p.stem, "dead_reason": "unparseable", "files": []})

    counts = {k: 0 for k in _DED_CLASSIFIED}
    counts["empty_items"] = 0
    classified_qids: dict[str, list[str]] = {k: [] for k in _DED_CLASSIFIED}
    file_verdicts: list[dict] = []
    for item in items:
        vlist = _classify_item(project_root, item)
        if not vlist:
            counts["empty_items"] += 1
            continue
        qid = str(item.get("qid", "?"))
        # 项级判定=最乐观文件判定（任一文件 content_landed/landed_elsewhere 即视为已收敛）
        q_verdict = "superseded_or_dropped"
        for v in vlist:
            if v.verdict in ("content_landed", "landed_elsewhere"):
                q_verdict = v.verdict
                break
        counts[q_verdict] += 1
        classified_qids[q_verdict].append(qid)
        for v in vlist:
            file_verdicts.append({"qid": qid, "path": v.path, "verdict": v.verdict, "detail": v.detail})

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_items": len(items),
        "truncated_to_limit": truncated,
        "counts": counts,
        "owner_cleanable_qids": classified_qids["content_landed"] + classified_qids["landed_elsewhere"],
        "keep_evidence_qids": classified_qids["superseded_or_dropped"],
        "file_verdicts": file_verdicts[:500],  # 上限防失控（detail 截断由调用方展示层负责）
        "note": "物理清理移交 Owner（AI 删除权受限）；本报告为季度退役审计输入",
    }

    out_dir = project_root / _AUDIT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / _AUDIT_FILE
    try:
        from zephyr.shared.io.file_utils import safe_write_text

        safe_write_text(out_path, json.dumps(report, ensure_ascii=False, indent=1), repo_root=project_root)
    except Exception as e:  # noqa: BLE001 — 写报告失败降级 warn（不阻断 commit 链）
        logger.warning("dead_queue_retirement: report write failed: %s", e)
        report["write_error"] = str(e)
    return report


def make_dead_queue_retirement_reconciler(gateway: "object") -> ReconcilerSpec:
    """Construct DEAD-QUEUE-RETIREMENT post-commit 季度退役审计 reconciler。

    Args:
        gateway: GitCommitGateway 实例（仅用其 project_root）。

    Returns:
        ReconcilerSpec(gate_id, trigger, reconcile, priority=795, file_ops=read+write)。
        trigger：commit 触及 commit_queue 元数据或本模块时执行。
    """
    project_root = Path(gateway.project_root)

    def _trigger(committed_files: list[str]) -> bool:
        return any(f.startswith(_TRIGGER_PREFIXES) for f in committed_files)

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        try:
            if _report_fresh(project_root, _REPORT_FRESH_SECONDS):
                return ReconcileResult(
                    action="skip",
                    detail=f"retirement audit report fresh (<{_REPORT_FRESH_SECONDS / 3600:.0f}h)，跳过本轮（季庭审计节流）",
                    gate_id=_GATE_ID,
                )
            report = _run_audit(project_root)
            counts = report.get("counts", {})
            cleanable = len(report.get("owner_cleanable_qids", []))
            total = report.get("total_items", 0)
            if total == 0:
                return ReconcileResult(action="clean", detail="dead queue empty", gate_id=_GATE_ID)
            sample = counts.get("content_landed", 0), counts.get("landed_elsewhere", 0), counts.get("superseded_or_dropped", 0)
            detail = (
                f"dead/ 退役审计: total={total} content_landed={sample[0]} "
                f"landed_elsewhere={sample[1]} superseded_or_dropped={sample[2]} "
                f"owner_cleanable={cleanable}（物理清理移交 Owner）；报告={_AUDIT_DIR}/{_AUDIT_FILE}"
            )
            items = [detail]
            if len(items) > _MAX_DETAIL_ITEMS:  # pragma: no cover — 防御分支
                items = items[:_MAX_DETAIL_ITEMS]
            return ReconcileResult(action="warn", detail="; ".join(items), gate_id=_GATE_ID)
        except Exception as e:  # noqa: BLE001 — reconciler 永不抛异常
            logger.warning("dead_queue_retirement: reconcile failed: %s", e)
            return ReconcileResult(action="warn", detail=f"dead_queue_retirement error: {e}", gate_id=_GATE_ID)

    return ReconcilerSpec(
        gate_id=_GATE_ID,
        trigger=_trigger,
        reconcile=_reconcile,
        priority=_PRIORITY,
        file_ops=frozenset({"read", "write"}),
    )
