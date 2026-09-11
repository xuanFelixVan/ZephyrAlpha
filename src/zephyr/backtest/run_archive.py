# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.run_archive
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.engine_base; zephyr.shared.io.file_utils; zephyr.shared.io.paths
# [CONSUMERS] SOP-B 七步循环(VAL); SOP-C C4 快筛管道(SCREEN); 消融对照器(ABLATION); scripts/backtest/verify_run_archive.py
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] run 目录只增不改(修正走 errata.md); run_id 落盘即冻结三处一致; 文件名 ASCII-only; 目录与文件名由本 API 拼装——AI/runner 禁手 mkdir 手写路径(SOP-D §6); 同 object_id 禁双 run 并行(§9.6, best-effort)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RunArchiveError
# [TESTS] tests/backtest/test_run_archive.py
# [TTL] permanent
"""run 过程档案图书馆 API（SOP-D，R1 裁定：落盘必须是代码，不是自觉）。

规范真源：docs/01_policies_and_standards/sop/backtest_system_sop/sop_d_run_archive_naming.md
（图书馆三原则/位置地图/编号/目录结构/kind×文件矩阵/meta 字段/复现演练）。
裁定来源：docs/_working/2026-09-11-backtest-evidence-log-discussion.md §八 R1（Owner 2026-09-11 认可）。

落点：data/backtest_artifacts/runs/<run_id>/（gitignore 区，可重跑再生——
预注册阈值等结论可信度资产进 git 走 backtest_backlog.yaml，不放这里）。

四个核心函数（SOP-D §6 指定）：
    create_run()    开新书——建目录+写 meta.json（含 snapshot_commit，PB-06）
    write_step()    上架——写七步产物/判定书/errata，禁覆盖（只增不改）
    finalize_run()  归档——kind×必选文件矩阵校验（SOP-D §4）+ 台账回执绑定
    load_meta()     查书名页
辅助：
    log_iteration() 07_iteration_log 追加一节（只增不改的迭代留痕，喂 Deflated Sharpe）
    iter_run_ids()  遍历现有 run（巡检脚本消费）
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Final
from zoneinfo import ZoneInfo

from zephyr.shared.io.file_utils import content_sha256, safe_write_text
from zephyr.shared.io.paths import REPO_ROOT

_TZ_SH: Final = ZoneInfo("Asia/Shanghai")
_RUNS_ROOT: Final = REPO_ROOT / "data" / "backtest_artifacts" / "runs"

_KINDS: Final[tuple[str, ...]] = ("VAL", "BACKTEST", "SCREEN", "ABLATION")

# 固定名步骤 → 文件名（SOP-D §4 目录结构）
_STEP_FILES: Final = {
    "01": "01_survey.md",
    "02": "02_data_gap.yaml",
    "03": "03_data_manifest.yaml",
    "05": "05_prune_log.yaml",
    "07": "07_iteration_log.yaml",
    "verdict": "verdict.md",
    "errata": "errata.md",
    "replay": "08_replay.md",
}
# 大文件子目录步骤（文件名由调用方给，API 校验 ASCII）
_SUBDIR_STEPS: Final[dict[str, str]] = {"04": "04_wide", "06": "06_narrow", "assets": "assets"}

# kind × 必选步骤（SOP-D §4 矩阵；03/verdict 全 kind 必选）
_REQUIRED_STEPS: Final[dict[str, set[str]]] = {
    "VAL": {"01", "02", "03", "05", "06", "verdict"},
    "BACKTEST": {"01", "02", "03", "06", "verdict"},
    "SCREEN": {"03", "04", "verdict"},
    "ABLATION": {"03", "04", "verdict"},
}

_RUN_ID_RE: Final = re.compile(r"^(VAL|SCR|ABL)-[A-Za-z0-9._-]+$")
_ASCII_RE: Final = re.compile(r"^[\x21-\x7e]+$")   # 可打印 ASCII 且无空格
_FILENAME_FORBIDDEN: Final[tuple[str, ...]] = ("/", "\\", ":")
_FILENAME_RESERVED: Final[frozenset[str]] = frozenset({".", ".."})


class RunArchiveError(Exception):
    """run 档案 API 违规（命名/覆盖/缺必选/并发）。

    Args:
        message: 静态人话描述（禁内嵌路径/文件名等动态值——MSG-EXPOSURE 5.99.20）。
        details: 动态上下文（路径/文件名等）走此字段，不进消息文本。
    """

    error_code = "ZA-BTARCH-0001"

    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(message)
        self.details = details or {}


# ── 内部工具 ─────────────────────────────────────────────────────────────

def _runs_root(artifacts_root: Path | None = None) -> Path:
    return Path(artifacts_root) if artifacts_root else _RUNS_ROOT


def _run_dir(run_id: str, artifacts_root: Path | None = None) -> Path:
    if not run_id or not _RUN_ID_RE.match(run_id):
        raise RunArchiveError(
            f"run_id 非法: {run_id!r}（需前缀 VAL-|SCR-|ABL- + ASCII，SOP-D §3 编号规范）"
        )
    return _runs_root(artifacts_root) / run_id


def _meta_path(run_dir: Path) -> Path:
    return run_dir / "meta.json"


def _read_meta(run_dir: Path) -> dict[str, Any]:
    p = _meta_path(run_dir)
    if not p.exists():
        raise RunArchiveError(f"meta.json 缺失（无主档案）: {p}")
    try:
        _loaded = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(_loaded, dict):
            raise RunArchiveError("meta.json 顶层非对象（损坏/被篡改）", details={"path": str(p)})
        return _loaded
    except (OSError, json.JSONDecodeError) as exc:
        raise RunArchiveError(f"meta.json 不可读/损坏: {p}: {exc}") from exc


def _write_meta(run_dir: Path, meta: dict[str, Any]) -> None:
    p = _meta_path(run_dir)
    base = content_sha256(p.read_text(encoding="utf-8")) if p.exists() else None
    safe_write_text(p, json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                    expected_base_sha256=base, encoding="utf-8")


def _check_ascii_filename(filename: str) -> None:
    if not filename or not _ASCII_RE.match(filename):
        raise RunArchiveError(
            "文件名非 ASCII/含空格（SOP-D §3 铁律，中文进文件内容）",
            details={"filename": filename},
        )
    if (
        any(sep in filename for sep in _FILENAME_FORBIDDEN)
        or ".." in filename
        or filename in _FILENAME_RESERVED
        or filename.endswith((" ", "."))
        or filename.startswith(" ")
    ):
        raise RunArchiveError(
            "文件名含路径分隔符/父引用/Windows 保留尾字符（穿越防护）",
            details={"filename": filename},
        )

def create_run(  # noqa: long-param-list  公共 API 契约绑定（14 测试），签名重构另批
    run_id: str,
    object_id: str,
    kind: str,
    *,
    window: dict[str, str] | None = None,
    holdout: dict[str, Any] | None = None,
    cost_mode: str = "rough",
    map_effective_from: str | None = None,
    created_by: str | None = None,
    artifacts_root: Path | None = None,
    allow_concurrent: bool = False,
) -> Path:
    """开新书：建 run 目录 + meta.json（run_id 落盘即冻结）。

    Args:
        run_id: 全局唯一 id（VAL-|SCR-|ABL- 前缀，SOP-D §3）。
        object_id: backtest_backlog 对象 id（BT-<批次>-<序号>；老 run 允许空串）。
        kind: VAL | BACKTEST | SCREEN | ABLATION。
        window: {"start": ..., "end": ...}（业务窗口，Asia/Shanghai 墙钟日期）。
        holdout: {"mode": ..., "cutoff": ...} 保密考卷声明（PB-08）。
        cost_mode: rough | full（约束一成本口径）。
        allow_concurrent: 同 object_id 未归档 run 已存在时放行（逃生通道，默认禁）。

    Raises:
        RunArchiveError: 命名违规 / 目录已存在（冻结）/ 同对象未归档 run 在飞。
    """
    if kind not in _KINDS:
        raise RunArchiveError(f"kind 非法: {kind!r}（合法值 {'|'.join(_KINDS)}）")
    run_dir = _run_dir(run_id, artifacts_root)
    if run_dir.exists():
        raise RunArchiveError(f"run 目录已存在（run_id 落盘即冻结，禁复用）: {run_dir}")
    if not allow_concurrent and object_id:
        for other in _runs_root(artifacts_root).glob("*/meta.json"):
            try:
                m = json.loads(other.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue   # 损坏 meta 交由巡检脚本报告，此处不阻断
            if m.get("object_id") == object_id and m.get("steps", {}).get("verdict") != "done":
                raise RunArchiveError(
                    f"同 object_id={object_id} 存在未归档 run {other.parent.name}"
                    "（SOP-D §9.6 禁双 run 并行；确需并行用 allow_concurrent=True 并留痕）"
                )
    try:
        run_dir.mkdir(parents=True, exist_ok=False)
    except OSError as exc:
        raise RunArchiveError("run 目录创建失败（磁盘/权限/路径占用）",
                              details={"run_dir": str(run_dir), "reason": str(exc)}) from exc

    from zephyr.backtest.core.engine_base import current_map_snapshot

    meta: dict[str, Any] = {
        "run_id": run_id,
        "object_id": object_id,
        "kind": kind,
        "created_at": datetime.now(_TZ_SH).isoformat(timespec="seconds"),
        "created_by": created_by or "ai-session:unknown",
        "snapshot_commit": current_map_snapshot(),
        "map_effective_from": map_effective_from,
        "window": window or {},
        "holdout": holdout or {},
        "cost_mode": cost_mode,
        "attempts": 0,
        "steps": {},
        "verdict_ref": None,
        "linked_artifacts": [],
    }
    _write_meta(run_dir, meta)
    return run_dir


def write_step(
    run_id: str,
    step: str,
    content: str | bytes,
    *,
    filename: str | None = None,
    encoding: str = "utf-8",
    artifacts_root: Path | None = None,
) -> Path:
    """上架：写一步产物。固定名步骤（01/02/03/05/07/verdict/errata/replay）content 为文本；
    子目录步骤（04/06/assets）MUST 给 filename（ASCII），content 文本或字节。

    只增不改：目标已存在即拒绝——修正走 errata（write_step("errata", ...)），禁原地改写。
    """
    run_dir = _run_dir(run_id, artifacts_root)
    meta = _read_meta(run_dir)
    if step in _SUBDIR_STEPS:
        if not filename:
            raise RunArchiveError(f"子目录步骤 {step} 必须给 filename")
        _check_ascii_filename(filename)
        target = run_dir / _SUBDIR_STEPS[step] / filename
        if target.exists():
            raise RunArchiveError(
                "只增不改：目标产物已存在（修正走 errata.md，禁原地改写）",
                details={"target": str(target)},
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        _write_content(target, content, encoding)
        meta["steps"][step] = "done"
    elif step in _STEP_FILES:
        if filename is not None and filename != _STEP_FILES[step]:
            raise RunArchiveError(f"步骤 {step} 文件名固定为 {_STEP_FILES[step]}，禁改名")
        target = run_dir / _STEP_FILES[step]
        if target.exists():
            raise RunArchiveError(
                "只增不改：目标产物已存在（修正走 errata.md，禁原地改写）",
                details={"target": str(target)},
            )
        _write_content(target, content, encoding)
        meta["steps"][step] = "done"
    else:
        raise RunArchiveError(f"未知步骤: {step!r}（合法：{'|'.join(sorted(_STEP_FILES))} + {'|'.join(sorted(_SUBDIR_STEPS))}）")
    _write_meta(run_dir, meta)
    return target


def _write_content(target: Path, content: str | bytes, encoding: str) -> None:
    if isinstance(content, bytes):
        target.write_bytes(content)
    else:
        target.write_text(content, encoding=encoding, newline="\n")


def log_iteration(
    run_id: str,
    changed: str,
    why: str,
    result: str,
    kept: bool,
    *,
    artifacts_root: Path | None = None,
) -> int:
    """07_iteration_log 追加一节（文本级追加保只增不改），meta.attempts 同步 +1。

    Returns:
        追加后的轮次号（即 meta.attempts）。
    """
    run_dir = _run_dir(run_id, artifacts_root)
    meta = _read_meta(run_dir)
    target = run_dir / _STEP_FILES["07"]
    round_no = int(meta.get("attempts", 0)) + 1
    entry = (
        f"- round: {round_no}\n"
        f"  changed: \"{changed}\"\n"
        f"  why: \"{why}\"\n"
        f"  result: \"{result}\"\n"
        f"  kept: {bool(kept)}\n"
    )
    if target.exists():
        with target.open("a", encoding="utf-8", newline="\n") as f:
            f.write(entry)
    else:
        _write_content(target, entry, "utf-8")
    meta["attempts"] = round_no
    meta["steps"]["07"] = "done"
    _write_meta(run_dir, meta)
    return round_no


def finalize_run(
    run_id: str,
    *,
    verdict_ref: dict[str, str] | None = None,
    linked_artifacts: list[str] | None = None,
    artifacts_root: Path | None = None,
) -> dict[str, Any]:
    """归档：kind×必选文件矩阵校验（SOP-D §4）→ 绑定台账回执 → 冻结。

    迭代纪律：attempts>1 时 07_iteration_log 必选（多重检验计数器与留痕一致，
    喂 Deflated Sharpe 的原料，SOP-B 留痕铁律）。
    """
    run_dir = _run_dir(run_id, artifacts_root)
    meta = _read_meta(run_dir)
    kind = meta.get("kind", "")
    required = _REQUIRED_STEPS.get(kind, set())
    done = meta.get("steps", {})
    missing = sorted(s for s in required if done.get(s) != "done")
    if int(meta.get("attempts", 0)) > 1 and done.get("07") != "done":
        missing.append("07")
    if missing:
        raise RunArchiveError(
            f"归档校验失败（kind={kind}）缺必选产物: {missing}（结论必须能翻到过程，SOP-D §4）"
        )
    if verdict_ref:
        meta["verdict_ref"] = verdict_ref
    if linked_artifacts:
        meta["linked_artifacts"] = linked_artifacts
    meta["steps"]["verdict"] = "done"
    meta["finalized_at"] = datetime.now(_TZ_SH).isoformat(timespec="seconds")
    _write_meta(run_dir, meta)
    return meta


def load_meta(run_id: str, *, artifacts_root: Path | None = None) -> dict[str, Any]:
    """查书名页：读 meta.json（无主档案/损坏 → RunArchiveError）。"""
    return _read_meta(_run_dir(run_id, artifacts_root))


def iter_run_ids(*, artifacts_root: Path | None = None) -> list[str]:
    """遍历现有 run id（巡检脚本/复现演练抽样消费；按名排序确定性输出）。"""
    root = _runs_root(artifacts_root)
    if not root.exists():
        return []
    return sorted(p.name for p in root.iterdir() if p.is_dir() and _RUN_ID_RE.match(p.name))


__all__: Final[list[str]] = [
    "RunArchiveError",
    "create_run",
    "finalize_run",
    "iter_run_ids",
    "load_meta",
    "log_iteration",
    "write_step",
]
