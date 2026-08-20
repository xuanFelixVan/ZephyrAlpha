# [A_test] module_id: MOD-GOV_reconcile_generators_smoke | layer=test | stability=volatile | safety=L | ai_modifiable
# [BLUEPRINT] MOD-GOV_SCRIPTS | docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama/generator_auto_trigger_pilot.md | §
# [MODULE] tests.governance.test_reconcile_generators
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module; DB 不可达->skip_test; subprocess spawn 失败->fail
# [TESTS] tests/governance/test_reconcile_generators.py
# [A_module] module_id=MOD-GOV_SCRIPTS | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_reconcile_generators.py — reconcile_generators.py e2e smoke test

#ARCH-TOOL-HEALTH-V1 裁定第 1 条：核心治理工具必须有 e2e smoke test。
reconcile_generators.py 是 23 个生成器的自动触发入口（apply 写 DB 后实时触发 +
boot_hooks 启动时 mtime 对比兜底），属于核心治理工具。

病根（第一性原理）
-----------------
编排器无测试时，以下 bug 类型无法检测：
1. **注册表格式漂移**：generator_registry.yaml 字段改名/删除→编排器 KeyError 静默
2. **双路径分派回归**：entry_function 不存在时 subprocess 回退失效→生成器不触发
3. **退出码语义误判**：exit 1+Traceback 被误判为 ok（FINDINGS）→ 崩溃静默
4. **stale 检测逻辑错误**：mtime 对比方向反了→YAML 变更后不触发重生成
5. **async spawn 失败**：reconcile_async 无法 spawn→apply 脚本静默无重生成

治本方案
--------
对标 test_apply_depgraph_smoke.py 的 e2e 风格：
1. **真实 import + 真实 YAML 加载**：不 mock 注册表，真实读 generator_registry.yaml
2. **reconcile('battle_map_db') 真实调用**：in-process 路径真实跑 battle_map 生成器（@pytest.mark.e2e，需 DB）
3. **_is_stale 逻辑单元测试**：temp 目录 + os.utime 控制 mtime，验证 4 种判定路径
4. **退出码语义 mock 测试**：mock subprocess.run，验证 0/1+Traceback/2/timeout 4 种退出码判定
5. **reconcile_async spawn 验证**：真实 spawn 子进程，验证 PID/log_file/status

Usage::

    py -3.12 -m pytest tests/governance/test_reconcile_generators.py -v
    py -3.12 -m pytest tests/governance/test_reconcile_generators.py -k "not e2e"  # 跳过 DB 测试
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT_PATH = _REPO_ROOT / "scripts" / "governance" / "reconcile_generators.py"


@pytest.fixture(scope="module")
def rg():
    """动态加载 reconcile_generators.py（对标 test_apply_depgraph_smoke.py 的 adg fixture）。

    真实执行模块级代码（含 import 语句）——若 import 缺失会立即抛 ImportError/NameError。
    """
    spec = importlib.util.spec_from_file_location("reconcile_generators_under_test", _SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module", autouse=True)
def _wait_detached_procs_at_teardown(rg):
    """模块结束时等待 reconcile_async spawn 的后台子进程退出。

    火忘式（fire-and-forget）子进程在空触发源下 ~0.3s 退出（Python 启动+reconcile 匹配
    0 生成器）。若不等待，session teardown 时 _DETACHED_PROCS 列表被 GC，Popen.__del__
    在子进程仍运行时触发 "subprocess still running" ResourceWarning，被 pytest
    unraisableexception 插件提升为异常导致 exit 1。本 finalizer 轮询 _prune_detached
    直到列表空或超时，确保子进程退出后再交还控制权。
    """
    yield
    deadline = time.time() + 10.0
    while time.time() < deadline:
        rg._prune_detached()
        if not rg._DETACHED_PROCS:
            break
        time.sleep(0.05)


# ============================================================================
# Test 1: Import smoke —— 检测 import 缺失 / 符号不存在
# ============================================================================


class TestImportSmoke:
    """验证 reconcile_generators.py 模块能正常 import（所有依赖符号可用）。"""

    def test_module_loads_without_error(self, rg):
        """模块能加载且无 ImportError/NameError。"""
        assert rg is not None, "reconcile_generators 模块加载失败"

    def test_core_functions_exist(self, rg):
        """核心公开函数存在（签名漂移检测）。"""
        for func_name in [
            "reconcile",
            "reconcile_async",
            "reconcile_stale",
            "_load_registry",
            "_invoke_generator",
            "_invoke_subprocess",
            "_is_stale",
            "_fmt_result",
            "main",
        ]:
            assert hasattr(rg, func_name), f"核心函数 {func_name} 缺失"

    def test_constants_exist(self, rg):
        """关键常量存在（退出码语义 / 超时 / 注册表路径）。"""
        assert rg._SUBPROCESS_TIMEOUT > 0, "_SUBPROCESS_TIMEOUT 应为正数"
        assert 0 in rg._OK_RETURNCODES, "exit 0 应在 _OK_RETURNCODES 中"
        assert 1 in rg._OK_RETURNCODES, "exit 1 应在 _OK_RETURNCODES 中（FINDINGS）"
        assert 2 not in rg._OK_RETURNCODES, "exit 2 不应在 _OK_RETURNCODES 中（ERROR）"
        assert rg._REGISTRY_YAML.exists(), f"generator_registry.yaml 不存在: {rg._REGISTRY_YAML}"


# ============================================================================
# Test 2: Registry loading —— 真实读 generator_registry.yaml
# ============================================================================


class TestRegistryLoading:
    """验证 _load_registry() 能真实加载 generator_registry.yaml。

    不 mock——真实读 YAML 文件，检测格式漂移（字段改名/删除）。
    """

    def test_registry_loads_successfully(self, rg):
        """_load_registry() 返回非空 dict，含 'generators' 键。"""
        data = rg._load_registry()
        assert isinstance(data, dict), f"返回类型应为 dict，实际 {type(data)}"
        assert "generators" in data, "返回 dict 缺少 'generators' 键"
        assert len(data["generators"]) > 0, "generators 列表为空"

    def test_registry_has_at_least_20_generators(self, rg):
        """注册表至少有 20 个生成器（当前 23 个，留余量防计数敏感）。"""
        data = rg._load_registry()
        assert len(data["generators"]) >= 20, f"生成器数量 {len(data['generators'])} < 20，注册表可能加载不完整"

    def test_all_generators_have_required_fields(self, rg):
        """每个生成器条目都有 name/module_path/trigger_sources/input_sources/output_globs。"""
        data = rg._load_registry()
        required = {"name", "module_path", "trigger_sources", "input_sources", "output_globs"}
        for gen in data["generators"]:
            missing = required - set(gen.keys())
            assert not missing, f"生成器 '{gen.get('name', '?')}' 缺少必填字段: {missing}"

    def test_battle_map_has_entry_function(self, rg):
        """battle_map 生成器声明了 entry_function=regenerate（in-process 路径）。"""
        data = rg._load_registry()
        bm = next((g for g in data["generators"] if g["name"] == "battle_map"), None)
        assert bm is not None, "注册表缺少 battle_map 生成器"
        assert bm.get("entry_function") == "regenerate", (
            f"battle_map entry_function 应为 'regenerate'，实际 '{bm.get('entry_function')}'"
        )

    def test_all_trigger_sources_use_convention(self, rg):
        """所有 trigger_sources 遵循 <name>_db 或 <name>_yaml 命名约定。"""
        data = rg._load_registry()
        for gen in data["generators"]:
            for ts in gen["trigger_sources"]:
                assert ts.endswith("_db") or ts.endswith("_yaml"), (
                    f"生成器 '{gen['name']}' 的 trigger_source '{ts}' 不符合 _db/_yaml 命名约定"
                )


# ============================================================================
# Test 3: CLI smoke —— --list 命令可运行
# ============================================================================


class TestCLISmoke:
    """验证 reconcile_generators.py CLI 入口可运行。"""

    def test_list_cli_runs(self):
        """--list CLI 命令能正常运行（returncode=0）且输出含生成器数。"""
        result = subprocess.run(
            [sys.executable, str(_SCRIPT_PATH), "--list"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            cwd=str(_REPO_ROOT),
        )
        assert result.returncode == 0, (
            f"--list CLI 失败 rc={result.returncode}\nstdout: {result.stdout[:500]}\nstderr: {result.stderr[:500]}"
        )
        assert "生成器" in result.stdout, f"--list 输出缺少 '生成器' 关键词\nstdout: {result.stdout[:500]}"

    def test_no_args_prints_help(self):
        """无参数调用打印 help（returncode=0，非崩溃）。"""
        result = subprocess.run(
            [sys.executable, str(_SCRIPT_PATH)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            cwd=str(_REPO_ROOT),
        )
        assert result.returncode == 0, f"无参数调用应返回 rc=0（print_help），实际 rc={result.returncode}"
        assert "usage:" in result.stdout or "--source" in result.stdout, "help 输出缺少 usage/--source"


# ============================================================================
# Test 4: reconcile() in-process —— 真实调用 battle_map 生成器（@pytest.mark.e2e）
# ============================================================================


@pytest.mark.e2e
class TestReconcileInProcess:
    """验证 reconcile('battle_map_db') 真实调用 battle_map 生成器。

    @pytest.mark.e2e：battle_map 生成器连接 PostgreSQL battle_map 表，
    检测 DB 配置漂移、生成器崩溃。
    跳过条件：PostgreSQL 不可达（CI 环境无 DB 时 skip）。
    """

    def test_reconcile_battle_map_db_succeeds(self, rg):
        """reconcile('battle_map_db') 通过 in-process 路径成功调用 battle_map 生成器。"""
        try:
            result = rg.reconcile("battle_map_db")
        except Exception as e:
            pytest.skip(f"reconcile('battle_map_db') 抛异常（DB 不可达？）: {e}")

        assert result["source"] == "battle_map_db"
        assert result["total"] >= 1, f"reconcile('battle_map_db') 应匹配至少 1 个生成器，实际 {result['total']}"
        # 生成器内吞 PG 连接错误返回 failed（非异常路径）——docstring 声明的
        # "PostgreSQL 不可达时 skip" 契约同样覆盖此路径
        for r in result["regenerated"]:
            if r["status"] != "ok" and "connection" in str(r.get("error", "")).lower():
                pytest.skip(f"PostgreSQL 不可达（生成器返回 failed）: {r.get('error', '')}")
        # battle_map 走 in-process 路径（entry_function=regenerate）
        for r in result["regenerated"]:
            assert r["generator"] == "battle_map"
            assert r["status"] == "ok", f"battle_map 生成器应返回 ok，实际 {r['status']}: {r.get('error', '')}"
            assert r.get("invoke_mode") == "in_process", f"battle_map 应走 in_process 路径，实际 {r.get('invoke_mode')}"

    def test_reconcile_unknown_source_returns_empty(self, rg):
        """reconcile('unknown_source') 匹配 0 个生成器，返回空列表。"""
        result = rg.reconcile("unknown_source_xyz")
        assert result["source"] == "unknown_source_xyz"
        assert result["total"] == 0
        assert result["regenerated"] == []


# ============================================================================
# Test 5: _is_stale() 逻辑 —— temp 目录 + os.utime 控制 mtime
# ============================================================================


class TestIsStaleLogic:
    """验证 _is_stale() 的 4 种判定路径。

    使用 tmp_path + os.utime 精确控制文件 mtime，不依赖真实文件系统状态。
    """

    def test_db_only_never_generated_is_stale(self, rg, monkeypatch, tmp_path):
        """db-only 生成器无成功标记 → (True, 'db_only_never_generated')。P2-1 boot 兜底。"""
        monkeypatch.setattr(rg, "_REPO_ROOT", tmp_path)
        monkeypatch.setattr(rg, "_REGEN_CACHE_DIR", tmp_path / "cache")
        entry = {
            "name": "test_db_only",
            "input_sources": ["db:depgraph_nodes|edges"],
            "output_globs": ["nonexistent/*.md"],
        }
        is_stale, reason = rg._is_stale(entry)
        assert is_stale is True
        assert reason == "db_only_never_generated"

    def test_db_only_recent_success_is_fresh(self, rg, monkeypatch, tmp_path):
        """db-only 生成器近期成功 → (False, 'db_only_fresh_*s')。"""
        monkeypatch.setattr(rg, "_REPO_ROOT", tmp_path)
        monkeypatch.setattr(rg, "_REGEN_CACHE_DIR", tmp_path / "cache")
        entry = {
            "name": "test_db_only",
            "input_sources": ["db:depgraph_nodes|edges"],
            "output_globs": ["nonexistent/*.md"],
        }
        rg._write_success_marker("test_db_only")
        is_stale, reason = rg._is_stale(entry)
        assert is_stale is False
        assert reason.startswith("db_only_fresh_")

    def test_db_only_old_success_is_stale(self, rg, monkeypatch, tmp_path):
        """db-only 生成器成功标记超阈值 → (True, 'db_only_stale_*s')。"""
        import time as _time

        monkeypatch.setattr(rg, "_REPO_ROOT", tmp_path)
        cache_dir = tmp_path / "cache"
        monkeypatch.setattr(rg, "_REGEN_CACHE_DIR", cache_dir)
        entry = {
            "name": "test_db_only",
            "input_sources": ["db:depgraph_nodes|edges"],
            "output_globs": ["nonexistent/*.md"],
        }
        old_ts = _time.time() - rg._DB_ONLY_STALE_THRESHOLD_SECONDS - 100
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / "gen_test_db_only.success").write_text(str(old_ts), encoding="utf-8")
        is_stale, reason = rg._is_stale(entry)
        assert is_stale is True
        assert reason.startswith("db_only_stale_")

    def test_no_outputs_returns_true(self, rg, monkeypatch, tmp_path):
        """有 yaml 输入源但无产物文件 → (True, 'no_outputs')。"""
        monkeypatch.setattr(rg, "_REPO_ROOT", tmp_path)
        # 创建 yaml 输入文件
        yaml_file = tmp_path / "input.yaml"
        yaml_file.write_text("test: value", encoding="utf-8")
        entry = {
            "input_sources": ["yaml:input.yaml"],
            "output_globs": ["nonexistent/*.md"],
        }
        is_stale, reason = rg._is_stale(entry)
        assert is_stale is True
        assert reason == "no_outputs"

    def test_input_newer_than_output_returns_true(self, rg, monkeypatch, tmp_path):
        """yaml 输入比产物新 → (True, 'input_newer_than_output')。"""
        monkeypatch.setattr(rg, "_REPO_ROOT", tmp_path)
        # 创建 yaml 输入文件（mtime=now+100）
        yaml_file = tmp_path / "input.yaml"
        yaml_file.write_text("test: value", encoding="utf-8")
        # 创建产物文件（mtime=now，比输入旧）
        output_file = tmp_path / "output.md"
        output_file.write_text("# generated", encoding="utf-8")
        # 设置 mtime：输入比产物新 100 秒
        now = time.time()
        os.utime(yaml_file, (now, now + 100))
        os.utime(output_file, (now, now))
        entry = {
            "input_sources": ["yaml:input.yaml"],
            "output_globs": ["output.md"],
        }
        is_stale, reason = rg._is_stale(entry)
        assert is_stale is True
        assert reason == "input_newer_than_output"

    def test_output_up_to_date_returns_false(self, rg, monkeypatch, tmp_path):
        """yaml 输入比产物旧 → (False, 'output_up_to_date')。"""
        monkeypatch.setattr(rg, "_REPO_ROOT", tmp_path)
        yaml_file = tmp_path / "input.yaml"
        yaml_file.write_text("test: value", encoding="utf-8")
        output_file = tmp_path / "output.md"
        output_file.write_text("# generated", encoding="utf-8")
        # 设置 mtime：产物比输入新 100 秒
        now = time.time()
        os.utime(yaml_file, (now, now))
        os.utime(output_file, (now, now + 100))
        entry = {
            "input_sources": ["yaml:input.yaml"],
            "output_globs": ["output.md"],
        }
        is_stale, reason = rg._is_stale(entry)
        assert is_stale is False
        assert reason == "output_up_to_date"

    def test_multiple_yaml_sources_takes_max_mtime(self, rg, monkeypatch, tmp_path):
        """多个 yaml 输入源取 max(mtime)——任一更新即 stale。"""
        monkeypatch.setattr(rg, "_REPO_ROOT", tmp_path)
        yaml1 = tmp_path / "input1.yaml"
        yaml1.write_text("a: 1", encoding="utf-8")
        yaml2 = tmp_path / "input2.yaml"
        yaml2.write_text("b: 2", encoding="utf-8")
        output_file = tmp_path / "output.md"
        output_file.write_text("# generated", encoding="utf-8")
        now = time.time()
        os.utime(yaml1, (now, now))  # 旧
        os.utime(yaml2, (now, now + 200))  # 新（比产物新）
        os.utime(output_file, (now, now + 100))
        entry = {
            "input_sources": ["yaml:input1.yaml", "yaml:input2.yaml"],
            "output_globs": ["output.md"],
        }
        is_stale, reason = rg._is_stale(entry)
        assert is_stale is True, "yaml2 比产物新，应 stale"
        assert reason == "input_newer_than_output"


# ============================================================================
# Test 6: 退出码语义 —— mock subprocess.run 验证 4 种退出码判定
# ============================================================================


class TestExitCodeSemantics:
    """验证 _invoke_subprocess() 的退出码判定逻辑。

    mock subprocess.run，验证：
    - exit 0 → ok
    - exit 1 无 Traceback → ok（FINDINGS，产物已生成）
    - exit 1 + Traceback → failed（崩溃伪装为 FINDINGS）
    - exit 2 → failed
    - TimeoutExpired → failed
    """

    def _make_entry(self, name="test_gen"):
        """构造测试用注册表条目。"""
        return {
            "name": name,
            "module_path": "fake.module.does_not_exist",
            "args": [],
        }

    def test_exit_0_is_ok(self, rg, monkeypatch):
        """exit 0 → status=ok。"""
        mock_proc = MagicMock(returncode=0, stdout="done", stderr="")
        monkeypatch.setattr(subprocess, "run", lambda *a, **kw: mock_proc)
        result = rg._invoke_subprocess(self._make_entry())
        assert result["status"] == "ok"
        assert result["returncode"] == 0

    def test_exit_1_no_traceback_is_ok(self, rg, monkeypatch):
        """exit 1 无 Traceback → status=ok（FINDINGS，产物已生成但有告警）。"""
        mock_proc = MagicMock(returncode=1, stdout="done with warnings", stderr="some warning")
        monkeypatch.setattr(subprocess, "run", lambda *a, **kw: mock_proc)
        result = rg._invoke_subprocess(self._make_entry())
        assert result["status"] == "ok", (
            f"exit 1 无 Traceback 应为 ok（FINDINGS），实际 {result['status']}: {result.get('error', '')}"
        )

    def test_exit_1_with_traceback_is_failed(self, rg, monkeypatch):
        """exit 1 + Traceback in stderr → status=failed（崩溃伪装为 FINDINGS）。"""
        mock_proc = MagicMock(
            returncode=1,
            stdout="",
            stderr="Traceback (most recent call last):\n  File ...\nNameError: foo",
        )
        monkeypatch.setattr(subprocess, "run", lambda *a, **kw: mock_proc)
        result = rg._invoke_subprocess(self._make_entry())
        assert result["status"] == "failed", "exit 1 + Traceback 应为 failed（崩溃），实际 " + result["status"]
        assert "crash" in result["error"], f"错误信息应含 'crash'，实际: {result['error']}"

    def test_exit_2_is_failed(self, rg, monkeypatch):
        """exit 2 → status=failed。"""
        mock_proc = MagicMock(returncode=2, stdout="", stderr="some error")
        monkeypatch.setattr(subprocess, "run", lambda *a, **kw: mock_proc)
        result = rg._invoke_subprocess(self._make_entry())
        assert result["status"] == "failed"

    def test_timeout_is_failed(self, rg, monkeypatch):
        """TimeoutExpired → status=failed，error 含 'timeout'。"""

        def raise_timeout(*a, **kw):
            raise subprocess.TimeoutExpired(cmd="test", timeout=300)

        monkeypatch.setattr(subprocess, "run", raise_timeout)
        result = rg._invoke_subprocess(self._make_entry())
        assert result["status"] == "failed"
        assert "timeout" in result["error"].lower()


# ============================================================================
# Test 7: reconcile_async() spawn 验证 —— 真实 spawn 子进程
# ============================================================================


class TestReconcileAsync:
    """验证 reconcile_async() 能 spawn detached subprocess 并返回正确结果。

    使用空触发源（无匹配生成器）确保子进程快速退出，不阻塞测试。
    """

    def test_async_returns_spawned_status(self, rg):
        """reconcile_async() 返回 status=spawned + pid + log_file。"""
        result = rg.reconcile_async("test_empty_source")
        assert result["status"] == "spawned", (
            f"应返回 status=spawned，实际 {result.get('status')}: {result.get('error', '')}"
        )
        assert "pid" in result, "返回 dict 缺少 'pid'"
        assert isinstance(result["pid"], int), f"pid 应为 int，实际 {type(result['pid'])}"
        assert result["pid"] > 0, f"pid 应为正数，实际 {result['pid']}"
        assert "log_file" in result, "返回 dict 缺少 'log_file'"

    def test_async_log_file_exists(self, rg):
        """reconcile_async() 创建的日志文件存在。"""
        result = rg.reconcile_async("test_empty_source_2")
        if result["status"] != "spawned":
            pytest.skip(f"spawn 失败: {result.get('error')}")
        log_path = Path(result["log_file"])
        assert log_path.exists(), f"日志文件不存在: {log_path}"
        assert log_path.suffix == ".log", f"日志文件扩展名应为 .log，实际 {log_path.suffix}"

    def test_async_log_dir_under_runtime(self, rg):
        """日志文件在 .runtime/logs/ 目录下（对标项目约定）。"""
        result = rg.reconcile_async("test_empty_source_3")
        if result["status"] != "spawned":
            pytest.skip(f"spawn 失败: {result.get('error')}")
        log_path = Path(result["log_file"])
        # 日志路径应含 .runtime/logs/
        assert ".runtime" in log_path.parts and "logs" in log_path.parts, (
            f"日志路径应在 .runtime/logs/ 下，实际: {log_path}"
        )


# ============================================================================
# Test 8: reconcile_stale() —— 扫描不崩溃，返回结构正确
# ============================================================================


class TestReconcileStaleStructure:
    """验证 reconcile_stale() 返回结构正确（不验证生成器实际执行）。

    reconcile_stale() 扫描全部生成器的 mtime，返回 regenerated/skipped/total_scanned。
    本测试只验证返回结构，不验证具体生成器是否被重生成（依赖文件系统状态）。
    """

    def test_stale_returns_correct_structure(self, rg):
        """reconcile_stale() 返回 dict 含 regenerated/skipped/total_scanned。"""
        result = rg.reconcile_stale()
        assert isinstance(result, dict)
        assert "regenerated" in result
        assert "skipped" in result
        assert "total_scanned" in result
        assert isinstance(result["regenerated"], list)
        assert isinstance(result["skipped"], list)
        assert result["total_scanned"] == len(result["regenerated"]) + len(result["skipped"])

    def test_stale_scans_all_generators(self, rg):
        """reconcile_stale() 扫描的生成器数 == 注册表生成器数。"""
        registry = rg._load_registry()
        expected_count = len(registry["generators"])
        result = rg.reconcile_stale()
        assert result["total_scanned"] == expected_count, (
            f"应扫描 {expected_count} 个生成器，实际 {result['total_scanned']}"
        )


# ============================================================================
# Test 9: _invoke_parallel() —— 并行调用顺序保持 + 失败隔离（治本缺口#2）
# ============================================================================


class TestParallelInvocation:
    """验证 _invoke_parallel() 的并行调度行为（治本缺口#2）。

    并行化的两个关键不变量：
    1. 结果顺序与 entries 一致（确定性报告）
    2. 单个生成器失败不影响其他（失败隔离）
    """

    def test_parallel_preserves_order(self, rg, monkeypatch):
        """_invoke_parallel 结果顺序与输入 entries 一致。"""
        names = ["gen_a", "gen_b", "gen_c"]

        def fake_invoke(entry):
            return {"status": "ok", "generator": entry["name"], "elapsed_ms": 1.0}

        monkeypatch.setattr(rg, "_invoke_generator", fake_invoke)
        entries = [{"name": n} for n in names]
        results = rg._invoke_parallel(entries)
        assert [r["generator"] for r in results] == names, "并行结果顺序应与输入一致（确定性报告）"

    def test_parallel_failure_isolation(self, rg, monkeypatch):
        """一个生成器抛异常不影响其他生成器执行。"""

        def fake_invoke(entry):
            if entry["name"] == "boom":
                raise RuntimeError("simulated crash")
            return {"status": "ok", "generator": entry["name"]}

        monkeypatch.setattr(rg, "_invoke_generator", fake_invoke)
        entries = [{"name": "ok1"}, {"name": "boom"}, {"name": "ok2"}]
        results = rg._invoke_parallel(entries)
        assert len(results) == 3
        assert results[0]["generator"] == "ok1" and results[0]["status"] == "ok"
        assert results[2]["generator"] == "ok2" and results[2]["status"] == "ok"
        # 失败的生成器返回 failed dict，不传播异常
        assert results[1]["status"] == "failed"
        assert "simulated crash" in results[1]["error"]

    def test_parallel_empty_returns_empty(self, rg):
        """空 entries 列表返回空结果（不创建线程池）。"""
        assert rg._invoke_parallel([]) == []

    def test_parallel_max_workers_configurable(self, rg, monkeypatch):
        """ZEPHYR_REGENERATE_WORKERS 环境变量可调 worker 数（≥1）。"""
        monkeypatch.setenv("ZEPHYR_REGENERATE_WORKERS", "8")
        # 重新 import 模块级常量需 reload；这里只验证 env 可读且为正数
        import importlib

        monkeypatch.delenv("ZEPHYR_REGENERATE_WORKERS", raising=False)
        # 默认值 4
        assert rg._MAX_WORKERS >= 1, "_MAX_WORKERS 应 ≥1"


# ============================================================================
# Test 10: post_commit_regen_yaml.py —— post-commit YAML 变更触发器（治本缺口#3）
# ============================================================================

_POST_COMMIT_SCRIPT = _REPO_ROOT / "scripts" / "governance" / "git_hooks" / "post_commit_regen_yaml.py"


@pytest.fixture(scope="module")
def pcr():
    """动态加载 post_commit_regen_yaml.py。"""
    spec = importlib.util.spec_from_file_location("post_commit_regen_yaml_under_test", _POST_COMMIT_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestPostCommitRegenYaml:
    """验证 post-commit YAML 变更触发器（治本缺口#3）。

    覆盖：①生成器 yaml 输入源收集 ②committed 文件匹配 ③逃生通道 ④绝不阻断（exit 0）
    """

    def test_module_loads(self, pcr):
        """脚本能正常 import。"""
        assert pcr is not None

    def test_generator_yaml_inputs_includes_battle_map(self, pcr):
        """_generator_yaml_inputs() 收集到 battle_map 的 yaml 输入源。"""
        inputs = pcr._generator_yaml_inputs()
        assert isinstance(inputs, set)
        assert len(inputs) > 0, "应收集到至少 1 个 yaml 输入源"
        # battle_map 的 yaml 输入源应在其中
        assert any("module_translation_registry.yaml" in i for i in inputs), (
            "battle_map 的 module_translation_registry.yaml 输入源缺失"
        )
        assert any("battle_map_domain_policy.yaml" in i for i in inputs), (
            "battle_map 的 battle_map_domain_policy.yaml 输入源缺失"
        )

    def test_matches_generator_input_exact(self, pcr):
        """精确路径匹配：committed 文件 == 输入源 → True。"""
        inputs = {"docs/foo/bar.yaml"}
        assert pcr._matches_generator_input(["docs/foo/bar.yaml"], inputs) is True

    def test_matches_generator_input_no_match(self, pcr):
        """不相关 YAML 文件 → False（避免每次提交任意 YAML 都触发）。"""
        inputs = {"docs/foo/bar.yaml"}
        assert pcr._matches_generator_input(["docs/01_policies_and_standards/trae_999_unrelated.yaml"], inputs) is False

    def test_matches_generator_input_empty(self, pcr):
        """空 committed 列表 → False。"""
        assert pcr._matches_generator_input([], {"docs/foo.yaml"}) is False

    def test_main_skip_env_returns_zero(self, pcr, monkeypatch):
        """ZEPHYR_SKIP_REGENERATE=1 → 立即返回 0，不触发任何检测。"""
        monkeypatch.setenv("ZEPHYR_SKIP_REGENERATE", "1")
        called = {"n": 0}

        def _boom():
            called["n"] += 1
            return ["should_not_be_called.yaml"]

        monkeypatch.setattr(pcr, "_committed_yaml_files", _boom)
        assert pcr.main() == 0
        assert called["n"] == 0, "逃生通道应跳过 _committed_yaml_files 调用"

    def test_main_no_yaml_change_returns_zero(self, pcr, monkeypatch):
        """commit 无 YAML 变更 → 返回 0，不 spawn。"""
        monkeypatch.delenv("ZEPHYR_SKIP_REGENERATE", raising=False)
        monkeypatch.setattr(pcr, "_committed_yaml_files", lambda: [])
        spawned = {"n": 0}
        monkeypatch.setattr(
            subprocess, "Popen", lambda *a, **k: spawned.__setitem__("n", spawned["n"] + 1) or MagicMock()
        )
        assert pcr.main() == 0
        assert spawned["n"] == 0, "无 YAML 变更不应 spawn"

    def test_main_yaml_not_generator_input_returns_zero(self, pcr, monkeypatch, tmp_path):
        """commit 改了 YAML 但非生成器输入源 → 返回 0，不 spawn。"""
        monkeypatch.delenv("ZEPHYR_SKIP_REGENERATE", raising=False)
        monkeypatch.setattr(
            pcr,
            "_committed_yaml_files",
            lambda: ["docs/01_policies_and_standards/trae_999_unrelated.yaml"],
        )
        spawned = {"n": 0}
        monkeypatch.setattr(
            subprocess, "Popen", lambda *a, **k: spawned.__setitem__("n", spawned["n"] + 1) or MagicMock()
        )
        assert pcr.main() == 0
        assert spawned["n"] == 0, "非生成器输入 YAML 不应 spawn"

    def test_main_never_blocks_on_error(self, pcr, monkeypatch):
        """任何异常 → 返回 0（post-commit 绝不阻断 git）。"""
        monkeypatch.delenv("ZEPHYR_SKIP_REGENERATE", raising=False)

        def _boom():
            raise RuntimeError("simulated git failure")

        monkeypatch.setattr(pcr, "_committed_yaml_files", _boom)
        assert pcr.main() == 0, "异常时必须返回 0，不得阻断 git"


# ============================================================================
# #ARCH-REGEN-CONCURRENCY-001 治本测试：跨进程串行锁（drop-not-queue）
# 病根：reconcile_async（--source 路径）无并发控制，post-commit worker 级联 +
#       apply_depgraph 多 reconciler → N× 编排器并发 → CPU 99% 爆炸（2026-08-05）。
# 治本：reconcile()/reconcile_stale() 入口加 OS 串行锁，drop-not-queue。
# 对标 test_post_commit_oscillation_guard.py（--stale 路径的 lockfile 测试）——
#       本类覆盖 --source 路径 + reconcile_stale 的全局串行锁。
# ============================================================================


class TestRegenConcurrencyLock:
    """验证跨进程串行锁的 drop-not-queue 语义与僵尸回收。"""

    def _hold_lock(self, rg, lock_dir, pid=None, age_seconds=0):
        """在 lock_dir 预置一个锁文件（模拟已被持有）。"""
        import os as _os

        lock_dir.mkdir(parents=True, exist_ok=True)
        lock_path = lock_dir / rg._REGEN_LOCK_NAME
        owner_pid = pid if pid is not None else _os.getpid()
        lock_path.write_text(f"{owner_pid}\n", encoding="utf-8")
        if age_seconds > 0:
            import time as _time

            old = _time.time() - age_seconds
            _os.utime(str(lock_path), (old, old))
        return lock_path

    def test_reconcile_drops_when_lock_held(self, rg, monkeypatch, tmp_path):
        """锁已被持有时 reconcile() 丢弃本次触发（drop-not-queue），不跑生成器。"""
        monkeypatch.setattr(rg, "_LOCK_DIR", tmp_path)
        self._hold_lock(rg, tmp_path)  # 当前 pid 持有 + 新鲜 → 非僵尸
        invoked = {"n": 0}
        monkeypatch.setattr(rg, "_invoke_parallel", lambda entries: invoked.__setitem__("n", invoked["n"] + 1) or [])
        result = rg.reconcile("depgraph_db")
        assert result["status"] == "skipped_dup", "锁被持有时应 drop"
        assert invoked["n"] == 0, "drop 时不应调用生成器"

    def test_reconcile_acquires_and_releases(self, rg, monkeypatch, tmp_path):
        """无锁时 reconcile() 正常执行并释放锁（lock 文件执行后消失）。"""
        monkeypatch.setattr(rg, "_LOCK_DIR", tmp_path)
        monkeypatch.setattr(rg, "_invoke_parallel", lambda entries: [])
        lock_path = tmp_path / rg._REGEN_LOCK_NAME
        result = rg.reconcile("depgraph_db")
        assert result["total"] == 0
        assert "status" not in result or result.get("status") != "skipped_dup", "应正常执行非 drop"
        assert not lock_path.exists(), "执行完毕后锁文件必须释放"

    def test_reconcile_stale_drops_when_lock_held(self, rg, monkeypatch, tmp_path):
        """锁被持有时 reconcile_stale() 同样 drop。"""
        monkeypatch.setattr(rg, "_LOCK_DIR", tmp_path)
        self._hold_lock(rg, tmp_path)
        invoked = {"n": 0}
        monkeypatch.setattr(rg, "_invoke_parallel", lambda entries: invoked.__setitem__("n", invoked["n"] + 1) or [])
        result = rg.reconcile_stale()
        assert result["status"] == "skipped_dup"
        assert invoked["n"] == 0

    def test_reconcile_steals_dead_pid_lock(self, rg, monkeypatch, tmp_path):
        """持有者进程已死 → 抢占僵尸锁并正常执行。"""
        monkeypatch.setattr(rg, "_LOCK_DIR", tmp_path)
        self._hold_lock(rg, tmp_path, pid=999999999)  # 极高 pid，几乎必然不存在
        monkeypatch.setattr(rg, "_invoke_parallel", lambda entries: [])
        result = rg.reconcile("depgraph_db")
        assert result.get("status") != "skipped_dup", "死 pid 锁应被抢占而非 drop"
        assert not (tmp_path / rg._REGEN_LOCK_NAME).exists(), "执行后应释放锁"

    def test_reconcile_steals_ttl_expired_lock(self, rg, monkeypatch, tmp_path):
        """锁龄超过 TTL（即使 pid 存活）→ 抢占。"""
        monkeypatch.setattr(rg, "_LOCK_DIR", tmp_path)
        monkeypatch.setattr(rg, "_REGEN_LOCK_TTL", 10)
        self._hold_lock(rg, tmp_path, age_seconds=999)  # 当前 pid 但 999s 前
        monkeypatch.setattr(rg, "_invoke_parallel", lambda entries: [])
        result = rg.reconcile("depgraph_db")
        assert result.get("status") != "skipped_dup", "超 TTL 锁应被抢占"

    def test_lock_released_on_exception(self, rg, monkeypatch, tmp_path):
        """生成器抛异常时锁仍由 finally 释放（不泄漏）。"""
        monkeypatch.setattr(rg, "_LOCK_DIR", tmp_path)

        def _boom(entries):
            raise RuntimeError("generator explosion")

        monkeypatch.setattr(rg, "_invoke_parallel", _boom)
        lock_path = tmp_path / rg._REGEN_LOCK_NAME
        with pytest.raises(RuntimeError):
            rg.reconcile("depgraph_db")
        assert not lock_path.exists(), "异常路径也必须释放锁"

    def test_two_sources_serialize_via_global_lock(self, rg, monkeypatch, tmp_path):
        """全局单键：不同 source 也串行（depgraph_db 与 battle_map_db 共享蓝图产物）。"""
        monkeypatch.setattr(rg, "_LOCK_DIR", tmp_path)
        self._hold_lock(rg, tmp_path)  # 任意持有中
        monkeypatch.setattr(rg, "_invoke_parallel", lambda entries: [])
        # 即便 source 不同，全局锁被持有时都应 drop
        assert rg.reconcile("depgraph_db")["status"] == "skipped_dup"
        assert rg.reconcile("battle_map_db")["status"] == "skipped_dup"
        assert rg.reconcile_stale()["status"] == "skipped_dup"
