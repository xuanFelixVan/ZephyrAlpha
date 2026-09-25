# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure/blueprint.md | §restore_drill
# [MODULE] scripts.backup.restore_drill
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.shared.infra.process_pool (run_subprocess_hidden); zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] schtasks 月度计划任务（ZEPHYR-RESTORE-DRILL，登记 process_reaper_keep）；DR 演练台账 logs/restore_drill_*.json
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 演练库=depgraph_drill（临时库，演练前确保不存在、演练完必 DROP，绝不触碰生产 depgraph 库）；对账全部只读；报告 JSON 落 logs/；凭据走 config/.env.postgres（RULE-SECRETS 管道，禁硬编码）；pg_restore 不可达时报告 failed 并退出 1（fail-visible）；裁决=四条件合取（判据版本 P-3R2，处方 P-3 废除「三表行数精确相等」恒红尺）：C1 表集合全等（演练库与生产库 public 基表表名集合全等）∧ C2 行数方向性 drill<=live（dump 是历史时点，演练库不可能多于活库；陈旧度 live-drill 只作报告读数、默认不设硬阈值，显式 --staleness-limit 才参与裁决）∧ C3 老数据内容指纹一致（三表各取「主键序头段 + 快照边界回退尾段」两段有界样本，只比两侧共有主键的不可变稳定列聚合指纹；样本为空=不可判=红）∧ C4 pg_restore 非零返回码按 stderr 分类（命中已知良性集合=记录并继续，集合外=判 failed，禁止静默放行）；文本主键必须钉 COLLATE "C"（演练库 datcollate 继承 template1，与生产库 C 不同，不钉则两侧取样行集零交集）；rows[t].match 语义=旧「精确相等」读数，仅留档不作裁决；报告 schema 只增不改不删
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 恢复/核数失败写 failed 报告后退出 1；临时库确保清理（finally 双通道 DROP + 存在性复核）；判据不满足写 pass=False + status + failed_criteria 后退出 1
# [TESTS] tests/backup/test_restore_drill.py
# [A_module] module_id=MOD-INF-043 | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 月度恢复演练 CLI 由 ZEPHYR-RESTORE-DRILL schtasks 月度事件触发，人工直跑为兜底形态，非常驻
"""restore_drill.py — depgraph 账本月度恢复演练（ulib3 T2）。

取最新 depgraph.dump → pg_restore 到临时库 depgraph_drill → 与生产库四条件对账
（表集合 / 行数方向性 / 老数据内容指纹 / pg_restore stderr 良性分类）
→ 报告落 logs/restore_drill_YYYYMMDD_HHMMSS.json → DROP 临时库。
Owner 裁定=月度自动演练（备份不只存，要能还原）；drill 结果不入账，人工阅。

判据沿革（处方 P-3）：P-3R1 要求「三表行数 drill==live 精确相等」，但 dump 是历史时点
快照、活库持续增长，只要演练不在 dump 那一瞬间就必然不等 → 恒红（2026-09-25 22:05 实测
live 44565/1634702/12669 vs drill 44524/1483550/12656 三表全红，pass 恒 False）。
P-3R2 改为可满足、且仍能抓真故障的多条件合取；裁决逻辑抽成纯函数 judge_drill()，
单测在同一份真实数据上做红绿对拍而不连真库。

Usage::

    python scripts/backup/restore_drill.py [--dump <path>]
                                           [--sample-rows 1500] [--sample-skip 200]
                                           [--staleness-limit N] [--keep-drill-db]
# [ALGO_FLOW] external: docs/03_modules/_domain_infrastructure/algo_flow/restore_drill.yaml
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

from zephyr.shared.infra.process_pool import run_subprocess_hidden
from zephyr.shared.io.paths import REPO_ROOT

__all__ = ["judge_drill", "run_drill"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定

_DRILL_DB = "depgraph_drill"
_LIVE_DB = "depgraph"
_TABLES = ("lib_assets", "lib_events", "nodes")
_DUMP_GLOB = "G:/backup/db_dumps/**/depgraph.dump"

# psql -c 语句集中化（§5.160.2）：psql 子进程调用面，SQL 文本模块级常量（表名/列名变参走 format）
_SQL_COUNT_ROWS = "SELECT count(*) FROM {}"
_SQL_DROP_DRILL_DB = "DROP DATABASE IF EXISTS " + _DRILL_DB
_SQL_DROP_DRILL_DB_FORCE = "DROP DATABASE IF EXISTS " + _DRILL_DB + " WITH (FORCE)"
_SQL_CREATE_DRILL_DB = "CREATE DATABASE " + _DRILL_DB
_SQL_DRILL_DB_EXISTS = "SELECT count(*) FROM pg_database WHERE datname='" + _DRILL_DB + "'"
#: C1 取数面：某库 public 下基表名（09-26 实测生产库 89 张，演练库还原后同为 89 张）
_SQL_LIST_BASE_TABLES = "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
#: C3 取数面·头段：按主键序取前 N 行（两侧各取自己的前 N，再只比共有主键）
_SQL_SAMPLE_ASC = "SELECT {pk}::text, {agg} FROM (SELECT * FROM {table} ORDER BY {order} ASC LIMIT {n}) _s ORDER BY 1"
#: C3 取数面·快照边界尾段：主键落在演练库尾段区间 [lo,hi] 内的前 N 行。
#: 用「演练库锚定的区间」而不是「两侧各取自己的后 N」——活库在 dump 之后继续追加，
#: 两侧各自取尾必然零交集（09-26 实测 lib_events 两侧各取尾 common=0），区间锚定才可比。
_SQL_SAMPLE_RANGE = (
    "SELECT {pk}::text, {agg} FROM (SELECT * FROM {table} WHERE {order} BETWEEN {lo} AND {hi} "
    "ORDER BY {order} ASC LIMIT {n}) _s ORDER BY 1"
)
#: C3 尾段区间上下界：自快照边界回退 skip 行后取 n 行的主键范围（只在演练库上算）
_SQL_SAMPLE_RANGE_BOUND = (
    "SELECT min(_s.k)::text, max(_s.k)::text FROM "
    "(SELECT {order} AS k FROM {table} ORDER BY {order} DESC LIMIT {n} OFFSET {skip}) _s"
)

#: 判据版本（可审计：09-25 及之前为 P-3R1「三表行数精确相等」恒红尺）
_CRITERIA_VERSION = "P-3R2"
#: 判据变更点说明——随报告出厂，避免下一个读报告的人把新尺当旧尺
_CRITERIA_CHANGE_NOTE = (
    "P-3R2 判据变更（修 2026-09-25 月检处方 P-3）：旧尺 pass=all(drill==live) 在「dump 是历史"
    "时点快照 + 活库持续增长」下恒不成立（09-25 实测 live 44565/1634702/12669 vs drill"
    " 44524/1483550/12656 → 恒红），且 pg_restore_rc 被记录却不参与裁决。新尺=C1 表集合全等 ∧"
    " C2 行数方向性 drill<=live ∧ C3 老数据内容指纹一致 ∧ C4 pg_restore stderr 良性分类。"
    " rows[t].match 字段保留（语义=旧「精确相等」读数，不再参与裁决）；陈旧度只作读数不作阈值"
    "（要阈值请显式 --staleness-limit，默认不设，以免制造下一次恒红）。"
)
#: 旧判据（P-3R1）留档表述：单测在同一份数据上做红绿对拍用
_LEGACY_JUDGE_NOTE = "P-3R1 旧尺：report['pass'] = all(rows[t]['drill'] == rows[t]['live'])"
#: C3 每表每段有界样本行数（头段 N + 快照边界尾段 N）
_DEFAULT_SAMPLE_ROWS = 1500
#: C3 尾段自快照边界回退的行数——把「dump 之后仍可能被改写」的最近一段排除在指纹之外
_DEFAULT_SAMPLE_SKIP = 200
#: C2 陈旧度硬阈值默认关闭（None=只入报告读数不判红）——「不要把陈旧度设成新的恒红阈值」
_DEFAULT_STALENESS_LIMIT: int | None = None

#: 主键列名（C3 样本取键面）
_PK_OF: dict[str, str] = {"lib_assets": "asset_id", "lib_events": "event_id", "nodes": "node_id"}
#: C3 主键序表达式。演练库由本脚本 CREATE DATABASE 建出，datcollate 继承 template1
#: =「Chinese (Simplified)_China.936」，而生产库 depgraph 的 datcollate=「C」（09-26 实测）——
#: 文本主键两侧排序结果不同，「两侧各取前 N」会零交集（实测 lib_assets common=0），
#: 于是 C3 会退化成 P-3 正在修的「恒红尺」。故文本主键必须钉死 COLLATE "C"；
#: bigint 主键用数值序（=时间序），不钉。判据变更点。
_PK_ORDER: dict[str, str] = {
    "lib_assets": 'asset_id COLLATE "C"',
    "lib_events": "event_id",
    "nodes": "node_id",
}
#: 主键是否数值型：决定尾段区间谓词的字面量形态（数值裸量 vs 文本引号量）
_PK_NUMERIC: dict[str, bool] = {"lib_assets": False, "lib_events": True, "nodes": True}
#: 行指纹列式：NULL 显式占位，避免 array_to_string 跳 NULL 造成列位漂移
_DIGEST_EXPR = "md5(array_to_string(ARRAY[{cols}], chr(31)))"
#: C3 各表稳定列——只取「注册即定、时间上不再改写」的列。判据变更点：列清单若混入可变列，
#: C3 立刻退化成恒红尺。09-26 在 live vs 演练库的共有老数据上逐列实测两侧 md5：
#:   lib_assets 仍被改写 = fingerprint_sha256(223)/fingerprint_aux(160)/built_at(1495)/generation(1495)
#:   nodes 仍被改写 = granularity/subdomain_id/blueprint_id/belongs_to/change_policy/impact_level/
#:                    modification_permission/file_header_score/tags/design_maturity/type_specific_data/
#:                    last_verified/build_status/content_hash/public_api
#:   lib_events 全列 append-only 零漂移
#: 故稳定列一律排除上述名单。
_STABLE_COLUMNS: dict[str, tuple[str, ...]] = {
    "lib_assets": (
        "kind",
        "home",
        "family_id",
        "owner_domain",
        "retention_class",
        "disposition_authority",
        "registered_at",
        "registered_by",
    ),
    "lib_events": ("asset_id", "action", "actor", "ts", "gate_passed", "detail"),
    "nodes": ("node_type", "path", "domain_id", "owner", "architecture_layer", "node_name", "file_path"),
}

#: pg_restore 已知良性错误集合。来源=2026-09-25 22:05 月检实测 rc=1 的那三条
#: （logs/restore_drill_20260925_220551.json 记 rc=1 但未存 stderr，故由 09-26 01:25 干净
#: 复跑逐条复证原文，见 logs/restore_drill_20260926_012521.json 的 pg_restore_stderr_excerpt）：
#:   ① CREATE SCHEMA public;                     → 模式 "public" 已经存在
#:   ② ALTER DEFAULT PRIVILEGES ... ON SEQUENCES → permission denied to change default privileges
#:   ③ ALTER DEFAULT PRIVILEGES ... ON TABLES    → permission denied to change default privileges
#: 判据变更点：非零返回码不再「只记录不裁决」，也不再无条件判红——按本集合分类，
#: 集合外错误一律判红（fail-visible），原始 stderr 片段随报告留证。
#: 匹配面取 `Command was:` 的 SQL 文本 + 错误行文本，不被 psql 本地化译文绑架
#: （zh_CN 下 "already exists" 输出为「已经存在」，故两种关键词都列）。
_BENIGN_RESTORE_ERRORS: tuple[dict[str, str], ...] = (
    {
        "id": "benign-schema-public-exists",
        "why": "dump 内含 CREATE SCHEMA public；演练库新建时 public 模式已存在，幂等噪声，不影响数据还原",
        "command": r"^\s*CREATE SCHEMA (?:IF NOT EXISTS )?public\b",
        "message": r"(?:already exists|已经存在)",
    },
    {
        "id": "benign-alter-default-privileges",
        "why": "dump 尾部 ALTER DEFAULT PRIVILEGES 需超管/对象属主权限；演练角色无权限，"
        "只影响模板级默认权限，不影响已还原的表与数据",
        "command": r"^\s*ALTER DEFAULT PRIVILEGES\b",
        "message": r"(?:permission denied to change default privileges|permission denied|修改默认权限)",
    },
)
_RE_RESTORE_ERROR_LINE = re.compile(r"^\s*pg_restore:\s*error\s*[:：]\s*(.*)$")
_RE_RESTORE_COMMAND_LINE = re.compile(r"^\s*Command was:\s*(.*)$")


def _iter_restore_errors(stderr: str) -> list[tuple[str, str]]:
    """把 pg_restore stderr 顺序切成 (error_line, command_snippet) 列表。

    必须单趟顺序配对：error 行在前、其 `Command was:` 在后，中间可插 DETAIL/HINT 行。
    反例（09-26 实跑复现并修掉）：两条正则各取一列再按序号拉链时，(.*) 配 DOTALL 会把
    首个匹配吞到串尾，第 2/3 条错误的 command 恒为空 → 良性集合永不命中 → 恒红。
    """
    out: list[tuple[str, str]] = []
    pending: str | None = None
    for raw in (stderr or "").splitlines():
        m = _RE_RESTORE_ERROR_LINE.match(raw)
        if m:
            if pending is not None:
                out.append((pending, ""))
            pending = m.group(1).strip()
            continue
        if pending is None:
            continue
        cm = _RE_RESTORE_COMMAND_LINE.match(raw)
        if cm:
            out.append((pending, cm.group(1).strip()))
            pending = None
    if pending is not None:
        out.append((pending, ""))
    return out


def _classify_pg_restore_stderr(stderr: str, rc: int) -> tuple[str, dict]:
    """C4：pg_restore 返回码按 stderr 分类。返回 (verdict, detail)。

    verdict：clean（rc=0 且无错误行）｜clean_with_noise（rc=0 但有错误行）
            ｜benign_only（rc!=0 且全部命中已知良性集合）｜unknown（有集合外错误 → 判红）
    """
    errors = _iter_restore_errors(stderr)
    detail: dict = {"rc": rc, "error_count": len(errors), "benign_matched": {}, "unknown_errors": []}
    if rc == 0:
        detail["verdict"] = "clean" if not errors else "clean_with_noise"
        return detail["verdict"], detail
    if not errors:
        # 非零但拿不到可解析错误行：不可证明良性 → fail-visible
        detail["unknown_errors"].append(
            {"reason": "nonzero rc without parsable error lines", "stderr_excerpt": (stderr or "")[:500]}
        )
        return "unknown", detail
    for err, cmd in errors:
        hit = None
        for rule in _BENIGN_RESTORE_ERRORS:
            if re.search(rule["command"], cmd, re.IGNORECASE) and re.search(rule["message"], err, re.IGNORECASE):
                hit = rule["id"]
                break
        if hit is None:
            detail["unknown_errors"].append({"error": err[:300], "command": cmd[:200]})
        else:
            detail["benign_matched"][hit] = detail["benign_matched"].get(hit, 0) + 1
    verdict = "benign_only" if not detail["unknown_errors"] else "unknown"
    return verdict, detail


def _merge_sample(live_rows: list[tuple[str, str]], drill_rows: list[tuple[str, str]]) -> dict:
    """C3 核心：两侧有界样本 → 只保留**共有主键**（=时间上不会再变的老数据）后做聚合指纹。

    为什么不能「两侧各按主键取前 N 再直接比 md5」（09-25 实测前 5000 行 md5 不等的原因）：
    活库在 dump 之后新插入的行会挤进前 N，两侧比的是不同行集。共有主键把这块漂移结构性
    消掉——只比同时存在于快照与活库的那些行；这些行上再出现内容不等，就不可能是时点差。
    """
    lmap = dict(live_rows)
    dmap = dict(drill_rows)
    common = sorted(set(lmap) & set(dmap))
    mismatched = [k for k in common if lmap[k] != dmap[k]]

    def _agg(m: dict[str, str]) -> str:
        payload = ";".join(f"{k}={m[k]}" for k in common)
        return hashlib.md5(payload.encode("utf-8")).hexdigest()

    fp_live, fp_drill = _agg(lmap), _agg(dmap)
    return {
        "sample_size": len(common),
        "live_rows_returned": len(lmap),
        "drill_rows_returned": len(dmap),
        "fingerprint_live": fp_live,
        "fingerprint_drill": fp_drill,
        "fingerprint_match": bool(common) and fp_live == fp_drill,
        "mismatched_pk_count": len(mismatched),
        "mismatched_pk_sample": mismatched[:5],
    }


def _judge_c1(live_tables: list[str], drill_tables: list[str]) -> dict:
    """C1 表集合全等：演练库必须还原出与生产库一模一样的 public 基表集合。"""
    lt, dt = set(live_tables), set(drill_tables)
    return {
        "ok": lt == dt,
        "live_table_count": len(lt),
        "drill_table_count": len(dt),
        "missing_in_drill": sorted(lt - dt),
        "extra_in_drill": sorted(dt - lt),
    }


def _judge_c2_one(live: int, drill: int, staleness_limit: int | None) -> dict:
    """C2 单表行数方向性：历史快照不可能多于活库；陈旧度默认只作读数、不判红。"""
    item: dict = {"live": live, "drill": drill, "match": drill == live}
    if drill < 0:
        return {
            **item,
            "ok": False,
            "staleness": None,
            "staleness_ratio": None,
            "reason": "演练库取不到该表行数（缺表）",
        }
    if drill > live:
        return {
            **item,
            "ok": False,
            "staleness": live - drill,
            "staleness_ratio": 0.0,
            "reason": "drill>live：历史快照不可能多于活库 → 残留演练库叠加或生产库掉数",
        }
    staleness = live - drill
    over = staleness_limit is not None and staleness > staleness_limit
    item = {
        **item,
        "ok": not over,
        "staleness": staleness,
        "staleness_ratio": round(staleness / live, 6) if live else 0.0,
        "staleness_hard_limited": bool(over),
    }
    if over:
        item["reason"] = f"陈旧度 {staleness} 超过显式阈值 {staleness_limit}"
    return item


def _judge_c2(row_counts: dict[str, dict[str, int]], staleness_limit: int | None) -> tuple[dict, dict]:
    """C2 汇总：返回（rows 逐表读数=沿用旧字段名, c2 判据片段）。"""
    rows = {t: _judge_c2_one(int(v["live"]), int(v["drill"]), staleness_limit) for t, v in row_counts.items()}
    c2 = {
        "ok": all(v["ok"] for v in rows.values()),
        "rule": "drill<=live 且 drill>=0；陈旧度只作读数不作硬阈值（staleness_limit=%r）" % (staleness_limit,),
    }
    return rows, c2


def _judge_c3_one(drill_count: int, sample: dict) -> dict:
    """C3 单表：两侧共有主键上的稳定列聚合指纹必须相等；共有样本为空=不可判=红。"""
    if drill_count < 0:
        return {"ok": False, "sample_size": 0, "reason": "演练库缺表，样本不可得"}
    merged = _merge_sample(list(sample.get("live") or []), list(sample.get("drill") or []))
    merged["regions"] = sample.get("regions") or {}
    if sample.get("error"):
        return {**merged, "ok": False, "reason": f"样本取数失败：{sample['error']}"}
    if merged["sample_size"] == 0:
        return {**merged, "ok": False, "reason": "两侧共有主键为空 → 内容一致性不可判（fail-visible，不静默放行）"}
    if not merged["fingerprint_match"]:
        return {**merged, "ok": False, "reason": "共有老数据的稳定列指纹不等 → 列值级真故障（时点差解释不了）"}
    return {**merged, "ok": True}


def _judge_c3(row_counts: dict[str, dict[str, int]], samples: dict[str, dict]) -> dict:
    """C3 汇总：三表逐表判定后合取。"""
    tables = {t: _judge_c3_one(int(v["drill"]), samples.get(t) or {}) for t, v in row_counts.items()}
    return {
        "ok": all(v["ok"] for v in tables.values()),
        "rule": "两侧共有主键上的稳定列聚合指纹必须相等；样本为空=不可判=红",
        "stable_columns": {k: list(v) for k, v in _STABLE_COLUMNS.items()},
        "tables": tables,
    }


def _judge_c4(pg_restore_rc: int, pg_restore_stderr: str) -> dict:
    """C4 汇总：非零返回码必须能证明良性，证明不了就判红（不静默放行）。"""
    verdict, detail = _classify_pg_restore_stderr(pg_restore_stderr, pg_restore_rc)
    return {"ok": verdict in _C4_PASSING_VERDICTS, "verdict": verdict, **detail}


#: 判红优先级表：status 词表沿用旧值（下游可能按 row_mismatch 读数），含义见 _judge_c* 各自 doc
_STATUS_BY_FAILED: tuple[tuple[str, str], ...] = (
    ("c1_table_set_equal", "table_set_mismatch"),
    ("c3_content_fingerprint", "content_mismatch"),
    ("c2_row_direction", "row_mismatch"),
)
#: C4 可放行的 verdict
_C4_PASSING_VERDICTS = ("clean", "clean_with_noise", "benign_only")
#: 只剩 C4 不过时的 status
_STATUS_RESTORE_FAILED = "pg_restore_error_unclassified"


def judge_drill(
    *,
    live_tables: list[str],
    drill_tables: list[str],
    row_counts: dict[str, dict[str, int]],
    samples: dict[str, dict],
    pg_restore_rc: int,
    pg_restore_stderr: str = "",
    staleness_limit: int | None = _DEFAULT_STALENESS_LIMIT,
) -> dict:
    """裁决纯函数（可单测，不连库）：四条件合取 → pass/status/criteria/rows 判据片段。

    入参全部是「已观测事实」，本函数不连库、不起子进程；四个条件各由 _judge_c* 判定。

    Args:
        live_tables / drill_tables: 两侧 public 基表名列表（C1）。
        row_counts: {table: {"live": int, "drill": int}}，drill=-1 表示演练库取不到该表（C2）。
        samples: {table: {"live": [(pk, 行指纹)], "drill": [...]}} 有界样本原始行（C3）。
        pg_restore_rc / pg_restore_stderr: 恢复子进程返回码与原始 stderr（C4）。
        staleness_limit: 陈旧度硬阈值（live-drill 行数差上界）；默认 None=只入报告读数不判红。
    """
    rows, c2 = _judge_c2(row_counts, staleness_limit)
    criteria = {
        "c1_table_set_equal": _judge_c1(live_tables, drill_tables),
        "c2_row_direction": c2,
        "c3_content_fingerprint": _judge_c3(row_counts, samples),
        "c4_pg_restore_rc": _judge_c4(pg_restore_rc, pg_restore_stderr),
    }
    failed = [k for k, v in criteria.items() if not v["ok"]]
    status = (
        "passed" if not failed else (next((s for k, s in _STATUS_BY_FAILED if k in failed), _STATUS_RESTORE_FAILED))
    )
    return {
        "pass": not failed,
        "status": status,
        "failed_criteria": failed,
        "criteria": criteria,
        "criteria_version": _CRITERIA_VERSION,
        "criteria_change_note": _CRITERIA_CHANGE_NOTE,
        "legacy_judge_note": _LEGACY_JUDGE_NOTE,
        "rows": rows,
    }


#: .env.postgres 缺省时的默认连接用户（PostgreSQL 出厂默认管理员名，非凭证）
_DEFAULT_PG_USER = "postgres"


def _pg_creds() -> tuple[str, str]:
    """从 config/.env.postgres 读 (user, password)（RULE-SECRETS 管道）。"""
    user, password = _DEFAULT_PG_USER, ""
    env_file = REPO_ROOT / "config/.env.postgres"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("POSTGRES_USER="):
                user = line.split("=", 1)[1].strip()
            elif line.startswith("POSTGRES_PASSWORD="):
                password = line.split("=", 1)[1].strip()
    return user, password


def _pg_bin(name: str) -> str:
    """定位 pg_dump/psql/pg_restore（PATH 优先，回退 Program Files 最新版本）。"""
    found = None
    try:
        found = name if os.path.basename(name) else None
    except Exception:  # noqa: BLE001
        found = None
    for base in (r"C:\Program Files\PostgreSQL",):
        root = Path(base)
        if root.is_dir():
            versions = sorted((int(p.name) for p in root.iterdir() if p.name.isdigit()), reverse=True)
            for v in versions:
                exe = root / str(v) / "bin" / name
                if exe.exists():
                    return str(exe)
    return found or name


def _find_latest_dump(explicit: str | None) -> Path | None:
    if explicit:
        p = Path(explicit)
        return p if p.exists() else None
    root = Path("G:/backup/db_dumps")
    candidates = (
        sorted(root.glob("**/depgraph.dump"), key=lambda p: p.stat().st_mtime, reverse=True) if root.exists() else []
    )
    return candidates[0] if candidates else None


def _count_rows(host: str, user: str, password: str, db: str, table: str, psql: str) -> int:
    env = {**os.environ, "PGPASSWORD": password}
    r = run_subprocess_hidden(
        [psql, "-h", host, "-U", user, "-d", db, "-t", "-A", "-c", _SQL_COUNT_ROWS.format(table)],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )
    if r.returncode != 0:
        raise RuntimeError(f"count {db}.{table} failed: {r.stderr[:200]}")
    return int((r.stdout or "0").strip() or 0)


def _psql_rows(host: str, user: str, password: str, db: str, sql: str, psql: str) -> list[list[str]]:
    """跑一条只读 SQL，按 \\x01 分隔取回多列结果（C1/C3 取数面）。"""
    env = {**os.environ, "PGPASSWORD": password}
    r = run_subprocess_hidden(
        [psql, "-h", host, "-U", user, "-d", db, "-t", "-A", "-F", "\x01", "-c", sql],
        capture_output=True,
        text=True,
        env=env,
        timeout=600,
    )
    if r.returncode != 0:
        raise RuntimeError(f"query on {db} failed: {(r.stderr or '')[:200]}")
    return [ln.split("\x01") for ln in (r.stdout or "").splitlines() if ln.strip()]


def _list_base_tables(host: str, user: str, password: str, psql: str, db: str) -> list[str]:
    """C1 取数：某库 public 下基表名列表。"""
    return [row[0] for row in _psql_rows(host, user, password, db, _SQL_LIST_BASE_TABLES, psql)]


def _pk_literal(table: str, value: str) -> str:
    """把取回的主键边界值渲染成谓词字面量（数值裸量 / 文本引号量，内嵌单引号翻倍转义）。

    边界值来自演练库自身（不是外部输入），但文本主键可能含单引号，故仍走转义；
    数值主键位拿到非数值 = 取数面被污染 → 直接抛（fail-visible，不拼出可注入的 SQL）。
    """
    if _PK_NUMERIC.get(table):
        if not value.lstrip("-").isdigit():
            raise ValueError(f"数值主键位拿到非数值边界值: {value!r}")
        return value
    return "'" + value.replace("'", "''") + "'"


def _digest_expr(table: str) -> str:
    """某表稳定列的行指纹表达式（列清单见 _STABLE_COLUMNS，NULL 显式占位）。"""
    cols = ", ".join(f"coalesce({c}::text, '<NULL>')" for c in _STABLE_COLUMNS[table])
    return _DIGEST_EXPR.format(cols=cols)


def _fetch_table_sample(
    host: str,
    user: str,
    password: str,
    psql: str,
    table: str,
    n: int,
    skip: int,
) -> dict:
    """C3 取数：头段 + 快照边界锚定尾段两段有界样本，交回纯函数取共有主键。

    只读取数；尾段失败降级为「仅头段」并留 error 读数（头段足以裁决，不因此判红）。
    """
    pk, order, agg = _PK_OF[table], _PK_ORDER[table], _digest_expr(table)
    head_sql = _SQL_SAMPLE_ASC.format(pk=pk, agg=agg, table=table, order=order, n=n)
    live: list[tuple[str, str]] = [(r[0], r[1]) for r in _psql_rows(host, user, password, _LIVE_DB, head_sql, psql)]
    drill: list[tuple[str, str]] = [(r[0], r[1]) for r in _psql_rows(host, user, password, _DRILL_DB, head_sql, psql)]
    regions: dict = {"head_live": len(live), "head_drill": len(drill)}
    try:
        bnd = _psql_rows(
            host,
            user,
            password,
            _DRILL_DB,
            _SQL_SAMPLE_RANGE_BOUND.format(pk=pk, table=table, order=order, n=n, skip=skip),
            psql,
        )
        lo_raw = bnd[0][0] if bnd and bnd[0][0] else ""
        hi_raw = bnd[0][1] if bnd and len(bnd[0]) > 1 else ""
        if lo_raw and hi_raw:
            range_sql = _SQL_SAMPLE_RANGE.format(
                pk=pk,
                agg=agg,
                table=table,
                order=order,
                n=n,
                lo=_pk_literal(table, lo_raw),
                hi=_pk_literal(table, hi_raw),
            )
            live_tail = [(r[0], r[1]) for r in _psql_rows(host, user, password, _LIVE_DB, range_sql, psql)]
            drill_tail = [(r[0], r[1]) for r in _psql_rows(host, user, password, _DRILL_DB, range_sql, psql)]
            live += live_tail
            drill += drill_tail
            regions.update({"tail_live": len(live_tail), "tail_drill": len(drill_tail), "tail_range": [lo_raw, hi_raw]})
        else:
            regions["tail_error"] = "演练库尾段区间不可得（表为空或行数不足 skip）"
    except Exception as exc:  # noqa: BLE001 — 尾段降级为仅头段，读数留痕
        regions["tail_error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
    return {"live": live, "drill": drill, "regions": regions}


def _drop_drill_db(host: str, user: str, password: str, psql: str) -> dict:
    """确保演练库不存在（普通 DROP 打不动活跃连接时走 FORCE，最后复核存在性）。

    残留演练库会带着上一次的表与数据，本次恢复在其上叠加会造出 drill≈2×live 的假象
    （09-26 实测残留态 nodes 25338 vs live 12708）；只 DROP 本脚本自建的临时库。
    """
    env = {**os.environ, "PGPASSWORD": password}
    reading: dict = {"absent": False}
    for sql, tag in ((_SQL_DROP_DRILL_DB, "plain"), (_SQL_DROP_DRILL_DB_FORCE, "force")):
        rc = run_subprocess_hidden(
            [psql, "-h", host, "-U", user, "-d", "postgres", "-c", sql],
            capture_output=True,
            text=True,
            env=env,
            timeout=120,
        ).returncode
        reading[f"drop_{tag}_rc"] = rc
        try:
            reading["absent"] = int(_psql_rows(host, user, password, "postgres", _SQL_DRILL_DB_EXISTS, psql)[0][0]) == 0
        except Exception:  # noqa: BLE001 — 复核失败按「未确认清理」处置
            reading["absent"] = False
        if reading["absent"]:
            reading["absent_via"] = tag
            return reading
    reading["absent_via"] = None
    return reading


def run_drill(
    dump_path: str | None = None,
    host: str = "localhost",
    *,
    sample_rows: int = _DEFAULT_SAMPLE_ROWS,
    sample_skip: int = _DEFAULT_SAMPLE_SKIP,
    staleness_limit: int | None = _DEFAULT_STALENESS_LIMIT,
    live_db: str = _LIVE_DB,
    keep_drill_db: bool = False,
) -> dict:
    """执行一次恢复演练并返回报告 dict（四条件判据见 judge_drill / [INVARIANTS]）。"""
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    user, password = _pg_creds()
    psql, pg_restore = _pg_bin("psql.exe"), _pg_bin("pg_restore.exe")
    dump = _find_latest_dump(dump_path)
    report: dict = {
        "started_at": started,
        "drill_db": _DRILL_DB,
        "dump": str(dump) if dump else None,
        "live_db": live_db,
        "status": "failed",
    }
    if dump is None:
        report["error"] = "未找到 depgraph.dump（检查 G:/backup/db_dumps 或 --dump）"
        return report
    env = {**os.environ, "PGPASSWORD": password}
    try:
        report["drill_db_preflight"] = _drop_drill_db(host, user, password, psql)
        run_subprocess_hidden(
            [psql, "-h", host, "-U", user, "-d", "postgres", "-c", _SQL_CREATE_DRILL_DB],
            capture_output=True,
            text=True,
            env=env,
            timeout=120,
            check=True,
        )
        r = run_subprocess_hidden(
            [pg_restore, "-h", host, "-U", user, "-d", _DRILL_DB, "--no-owner", str(dump)],
            capture_output=True,
            text=True,
            env=env,
            timeout=1800,
        )
        report["pg_restore_rc"] = r.returncode
        report["pg_restore_stderr_excerpt"] = (r.stderr or "")[-4000:]
        # ---- 观测采集（全部只读）：C1 表集合 / C2 行数 / C3 老数据样本 ----
        live_tables = _list_base_tables(host, user, password, psql, live_db)
        drill_tables = _list_base_tables(host, user, password, psql, _DRILL_DB)
        row_counts: dict[str, dict[str, int]] = {}
        samples: dict[str, dict] = {}
        for t in _TABLES:
            live = _count_rows(host, user, password, live_db, t, psql)
            try:
                drill = _count_rows(host, user, password, _DRILL_DB, t, psql)
            except Exception:  # noqa: BLE001 — 演练库缺表（旧 dump）记 -1
                drill = -1
            row_counts[t] = {"live": live, "drill": drill}
            if drill < 0:
                samples[t] = {"live": [], "drill": [], "error": "演练库缺表"}
                continue
            try:
                samples[t] = _fetch_table_sample(host, user, password, psql, t, sample_rows, sample_skip)
            except Exception as exc:  # noqa: BLE001 — 取数失败交 C3 判「样本不可得=红」
                samples[t] = {"live": [], "drill": [], "error": f"{type(exc).__name__}: {str(exc)[:200]}"}
        report.update(
            judge_drill(
                live_tables=live_tables,
                drill_tables=drill_tables,
                row_counts=row_counts,
                samples=samples,
                pg_restore_rc=r.returncode,
                pg_restore_stderr=r.stderr or "",
                staleness_limit=staleness_limit,
            )
        )
        report["sample_params"] = {
            "rows": sample_rows,
            "skip": sample_skip,
            "default_rows": _DEFAULT_SAMPLE_ROWS,
            "default_skip": _DEFAULT_SAMPLE_SKIP,
        }
        report["sample_regions"] = {t: s.get("regions") or {} for t, s in samples.items()}
    except Exception as exc:  # noqa: BLE001 — fail-visible：写报告后由 main() 以非 0 退出
        report["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        if keep_drill_db:
            report["drill_db_dropped"] = False
            report["drill_db_kept"] = "--keep-drill-db 显式保留（复验用）；下次演练的前置清理会收"
        else:
            try:
                cleaning = _drop_drill_db(host, user, password, psql)
                report["drill_db_cleanup"] = cleaning
                report["drill_db_dropped"] = bool(cleaning.get("absent"))
            except Exception as exc:  # noqa: BLE001 — 清理失败留痕，不掩盖判据结论
                report["drill_db_dropped"] = False
                report["drill_db_cleanup_error"] = f"{type(exc).__name__}: {exc}"
    return report


def main() -> int:
    """CLI 入口：跑演练+落报告，pass=0 否则 1（计划任务侧凭退出码可见）。"""
    parser = argparse.ArgumentParser(description="depgraph 账本月度恢复演练（ulib3 T2）")
    parser.add_argument("--dump", default=None, help="指定 dump 路径（默认 G:/backup/db_dumps 最新）")
    parser.add_argument(
        "--sample-rows",
        type=int,
        default=_DEFAULT_SAMPLE_ROWS,
        help=f"C3 每段有界样本行数（默认 {_DEFAULT_SAMPLE_ROWS}）",
    )
    parser.add_argument(
        "--sample-skip",
        type=int,
        default=_DEFAULT_SAMPLE_SKIP,
        help=f"C3 尾段自快照边界回退行数（默认 {_DEFAULT_SAMPLE_SKIP}）",
    )
    parser.add_argument(
        "--staleness-limit",
        type=int,
        default=_DEFAULT_STALENESS_LIMIT,
        help="C2 陈旧度硬阈值（live-drill 行数差上界）；默认不设=只入报告读数不判红",
    )
    parser.add_argument("--keep-drill-db", action="store_true", help="复验用：演练后保留临时库（默认必 DROP）")
    args = parser.parse_args()
    report = run_drill(
        args.dump,
        sample_rows=args.sample_rows,
        sample_skip=args.sample_skip,
        staleness_limit=args.staleness_limit,
        keep_drill_db=args.keep_drill_db,
    )
    out = REPO_ROOT / "logs" / f"restore_drill_{time.strftime('%Y%m%d_%H%M%S')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"restore drill status={report['status']} pass={report.get('pass')} report={out}")
    print(
        "criteria="
        + json.dumps({k: bool(v.get("ok")) for k, v in (report.get("criteria") or {}).items()}, ensure_ascii=False)
    )
    return 0 if report.get("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
