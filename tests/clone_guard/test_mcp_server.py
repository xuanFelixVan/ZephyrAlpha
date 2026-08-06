# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.4
# [MODULE] tests.clone_guard.test_mcp_server
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/clone_guard/test_mcp_server.py
# [A_test] module_id: MOD-CLONE_GUARD | layer=test | stability=volatile | safety=L | ai_modifiable
# [TTL] permanent
"""CloneGuardMCPServer 单元测试——mock orchestrator，不依赖真实 echo-guard CLI。

覆盖：
  - 工具注册（2 工具：check_before_write + health_check）
  - _check_before_write：空文件 / 正常 findings / degraded / 异常兜底
  - _health_check：引擎可用 / 不可用
  - _build_hint：各种 findings 组合
  - create_server 工厂函数
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.clone_guard.engines.echo_guard_adapter import Finding
from zephyr.clone_guard.mcp_server import CloneGuardMCPServer, create_server
from zephyr.clone_guard.orchestrator import CheckResult

# ---------------------------------------------------------------------------
# 辅助工厂
# ---------------------------------------------------------------------------


def _make_finding(
    *,
    severity: str = "extract",
    clone_type: str = "T2",
    similarity: float = 0.92,
    source_file: str = "src/new.py",
    source_function: str = "calc",
    existing_file: str = "src/old.py",
    existing_function: str = "compute",
    import_suggestion: str | None = "from src.old import compute",
) -> Finding:
    return Finding(
        finding_id="F-001",
        severity=severity,
        clone_type=clone_type,
        similarity=similarity,
        source_file=source_file,
        source_function=source_function,
        source_lineno=10,
        existing_file=existing_file,
        existing_function=existing_function,
        existing_lineno=20,
        import_suggestion=import_suggestion,
    )


def _make_server_with_mock_orch(
    tmp_path: Path, check_result: CheckResult
) -> CloneGuardMCPServer:
    """创建 server 并注入 mock orchestrator（避免依赖 echo-guard CLI）。"""
    server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
    mock_orch = MagicMock()
    mock_orch.check.return_value = check_result
    server._orchestrator = mock_orch  # 注入 mock，跳过懒加载
    return server


# ---------------------------------------------------------------------------
# 工具注册测试
# ---------------------------------------------------------------------------


class TestToolRegistration:
    """工具注册测试。"""

    def test_two_tools_registered(self, tmp_path: Path):
        """注册 2 工具：check_before_write + health_check。"""
        server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
        assert "clone_guard.check_before_write" in server.tool_names
        assert "clone_guard.health_check" in server.tool_names
        assert len(server.tool_names) == 2

    def test_server_id(self, tmp_path: Path):
        server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
        assert server.server_id == "clone_guard"

    def test_tool_safety_level_is_L(self, tmp_path: Path):
        """两个工具都是 safety_level=L（只读检测，不修改文件）。"""
        server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
        for tool_def in server.tools.values():
            assert tool_def.safety_level == "L"


# ---------------------------------------------------------------------------
# _check_before_write 测试
# ---------------------------------------------------------------------------


class TestCheckBeforeWrite:
    """check_before_write handler 测试——覆盖空文件/正常/降级/异常路径。"""

    def test_empty_files_returns_passed_no_findings(self, tmp_path: Path):
        """空文件列表直接返回 passed=True。"""
        server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
        result = server._check_before_write(files=[])
        assert result["passed"] is True
        assert result["findings_count"] == 0
        assert result["findings"] == []
        assert result["degraded"] is False
        assert result["checked_files"] == 0

    def test_no_findings_returns_passed(self, tmp_path: Path):
        """orchestrator 返回无 findings → passed=True。"""
        check_result = CheckResult(passed=True, findings=[], degraded=False, checked_files=2)
        server = _make_server_with_mock_orch(tmp_path, check_result)

        result = server._check_before_write(files=["src/foo.py", "src/bar.py"])

        assert result["passed"] is True
        assert result["findings_count"] == 0
        assert result["degraded"] is False
        assert result["checked_files"] == 2
        assert "可以安全写入" in result["hint"]

    def test_extract_findings_returns_not_passed(self, tmp_path: Path):
        """orchestrator 返回 extract 级 findings → passed=False（L0 advisory 但仍标注未通过）。"""
        finding = _make_finding(severity="extract", import_suggestion="from src.old import compute")
        check_result = CheckResult(passed=False, findings=[finding], degraded=False, checked_files=1)
        server = _make_server_with_mock_orch(tmp_path, check_result)

        result = server._check_before_write(files=["src/new.py"])

        assert result["passed"] is False
        assert result["findings_count"] == 1
        assert result["degraded"] is False
        assert result["findings"][0]["severity"] == "extract"
        assert result["findings"][0]["import_suggestion"] == "from src.old import compute"
        assert "import_suggestion" in result["hint"] or "from src.old import compute" in result["hint"]

    def test_review_findings_returns_passed_with_hint(self, tmp_path: Path):
        """orchestrator 返回 review 级 findings → passed=True（review 不阻断）但有 hint。"""
        finding = _make_finding(severity="review", similarity=0.75, import_suggestion=None)
        check_result = CheckResult(passed=True, findings=[finding], degraded=False, checked_files=1)
        server = _make_server_with_mock_orch(tmp_path, check_result)

        result = server._check_before_write(files=["src/new.py"])

        assert result["passed"] is True
        assert result["findings_count"] == 1
        assert result["findings"][0]["severity"] == "review"
        assert "review" in result["hint"].lower() or "精简" in result["hint"]

    def test_degraded_returns_passed_with_degraded_hint(self, tmp_path: Path):
        """orchestrator 降级 → passed=True + degraded=True + 降级 hint。"""
        check_result = CheckResult(
            passed=True, findings=[], degraded=True, error="echo-guard 不可用", checked_files=1
        )
        server = _make_server_with_mock_orch(tmp_path, check_result)

        result = server._check_before_write(files=["src/foo.py"])

        assert result["passed"] is True  # L0 降级放行
        assert result["degraded"] is True
        assert result["error"] == "echo-guard 不可用"
        assert "降级" in result["hint"]

    def test_orchestrator_exception_does_not_raise(self, tmp_path: Path):
        """orchestrator 抛异常时 _check_before_write 不抛异常（L0 永不阻断）。"""
        server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
        mock_orch = MagicMock()
        mock_orch.check.side_effect = RuntimeError("unexpected boom")
        server._orchestrator = mock_orch

        result = server._check_before_write(files=["src/foo.py"])

        assert result["passed"] is True  # 降级放行
        assert result["degraded"] is True
        assert "unexpected boom" in result["error"]
        assert "降级" in result["hint"]

    def test_finding_serialization(self, tmp_path: Path):
        """finding 正确序列化为可 JSON 化的 dict。"""
        finding = _make_finding(
            severity="extract",
            clone_type="T3",
            similarity=0.885,
            source_file="src/new.py",
            source_function="my_func",
            existing_file="src/existing.py",
            existing_function="their_func",
            import_suggestion="from src.existing import their_func",
        )
        check_result = CheckResult(passed=False, findings=[finding], degraded=False, checked_files=1)
        server = _make_server_with_mock_orch(tmp_path, check_result)

        result = server._check_before_write(files=["src/new.py"])

        f = result["findings"][0]
        assert f["severity"] == "extract"
        assert f["clone_type"] == "T3"
        assert f["similarity"] == pytest.approx(0.885, abs=0.001)  # round(0.885, 4)
        assert f["source_file"] == "src/new.py"
        assert f["source_function"] == "my_func"
        assert f["existing_file"] == "src/existing.py"
        assert f["existing_function"] == "their_func"
        assert f["import_suggestion"] == "from src.existing import their_func"

    def test_similarity_rounded_to_4_decimals(self, tmp_path: Path):
        """similarity 四舍五入到 4 位小数。"""
        finding = _make_finding(similarity=0.123456789)
        check_result = CheckResult(passed=False, findings=[finding], degraded=False, checked_files=1)
        server = _make_server_with_mock_orch(tmp_path, check_result)

        result = server._check_before_write(files=["src/new.py"])

        assert result["findings"][0]["similarity"] == 0.1235  # round(0.123456789, 4)

    def test_session_id_accepted_but_not_required(self, tmp_path: Path):
        """session_id 参数被接受但不影响检测结果。"""
        check_result = CheckResult(passed=True, findings=[], degraded=False, checked_files=1)
        server = _make_server_with_mock_orch(tmp_path, check_result)

        result = server._check_before_write(files=["src/foo.py"], session_id="sess-123")

        assert result["passed"] is True

    def test_checked_at_timestamp_present(self, tmp_path: Path):
        """结果包含 checked_at 时间戳。"""
        check_result = CheckResult(passed=True, findings=[], degraded=False, checked_files=0)
        server = _make_server_with_mock_orch(tmp_path, check_result)

        result = server._check_before_write(files=[])

        assert "checked_at" in result
        assert isinstance(result["checked_at"], str)


# ---------------------------------------------------------------------------
# _health_check 测试
# ---------------------------------------------------------------------------


class TestHealthCheck:
    """health_check handler 测试。"""

    def test_returns_engine_available_false_when_no_index(self, tmp_path: Path):
        """索引不存在时 engine_available=False。"""
        server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
        with patch("zephyr.clone_guard.mcp_server.EchoGuardAdapter") as mock_adapter_cls:
            mock_adapter = MagicMock()
            mock_adapter.health_check.return_value = False
            mock_adapter_cls.return_value = mock_adapter

            result = server._health_check()

        assert result["engine_available"] is False
        assert result["index_exists"] is False
        assert "降级" in result["hint"] or "不可用" in result["hint"]

    def test_returns_engine_available_true_when_healthy(self, tmp_path: Path):
        """引擎可用时 engine_available=True。"""
        (tmp_path / ".echo-guard").mkdir(parents=True)
        (tmp_path / ".echo-guard" / "index.duckdb").touch()

        server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
        with patch("zephyr.clone_guard.mcp_server.EchoGuardAdapter") as mock_adapter_cls:
            mock_adapter = MagicMock()
            mock_adapter.health_check.return_value = True
            mock_adapter_cls.return_value = mock_adapter

            result = server._health_check()

        assert result["engine_available"] is True
        assert result["index_exists"] is True
        assert "可用" in result["hint"]

    def test_includes_env_config(self, tmp_path: Path):
        """health_check 返回 env 配置（含 HF_HUB_OFFLINE）。"""
        server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
        with patch("zephyr.clone_guard.mcp_server.EchoGuardAdapter") as mock_adapter_cls:
            mock_adapter = MagicMock()
            mock_adapter.health_check.return_value = False
            mock_adapter_cls.return_value = mock_adapter

            result = server._health_check()

        assert "env" in result
        assert isinstance(result["env"], dict)

    def test_adapter_exception_does_not_raise(self, tmp_path: Path):
        """EchoGuardAdapter.health_check 抛异常时不影响 _health_check。"""
        server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
        with patch("zephyr.clone_guard.mcp_server.EchoGuardAdapter") as mock_adapter_cls:
            mock_adapter = MagicMock()
            mock_adapter.health_check.side_effect = RuntimeError("boom")
            mock_adapter_cls.return_value = mock_adapter

            result = server._health_check()

        assert result["engine_available"] is False


# ---------------------------------------------------------------------------
# _build_hint 测试
# ---------------------------------------------------------------------------


class TestBuildHint:
    """_build_hint 静态方法测试——覆盖各种 findings 组合。"""

    def test_degraded_hint(self):
        """降级模式返回降级 hint。"""
        result = CheckResult(passed=True, degraded=True, checked_files=1)
        hint = CloneGuardMCPServer._build_hint(result, [])
        assert "降级" in hint

    def test_no_findings_hint(self):
        """无 findings 返回安全写入 hint。"""
        result = CheckResult(passed=True, findings=[], degraded=False, checked_files=1)
        hint = CloneGuardMCPServer._build_hint(result, [])
        assert "安全写入" in hint

    def test_extract_findings_hint_includes_suggestion(self):
        """extract 级 findings 的 hint 包含 import_suggestion。"""
        result = CheckResult(passed=False, degraded=False, checked_files=1)
        findings = [
            {
                "severity": "extract",
                "import_suggestion": "from src.old import compute",
                "source_function": "calc",
            }
        ]
        hint = CloneGuardMCPServer._build_hint(result, findings)
        assert "extract" in hint
        assert "from src.old import compute" in hint

    def test_review_findings_hint(self):
        """review 级 findings 的 hint 包含精简建议。"""
        result = CheckResult(passed=True, degraded=False, checked_files=1)
        findings = [{"severity": "review", "import_suggestion": None}]
        hint = CloneGuardMCPServer._build_hint(result, findings)
        assert "review" in hint or "精简" in hint

    def test_extract_without_suggestion_no_crash(self):
        """extract 级 findings 但无 import_suggestion 时不崩溃。"""
        result = CheckResult(passed=False, degraded=False, checked_files=1)
        findings = [{"severity": "extract", "import_suggestion": None, "source_function": "fn"}]
        hint = CloneGuardMCPServer._build_hint(result, findings)
        assert isinstance(hint, str)


# ---------------------------------------------------------------------------
# create_server 工厂函数测试
# ---------------------------------------------------------------------------


class TestCreateServer:
    """create_server 工厂函数测试。"""

    def test_returns_clone_guard_mcp_server(self, tmp_path: Path):
        server = create_server(repo_root=tmp_path, enable_rbac=False)
        assert isinstance(server, CloneGuardMCPServer)

    def test_server_has_tools(self, tmp_path: Path):
        server = create_server(repo_root=tmp_path, enable_rbac=False)
        assert len(server.tool_names) == 2

    def test_default_repo_root(self):
        """不传 repo_root 时使用默认当前目录。"""
        server = create_server(enable_rbac=False)
        assert isinstance(server, CloneGuardMCPServer)
        assert server.server_id == "clone_guard"
