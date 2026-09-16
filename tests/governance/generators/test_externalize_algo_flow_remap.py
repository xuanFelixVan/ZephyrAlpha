# [A_test] module_id: MOD-GOV_ALGO_EXTRACTOR | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_ALGO_EXTRACTOR | docs/03_modules/_cross_layer/gov_scripts/blueprint.md
# [MODULE] tests.governance.generators.test_externalize_algo_flow_remap
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_externalize_algo_flow_remap.py — 出仓器批级 stem 碰撞预判单元测试。

背景（P2-1 orchestrator 批实证）：_yaml_rel_for 靠"盘上 yaml 已存在"改道
parent__stem，同批内后处理文件的改道依赖 rglob 排序+落盘副作用——dry-run
预测路径与正式跑不一致（映射改道雷同族）。_plan_stem_collision_remaps 在
批开始前静态判定碰撞，子包件确定性改道，处理顺序无关。

纯路径运算单测：目标 Path 全部为 REPO_ROOT 下虚构路径（不触盘、不依赖仓库
真实出仓状态，本批落地后测试仍稳定）。
"""

from __future__ import annotations

import sys
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT

_GOV_DIR = str(REPO_ROOT / "scripts" / "governance")
_GEN_DIR = str(REPO_ROOT / "scripts" / "governance" / "d5_architecture" / "generators")
for _p in (_GOV_DIR, _GEN_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import externalize_algo_flow as ext  # noqa: E402


def _pkg(*parts: str) -> Path:
    """构造 src/zephyr/<...> 虚构目标 Path（纯路径，不要求存在）。"""
    return REPO_ROOT.joinpath("src", "zephyr", *parts)


def teardown_function() -> None:
    ext._PLANNED_REMAP.clear()


def test_no_collision_no_remap() -> None:
    targets = [_pkg("alpha", "a.py"), _pkg("alpha", "sub", "b.py"), _pkg("alpha", "__init__.py")]
    ext._plan_stem_collision_remaps(targets)
    assert ext._PLANNED_REMAP == {}


def test_collision_subpackage_remapped_root_keeps_flat() -> None:
    """同 stem 两文件：域根件保平铺名，子包件改道 parent__stem（orchestrator task_queue 实证形态）。"""
    root_f = _pkg("orchestrator", "task_queue.py")
    sub_f = _pkg("orchestrator", "core", "task_queue.py")
    ext._plan_stem_collision_remaps([sub_f, root_f])
    assert ext._PLANNED_REMAP == {
        "src/zephyr/orchestrator/core/task_queue.py": (
            "docs/03_modules/_domain_orchestrator/algo_flow/core__task_queue.yaml"
        )
    }


def test_collision_resolution_order_independent() -> None:
    """改道判定与批内处理顺序无关（rglob 排序依赖消除的回归断言）。"""
    a = [_pkg("d", "x", "same.py"), _pkg("d", "same.py"), _pkg("d", "y", "same.py")]
    b = list(reversed(a))
    ext._plan_stem_collision_remaps(a)
    remap_a = dict(ext._PLANNED_REMAP)
    ext._plan_stem_collision_remaps(b)
    remap_b = dict(ext._PLANNED_REMAP)
    assert remap_a == remap_b
    # 三个同 stem：域根 1 件平铺，两个子包件各得唯一 parent 前缀名
    assert len(remap_a) == 2
    assert remap_a["src/zephyr/d/x/same.yaml".replace("same.yaml", "same.py")].endswith("x__same.yaml")
    assert remap_a["src/zephyr/d/y/same.py"].endswith("y__same.yaml")
    assert "src/zephyr/d/same.py" not in remap_a


def test_init_files_never_remapped() -> None:
    """__init__.py 永不入碰撞表（parent__init__ 命名天然唯一）。"""
    targets = [_pkg("d", "__init__.py"), _pkg("d", "sub", "__init__.py")]
    ext._plan_stem_collision_remaps(targets)
    assert ext._PLANNED_REMAP == {}


def test_orchestrator_real_targets_plan_is_deterministic() -> None:
    """真实 orchestrator 域清单（只读 glob）：唯一碰撞对=core/task_queue.py，其余平铺。"""
    root = REPO_ROOT / "src" / "zephyr" / "orchestrator"
    targets = sorted(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)
    ext._plan_stem_collision_remaps(targets)
    assert set(ext._PLANNED_REMAP) == {"src/zephyr/orchestrator/core/task_queue.py"}
    yaml_rel = ext._PLANNED_REMAP["src/zephyr/orchestrator/core/task_queue.py"]
    assert yaml_rel.endswith("core__task_queue.yaml")
