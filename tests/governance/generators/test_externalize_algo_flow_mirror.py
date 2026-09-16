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
import _shared.code_algorithm_extractor as coae  # noqa: E402


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
    # 两个根都要打桩：出仓器落点用 ext.REPO_ROOT，写时终验走 extractor 自己的 REPO_ROOT
    monkeypatch.setattr(ext, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(coae, "REPO_ROOT", tmp_path)
    ext._IGNORED_DIR_NAMES = None
    ext._PLANNED_MIRROR.clear()
    ext._PLANNED_REMAP.clear()
    ext._PLANNED_UNIQ.clear()
    ext._MIRROR_DOMAINS.clear()
    ext._EXISTING_YAML_CACHE.clear()
    yield tmp_path
    ext._IGNORED_DIR_NAMES = None
    ext._PLANNED_MIRROR.clear()
    ext._PLANNED_REMAP.clear()
    ext._PLANNED_UNIQ.clear()
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


def test_manifest_mode_targets_are_cross_package_one_batch(tmp_path, capsys):
    """--files-from 清单模式：整波跨包一次规划（逐 pkg 调用会把同域镜像规划切批）。

    波次并发前提：一个域目录只由一个会话规划——清单模式是 6 个并发子代理共用
    单一批次规划入口，同时跳过缺失/非 .py 行（清单与盘不同步时宁漏勿错）。
    """
    a = _mk_src(tmp_path, "src/zephyr/dz/access/wal.py")
    b = _mk_src(tmp_path, "src/zephyr/dz/boot.py")
    manifest = tmp_path / ".runtime/tmp/plan.txt"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        "\n".join(
            [
                "src/zephyr/dz/access/wal.py",
                "src/zephyr/dz/boot.py",
                "src/zephyr/dz/gone.py",  # 缺失 → 跳过
                "docs/notes.md",  # 非 .py → 跳过
                "",
            ]
        ),
        encoding="utf-8",
    )
    got = ext._iter_targets(None, None, ".runtime/tmp/plan.txt")
    assert got == [a, b]
    assert ext.main(["--files-from", ".runtime/tmp/plan.txt", "--dry-run"]) == 0
    import json as _json

    out = _json.loads(capsys.readouterr().out)
    assert out["summary"] == {"dryrun": 2}
    assert {r["file"] for r in out["results"]} == {
        "src/zephyr/dz/access/wal.py",
        "src/zephyr/dz/boot.py",
    }


def test_same_named_subpackage_init_files_get_unique_landing(tmp_path):
    """批级注入性：不同子包同名 __init__.py 不得共用一个 yaml（后者覆盖=静默丢图）。

    2026-09-16 波次 dry-run 普查实证（grp6 唯一碰撞对）：
    signal_fundamental/{gen,strategy}/implementations/__init__.py 都推导
    implementations__init__.yaml。rel 字典序首件保原名，次件升阶梯名；两件都落盘。
    """
    a = _mk_src(tmp_path, "src/zephyr/sf/gen/implementations/__init__.py")
    b = _mk_src(tmp_path, "src/zephyr/sf/strategy/implementations/__init__.py")
    ext._plan_stem_collision_remaps([a, b])  # __init__ 不入 stem 表（既有契约）
    ext._plan_capacity_mirrors([a, b])
    ext._plan_path_uniqueness([a, b])
    ra = ext.externalize(a, dry_run=True)
    rb = ext.externalize(b, dry_run=True)
    assert ra["yaml"] != rb["yaml"], (ra, rb)
    assert ra["yaml"].endswith("implementations__init__.yaml")  # 首件原名不动
    assert rb["yaml"].startswith(ra["yaml"].rsplit("/", 1)[0] + "/")
    for r in (ra, rb):
        assert "___init__" not in r["yaml"]  # 域目录不得退化成 _domain___init__
    ext._plan_path_uniqueness([b, a])
    assert {ext.externalize(x, dry_run=True)["yaml"] for x in (a, b)} == {
        ra["yaml"],
        rb["yaml"],
    }  # 与批内顺序无关


def test_uniqueness_pass_leaves_non_colliding_plan_untouched(tmp_path):
    """无碰撞批：注入性收口零改道（既有平铺/镜像命名契约不回跳）。"""
    targets = [
        _mk_src(tmp_path, "src/zephyr/d/access/wal.py"),
        _mk_src(tmp_path, "src/zephyr/d/impl/__init__.py"),
        _mk_src(tmp_path, "src/zephyr/d/boot.py"),
    ]
    ext._plan_capacity_mirrors(targets)
    before = {p.name: ext._predicted_yaml_rel(p, p.relative_to(tmp_path).as_posix(), "_domain_d") for p in targets}
    ext._plan_path_uniqueness(targets)
    assert ext._PLANNED_UNIQ == {}
    after = {p.name: ext._predicted_yaml_rel(p, p.relative_to(tmp_path).as_posix(), "_domain_d") for p in targets}
    assert after == before


def test_foreign_occupant_escalates_at_plan_time(tmp_path):
    """盘上他人真源占用（无批内碰撞）→ 规划期升档，不再永久 failed（grp2 cross_asset 实证）。"""
    foreign = tmp_path / "docs/03_modules/_domain_trading/algo_flow"
    foreign.mkdir(parents=True)
    (foreign / "core__init__.yaml").write_text(
        "doc_type: architecture_view\nsource_of_truth: src/zephyr/trading/core/__init__.py\n", encoding="utf-8"
    )
    p = _mk_src(tmp_path, "src/zephyr/cross_asset/core/__init__.py")
    rel = "src/zephyr/cross_asset/core/__init__.py"
    ext._plan_path_uniqueness([p])
    assert ext._PLANNED_UNIQ[rel].endswith("cross_asset__core__init__.yaml")
    r = ext.externalize(p, dry_run=False)
    assert r["status"] == "externalized", r
    assert r["yaml"] == ext._PLANNED_UNIQ[rel]
    # 他人真源逐字不动
    assert "src/zephyr/trading/core/__init__.py" in (foreign / "core__init__.yaml").read_text(encoding="utf-8")


def test_rerun_reports_already_with_anchor_target(tmp_path):
    """幂等复跑口径：已出仓件必须报 already（曾误报 skipped/no inline block，dry-run 失真）。"""
    p = _mk_src(tmp_path, "src/zephyr/d/again.py")
    first = ext.externalize(p, dry_run=False)
    assert first["status"] == "externalized", first
    again = ext.externalize(p, dry_run=False)
    assert again["status"] == "already"
    assert again["yaml"] == first["yaml"]


def test_header_only_block_is_promoted_and_externalized(tmp_path):
    """契约头单真源形态（无锚）：头块转正进 docstring 后走同一管写出仓。

    旧口径是 skipped + "unreachable"——184 件因此长期停在"读卡路径看不见的头块"里，
    既不出仓也没人删（P2-1 死块普查 2026-09-16）。
    """
    p = tmp_path / "src/zephyr/d/dead.py"
    p.parent.mkdir(parents=True)
    p.write_text(
        "# [BLUEPRINT] MOD-X | docs/03_modules/_domain_d/blueprint.md\n"
        "# [ALGO_FLOW]\n# 层: 输入\n# - id: B1\n#   name: 头块节点\n# [/ALGO_FLOW]\n"
        '"""DeadBanner — 横幅区块，docstring 无块。\n\n概述文字。\n"""\n\nX = 1\n',
        encoding="utf-8",
    )
    r = ext.externalize(p, dry_run=False)
    assert r["status"] == "externalized", r
    assert r["header_promoted"] is True
    src = p.read_text(encoding="utf-8")
    assert ext._header_block_spans(src) == []
    assert src.count("# [ALGO_FLOW]") == 1  # 只剩锚行
    machine = ext._yaml_machine_block(tmp_path / r["yaml"])
    assert "- id: B1" in machine and "头块节点" in machine
    # 转正后 extractor 看得见（旧形态永远看不见=死图）
    got = coae.extract_algorithm_from_code(p, module_id="", truncate=False)
    assert [n.id for n in got.algo_flow.nodes] == ["B1"]


def test_residual_dead_block_reconciled_into_prose(tmp_path):
    """出仓成功后残留死块（第二个裸字符串字面量块）不再只计数：未覆盖口径进 prose。"""
    p = tmp_path / "src/zephyr/d/twoblock.py"
    p.parent.mkdir(parents=True)
    p.write_text(
        '"""TwoBlock — 契约头减负夹具。\n\n'
        "# [ALGO_FLOW]\n# 层: 输入\n# - id: I1\n#   name: 入参\n# [/ALGO_FLOW]\n"
        '"""\n\n'
        "X = 1\n\n"
        '"""\n'
        "# [ALGO_FLOW]\n# 层: 输入\n# - id: DEAD1\n#   name: 第二个字符串字面量块\n# [/ALGO_FLOW]\n"
        '"""\n',
        encoding="utf-8",
    )
    r = ext.externalize(p, dry_run=False)
    assert r["status"] == "externalized", r
    rec = r["header_reconcile"]
    assert rec["status"] == "reconciled", rec
    assert rec["prose_blocks"] == 1
    src = p.read_text(encoding="utf-8")
    assert ext._header_block_spans(src) == []
    assert "DEAD1" not in src
    ytxt = (tmp_path / r["yaml"]).read_text(encoding="utf-8")
    assert "DEAD1" in ytxt and f"{ext._PROSE_KEY}:" in ytxt
    assert ext._ids_of(ext._yaml_machine_block(tmp_path / r["yaml"])) == {"I1"}


def _mk_dual_truth(tmp_path: Path, rel: str, header_block: str) -> tuple[Path, str]:
    """造 184 件盘上现场：docstring 已带锚（yaml 已落）+ 契约头留一份 ALGO_FLOW 副本。"""
    p = tmp_path / rel
    p.parent.mkdir(parents=True)
    p.write_text(
        "# [BLUEPRINT] MOD-X | docs/03_modules/_domain_d/blueprint.md\n"
        "# [TTL] permanent\n"
        + _module_src(p.stem),
        encoding="utf-8",
    )
    first = ext.externalize(p, dry_run=False)
    assert first["status"] == "externalized", first
    txt = p.read_text(encoding="utf-8")
    assert "# [ALGO_FLOW] external:" in txt
    p.write_text(txt.replace("# [TTL] permanent\n", "# [TTL] permanent\n" + header_block), encoding="utf-8")
    assert ext._header_block_spans(p.read_text(encoding="utf-8"))
    return p, first["yaml"]


def test_anchored_header_duplicate_dropped_without_prose(tmp_path):
    """头块是 yaml 机器块的旧快照（节点 id 全被覆盖）→ 直删，不造 prose 键（零信息损失）。"""
    dup = (
        "# [ALGO_FLOW]\n# 层: 输入\n# - id: I1\n#   name: 入参\n# 层: 算法\n"
        "# - id: A1\n#   name_zh: ① 主流程\n# [/ALGO_FLOW]\n"
    )
    p, yaml_rel = _mk_dual_truth(tmp_path, "src/zephyr/d/dup.py", dup)
    r = ext.externalize(p, dry_run=False)
    assert r["status"] == "already", r
    assert r["header_reconcile"]["status"] == "reconciled", r
    assert r["header_reconcile"]["deleted_blocks"] == 1
    src = p.read_text(encoding="utf-8")
    assert ext._header_block_spans(src) == []
    assert src.count("# [ALGO_FLOW]") == 1  # 只剩锚行
    ytxt = (tmp_path / yaml_rel).read_text(encoding="utf-8")
    assert ext._PROSE_KEY not in ytxt
    assert ext._ids_of(ext._yaml_machine_block(tmp_path / yaml_rel)) == {"I1", "A1"}


def test_anchored_header_shorthand_preserved_verbatim(tmp_path):
    """头块是手写算法速记（yaml 机器块无此口径）→ 逐字进 prose 后才删头块。"""
    shorthand = "# [ALGO_FLOW]\n# F1: 阈值>0.3 判漂移\n# [/ALGO_FLOW]\n"
    p, yaml_rel = _mk_dual_truth(tmp_path, "src/zephyr/d/prose.py", shorthand)
    r = ext.externalize(p, dry_run=False)
    rec = r["header_reconcile"]
    assert rec["status"] == "reconciled" and rec["prose_blocks"] == 1, rec
    src = p.read_text(encoding="utf-8")
    assert ext._header_block_spans(src) == [] and "F1:" not in src
    ytxt = (tmp_path / yaml_rel).read_text(encoding="utf-8")
    assert "F1: 阈值>0.3 判漂移" in ytxt and f"{ext._PROSE_KEY}:" in ytxt
    assert ext._ids_of(ext._yaml_machine_block(tmp_path / yaml_rel)) == {"I1", "A1"}


def test_reconcile_write_failure_restores_both_files(tmp_path, monkeypatch):
    """清偿中途写盘失败必须双件还原（不留"头块已删/prose 未落"的半吊子真源）。"""
    shorthand = "# [ALGO_FLOW]\n# F9: 只有头块有的口径\n# [/ALGO_FLOW]\n"
    p, yaml_rel = _mk_dual_truth(tmp_path, "src/zephyr/d/rollback.py", shorthand)
    before_py = p.read_bytes()
    yaml_path = tmp_path / yaml_rel
    before_y = yaml_path.read_bytes()

    real = ext.safe_write_text

    def _fail_on_py(path, content, *a, **k):
        if str(path).endswith(".yaml"):
            return real(path, content, *a, **k)
        raise OSError("simulated .py write lock")

    monkeypatch.setattr(ext, "safe_write_text", _fail_on_py)
    res = ext._reconcile_header_blocks(p, False)
    monkeypatch.undo()
    assert res["status"] == "failed", res
    assert p.read_bytes() == before_py
    assert yaml_path.read_bytes() == before_y


def test_unparsable_header_mirror_deduped_without_yaml(tmp_path):
    """双位镜像件（无锚无 yaml，块为速记不可解析）：头块与 docstring 块逐字相同 → 删头块。

    盘上现场=risk_layer_orchestrator（2026-08-18 人工恢复 docstring 副本时留的头注镜像）。
    此类件出仓器永不产 yaml（速记块 parse 无节点），若只报 skipped 则门禁第 3 判据把该件
    永久锁死在"不可提交"态，故按 docstring 参照清偿。
    """
    shorthand = "# [ALGO_FLOW]\n# I1: nav(盘中净值)\n# F1: evaluate_intraday(净值→回撤)\n# [/ALGO_FLOW]\n"
    p = tmp_path / "src/zephyr/d/mirror.py"
    p.parent.mkdir(parents=True)
    p.write_text(
        "# [BLUEPRINT] MOD-X | docs/03_modules/_domain_d/blueprint.md\n"
        "# [TTL] permanent\n"
        + shorthand
        + '"""Mirror — 双位镜像夹具。\n\n'
        + shorthand
        + '"""\n\nX = 1\n',
        encoding="utf-8",
    )
    r = ext.externalize(p, dry_run=False)
    assert r["status"] == "deduped", r
    assert r["deleted_blocks"] == 1 and r["prose_blocks"] == 0, r
    src = p.read_text(encoding="utf-8")
    assert ext._header_block_spans(src) == []
    assert src.count("# [ALGO_FLOW]") == 1  # 只剩 docstring 内那一份
    assert "F1: evaluate_intraday" in ext._module_docstring(src)  # 口径零损失
    assert not (tmp_path / "docs/03_modules/_domain_d/algo_flow").exists()


def test_uncovered_header_mirror_without_yaml_is_not_deleted(tmp_path):
    """同类件但头块含 docstring 没有的口径 → 无 yaml 可归并 → 拒绝删除（不静默销毁）。"""
    inner = "# [ALGO_FLOW]\n# I1: nav(盘中净值)\n# [/ALGO_FLOW]\n"
    outer = "# [ALGO_FLOW]\n# I1: nav(盘中净值)\n# A9: 只有头块有的清算口径\n# [/ALGO_FLOW]\n"
    p = tmp_path / "src/zephyr/d/mirror_uncovered.py"
    p.parent.mkdir(parents=True)
    p.write_text(
        "# [TTL] permanent\n" + outer + '"""MirrorUncovered — 夹具。\n\n' + inner + '"""\n\nX = 1\n',
        encoding="utf-8",
    )
    before = p.read_bytes()
    r = ext.externalize(p, dry_run=False)
    assert r["status"] == "skipped", r
    assert r["header_dedup"]["status"] == "failed" and "无 yaml" in r["header_dedup"]["reason"]
    assert p.read_bytes() == before  # 逐字节未动


def test_unparsable_promoted_block_stays_inline(tmp_path):
    """只在契约头的速记块：转正后仍不可解析 → 留在 docstring（promoted_inline），不回滚。

    盘上现场=drift_observatory_orchestrator / wyckoff_walkforward。回滚等于把此类件永久
    锁死在死块态；转正后它和全仓其他不可解析块同状态（内联单真源、门禁放行）。
    """
    p = tmp_path / "src/zephyr/d/shorthand_head.py"
    p.parent.mkdir(parents=True)
    p.write_text(
        "# [BLUEPRINT] MOD-X | docs/03_modules/_domain_d/blueprint.md\n"
        "# [ALGO_FLOW]\n# I1: 入参速记\n# F1: 主流程速记\n# [/ALGO_FLOW]\n"
        '"""ShorthandHead — 速记只在头注。\n\n概述。\n"""\n\nX = 1\n',
        encoding="utf-8",
    )
    r = ext.externalize(p, dry_run=False)
    assert r["status"] == "promoted_inline", r
    assert r["header_promoted"] is True
    src = p.read_text(encoding="utf-8")
    assert ext._header_block_spans(src) == []
    doc = ext._module_docstring(src)
    assert "I1: 入参速记" in doc and "F1: 主流程速记" in doc  # 逐字进 docstring
    assert src.count("# [ALGO_FLOW]") == 1
    assert not (tmp_path / "docs/03_modules/_domain_d/algo_flow").exists()
    import ast

    ast.parse(src)


def test_gitignore_named_bucket_is_renamed(tmp_path):
    """撞 .gitignore 目录型忽略规则的镜像桶改道 *_doc——否则落点 yaml 静默漏提交、源码锚点变悬空指针。

    波次实证：src/zephyr/infrastructure/system_telemetry/logs/ 的镜像桶原名 logs，
    .gitignore:234 的未锚定 ``logs/`` 规则把它整域吞掉，登记工具（git ls-files --others）
    看不见=CREATE-GUARD 无令牌可查=提交静默漏件。
    """
    (tmp_path / ".gitignore").write_text(
        "# ignore rules\nlogs/\nbuild\n!keep/\n/runtime/\n*.tmp\n", encoding="utf-8"
    )
    _seed_flat(tmp_path, "_domain_d", ext._MIRROR_TRIGGER)
    p = _mk_src(tmp_path, "src/zephyr/d/logs/wal.py")
    ext._plan_capacity_mirrors([p])
    planned = ext._PLANNED_MIRROR["src/zephyr/d/logs/wal.py"]
    assert planned == "docs/03_modules/_domain_d/algo_flow/logs_doc/wal.yaml"
    r = ext.externalize(p, dry_run=False)
    assert r["status"] == "externalized", r
    assert r["yaml"] == planned
    assert (tmp_path / planned).is_file()
    assert f"# [ALGO_FLOW] external: {planned}" in p.read_text(encoding="utf-8")


def test_unanchored_rules_only_and_nested_segments(tmp_path):
    """只认未锚定纯目录名规则（/runtime/ 带锚定、*.tmp 带通配、!keep/ 取反都不算）；嵌套段逐段规避。"""
    (tmp_path / ".gitignore").write_text("logs/\nbuild\n!keep/\n/runtime/\n*.tmp\n", encoding="utf-8")
    ignored = ext._gitignored_dir_names()
    assert {"logs", "build"} <= ignored
    assert not {"keep", "runtime", "*.tmp"} & ignored
    _seed_flat(tmp_path, "_domain_d", ext._MIRROR_TRIGGER)
    p = _mk_src(tmp_path, "src/zephyr/d/logs/build/keep/x.py")
    ext._plan_capacity_mirrors([p])
    assert ext._PLANNED_MIRROR["src/zephyr/d/logs/build/keep/x.py"].endswith(
        "logs_doc/build_doc/keep/x.yaml"
    )


def test_no_gitignore_means_no_renames(tmp_path):
    """缺 .gitignore（或读不到）→ 空规则集，桶名一律原样，绝不凭空加后缀。"""
    assert not (tmp_path / ".gitignore").exists()
    _seed_flat(tmp_path, "_domain_d", ext._MIRROR_TRIGGER)
    targets = [_mk_src(tmp_path, "src/zephyr/d/logs/wal.py"), _mk_src(tmp_path, "src/zephyr/d/access/wal.py")]
    ext._plan_capacity_mirrors(targets)
    vals = sorted(ext._PLANNED_MIRROR.values())
    assert vals == [
        "docs/03_modules/_domain_d/algo_flow/access/wal.yaml",
        "docs/03_modules/_domain_d/algo_flow/logs/wal.yaml",
    ]


def test_bucket_rename_is_deterministic_across_runs(tmp_path):
    """撞名改道可复算：连跑两遍同名（新件重跑不得改道、既有 yaml 走复用不重复落盘）。"""
    (tmp_path / ".gitignore").write_text("logs/\n", encoding="utf-8")
    _seed_flat(tmp_path, "_domain_d", ext._MIRROR_TRIGGER)
    p = _mk_src(tmp_path, "src/zephyr/d/logs/wal.py")
    ext._plan_capacity_mirrors([p])
    first = ext.externalize(p, dry_run=False)
    ext._plan_capacity_mirrors([p])
    second = ext.externalize(p, dry_run=False)
    assert first["yaml"] == second["yaml"] == "docs/03_modules/_domain_d/algo_flow/logs_doc/wal.yaml"
    assert first["status"] == "externalized"
    assert second["status"] in {"externalized", "already", "skipped"}
    assert len(list((tmp_path / "docs/03_modules/_domain_d/algo_flow/logs_doc").glob("*.yaml"))) == 1


# --- P2-1 尾池三态分家（截断型块 / 零边 / 五段式散文 / 根层件落点）----------------


_TRUNC_BODY = (
    "trunc —— 截断型块夹具（块体无收口标记，P2-1 尾池 17 件实测形态）。\n"
    "\n"
    "# [ALGO_FLOW]\n"
    "# 层: 输入\n"
    "# - id: I1\n"
    "#   name: 入参\n"
    "# 层: 算法\n"
    "# - id: A1\n"
    "#   name_zh: ① 主流程\n"
)
_EDGE_TAIL = "#\n# 边:\n# I1 --> A1\n"


def _mk_trunc(root: Path, rel: str, *, with_edge: bool) -> tuple[Path, str]:
    """写未闭合块夹具，返回 (路径, docstring 值文本)（值文本即迁移前的解析输入）。"""
    body = _TRUNC_BODY + (_EDGE_TAIL if with_edge else "")
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f'"""{body}"""\n\nX = 1\n', encoding="utf-8")
    return p, body


def _graph(text: str) -> tuple[list, list]:
    g = coae.parse_algo_flow(text)
    assert g is not None
    return [(n.id, n.layer) for n in g.nodes], [(e.src, e.dst, e.is_break) for e in g.edges]


def test_truncated_block_with_edges_is_externalized(tmp_path):
    """截断型块 + 有边 → 出仓：镜像补 # [/ALGO_FLOW]，源码只留锚行，图逐字等价。

    补标记可证语义零改动（parse_algo_flow 节点段"见收标记即止、否则扫到文本尾"，
    边段一律扫到文本尾），所以截断块不必先人工补口再出仓。
    """
    p, body = _mk_trunc(tmp_path, "src/zephyr/d/trunc.py", with_edge=True)
    nodes_b, edges_b = _graph(body)
    assert edges_b == [("I1", "A1", False)]
    r = ext.externalize(p, dry_run=False)
    assert r["status"] == "externalized", r
    machine = ext._yaml_machine_block(tmp_path / r["yaml"])
    assert machine.rstrip().endswith("# [/ALGO_FLOW]"), machine
    assert _graph(machine) == (nodes_b, edges_b)  # 镜像即新真源，节点/边逐项一致
    src = p.read_text(encoding="utf-8")
    assert src.count("# [ALGO_FLOW]") == 1 and f"# [ALGO_FLOW] external: {r['yaml']}" in src
    assert "- id: I1" not in src and "-->" not in src  # 块体与边段都收进镜像
    final = coae.extract_algorithm_from_code(p, module_id="", truncate=False)
    assert [(n.id, n.layer) for n in final.algo_flow.nodes] == nodes_b
    assert [(e.src, e.dst, e.is_break) for e in final.algo_flow.edges] == edges_b


def test_truncated_block_without_edges_is_refused(tmp_path):
    """截断型块 + 零边 → 拒不出仓（validate_graph 对无边图报"无边定义"，镜像必被门禁拦）。"""
    p, body = _mk_trunc(tmp_path, "src/zephyr/d/trunc_noedge.py", with_edge=False)
    nodes_b, edges_b = _graph(body)
    assert nodes_b and edges_b == []
    before = p.read_bytes()
    r = ext.externalize(p, dry_run=False)
    assert r["status"] == "skipped", r
    assert "no edges" in r["reason"], r
    assert p.read_bytes() == before  # 源码零改动
    assert not (tmp_path / "docs").exists()  # 零写入


def test_legacy_five_section_block_reports_its_own_reason(tmp_path):
    """零节点两族分家（一）：五段式散文块报 legacy 五段式，不再与"不可解析"混一档。"""
    p = tmp_path / "src/zephyr/d/legacy5.py"
    p.parent.mkdir(parents=True)
    p.write_text(
        '"""Legacy5 — 五段式散文夹具（旧版语法，无 - id: 行）。\n\n'
        "# [ALGO_FLOW]\n"
        "# 输入: 因子 IC 序列\n"
        "# 算法: 逐窗 deflated Sharpe 判合格\n"
        "# 输出: 状态标签\n"
        "# [/ALGO_FLOW]\n"
        '"""\n\nX = 1\n',
        encoding="utf-8",
    )
    r = ext.externalize(p, dry_run=False)
    assert r["status"] == "skipped", r
    assert r["reason"] == ext._LEGACY_PROSE_SKIP_REASON, r
    assert not (tmp_path / "docs").exists()


def test_shorthand_zero_node_block_keeps_generic_reason(tmp_path):
    """零节点两族分家（二）：``# I1: 速记`` 型（无五段式口径行）仍报原口径。"""
    p = tmp_path / "src/zephyr/d/shorthand.py"
    p.parent.mkdir(parents=True)
    p.write_text(
        '"""Shorthand — 速记夹具。\n\n'
        "# [ALGO_FLOW]\n# I1: 入参速记\n# F1: 主流程速记\n# [/ALGO_FLOW]\n"
        '"""\n\nX = 1\n',
        encoding="utf-8",
    )
    r = ext.externalize(p, dry_run=False)
    assert r["status"] == "skipped", r
    assert r["reason"] == ext._NO_NODES_SKIP_REASON, r


def test_root_level_module_mirrors_into_shared_domain(tmp_path):
    """根层件 src/zephyr/<mod>.py：域落既有 _domain_shared，镜像名 root_<stem>.yaml。

    旧口径把末段文件名当包名，造出 ``_domain___init__`` 这类不存在的域目录（盘上从未
    落盘=静默丢图）；``source_of_truth:`` 头仍指真实源路径，provenance 机械可逆。
    """
    assert ext._domain_of("src/zephyr/demo_root.py") == "_domain_shared"
    assert ext._domain_of("src/zephyr/__init__.py") == "_domain_shared"
    assert ext._yaml_rel_for(
        tmp_path / "src/zephyr/demo_root.py", "src/zephyr/demo_root.py", "_domain_shared"
    ) == "docs/03_modules/_domain_shared/algo_flow/root_demo_root.yaml"
    assert ext._yaml_rel_for(
        tmp_path / "src/zephyr/__init__.py", "src/zephyr/__init__.py", "_domain_shared"
    ) == "docs/03_modules/_domain_shared/algo_flow/root___init__.yaml"

    p = _mk_src(tmp_path, "src/zephyr/demo_root.py")
    r = ext.externalize(p, dry_run=False)
    assert r["status"] == "externalized", r
    assert r["yaml"] == "docs/03_modules/_domain_shared/algo_flow/root_demo_root.yaml"
    ytxt = (tmp_path / r["yaml"]).read_text(encoding="utf-8")
    assert "source_of_truth: src/zephyr/demo_root.py" in ytxt
    assert "module: src.zephyr.demo_root" in ytxt
    assert "root_demo_root" in ytxt.splitlines()[0]  # 头注与镜像名同源
    assert f"# [ALGO_FLOW] external: {r['yaml']}" in p.read_text(encoding="utf-8")
