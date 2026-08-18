# [A_test] module_id=MOD-INF-013 | layer=test | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/model_context_protocol_servers/blueprint.md | §14
# [TESTS] tests/test_mcp_launcher.py
# [TTL] task_bound

"""MCP集群launcher.py自动化测试——DAG拓扑/路径/dry-run/signal/timeout。

覆盖DM-202314验收标准：5个维度验证MCP集群启动/关闭自动化能力。
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

from zephyr.shared.io.paths import REPO_ROOT


@pytest.fixture(scope="module")
def launcher_module():
    """导入launcher模块（避免实际启动进程）。"""
    import importlib.util

    launcher_path = REPO_ROOT / "scripts" / "mcp" / "launcher.py"
    spec = importlib.util.spec_from_file_location("launcher", launcher_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestMCPLauncher:
    """MCP集群launcher.py自动化测试。"""

    def test_dag_topology(self, launcher_module):
        """验证DAG拓扑排序：layer_1无依赖，layer_4为gateway最后启动。"""
        order = launcher_module.topological_order()

        # 应有4个非空层（layer_0为空，跳过）
        assert len(order) == 4, f"Expected 4 non-empty layers, got {len(order)}"

        # layer_1应包含基础Server
        layer_1 = order[0]
        assert "gate_engine" in layer_1
        assert "blueprint_search" in layer_1
        assert "governance" in layer_1

        # layer_2应包含task_manager
        layer_2 = order[1]
        assert "task_manager" in layer_2

        # layer_3应包含session_handoff和intent_router
        layer_3 = order[2]
        assert "session_handoff" in layer_3
        assert "intent_router" in layer_3

        # layer_4应只有gateway（最后启动）
        layer_4 = order[3]
        assert layer_4 == ["gateway"], f"Expected ['gateway'], got {layer_4}"

    def test_server_paths_exist(self, launcher_module):
        """验证全部9个Server脚本路径存在。"""
        scripts = launcher_module.SERVER_SCRIPTS
        assert len(scripts) == 9, f"Expected 9 servers, got {len(scripts)}"

        for server_id, script_rel in scripts.items():
            script_path = REPO_ROOT / script_rel
            assert script_path.exists(), f"Server {server_id} script not found: {script_path}"

    def test_dry_run_output(self, launcher_module, capsys):
        """验证--dry-run模式输出包含全部9个Server。"""
        exit_code = launcher_module.dry_run()
        captured = capsys.readouterr()

        assert exit_code == 0, f"dry_run returned exit_code={exit_code}"
        assert "9" in captured.out, "Output should mention 9 servers"

        # 验证所有Server ID出现在输出中
        for server_id in launcher_module.SERVER_SCRIPTS:
            assert server_id in captured.out, f"Server {server_id} not in dry_run output"

    def test_signal_handler_registered(self, launcher_module):
        """验证launcher.py定义了signal处理函数（通过检查源码结构）。"""
        import inspect

        # launch_all函数应包含signal注册逻辑
        source = inspect.getsource(launcher_module.launch_all)
        assert "signal.signal" in source, "launch_all should register signal handlers"
        assert "SIGINT" in source, "Should handle SIGINT"
        assert "SIGTERM" in source, "Should handle SIGTERM"
        assert "_shutdown" in source, "Should define _shutdown callback"

    def test_idle_timeout_config(self, launcher_module):
        """验证ProcessLifecycleGateway的idle_timeout配置（600秒=10分钟）。"""
        import inspect

        # start_server函数应包含idle_timeout_s参数
        source = inspect.getsource(launcher_module.start_server)
        assert "idle_timeout_s" in source, "start_server should set idle_timeout_s"

        # launch_all函数也应包含idle_timeout_s
        source_all = inspect.getsource(launcher_module.launch_all)
        assert "idle_timeout_s" in source_all, "launch_all should set idle_timeout_s"

        # 验证超时值为600秒（10分钟）
        assert "600" in source or "600" in source_all, "idle_timeout should be 600 seconds"
