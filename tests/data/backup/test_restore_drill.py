# 复活自死袋 q-20261004-st-tests-chief-20261004-0001（等 64 袋同字节）；契约断言按
# T1b(5956914d627)/T1c(aca29fd557) 更正 pass:None->False，假 store 按 T1d 补齐 HEAD 的
# H06 locale 读取面（cad41feb2f），合成 dump 按 T1d 添加，血缘=部分继承。
# 本件证契约与裁决逻辑，不证 dump 真可恢复；月度真跑不得因此撤。
# [A_test] module_id: MOD-INF-043 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md | §dr-drill
# [MODULE] tests.data.backup.test_restore_drill
# [DOMAIN] D_AUDITTEST
# [DEPENDENCIES] scripts.backup.restore_drill (judge_drill/run_drill/_classify_pg_restore_stderr)
# [CONSUMERS] pytest tests/data/backup
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
- 失败支报告契约（T1b/T1c/候裁⑦）：8 键齐备、rows={} 为 dict、json 可序列化；judge_drill 反钉=骨架不过严
- 损坏 dump（0 字节/非归档）：_find_latest_dump 只查存在性不校验格式，唯一拦截面=C4 返回码
- 漂移守卫：假 store 认得的语句面必须覆盖 HEAD 经 run_subprocess_hidden 下发的每一条 SQL
  （restore_drill 日后加查询而假 store 没跟上 → 本件转红，不静默老化）

测试隔离：全部走 tmp_path，不写 data/ 与 logs/ 生产路径，不连生产库。
"""

from __future__ import annotations

import inspect
import json
import re
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
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
    """内存版"两个库"：生产库持续增长，演练库是历史快照（缺最新那批行）。

    分派面必须与 HEAD 的 restore_drill.py 取数面一一对应（H06/cad41feb2f 加了活库 locale
    读取，IN1-32b 加了 restore 前的 DROP SCHEMA public）——漏一条就会落进末尾的
    "未覆盖" 断言，run_drill 只能交出 criteria={} 的失败骨架（本件三条红的真根因）。
    """

    #: 活库实测 locale（09-26 实测 datcollate=C；_DRILL_LOCALE_FALLBACK 同值，
    #: 但 drill_db_locale_source 能分辨"读到"与"回落"，见 H06 专项测试）
    _DEFAULT_LIVE_LOCALE = ("C", "C", "UTF8")

    def __init__(
        self, tables: list[str], rows: dict[str, dict[str, int]], live_locale: tuple[str, str, str] | None = None
    ) -> None:
        self.tables, self.rows = tables, rows
        self.live_locale = live_locale or self._DEFAULT_LIVE_LOCALE
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
            assert "TEMPLATE template0" in sql, "H06 后演练库只能由 template0+显式 locale 建出（旧语句已退役）"
            self.drill_alive = True
            return _FakeProc(0, "CREATE DATABASE\n")
        if sql.startswith("DROP DATABASE"):
            self.drops += 1
            self.drill_alive = False
            return _FakeProc(0, "DROP DATABASE\n")
        if sql.startswith("DROP SCHEMA"):
            # IN1-32b：PG15 createdb 预建 public 与 dump 内 CREATE SCHEMA public 撞车，restore 前重置
            assert db == rd._DRILL_DB and self.drill_alive, "public schema 只重置已建出的演练库"
            return _FakeProc(0, "DROP SCHEMA\n")
        if "datcollate" in sql:
            # H06（cad41feb2f）：建库前读活库实测 locale——三列，_psql_rows 按 \x01 切
            assert "WHERE datname=" in sql, f"locale 语句形态意外: {sql[:120]}"
            return _FakeProc(0, "\x01".join(self.live_locale) + "\n")
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


class _BrokenDumpStore(_FakeStore):
    """dump 文件存在但内容损坏（0 字节/非归档）：pg_restore 报集合外错误。

    取数面与父类全同——因为损坏只在 restore 那一步显形，这正是 _find_latest_dump
    "存在即放行" 的必然后果（唯一拦截面=C4）。
    """

    def handle(self, argv: list[str]) -> _FakeProc:
        argv = list(argv)
        if Path(argv[0]).name.lower().startswith("pg_restore"):
            self.drill_alive = True
            return _FakeProc(1, "", _CORRUPT_DUMP_STDERR)
        return super().handle(argv)


class _NoLocaleStore(_FakeStore):
    """活库 locale 查询拿不到三列（本例回单列）→ run_drill 必须走回落支并如实入报告。"""

    def handle(self, argv: list[str]) -> _FakeProc:
        argv = list(argv)
        if "-c" in argv and "datcollate" in argv[argv.index("-c") + 1]:
            return _FakeProc(0, "0\n")
        return super().handle(argv)


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


def _install_fake_store(monkeypatch, store: _FakeStore) -> None:
    """把假 store 钉到唯一取数口 run_subprocess_hidden（createdb/psql/pg_restore 同一名）。

    HEAD 里所有子进程交互都汇过这一个名字，钉住它=钉住全部 DB 面，零真实连接。
    """
    monkeypatch.setattr(rd, "_pg_creds", lambda: ("fake_user", "fake_pw"))
    monkeypatch.setattr(rd, "_pg_bin", lambda name: f"/fake/bin/{name}")
    monkeypatch.setattr(rd, "run_subprocess_hidden", lambda argv, **kw: store.handle(list(argv)))


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
    assert rep["status"] == "failed" and rep.get("pass") is False
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


# ── T1d 复活补齐：取数面漂移守卫 / 失败支报告契约 / 损坏 dump / H06 locale 读取面 ──

#: 假 store 认得的语句面（与 _FakeStore.handle 的分派一一对应）。每条都必须能在 handle 源码里
#: 找到字面量——否则这份"覆盖了哪些面"的清单就是自说自话（见漂移守卫测试的清单-代码核）。
_FAKE_DISPATCH_KEYS: tuple[str, ...] = (
    "pg_restore",  # exe 级：恢复子进程（C4 观测面）
    "create database",  # 建演练库（H06：template0 + 实测 locale）
    "drop database",  # 演练库清理（plain/FORCE 双通道）
    "drop schema",  # IN1-32b：restore 前重置演练库 public
    "datcollate",  # H06（cad41feb2f）：建库前读活库实测 locale
    "from pg_database",  # 演练库存在性复核
    "from pg_tables",  # C1 表集合
    "count(*)",  # C2 行数
    "select min(_s.k)",  # C3 尾段区间上下界
    "::text, md5(",  # C3 头段/尾段有界样本
)
#: 判据 8 键：成功路径由 judge_drill 一次产出，失败路径由 run_drill 骨架起手带齐（T1b→T1c→候裁⑦）
_JUDGE_KEYS = frozenset(
    {
        "criteria",
        "criteria_change_note",
        "criteria_version",
        "failed_criteria",
        "legacy_judge_note",
        "pass",
        "rows",
        "status",
    }
)
_CRITERIA_KEYS = ("c1_table_set_equal", "c2_row_direction", "c3_content_fingerprint", "c4_pg_restore_rc")
#: 损坏 dump（0 字节/非归档）在 pg_restore 处的形态：没有 `Command was:` 可配对，
#: 良性集合永不命中 → C4=unknown。_find_latest_dump 不校验格式，所以这是唯一拦截面。
_CORRUPT_DUMP_STDERR = "pg_restore: error: input file appears to be truncated: not a valid archive\n"

#: C3/C1 模板占位符的实值（一律取模块自带常量，使渲染出的语句与真跑同形）
_SQL_FILL: dict[str, str] = {
    "db": rd._LIVE_DB,
    "table": "lib_assets",
    "pk": rd._PK_OF["lib_assets"],
    "order": rd._PK_ORDER["lib_assets"],
    "agg": rd._digest_expr("lib_assets"),
    "cols": ", ".join(rd._STABLE_COLUMNS["lib_assets"]),
    "n": str(rd._DEFAULT_SAMPLE_ROWS),
    "skip": str(rd._DEFAULT_SAMPLE_SKIP),
    "lo": "44324",
    "hi": "44524",
}
_TOKEN_RE = re.compile(r"\{([^{}]*)\}")
_SQL_PIECE_RE = re.compile(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|[A-Za-z_][A-Za-z0-9_]*')
_SQL_HEAD = "SELECT|CREATE|DROP|ALTER|WITH|INSERT|UPDATE|TRUNCATE"
#: 全源扫描：SQL 关键字开头的字符串字面量（未来内联在函数体里的语句也逃不掉）
_SQL_LITERAL_RE = re.compile(
    r'"((?:' + _SQL_HEAD + r')\b[^"]*)"|\'((?:' + _SQL_HEAD + r")\b[^\']*)\'",
    re.IGNORECASE,
)


def _render_sql(text: str) -> str:
    """把源码里的 SQL 模板占位符填成具体语句（{_DRILL_DB} 这类直接引用模块常量）。"""

    def _sub(m: re.Match) -> str:
        key = m.group(1).strip()
        if not key:
            return _SQL_FILL["table"]  # _SQL_COUNT_ROWS 的位置参数=表名
        if key in _SQL_FILL:
            return str(_SQL_FILL[key])
        v = getattr(rd, key, None)
        return v if isinstance(v, str) else "1"

    return _TOKEN_RE.sub(_sub, text)


def _sql_fragments_from_source(src: str) -> dict[str, str]:
    """从 restore_drill.py 源码文本还原"经 run_subprocess_hidden 下发的每一条语句"。

    两条抽取路互补：① 模块级 _SQL_* 常量（跨行隐式拼接与 "…" + _VAR + "…" 全部还原成整句）；
    ② 全源扫 SQL 关键字开头的字面量（覆盖内联在函数体里的语句）。②里已被①还原过的片段跳过，
    免得半截片段（如 _SQL_SAMPLE_RANGE 的首行）把断言面弄虚。建库语句另附工厂函数实调结果。
    """
    frags: dict[str, str] = {}
    lines = src.splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"(_SQL_[A-Z0-9_]+)\s*=\s*(.*)$", lines[i])
        if not m:
            i += 1
            continue
        rhs = [m.group(2)]
        j = i + 1
        while j < len(lines) and lines[j][:1] in (" ", "\t"):
            rhs.append(lines[j].strip())
            j += 1
        pieces: list[str] = []
        for tok in _SQL_PIECE_RE.findall(" ".join(rhs)):
            if tok[0] in "\"'":
                pieces.append(_render_sql(tok[1:-1]))
            else:
                v = getattr(rd, tok, None)
                if isinstance(v, str):
                    pieces.append(_render_sql(v))
        frags[m.group(1)] = "".join(pieces)
        i = j
    for idx, lit in enumerate(_SQL_LITERAL_RE.finditer(src)):
        rendered = _render_sql(lit.group(1) or lit.group(2))
        if any(rendered in v for v in frags.values()):
            continue
        frags[f"inline#{idx}"] = rendered
    frags["<_build_create_drill_sql()>"] = rd._build_create_drill_sql(*rd._DRILL_LOCALE_FALLBACK)
    return frags


def _fake_dispatch_verdict(sql: str) -> str:
    """假 store 对一条语句的处置：ok｜stateful（有分支接得住，只是状态前置不合）｜uncovered。

    uncovered（落进 handle 末尾的"未覆盖"分支）就是漂移信号：HEAD 加了取数面而假 store 没跟上。
    """
    best = "uncovered"
    for db, alive in ((rd._LIVE_DB, False), (rd._DRILL_DB, True)):
        store = _FakeStore(_table_names(3), {t: dict(v) for t, v in _REAL_0925_ROWS.items()})
        store.drill_alive = alive
        argv = [
            "/fake/bin/psql.exe",
            "-h",
            "localhost",
            "-U",
            "fake_user",
            "-d",
            db,
            "-t",
            "-A",
            "-F",
            "\x01",
            "-c",
            sql,
        ]
        try:
            store.handle(argv)
            return "ok"
        except AssertionError as exc:
            if "未覆盖" not in str(exc):
                best = "stateful"
    return best


def test_fake_dispatch_covers_every_statement_head_sends():
    """漂移守卫：假 store 认得的语句面 ⊇ HEAD 实际下发的语句面。

    HEAD（scripts/backup/restore_drill.py）新增一条取数查询而这里没补分支 → 本测试转红，
    而不是像死袋那样静默老化（run_drill 只会悄悄交出 criteria={} 的失败骨架）。
    """
    src = (_SCRIPT_DIR / "restore_drill.py").read_text(encoding="utf-8")
    frags = _sql_fragments_from_source(src)
    assert len(frags) >= 12, f"源码抽取失效（只拿到 {len(frags)} 条语句），守卫不能空跑：{sorted(frags)}"

    for label, sql in frags.items():
        hit = [k for k in _FAKE_DISPATCH_KEYS if k in sql.lower()]
        assert hit, f"HEAD 语句 {label} 不在假 store 认得的 key 集内: {sql[:160]}"
        assert _fake_dispatch_verdict(sql) != "uncovered", f"假 psql 未覆盖 HEAD 取数面 {label}: {sql[:160]}"

    # 窄 key 归属（_FAKE_DISPATCH_KEYS 的次序=handle 分派的次序）：HEAD 每个取数面都要落到自己的
    # 专属分支上，不许被宽分支代管——否则"H06 新查询被旧 pg_database 分支悄悄吞掉"这类漂移量不出
    narrow = {next(k for k in _FAKE_DISPATCH_KEYS if k in sql.lower()) for sql in frags.values()}
    expected_surfaces = {
        "create database",
        "drop database",
        "drop schema",
        "datcollate",
        "from pg_database",
        "from pg_tables",
        "count(*)",
        "select min(_s.k)",
        "::text, md5(",
    }
    assert expected_surfaces <= narrow, f"HEAD 取数面缺专属分派: {sorted(expected_surfaces - narrow)}"

    # 清单-代码核：声明的每个 key 必须真在 handle 的分派里（防清单与现实脱节）
    handle_src = inspect.getsource(_FakeStore.handle).lower()
    for key in _FAKE_DISPATCH_KEYS:
        assert key in handle_src, f"key 清单与分派代码漂移：{key} 已不在 _FakeStore.handle 里"

    # 红证（自证可失效）：给源码加一条假查询，守卫必须认它为未覆盖——否则本守卫是摆设
    mutated = src + '\n_SQL_DRIFT_GUARD_SELF_TEST = "SELECT last_autovacuum FROM pg_stat_user_tables"\n'
    extra = {k: v for k, v in _sql_fragments_from_source(mutated).items() if k not in frags}
    assert extra, "漂移守卫自证失效：新增语句没被源码抽取认到"
    for label, sql in extra.items():
        assert _fake_dispatch_verdict(sql) == "uncovered", f"新增语句 {label} 竟被认成已覆盖: {sql[:160]}"


def test_run_drill_failed_skeleton_carries_full_report_contract(tmp_path):
    """失败支骨架（T1b/T1c/候裁⑦）：8 键齐备、rows={} 是 dict、可 json 序列化，语义零改动。"""
    rep = rd.run_drill(str(tmp_path / "absent.dump"))
    assert rep["status"] == "failed"
    assert rep["pass"] is False, "T1b：判不了=不通过，缺键不是未判（消费侧直读不得 KeyError）"
    assert rep["criteria"] == {}, "空 criteria=一条判据都没评估成，绝不冒领 ok"
    assert rep["failed_criteria"] == [], "没评估成的判据不指认为红"
    assert isinstance(rep["rows"], dict) and rep["rows"] == {}, "候裁⑦：rows 初值={}（与成功路径同型），不是 0"
    with pytest.raises(KeyError):
        rep["rows"]["nodes"]  # dict 型 → 读侧按表名取值抛 KeyError；int 初值会抛 TypeError
    assert rep["legacy_judge_note"] == "", "旧尺说明只在真做过裁决时才有意义"
    assert rep["criteria_version"] == "P-3R2" == rd._CRITERIA_VERSION, "尺的版本与轮次无关"
    assert rep["criteria_change_note"] == rd._CRITERIA_CHANGE_NOTE
    assert set(rep) >= _JUDGE_KEYS, f"失败支报告契约缺项: {sorted(_JUDGE_KEYS - set(rep))}"
    json.dumps(rep, ensure_ascii=False)  # 报告必须可落盘（main 直接 dumps）


def test_judge_drill_pure_output_flips_skeleton_to_passed(tmp_path):
    """反钉：失败骨架不是过度严格——键集与 judge_drill 产出同型，评完 update 即 passed。"""
    skeleton = rd.run_drill(str(tmp_path / "absent.dump"))
    judge = rd.judge_drill(
        live_tables=_table_names(89),
        drill_tables=_table_names(89),
        row_counts=_REAL_0925_ROWS,
        samples=_consistent_samples(_REAL_0925_ROWS),
        pg_restore_rc=1,
        pg_restore_stderr=_REAL_BENIGN_STDERR,
    )
    assert set(judge) == _JUDGE_KEYS and len(judge) == 8, sorted(judge)
    assert judge["pass"] is True, judge["failed_criteria"]
    assert tuple(sorted(judge["criteria"])) == tuple(sorted(_CRITERIA_KEYS))
    assert set(skeleton) >= _JUDGE_KEYS, "骨架必须带齐 judge 的 8 键，否则消费侧仍会 KeyError"

    merged = dict(skeleton)
    merged.update(judge)
    assert merged["status"] == "passed"
    assert merged["pass"] is True
    assert merged["failed_criteria"] == []
    assert merged["criteria_version"] == skeleton["criteria_version"], "版本round无关：update 前后同值"
    assert merged["legacy_judge_note"] == rd._LEGACY_JUDGE_NOTE
    assert merged["rows"] and all(t in merged["rows"] for t in rd._TABLES)
    json.dumps(merged, ensure_ascii=False)


@pytest.mark.parametrize("payload", [b"", b"\x00\x01this-is-not-a-pgdump-archive"], ids=["zero-byte", "corrupt"])
def test_broken_dump_is_caught_only_by_c4_pg_restore_rc(monkeypatch, tmp_path, payload):
    """损坏 dump：_find_latest_dump 只查存在性不校验归档格式 → 唯一拦截面=C4 返回码。

    这是既成事实的机器固化（不是新判据）：0 字节/非归档文件照样进演练，
    靠 C4（pg_restore rc + stderr 分类）判红，其余三条件无从分辨损坏。
    """
    dump = tmp_path / "depgraph.dump"
    dump.write_bytes(payload)
    assert rd._find_latest_dump(str(dump)) == dump, "前提：存在即放行，不校验 pg_dump 格式"
    assert rd._find_latest_dump(str(tmp_path / "nope.dump")) is None, "只有不存在才被挡在取数面之前"

    store = _BrokenDumpStore(_table_names(89), {t: dict(v) for t, v in _REAL_0925_ROWS.items()})
    _install_fake_store(monkeypatch, store)
    rep = rd.run_drill(str(dump))
    assert rep.get("error") is None, "损坏 dump 不抛异常：它一路走到对账，由判据兜住"
    c4 = rep["criteria"]["c4_pg_restore_rc"]
    assert c4["ok"] is False and c4["verdict"] == "unknown"
    assert c4["unknown_errors"], "集合外错误必须留原始片段入报告"
    assert rep["failed_criteria"] == ["c4_pg_restore_rc"], "C4 是唯一拦截面"
    for key in _CRITERIA_KEYS[:3]:
        assert rep["criteria"][key]["ok"] is True, f"{key} 对损坏 dump 无从判红（这正是 C4 不可替代的原因）"
    assert rep["status"] != "passed"
    assert rep["pass"] is False
    assert store.drill_alive is False and rep["drill_db_dropped"] is True, "判红也必须清理演练库"


@pytest.mark.parametrize(
    "live_locale, expected_source",
    [(("C", "C", "UTF8"), "live_db"), (("en_US.UTF-8", "en_US.UTF-8", "UTF8"), "live_db")],
    ids=["measured-c", "measured-en_US"],
)
def test_run_drill_h06_creates_drill_db_from_live_measured_locale(monkeypatch, tmp_path, live_locale, expected_source):
    """H06 读取面真的被走通：locale 来自活库查询（非回落），并原样进 template0 建库语句。"""
    store = _FakeStore(_table_names(89), {t: dict(v) for t, v in _REAL_0925_ROWS.items()}, live_locale=live_locale)
    _install_fake_store(monkeypatch, store)
    dump = tmp_path / "depgraph.dump"
    dump.write_bytes(b"PGDMP\x00synthetic-fixture\n")

    rep = rd.run_drill(str(dump))
    assert rep.get("error") is None, str(rep.get("error"))[:200]
    assert rep["drill_db_locale_source"] == expected_source
    assert rep["drill_db_locale"] == {"collate": live_locale[0], "ctype": live_locale[1], "encoding": live_locale[2]}
    creates = [sql for _db, sql in store.statements if sql.startswith("CREATE DATABASE")]
    assert len(creates) == 1, creates
    assert "TEMPLATE template0" in creates[0]
    assert f"LC_COLLATE '{live_locale[0]}'" in creates[0] and f"LC_CTYPE '{live_locale[1]}'" in creates[0]
    assert f"ENCODING '{live_locale[2]}'" in creates[0]
    reset = [(db, sql) for db, sql in store.statements if sql.startswith("DROP SCHEMA")]
    assert reset and all(db == rd._DRILL_DB for db, _s in reset), "IN1-32b：public 重置只打演练库"
    assert rep["drill_db_schema_reset_rc"] == 0
    assert rep["pass"] is True, rep["failed_criteria"]


def test_run_drill_h06_records_locale_fallback_when_live_reading_unusable(monkeypatch, tmp_path):
    """活库 locale 读不到三列（本例返回单列）→ 必须回落实测缺省并把回落事实入报告。"""
    store = _NoLocaleStore(_table_names(89), {t: dict(v) for t, v in _REAL_0925_ROWS.items()})
    _install_fake_store(monkeypatch, store)
    dump = tmp_path / "depgraph.dump"
    dump.write_bytes(b"PGDMP\x00synthetic-fixture\n")

    rep = rd.run_drill(str(dump))
    assert rep.get("error") is None, str(rep.get("error"))[:200]
    assert rep["drill_db_locale_source"] == "fallback"
    assert tuple(rep["drill_db_locale"][k] for k in ("collate", "ctype", "encoding")) == rd._DRILL_LOCALE_FALLBACK
    creates = [sql for _db, sql in store.statements if sql.startswith("CREATE DATABASE")]
    assert len(creates) == 1 and "TEMPLATE template0" in creates[0]
    assert rep["pass"] is True, rep["failed_criteria"]
