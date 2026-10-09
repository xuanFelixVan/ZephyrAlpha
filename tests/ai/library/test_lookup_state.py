# [BLUEPRINT] MOD-LIB-003 | docs/03_modules/_domain_library/blueprint.md | §
# [TTL] permanent
"""lookup ``state`` 子命令回归（F1 资产状态断言·三源模式，st-examchief-20261009）。

零真库零生产路径：馆源 monkeypatch ``lookup_assets``；git 源用 tmp_path 真仓库
（中文消息验证 --grep/-S 的 subprocess UTF-8 编码链）；工棚/挂账源注入 tmp_path
假树（docs/_working 与 config 根均为 lookup_state 可注入参数）。锁定契约：
①每源一节 + state-snapshot 时间戳头；②零命中打 -- no hits --；③退出码
任一源命中=0 / 三源全零=1；④sources-with-hits 计数；⑤中文 query 全链；
⑥touched-paths 通道（源③命中文件反查落库提交）与单源行上限。
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

import pytest

from zephyr.library import lookup as lookup_mod

_SNAPSHOT_RE = re.compile(r"state-snapshot at \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}")


def _rows(count: int) -> list[dict[str, Any]]:
    return [
        {"asset_id": f"AST-{i}", "kind": "file", "status": "active", "home": f"docs/x{i}.md", "title": f"标题{i}"}
        for i in range(count)
    ]


def _all_sources_zero(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """三源全零替身：馆源空、git 空输出、工棚/挂账空目录（退出码 1 判定的基座）。"""
    monkeypatch.setattr(lookup_mod, "lookup_assets", lambda *a, **k: [])
    monkeypatch.setattr(lookup_mod, "_run_git", lambda *a, **k: "")
    workshop = tmp_path / "docs" / "_working"
    config = tmp_path / "config"
    workshop.mkdir(parents=True)
    config.mkdir()
    return workshop, config


def _git(repo: Path, *args: str) -> None:
    subprocess.run(  # noqa: S603 — 受控 git 自调用（tmp_path 测试仓，非外部输入）
        ["git", *args],
        cwd=str(repo),
        check=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.name", "tester")
    _git(repo, "config", "user.email", "tester@example.com")
    return repo


# ─────────────────────────── 编排契约（三源节/时间戳/退出码）───────────────────────


def test_all_zero_sources_exit_1_with_no_hits_markers(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any, capsys: pytest.CaptureFixture[str]
) -> None:
    """三源全零：退出码 1，三个 -- no hits --，sources-with-hits: 0/3，三处时间戳头。"""
    workshop, config = _all_sources_zero(monkeypatch, tmp_path)
    code = lookup_mod.lookup_state("GPU 摊销", repo_root=tmp_path, workshop_root=workshop, config_root=config)
    assert code == 1
    out = capsys.readouterr().out
    assert out.count("-- no hits --") == 3
    assert "sources-with-hits: 0/3" in out
    assert len(_SNAPSHOT_RE.findall(out)) == 3
    assert "== source-1: 馆索引 (lib_assets) ==" in out
    assert "== source-2: git log" in out
    assert "== source-3: 工棚+挂账面" in out


def test_any_source_hit_exit_0(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any, capsys: pytest.CaptureFixture[str]
) -> None:
    """仅工棚源命中：退出码 0，sources-with-hits: 1/3。"""
    monkeypatch.setattr(lookup_mod, "lookup_assets", lambda *a, **k: [])
    monkeypatch.setattr(lookup_mod, "_run_git", lambda *a, **k: "")
    workshop = tmp_path / "docs" / "_working"
    workshop.mkdir(parents=True)
    (workshop / "note.md").write_text("GPU 摊销 进度便签\n", encoding="utf-8")
    config = tmp_path / "config"
    config.mkdir()
    code = lookup_mod.lookup_state("GPU 摊销", repo_root=tmp_path, workshop_root=workshop, config_root=config)
    assert code == 0
    assert "sources-with-hits: 1/3" in capsys.readouterr().out


def test_empty_query_exit_1_zero_side_effects(capsys: pytest.CaptureFixture[str]) -> None:
    """空 query：直接退出码 1，不触任何源（无三源节输出）。"""
    code = lookup_mod.lookup_state("   ")
    assert code == 1
    assert "(state: empty query)" in capsys.readouterr().out


def test_state_subcommand_dispatch_and_audit(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any, audit_dir_like: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """main(["state", q, "--session", sid])：state 占位词不进 query，审计 face=state。"""
    import json

    import zephyr.governance.capability_lookup as cap_mod

    captured: dict[str, Any] = {}

    def _fake_state(query: str, **kwargs: Any) -> int:
        captured["query"] = query
        captured["kwargs"] = kwargs
        return 0

    monkeypatch.setattr(lookup_mod, "lookup_state", _fake_state)
    code = lookup_mod.main(["state", "GPU 摊销", "--session", "st-state-x"])
    assert code == 0
    assert captured["query"] == "GPU 摊销"
    audit_file = audit_dir_like / "st-state-x.jsonl"
    assert audit_file.exists()
    entry = json.loads(audit_file.read_text(encoding="utf-8").splitlines()[0])
    assert entry["query"] == {"query": "GPU 摊销", "face": "state"}
    assert entry["result_count"] == 1
    assert entry["tool"] == "zephyr.library.lookup"


@pytest.fixture()
def audit_dir_like(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> Path:
    """审计目录改道 tmp_path（测试隔离：禁写生产路径）。"""
    import zephyr.governance.capability_lookup as cap_mod

    target = tmp_path / "lookup_audit"
    monkeypatch.setattr(cap_mod, "LOOKUP_AUDIT_DIR", target)
    return target


# ─────────────────────────── 源③ 工棚+挂账面（tmp_path 假树）───────────────────────


def _make_workshop_tree(tmp_path: Path) -> tuple[Path, Path]:
    workshop = tmp_path / "docs" / "_working"
    config = tmp_path / "config"
    (workshop / "gpu_rewrite").mkdir(parents=True)
    (workshop / "unrelated").mkdir(parents=True)
    config.mkdir()
    (workshop / "gpu_rewrite" / "p1_wiring_benchmark.md").write_text(
        "GPU wiring benchmark 薄核卷宗\n无关行\n", encoding="utf-8"
    )
    (workshop / "unrelated" / "readme.md").write_text("完全无关的内容\n", encoding="utf-8")
    (workshop / "gpu_notes.md").write_text("无词内容\n", encoding="utf-8")  # 仅文件名命中
    (config / "search_space_prereg.yaml").write_text(
        "resonance_per_cell_seconds_target: 3.5\n"
        "resonance_per_cell_seconds_measured: 0.53  # 实测回填：gpu_core 薄核 0.53s/格；批量摊销复测待 L2 落地后重跑回填\n",
        encoding="utf-8",
    )
    (config / "unrelated.yaml").write_text("key: value\n", encoding="utf-8")
    return workshop, config


def test_workshop_source_hits_prereg_note_ranked_first(tmp_path: Any) -> None:
    """挂账便签（config，全词同现）置顶带摘录；战役目录文件优先列名并归目录命中组。"""
    workshop, config = _make_workshop_tree(tmp_path)
    lines, dir_paths, other_paths, has = lookup_mod._state_source_workshop("GPU 摊销", workshop, config)
    assert has
    assert lines[0].startswith("config/search_space_prereg.yaml")
    assert "[words 2/2]" in lines[0]
    joined = "\n".join(lines)
    assert "resonance_per_cell_seconds_measured" in joined  # 挂账便签原文（L2 行）
    assert "批量摊销复测待 L2 落地后重跑回填" in joined
    assert "docs/_working/gpu_rewrite/p1_wiring_benchmark.md" in joined  # 目录名命中列名
    assert "docs/_working/gpu_notes.md" in joined  # 文件名命中通道
    assert "unrelated" not in joined
    assert "config/search_space_prereg.yaml" in other_paths  # 内容命中组回喂源②
    assert "docs/_working/gpu_rewrite/p1_wiring_benchmark.md" in dir_paths  # 目录命中组回喂源②
    assert "docs/_working/unrelated/readme.md" not in dir_paths + other_paths


def test_workshop_source_zero_hits(tmp_path: Any) -> None:
    """空树：([], [], [], False)。"""
    workshop = tmp_path / "docs" / "_working"
    config = tmp_path / "config"
    workshop.mkdir(parents=True)
    config.mkdir()
    lines, dir_paths, other_paths, has = lookup_mod._state_source_workshop("GPU 摊销", workshop, config)
    assert lines == [] and dir_paths == [] and other_paths == [] and not has


def test_workshop_source_excerpt_and_total_caps(tmp_path: Any) -> None:
    """摘录策略：全词同现文件各取最佳 1 行，总输出 ≤15 行（规格 2 行上限）。"""
    workshop = tmp_path / "docs" / "_working"
    config = tmp_path / "config"
    (workshop / "big").mkdir(parents=True)
    config.mkdir()
    (workshop / "big" / "hits.md").write_text(
        "".join(f"GPU 第{i}行命中摊销内容\n" for i in range(30)),
        encoding="utf-8",
    )
    lines, _dir_paths, _other_paths, has = lookup_mod._state_source_workshop("GPU 摊销", workshop, config)
    assert has
    excerpt_lines = [line for line in lines if line.lstrip().startswith("L")]
    assert len(excerpt_lines) == 1  # 同现文件各取最佳 1 行
    assert "GPU 第0行命中摊销内容" in excerpt_lines[0]  # 取行号最前的同现行
    assert len(lines) <= 15


# ─────────────────────────── 源② git log（tmp_path 真仓）───────────────────────


def test_git_source_chinese_grep_and_pickaxe(tmp_path: Any) -> None:
    """真仓中文链：--grep 全串中文消息命中（grep 通道）+ 内容词 pickaxe 命中（-S 通道）。"""
    repo = _init_repo(tmp_path)
    (repo / "ledger.md").write_text("摊销术语落在内容里\n", encoding="utf-8")
    _git(repo, "add", "ledger.md")
    _git(repo, "commit", "-m", "chore: 无关键词消息")  # pickaxe 命中体：消息无词、内容有"摊销"
    (repo / "bench.md").write_text("benchmark\n", encoding="utf-8")
    _git(repo, "add", "bench.md")
    _git(repo, "commit", "-m", "[测试会话] GPU 摊销 薄核接线落地")  # grep 全串命中体
    lines, has = lookup_mod._state_source_gitlog("GPU 摊销", [], [], repo)
    assert has
    joined = "\n".join(lines)
    assert "[channel:grep]" in joined
    assert "[channel:pickaxe]" in joined
    assert "GPU 摊销 薄核接线落地" in joined  # 中文消息经 subprocess UTF-8 链无乱码


def test_git_source_touched_paths_channel(tmp_path: Any) -> None:
    """touched-paths 目录命中组：源③命中文件的落库提交（消息无词、内容有词）被反查出来。"""
    repo = _init_repo(tmp_path)
    target = repo / "docs" / "_working" / "x"
    target.mkdir(parents=True)
    (target / "e.md").write_text("GPU 内容证据\n", encoding="utf-8")
    _git(repo, "add", "docs/_working/x/e.md")
    _git(repo, "commit", "-m", "unrelated message body")
    lines, has = lookup_mod._state_source_gitlog("GPU 摊销", ["docs/_working/x/e.md"], [], repo)
    assert has
    joined = "\n".join(lines)
    assert "[channel:paths]" in joined
    assert "unrelated message body" in joined


def test_git_source_other_paths_group_and_stash_filtered(tmp_path: Any) -> None:
    """内容命中组（第二 pathspec 组）反查挂账册提交；stash 派生提交（WIP/index on）被过滤。"""
    repo = _init_repo(tmp_path)
    (repo / "config").mkdir()
    prereg = repo / "config" / "prereg.yaml"
    prereg.write_text("resonance: 0.53  # 摊销口径\n", encoding="utf-8")
    _git(repo, "add", "config/prereg.yaml")
    _git(repo, "commit", "-m", "declare budget caps")
    # 制造 stash 派生提交（改文件入 stash → WIP on/index on 两提交入 refs/stash）
    (repo / "config" / "prereg.yaml").write_text("resonance: 0.99  # GPU 改动\n", encoding="utf-8")
    _git(repo, "stash")
    lines, has = lookup_mod._state_source_gitlog("GPU 摊销", [], ["config/prereg.yaml"], repo)
    assert has
    joined = "\n".join(lines)
    assert "[channel:paths]" in joined
    assert "declare budget caps" in joined
    assert "WIP on" not in joined and "index on" not in joined


def test_git_source_no_hits_in_empty_repo(tmp_path: Any) -> None:
    """空仓（无提交）：git log 失败被吞，返回空表 has=False（不抛异常）。"""
    repo = _init_repo(tmp_path)
    lines, has = lookup_mod._state_source_gitlog("GPU 摊销", [], [], repo)
    assert lines == [] and not has


def test_git_source_total_cap_15(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    """总行上限：30 条候选只出 15 行（规格 2 每源 ≤15 行）。"""
    monkeypatch.setattr(
        lookup_mod,
        "_run_git",
        lambda *_a, **_k: "".join(f"abc{i:03d} fake subject line\n" for i in range(30)),
    )
    lines, has = lookup_mod._state_source_gitlog("gpu", [], [], tmp_path)
    assert has
    assert len(lines) == 15


def test_run_git_decodes_utf8_with_replace(tmp_path: Any) -> None:
    """_run_git 编码契约：显式 encoding=utf-8 + errors=replace（win32 中文消息不炸）。"""
    repo = _init_repo(tmp_path)
    (repo / "a.md").write_text("内容\n", encoding="utf-8")
    _git(repo, "add", "a.md")
    _git(repo, "commit", "-m", "中文提交消息")
    out = lookup_mod._run_git(["log", "--all", "--oneline"], repo)
    assert "中文提交消息" in out


# ─────────────────────────── 源① 馆索引（monkeypatch lookup_assets）───────────────────────


def test_index_source_renders_asset_home_title(monkeypatch: pytest.MonkeyPatch) -> None:
    """命中行含 asset_id/home/标题（≤10 条）。"""
    monkeypatch.setattr(lookup_mod, "lookup_assets", lambda *a, **k: _rows(2))
    lines, has = lookup_mod._state_source_index("GPU")
    assert has
    assert len(lines) == 2
    assert lines[0].startswith("AST-0\tdocs/x0.md\t")
    assert "标题0" in lines[0]


def test_index_source_word_fallback_after_full_query_miss(monkeypatch: pytest.MonkeyPatch) -> None:
    """全 query 零命中时逐词补充（"GPU 摊销"→词 GPU/摊销 各查一轮，≤10 条去重合并）。"""
    calls: list[str] = []

    def _fake_lookup(query: str, limit: int = 20, **kwargs: Any) -> list[dict[str, Any]]:
        calls.append(query)
        if query == "GPU":
            return _rows(1)
        return []

    monkeypatch.setattr(lookup_mod, "lookup_assets", _fake_lookup)
    lines, has = lookup_mod._state_source_index("GPU 摊销")
    assert has
    assert calls[0] == "GPU 摊销"
    assert "GPU" in calls
    assert lines[0].startswith("AST-0\t")


def test_index_source_error_isolated(monkeypatch: pytest.MonkeyPatch) -> None:
    """DB 故障：源级隔离——记错误行、has=False，不上抛拖垮证据包。"""

    def _boom(*a: object, **k: object) -> list[dict[str, Any]]:
        raise RuntimeError("pool down")

    monkeypatch.setattr(lookup_mod, "lookup_assets", _boom)
    lines, has = lookup_mod._state_source_index("GPU 摊销")
    assert not has
    assert len(lines) == 1
    assert "index source error" in lines[0]
