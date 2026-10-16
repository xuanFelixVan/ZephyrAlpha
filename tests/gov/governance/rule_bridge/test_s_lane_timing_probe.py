"""S 车道时延探针单测（图11 D11-S01..S09 九环节，st-sO2-probe-20261004 手术1d）。

覆盖：
- 装饰器记录四字段契约 {sid, phase, duration_seconds, ts}（ts 显式 UTC 时区）
- sid 位置参数提取（sid_index 生效/越界回退 None/kwargs 兜底）
- fail-open 三面：落盘路径不可写不抛+返回值原样；被包裹函数异常照常传播+finally 补记；
  emit 二次异常不吞业务返回值
- pytest 环境默认停写（测试隔离红线）+ _S_LANE_TIMINGS_TEST_MODE 显式开闸
- 九环节静态接线面：9 个目标函数全部挂 @_s_lane_probe 且 phase 集恰为 D11-S01..S09
- 图11 生成器 load_s_lane_p50 聚合面：p50 奇偶口径/未知 phase 过滤/文件缺失 fail-open

测试隔离：全部 monkeypatch _S_LANE_TIMINGS_PATH 到 tmp_path（禁写生产路径），
生成器聚合面读 tmp 合成 jsonl。
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

import zephyr.gov_enforcement.rule_bridge.session_worktree as sw


@pytest.fixture
def probe_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """探针测试环境：显式开测试闸 + jsonl 落 tmp_path。"""
    monkeypatch.setattr(sw, "_S_LANE_TIMINGS_TEST_MODE", True)
    timings = tmp_path / "s_lane_timings.jsonl"
    monkeypatch.setattr(sw, "_S_LANE_TIMINGS_PATH", timings)
    return timings


def _read_records(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# 绿组：记录契约 + sid 提取
# ---------------------------------------------------------------------------


def test_green_record_contract_and_sid_extraction(probe_env: Path):
    """四字段契约 + 位置参数 sid 提取（rec1 位置/args 越界 kwargs/无 sid=""）。"""
    rec1_hit = False

    @sw._s_lane_probe("D11-S06", 0)
    def fn_pos(sid: str, files: list[str]) -> str:
        return f"ok-{sid}"

    assert fn_pos("sess-a", ["x.py"]) == "ok-sess-a"
    recs = _read_records(probe_env)
    assert len(recs) == 1
    r = recs[0]
    assert set(r.keys()) == {"sid", "phase", "duration_seconds", "ts"}
    assert r["sid"] == "sess-a"
    assert r["phase"] == "D11-S06"
    assert isinstance(r["duration_seconds"], float) and r["duration_seconds"] >= 0.0
    assert r["ts"].endswith("+00:00"), "ts 必须带显式 UTC 时区（RULE-SCHEMA-TZ）"
    rec1_hit = True

    # args 越界（sid_index=5 但只有 1 个位置参数）→ kwargs 无 session_id → sid=""
    @sw._s_lane_probe("D11-S05", 5)
    def fn_oob(root: Path) -> int:
        return 7

    assert fn_oob(Path(".")) == 7
    r2 = _read_records(probe_env)[-1]
    assert r2["sid"] == "" and r2["phase"] == "D11-S05"

    # kwargs 兜底：args 越界时从 kwargs["session_id"] 取
    @sw._s_lane_probe("D11-S07", 3)
    def fn_kw(root: Path, session_id: str | None = None) -> str:
        return session_id or "none"

    assert fn_kw(Path("."), session_id="sess-kw") == "sess-kw"
    r3 = _read_records(probe_env)[-1]
    assert r3["sid"] == "sess-kw" and r3["phase"] == "D11-S07"

    assert rec1_hit


def test_green_duration_measures_real_elapsed(probe_env: Path):
    """duration_seconds 真实测时（sleep 0.05s ⇒ 记录值 ≥ 0.05）。"""
    import time

    @sw._s_lane_probe("D11-S01")
    def slow() -> None:
        time.sleep(0.05)

    slow()
    r = _read_records(probe_env)[-1]
    assert r["duration_seconds"] >= 0.05
    assert r["sid"] == ""  # S01 无 sid 参数


# ---------------------------------------------------------------------------
# 红组：fail-open 三面（计时失败绝不阻断业务）
# ---------------------------------------------------------------------------


def test_red_unwritable_path_fail_open(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """落盘路径不可写（父目录被同名文件占位）⇒ 不抛、返回值原样透传。"""
    monkeypatch.setattr(sw, "_S_LANE_TIMINGS_TEST_MODE", True)
    blocker = tmp_path / "blocker"
    blocker.write_text("i am a file", encoding="utf-8")
    monkeypatch.setattr(sw, "_S_LANE_TIMINGS_PATH", blocker / "sub" / "s.jsonl")

    @sw._s_lane_probe("D11-S02", 0)
    def fn(sid: str) -> dict:
        return {"ok": True, "sid": sid}

    assert fn("sess-x") == {"ok": True, "sid": "sess-x"}  # 不抛=探针 fail-open


def test_red_business_exception_propagates_and_still_records(probe_env: Path):
    """被包裹函数异常照常传播（零改既有逻辑）+ finally 仍补记一条时延。"""
    boom = RuntimeError("business failure")

    @sw._s_lane_probe("D11-S08", 0)
    def fn(sid: str) -> None:
        raise boom

    with pytest.raises(RuntimeError, match="business failure"):
        fn("sess-boom")
    recs = _read_records(probe_env)
    assert len(recs) == 1
    assert recs[0]["sid"] == "sess-boom" and recs[0]["phase"] == "D11-S08"


def test_red_pytest_default_no_write(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """pytest 环境默认停写（不开 _S_LANE_TIMINGS_TEST_MODE ⇒ 零落盘）。"""
    timings = tmp_path / "should_not_exist.jsonl"
    monkeypatch.setattr(sw, "_S_LANE_TIMINGS_TEST_MODE", False)
    monkeypatch.setattr(sw, "_S_LANE_TIMINGS_PATH", timings)

    @sw._s_lane_probe("D11-S04", 0)
    def fn(sid: str) -> str:
        return sid

    assert fn("sess-nw") == "sess-nw"
    assert not timings.exists(), "pytest 默认必须停写（测试隔离红线：禁写生产路径）"


# ---------------------------------------------------------------------------
# 静态接线面：九环节全挂探针
# ---------------------------------------------------------------------------

_PHASE_FN = {
    "D11-S01": "_run_startup_health_check",
    "D11-S02": "session_worktree_start",
    "D11-S03": "_spawn_heartbeat_daemon",
    "D11-S04": "claim_files_for_edit",
    "D11-S05": "_wt_stage_changes",
    "D11-S06": "session_worktree_commit",
    "D11-S07": "session_worktree_merge",
    "D11-S08": "session_worktree_abort",
    "D11-S09": "_run_post_merge_reconcile",
}


def test_green_nine_probes_wired():
    """9 个目标函数全部挂 @_s_lane_probe 且 phase 集恰为 D11-S01..S09。"""
    decorated = set()
    for phase, name in _PHASE_FN.items():
        fn = getattr(sw, name, None)
        assert fn is not None, f"{name} 缺失"
        assert hasattr(fn, "__wrapped__"), f"{name} 未被装饰（探针接线面破了）"
        head = "\n".join(inspect.getsource(fn).splitlines()[:5])
        assert f'@_s_lane_probe("{phase}"' in head, f"{name} 未挂 {phase} 探针（或装饰行被挪走）"
        decorated.add(phase)
    assert decorated == {f"D11-S{i:02d}" for i in range(1, 10)}, "phase 集必须恰为九环节"


def test_green_module_mapping_table_covers_nine():
    """模块内探针映射表注释九行齐全（防有人删行静默丢环节）。"""
    src = inspect.getsource(sw)
    for phase, name in _PHASE_FN.items():
        assert f"{phase}={name}" in src, f"映射表缺 {phase}={name}"


# ---------------------------------------------------------------------------
# 图11 生成器聚合面（手术1c：load_s_lane_p50）
# ---------------------------------------------------------------------------


def _gen():
    import generate_dev_delivery_map as gen

    return gen


def _load_gen(monkeypatch: pytest.MonkeyPatch):
    import sys

    repo = Path(__file__).resolve().parents[4]
    gov = repo / "scripts" / "governance"
    for p in (
        str(gov / "d5_architecture" / "generators"),
        str(gov / "d5_architecture" / "validators"),
        str(gov),
        str(repo / "src"),
    ):
        if p not in sys.path:
            sys.path.insert(0, p)
    return _gen()


def test_green_p50_aggregation_odd_even(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """p50 口径：奇数取中位、偶数取双中均值；样本数如实。"""
    gen = _load_gen(monkeypatch)
    f = tmp_path / ".runtime" / "audit" / "s_lane_timings.jsonl"
    f.parent.mkdir(parents=True)
    rows = [
        {"sid": "a", "phase": "D11-S06", "duration_seconds": 1.0, "ts": "t"},
        {"sid": "a", "phase": "D11-S06", "duration_seconds": 3.0, "ts": "t"},
        {"sid": "b", "phase": "D11-S06", "duration_seconds": 2.0, "ts": "t"},  # 奇数中位=2.0
        {"sid": "b", "phase": "D11-S07", "duration_seconds": 10.0, "ts": "t"},
        {"sid": "b", "phase": "D11-S07", "duration_seconds": 20.0, "ts": "t"},  # 偶数均值=15.0
        {"sid": "c", "phase": "D11-C01", "duration_seconds": 99.0, "ts": "t"},  # 非 S 道=过滤
        {"sid": "c", "phase": "D11-S99", "duration_seconds": 99.0, "ts": "t"},  # 未知名=过滤
        {"sid": "c", "phase": "D11-S02", "duration_seconds": -1.0, "ts": "t"},  # 负值=过滤
        {"phase": "D11-S02"},  # 缺字段=过滤
    ]
    f.write_text("\n".join(json.dumps(r) for r in rows) + "\n{bad json\n", encoding="utf-8")
    out = gen.load_s_lane_p50(tmp_path)
    assert out["D11-S06"]["p50_seconds"] == 2.0 and out["D11-S06"]["latency_samples"] == 3
    assert out["D11-S07"]["p50_seconds"] == 15.0 and out["D11-S07"]["latency_samples"] == 2
    assert set(out) == {"D11-S06", "D11-S07"}, "未知 phase/负值/坏行必须全部过滤"


def test_green_p50_missing_file_fail_open(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """jsonl 缺失 ⇒ {} （worktree/CI 无 .runtime 不产 p50 字段）。"""
    gen = _load_gen(monkeypatch)
    assert gen.load_s_lane_p50(tmp_path) == {}
