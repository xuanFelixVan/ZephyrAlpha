# [BLUEPRINT] MOD-BT-018 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""N 试次账本（MOD-BT-200）单元测试——零 CH/零网络，假 conn + tmp_path 注入。

覆盖面：
- 口径合成：count = screen_runs + batch_records；manual_population 只入 known_floor 不入 count
- 幂等：record_run 同 batch_id 跳过；sync 重复执行不重复计
- fail-closed：账本缺失抛错；假 conn 读数缺失（空行）不阻断但读数为 0 口径自洽
- CAS：并发写冲突退避后成功（monkeypatch safe_write_text 前两次抛错）
- 骨架初始化：create_if_missing 落盘可读
- n_eff 预留位：恒 None（批次 B 落地前）
- 行尾真源（st-crlffix-20260919）：写 .gitattributes 钉 eol=lf 的册后**裸字节 CRLF=0**；
  另锁 safe_write_text 的 newline 默认未被翻转
"""

from __future__ import annotations

import inspect
import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from zephyr.backtest.core.n_trial_ledger import ( 
    compute_effective_rank,

    LEDGER_REGISTRY_PATH,
    REGISTRY_SKELETON,
    TrialLedger,
    TrialLedgerError,
)


class FakeCHConn:
    """假 ClickHouse 连接：execute(sql) -> rows，只认台账 group-by 查询。"""

    def __init__(self, rows: list[tuple]) -> None:
        self.rows = rows
        self.calls: list[str] = []

    def execute(self, sql: str):  # noqa: ANN001
        self.calls.append(sql)
        return self.rows


@pytest.fixture()
def ledger(tmp_path):
    return TrialLedger(registry_path=tmp_path / "trial_ledger_registry.yaml")


def test_missing_ledger_fail_closed(ledger):
    with pytest.raises(TrialLedgerError):
        ledger.cumulative_trials()


def test_skeleton_init_and_zero_count(ledger):
    data = ledger.load_registry(create_if_missing=True)
    assert data["screen_runs"]["total_trials"] == 0
    assert ledger.cumulative_trials() == 0
    assert LEDGER_REGISTRY_PATH.name == "trial_ledger_registry.yaml"


def test_record_run_and_snapshot(ledger):
    ledger.load_registry(create_if_missing=True)
    out = ledger.record_run("factory_grid_batch_a", "grid_x", 1999, note="manifest")
    assert out["status"] == "recorded"
    assert out["cumulative_trials"] == 1999
    snap = ledger.snapshot()
    assert snap.ledger_trials == 1999
    assert snap.breakdown == {"screen_runs": 0, "batch:grid_x": 1999}
    assert snap.manual_population == 0
    assert snap.known_floor == snap.ledger_trials
    assert snap.n_trials_raw == 1999
    assert snap.n_trials_effective is None  # 预注册：批次 B 落地前恒 None


def test_record_run_idempotent(ledger):
    ledger.load_registry(create_if_missing=True)
    ledger.record_run("manual", "B-1", 100)
    out = ledger.record_run("manual", "B-1", 100)
    assert out["status"] == "exists"
    assert ledger.cumulative_trials() == 100


def test_record_run_validation(ledger):
    ledger.load_registry(create_if_missing=True)
    with pytest.raises(ValueError):
        ledger.record_run("manual", "", 10)
    with pytest.raises(ValueError):
        ledger.record_run("manual", "B", -1)


def test_manual_population_not_in_count(ledger):
    ledger.load_registry(create_if_missing=True)
    ledger._cas_update(lambda d: d.update(manual_population=500) or "set manual")  # noqa: SLF001
    assert ledger.cumulative_trials() == 0
    snap = ledger.snapshot()
    assert snap.manual_population == 500
    assert snap.known_floor == 500
    assert snap.n_trials_raw == 0


def test_sync_screen_counts_with_fake_conn(ledger, tmp_path):
    conn = FakeCHConn([("SCR-a", 32), ("SCR-b", 5)])
    out = ledger.sync_screen_counts(conn, grid_root=tmp_path, synced_by="st-test")
    assert out["screen_runs"] == 37
    assert out["screen_batches"] == 2
    assert out["cumulative_trials"] == 37
    # 计数边界（2026-09-15 裁定）：只算 is_sharpe 非空证据行（机器回测成绩），
    # deferred_c4 挂起行等零成绩行不入 N——同步 SQL 必须带证据行过滤。
    assert "is_sharpe IS NOT NULL" in conn.calls[0]
    data = ledger.load_registry()
    assert data["screen_runs"]["last_synced_by"] == "st-test"
    assert data["screen_runs"]["last_synced_at"]


def test_sync_discovers_grid_summaries(ledger, tmp_path):
    g = tmp_path / "grid_20260915-052749"
    g.mkdir(parents=True)
    (g / "summary.json").write_text(
        json.dumps({"n_raw": 362880, "n_sampled": 2000, "evaluated": 1999}),
        encoding="utf-8",
    )
    conn = FakeCHConn([])
    out = ledger.sync_screen_counts(conn, grid_root=tmp_path, synced_by="st-test")
    assert out["grid_added"] == ["grid_20260915-052749"]
    assert out["cumulative_trials"] == 1999  # evaluated 优先（实跑数=可审计）
    # 幂等：重复 sync 不重复计
    out2 = ledger.sync_screen_counts(conn, grid_root=tmp_path, synced_by="st-test")
    assert out2["grid_added"] == []
    assert out2["cumulative_trials"] == 1999


def test_sync_grid_falls_back_to_n_sampled(ledger, tmp_path):
    g = tmp_path / "grid_x"
    g.mkdir()
    (g / "summary.json").write_text(json.dumps({"n_sampled": 500}), encoding="utf-8")
    out = ledger.sync_screen_counts(FakeCHConn([]), grid_root=tmp_path)
    assert out["cumulative_trials"] == 500


def test_sync_skips_broken_summary(ledger, tmp_path):
    g = tmp_path / "grid_bad"
    g.mkdir()
    (g / "summary.json").write_text("{not json", encoding="utf-8")
    out = ledger.sync_screen_counts(FakeCHConn([]), grid_root=tmp_path)
    assert out["grid_added"] == []
    assert out["cumulative_trials"] == 0


def test_cas_retry_on_conflict(ledger, tmp_path, monkeypatch):
    """前两次 safe_write_text 抛冲突，第三次成功——立即重试（无 sleep）生效。"""
    from zephyr.backtest.core import n_trial_ledger as mod

    ledger.load_registry(create_if_missing=True)
    calls = {"n": 0}
    real = mod.safe_write_text

    def flaky(path, content, **kw):
        calls["n"] += 1
        if calls["n"] <= 2:
            raise PermissionError("simulated concurrent writer")
        return real(path, content, **kw)

    monkeypatch.setattr(mod, "safe_write_text", flaky)
    out = ledger.record_run("manual", "B-cas", 42)
    assert out["status"] == "recorded"
    assert calls["n"] == 3
    assert ledger.cumulative_trials() == 42


def test_yaml_structure_valid(ledger):
    ledger.load_registry(create_if_missing=True)
    data = yaml.safe_load(ledger._path.read_text(encoding="utf-8"))  # noqa: SLF001
    for key in REGISTRY_SKELETON:
        assert key in data


# ── CRLF 治本回归（st-crlffix-20260919）───────────────────────────────────────
# 缺陷：_cas_update / load_registry 落骨架两处调 safe_write_text 未传 newline，
# 而 safe_write_text 缺省 newline=None → open(newline=None) 在 Windows 把 "\n"
# 翻成 os.linesep，每次写都往 .gitattributes 钉 LF 的注册表注入 CRLF。
# 危险点：safe_write_text 自家"写后回读校验"用 universal-newlines 读，对 CRLF
# 免疫 ⇒ 污染不被发现。故断言必须看**裸字节**，不能走 read_text。

GIT = shutil.which("git")


def _git(cwd: Path, *args: str) -> str:
    r = subprocess.run([GIT, *args], cwd=str(cwd), capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, f"git {' '.join(args)} 失败: {r.stderr}"
    return (r.stdout or "").strip()


def _eol_counts(path: Path) -> tuple[int, int]:
    """(CRLF 数, 裸 LF 数)——裸字节口径，绕开 universal newlines。"""
    raw = path.read_bytes()
    lf = raw.count(b"\n")
    crlf = raw.count(b"\r\n")
    return crlf, lf - crlf


@pytest.fixture()
def lf_pinned_repo(tmp_path):
    """一次性小仓：真 git init + .gitattributes 钉 *.yaml eol=lf，册以 LF 出生。"""
    if not GIT:
        pytest.skip("git 不可用，无法构造真 eol=lf 钉定面")
    root = tmp_path / "pinned_repo"
    root.mkdir()
    _git(root, "init", "-q", ".")
    (root / ".gitattributes").write_text("* text=auto eol=lf\n*.yaml text eol=lf\n", encoding="utf-8")
    reg = root / "trial_ledger_registry.yaml"
    # LF 出生（显式 newline="\n"，与本探针无关的基准真源）
    with open(reg, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(yaml.safe_dump(REGISTRY_SKELETON, allow_unicode=True, sort_keys=False))
    _git(root, "add", ".")
    _git(root, "-c", "user.email=t@invalid", "-c", "user.name=t", "commit", "-q", "-m", "birth LF")
    assert _git(root, "check-attr", "eol", "--", "trial_ledger_registry.yaml").endswith("eol: lf")
    assert _eol_counts(reg) == (0, reg.read_bytes().count(b"\n")), "出生证必须是纯 LF"
    return reg


def test_cas_update_keeps_lf_on_lf_pinned_registry(lf_pinned_repo):
    """① 主修点：_cas_update 写 LF 钉定册后，盘上 CRLF 必须为 0（裸字节断言）。"""
    reg = lf_pinned_repo
    before = reg.read_bytes()

    TrialLedger(registry_path=reg).record_run("manual", "B-crlf", 5, note="crlf 治本回归")

    crlf, bare_lf = _eol_counts(reg)
    assert crlf == 0, f"_cas_update 往 eol=lf 钉定册注入了 {crlf} 个 CRLF"
    assert bare_lf > 0, "文件应仍有行尾（防空文件假绿）"
    # 语义不变：剥掉 CR 后逐行应与"LF 口径读入"一致，且新记录确实落账
    assert reg.read_bytes().count(b"\r") == 0
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    assert [r["batch_id"] for r in data["batch_records"]] == ["B-crlf"]
    assert before.count(b"\r\n") == 0  # 前提自证：写前是干净的


def test_skeleton_bootstrap_keeps_lf_on_lf_pinned_registry(lf_pinned_repo):
    """② 副修点：load_registry(create_if_missing=True) 落骨架同样不得注 CRLF。"""
    reg = lf_pinned_repo.parent / "brand_new_registry.yaml"
    TrialLedger(registry_path=reg).load_registry(create_if_missing=True)
    crlf, bare_lf = _eol_counts(reg)
    assert crlf == 0, f"骨架初始化注入了 {crlf} 个 CRLF"
    assert bare_lf > 0
    assert yaml.safe_load(reg.read_text(encoding="utf-8"))["screen_runs"]["total_trials"] == 0


def test_default_newline_channel_not_flipped():
    """③ 阴性对照护栏：本车道只修调用点，未翻 safe_write_text 默认。

    钉 LF 的册由调用点禁翻译；未钉定的目标经默认通道仍按平台默认走
    ——默认值一改影响全部调用方（门位级行为变更），此断言锁死"不顺手改默认"。
    """
    from zephyr.shared.io.file_utils import safe_write_text

    sig = inspect.signature(safe_write_text)
    assert sig.parameters["newline"].default is None, (
        "safe_write_text 的 newline 默认值被改动——默认变更属门位级，本车道未授权"
    )


class TestEffectiveRank:
    """T1（2026-09-16）：effective_rank 估计器（预注册 4.1 规格）+ 披露位写入。"""

    def _ledger_tmp(self, tmp_path):
        return TrialLedger(registry_path=tmp_path / "trial_ledger_registry.yaml")

    def test_independent_series_n_eff_near_n(self) -> None:
        import numpy as np

        rng = np.random.default_rng(11)
        data = {f"s{i}": rng.normal(0, 0.01, 250) for i in range(8)}
        n_eff, meta = compute_effective_rank(data)
        assert not meta["boundary"]
        assert 5 <= n_eff <= 8  # 独立序列→熵广度接近 N

    def test_identical_series_n_eff_one(self) -> None:
        import numpy as np

        base = np.random.default_rng(5).normal(0, 0.01, 200)
        data = {f"s{i}": base + 1e-12 * i for i in range(6)}  # 完全相关
        n_eff, _ = compute_effective_rank(data)
        assert n_eff == 1  # 完全相关→有效试验数 1

    def test_uneven_lengths_aligned_not_crash(self) -> None:
        """红蓝实战（批 11h 白跑根因）：不同格点净收益天数不齐——必须 index 对齐而非构造炸。"""
        import numpy as np

        rng = np.random.default_rng(9)
        data = {f"s{i}": list(rng.normal(0, 0.01, 200 - i * 7)) for i in range(5)}  # 200..172 不齐
        n_eff, meta = compute_effective_rank(data)  # 旧实现此处 ValueError
        assert meta["common_T"] == 172 and not meta["boundary"]

    def test_short_common_T_boundary_no_reduction(self) -> None:
        import numpy as np

        rng = np.random.default_rng(3)
        data = {f"s{i}": rng.normal(0, 0.01, 30) for i in range(5)}  # < min_T=60
        n_eff, meta = compute_effective_rank(data)
        assert meta["boundary"] and n_eff == 5  # 数据不足→不折减（诚实边界）

    def test_set_effective_roundtrip(self, tmp_path) -> None:
        led = self._ledger_tmp(tmp_path)
        led.load_registry(create_if_missing=True)
        led.record_run("manual", "BATCH-T1", 100, note="t1")
        r = led.set_effective_trials(7, note="batch:T1 spec=effective_rank")
        assert r["snapshot_n_raw"] >= 100
        snap = led.snapshot()
        assert snap.n_trials_effective == 7
        # 覆盖语义+previous 留痕
        led.set_effective_trials(9, note="batch:T2")
        snap2 = led.snapshot()
        assert snap2.n_trials_effective == 9
        d = led.load_registry()
        assert d["n_trials_effective"]["previous"]["value"] == 7

def test_count_of_missing_n_trials_fails_closed():
    """rpt_v04 回归：batch_records 缺 n_trials 必须 raise（旧码 or 0 静默缩水分母=DSR 欠折减）"""
    from zephyr.backtest.core.n_trial_ledger import TrialLedger
    data = {"screen_runs": {"total_trials": 10}, "batch_records": [{"batch_id": "b1", "n_trials": None}]}
    with pytest.raises(ValueError, match="n_trials"):
        TrialLedger._count_of(data)
    # 正常路径不受影响
    ok = {"screen_runs": {"total_trials": 10}, "batch_records": [{"batch_id": "b1", "n_trials": 5}]}
    assert TrialLedger._count_of(ok) == 15
