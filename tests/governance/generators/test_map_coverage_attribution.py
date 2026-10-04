# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §join_checker
# [MODULE] tests.governance.generators.test_map_coverage_attribution
# [DOMAIN] D_GOV_SCRIPTS
# [MODIFY-GUARD] none（测试只读生成器，tmp_path 隔离，零生产写）
# [DEPENDENCIES] pytest; yaml; scripts.governance.d5_architecture.generators.generate_map_coverage_attribution
# [CONSUMERS] join checker 质量守卫（红蓝三攻击：伪造孤儿/悬空键/闭包环——坏归属必须被点名）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 全部宇宙构造于 tmp_path 副本（monkeypatch 根路径与连接，禁碰生产 PG/生产图）；
#   悬空键必须进 dangling_keys 段（禁静默丢弃）；闭包环必须终止（禁死循环）；
#   PG 生产连接函数被 monkeypatch 为必炸桩——测试全程零生产 PG 触碰
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""join checker（generate_map_coverage_attribution）红蓝对抗测试——裁定#481 分母执行件的能红证明。

三攻击样例（总包令钦定）+ 六条核心不变量：
a) 伪造孤儿：tmp 副宇宙放无挂载零引用文件 → 必须判 orphan（status+orphans 段双落）；
b) 悬空键：假图挂 MOD-DOES-NOT-EXIST → 必须进 dangling_keys，不崩不静默；
c) 闭包环：a↔b 互引且均无挂载 → 判孤儿且 BFS 终止（测试能跑完即证不死循环）。
不变量：空 __init__ 并入父包不计 / 非空 __init__ 独立计 / 直接挂载 status=direct /
闭包归属 status=derived（imports 挂载件者derived 到该图）/ 一文件多图 maps_direct 列全 /
tests/ 只入辅账不入主账 / PG 生产连接桩被触碰即炸（证明测试零生产依赖）。
"""

import sys
import textwrap
from pathlib import Path

import pytest
import yaml

_GEN_DIR = str(Path(__file__).resolve().parents[3] / "scripts" / "governance" / "d5_architecture" / "generators")
if _GEN_DIR not in sys.path:
    sys.path.insert(0, _GEN_DIR)

import generate_map_coverage_attribution as mca  # noqa: E402

# ---------- 副宇宙构造 ----------


def _write(p: Path, text: str = "") -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(text), encoding="utf-8")
    return p


@pytest.fixture()
def fake_universe(tmp_path: Path, monkeypatch):
    """tmp 副宇宙：8 主账单元 + 1 辅账测试件；生产 PG 连接桩=必炸。"""
    src = tmp_path / "src" / "zephyr"
    _write(src / "__init__.py", "")  # 空壳 __init__（并入父包，不计）
    _write(
        src / "pkg_a" / "__init__.py",
        '"""package doc."""\n',  # 仅 docstring = 空壳语义? 设计口径=仅空壳并入；docstring 属空壳
    )
    mounted = _write(
        src / "pkg_a" / "mounted.py",
        '"""mounted unit."""\n# [CONSUMERS] test-only\nVALUE = 1\n',
    )
    _write(src / "pkg_b" / "__init__.py", "X = 1\n")  # 非空 __init__ → 独立计
    _write(
        src / "pkg_b" / "uses_mounted.py",
        "from zephyr.pkg_a.mounted import VALUE\nOUT = VALUE\n",
    )
    orphan = _write(src / "pkg_c" / "orphan.py", "FLAG = 0\n")
    _write(src / "pkg_d" / "cyc_a.py", "from zephyr.pkg_d.cyc_b import B\nA = 1\n")
    _write(src / "pkg_d" / "cyc_b.py", "from zephyr.pkg_d.cyc_a import A\nB = 2\n")
    tool = _write(tmp_path / "scripts" / "tool.py", "print('tool')\n")
    _write(tmp_path / "tests" / "test_x.py", "def test_x():\n    assert True\n")

    # 生产 PG 连接桩：被触碰即 AssertionError（证明测试零生产依赖）
    import zephyr.governance.depgraph_schema as ds

    monkeypatch.setattr(
        mca, "get_depgraph_pg_connection", lambda: (_ for _ in ()).throw(AssertionError("production PG touched"))
    )
    monkeypatch.setattr(
        ds, "get_depgraph_pg_connection", lambda: (_ for _ in ()).throw(AssertionError("production PG touched"))
    )

    return {
        "root": tmp_path,
        "mounted": mounted,
        "orphan": orphan,
        "tool": tool,
        "units_expected": 7,  # mounted/uses_mounted/orphan/cyc_a/cyc_b/pkg_b__init__/scripts tool
    }


def _depgraph_view() -> mca.DepgraphView:
    return mca.DepgraphView(
        mod_to_paths={"MOD-REAL-01": ["src/zephyr/pkg_a/mounted.py"]},
        # 边语义=(from imports to)：uses_mounted imports mounted → mounted 的 dependents 含 uses_mounted
        edges=[("src/zephyr/pkg_b/uses_mounted.py", "src/zephyr/pkg_a/mounted.py")],
    )


def _map_file(tmp_path: Path, name: str, payload) -> Path:
    p = tmp_path / "maps" / f"{name}.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    return p


def _maps_dir(tmp_path: Path, **extra_nodes) -> dict:
    """六图假源：GOMAP 挂 mounted（dotted+path），TDM 挂 mounted（module_ref=MOD），其余节点可注入。"""
    d = tmp_path / "maps"
    d.mkdir(exist_ok=True)
    files = {
        "GOMAP": _map_file(
            tmp_path,
            "governance_operations_map",
            {
                "families": {"L1": [{"module": "zephyr.pkg_a.mounted", "path": "src/zephyr/pkg_a/mounted.py"}]},
                "pipeline": {"layers": [{"mounts": ["zephyr.pkg_a.mounted"]}]},
            },
        ),
        "TDM": _map_file(
            tmp_path,
            "trading_decision_map",
            {"nodes": ([{"node_id": "TDM-1", "module_ref": "MOD-REAL-01"}] + extra_nodes.get("TDM", []))},
        ),
        "FACTORY": _map_file(
            tmp_path,
            "strategy_production_map",
            {"nodes": [{"node_id": "FAC-1", "module_ref": "MOD-REAL-01"}]},  # 盘面实证：图9 MOD-* 值在 module_ref,
        ),
        "FIG11": _map_file(tmp_path, "dev_delivery_map", {"nodes": extra_nodes.get("FIG11", [])}),
        "FIG12": _map_file(tmp_path, "data_supply_chain_map", {"nodes": extra_nodes.get("FIG12", [])}),
        "FIG13": _map_file(tmp_path, "trading_day_cycle_map", {"nodes": extra_nodes.get("FIG13", [])}),
    }
    return files


def _run(universe, maps, **kw):
    out_yaml = universe["root"] / "out" / "30.yaml"
    out_md = universe["root"] / "out" / "31.md"
    result = mca.run_attribution(
        repo_root=universe["root"],
        map_files=maps,
        depgraph_override=_depgraph_view(),
        script_manifest=None,
        frontend_map=None,
        output_yaml=out_yaml,
        output_md=out_md,
        git_last_commit=lambda root, rel: "2026-01-01",
        **kw,
    )
    assert out_yaml.exists() and out_md.exists()
    return result


# ---------- a) 伪造孤儿 ----------


def test_fake_orphan_must_be_judged(fake_universe):
    """无挂载零引用文件必须判 orphan：status+orphans 段双落，不得静默。"""
    res = _run(fake_universe, _maps_dir(fake_universe["root"]))
    units = {u["file"]: u for u in res["units"]}
    ou = units["src/zephyr/pkg_c/orphan.py"]
    assert ou["status"] == "orphan"
    assert ou["maps_direct"] == [] and ou["maps_derived"] == []
    orphan_files = {o["file"] for o in res["orphans"]}
    assert "src/zephyr/pkg_c/orphan.py" in orphan_files
    orow = next(o for o in res["orphans"] if o["file"] == "src/zephyr/pkg_c/orphan.py")
    assert orow["tier"] == "suspect_orphan"
    assert orow["evidence"]["last_commit"] == "2026-01-01"


# ---------- b) 悬空键 ----------


def test_dangling_key_reported_not_silent(fake_universe):
    """挂 MOD-DOES-NOT-EXIST → 进 dangling_keys；不崩；其余归属不受牵连。"""
    maps = _maps_dir(fake_universe["root"], TDM=[{"node_id": "TDM-9", "module_ref": "MOD-DOES-NOT-EXIST"}])
    res = _run(fake_universe, maps)
    dangling = [d["key"] for d in res["dangling_keys"]]
    assert "MOD-DOES-NOT-EXIST" in dangling
    assert all(d["source_map"] == "TDM" for d in res["dangling_keys"] if d["key"] == "MOD-DOES-NOT-EXIST")
    # 归属不受牵连：真挂载件照常 direct
    units = {u["file"]: u for u in res["units"]}
    assert units["src/zephyr/pkg_a/mounted.py"]["status"] == "direct"


# ---------- c) 闭包环 ----------


def test_closure_cycle_terminates_and_reports_orphans(fake_universe):
    """a↔b 互引且无挂载 → 双孤儿；测试能跑完 = BFS 终止。"""
    res = _run(fake_universe, _maps_dir(fake_universe["root"]))
    units = {u["file"]: u for u in res["units"]}
    assert units["src/zephyr/pkg_d/cyc_a.py"]["status"] == "orphan"
    assert units["src/zephyr/pkg_d/cyc_b.py"]["status"] == "orphan"


# ---------- 核心不变量 ----------


def test_empty_init_merged_and_nonempty_init_counted(fake_universe):
    """空壳 __init__ 并入父包不计；非空 __init__ 独立计。"""
    res = _run(fake_universe, _maps_dir(fake_universe["root"]))
    files = {u["file"] for u in res["units"]}
    assert "src/zephyr/__init__.py" not in files  # 空壳并入
    assert "src/zephyr/pkg_a/__init__.py" not in files  # 仅 docstring=空壳
    assert "src/zephyr/pkg_b/__init__.py" in files  # 非空独立计
    assert res["accounting_units_total"] == fake_universe["units_expected"]


def test_direct_and_closure_attribution_and_multimap(fake_universe):
    """直接挂载=direct；imports 挂载件=derived 到该图；一文件多图 maps_direct 列全。"""
    maps = _maps_dir(fake_universe["root"])
    # FIG11 双键再挂 mounted（module_id 走 PG 反查 + module_ref 路径直挂）→ 多图
    maps["FIG11"] = _map_file(
        fake_universe["root"],
        "dev_delivery_map",
        {
            "nodes": [
                {
                    "node_id": "D11-1",
                    "module_id": "MOD-REAL-01",
                    "module_ref": "src/zephyr/pkg_a/mounted.py",
                    "source_anchors": ["src/zephyr/pkg_a/mounted.py:1"],
                }
            ]
        },
    )
    res = _run(fake_universe, maps)
    units = {u["file"]: u for u in res["units"]}
    mu = units["src/zephyr/pkg_a/mounted.py"]
    assert mu["status"] == "direct"
    assert set(mu["maps_direct"]) == {"GOMAP", "TDM", "FACTORY", "FIG11"}
    du = units["src/zephyr/pkg_b/uses_mounted.py"]
    assert du["status"] == "derived"
    assert "GOMAP" in du["maps_derived"] and "TDM" in du["maps_derived"]
    assert res["closure_derived"] >= 1
    assert res["by_map"]["GOMAP"] == 1 and res["by_map"]["FIG11"] == 1


def test_auxiliary_ledger_isolated(fake_universe):
    """tests/ 只入辅账（记数），不进主账 units、不回流归属。"""
    res = _run(fake_universe, _maps_dir(fake_universe["root"]))
    files = {u["file"] for u in res["units"]}
    assert not any(f.startswith("tests/") for f in files)
    assert res["auxiliary_ledger"]["tests_py_count"] == 1


def test_pg_unreachable_fails_loud(fake_universe, monkeypatch):
    """生产路径 PG 不可达 → 显式报错退出，禁 fail-open。"""
    monkeypatch.setattr(  # 连接工厂（未被 override 时唯一取数路径）必炸
        mca,
        "get_depgraph_pg_connection",
        lambda: (_ for _ in ()).throw(RuntimeError("pg down")),
    )
    with pytest.raises(SystemExit):
        mca.run_attribution(
            repo_root=fake_universe["root"],
            map_files=_maps_dir(fake_universe["root"]),
            depgraph_override=None,  # 走生产路径 → 必炸
            script_manifest=None,
            frontend_map=None,
            output_yaml=fake_universe["root"] / "out2" / "30.yaml",
            output_md=fake_universe["root"] / "out2" / "31.md",
            git_last_commit=lambda root, rel: "2026-01-01",
        )


def test_production_pg_never_touched(fake_universe):
    """全套用例跑在 override 模式；本测试防回归：run_attribution 不传 override 必须 PG 取数。"""
    # 已由 fixture 必炸桩 + test_pg_unreachable_fails_loud 覆盖；此处锁 API 形状防漂移
    import inspect

    sig = inspect.signature(mca.run_attribution)
    assert "depgraph_override" in sig.parameters
    assert "repo_root" in sig.parameters
