# [BLUEPRINT] MOD-L02-027 | docs/03_modules/_domain_factor/casebook/blueprint.md | §D-FACTOR-CASE-01
# [MODULE] zephyr.factor.casebook.casebook
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] sqlite3(标准库); zephyr.shared.io.paths(REPO_ROOT)
# [CONSUMERS] (暂无；数据期 LLM 挖因子流程为首个计划消费者)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 只存统计量不存持仓/金额（宪章 B-011）；verdict ∈ {success,failure,fixed}；空 hypothesis 拒绝；非有限 ic/icir/turnover 拒绝；WAL + threading.Lock 并发写安全
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入校验失败->CasebookError(ValueError 子类，fail-closed)；sqlite 错误直接上抛不吞
# [TESTS] tests/factor/test_casebook.py
# [A_module] module_id=MOD-L02-027 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D-FACTOR-CASE-01 因子研究案例库——成功/失败→修复案例沉淀，防 AI 重复试错。

设计依据：2026-08 架构审查报告 §4.2（ALG-03）——借鉴 RD-Agent CoSTEER 实证的
「成功案例库+失败→修复库」机制（只借鉴机制，不引入 RD-Agent/Qlib 框架本体），
为数据期 LLM 挖因子打底，即刻降低 AI 重复试错的 token 消耗。

职责边界：
- 只存因子研究统计量（hypothesis/factor_expr/ic/icir/turnover/verdict/failure_diag/tags），
  不存任何持仓、金额、下单记录（宪章 B-011 合规红线）
- verdict 三值词表：success（成功）/ failure（失败）/ fixed（失败→修复）
- 检索先按因子族标签（tags 精确元素匹配），向量检索后置不抢（架构审查报告同口径）

存储：SQLite 单文件 data/databases/factor_casebook.db（92 号清单 D2 裁定授权新库）；
WAL 模式 + busy_timeout + 进程内 threading.Lock，支持多线程并发写。
"""

from __future__ import annotations

import logging
import math
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Final, Iterable

from zephyr.shared.io.paths import REPO_ROOT

log = logging.getLogger(__name__)

__all__: Final[list[str]] = [
    "VERDICTS",
    "CasebookError",
    "DEFAULT_DB_PATH",
    "get_case",
    "query_similar",
    "record_case",
]

#: 默认库路径（92 号清单 D2 裁定授权的新 SQLite 库；运行时产物不入 git）
DEFAULT_DB_PATH: Final[Path] = REPO_ROOT / "data" / "databases" / "factor_casebook.db"

#: verdict 合法词表：success=成功 / failure=失败 / fixed=失败→修复
VERDICTS: Final[frozenset[str]] = frozenset({"success", "failure", "fixed"})

#: 单次检索上限硬顶，防 AI 误传大 limit 拖垮上下文
_MAX_LIMIT: Final[int] = 500

#: 进程内写锁（WAL 已保证跨连接并发，本锁兜底同进程写串行化）
_WRITE_LOCK: Final[threading.Lock] = threading.Lock()

_SCHEMA_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS cases(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hypothesis TEXT NOT NULL,
    factor_expr TEXT,
    factor_json TEXT,
    ic REAL,
    icir REAL,
    turnover REAL,
    verdict TEXT NOT NULL,
    failure_diag TEXT,
    tags TEXT,
    created_at TEXT NOT NULL
)
"""


class CasebookError(ValueError):
    """案例库输入校验错误（fail-closed：非法输入一律拒绝，不落库）。"""


def _connect(db_path: Path) -> sqlite3.Connection:
    """建立连接并确保 schema 存在（幂等）。

    WAL 模式 + busy_timeout=30s：多线程/多进程并发写不崩；
    连接按调用短生命周期创建，避免跨线程共用连接的 SQLITE_MISUSE。
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(_SCHEMA_SQL)
    return conn


def _validate_metric(name: str, value: float | None) -> float | None:
    """校验统计量：None 放行，非有限值（NaN/inf）拒绝。"""
    if value is None:
        return None
    v = float(value)
    if not math.isfinite(v):
        raise CasebookError(f"{name} 必须为有限实数，拒绝值: {value!r}")
    return v


def _normalize_tags(tags: str | Iterable[str] | None) -> str | None:
    """归一化标签为逗号连接字符串（去空白、去空元素、保持顺序去重）。"""
    if tags is None:
        return None
    items = [tags] if isinstance(tags, str) else list(tags)
    seen: list[str] = []
    for item in items:
        tag = str(item).strip()
        if tag and tag not in seen:
            seen.append(tag)
    return ",".join(seen) if seen else None


def _row_to_dict(row: sqlite3.Row | tuple) -> dict:
    """行转 dict；tags 由逗号字符串还原为 list[str]（空为 []）。"""
    (cid, hypothesis, factor_expr, factor_json, ic, icir, turnover,
     verdict, failure_diag, tags, created_at) = row
    return {
        "id": cid,
        "hypothesis": hypothesis,
        "factor_expr": factor_expr,
        "factor_json": factor_json,
        "ic": ic,
        "icir": icir,
        "turnover": turnover,
        "verdict": verdict,
        "failure_diag": failure_diag,
        "tags": [t for t in tags.split(",") if t] if tags else [],
        "created_at": created_at,
    }


def record_case(
    hypothesis: str,
    *,
    verdict: str,
    factor_expr: str | None = None,
    factor_json: str | None = None,
    ic: float | None = None,
    icir: float | None = None,
    turnover: float | None = None,
    failure_diag: str | None = None,
    tags: str | Iterable[str] | None = None,
    db_path: str | Path | None = None,
) -> int:
    """写入一条因子研究案例，返回自增 case id。

    Args:
        hypothesis: 研究假设（必填，空串/纯空白拒绝）。
        verdict: 结论词表值：success / failure / fixed（必填，词表外拒绝）。
        factor_expr: 因子表达式文本（可选）。
        factor_json: 因子结构化 JSON 文本（可选）。
        ic: 信息系数（可选，非有限值拒绝）。
        icir: 信息比率（可选，非有限值拒绝）。
        turnover: 换手率（可选，非有限值拒绝）。
        failure_diag: 失败诊断/修复说明（可选）。
        tags: 因子族标签，字符串或字符串可迭代（可选）。
        db_path: 库路径覆盖（测试用）；None 用默认 data/databases/factor_casebook.db。

    Returns:
        新案例的自增 id。

    Raises:
        CasebookError: hypothesis 为空、verdict 非法、统计量非有限值。
    """
    hyp = str(hypothesis).strip() if hypothesis is not None else ""
    if not hyp:
        raise CasebookError("hypothesis 不能为空（fail-closed）")
    if verdict not in VERDICTS:
        raise CasebookError(
            f"verdict 非法: {verdict!r}，合法词表: {sorted(VERDICTS)}"
        )
    ic_v = _validate_metric("ic", ic)
    icir_v = _validate_metric("icir", icir)
    turnover_v = _validate_metric("turnover", turnover)
    tags_s = _normalize_tags(tags)
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    with _WRITE_LOCK:
        conn = _connect(path)
        try:
            cur = conn.execute(
                "INSERT INTO cases(hypothesis, factor_expr, factor_json, ic, icir,"
                " turnover, verdict, failure_diag, tags, created_at)"
                " VALUES(?,?,?,?,?,?,?,?,?,?)",
                (hyp, factor_expr, factor_json, ic_v, icir_v, turnover_v,
                 verdict, failure_diag, tags_s, created_at),
            )
            conn.commit()
            case_id = int(cur.lastrowid)
        finally:
            conn.close()
    log.debug("案例入库 id=%d verdict=%s tags=%s", case_id, verdict, tags_s)
    return case_id


def query_similar(
    family_tag: str | None = None,
    verdict: str | None = None,
    limit: int = 20,
    *,
    db_path: str | Path | None = None,
) -> list[dict]:
    """按因子族标签/结论检索案例（向量检索后置，本版只做标签+词表过滤）。

    Args:
        family_tag: 因子族标签，按 tags 元素精确匹配；None 不按标签过滤。
        verdict: 结论过滤；None 不过滤，词表外值拒绝。
        limit: 返回条数上限（1~_MAX_LIMIT，超出截断）。
        db_path: 库路径覆盖（测试用）。

    Returns:
        案例 dict 列表，按 id 倒序（最新在前）；空库/无匹配返回 []。

    Raises:
        CasebookError: verdict 词表外或 limit 非正整数。
    """
    if verdict is not None and verdict not in VERDICTS:
        raise CasebookError(
            f"verdict 非法: {verdict!r}，合法词表: {sorted(VERDICTS)}"
        )
    try:
        lim = int(limit)
    except (TypeError, ValueError) as exc:
        raise CasebookError(f"limit 必须为正整数，拒绝值: {limit!r}") from exc
    if lim < 1:
        raise CasebookError(f"limit 必须为正整数，拒绝值: {limit!r}")
    lim = min(lim, _MAX_LIMIT)

    sql = ("SELECT id, hypothesis, factor_expr, factor_json, ic, icir, turnover,"
           " verdict, failure_diag, tags, created_at FROM cases")
    clauses: list[str] = []
    params: list[object] = []
    if family_tag is not None:
        tag = str(family_tag).strip()
        if tag:
            # tags 存逗号连接串；包裹边界做元素级精确匹配，防 mom 误配 momentum
            clauses.append("(',' || tags || ',') LIKE ? ESCAPE '\\'")
            esc = tag.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            params.append(f"%,{esc},%")
    if verdict is not None:
        clauses.append("verdict = ?")
        params.append(verdict)
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(lim)

    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    if not path.exists():
        return []  # 库未建=空库，不主动创建文件
    conn = _connect(path)
    try:
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()
    return [_row_to_dict(r) for r in rows]


def get_case(
    case_id: int,
    *,
    db_path: str | Path | None = None,
) -> dict | None:
    """按 id 取单条案例；不存在返回 None（不抛异常）。"""
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    if not path.exists():
        return None
    conn = _connect(path)
    try:
        row = conn.execute(
            "SELECT id, hypothesis, factor_expr, factor_json, ic, icir, turnover,"
            " verdict, failure_diag, tags, created_at FROM cases WHERE id = ?",
            (int(case_id),),
        ).fetchone()
    finally:
        conn.close()
    return _row_to_dict(row) if row else None
