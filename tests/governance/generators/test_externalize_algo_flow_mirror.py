# [A_test] test_id=P21-MIRROR-001 | module=scripts/governance/d5_architecture/generators/externalize_algo_flow.py | gate=pytest
# [BLUEPRINT] MOD-GOV_ALGO_EXTRACTOR | scripts/governance/d5_architecture/generators/externalize_algo_flow.py | 容量镜像 GOV-DOC-018
# [MODULE] tests.governance.generators.test_externalize_algo_flow_mirror
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""test_externalize_algo_flow_mirror.py — 出仓器 GOV-DOC-018 容量镜像单元测试。

背景（P2-1 波次实证）：_domain_data 平铺 116/120、_domain_signal 102/120，剩余 6 个大域
（governance 356 / infrastructure 347 / feedback_loop 338 / shared 240 / gov_enforcement 200 /
security 188）按平铺命名必然撞 folder_capacity_hard_limit（T_soft=120 硬阻断）——
平铺契约在千件级域上不成立。治本=平铺饱和后按源子包镜像落点，超容量桶再按 stem 字符分片。

全测试在 tmp_path 假仓库里跑（monkeypatch ext.REPO_ROOT），零触真盘。
"""

from __future__ import annotations

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


def _module_src(stem: str) -> str:
    """带真内联 ALGO_FLOW 块的最小可解析模块（块形与 extractor/link-gate 夹具一致）。"""
    return (
        f'"""{stem} —— 测试夹具模块说明。\n'
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


def _mk_src(root: Path, rel: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(_module_src(p.stem), encoding="utf-8")
    return p


def _seed_flat(root: Path, domain_dir: str, n: int) -> None:
    d = root / "docs" / "03_modules" / domain_dir / "algo_flow"
    d.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        (d / f"legacy_{i:04d}.yaml").write_text(
            f"doc_type: architecture_view\nsource_of_truth: src/zephyr/d/legacy_{i:04d}.py\n", encoding="utf-8"
        )


@pytest.fixture(autouse=True)
def _isolate(monkeypatch, tmp_path):
    monkeypatch.setattr(ext, "REPO_ROOT", tmp_path)
    ext._PLANNED_MIRROR.clear()
    ext._PLANNED_REMAP.clear()
    ext._MIRROR_DOMAINS.clear()
    ext._EXISTING_YAML_CACHE.clear()
    yield tmp_path
    ext._PLANNED_MIRROR.clear()
    ext._PLANNED_REMAP.clear()
    ext._MIRROR_DOMAINS.clear()
    ext._EXISTING_YAML_CACHE.clear()


def test_below_trigger_keeps_flat_plan(tmp_path):
    """平铺余量充足 → 不入镜像表，_yaml_rel_for 平铺推导不变（既有域零影响）。"""
    targets = [_mk_src(tmp_path, f"src/zephyr/d/m{i}.py") for i in range(5)]
    ext._plan_capacity_mirrors(targets)
    assert ext._PLANNED_MIRROR == {}
    assert ext._MIRROR_DOMAINS == []
    assert ext._yaml_rel_for(targets[0], "src/zephyr/d/m0.py", "_domain_d").endswith("algo_flow/m0.yaml")


def test_saturated_domain_mirrors_subpackages(tmp_path):
    """平铺饱和 → 本批新件按源子包路径镜像落点（域根件入域名桶）。"""
    _seed_flat(tmp_path, "_domain_d", ext._MIRROR_TRIGGER)
    targets = [
        _mk_src(tmp_path, "src/zephyr/d/access/wal.py"),
        _mk_src(tmp_path, "src/zephyr/d/access/deep/codec.py"),
        _mk_src(tmp_path, "src/zephyr/d/boot.py"),
    ]
    ext._plan_capacity_mirrors(targets)
    got = {k: v.replace("docs/03_modules/_domain_d/algo_flow/", "") for k, v in ext._PLANNED_MIRROR.items()}
    assert got == {
        "src/zephyr/d/access/wal.py": "access/wal.yaml",
        "src/zephyr/d/access/deep/codec.py": "access/deep/codec.yaml",
        "src/zephyr/d/boot.py": "d/boot.yaml",
    }
    assert ext._MIRROR_DOMAINS == ["_domain_d"]


def test_same_stem_different_subpkg_needs_no_parent_prefix(tmp_path):
    """镜像目录本身消歧：跨子包同 stem 各得其所，不再产 parent__stem 长名。"""
    _seed_flat(tmp_path, "_domain_d", ext._MIRROR_TRIGGER)
    targets = [
        _mk_src(tmp_path, "src/zephyr/d/a/same.py"),
        _mk_src(tmp_path, "src/zephyr/d/b/same.py"),
    ]
    ext._plan_capacity_mirrors(targets)
    vals = sorted(ext._PLANNED_MIRROR.values())
    assert vals == [
        "docs/03_modules/_domain_d/algo_flow/a/same.yaml",
        "docs/03_modules/_domain_d/algo_flow/b/same.yaml",
    ]


def test_cross_pkg_same_bucket_disambiguates(tmp_path, monkeypatch):
    """两 pkg 映射同域、子包+stem 全同 → 桶内同名，整桶升级到 pkg__stem 消歧（绝不覆盖）。"""
    monkeypatch.setattr(ext, "_DOMAIN_DIRS", {**ext._DOMAIN_DIRS, "d": "_domain_d", "d2": "_domain_d"})
    _seed_flat(tmp_path, "_domain_d", ext._MIRROR_TRIGGER)
    targets = [
        _mk_src(tmp_path, "src/zephyr/d/sub/x.py"),
        _mk_src(tmp_path, "src/zephyr/d2/sub/x.py"),
    ]
    ext._plan_capacity_mirrors(targets)
    vals = sorted(ext._PLANNED_MIRROR.values())
    assert len(set(vals)) == 2
    assert all(v.count("algo_flow/sub/") == 1 for v in vals)
    assert all("__" in Path(v).name for v in vals)


def test_oversized_bucket_shards_and_stays_under_trigger(tmp_path):
    """单子包件数超桶触发 → 按 stem 首字符分片，任一分片仍 < 触发值。"""
    _seed_flat(tmp_path, "_domain_d", ext._MIRROR_TRIGGER)
    n = ext._BUCKET_TRIGGER * 2 + 8
    targets = [_mk_src(tmp_path, f"src/zephyr/d/big/{chr(97 + i % 26)}{i}.py") for i in range(n)]
    ext._plan_capacity_mirrors(targets)
    assert len(ext._PLANNED_MIRROR) == n
    by_dir: dict[Path, int] = {}
    for v in ext._PLANNED_MIRROR.values():
        d = (tmp_path / v).parent
        by_dir[d] = by_dir.get(d, 0) + 1
    assert max(by_dir.values()) < ext._BUCKET_TRIGGER
    assert all("big" in d.parts for d in by_dir)


def test_plan_independent_of_target_order(tmp_path):
    """落点与批内顺序无关（平铺改道时序依赖家族的第二例）。"""
    _seed_flat(tmp_path, "_domain_d", ext._MIRROR_TRIGGER)
    targets = [
        _mk_src(tmp_path, "src/zephyr/d/a/same.py"),
        _mk_src(tmp_path, "src/zephyr/d/b/same.py"),
        _mk_src(tmp_path, "src/zephyr/d/root_a.py"),
        _mk_src(tmp_path, "src/zephyr/d/a/same_core.py"),
    ]
    ext._plan_capacity_mirrors(targets)
    first = dict(ext._PLANNED_MIRROR)
    ext._plan_capacity_mirrors(list(reversed(targets)))
    assert ext._PLANNED_MIRROR == first


def test_existing_yaml_reuse_beats_mirror(tmp_path):
    """已落盘且 source_of_truth 命中 → 复用原平铺路径（重跑不改道，锚不错位）。"""
    _seed_flat(tmp_path, "_domain_d", ext._MIRROR_TRIGGER)
    p = _mk_src(tmp_path, "src/zephyr/d/access/wal.py")
    y = tmp_path / "docs/03_modules/_domain_d/algo_flow/wal.yaml"
    y.write_text(
        "doc_type: architecture_view\nsource_of_truth: src/zephyr/d/access/wal.py\n", encoding="utf-8"
    )
    ext._EXISTING_YAML_CACHE.clear()
    ext._plan_capacity_mirrors([p])
    rel = "src/zephyr/d/access/wal.py"
    assert ext._existing_yaml_for(rel, "_domain_d") == "docs/03_modules/_domain_d/algo_flow/wal.yaml"
    # externalize 选路：既有 yaml 最优先
    r = ext.externalize(p, dry_run=True)
    assert r["status"] == "dryrun"
    assert r["yaml"] == "docs/03_modules/_domain_d/algo_flow/wal.yaml"


def test_other_source_occupant_forces_escalation(tmp_path):
    """镜像落点被他人真源占用 → 升级消歧名，绝不改写他人 yaml。"""
    _seed_flat(tmp_path, "_domain_d", ext._MIRROR_TRIGGER)
    occupied = tmp_path / "docs/03_modules/_domain_d/algo_flow/access"
    occupied.mkdir(parents=True)
    (occupied / "wal.yaml").write_text(
        "doc_type: architecture_view\nsource_of_truth: src/zephyr/other/wal.py\n", encoding="utf-8"
    )
    p = _mk_src(tmp_path, "src/zephyr/d/access/wal.py")
    ext._plan_capacity_mirrors([p])
    planned = ext._PLANNED_MIRROR["src/zephyr/d/access/wal.py"]
    assert planned.endswith("access__wal.yaml")
    assert planned != "docs/03_modules/_domain_d/algo_flow/access/wal.yaml"
    # 真跑：新件落新名，占用件字节不变
    r = ext.externalize(p, dry_run=False)
    assert r["status"] == "externalized"
    assert (tmp_path / planned).is_file()
    assert "src/zephyr/other/wal.py" in (occupied / "wal.yaml").read_text(encoding="utf-8")


def test_dry_run_prediction_equals_written_path(tmp_path):
    """dry-run 预测 == 正式落盘路径（批次计划与实盘零时序依赖）。"""
    _seed_flat(tmp_path, "_domain_d", ext._MIRROR_TRIGGER)
    targets = [
        _mk_src(tmp_path, "src/zephyr/d/access/wal.py"),
        _mk_src(tmp_path, "src/zephyr/d/boot.py"),
    ]
    ext._plan_capacity_mirrors(targets)
    predicted = {p.name: ext.externalize(p, dry_run=True)["yaml"] for p in targets}
    ext._plan_capacity_mirrors(targets)
    for p in targets:
        r = ext.externalize(p, dry_run=False)
        assert r["status"] == "externalized", r
        assert r["yaml"] == predicted[p.name]
        assert (tmp_path / r["yaml"]).is_file()
        assert not p.with_suffix(".py.bak").exists()
        # 源码只留一行锚
        assert f"# [ALGO_FLOW] external: {r['yaml']}" in p.read_text(encoding="utf-8")


def test_never_overwrites_foreign_yaml_even_when_derived(tmp_path):
    """平铺推导+parent__ 前缀两格都被他人真源占满 → 写前占用检测报 failed（绝不静默改写）。"""
    d = tmp_path / "docs/03_modules/_domain_d/algo_flow"
    d.mkdir(parents=True)
    for name, owner in (("solo.yaml", "src/zephyr/other/solo.py"), ("d__solo.yaml", "src/zephyr/x/solo.py")):
        (d / name).write_text(
            f"doc_type: architecture_view\nsource_of_truth: {owner}\n", encoding="utf-8"
        )
    p = _mk_src(tmp_path, "src/zephyr/d/solo.py")
    r = ext.externalize(p, dry_run=False)
    assert r["status"] == "failed"
    assert "被他人真源占用" in r["reason"]
    for name in ("solo.yaml", "d__solo.yaml"):
        assert "src/zephyr/" in (d / name).read_text(encoding="utf-8")
    assert "# [ALGO_FLOW]" in p.read_text(encoding="utf-8")  # 源文件保持内联未动
