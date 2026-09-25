"""S3 shadow_runner 验收测试：三闸/corpus 冻结/分歧统计/零生产写隔离证明。"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from zephyr.intelligence.switch_engine.shadow_runner import (
    MANIFEST_NAME,
    ShadowGateError,
    ShadowRunConfig,
    ShadowRunner,
    default_command_runner,
    write_corpus_manifest,
)
from zephyr.shared.io.paths import REPO_ROOT


def build_corpus(tmp_path: Path, items: int = 2) -> Path:
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    for index in range(items):
        (corpus_dir / f"case_{index}.json").write_text(
            json.dumps({"input": index}), encoding="utf-8"
        )
    write_corpus_manifest(corpus_dir, seed=7)
    return corpus_dir


def build_config(tmp_path: Path, *, corpus_dir: Path | None = None, output_dir: Path | None = None) -> ShadowRunConfig:
    wt_a = tmp_path / "wt-champion"
    wt_b = tmp_path / "wt-challenger"
    wt_a.mkdir(exist_ok=True)
    wt_b.mkdir(exist_ok=True)
    return ShadowRunConfig(
        switch_id="SW-20260923-shadow",
        champion_worktree=wt_a,
        challenger_worktree=wt_b,
        corpus_dir=corpus_dir or build_corpus(tmp_path),
        output_dir=output_dir or (tmp_path / "out"),
        module_ref="demo_mod:run",
    )


def side_runner(stdout_by_side: dict[str, str]) -> Callable[..., tuple[str, str]]:
    def runner(worktree: Path, module_ref: str, item_path: Path, out_dir: Path) -> tuple[str, str]:
        return stdout_by_side[worktree.name], ""

    return runner


def test_identical_run_zero_disagreement(tmp_path: Path) -> None:
    same = json.dumps({"v": 1})
    config = build_config(tmp_path)
    runner = ShadowRunner(config, command_runner=side_runner(
        {config.champion_worktree.name: same, config.challenger_worktree.name: same}
    ))
    report = runner.run()
    assert report.total == 2
    assert report.identical == 2
    assert report.disagreement_rate == 0.0
    assert report.consumer == "comparator_only"  # 消费闸：仅供对比器
    written = config.output_dir / "comparison" / f"{config.switch_id}.json"
    assert written.is_file()
    payload: dict[str, Any] = json.loads(written.read_text(encoding="utf-8"))
    assert payload["disagreement_rate"] == 0.0


def test_full_disagreement_rate(tmp_path: Path) -> None:
    config = build_config(tmp_path)
    runner = ShadowRunner(config, command_runner=side_runner({
        config.champion_worktree.name: json.dumps({"v": 1}),
        config.challenger_worktree.name: json.dumps({"v": 2}),
    }))
    report = runner.run()
    assert report.disagreement_rate == 1.0
    assert all(c.diff_kind == "semantic_diff" for c in report.comparisons)


def test_error_side_does_not_crash_round(tmp_path: Path) -> None:
    config = build_config(tmp_path)

    def runner(worktree: Path, module_ref: str, item_path: Path, out_dir: Path) -> tuple[str, str]:
        if worktree.name == config.challenger_worktree.name:
            raise RuntimeError("challenger boom")
        return json.dumps({"v": 1}), ""

    report = ShadowRunner(config, command_runner=runner).run()
    assert report.comparisons[0].diff_kind == "error_b"
    assert report.total == 2  # 件级失败不炸整轮


def test_data_gate_forbids_business_data_dir(tmp_path: Path) -> None:
    """数据闸：output_dir 落 data/ 业务目录即拒跑（fail-closed，且零目录创建）。"""
    forbidden = REPO_ROOT / "data" / "shadow_should_never_exist"
    config = build_config(tmp_path, output_dir=forbidden)
    with pytest.raises(ShadowGateError, match="数据闸"):
        ShadowRunner(config, command_runner=side_runner({"wt-champion": "", "wt-challenger": ""})).run()
    assert not forbidden.exists()  # 零生产写证明


def test_code_gate_rejects_missing_or_same_worktrees(tmp_path: Path) -> None:
    config = build_config(tmp_path)
    broken = ShadowRunConfig(
        switch_id=config.switch_id,
        champion_worktree=tmp_path / "missing_wt",
        challenger_worktree=config.challenger_worktree,
        corpus_dir=config.corpus_dir,
        output_dir=config.output_dir,
        module_ref=config.module_ref,
    )
    with pytest.raises(ShadowGateError, match="代码闸"):
        ShadowRunner(broken, command_runner=side_runner({"missing_wt": "", "wt-challenger": ""})).run()
    same = ShadowRunConfig(
        switch_id=config.switch_id,
        champion_worktree=config.champion_worktree,
        challenger_worktree=config.champion_worktree,
        corpus_dir=config.corpus_dir,
        output_dir=config.output_dir,
        module_ref=config.module_ref,
    )
    with pytest.raises(ShadowGateError, match="双检出"):
        ShadowRunner(same, command_runner=side_runner({"wt-champion": "", "wt-challenger": ""})).run()


def test_corpus_freeze_violation_rejected(tmp_path: Path) -> None:
    corpus_dir = build_corpus(tmp_path)
    config = build_config(tmp_path, corpus_dir=corpus_dir)
    runner = ShadowRunner(config, command_runner=side_runner(
        {config.champion_worktree.name: "{}", config.challenger_worktree.name: "{}"}
    ))
    # 冻结后改 corpus（改 corpus=新 switch_id，在役改冻结集=违约）
    (corpus_dir / "case_9.json").write_text(json.dumps({"input": 9}), encoding="utf-8")
    with pytest.raises(ShadowGateError, match="冻结违约"):
        runner.run()
    # 未冻结（无 manifest）同样拒
    empty_dir = tmp_path / "corpus_unfrozen"
    empty_dir.mkdir()
    (empty_dir / "case_0.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ShadowGateError, match="未冻结"):
        ShadowRunner(
            build_config(tmp_path, corpus_dir=empty_dir),
            command_runner=side_runner({"wt-champion": "", "wt-challenger": ""}),
        ).verify_gates()


def test_default_runner_pythonpath_isolation(tmp_path: Path) -> None:
    """默认执行件：PYTHONPATH 仅指本 worktree src（禁 B import 主区代码）。"""
    wt = tmp_path / "wt-probe"
    (wt / "src").mkdir(parents=True)
    (wt / "src" / "shadow_probe.py").write_text(
        "import os, json\n\n"
        "def run(payload):\n"
        "    return {'pythonpath': os.environ.get('PYTHONPATH', ''), 'payload': payload}\n",
        encoding="utf-8",
    )
    item = tmp_path / "case_0.json"
    item.write_text(json.dumps({"input": 1}), encoding="utf-8")
    out_dir = tmp_path / "out"
    stdout, stderr = default_command_runner(wt, "shadow_probe:run", item, out_dir)
    result = json.loads(stdout)
    assert result["pythonpath"] == str(wt / "src")  # 覆盖式：不继承主区路径
    assert result["payload"] == {"input": 1}
    assert (out_dir / wt.name / "case_0.out.json").is_file()
    assert stderr == ""
    assert not (out_dir / MANIFEST_NAME).exists()
