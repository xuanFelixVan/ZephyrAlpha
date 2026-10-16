# [BLUEPRINT] MOD-INF-005 | tests/gov/governance/price_cage/test_price_cage_judge.py | §
# [A_test] module_id: MOD-INF-005 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.gov.governance.test_price_cage_judge
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d6_security.price_cage_supply_sampler;
#   scripts.governance.d6_security.price_cage_unknown_reject_judge
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 测试零生产写面（全部读写路径指向 tmp_path）；judge 证据流全参数化注入；
#   sampler 时段/交易日判定用 monkeypatch（now_utc/is_trading_day）不动真源
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/gov/governance/test_price_cage_judge.py
# [TTL] permanent
"""裁定#535「unknown_reject 武装核证」两脚本（sampler/judge）单测。

覆盖组：
- TestSamplerGuards: 非交易日/非交易时段零写（monkeypatch time/trading_calendar）；时段边界
- TestSamplerEvidence: 时段内三重 fresh 判定（probe/age/timetag）+ 证据行 schema + probe 异常留证
- TestJudgeEvidence: 5 天全绿→PASS；缺 1 天→FAIL；fresh 率不足→FAIL；
  flags 两键缺失/BF-6 缺席/判定日志落点缺失→FAIL-BLOCKED；越权 set→FAIL；判定日志不达量→FAIL

测试隔离：读写路径全部 tmp_path；judge 的 bf6 探测经参数/monkeypatch 注入（不依赖 HEAD 态）。
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

_REPO = Path(__file__).resolve().parents[4]


def _load_script(rel: str, name: str):
    """按路径加载 scripts/ 下单文件模块（scripts 不是 sys.path 包，走 spec 装载）。"""
    path = _REPO / rel
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader, f"cannot load {path}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def sampler():
    return _load_script("scripts/governance/d6_security/price_cage/price_cage_supply_sampler.py", "test_pcj_sampler")


@pytest.fixture(scope="module")
def judge():
    return _load_script(
        "scripts/governance/d6_security/price_cage/price_cage_unknown_reject_judge.py", "test_pcj_judge"
    )


_CN = ZoneInfo("Asia/Shanghai")
_TODAY = date(2026, 10, 15)  # 观察窗第 1 天（锚定过去日期=日历判定确定性，不随测试日漂移）

_FLAGS_YAML_GREEN = """
flags:
  metrics:
    enabled: true
  ex_core_price_cage_base_supply:
    enabled: false
  ex_core_price_cage_unknown_reject:
    enabled: false
"""
_FLAGS_YAML_NO_CAGE = """
flags:
  metrics:
    enabled: true
"""


def _beijing(y: int, m: int, d: int, hh: int, mm: int = 0) -> datetime:
    return datetime(y, m, d, hh, mm, tzinfo=_CN)


def _mk_quote_csv(path: Path, timetag: str) -> Path:
    """造 29 列 quote.csv 尾行（第 29 列=timetag，列布局同 qmt_file_bridge_quote.py 头注）。"""
    cols = [f"c{i}" for i in range(28)] + [timetag]
    path.write_text(",".join(cols) + "\n", encoding="utf-8")
    return path


def _probe_ok(quote_path: Path, age_s: float = 1.0) -> dict:
    return {"alive": True, "quote_file": {"path": str(quote_path), "exists": True, "age_s": age_s, "fresh": True}}


def _write_evidence(path: Path, days: list[date], *, per_window: int = 31, fresh_ratio: float = 1.0) -> None:
    """造采样证据面（每格 per_window 条，fresh 占比 fresh_ratio）。"""
    lines = []
    for day in days:
        for window in ("am", "pm"):
            n_fresh = int(per_window * fresh_ratio)
            for i in range(per_window):
                lines.append(
                    json.dumps(
                        {
                            "date": day.isoformat(),
                            "window": window,
                            "ts": f"{day.isoformat()}T10:00:0{i % 10}",
                            "fresh": i < n_fresh,
                            "age_s": 1.0,
                            "env": "sim",
                        },
                        ensure_ascii=False,
                    )
                )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_cage_log(path: Path, days: list[date], per_day: int = 4) -> None:
    lines = [
        json.dumps({"date": d.isoformat(), "ts": f"{d.isoformat()}T10:00:00+00:00"})
        for d in days
        for _ in range(per_day)
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ── 采样器：时段/交易日守卫 ──────────────────────────────────────────


class TestSamplerGuards:
    def test_non_trading_day_zero_write(self, sampler, tmp_path, monkeypatch):
        """非交易日零写零副作用（trading_calendar 判定=monkeypatch 注入）。"""
        monkeypatch.setattr(sampler, "is_trading_day", lambda day=None: False)
        rc = sampler.run_sampler(
            now_cn=_beijing(2026, 10, 17, 10, 0),  # 周六
            audit_dir=tmp_path,
            quote_file=None,
            env="sim",
            probe_fn=lambda: _probe_ok(tmp_path / "quote.csv"),
            trading_day=sampler.is_trading_day(),
        )
        assert rc == 0
        assert list(tmp_path.iterdir()) == []

    def test_out_of_session_zero_write(self, sampler, tmp_path, monkeypatch):
        """非连续竞价时段（午休 12:00）零写（time=monkeypatch now_utc 注入）。"""
        fixed = _beijing(2026, 10, 15, 12, 0)
        monkeypatch.setattr(sampler, "is_trading_day", lambda day=None: True)
        monkeypatch.setattr(sampler, "now_utc", lambda: fixed)
        rc = sampler.main(["--audit-dir", str(tmp_path)])
        assert rc == 0
        assert list(tmp_path.iterdir()) == []

    def test_session_window_boundaries(self, sampler):
        f = sampler.session_window_of
        assert f(_beijing(2026, 10, 15, 9, 30).time()) == "am"
        assert f(_beijing(2026, 10, 15, 11, 30).time()) == "am"
        assert f(_beijing(2026, 10, 15, 11, 31).time()) is None
        assert f(_beijing(2026, 10, 15, 13, 0).time()) == "pm"
        assert f(_beijing(2026, 10, 15, 15, 0).time()) == "pm"
        assert f(_beijing(2026, 10, 15, 15, 1).time()) is None


# ── 采样器：三重 fresh 判定与证据行 ──────────────────────────────────


class TestSamplerEvidence:
    def test_in_session_fresh_write(self, sampler, tmp_path):
        """时段内三重判据全过→fresh=True 证据落盘（规格 6 字段齐全）。"""
        quote = _mk_quote_csv(tmp_path / "quote.csv", "20261015 09:59:57")
        rc = sampler.run_sampler(
            now_cn=_beijing(2026, 10, 15, 10, 0),
            audit_dir=tmp_path,
            quote_file=quote,
            env="sim",
            probe_fn=lambda: _probe_ok(quote),
            trading_day=True,
        )
        assert rc == 0
        rows = [
            json.loads(ln) for ln in (tmp_path / "price_cage_supply.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        assert len(rows) == 1
        rec = rows[0]
        assert rec["date"] == "2026-10-15"
        assert rec["window"] == "am"
        assert rec["fresh"] is True
        assert rec["age_s"] == 1.0
        assert rec["env"] == "sim"
        assert rec["timetag"] == "20261015 09:59:57"

    def test_stale_timetag_not_fresh(self, sampler, tmp_path):
        """尾行 timetag 差>60s→fresh=False+reason 留证（mtime 新鲜救不了行内陈旧）。"""
        quote = _mk_quote_csv(tmp_path / "quote.csv", "20261015 09:57:00")
        rc = sampler.run_sampler(
            now_cn=_beijing(2026, 10, 15, 10, 0),
            audit_dir=tmp_path,
            quote_file=quote,
            env="sim",
            probe_fn=lambda: _probe_ok(quote, age_s=5.0),
            trading_day=True,
        )
        assert rc == 0
        rec = json.loads((tmp_path / "price_cage_supply.jsonl").read_text(encoding="utf-8").splitlines()[-1])
        assert rec["fresh"] is False
        assert rec["reason"] == "timetag_age_gt_60"

    def test_probe_exception_recorded_not_raised(self, sampler, tmp_path):
        """probe 基础设施异常→按不新鲜留证不抛（fail-visible）。"""
        rc = sampler.run_sampler(
            now_cn=_beijing(2026, 10, 15, 10, 0),
            audit_dir=tmp_path,
            quote_file=None,
            env="real",
            probe_fn=lambda: (_ for _ in ()).throw(RuntimeError("bridge down")),
            trading_day=True,
        )
        assert rc == 0
        rec = json.loads((tmp_path / "price_cage_supply.jsonl").read_text(encoding="utf-8").splitlines()[-1])
        assert rec["fresh"] is False
        assert rec["env"] == "real"


# ── 判官：观察窗证据核证 ─────────────────────────────────────────────


class TestJudgeEvidence:
    def test_all_green_pass(self, judge, tmp_path):
        """5 交易日全格达标+前提件齐+判定日志足量+无越权 set→PASS。"""
        days = judge.recent_trading_days(_TODAY, 5)
        assert len(days) == 5
        evidence = tmp_path / "supply.jsonl"
        flags_yaml = tmp_path / "flags.yaml"
        cage_log = tmp_path / "cage.jsonl"
        _write_evidence(evidence, days)
        flags_yaml.write_text(_FLAGS_YAML_GREEN, encoding="utf-8")
        _write_cage_log(cage_log, days)
        rep = judge.run_judge(
            today=_TODAY,
            evidence_path=evidence,
            flags_yaml=flags_yaml,
            flag_audit=tmp_path / "feature_flags.jsonl",
            cage_log=cage_log,
            bf6_ok=True,
        )
        assert rep.verdict == "PASS"
        assert rep.missing_prereqs == []
        assert all(c.ok for c in rep.cells)
        assert len(rep.cells) == 10

    def test_missing_one_day_fail(self, judge, tmp_path):
        """缺 1 个交易日证据→FAIL（该日两窗全 INSUFFICIENT）。"""
        days = judge.recent_trading_days(_TODAY, 5)
        evidence = tmp_path / "supply.jsonl"
        flags_yaml = tmp_path / "flags.yaml"
        cage_log = tmp_path / "cage.jsonl"
        _write_evidence(evidence, days[:-1])
        flags_yaml.write_text(_FLAGS_YAML_GREEN, encoding="utf-8")
        _write_cage_log(cage_log, days)
        rep = judge.run_judge(
            today=_TODAY,
            evidence_path=evidence,
            flags_yaml=flags_yaml,
            flag_audit=tmp_path / "feature_flags.jsonl",
            cage_log=cage_log,
            bf6_ok=True,
        )
        assert rep.verdict == "FAIL"
        bad_cells = [c for c in rep.cells if not c.ok]
        assert {(c.day, c.window) for c in bad_cells} == {(days[-1].isoformat(), w) for w in ("am", "pm")}

    def test_low_fresh_rate_fail(self, judge, tmp_path):
        """某窗 fresh 率<80%→FAIL。"""
        days = judge.recent_trading_days(_TODAY, 5)
        evidence = tmp_path / "supply.jsonl"
        flags_yaml = tmp_path / "flags.yaml"
        cage_log = tmp_path / "cage.jsonl"
        _write_evidence(evidence, days, fresh_ratio=0.5)
        flags_yaml.write_text(_FLAGS_YAML_GREEN, encoding="utf-8")
        _write_cage_log(cage_log, days)
        rep = judge.run_judge(
            today=_TODAY,
            evidence_path=evidence,
            flags_yaml=flags_yaml,
            flag_audit=tmp_path / "feature_flags.jsonl",
            cage_log=cage_log,
            bf6_ok=True,
        )
        assert rep.verdict == "FAIL"
        assert all("fresh率" in c.note for c in rep.cells if not c.ok)

    def test_flags_keys_missing_blocked(self, judge, tmp_path):
        """flags.yaml 两键缺失→FAIL-BLOCKED+两键列入缺失清单。"""
        days = judge.recent_trading_days(_TODAY, 5)
        evidence = tmp_path / "supply.jsonl"
        flags_yaml = tmp_path / "flags.yaml"
        cage_log = tmp_path / "cage.jsonl"
        _write_evidence(evidence, days)
        flags_yaml.write_text(_FLAGS_YAML_NO_CAGE, encoding="utf-8")
        _write_cage_log(cage_log, days)
        rep = judge.run_judge(
            today=_TODAY,
            evidence_path=evidence,
            flags_yaml=flags_yaml,
            flag_audit=tmp_path / "feature_flags.jsonl",
            cage_log=cage_log,
            bf6_ok=True,
        )
        assert rep.verdict == "FAIL-BLOCKED"
        assert any(
            "ex_core_price_cage_base_supply" in m and "ex_core_price_cage_unknown_reject" in m
            for m in rep.missing_prereqs
        )

    def test_bf6_impl_missing_blocked(self, judge, tmp_path):
        """BF-6 判定件缺席→FAIL-BLOCKED（实现件未落地是合法输入态，不崩溃）。"""
        days = judge.recent_trading_days(_TODAY, 5)
        evidence = tmp_path / "supply.jsonl"
        flags_yaml = tmp_path / "flags.yaml"
        cage_log = tmp_path / "cage.jsonl"
        _write_evidence(evidence, days)
        flags_yaml.write_text(_FLAGS_YAML_GREEN, encoding="utf-8")
        _write_cage_log(cage_log, days)
        rep = judge.run_judge(
            today=_TODAY,
            evidence_path=evidence,
            flags_yaml=flags_yaml,
            flag_audit=tmp_path / "feature_flags.jsonl",
            cage_log=cage_log,
            bf6_ok=False,
        )
        assert rep.verdict == "FAIL-BLOCKED"
        assert any("BF-6" in m for m in rep.missing_prereqs)

    def test_cage_log_missing_blocked(self, judge, tmp_path):
        """判定日志持久化落点未建→FAIL-BLOCKED（待施工件③）。"""
        days = judge.recent_trading_days(_TODAY, 5)
        evidence = tmp_path / "supply.jsonl"
        flags_yaml = tmp_path / "flags.yaml"
        _write_evidence(evidence, days)
        flags_yaml.write_text(_FLAGS_YAML_GREEN, encoding="utf-8")
        rep = judge.run_judge(
            today=_TODAY,
            evidence_path=evidence,
            flags_yaml=flags_yaml,
            flag_audit=tmp_path / "feature_flags.jsonl",
            cage_log=tmp_path / "nonexistent.jsonl",
            bf6_ok=True,
        )
        assert rep.verdict == "FAIL-BLOCKED"
        assert any("判定日志" in m for m in rep.missing_prereqs)

    def test_unauthorized_set_fail(self, judge, tmp_path):
        """两键已登记但 feature_flags.jsonl 有越权 set→FAIL+逐条列出。"""
        days = judge.recent_trading_days(_TODAY, 5)
        evidence = tmp_path / "supply.jsonl"
        flags_yaml = tmp_path / "flags.yaml"
        flag_audit = tmp_path / "feature_flags.jsonl"
        cage_log = tmp_path / "cage.jsonl"
        _write_evidence(evidence, days)
        flags_yaml.write_text(_FLAGS_YAML_GREEN, encoding="utf-8")
        _write_cage_log(cage_log, days)
        flag_audit.write_text(
            json.dumps(
                {
                    "timestamp": "2026-10-15T02:00:00+00:00",
                    "action": "set",
                    "key": "ex_core_price_cage_unknown_reject",
                    "state": "on",
                }
            ),
            encoding="utf-8",
        )
        rep = judge.run_judge(
            today=_TODAY,
            evidence_path=evidence,
            flags_yaml=flags_yaml,
            flag_audit=flag_audit,
            cage_log=cage_log,
            bf6_ok=True,
        )
        assert rep.verdict == "FAIL"
        assert len(rep.unauthorized_sets) == 1

    def test_cage_log_shortfall_fail(self, judge, tmp_path):
        """判定日志存在但某日<4 条→FAIL。"""
        days = judge.recent_trading_days(_TODAY, 5)
        evidence = tmp_path / "supply.jsonl"
        flags_yaml = tmp_path / "flags.yaml"
        cage_log = tmp_path / "cage.jsonl"
        _write_evidence(evidence, days)
        flags_yaml.write_text(_FLAGS_YAML_GREEN, encoding="utf-8")
        _write_cage_log(cage_log, days[:-1], per_day=4)
        _write_cage_log(tmp_path / "tail.jsonl", days[-1:], per_day=2)
        cage_log.write_text(
            cage_log.read_text(encoding="utf-8") + (tmp_path / "tail.jsonl").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        rep = judge.run_judge(
            today=_TODAY,
            evidence_path=evidence,
            flags_yaml=flags_yaml,
            flag_audit=tmp_path / "feature_flags.jsonl",
            cage_log=cage_log,
            bf6_ok=True,
        )
        assert rep.verdict == "FAIL"
        assert rep.cage_log_daily[days[-1].isoformat()] == 2

    def test_main_exit_codes(self, judge, tmp_path, monkeypatch):
        """main 全链路 exit 映射：全绿=0（bf6 探测 monkeypatch 注入 True）。"""
        days = judge.recent_trading_days(_TODAY, 5)
        evidence = tmp_path / "supply.jsonl"
        flags_yaml = tmp_path / "flags.yaml"
        cage_log = tmp_path / "cage.jsonl"
        _write_evidence(evidence, days)
        flags_yaml.write_text(_FLAGS_YAML_GREEN, encoding="utf-8")
        _write_cage_log(cage_log, days)
        monkeypatch.setattr(judge, "probe_bf6_symbols", lambda: True)
        rc = judge.main(
            [
                "--evidence",
                str(evidence),
                "--flags-yaml",
                str(flags_yaml),
                "--flag-audit",
                str(tmp_path / "feature_flags.jsonl"),
                "--cage-log",
                str(cage_log),
                "--today",
                _TODAY.isoformat(),
            ]
        )
        assert rc == 0
