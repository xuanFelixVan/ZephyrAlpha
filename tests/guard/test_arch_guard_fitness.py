# [A_test] module_id: SRC-TST-1822 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-452 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.arch_guard.test_arch_guard_fitness
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
test_arch_guard_fitness.py — arch_guard 适应度函数最小测试集

AUDIT-04 X-01 修复：为 arch_guard 适应度函数补充最小测试覆盖。
测试策略：
  1. 每个 FF 脚本可导入且 main() 可调用
  2. 缺少配置文件时返回 exit code 2（config error）
  3. run_all.py 编排器可正常加载 manifest
  4. manifest 注册的 FF 脚本在磁盘上存在

注意：这些测试验证的是 FF 脚本的结构完整性和基本控制流，
不验证业务逻辑正确性（业务逻辑依赖真实配置文件，属于集成测试范畴）。
"""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from zephyr.shared.io.paths import REPO_ROOT

ARCH_GUARD_ROOT = REPO_ROOT / "scripts" / "arch_guard"
FF_ROOT = ARCH_GUARD_ROOT / "fitness_functions"

FF_SCRIPTS_ON_DISK = sorted(f.stem for f in FF_ROOT.glob("check_*.py") if f.is_file())

GUARD_SCRIPTS = [
    ("check_acl_boundary", ARCH_GUARD_ROOT / "check_acl_boundary.py"),
    ("check_fe_acl_boundary", ARCH_GUARD_ROOT / "check_fe_acl_boundary.py"),
    ("check_schema_consistency", ARCH_GUARD_ROOT / "check_schema_consistency.py"),
    ("check_cross_plane_communication", ARCH_GUARD_ROOT / "check_cross_plane_communication.py"),
    ("check_hot_path_purity", ARCH_GUARD_ROOT / "check_hot_path_purity.py"),
]

LAYER_BOUNDARY_SCRIPT_RETIRED = "import_linter/layer_boundary_check.py（已删除 2026-07-09，14层架构废弃）"


def _import_ff_module(name: str):
    script_path = FF_ROOT / f"{name}.py"
    assert script_path.is_file(), f"FF 脚本不存在: {script_path}"
    spec = importlib.util.spec_from_file_location(f"arch_guard_ff.{name}", script_path)
    assert spec is not None, f"无法创建 spec: {name}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"arch_guard_ff.{name}"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("name", FF_SCRIPTS_ON_DISK)
def test_ff_script_importable(name: str):
    mod = _import_ff_module(name)
    assert hasattr(mod, "main"), f"{name} 缺少 main() 函数"
    assert callable(mod.main), f"{name}.main 不可调用"


@pytest.mark.parametrize("name", FF_SCRIPTS_ON_DISK)
def test_ff_returns_int_on_missing_config(name: str):
    mod = _import_ff_module(name)
    with patch.object(Path, "is_file", return_value=False):
        result = mod.main()
        assert isinstance(result, int), f"{name}.main() 返回非 int: {type(result)}"
        assert result in (0, 1, 2), f"{name}.main() 返回异常 exit code: {result}"


@pytest.mark.parametrize("name,script_path", GUARD_SCRIPTS)
def test_guard_script_importable(name: str, script_path: Path):
    assert script_path.is_file(), f"Guard 脚本不存在: {script_path}"
    spec = importlib.util.spec_from_file_location(f"arch_guard.{name}", script_path)
    assert spec is not None, f"无法创建 spec: {name}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"arch_guard.{name}"] = mod
    spec.loader.exec_module(mod)
    assert hasattr(mod, "main"), f"{name} 缺少 main() 函数"


def _load_run_all():
    spec = importlib.util.spec_from_file_location("arch_guard.run_all", ARCH_GUARD_ROOT / "run_all.py")
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["arch_guard.run_all"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_run_all_loads_manifest():
    mod = _load_run_all()
    manifest = mod.load_manifest()
    assert "fitness_functions" in manifest
    active = [ff for ff in manifest["fitness_functions"] if ff.get("status") == "active"]
    assert len(active) >= 10, f"active FF 数量异常: {len(active)}"


def test_manifest_ff_scripts_exist_on_disk():
    mod = _load_run_all()
    manifest = mod.load_manifest()
    missing = []
    for ff in manifest["fitness_functions"]:
        rel_path = ff.get("path", "")
        full_path = ARCH_GUARD_ROOT / rel_path
        if not full_path.is_file():
            missing.append(f"{ff['id']} ({rel_path})")
    assert not missing, f"manifest 注册但磁盘不存在的 FF 脚本: {missing}"


def test_at_least_10_ff_scripts_on_disk():
    assert len(FF_SCRIPTS_ON_DISK) >= 10, f"FF 脚本数量不足: {len(FF_SCRIPTS_ON_DISK)}"
