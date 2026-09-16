# [A_test] test_id=P21-DEBT-001 | module=scripts/governance/d5_architecture/generators/report_algo_flow_author_debt.py | gate=pytest
# [BLUEPRINT] MOD-GOV_ALGO_EXTRACTOR | docs/03_modules/_cross_layer/gov_scripts/blueprint.md | §algo_flow_author_debt
# [MODULE] tests.governance.generators.test_report_algo_flow_author_debt
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_report_algo_flow_author_debt.py — 作者欠账台账生成器单元测试（P2-1 尾池）。

钉扎三件事（都是本战役踩过坑的地方）：
  1. 三态分桶正确（五段式散文 / 零边 / 零节点），且报因字符串直接来自出仓器常量——
     出仓器改写措辞即本测试变红（台账与工具不许脱钩）；
  2. ``classify_pool`` 全链零写入：externalize(dry_run=True) 若偷偷落盘（改源码/新建
     yaml）即刻失败——dry-run 是"只报告"的全部前提；
  3. markdown 写手产出的 GENERATED 标记与计数自证（静态清单必由生成器产出）。

全部在 tmp_path 假仓库里跑（monkeypatch rep.REPO_ROOT / ext.REPO_ROOT），零触真盘。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from zephyr.shared.io.paths import REPO_ROOT

_GOV_DIR = str(REPO_ROOT / "scripts" / "governance")
_GEN_DIR = str(REPO_ROOT / "scripts" / "governance" / "d5_architecture" / "generators")
for _p in (_GOV_DIR, _GEN_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import externalize_algo_flow as ext  # noqa: E402
import report_algo_flow_author_debt as rep  # noqa: E402


def _prose_src(stem: str) -> str:
    """五段式散文块（旧机器块语法：有标记无 ``# - id:`` 行）。"""
    return (
        f'"""{stem} —— 五段式散文夹具。\n'
        f"\n"
        f"# [ALGO_FLOW]\n"
        f"# 输入: 原始行情\n"
        f"# 算法: 先清洗再聚合\n"
        f"# 输出: 因子序列\n"
        f"# [/ALGO_FLOW]\n"
        f'"""\n'
    )


def _no_edges_src(stem: str) -> str:
    """截断型零边块（有节点无收标记无边）——出仓即造门禁必拦的零边镜像。"""
    return (
        f'"""{stem} —— 截断型零边夹具。\n'
        f"\n"
        f"# [ALGO_FLOW]\n"
        f"# 层: 输入\n"
        f"# - id: I1\n"
        f"#   name: 入参\n"
        f"# 层: 算法\n"
        f"# - id: A1\n"
        f"#   name_zh: ① 主流程\n"
        f'"""\n'
    )


def _no_nodes_src(stem: str) -> str:
    """闭合但零节点的手写速记块（既无 ``- id:`` 也非五段式）→ 须逐件诊断。"""
    return (
        f'"""{stem} —— 手写速记夹具。\n'
        f"\n"
        f"# [ALGO_FLOW]\n"
        f"# 大致流程：先取数、再算比值、最后落库（速记）\n"
        f"# [/ALGO_FLOW]\n"
        f'"""\n'
    )


def _mechanical_src(stem: str) -> str:
    """可机械出仓的完整块（有节点也有边）——落 resolvable 桶，不算欠账。"""
    return (
        f'"""{stem} —— 可机械出仓夹具。\n'
        f"\n"
        f"# [ALGO_FLOW]\n"
        f"# 层: 输入\n"
        f"# - id: I1\n"
        f"#   name: 入参\n"
        f"# 层: 算法\n"
        f"# - id: A1\n"
        f"#   name_zh: ① 主流程\n"
        f"# [/ALGO_FLOW]\n"
        f"# 边:\n"
        f"# I1 --> A1\n"
        f'"""\n'
    )


@pytest.fixture
def fake_repo(tmp_path: Path) -> Path:
    """假仓库（tmp_path 的子目录）：src/zephyr/demo/ 下四件夹具（三态欠账+一件可机械出仓）。

    刻意与 tmp_path 隔开一层：CLI 测试把 --out/--json 落在 tmp_path 里，快照只盯假仓库，
    产物写在仓外不会被误判成"生成器偷写"。
    """
    root = tmp_path / "repo"
    for stem, writer in (
        ("legacy_prose", _prose_src),
        ("no_edge_truncated", _no_edges_src),
        ("unparsable_note", _no_nodes_src),
        ("mech_ok", _mechanical_src),
    ):
        p = root / "src" / "zephyr" / "demo" / f"{stem}.py"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(writer(stem), encoding="utf-8")
    return root


def _pool(root: Path) -> list[Path]:
    d = root / "src" / "zephyr" / "demo"
    return sorted(d.glob("*.py"))


def _snapshot(root: Path) -> dict[str, bytes]:
    """全仓文件字节快照（含 docs/ 下 yaml）——零写入判据的证据。"""
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def test_classify_pool_buckets_three_debt_classes(fake_repo):
    cls = rep.classify_pool(_pool(fake_repo), fake_repo)
    counts = cls["counts"]
    assert counts["prose"] == 1
    assert counts["no_edges"] == 1
    assert counts["no_nodes"] == 1
    assert counts["resolvable"] == 1
    assert counts["other"] == 0
    assert counts["debt_total"] == 3
    # 恒等式：欠账 + 可机械 + 其他 = 池总数（少报一件即台账失真）
    assert counts["debt_total"] + counts["resolvable"] + counts["other"] == counts["pool"] == 4


def test_bucket_reasons_are_outboxer_constants(fake_repo):
    """报因真源=出仓器常量：出仓器改写措辞即本测试变红（不许两处各写一份）。"""
    cls = rep.classify_pool(_pool(fake_repo), fake_repo)
    by_class = {e["class"]: e for e in cls["entries"]}
    assert by_class["prose"]["reason"] == ext._LEGACY_PROSE_SKIP_REASON
    assert by_class["no_edges"]["reason"] == ext._NO_EDGE_SKIP_REASON
    assert by_class["no_nodes"]["reason"] == ext._NO_NODES_SKIP_REASON
    assert by_class["prose"]["status"] == "skipped"
    assert by_class["prose"]["group"] == "demo"
    assert ext._is_content_skip_reason(by_class["no_nodes"]["reason"]) is True


def test_classify_pool_is_zero_write(fake_repo):
    """dry_run=True 必须零写入：源码字节不变、docs/ 下不得冒出新 yaml。"""
    before = _snapshot(fake_repo)
    rep.classify_pool(_pool(fake_repo), fake_repo)
    assert _snapshot(fake_repo) == before
    assert not (fake_repo / "docs").exists()


def test_classify_pool_restores_outboxer_repo_root(fake_repo):
    prev = ext.REPO_ROOT
    rep.classify_pool(_pool(fake_repo), fake_repo)
    assert prev == ext.REPO_ROOT


def test_classify_pool_keeps_missing_entries_visible(fake_repo):
    """清单与盘脱钩时不得静默少报：缺件进 other 桶并带报因。"""
    paths = _pool(fake_repo) + [fake_repo / "src" / "zephyr" / "demo" / "ghost.py"]
    cls = rep.classify_pool(paths, fake_repo)
    assert cls["counts"]["pool"] == 5
    assert cls["counts"]["other"] == 1
    ghost = [e for e in cls["entries"] if e["file"].endswith("ghost.py")][0]
    assert ghost["status"] == "missing"
    assert ghost["reason"]


def test_render_report_marker_and_listings(fake_repo):
    cls = rep.classify_pool(_pool(fake_repo), fake_repo)
    md = rep.render_report(cls, source="`--file-list fake.txt`")
    head = md.splitlines()
    # frontmatter 必在首（docs/_working/ 是 temporary 区，.md 无 frontmatter 即 TTL-METADATA 硬拦）
    assert head[0] == "---"
    assert "ttl: task_bound" in md
    assert rep._GENERATED_MARKER in head[:8]
    assert head[head.index("---", 1) + 2] == rep._GENERATED_MARKER
    assert "\r\n" not in md
    assert "## 统计" in md
    for needle in (
        ext._LEGACY_PROSE_SKIP_REASON,
        ext._NO_EDGE_SKIP_REASON,
        ext._NO_NODES_SKIP_REASON,
    ):
        assert f"`{needle}`" in md
    for name in ("legacy_prose.py", "no_edge_truncated.py", "unparsable_note.py", "mech_ok.py"):
        assert name in md
    assert "### demo（1 件）" in md


def test_main_writes_report_and_json_without_touching_repo(fake_repo, monkeypatch, tmp_path):
    """CLI 端到端：只写 --out/--json（均在 tmp_path），真仓 docs/ 不冒产物。"""
    monkeypatch.setattr(rep, "REPO_ROOT", fake_repo)
    list_file = fake_repo / "pool.txt"
    list_file.write_text(
        "\n".join(p.relative_to(fake_repo).as_posix() for p in _pool(fake_repo)) + "\n",
        encoding="utf-8",
    )
    before = _snapshot(fake_repo)
    real_ledger = REPO_ROOT / "docs" / "_working" / "reports" / "algo_flow_author_debt.md"
    ledger_before = real_ledger.read_bytes() if real_ledger.is_file() else None
    out_md = tmp_path / "outside" / "debt.md"
    out_json = tmp_path / "outside" / "debt.json"
    rc = rep.main(
        ["--file-list", str(list_file), "--out", str(out_md), "--json", str(out_json)]
    )
    assert rc == 0
    assert out_md.is_file() and out_json.is_file()
    written = out_md.read_text(encoding="utf-8").splitlines()
    assert written[0] == "---" and rep._GENERATED_MARKER in written[:8]
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["counts"]["debt_total"] == 3
    assert payload["counts"]["resolvable"] == 1
    assert len(payload["entries"]) == 4
    assert payload["debt_classes"]["no_edges"]["skip_reason"] == ext._NO_EDGE_SKIP_REASON
    assert _snapshot(fake_repo) == before
    # 零写入判据用指纹，不用"不存在"：台账一经交付进 HEAD 就长存，断不存在=交付即炸本测试
    assert (real_ledger.read_bytes() if real_ledger.is_file() else None) == ledger_before, (
        "--out 未生效：CLI 写了真仓生产台账路径"
    )


def test_read_file_list_skips_blanks_and_comments(tmp_path):
    lst = tmp_path / "list.txt"
    lst.write_text(
        "# 注释行\n\nsrc/zephyr/a/b.py\nsrc\\zephyr\\c\\d.py\n", encoding="utf-8"
    )
    paths = rep.read_file_list(lst, tmp_path)
    assert [p.as_posix().split("/src/")[-1] for p in paths] == ["zephyr/a/b.py", "zephyr/c/d.py"]
