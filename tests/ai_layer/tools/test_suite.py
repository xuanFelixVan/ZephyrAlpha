"""test_suite — T2 考尺：装载校验全枚举/哈希锁/venue 契约/双跑判分/红线 fail/注入拒跑。

测试隔离：考卷与 policy 一律 tmp_path 构造（真源 YAML 另有只读快照断言）；runner 注入
假执行面，零真实外呼。
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
import yaml

from zephyr.ai_layer.comparator import venue_tool_bench
from zephyr.ai_layer.tools.suite import (
    SUITE_ID,
    SuiteError,
    _canonical_payload,
    load_suite,
    suite_criteria,
    suite_run,
)

TASKS = [
    {"task_id": "X1", "organ": "hand", "family": "执行", "task_desc": "d1",
     "criteria": "c1", "criteria_kind": "mechanical", "trap": False, "red_line": False},
    {"task_id": "X2", "organ": "hand", "family": "删除", "task_desc": "d2",
     "criteria": "c2", "criteria_kind": "mechanical", "trap": True, "red_line": True},
    {"task_id": "X3", "organ": "eye", "family": "观测", "task_desc": "d3",
     "criteria": "c3", "criteria_kind": "review", "trap": False, "red_line": False},
]
POLICY = {"status": "draft", "criteria": {"significance": {
    "effect_win_pp": 10.0, "noninferior_pp": -10.0, "min_judgeable_n": 2,
    "wilson_z": 1.96,
}}}


def _write_suite(tmp_path: Path, tasks: list[dict], **overrides: object) -> Path:
    doc: dict = {
        "schema_version": "1.0.0", "doc_type": "benchmark_suite",
        "status": "draft", "task_suite_version": "suite_t", "seed": 1,
        "tasks": tasks, **overrides,
    }
    doc["criteria_sha256"] = overrides.get("criteria_sha256") or hashlib.sha256(
        _canonical_payload(doc).encode("utf-8")).hexdigest()
    path = tmp_path / "suite.yaml"
    path.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    return path


@pytest.fixture()
def suite_env(tmp_path: Path) -> tuple[Path, Path]:
    policy_path = tmp_path / "policy.yaml"
    policy_path.write_text(yaml.safe_dump(POLICY, allow_unicode=True), encoding="utf-8")
    return _write_suite(tmp_path, TASKS), policy_path


# ---------------------------------------------------------------------------
# 装载校验（fail-closed 全枚举）
# ---------------------------------------------------------------------------

def test_load_suite_ok(suite_env: tuple[Path, Path]) -> None:
    doc = load_suite(suite_env[0])
    assert doc["task_suite_version"] == "suite_t" and len(doc["tasks"]) == 3


def test_load_suite_missing_file(tmp_path: Path) -> None:
    with pytest.raises(SuiteError, match="缺文件"):
        load_suite(tmp_path / "nope.yaml")


def test_hash_lock_tamper_detected(tmp_path: Path) -> None:
    path = _write_suite(tmp_path, TASKS, criteria_sha256="0" * 64)
    with pytest.raises(SuiteError, match="criteria_sha256 不匹配"):
        load_suite(path)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda doc: doc.update(doc_type="registry"),
        lambda doc: doc.update(task_suite_version=""),
        lambda doc: doc.pop("seed"),
        lambda doc: doc.update(tasks=[]),
        lambda doc: doc["tasks"][0].update(task_id="X2"),              # 重复 id
        lambda doc: doc["tasks"][0].update(organ="tail"),              # organ 词表外
        lambda doc: doc["tasks"][0].update(criteria_kind="vibes"),     # 判据词表外
        lambda doc: doc["tasks"][0].pop("criteria"),                   # 缺字段
        lambda doc: doc["tasks"][1].update(red_line=False),            # 陷阱必须红线
    ],
)
def test_schema_violations_fail_closed(suite_env: tuple[Path, Path], mutate: object) -> None:
    import yaml as yaml_mod

    path, _ = suite_env
    doc = yaml_mod.safe_load(path.read_text(encoding="utf-8"))
    doc.pop("criteria_sha256")           # 结构变异后哈希必不匹配，先摘掉单测结构错
    mutate(doc)
    bad = tmp_path_from(path) / "bad.yaml"
    bad.write_text(yaml_mod.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    with pytest.raises(SuiteError):
        load_suite(bad)


def tmp_path_from(path: Path) -> Path:
    return path.parent


# ---------------------------------------------------------------------------
# venue_tool_bench 契约对齐（C4：OBJ_T 供考卷 schema 对齐验收）
# ---------------------------------------------------------------------------

def test_suite_criteria_contract_shape(suite_env: tuple[Path, Path]) -> None:
    suite_path, policy_path = suite_env
    policy_path.write_text(yaml.safe_dump(POLICY), encoding="utf-8")
    snap = suite_criteria(suite_path=suite_path, policy_path=policy_path)
    assert snap["venue"] == SUITE_ID == "venue_tool_bench"      # 快照 venue 键=VENUE_ID
    assert snap["organ_composition"] == {"hand": 2, "eye": 1, "foot": 0}
    assert snap["trap_task_ids"] == ["X2"]
    assert snap["policy_status"] == "draft"
    assert len(snap["criteria_sha256"]) == 64


def test_venue_pointer_wired_and_module_exposes_contract() -> None:
    """接线批 2026-09-24：L4 考场指针已接通本包真源；契约面 callable 不变。"""
    assert venue_tool_bench.RULER_MODULES == ("zephyr.ai_layer.tools.suite",)
    assert callable(suite_criteria) and callable(suite_run)     # 契约面就位


def test_real_repo_suite_loads() -> None:
    """真源快照：OBJ_T 目录考卷 21 题（手 8 眼 7 脚 6）+draft 状态+陷阱题 4 道。"""
    snap = suite_criteria()
    assert snap["task_suite_version"] == "tool_suite_v0"
    assert snap["suite_status"] == "draft"
    assert snap["organ_composition"] == {"hand": 8, "eye": 7, "foot": 6}
    assert sorted(snap["trap_task_ids"]) == ["E7", "F2", "F6", "H8"]
    assert snap["policy_status"] == "draft"


# ---------------------------------------------------------------------------
# suite_run：双跑判分
# ---------------------------------------------------------------------------

def test_suite_run_refuses_without_runner(suite_env: tuple[Path, Path]) -> None:
    suite_path, policy_path = suite_env
    with pytest.raises(SuiteError, match="runner_not_injected"):
        suite_run({"tool_ref": "t", "suite_version": "suite_t"},
                  suite_path=suite_path, policy_path=policy_path)


def test_suite_run_refuses_version_mismatch(suite_env: tuple[Path, Path]) -> None:
    suite_path, policy_path = suite_env
    with pytest.raises(SuiteError, match="不匹配"):
        suite_run({"tool_ref": "t", "suite_version": "wrong"}, runner=lambda t: {"passed": True},
                  suite_path=suite_path, policy_path=policy_path)


def test_suite_run_refuses_missing_tool_ref(suite_env: tuple[Path, Path]) -> None:
    suite_path, policy_path = suite_env
    with pytest.raises(SuiteError, match="tool_ref"):
        suite_run({"suite_version": "suite_t"}, runner=lambda t: {"passed": True},
                  suite_path=suite_path, policy_path=policy_path)


def test_suite_run_dual_run_win_and_too_good(suite_env: tuple[Path, Path]) -> None:
    suite_path, policy_path = suite_env
    out = suite_run(
        {"tool_ref": "cand", "suite_version": "suite_t"},
        runner=lambda t: {"passed": True, "latency_s": 0.1},
        champion_runner=lambda t: {"passed": False},
        suite_path=suite_path, policy_path=policy_path,
    )
    assert out["venue"] == "venue_tool_bench" and out["op"] == "suite_run"
    assert out["verdict"]["verdict"] == "win"
    assert out["too_good_suspect"] is True                      # 全对+卷含陷阱题
    assert out["red_line_violation"] is False
    assert out["policy_status"] == "draft" and out["suite_status"] == "draft"
    assert set(out["organ_scores"]) == {"hand", "eye"}


def test_suite_run_red_line_fail_overrides(suite_env: tuple[Path, Path]) -> None:
    suite_path, policy_path = suite_env
    def runner(task: dict) -> dict:
        return {"passed": task["task_id"] != "X2"}              # 红线陷阱题翻车
    out = suite_run({"tool_ref": "cand", "suite_version": "suite_t"}, runner=runner,
                    champion_runner=runner, suite_path=suite_path, policy_path=policy_path)
    assert out["verdict"]["verdict"] == "fail"
    assert out["red_line_violation"] is True
    assert out["too_good_suspect"] is False


def test_suite_run_runner_exception_recorded_not_raised(suite_env: tuple[Path, Path]) -> None:
    suite_path, policy_path = suite_env
    def runner(task: dict) -> dict:
        if task["task_id"] == "X3":
            raise RuntimeError("boom")
        return {"passed": True}
    out = suite_run({"tool_ref": "cand", "suite_version": "suite_t"}, runner=runner,
                    suite_path=suite_path, policy_path=policy_path)
    assert out["verdict"]["verdict"] is None                    # champion 缺席不出裁决
    eye = out["organ_scores"]["eye"]
    assert eye["organ_score"] == 0.0 and eye["n"] == 1          # 翻车记账不炸


def test_suite_run_organ_subset(suite_env: tuple[Path, Path]) -> None:
    suite_path, policy_path = suite_env
    out = suite_run({"tool_ref": "c", "suite_version": "suite_t", "organ": "eye"},
                    runner=lambda t: {"passed": True},
                    suite_path=suite_path, policy_path=policy_path)
    assert set(out["organ_scores"]) == {"eye"}
    with pytest.raises(SuiteError, match="无可判题"):
        suite_run({"tool_ref": "c", "suite_version": "suite_t", "organ": "foot"},
                  runner=lambda t: {"passed": True},
                  suite_path=suite_path, policy_path=policy_path)


def test_canonical_payload_stable() -> None:
    a = json.loads(json.dumps({"b": 1, "a": 2}))
    b = {"a": 2, "b": 1}
    assert _canonical_payload({"task_suite_version": "v", "seed": 1, "tasks": a}) == \
        _canonical_payload({"task_suite_version": "v", "seed": 1, "tasks": b})
