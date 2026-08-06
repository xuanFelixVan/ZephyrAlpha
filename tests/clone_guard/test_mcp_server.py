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
"""CloneGuardMCPServer 单元测试——mock orchestrator/relate，不依赖真实 CLI。

覆盖：
  - 工具注册（4 工具：check_before_write + search_functions + audit_status + health_check）
  - _check_before_write：空文件 / 正常 findings / degraded / 异常兜底
  - _search_functions：空查询 / relate 不可用降级 / 正常结果
  - _audit_status：无历史审计 / 有审计结果 / 异常兜底
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


def _make_server_with_mock_orch(tmp_path: Path, check_result: CheckResult | None = None) -> CloneGuardMCPServer:
    """创建 server 并注入 mock orchestrator（避免依赖 echo-guard CLI）。"""
    server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
    mock_orch = MagicMock()
    if check_result is not None:
        mock_orch.check.return_value = check_result
    server._orchestrator = mock_orch  # 注入 mock，跳过懒加载
    return server


# ---------------------------------------------------------------------------
# 工具注册测试
# ---------------------------------------------------------------------------


class TestToolRegistration:
    """工具注册测试。"""

    def test_four_tools_registered(self, tmp_path: Path):
        """注册 4 工具：check_before_write + search_functions + audit_status + health_check。"""
        server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
        assert "clone_guard.check_before_write" in server.tool_names
        assert "clone_guard.search_functions" in server.tool_names
        assert "clone_guard.audit_status" in server.tool_names
        assert "clone_guard.health_check" in server.tool_names
        assert len(server.tool_names) == 4

    def test_server_id(self, tmp_path: Path):
        server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
        assert server.server_id == "clone_guard"

    def test_tool_safety_level_is_L(self, tmp_path: Path):
        """四个工具都是 safety_level=L（只读检测，不修改文件）。"""
        server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
        for tool_def in server.tools.values():
            assert tool_def.safety_level == "L"


# ---------------------------------------------------------------------------
# _check_before_write 测试
# ---------------------------------------------------------------------------


class TestCheckBeforeWrite:
    """check_before_write handler 测试——覆盖空文件/正常/降级/异常路径。"""

    def test_empty_files_returns_passed_no_findings(self, tmp_path: Path):
        server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
        result = server._check_before_write(files=[])
        assert result["passed"] is True
        assert result["findings_count"] == 0
        assert result["degraded"] is False
        assert result["checked_files"] == 0

    def test_no_findings_returns_passed(self, tmp_path: Path):
        check_result = CheckResult(passed=True, findings=[], degraded=False, checked_files=2)
        server = _make_server_with_mock_orch(tmp_path, check_result)
        result = server._check_before_write(files=["src/foo.py", "src/bar.py"])
        assert result["passed"] is True
        assert result["degraded"] is False
        assert result["checked_files"] == 2
        assert "可以安全写入" in result["hint"]

    def test_extract_findings_returns_not_passed(self, tmp_path: Path):
        finding = _make_finding(severity="extract", import_suggestion="from src.old import compute")
        check_result = CheckResult(passed=False, findings=[finding], degraded=False, checked_files=1)
        server = _make_server_with_mock_orch(tmp_path, check_result)
        result = server._check_before_write(files=["src/new.py"])
        assert result["passed"] is False
        assert result["findings_count"] == 1
        assert result["findings"][0]["severity"] == "extract"

    def test_degraded_returns_passed_with_degraded_hint(self, tmp_path: Path):
        check_result = CheckResult(passed=True, findings=[], degraded=True, error="echo-guard 不可用", checked_files=1)
        server = _make_server_with_mock_orch(tmp_path, check_result)
        result = server._check_before_write(files=["src/foo.py"])
        assert result["passed"] is True
        assert result["degraded"] is True
        assert "降级" in result["hint"]

    def test_orchestrator_exception_does_not_raise(self, tmp_path: Path):
        server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
        mock_orch = MagicMock()
        mock_orch.check.side_effect = RuntimeError("unexpected boom")
        server._orchestrator = mock_orch
        result = server._check_before_write(files=["src/foo.py"])
        assert result["passed"] is True  # 降级放行
        assert result["degraded"] is True
        assert "unexpected boom" in result["error"]

    def test_similarity_rounded_to_4_decimals(self, tmp_path: Path):
        finding = _make_finding(similarity=0.123456789)
        check_result = CheckResult(passed=False, findings=[finding], degraded=False, checked_files=1)
        server = _make_server_with_mock_orch(tmp_path, check_result)
        result = server._check_before_write(files=["src/new.py"])
        assert result["findings"][0]["similarity"] == 0.1235

    def test_checked_at_timestamp_present(self, tmp_path: Path):
        check_result = CheckResult(passed=True, findings=[], degraded=False, checked_files=0)
        server = _make_server_with_mock_orch(tmp_path, check_result)
        result = server._check_before_write(files=[])
        assert "checked_at" in result
        assert isinstance(result["checked_at"], str)


# ---------------------------------------------------------------------------
# _search_functions 测试
# ---------------------------------------------------------------------------


class TestSearchFunctions:
    """search_functions handler 测试——L0 按语义搜已有函数。"""

    def test_empty_query_returns_no_search(self, tmp_path: Path):
        """空查询 → 无需搜索。"""
        server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
        result = server._search_functions(query="")
        assert result["results"] == []
        assert result["degraded"] is False
        assert "未提供查询" in result["hint"]

    def test_relate_unavailable_returns_degraded(self, tmp_path: Path):
        """relate 不可用 → degraded=True + 空结果。"""
        server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
        with patch("zephyr.clone_guard.mcp_server.RelateAdapter") as mock_cls:
            mock_adapter = MagicMock()
            mock_adapter.health_check.return_value = False
            mock_cls.return_value = mock_adapter
            result = server._search_functions(query="def compute():")
        assert result["results"] == []
        assert result["degraded"] is True
        assert "relate" in result["engines_checked"]
        assert result["engines_available"] == []

    def test_relate_returns_results(self, tmp_path: Path):
        """relate 可用 → 序列化结果 + 去重 + 按相似度排序。"""
        server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
        f1 = _make_finding(
            severity="acknowledged",
            similarity=0.88,
            existing_file="src/a.py",
            existing_function="compute",
            import_suggestion="from src.a import compute",
        )
        f2 = _make_finding(
            severity="acknowledged",
            similarity=0.95,
            existing_file="src/b.py",
            existing_function="calc",
            import_suggestion="from src.b import calc",
        )
        with patch("zephyr.clone_guard.mcp_server.RelateAdapter") as mock_cls:
            mock_adapter = MagicMock()
            mock_adapter.health_check.return_value = True
            mock_adapter.search.return_value = [f1, f2]
            mock_cls.return_value = mock_adapter
            result = server._search_functions(query="def compute():", top_k=10)
        assert result["degraded"] is False
        assert result["results_count"] == 2
        # 按相似度降序
        assert result["results"][0]["similarity"] == pytest.approx(0.95, abs=0.001)
        assert result["results"][0]["existing_function"] == "calc"
        assert result["results"][0]["engine"] == "relate"
        assert "找到 2 个相似函数" in result["hint"]

    def test_dedup_by_existing_file_function(self, tmp_path: Path):
        """同 (existing_file, existing_function) 去重，保留相似度最高。"""
        server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
        f1 = _make_finding(
            severity="acknowledged",
            similarity=0.80,
            existing_file="src/a.py",
            existing_function="compute",
            import_suggestion=None,
        )
        f2 = _make_finding(
            severity="acknowledged",
            similarity=0.92,
            existing_file="src/a.py",
            existing_function="compute",
            import_suggestion=None,
        )
        with patch("zephyr.clone_guard.mcp_server.RelateAdapter") as mock_cls:
            mock_adapter = MagicMock()
            mock_adapter.health_check.return_value = True
            mock_adapter.search.return_value = [f1, f2]
            mock_cls.return_value = mock_adapter
            result = server._search_functions(query="def compute():")
        assert result["results_count"] == 1
        assert result["results"][0]["similarity"] == pytest.approx(0.92, abs=0.001)

    def test_relate_exception_does_not_raise(self, tmp_path: Path):
        """relate 异常时 search_functions 不抛异常。"""
        server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
        with patch("zephyr.clone_guard.mcp_server.RelateAdapter") as mock_cls:
            mock_cls.side_effect = RuntimeError("boom")
            result = server._search_functions(query="def compute():")
        assert result["degraded"] is True
        assert result["results"] == []


# ---------------------------------------------------------------------------
# _audit_status 测试
# ---------------------------------------------------------------------------


class TestAuditStatus:
    """audit_status handler 测试——L2 查询技术债。"""

    def test_no_audit_returns_no_audit_status(self, tmp_path: Path):
        """无历史审计 → status=no_audit。"""
        server = _make_server_with_mock_orch(tmp_path)
        server._orchestrator.load_latest_audit.return_value = None
        result = server._audit_status()
        assert result["status"] == "no_audit"
        assert result["degraded"] is False
        assert "尚未执行" in result["hint"]

    def test_with_audit_returns_ok(self, tmp_path: Path):
        """有审计结果 → status=ok + 字段透传。"""
        server = _make_server_with_mock_orch(tmp_path)
        server._orchestrator.load_latest_audit.return_value = {
            "timestamp": "2026-08-06T12:00:00",
            "health_score": "B",
            "findings_count": 3,
            "refactoring_plan": ["[majority] src/a.py:fn → 复用 src/b.py:fn"],
            "degraded_engines": [],
            "active_engine_count": 3,
            "checked_files": 42,
        }
        result = server._audit_status()
        assert result["status"] == "ok"
        assert result["health_score"] == "B"
        assert result["findings_count"] == 3
        assert len(result["refactoring_plan"]) == 1
        assert result["checked_files"] == 42

    def test_severe_health_score_hint(self, tmp_path: Path):
        """health_score=F → hint 提示严重。"""
        server = _make_server_with_mock_orch(tmp_path)
        server._orchestrator.load_latest_audit.return_value = {
            "timestamp": "2026-08-06T12:00:00",
            "health_score": "F",
            "findings_count": 10,
            "refactoring_plan": [],
        }
        result = server._audit_status()
        assert "严重" in result["hint"]

    def test_orchestrator_exception_does_not_raise(self, tmp_path: Path):
        """load_latest_audit 异常时 audit_status 不抛异常。"""
        server = _make_server_with_mock_orch(tmp_path)
        server._orchestrator.load_latest_audit.side_effect = RuntimeError("boom")
        result = server._audit_status()
        assert result["status"] == "error"
        assert result["degraded"] is True


# ---------------------------------------------------------------------------
# _health_check 测试
# ---------------------------------------------------------------------------


class TestHealthCheck:
    """health_check handler 测试。"""

    def test_returns_engine_available_false_when_no_index(self, tmp_path: Path):
        server = CloneGuardMCPServer(repo_root=tmp_path, enable_rbac=False)
        with patch("zephyr.clone_guard.mcp_server.EchoGuardAdapter") as mock_adapter_cls:
            mock_adapter = MagicMock()
            mock_adapter.health_check.return_value = False
            mock_adapter_cls.return_value = mock_adapter
            result = server._health_check()
        assert result["engine_available"] is False

    def test_returns_engine_available_true_when_healthy(self, tmp_path: Path):
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

    def test_adapter_exception_does_not_raise(self, tmp_path: Path):
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
    """_build_hint 静态方法测试。"""

    def test_degraded_hint(self):
        result = CheckResult(passed=True, degraded=True, checked_files=1)
        hint = CloneGuardMCPServer._build_hint(result, [])
        assert "降级" in hint

    def test_no_findings_hint(self):
        result = CheckResult(passed=True, findings=[], degraded=False, checked_files=1)
        hint = CloneGuardMCPServer._build_hint(result, [])
        assert "安全写入" in hint

    def test_extract_findings_hint_includes_suggestion(self):
        result = CheckResult(passed=False, degraded=False, checked_files=1)
        findings = [
            {"severity": "extract", "import_suggestion": "from src.old import compute", "source_function": "calc"}
        ]
        hint = CloneGuardMCPServer._build_hint(result, findings)
        assert "extract" in hint
        assert "from src.old import compute" in hint

    def test_review_findings_hint(self):
        result = CheckResult(passed=True, degraded=False, checked_files=1)
        findings = [{"severity": "review", "import_suggestion": None}]
        hint = CloneGuardMCPServer._build_hint(result, findings)
        assert "review" in hint or "精简" in hint


# ---------------------------------------------------------------------------
# create_server 工厂函数测试
# ---------------------------------------------------------------------------


class TestCreateServer:
    """create_server 工厂函数测试。"""

    def test_returns_clone_guard_mcp_server(self, tmp_path: Path):
        server = create_server(repo_root=tmp_path, enable_rbac=False)
        assert isinstance(server, CloneGuardMCPServer)

    def test_server_has_four_tools(self, tmp_path: Path):
        server = create_server(repo_root=tmp_path, enable_rbac=False)
        assert len(server.tool_names) == 4

    def test_default_repo_root(self):
        """不传 repo_root 时使用默认当前目录。"""
        server = create_server(enable_rbac=False)
        assert isinstance(server, CloneGuardMCPServer)
        assert server.server_id == "clone_guard"
