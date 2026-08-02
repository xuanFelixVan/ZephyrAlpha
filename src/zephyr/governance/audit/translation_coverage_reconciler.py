# [BLUEPRINT] MOD-GOV_TRANSLATION_COVERAGE_RECONCILER | docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml | §TRANSLATION-COVERAGE
# [MODULE] zephyr.governance.audit.translation_coverage_reconciler
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcileResult, ReconcilerSpec); zephyr.governance.depgraph_schema (get_depgraph_pg_connection); zephyr.shared.io.paths (REPO_ROOT); scripts.governance._shared.module_translation_loader (get_module_translation, is_generic_plain_zh, is_generic_plain_suffix)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] post-commit 事件触发（src/*.py 或 scripts/*.py commit）；reconciler 永不抛异常；warn-only（漂移不阻断 commit，仅告警+落盘报告供追踪）；DB/loader 不可达 fail-open；只读扫描（不写 DB/YAML）
# [MODIFY-GUARD] _GATE_ID / _PRIORITY / _MIN_CJK / _DRIFT_REPORT_PATH
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] reconcile 永不抛异常——DB/loader/IO 异常降级为 ReconcileResult(action="warn")
# [TESTS] tests/governance/audit/test_translation_coverage_reconciler.py
# [A_module] module_id=MOD-GOV_TRANSLATION_COVERAGE_RECONCILER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: reconciler 是 commit 事件触发(非 cron/manual)

"""translation_coverage_reconciler.py — 翻译覆盖率存量对账 reconciler.

TRANSLATION-COVERAGE 四层防御的 Layer 4（post-commit 存量对账）：扫描 depgraph 全部
节点（有 file_path 且在 src/zephyr/ 或 scripts/ 范围内）vs 翻译真源
``module_translation_registry.yaml``，生成 ``missing_plain`` / ``short_plain`` /
``generic_plain`` 三类漂移报告，落盘到 ``.runtime/translation_coverage/drift_report.json``。

治本动机（第一性原理）
--------------------
Layer 1（apply_depgraph 登记时 warn）+ Layer 2（提交时 gate 阻断）+ Layer 3（is_generic
质量检测）只管"新增模块"。存量 8324 条目中仍可能因 reconciler 回退、手工编辑、批量
修复遗漏等产生漂移。本 reconciler 做**全量存量对账**——每次 commit 涉及 .py 文件时
全扫 depgraph，把漂移落盘供追踪，与 gate（只检 staged 新增）互补。

真源边界（SSoT 分类铁律 TRAE-062）
----------------------------------
- depgraph（架构数据）→ 只读查询 PostgreSQL（``get_depgraph_pg_connection`` read_only）
- 翻译注册表（规则数据）→ 只读查询 YAML（``module_translation_loader``）
- 漂移报告（派生数据）→ 写 ``.runtime/`` 派生产物（非真源，可重建）

priority=951（晚于 dead_public_wrapper(950)，两者都是 late-stage warn-only 全扫）

Usage
-----
::

    from zephyr.governance.audit.translation_coverage_reconciler import (
        make_translation_coverage_reconciler,
    )

    registry.register(make_translation_coverage_reconciler(gateway))
"""

from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path

from zephyr.governance.audit.reconciliation_registry import (
    ReconcileResult,
    ReconcilerSpec,
)
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

__all__ = ["make_translation_coverage_reconciler"]

# 关联的 pre-commit GATE 标识（与 translation_coverage_gate.py 同名——reconciler 补偿 gate）
_GATE_ID = "TRANSLATION-COVERAGE"

# 执行优先级——晚于 dead_public_wrapper(950)，两者都是 late-stage warn-only 全扫
_PRIORITY = 951

# plain_zh 最低 CJK 字符数（与 gate / 写入工具一致，防过短无信息简介）
_MIN_CJK = 8

# 漂移报告落盘路径（.runtime/ 派生产物，非真源，可重建）
_DRIFT_REPORT_PATH = REPO_ROOT / ".runtime" / "translation_coverage" / "drift_report.json"

# 范围限定：src/zephyr/ + scripts/ 下（与 gate 同范围）
_SRC_ZEPHYR_PREFIX = "src/zephyr/"
_SCRIPTS_PREFIX = "scripts/"

# SQL 集中化（NO-BARE-SQL gate 合规，常量名需匹配 ^_?SQL_\w+$ 豁免正则）
_SQL_GET_NODES_WITH_FILE_PATH = (
    "SELECT path, file_path FROM nodes "
    "WHERE file_path IS NOT NULL AND file_path != ''"
)

# detail 中每类最多显示的条目数（防过长）
_MAX_DETAIL_ITEMS = 5


def _cjk_len(s: str) -> int:
    """统计 CJK 字符数（大白话最低信息量基线）。"""
    return len(re.findall(r"[\u4e00-\u9fff]", s or ""))


def _is_in_scope(file_path: str) -> bool:
    """判断 file_path 是否在检测范围内（src/zephyr/ 或 scripts/ 下）。

    与 translation_coverage_gate.py 同范围（tests/ 不在 depgraph file_path 中，
    天然排除）。
    """
    return file_path.startswith(_SRC_ZEPHYR_PREFIX) or file_path.startswith(_SCRIPTS_PREFIX)


def _query_depgraph_nodes() -> list[dict[str, str]] | None:
    """查询 depgraph 全部有 file_path 的节点。

    Returns:
        节点列表（每条含 path/file_path）；DB 不可达返回 None（fail-open）。
    """
    try:
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection(autocommit=True, read_only=True)
        try:
            cur = conn.cursor()
            cur.execute(_SQL_GET_NODES_WITH_FILE_PATH)
            rows = cur.fetchall()
            # psycopg3 返回元组（read_only 连接）；兼容 dict cursor
            result: list[dict[str, str]] = []
            for row in rows:
                if isinstance(row, dict):
                    result.append({"path": row.get("path", ""), "file_path": row.get("file_path", "")})
                else:
                    # 元组：按 SELECT 顺序 path, file_path
                    result.append({"path": row[0] or "", "file_path": row[1] or ""})
            return result
        finally:
            conn.close()
    except Exception as e:  # noqa: BLE001 — DB 不可达=环境异常，fail-open
        logger.warning(
            "translation_coverage_reconciler: depgraph 查询失败(%s: %s)，fail-open。",
            type(e).__name__, e, exc_info=True,
        )
        return None


def _load_translation_loader():
    """懒加载翻译 loader（跨 src/scripts 边界，对标 gate 的 sys.path 注入模式）。

    Returns:
        loader 模块（含 get_module_translation/is_generic_plain_zh/is_generic_plain_suffix）；
        不可达返回 None（fail-open）。
    """
    try:
        _shared_dir = str(REPO_ROOT / "scripts" / "governance")
        if _shared_dir not in sys.path:
            sys.path.insert(0, _shared_dir)
        from _shared.module_translation_loader import (  # noqa: WPS433 — 跨边界懒加载
            get_module_translation,
            is_generic_plain_zh,
            is_generic_plain_suffix,
        )
        return {
            "get_module_translation": get_module_translation,
            "is_generic_plain_zh": is_generic_plain_zh,
            "is_generic_plain_suffix": is_generic_plain_suffix,
        }
    except Exception as e:  # noqa: BLE001 — loader 不可达=环境异常，fail-open
        logger.warning(
            "translation_coverage_reconciler: 翻译 loader 不可达(%s: %s)，fail-open。",
            type(e).__name__, e, exc_info=True,
        )
        return None


def _scan_drift(nodes: list[dict[str, str]], loader: dict) -> dict[str, list[str]]:
    """扫描 depgraph 节点 vs 翻译真源，返回三类漂移。

    Returns:
        ``{"missing": [...], "short": [...], "generic": [...]}``——key 为漂移类别，
        value 为 file_path 列表。
    """
    get_module_translation = loader["get_module_translation"]
    is_generic_plain_zh = loader["is_generic_plain_zh"]
    is_generic_plain_suffix = loader["is_generic_plain_suffix"]

    drift: dict[str, list[str]] = {"missing": [], "short": [], "generic": []}

    for node in nodes:
        file_path = node.get("file_path", "")
        if not file_path or not _is_in_scope(file_path):
            continue
        try:
            trans = get_module_translation(file_path)
            if not trans:
                drift["missing"].append(file_path)
                continue
            plain = (trans.get("plain_zh") or "").strip()
            if not plain:
                drift["missing"].append(file_path)
                continue
            if _cjk_len(plain) < _MIN_CJK:
                drift["short"].append(file_path)
                continue
            if is_generic_plain_zh(plain):
                drift["generic"].append(file_path)
                continue
            name_zh = (trans.get("name_zh") or "").strip()
            if name_zh and is_generic_plain_suffix(plain, name_zh):
                drift["generic"].append(file_path)
        except Exception as e:  # noqa: BLE001 — 单条查询异常跳过，不中断全扫
            logger.debug(
                "translation_coverage_reconciler: 查询 %s 异常(%s: %s)，跳过。",
                file_path, type(e).__name__, e,
            )

    return drift


def _write_drift_report(drift: dict[str, list[str]]) -> None:
    """把漂移报告落盘到 .runtime/translation_coverage/drift_report.json。

    fail-open：写入失败不阻断（报告是派生产物，下次 commit 会重建）。
    """
    try:
        _DRIFT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "gate_id": _GATE_ID,
            "missing_plain": drift["missing"],
            "short_plain": drift["short"],
            "generic_plain": drift["generic"],
            "summary": {
                "missing_count": len(drift["missing"]),
                "short_count": len(drift["short"]),
                "generic_count": len(drift["generic"]),
                "total_drift": len(drift["missing"]) + len(drift["short"]) + len(drift["generic"]),
            },
        }
        _DRIFT_REPORT_PATH.write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception as e:  # noqa: BLE001 — 落盘失败不阻断
        logger.warning(
            "translation_coverage_reconciler: 漂移报告落盘失败(%s: %s)。",
            type(e).__name__, e, exc_info=True,
        )


def _format_detail(drift: dict[str, list[str]]) -> str:
    """格式化漂移详情字符串（每类限制显示数量）。"""
    parts: list[str] = []
    for label, items in [
        ("missing", drift["missing"]),
        ("short", drift["short"]),
        ("generic", drift["generic"]),
    ]:
        if not items:
            continue
        shown = items[:_MAX_DETAIL_ITEMS]
        suffix = f" (还有 {len(items) - _MAX_DETAIL_ITEMS} 个)" if len(items) > _MAX_DETAIL_ITEMS else ""
        parts.append(f"{label}[{', '.join(shown)}{suffix}]")
    return "；".join(parts) if parts else ""


def make_translation_coverage_reconciler(gateway: object) -> ReconcilerSpec:
    """构造翻译覆盖率存量对账 reconciler（warn-only）。

    Args:
        gateway: GitCommitGateway 实例（仅用其 project_root，此处通过 REPO_ROOT 替代）。

    Returns:
        ReconcilerSpec(gate_id=_GATE_ID, priority=_PRIORITY)。trigger 在
        src/*.py 或 scripts/*.py commit 时返回 True；reconcile 全扫 depgraph 节点
        vs 翻译真源，生成漂移报告并 warn。
    """

    def _trigger(committed_files: list[str]) -> bool:
        """Trigger when Python files in src/ or scripts/ are committed."""
        return any(
            (f.startswith("src/") or f.startswith("scripts/")) and f.endswith(".py")
            for f in committed_files
        )

    def _reconcile(
        committed_files: list[str], session_id: str
    ) -> ReconcileResult:
        """全扫 depgraph 节点 vs 翻译真源，生成漂移报告并 warn。"""
        try:
            # 1. 查 depgraph 全量节点（None=fail-open DB 不可达）
            nodes = _query_depgraph_nodes()
            if nodes is None:
                return ReconcileResult(
                    action="warn",
                    detail="depgraph DB 不可达，跳过存量对账",
                    gate_id=_GATE_ID,
                )

            # 2. 加载翻译 loader（None=fail-open loader 不可达）
            loader = _load_translation_loader()
            if loader is None:
                return ReconcileResult(
                    action="warn",
                    detail="翻译 loader 不可达，跳过存量对账",
                    gate_id=_GATE_ID,
                )

            # 3. 扫描漂移
            drift = _scan_drift(nodes, loader)

            # 4. 落盘报告（fail-open）
            _write_drift_report(drift)

            total = (
                len(drift["missing"]) + len(drift["short"]) + len(drift["generic"])
            )
            if total == 0:
                return ReconcileResult(
                    action="clean",
                    detail="no translation coverage drift found",
                    gate_id=_GATE_ID,
                )

            detail = _format_detail(drift)
            return ReconcileResult(
                action="warn",
                detail=f"{total} translation coverage drift(s): {detail}",
                gate_id=_GATE_ID,
            )
        except Exception as e:  # noqa: BLE001 — reconciler 永不抛异常
            logger.warning(
                "translation_coverage_reconciler: reconcile 失败(%s: %s)。",
                type(e).__name__, e, exc_info=True,
            )
            return ReconcileResult(
                action="warn",
                detail=f"translation_coverage reconcile error: {e}",
                gate_id=_GATE_ID,
            )

    return ReconcilerSpec(
        gate_id=_GATE_ID,
        trigger=_trigger,
        reconcile=_reconcile,
        priority=_PRIORITY,
    )
