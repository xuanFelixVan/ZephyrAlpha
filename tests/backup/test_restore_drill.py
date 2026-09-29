# [A_test] module_id: MOD-INF-043 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md | §dr-drill
# [MODULE] tests.backup.test_restore_drill
# [DOMAIN] D_AUDITTEST
# [DEPENDENCIES] scripts.backup.restore_drill (judge_drill/run_drill/_classify_pg_restore_stderr)
# [CONSUMERS] pytest tests/backup
# [STARTUP] manual
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
# noqa: m11-perm-manual-legitimate  M11豁免: 单测由 pytest 触发，非常驻进程
"""test_restore_drill.py — 月度恢复演练判据（P-3R2）测试：红绿对拍，不连真库。

大白话：备份演练的"尺子"以前要求"还原出来的库必须和正在用的库一模一样"，
可是还原用的是历史快照，活库一直在长个儿，所以这把尺子永远量出红灯。
本测试用 2026-09-25 月检的真实数字做对拍：旧尺判红、新尺判绿；
再反过来构造"演练库比活库还多行""表少一张""老数据内容被改花"三种真故障，
证明新尺把它们全判红——即新尺不是"放宽到永远绿"，而是"该绿能绿、该红必红"。

覆盖：
- judge_drill 纯函数四条件（C1 表集合/C2 行数方向性/C3 老数据指纹/C4 pg_restore stderr 分类）
- 红绿对拍：同一份 09-25 实测数据上旧判据 False、新判据 True
- 陈旧度只作读数不作硬阈值；显式 --staleness-limit 时才参与裁决
- run_drill 全链路（假 psql/pg_restore，零真实连接）：报告 schema 只增不改不删、临时库必被 DROP
- 真故障必须可见：unknown pg_restore 错误 / 样本为空 / 内容指纹不等 → pass=False 且退出码非 0

测试隔离：全部走 tmp_path，不写 data/ 与 logs/ 生产路径，不连生产库。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_DIR = _REPO_ROOT / "scripts" / "backup"
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import restore_drill as rd  # noqa: E402

# ── 2026-09-25 22:05 月检实测数（logs/restore_drill_20260925_220551.json） ──────────
_REAL_0925_ROWS = {
    "lib_assets": {"live": 44565, "drill": 44524},  # 活库在 dump 之后多了 41 行
    "lib_events": {"live": 1634702, "drill": 1483550},  # 多了 151152 行
    "nodes": {"live": 12669, "drill": 12656},  # 多了 13 行
}
#: 09-25/09-26 实测 pg_restore stderr 原文（三条已知良性；zh_CN 本地化译名保留原样）
_REAL_BENIGN_STDERR = (
    'pg_restore: error: could not execute query: 错误:  模式 "public" 已经存在\n'
    "Command was: CREATE SCHEMA public;\n"
    "\n"
    "\n"
    "pg_restore: error: could not execute query: 错误:  permission denied to change default privileges\n"
    "Command was: ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public "
    "GRANT SELECT ON SEQUENCES TO zephyr;\n"
    "\n"
    "\n"
    "pg_restore: error: could not execute query: 错误:  permission denied to change default privileges\n"
    "Command was: ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public "
    "GRANT SELECT ON TABLES TO zephyr;\n"
    "\n"
    "pg_restore: warning: errors ignored on restore: 3\n"
)


def _legacy_verdict(row_counts: dict[str, dict[str, int]]) -> bool:
    """复刻 P-3R1 旧判据（140/142 行原式）：三表 drill==live 精确相等才算过。"""
    return all(v["drill"] == v["live"] for v in row_counts.values())


def _table_names(n: int, prefix: str = "tbl_") -> list[str]:
    return [f"{prefix}{i:03d}" for i in range(n)]


def _sample(pairs: list[tuple[str, str]]) -> list[tuple[str, str]]:
    return list(pairs)


def _consistent_samples(row_counts: dict[str, dict[str, int]]) -> dict[str, dict]:
    """构造"两侧共有主键上内容完全一致"的样本（等价于真库里那段不会再变的老数据）。"""
    out: dict[str, dict] = {}
    for t, v in row_counts.items():
        n = min(v["drill"], 50)
        pairs = [(f"{t}-pk-{i:05d}", f"digest-{i % 7}") for i in range(n)]
        out[t] = {"live": _sample(pairs), "drill": _sample(pairs), "regions": {}}
    return out


def _judge(row_counts, live_tables, drill_tables, samples, rc=1, stderr=_REAL_BENIGN_STDERR, **kw):
    return rd.judge_drill(
        live_tables=live_tables,
        drill_tables=drill_tables,
        row_counts=row_counts,
        samples=samples,
        pg_restore_rc=rc,
        pg_restore_stderr=stderr,
        **kw,
    )


# ── 红绿对拍：本车道要修的那条病 ─────────────────────────────────────────


def test_red_green_pair_on_real_0925_numbers():
    """同一份 09-25 实测数据：旧判据（精确相等）判红，新判据（四条件合取）判绿。

    这就是处方 P-3 定的"尺坏不是数据坏"——活库在 dump 之后增长了 41/151152/13 行。
    """
    live_tables, drill_tables = _table_names(89), _table_names(89)
    samples = _consistent_samples(_REAL_0925_ROWS)

    assert _legacy_verdict(_REAL_0925_ROWS) is False, "旧尺在增长场景下必须判红（这就是恒红病本身）"

    rep = _judge(_REAL_0925_ROWS, live_tables, drill_tables, samples)
    assert rep["pass"] is True, json.dumps(rep["failed_criteria"], ensure_ascii=False)
    assert rep["status"] == "passed"
    assert rep["criteria_version"] == rd._CRITERIA_VERSION
    # 陈旧度只作读数，不参与裁决
    assert rep["rows"]["lib_events"]["staleness"] == 151152
    assert rep["rows"]["lib_assets"]["staleness"] == 41
    assert rep["rows"]["lib_assets"]["match"] is False  # 旧字段留档，语义不变但不作裁决


@pytest.mark.parametrize("growth", [(41, 150000, 13), (1, 1, 1), (0, 0, 0)])
def test_new_criteria_tolerates_any_live_growth(growth):
    """活库增长多少行都不该让判据变红（增长=时点差，不是故障）。"""
    base = {"lib_assets": 44524, "lib_events": 1483550, "nodes": 12656}
    rows = {t: {"live": base[t] + g, "drill": base[t]} for t, g in zip(base, growth, strict=True)}
    rep = _judge(rows, _table_names(89), _table_names(89), _consistent_samples(rows))
    assert rep["pass"] is True, rep["failed_criteria"]


# ── 真故障必须判红（新尺不是"放宽到永远绿"） ────────────────────────────


def test_drill_exceeding_live_is_red():
    """演练库比活库还多行 → 历史快照不可能发生 → 判红（09-26 实测污染态 nodes 25338>12708）。"""
    rows = dict(_REAL_0925_ROWS)
    rows["nodes"] = {"live": 12708, "drill": 25338}
    rep = _judge(rows, _table_names(89), _table_names(89), _consistent_samples(rows))
    assert rep["pass"] is False
    assert rep["status"] == "row_mismatch"
    assert "c2_row_direction" in rep["failed_criteria"]
    assert rep["rows"]["nodes"]["ok"] is False


def test_missing_table_in_drill_is_red():
    """表集合缺一张 → 判红，且点名是哪张。"""
    live_tables = _table_names(89)
    drill_tables = [t for t in live_tables if t != "tbl_042"]
    rep = _judge(_REAL_0925_ROWS, live_tables, drill_tables, _consistent_samples(_REAL_0925_ROWS))
    assert rep["pass"] is False
    assert rep["status"] == "table_set_mismatch"
    assert rep["criteria"]["c1_table_set_equal"]["missing_in_drill"] == ["tbl_042"]


def test_extra_table_in_drill_is_red():
    live_tables, drill_tables = _table_names(89), _table_names(90)
    rep = _judge(_REAL_0925_ROWS, live_tables, drill_tables, _consistent_samples(_REAL_0925_ROWS))
    assert rep["pass"] is False
    assert rep["criteria"]["c1_table_set_equal"]["extra_in_drill"] == ["tbl_089"]


def test_content_divergence_on_shared_old_rows_is_red():
    """共有老数据的稳定列被改花 → C3 判红并点名主键（列值级真故障，非陈旧度）。"""
    rows = _REAL_0925_ROWS
    samples = _consistent_samples(rows)
    live_pairs = list(samples["nodes"]["live"])
    live_pairs[3] = (live_pairs[3][0], "TAMPERED")
    samples["nodes"]["live"] = live_pairs
    rep = _judge(rows, _table_names(89), _table_names(89), samples)
    assert rep["pass"] is False
    assert rep["status"] == "content_mismatch"
    c3 = rep["criteria"]["c3_content_fingerprint"]["tables"]["nodes"]
    assert c3["mismatched_pk_count"] == 1
    assert c3["mismatched_pk_sample"] == ["nodes-pk-00003"]
    assert c3["fingerprint_match"] is False


def test_empty_shared_sample_is_red_not_silent():
    """共有主键为空 = 内容一致性不可判 → 判红（不许静默放行，也不许当作"没数据所以通过"）。"""
    rows = _REAL_0925_ROWS
    samples = _consistent_samples(rows)
    samples["lib_events"]["live"] = [("only-in-live-1", "d")]
    samples["lib_events"]["drill"] = [("only-in-drill-1", "d")]
    rep = _judge(rows, _table_names(89), _table_names(89), samples)
    assert rep["pass"] is False
    assert rep["criteria"]["c3_content_fingerprint"]["tables"]["lib_events"]["sample_size"] == 0


def test_missing_drill_table_marks_count_unavailable_and_red():
    """演练库缺被核表（count=-1）→ C2 判红，旧字段 drill 仍为 -1。"""
    rows = dict(_REAL_0925_ROWS)
    rows["nodes"] = {"live": 12669, "drill": -1}
    samples = _consistent_samples(_REAL_0925_ROWS)
    del samples["nodes"]
    rep = _judge(rows, _table_names(89), _table_names(89), samples)
    assert rep["pass"] is False
    assert rep["rows"]["nodes"]["drill"] == -1
    assert "c2_row_direction" in rep["failed_criteria"]


# ── C4：pg_restore 返回码分类 ────────────────────────────────────────────


def test_benign_stderr_set_from_real_run():
    """09-25/09-26 实测三条良性：命中已知集合 → 记录并继续（不判红，也不静默吞掉）。"""
    verdict, detail = rd._classify_pg_restore_stderr(_REAL_BENIGN_STDERR, 1)
    assert verdict == "benign_only"
    assert detail["error_count"] == 3
    assert detail["benign_matched"]["benign-schema-public-exists"] == 1
    assert detail["benign_matched"]["benign-alter-default-privileges"] == 2
    assert detail["unknown_errors"] == []


def test_unknown_pg_restore_error_is_fail_visible():
    """集合外错误（例：COPY 中途失败）→ 判红并留原始片段。"""
    stderr = _REAL_BENIGN_STDERR + (
        "pg_restore: error: could not execute query: 错误:  duplicate key value violates "
        'unique constraint "nodes_pkey"\nCommand was: COPY public.nodes (node_id, ...) FROM stdin;\n'
    )
    verdict, detail = rd._classify_pg_restore_stderr(stderr, 1)
    assert verdict == "unknown"
    assert any("duplicate key" in u.get("error", "") for u in detail["unknown_errors"])
    rows = _REAL_0925_ROWS
    rep = _judge(rows, _table_names(89), _table_names(89), _consistent_samples(rows), rc=1, stderr=stderr)
    assert rep["pass"] is False
    assert rep["status"] == "pg_restore_error_unclassified"


def test_nonzero_rc_without_parsable_error_is_red():
    """非零但拿不到可解析错误行 = 不可证明良性 → 判红（不许"看不见就当没事"）。"""
    verdict, detail = rd._classify_pg_restore_stderr("some opaque failure", 2)
    assert verdict == "unknown"
    assert detail["unknown_errors"]
    rep = _judge(
        _REAL_0925_ROWS,
        _table_names(89),
        _table_names(89),
        _consistent_samples(_REAL_0925_ROWS),
        rc=2,
        stderr="some opaque failure",
    )
    assert rep["pass"] is False


@pytest.mark.parametrize(
    "locale_stderr",
    [
        # zh_CN 本地化译文
        'pg_restore: error: could not execute query: 错误:  模式 "public" 已经存在\nCommand was: CREATE SCHEMA public;\n',
        # en_US 原文
        'pg_restore: error: could not execute query: ERROR:  schema "public" already exists\n'
        "Command was: CREATE SCHEMA public;\n",
    ],
)
def test_benign_matching_is_locale_independent(locale_stderr):
    """良性判定吃 Command was 的 SQL 文本 + 双语关键词，不被 psql 本地化译文绑架。"""
    assert rd._classify_pg_restore_stderr(locale_stderr, 1)[0] == "benign_only"


def test_zero_rc_with_noise_still_passes():
    assert rd._classify_pg_restore_stderr("pg_restore: warning: something\n", 0)[0] == "clean"


def test_error_command_pairing_is_positional_not_zipindexed():
    """回归：三条错误必须各自配到自己的 Command was（早期 DOTALL 版本会把第 2/3 条 command 吞空）。"""
    pairs = rd._iter_restore_errors(_REAL_BENIGN_STDERR)
    assert len(pairs) == 3
    assert all(cmd for _, cmd in pairs), pairs
    assert pairs[0][1].startswith("CREATE SCHEMA public")
    assert all(p[1].startswith("ALTER DEFAULT PRIVILEGES") for p in pairs[1:])


# ── C2：陈旧度是读数不是新恒红阈值 ───────────────────────────────────────


def test_staleness_limit_off_by_default_and_configurable():
    rows = {
        "lib_assets": {"live": 900000, "drill": 44524},
        "lib_events": {"live": 1483550, "drill": 1483550},
        "nodes": {"live": 12656, "drill": 12656},
    }
    samples = _consistent_samples(rows)
    tables = _table_names(89)
    assert _judge(rows, tables, tables, samples)["pass"] is True, "默认不设硬阈值：再陈旧也不恒红"
    rep = _judge(rows, tables, tables, samples, staleness_limit=1000)
    assert rep["pass"] is False
    assert rep["rows"]["lib_assets"]["staleness"] == 855476
    assert rep["rows"]["lib_assets"]["staleness_hard_limited"] is True
    assert "staleness_limit=1000" in rep["criteria"]["c2_row_direction"]["rule"]


# ── run_drill 全链路（假 psql/pg_restore：零真实连接，报告 schema 只增不改不删） ──


class _FakeProc:
    def __init__(self, rc: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.returncode, self.stdout, self.stderr = rc, stdout, stderr


class _FakeStore:
    """内存版"两个库"：生产库持续增长，演练库是历史快照（缺最新那批行）。"""

    def __init__(self, tables: list[str], rows: dict[str, dict[str, int]]) -> None:
        self.tables, self.rows = tables, rows
        self.statements: list[tuple[str, str]] = []
        self.drill_alive = False
        self.drops = 0

    def handle(self, argv: list[str]) -> _FakeProc:
        exe = Path(argv[0]).name.lower()
        if exe.startswith("pg_restore"):
            self.drill_alive = True
            return _FakeProc(1, "", _REAL_BENIGN_STDERR)
        sql = argv[argv.index("-c") + 1]
        db = argv[argv.index("-d") + 1]
        self.statements.append((db, sql))
        if sql.startswith("CREATE DATABASE"):
            assert not self.drill_alive, "演练库必须先不存在，否则会在残留库上叠加出重复行"
            self.drill_alive = True
            return _FakeProc(0, "CREATE DATABASE\n")
        if sql.startswith("DROP DATABASE"):
            self.drops += 1
            self.drill_alive = False
            return _FakeProc(0, "DROP DATABASE\n")
        if "FROM pg_database" in sql:
            return _FakeProc(0, "1\n" if self.drill_alive else "0\n")
        if "FROM pg_tables" in sql:
            if not self.drill_alive and db == rd._DRILL_DB:
                return _FakeProc(1, "", "database does not exist")
            return _FakeProc(0, "\n".join(self.tables) + "\n")
        if "count(*)" in sql:
            table = sql.split("FROM", 1)[1].strip().split(";", 1)[0].strip()
            if db == rd._DRILL_DB and not self.drill_alive:
                return _FakeProc(1, "", "table missing")
            n = self.rows[table]["drill" if db == rd._DRILL_DB else "live"]
            return _FakeProc(0, f"{n}\n")
        if sql.startswith("SELECT min(_s.k)"):
            table = sql.split("FROM ", 2)[2].split(" ORDER BY", 1)[0]
            n = self.rows[table]["drill"]
            # 演练库尾段主键区间（数值口径，跨 text/bigint 两侧一致）
            return _FakeProc(0, f"{n - 1200}\x01{n - 201}\n")
        if "::text, md5(" in sql:
            table = sql.split("FROM ", 2)[2].split(" ", 1)[0].strip("(")
            side = "drill" if db == rd._DRILL_DB else "live"
            n = self.rows[table][side]
            where = " BETWEEN " in sql
            if where:
                m = re.search(r"BETWEEN\s+(.+?)\s+AND\s+(.+?)\s+ORDER BY", sql)
                assert m, f"假 psql 解析区间谓词失败: {sql[:200]}"
                lo_n = int(m.group(1).strip().strip("'"))
                hi_n = int(m.group(2).strip().strip("'"))
            else:
                lo_n, hi_n = 0, max(0, min(self.rows[table]["live"], self.rows[table]["drill"]) - 1)
            out = []
            # 直接在窗口内取值（勿扫全表：lib_events 百万级会让单测跑一分多钟）
            drill_n = self.rows[table]["drill"]
            start = max(lo_n, 0)
            for i in range(start, min(hi_n, min(n, self.rows[table]["live"], drill_n - 1)) + 1):
                # 老数据两侧字节一致；dump 之后新增的行只存在于 live（i>=drill 时演练库没有）
                if i >= drill_n:
                    continue
                out.append(f"{i}\x01digest-{i % 7}")
                if len(out) >= 1500:
                    break
            return _FakeProc(0, ("\n".join(out) + "\n") if out else "")
        raise AssertionError(f"假 psql 未覆盖的语句: {sql[:160]}")


@pytest.fixture()
def fake_drill(monkeypatch, tmp_path):
    dump = tmp_path / "depgraph.dump"
    dump.write_bytes(b"fake toc")

    store = _FakeStore(_table_names(89), {t: dict(v) for t, v in _REAL_0925_ROWS.items()})
    store.rows = {t: {"live": v["live"], "drill": v["drill"]} for t, v in _REAL_0925_ROWS.items()}
    monkeypatch.setattr(rd, "_pg_creds", lambda: ("fake_user", "fake_pw"))
    monkeypatch.setattr(rd, "_pg_bin", lambda name: f"/fake/bin/{name}")

    def _fake_run(argv, **kw):
        return store.handle(list(argv))

    monkeypatch.setattr(rd, "run_subprocess_hidden", _fake_run)
    return store, dump


def test_run_drill_end_to_end_passes_with_growing_live(fake_drill):
    store, dump = fake_drill
    rep = rd.run_drill(str(dump))
    assert rep["pass"] is True, json.dumps(rep.get("criteria", {}), ensure_ascii=False)[:800]
    assert rep["status"] == "passed"
    assert rep["pg_restore_rc"] == 1 and rep["criteria"]["c4_pg_restore_rc"]["verdict"] == "benign_only"
    assert rep["rows"]["lib_assets"]["match"] is False  # 旧字段仍在且仍如实记录"精确不等"
    assert rep["drill_db_dropped"] is True
    assert store.drill_alive is False, "演练结束必须 DROP 临时库"
    assert store.drops >= 1
    # 头段与快照边界尾段都取到了数（否则 C3 只在半边样本上成立，覆盖不足）
    for t, reg in rep["sample_regions"].items():
        assert "tail_error" not in reg, (t, reg)
        assert reg["head_live"] > 0 and reg["head_drill"] > 0, (t, reg)
        assert reg["tail_live"] > 0 and reg["tail_drill"] > 0, (t, reg)
    assert rep["criteria"]["c3_content_fingerprint"]["tables"]["nodes"]["sample_size"] > 2000


def test_run_drill_report_schema_is_additive_only(fake_drill, monkeypatch, tmp_path):
    """下游可能读旧四字段：pass/status/rows/pg_restore_rc 必须仍在，rows[t] 仍含 live/drill/match。"""
    store, dump = fake_drill
    monkeypatch.setattr(rd, "REPO_ROOT", tmp_path)
    (tmp_path / "logs").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(sys, "argv", ["restore_drill.py"])
    assert rd.main() == 0
    written = list((tmp_path / "logs").glob("restore_drill_*.json"))
    assert len(written) == 1
    rep = json.loads(written[0].read_text(encoding="utf-8"))
    for key in ("started_at", "drill_db", "dump", "status", "pg_restore_rc", "pass", "rows", "drill_db_dropped"):
        assert key in rep, f"报告 schema 缺既有字段 {key}"
    for t in rd._TABLES:
        assert {"live", "drill", "match"} <= set(rep["rows"][t]), f"rows[{t}] 旧键被改动"
    # 只增：新判据细节字段
    for key in (
        "criteria",
        "criteria_version",
        "criteria_change_note",
        "failed_criteria",
        "pg_restore_stderr_excerpt",
        "sample_params",
    ):
        assert key in rep, f"新判据字段 {key} 未落入报告"
    assert rep["criteria"]["c1_table_set_equal"]["live_table_count"] == 89


def test_run_drill_fail_visible_on_unknown_restore_error(fake_drill, monkeypatch, tmp_path):
    """pg_restore 报集合外错误 → 退出码非 0（计划任务侧可见），不许静默绿。"""
    store, dump = fake_drill

    def _boom(argv, **kw):
        argv = list(argv)
        if Path(argv[0]).name.lower().startswith("pg_restore"):
            store.drill_alive = True
            return _FakeProc(
                1,
                "",
                _REAL_BENIGN_STDERR + "pg_restore: error: could not execute query: 错误:  out of memory\n"
                "Command was: COPY public.nodes FROM stdin;\n",
            )
        return store.handle(argv)

    monkeypatch.setattr(rd, "run_subprocess_hidden", _boom)
    monkeypatch.setattr(sys, "argv", ["restore_drill.py", "--dump", str(dump)])
    monkeypatch.setattr(rd, "REPO_ROOT", tmp_path)
    (tmp_path / "logs").mkdir(parents=True, exist_ok=True)
    assert rd.main() == 1, "判红必须以非 0 退出码让计划任务侧可见"
    rep_file = sorted((tmp_path / "logs").glob("restore_drill_*.json"))[-1]
    rep = json.loads(rep_file.read_text(encoding="utf-8"))
    assert rep["pass"] is False
    assert rep["status"] == "pg_restore_error_unclassified"
    assert rep["criteria"]["c4_pg_restore_rc"]["unknown_errors"], "集合外错误必须留原始片段入报告"
    assert store.drill_alive is False, "判红也必须清理临时库"
    assert rep["drill_db_dropped"] is True


def test_run_drill_missing_dump_is_reported(monkeypatch, tmp_path):
    monkeypatch.setattr(rd, "_pg_creds", lambda: ("u", "p"))
    monkeypatch.setattr(rd, "_pg_bin", lambda name: f"/fake/{name}")
    rep = rd.run_drill(str(tmp_path / "nope.dump"))
    assert rep["status"] == "failed" and rep.get("pass") is None
    assert "depgraph.dump" in rep["error"]


# ── 取数面细节 ───────────────────────────────────────────────────────────


def test_text_pk_sample_is_pinned_to_collate_c():
    """演练库 datcollate 与生产库不同（09-26 实测 C vs Chinese_PRC.936），文本主键必须钉 COLLATE "C"。"""
    assert 'COLLATE "C"' in rd._PK_ORDER["lib_assets"]
    sql = rd._SQL_SAMPLE_ASC.format(pk="asset_id", agg="X", table="lib_assets", order=rd._PK_ORDER["lib_assets"], n=10)
    assert 'ORDER BY asset_id COLLATE "C" ASC' in sql


def test_numeric_pk_literal_is_bare_and_text_literal_is_escaped():
    assert rd._pk_literal("nodes", "15208297") == "15208297"
    assert rd._pk_literal("lib_assets", "MOD:a'b") == "'MOD:a''b'"
    with pytest.raises(ValueError):
        rd._pk_literal("nodes", "1; DROP TABLE nodes")  # 数值主键位不接受非数值注入面


def test_stable_columns_exclude_measured_mutable_columns():
    """09-26 逐列实测：这些列在 dump 之后仍被改写，进了指纹就会退化成恒红尺。"""
    forbidden = {
        "lib_assets": {"fingerprint_sha256", "fingerprint_aux", "built_at", "generation"},
        "nodes": {"content_hash", "build_status", "last_verified", "granularity"},
    }
    for t, bad in forbidden.items():
        assert not (set(rd._STABLE_COLUMNS[t]) & bad), f"{t} 稳定列混入了可变列"


def test_c2_direction_uses_strict_inequality_on_equal_counts():
    """dump 与活库恰好同刻（行数相等）也是允许的——方向性判据不能把"相等"误判成故障。"""
    rows = {t: {"live": v["drill"], "drill": v["drill"]} for t, v in _REAL_0925_ROWS.items()}
    rep = _judge(rows, _table_names(89), _table_names(89), _consistent_samples(rows))
    assert rep["pass"] is True
    assert all(v["match"] is True for v in rep["rows"].values())


# ============ H06（2026-09-29 SW11）：演练库 collate 保真（template0） ============


def test_h06_create_drill_sql_pins_template0_and_live_locale():
    """建库语句必须 template0+显式三 locale——治本 datcollate 继承 template1 的零交集根因。"""
    sql = rd._build_create_drill_sql("C", "C", "UTF8")
    assert "TEMPLATE template0" in sql
    assert "LC_COLLATE 'C'" in sql
    assert "LC_CTYPE 'C'" in sql
    assert "ENCODING 'UTF8'" in sql
    assert rd._DRILL_DB in sql
    # 旧语句（继承 template1）降级为对照常量，运行面唯一建库入口=_build_create_drill_sql
    assert rd._SQL_CREATE_DRILL_DB_LEGACY == "CREATE DATABASE " + rd._DRILL_DB
    src = Path(rd.__file__).read_text(encoding="utf-8")
    run_face = src.split("def run_drill", 1)[1]
    assert "_SQL_CREATE_DRILL_DB " not in run_face.replace("_SQL_CREATE_DRILL_DB_LEGACY", "")


def test_h06_create_drill_sql_escapes_single_quotes():
    """locale 读数含单引号（如 Windows locale 名带撇号）时 SQL 转义，不破语句。"""
    sql = rd._build_create_drill_sql("Chinese (Simplified)_China.936", "C", "UTF8")
    assert "LC_COLLATE 'Chinese (Simplified)_China.936'" in sql
    evil = "obrien"
    sql2 = rd._build_create_drill_sql(f"{evil}'x", "C", "UTF8")
    assert "LC_COLLATE 'obrien''x'" in sql2


def test_h06_fallback_locale_is_live_measured_values():
    """locale 读数失败回落值=活库 09-26 实测值（C/C/UTF8），回落事实由 run_drill 入报告。"""
    assert rd._DRILL_LOCALE_FALLBACK == ("C", "C", "UTF8")
