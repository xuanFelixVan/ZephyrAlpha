# [BLUEPRINT] MOD-LIB-001 | docs/03_modules/_domain_library/blueprint.md | §1
# [MODULE] zephyr.library.library_regen_reconciler
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcileResult, ReconcilerSpec); zephyr.library.collectors (collect_all, ingest_all); zephyr.library.librarian (Librarian); zephyr.shared.infra.process_pool (run_subprocess_hidden)
# [CONSUMERS] zephyr.governance.audit.reconciliation_registry（_EXTERNAL_SPEC_MODULES 构造期发现，post-commit 事件触发）
# [STARTUP] imported by reconciliation_registry（惰性 importlib）
# [MATURITY] production
# [INVARIANTS] 事件触发（post-commit），禁 cron/Timer/sleep-loop（永久系统四要素）；只增量采集+入账+馆页重生成+对账，零删除零状态改写（coverage 注销仍走死亡证明人工链）；trigger=馆藏输入面（src/scripts/data/catalogs）变更；全程 fail-soft（单步失败降级 warn 不抛）；库不可达 action=skip；馆页/对账报告为生成视图（gitignore 面），提交仍走人工批；全量入账必经 ingest_with_shrink_guard 供数轴缩水闸（缩水=audit 告警事件+raise，总筹裁-07）
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] reconcile 永不抛异常——各步异常折叠为 ReconcileResult(action="warn", detail=阶段+摘要)
# [TESTS] tests/library/test_library_regen_reconciler.py
# [A_module] module_id=MOD-LIB-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""library_regen_reconciler.py — 图书馆 post-commit 自动刷新（ulib3 T4）。

消灭手动 regen：commit 触碰馆藏输入面（src/scripts/data/登记表）后自动跑
"增量采集→指纹刷新（ingest upsert 即指纹更新）→馆页重生成→coverage 对账"。
方案对标 schedule_consistency_reconciler 的 ReconcilerSpec 外部规格通道
（post-commit 事件触发，宪法红线：reconciler 禁 cron/sleep-loop）。

# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/library_regen_reconciler.yaml
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Final

logger = logging.getLogger(__name__)

__all__: Final[list[str]] = [
    "LibraryIngestShrinkError",
    "ingest_with_shrink_guard",
    "make_library_regen_reconciler",
]

#: 馆藏输入面前缀（命中才触发；馆页/报告/纯文档变更不触发，防 regen 风暴）
_TRIGGER_PREFIXES = ("src/", "scripts/", "data/", "docs/01_policies_and_standards/_registry/")

#: 守卫告警事件锚（action=audit 只落 lib_events，不触发 upsert、非馆藏实体）
_GUARD_ASSET_ID = "LIB:INGEST-SHRINK-GUARD"


class LibraryIngestShrinkError(RuntimeError):
    """全量入账后 potential_consumers 非空计数缩水（守卫触发，总筹裁-07）。"""


def _count_nonempty_consumers(conn) -> int:
    """供数反查轴非空行数快照（SQL 常量真源=ledger_schema）。"""
    from zephyr.library.ledger_schema import _SQL_COUNT_NONEMPTY_CONSUMERS

    with conn.cursor() as cur:
        cur.execute(_SQL_COUNT_NONEMPTY_CONSUMERS)
        return int(cur.fetchone()[0])


def ingest_with_shrink_guard(conn, librarian, collected, actor: str, *, count_fn=None) -> tuple[int, int, int]:
    """全量入账前后对 potential_consumers 非空计数做快照对比（缩水闸）。

    背景：09-24~27 三轮全量 ingest 把 #410② 人工回填 68 资产的供数轴清零
    （根因=upsert 冲突分支引用被 VALUES COALESCE 预空的 EXCLUDED，裁-07 取证）。
    本闸在入账后立即复核：缩水即先写 audit 告警事件再 raise——由调用方
    （post-commit reconciler，事件触发）折叠为 warn，非 cron/sleep-loop。

    Args:
        conn: 总账 PG 连接（快照计数用）。
        librarian: 馆员实例（入账+告警事件写路径）。
        collected: collect_all 结果。
        actor: 登记会话标识。
        count_fn: 计数注入缝（测试用；缺省走 _SQL_COUNT_NONEMPTY_CONSUMERS）。

    Returns:
        (登记条数, before, after)。

    Raises:
        LibraryIngestShrinkError: after < before（告警事件已先行落账）。
    """
    counter = count_fn if count_fn is not None else lambda: _count_nonempty_consumers(conn)
    from zephyr.library.collectors import ingest_all

    before = counter()
    n = ingest_all(librarian, collected, actor)
    after = counter()
    if after < before:
        librarian.act(
            "audit",
            _GUARD_ASSET_ID,
            actor=actor,
            detail={"alert": "potential_consumers_shrink", "before": before, "after": after, "delta": after - before},
        )
        raise LibraryIngestShrinkError(
            f"potential_consumers 非空计数缩水 {before}->{after}（全量入账 {n} 条），告警事件已落账"
        )
    return n, before, after


def make_library_regen_reconciler(gateway: object | None = None):
    """构造图书馆 post-commit 刷新 reconciler（action ∈ clean/warn/skip）。"""
    from zephyr.governance.audit.reconciliation_registry import ReconcileResult, ReconcilerSpec

    if gateway is not None and getattr(gateway, "project_root", None):
        project_root = Path(str(gateway.project_root))
    else:
        from zephyr.shared.io.paths import REPO_ROOT

        project_root = Path(str(REPO_ROOT))

    def _rel(f: str) -> str:
        try:
            return os.path.relpath(f, str(project_root)).replace("\\", "/")
        except ValueError:
            return f

    def _trigger(committed_files: list[str]) -> bool:
        return any(_rel(f).startswith(_TRIGGER_PREFIXES) for f in committed_files)

    def _reconcile(committed_files: list[str], session_id: str):
        stages: list[str] = []
        try:
            # ① 增量采集 + ② 指纹刷新（ingest=upsert，指纹/标题/供数轴不回退）
            from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
            from zephyr.library.collectors import collect_all
            from zephyr.library.librarian import Librarian

            collected = collect_all()
            conn = get_depgraph_pg_connection()
            try:
                n, before, after = ingest_with_shrink_guard(
                    conn, Librarian(conn), collected, actor=session_id or "library-regen"
                )
            finally:
                conn.close()
            stages.append(f"采集入账 {n}（供数非空 {before}->{after}）")
        except Exception as exc:  # noqa: BLE001 — fail-soft
            logger.warning("library-regen 采集入账失败: %s", exc, exc_info=True)
            return ReconcileResult(action="warn", detail=f"library-regen 采集入账失败: {exc}")

        try:
            # ③ 馆页重生成（生成视图）
            from zephyr.shared.infra.process_pool import (
                run_subprocess_hidden,  # noqa: PLC0415 — 生成器为 scripts 面 CLI，进程内 import 重
            )

            r = run_subprocess_hidden(
                ["python", "scripts/governance/generators/generate_library_index.py"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=300,
                env={**os.environ, "PATH": os.environ.get("PATH", "")},
            )
            stages.append("馆页重生成 rc=0" if r.returncode == 0 else f"馆页重生成 rc={r.returncode}")
        except Exception as exc:  # noqa: BLE001 — fail-soft
            stages.append(f"馆页重生成异常 {type(exc).__name__}")

        try:
            # ④ 对账
            from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: PLC0415

            r = run_subprocess_hidden(
                ["python", "scripts/governance/generators/check_library_coverage.py"],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=300,
            )
            tail = (r.stdout or "").strip().splitlines()[-1] if (r.stdout or "").strip() else f"rc={r.returncode}"
            stages.append(f"对账 {tail}")
        except Exception as exc:  # noqa: BLE001 — fail-soft
            stages.append(f"对账异常 {type(exc).__name__}")

        detail = f"library-regen post-commit（{session_id or 'unknown'}）：" + "；".join(stages)
        logger.info(detail)
        bad = any(("rc=" in s and "rc=0" not in s) or "异常" in s or "失败" in s for s in stages)
        return ReconcileResult(action="warn" if bad else "clean", detail=detail)

    return ReconcilerSpec(
        gate_id="LIBRARY-REGEN",
        trigger=_trigger,
        reconcile=_reconcile,
        # 显式声明制：读=盘面采集+索引登记面；写=馆页/对账报告生成视图（零 commit 零删除）
        file_ops=frozenset({"read", "write"}),
        priority=200,
    )


def make_external_reconciler_spec(host: object | None = None):
    """ReconciliationRegistry 外部规格发现钩子入口（签名稳定）。"""
    return make_library_regen_reconciler(host)
