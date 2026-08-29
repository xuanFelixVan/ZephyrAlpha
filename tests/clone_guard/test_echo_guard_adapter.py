# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] tests.clone_guard.test_echo_guard_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/clone_guard/test_echo_guard_adapter.py
# [A_test] module_id: MOD-CLONE_GUARD | layer=test | stability=volatile | safety=L | ai_modifiable
# [TTL] permanent
"""EchoGuardAdapter 单元测试——mock subprocess 调用，不依赖真实 echo-guard CLI。"""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.echo_guard_adapter import EchoGuardAdapter, Finding


class TestEchoGuardAdapterHealthCheck:
    """health_check 测试。"""

    def test_no_index_returns_false(self, tmp_path: Path):
        """索引文件不存在时返回 False。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        assert adapter.health_check() is False

    def test_cli_missing_returns_false(self, tmp_path: Path):
        """CLI 未安装时返回 False。"""
        (tmp_path / ".echo-guard" / "index.duckdb").parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / ".echo-guard" / "index.duckdb").touch()
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        with patch("subprocess.run", side_effect=FileNotFoundError):
            assert adapter.health_check() is False

    def test_cli_ok_returns_true(self, tmp_path: Path):
        """CLI 存在 + 索引存在时返回 True。"""
        (tmp_path / ".echo-guard").mkdir(parents=True)
        (tmp_path / ".echo-guard" / "index.duckdb").touch()
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0)
        with patch("subprocess.run", return_value=mock_result):
            assert adapter.health_check() is True


class TestEchoGuardAdapterDetect:
    """detect 测试——覆盖降级路径和正常路径。"""

    def test_empty_files_returns_empty_no_degraded(self, tmp_path: Path):
        """空文件列表直接返回（不调用 CLI）。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        findings, degraded = adapter.detect([])
        assert findings == []
        assert degraded is False

    def test_echo_guard_disabled_returns_degraded(self, tmp_path: Path):
        """echo_guard_enabled=False 时返回空 + degraded=True。"""
        cfg = CloneGuardConfig(echo_guard_enabled=False)
        adapter = EchoGuardAdapter(tmp_path, cfg)
        findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_cli_not_found_degraded(self, tmp_path: Path):
        """CLI 未安装时降级（空列表 + degraded=True）。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        with patch("subprocess.run", side_effect=FileNotFoundError):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_cli_timeout_degraded(self, tmp_path: Path):
        """CLI 超时时降级。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="echo-guard", timeout=30)):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_no_index_exit_code_2_degraded(self, tmp_path: Path):
        """exit_code=2（索引不存在）时降级。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=2, stdout="", stderr="no index")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_unknown_exit_code_degraded(self, tmp_path: Path):
        """未知退出码时降级。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=99, stdout="", stderr="unknown error")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_json_decode_error_degraded(self, tmp_path: Path):
        """JSON 解析失败时降级。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0, stdout="not json{", stderr="")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_no_findings_returns_empty(self, tmp_path: Path):
        """正常执行但无克隆发现。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"findings": []}), stderr="")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is False

    def test_match_finding_parsed(self, tmp_path: Path):
        """type=match 的 finding 正确解析为 Finding 对象。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        raw = {
            "findings": [
                {
                    "type": "match",
                    "finding_id": "F-001",
                    "severity": "extract",
                    "clone_type": "T2",
                    "similarity_score": 0.92,
                    "source": {"filepath": "src/new.py", "name": "calc", "lineno": 10},
                    "existing": {
                        "filepath": "src/old.py",
                        "name": "compute",
                        "lineno": 20,
                        "import_suggestion": "from src.old import compute",
                    },
                }
            ]
        }
        mock_result = MagicMock(returncode=1, stdout=json.dumps(raw), stderr="")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.detect(["src/new.py"])
        assert degraded is False
        assert len(findings) == 1
        f = findings[0]
        assert f.finding_id == "F-001"
        assert f.severity == "extract"
        assert f.clone_type == "T2"
        assert f.similarity == pytest.approx(0.92)
        assert f.source_file == "src/new.py"
        assert f.source_function == "calc"
        assert f.source_lineno == 10
        assert f.existing_file == "src/old.py"
        assert f.existing_function == "compute"
        assert f.existing_lineno == 20
        assert f.import_suggestion == "from src.old import compute"

    def test_group_finding_parsed(self, tmp_path: Path):
        """type=group 的 finding（多副本组）正确解析为多个 Finding。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        raw = {
            "findings": [
                {
                    "type": "group",
                    "finding_id": "G-001",
                    "severity": "extract",
                    "clone_type": "T3",
                    "similarity_score": 0.88,
                    "functions": [
                        {"filepath": "src/a.py", "name": "fn_a", "lineno": 5},
                        {"filepath": "src/b.py", "name": "fn_b", "lineno": 15},
                        {"filepath": "src/c.py", "name": "fn_c", "lineno": 25},
                    ],
                }
            ]
        }
        mock_result = MagicMock(returncode=1, stdout=json.dumps(raw), stderr="")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.detect(["src/a.py"])
        assert degraded is False
        assert len(findings) == 2  # 3 functions → 2 pairs (source vs each existing)
        assert findings[0].source_file == "src/a.py"
        assert findings[0].existing_file == "src/b.py"
        assert findings[1].existing_file == "src/c.py"

    def test_malformed_finding_skipped(self, tmp_path: Path):
        """格式错误的 finding 被跳过（不抛异常）。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        raw = {
            "findings": [
                {"type": "match", "finding_id": "BAD"},  # 缺 source/existing
                {
                    "type": "match",
                    "finding_id": "GOOD",
                    "severity": "review",
                    "clone_type": "T1",
                    "similarity_score": 0.5,
                    "source": {"filepath": "a.py", "name": "f1", "lineno": 1},
                    "existing": {"filepath": "b.py", "name": "f2", "lineno": 2},
                },
            ]
        }
        mock_result = MagicMock(returncode=1, stdout=json.dumps(raw), stderr="")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.detect(["a.py"])
        assert degraded is False
        assert len(findings) == 1
        assert findings[0].finding_id == "GOOD"


class TestEnvInjection:
    """env 注入测试——#ARCH-FORCE-MERGE-DEDUP-001 Phase A 闭合（HF_HUB_OFFLINE 离线优先）。

    验证 EchoGuardAdapter 在 subprocess.run 调用时注入 config.env，
    确保 L1 pre-commit 路径强制离线模式（Tier 1 AST 哈希检测）。
    """

    def test_detect_injects_config_env(self, tmp_path: Path):
        """detect 调用 subprocess.run 时注入 config.env。"""
        cfg = CloneGuardConfig(env={"HF_HUB_OFFLINE": "1"})
        adapter = EchoGuardAdapter(tmp_path, cfg)
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"findings": []}), stderr="")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            adapter.detect(["src/foo.py"])
        mock_run.assert_called_once()
        _, kwargs = mock_run.call_args
        assert "env" in kwargs
        assert kwargs["env"]["HF_HUB_OFFLINE"] == "1"

    def test_detect_merges_system_env(self, tmp_path: Path):
        """detect 注入的 env 包含系统环境变量 + config.env（config 覆盖系统）。"""
        cfg = CloneGuardConfig(env={"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"})
        adapter = EchoGuardAdapter(tmp_path, cfg)
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"findings": []}), stderr="")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            adapter.detect(["src/foo.py"])
        _, kwargs = mock_run.call_args
        # 系统 env（PATH 等）应存在
        assert "PATH" in kwargs["env"]
        # config env 应存在
        assert kwargs["env"]["HF_HUB_OFFLINE"] == "1"
        assert kwargs["env"]["TRANSFORMERS_OFFLINE"] == "1"

    def test_health_check_injects_config_env(self, tmp_path: Path):
        """health_check 调用 subprocess.run 时注入 config.env。"""
        (tmp_path / ".echo-guard").mkdir(parents=True)
        (tmp_path / ".echo-guard" / "index.duckdb").touch()
        cfg = CloneGuardConfig(env={"HF_HUB_OFFLINE": "1"})
        adapter = EchoGuardAdapter(tmp_path, cfg)
        mock_result = MagicMock(returncode=0)
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            adapter.health_check()
        mock_run.assert_called_once()
        _, kwargs = mock_run.call_args
        assert kwargs["env"]["HF_HUB_OFFLINE"] == "1"

    def test_default_env_empty_uses_system_env_only(self, tmp_path: Path):
        """无 env 配置时仅使用系统环境变量（env={} 不破坏系统 env）。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"findings": []}), stderr="")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            adapter.detect(["src/foo.py"])
        _, kwargs = mock_run.call_args
        assert "env" in kwargs
        # 系统 PATH 仍存在
        assert "PATH" in kwargs["env"]

    def test_config_env_overrides_system_env(self, tmp_path: Path):
        """config.env 覆盖同名系统环境变量（config 优先级高）。"""
        cfg = CloneGuardConfig(env={"CUSTOM_VAR": "from_config"})
        adapter = EchoGuardAdapter(tmp_path, cfg)
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"findings": []}), stderr="")
        with patch.dict("os.environ", {"CUSTOM_VAR": "from_system"}, clear=False):
            with patch("subprocess.run", return_value=mock_result) as mock_run:
                adapter.detect(["src/foo.py"])
        _, kwargs = mock_run.call_args
        assert kwargs["env"]["CUSTOM_VAR"] == "from_config"  # config 覆盖系统


class TestEchoGuardAdapterScan:
    """scan 测试——L2 全量审计路径（无文件参数，全索引扫描）。

    守 L2 scan 改造（蓝图 §3.4 阶段2）：scan() 走 ``echo-guard scan`` 不传文件，
    规避 Windows CreateProcess 命令行长度上限。本类镜像 TestEchoGuardAdapterDetect
    的降级/解析覆盖，确保 scan 与 detect 行为同构（同 ERROR_CONTRACT + 同 _parse_findings）。
    """

    def test_echo_guard_disabled_returns_degraded(self, tmp_path: Path):
        """echo_guard_enabled=False 时 scan 返回空 + degraded=True（不调 CLI）。"""
        cfg = CloneGuardConfig(echo_guard_enabled=False)
        adapter = EchoGuardAdapter(tmp_path, cfg)
        with patch("subprocess.run") as mock_run:
            findings, degraded = adapter.scan()
        assert findings == []
        assert degraded is True
        mock_run.assert_not_called()  # 禁用时不触发 CLI

    def test_cli_not_found_degraded(self, tmp_path: Path):
        """CLI 未安装时 scan 降级（空列表 + degraded=True）。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        with patch("subprocess.run", side_effect=FileNotFoundError):
            findings, degraded = adapter.scan()
        assert findings == []
        assert degraded is True

    def test_cli_timeout_degraded(self, tmp_path: Path):
        """CLI 超时时 scan 降级。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="echo-guard", timeout=300)):
            findings, degraded = adapter.scan()
        assert findings == []
        assert degraded is True

    def test_no_index_exit_code_2_degraded(self, tmp_path: Path):
        """exit_code=2（索引不存在）时 scan 降级。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=2, stdout="", stderr="no index")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.scan()
        assert findings == []
        assert degraded is True

    def test_unknown_exit_code_degraded(self, tmp_path: Path):
        """未知退出码时 scan 降级。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=99, stdout="", stderr="unknown error")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.scan()
        assert findings == []
        assert degraded is True

    def test_json_decode_error_degraded(self, tmp_path: Path):
        """JSON 解析失败时 scan 降级。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0, stdout="not json{", stderr="")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.scan()
        assert findings == []
        assert degraded is True

    def test_no_findings_returns_empty(self, tmp_path: Path):
        """scan 正常执行但无克隆发现。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"findings": []}), stderr="")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.scan()
        assert findings == []
        assert degraded is False

    def test_match_finding_parsed(self, tmp_path: Path):
        """scan 的 type=match finding 正确解析为 Finding 对象。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        raw = {
            "findings": [
                {
                    "type": "match",
                    "finding_id": "F-001",
                    "severity": "extract",
                    "clone_type": "T2",
                    "similarity_score": 0.92,
                    "source": {"filepath": "src/new.py", "name": "calc", "lineno": 10},
                    "existing": {
                        "filepath": "src/old.py",
                        "name": "compute",
                        "lineno": 20,
                        "import_suggestion": "from src.old import compute",
                    },
                }
            ]
        }
        mock_result = MagicMock(returncode=1, stdout=json.dumps(raw), stderr="")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.scan()
        assert degraded is False
        assert len(findings) == 1
        f = findings[0]
        assert f.finding_id == "F-001"
        assert f.severity == "extract"
        assert f.clone_type == "T2"
        assert f.similarity == pytest.approx(0.92)
        assert f.source_file == "src/new.py"
        assert f.existing_file == "src/old.py"
        assert f.import_suggestion == "from src.old import compute"

    def test_group_finding_parsed(self, tmp_path: Path):
        """scan 的 type=group finding（多副本组）正确解析为多个 Finding。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        raw = {
            "findings": [
                {
                    "type": "group",
                    "finding_id": "G-001",
                    "severity": "extract",
                    "clone_type": "T3",
                    "similarity_score": 0.88,
                    "functions": [
                        {"filepath": "src/a.py", "name": "fn_a", "lineno": 5},
                        {"filepath": "src/b.py", "name": "fn_b", "lineno": 15},
                        {"filepath": "src/c.py", "name": "fn_c", "lineno": 25},
                    ],
                }
            ]
        }
        mock_result = MagicMock(returncode=1, stdout=json.dumps(raw), stderr="")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.scan()
        assert degraded is False
        assert len(findings) == 2  # 3 functions → 2 pairs (source vs each existing)
        assert findings[0].source_file == "src/a.py"
        assert findings[0].existing_file == "src/b.py"
        assert findings[1].existing_file == "src/c.py"

    def test_malformed_finding_skipped(self, tmp_path: Path):
        """scan 格式错误的 finding 被跳过（不抛异常）。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        raw = {
            "findings": [
                {"type": "match", "finding_id": "BAD"},  # 缺 source/existing
                {
                    "type": "match",
                    "finding_id": "GOOD",
                    "severity": "review",
                    "clone_type": "T1",
                    "similarity_score": 0.5,
                    "source": {"filepath": "a.py", "name": "f1", "lineno": 1},
                    "existing": {"filepath": "b.py", "name": "f2", "lineno": 2},
                },
            ]
        }
        mock_result = MagicMock(returncode=1, stdout=json.dumps(raw), stderr="")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.scan()
        assert degraded is False
        assert len(findings) == 1
        assert findings[0].finding_id == "GOOD"

    def test_scan_command_has_no_file_args(self, tmp_path: Path):
        """scan 命令仅 scan --output json，不含文件参数——规避命令行长度上限。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"findings": []}), stderr="")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            adapter.scan()
        args, _ = mock_run.call_args
        assert args[0] == ["echo-guard", "scan", "--output", "json"]

    def test_scan_uses_audit_timeout_by_default(self, tmp_path: Path):
        """scan 默认用 config.audit_timeout_sec（300s），非 L1 的 30s。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"findings": []}), stderr="")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            adapter.scan()
        _, kwargs = mock_run.call_args
        assert kwargs["timeout"] == 300  # audit_timeout_sec，而非 pre_commit_timeout_sec(30)

    def test_scan_explicit_timeout_respected(self, tmp_path: Path):
        """scan 显式 timeout 覆盖默认 audit_timeout_sec。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"findings": []}), stderr="")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            adapter.scan(timeout=120)
        _, kwargs = mock_run.call_args
        assert kwargs["timeout"] == 120

    def test_scan_injects_config_env(self, tmp_path: Path):
        """scan 调用 subprocess.run 时注入 config.env（L2 离线优先一致）。"""
        cfg = CloneGuardConfig(env={"HF_HUB_OFFLINE": "1"})
        adapter = EchoGuardAdapter(tmp_path, cfg)
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"findings": []}), stderr="")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            adapter.scan()
        mock_run.assert_called_once()
        _, kwargs = mock_run.call_args
        assert "env" in kwargs
        assert kwargs["env"]["HF_HUB_OFFLINE"] == "1"

    def test_scan_merges_system_env(self, tmp_path: Path):
        """scan 注入的 env 包含系统环境变量 + config.env（config 覆盖系统）。"""
        cfg = CloneGuardConfig(env={"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"})
        adapter = EchoGuardAdapter(tmp_path, cfg)
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"findings": []}), stderr="")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            adapter.scan()
        _, kwargs = mock_run.call_args
        assert "PATH" in kwargs["env"]  # 系统 env 保留
        assert kwargs["env"]["HF_HUB_OFFLINE"] == "1"
        assert kwargs["env"]["TRANSFORMERS_OFFLINE"] == "1"


class TestEchoGuardAdapterAcknowledge:
    """acknowledge CLI 路径测试——``acknowledge_via_cli=True`` 走 echo-guard CLI。

    镜像 detect/scan 的降级覆盖，确保 CLI 路径守 ERROR_CONTRACT：
    CLI 失败/超时/异常返回 (False, error)，不抛异常。
    默认路径（round-trip）见 TestEchoGuardAdapterAcknowledgeRoundTrip。
    """

    def test_echo_guard_disabled_returns_error(self, tmp_path: Path):
        """echo_guard_enabled=False 时返回 (False, error) 且不调 CLI/roundtrip。"""
        cfg = CloneGuardConfig(echo_guard_enabled=False, acknowledge_via_cli=True)
        adapter = EchoGuardAdapter(tmp_path, cfg)
        with patch("subprocess.run") as mock_run:
            success, error = adapter.acknowledge("F-001", "intentional", "合理重复")
        assert success is False
        assert error is not None
        mock_run.assert_not_called()  # 禁用时不触发 CLI

    def test_cli_not_found_returns_error(self, tmp_path: Path):
        """CLI 未安装时返回 (False, error)。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig(acknowledge_via_cli=True))
        with patch("subprocess.run", side_effect=FileNotFoundError):
            success, error = adapter.acknowledge("F-001", "intentional", "合理重复")
        assert success is False
        assert error is not None
        assert "未安装" in error

    def test_cli_timeout_returns_error(self, tmp_path: Path):
        """CLI 超时时返回 (False, error)。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig(acknowledge_via_cli=True))
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="echo-guard", timeout=30)):
            success, error = adapter.acknowledge("F-001", "intentional", "合理重复")
        assert success is False
        assert error is not None
        assert "超时" in error

    def test_generic_exception_returns_error(self, tmp_path: Path):
        """其他异常也返回 (False, error)，不抛出。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig(acknowledge_via_cli=True))
        with patch("subprocess.run", side_effect=OSError("boom")):
            success, error = adapter.acknowledge("F-001", "intentional", "合理重复")
        assert success is False
        assert error is not None

    def test_nonzero_exit_returns_error(self, tmp_path: Path):
        """CLI 非零退出码（finding_id 不存在等）返回 (False, error)。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig(acknowledge_via_cli=True))
        mock_result = MagicMock(returncode=1, stdout="", stderr="finding not found")
        with patch("subprocess.run", return_value=mock_result):
            success, error = adapter.acknowledge("F-NOPE", "intentional", "x")
        assert success is False
        assert error is not None
        assert "退出码=1" in error
        assert "finding not found" in error

    def test_zero_exit_returns_success(self, tmp_path: Path):
        """CLI 退出码 0 → (True, None)。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig(acknowledge_via_cli=True))
        mock_result = MagicMock(returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=mock_result):
            success, error = adapter.acknowledge("F-001", "dismissed", "非重复")
        assert success is True
        assert error is None

    def test_command_args_correct(self, tmp_path: Path):
        """acknowledge 命令含 finding_id/--verdict/--note 三个参数。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig(acknowledge_via_cli=True))
        mock_result = MagicMock(returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            adapter.acknowledge("F-001", "intentional", "两处实现均需保留")
        args, _ = mock_run.call_args
        assert args[0] == [
            "echo-guard",
            "acknowledge",
            "F-001",
            "--verdict",
            "intentional",
            "--note",
            "两处实现均需保留",
        ]

    def test_uses_pre_commit_timeout_by_default(self, tmp_path: Path):
        """acknowledge 默认用 config.pre_commit_timeout_sec（30s），非 L2 的 300s。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig(acknowledge_via_cli=True))
        mock_result = MagicMock(returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            adapter.acknowledge("F-001", "intentional", "x")
        _, kwargs = mock_run.call_args
        assert kwargs["timeout"] == 30  # pre_commit_timeout_sec，而非 audit_timeout_sec(300)

    def test_explicit_timeout_respected(self, tmp_path: Path):
        """显式 timeout 覆盖默认 pre_commit_timeout_sec。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig(acknowledge_via_cli=True))
        mock_result = MagicMock(returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            adapter.acknowledge("F-001", "intentional", "x", timeout=45)
        _, kwargs = mock_run.call_args
        assert kwargs["timeout"] == 45

    def test_injects_config_env(self, tmp_path: Path):
        """acknowledge 注入 config.env（与 detect/scan 一致）。"""
        cfg = CloneGuardConfig(env={"HF_HUB_OFFLINE": "1"}, acknowledge_via_cli=True)
        adapter = EchoGuardAdapter(tmp_path, cfg)
        mock_result = MagicMock(returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            adapter.acknowledge("F-001", "intentional", "x")
        _, kwargs = mock_run.call_args
        assert kwargs["env"]["HF_HUB_OFFLINE"] == "1"

    def test_merges_system_env(self, tmp_path: Path):
        """注入的 env 保留系统 PATH + config.env 覆盖。"""
        cfg = CloneGuardConfig(env={"HF_HUB_OFFLINE": "1"}, acknowledge_via_cli=True)
        adapter = EchoGuardAdapter(tmp_path, cfg)
        mock_result = MagicMock(returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            adapter.acknowledge("F-001", "intentional", "x")
        _, kwargs = mock_run.call_args
        assert "PATH" in kwargs["env"]
        assert kwargs["env"]["HF_HUB_OFFLINE"] == "1"

    def test_cwd_is_repo_root(self, tmp_path: Path):
        """acknowledge 在 repo_root 目录下执行（echo-guard.yml 在仓库根）。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig(acknowledge_via_cli=True))
        mock_result = MagicMock(returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            adapter.acknowledge("F-001", "intentional", "x")
        _, kwargs = mock_run.call_args
        assert kwargs["cwd"] == str(tmp_path)


# ---------------------------------------------------------------------------
# acknowledge 路由分流测试
# ---------------------------------------------------------------------------


class TestAcknowledgeRouting:
    """acknowledge 分流测试——acknowledge_via_cli 决定走 CLI 还是 round-trip。"""

    def test_default_routes_to_roundtrip_not_cli(self, tmp_path: Path):
        """默认 acknowledge_via_cli=False → 走 round-trip，不调 subprocess.run。"""
        yml = tmp_path / "echo-guard.yml"
        yml.write_text("min_function_lines: 3\nacknowledged: []\n", encoding="utf-8")
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())  # 默认 acknowledge_via_cli=False
        with patch("subprocess.run") as mock_run:
            success, _ = adapter.acknowledge("a.py:fn:h1||b.py:fn:h2", "intentional", "x")
        assert success is True
        mock_run.assert_not_called()  # round-trip 路径不调 CLI

    def test_cli_flag_routes_to_cli(self, tmp_path: Path):
        """acknowledge_via_cli=True → 走 CLI（调 subprocess.run）。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig(acknowledge_via_cli=True))
        mock_result = MagicMock(returncode=0, stdout="", stderr="")
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            adapter.acknowledge("F-001", "intentional", "x")
        mock_run.assert_called_once()  # CLI 路径调 subprocess


# ---------------------------------------------------------------------------
# acknowledge round-trip 路径测试（治本 #ARCH-ECHO-GUARD-YML-COMMENT-LOSS）
# ---------------------------------------------------------------------------


class TestEchoGuardAdapterAcknowledgeRoundTrip:
    """acknowledge 项目层 ruamel round-trip 路径测试——保留注释，治本注释丢失副作用。"""

    def test_roundtrip_preserves_comments(self, tmp_path: Path):
        """治本核心：round-trip 路径保留 echo-guard.yml 所有注释（顶部/手工/行内）。"""
        yml = tmp_path / "echo-guard.yml"
        yml.write_text(
            "# Echo Guard configuration\n"
            "# 重要手工注释——不应丢失\n"
            "min_function_lines: 3\n"
            "fail_on: extract  # 行内注释\n"
            "acknowledged: []\n",
            encoding="utf-8",
        )
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        success, error = adapter.acknowledge("a.py:fn:hash1||b.py:fn:hash2", "intentional", "测试")
        assert success is True, f"acknowledge 失败: {error}"
        content = yml.read_text(encoding="utf-8")
        assert "# Echo Guard configuration" in content  # 顶部注释保留
        assert "# 重要手工注释——不应丢失" in content  # 手工注释保留
        assert "# 行内注释" in content  # 行内注释保留

    def test_roundtrip_intentional_entry_format(self, tmp_path: Path):
        """intentional entry 含 id/verdict/source_hash(8)/existing_hash(8)。"""
        yml = tmp_path / "echo-guard.yml"
        yml.write_text("acknowledged: []\n", encoding="utf-8")
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        fid = "a.py:fn:abcdef1234||b.py:fn:fedcba9876"
        success, _ = adapter.acknowledge(fid, "intentional", "测试")
        assert success
        from ruamel.yaml import YAML

        data = YAML().load(yml.read_text(encoding="utf-8"))
        entry = data["acknowledged"][0]
        assert entry["id"] == fid
        assert entry["verdict"] == "intentional"
        assert entry["source_hash"] == "abcdef12"  # 前 8 字符
        assert entry["existing_hash"] == "fedcba98"

    def test_roundtrip_dismissed_entry_format(self, tmp_path: Path):
        """dismissed entry 含 id/verdict/stable_key。"""
        yml = tmp_path / "echo-guard.yml"
        yml.write_text("acknowledged: []\n", encoding="utf-8")
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        fid = "a.py:fn:h1||b.py:fn:h2"
        success, _ = adapter.acknowledge(fid, "dismissed", "非重复")
        assert success
        from ruamel.yaml import YAML

        data = YAML().load(yml.read_text(encoding="utf-8"))
        entry = data["acknowledged"][0]
        assert entry["id"] == fid
        assert entry["verdict"] == "dismissed"
        assert entry["stable_key"] == "a.py:fn||b.py:fn"  # 排序两侧去 hash

    def test_roundtrip_dedup_same_id(self, tmp_path: Path):
        """同 finding_id 二次 acknowledge 替换旧 entry，不重复。"""
        yml = tmp_path / "echo-guard.yml"
        yml.write_text("acknowledged: []\n", encoding="utf-8")
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        fid = "a.py:fn:h1||b.py:fn:h2"
        adapter.acknowledge(fid, "intentional", "第一次")
        adapter.acknowledge(fid, "dismissed", "第二次改主意")
        from ruamel.yaml import YAML

        data = YAML().load(yml.read_text(encoding="utf-8"))
        assert len(data["acknowledged"]) == 1  # 去重，非 2
        assert data["acknowledged"][0]["verdict"] == "dismissed"  # 后者覆盖

    def test_roundtrip_creates_acknowledged_section_if_absent(self, tmp_path: Path):
        """echo-guard.yml 无 acknowledged 段时自动创建。"""
        yml = tmp_path / "echo-guard.yml"
        yml.write_text("min_function_lines: 3\n", encoding="utf-8")  # 无 acknowledged
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        success, _ = adapter.acknowledge("a.py:fn:h1||b.py:fn:h2", "intentional", "x")
        assert success
        from ruamel.yaml import YAML

        data = YAML().load(yml.read_text(encoding="utf-8"))
        assert "acknowledged" in data
        assert len(data["acknowledged"]) == 1

    def test_roundtrip_yml_not_exists(self, tmp_path: Path):
        """echo-guard.yml 不存在 → (False, error)。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        success, error = adapter.acknowledge("F-001", "intentional", "x")
        assert success is False
        assert error is not None
        assert "echo-guard.yml 不存在" in error

    def test_roundtrip_ruamel_not_installed(self, tmp_path: Path):
        """ruamel.yaml 未安装 → (False, error)，不抛异常。"""
        yml = tmp_path / "echo-guard.yml"
        yml.write_text("acknowledged: []\n", encoding="utf-8")
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        with patch.dict("sys.modules", {"ruamel.yaml": None, "ruamel": None}):
            success, error = adapter.acknowledge("F-001", "intentional", "x")
        assert success is False
        assert error is not None
        assert "ruamel.yaml" in error

    def test_roundtrip_invalid_verdict_returns_error(self, tmp_path: Path):
        """非法 verdict → (False, error)，不写 yml。"""
        yml = tmp_path / "echo-guard.yml"
        yml.write_text("acknowledged: []\n", encoding="utf-8")
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        success, error = adapter.acknowledge("F-001", "maybe", "x")
        assert success is False
        assert error is not None
        assert "verdict" in error

    def test_roundtrip_compatible_with_echo_guard_load(self, tmp_path: Path):
        """兼容性核心：项目层写的 yml 能被 echo_guard.config.EchoGuardConfig 识别 + is_suppressed=True。"""
        from echo_guard.config import EchoGuardConfig as EGConfig

        yml = tmp_path / "echo-guard.yml"
        yml.write_text("min_function_lines: 3\nacknowledged: []\n", encoding="utf-8")
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        fid = "a.py:fn:abcdef12||b.py:fn:fedcba98"
        success, _ = adapter.acknowledge(fid, "intentional", "兼容性测试")
        assert success
        eg_cfg = EGConfig.load(str(tmp_path))  # echo-guard 自己的加载器
        assert eg_cfg.is_suppressed(fid, "abcdef12", "fedcba98") is True


# ---------------------------------------------------------------------------
# prune 测试（项目层 round-trip 接管）
# ---------------------------------------------------------------------------


class TestEchoGuardAdapterPrune:
    """prune 测试——移除 stale intentional entry，保留 dismissed，保留注释。"""

    def _write_yml_with_acknowledged(self, yml: Path) -> None:
        """写一个含注释 + acknowledged 段（1 stale intentional + 1 fresh intentional + 1 dismissed）的 yml。"""
        yml.write_text(
            "# Echo Guard 配置——注释应保留\n"
            "min_function_lines: 3\n"
            "acknowledged:\n"
            "  - id: stale.py:fn:oldhash||other.py:fn:oldhash\n"
            "    verdict: intentional\n"
            "    source_hash: oldhash\n"
            "    existing_hash: oldhash\n"
            "  - id: fresh.py:fn:newhash||other.py:fn:newhash\n"
            "    verdict: intentional\n"
            "    source_hash: newhash\n"
            "    existing_hash: newhash\n"
            "  - id: dismissed.py:fn:h1||other.py:fn:h2\n"
            "    verdict: dismissed\n"
            "    stable_key: dismissed.py:fn||other.py:fn\n",
            encoding="utf-8",
        )

    def test_prune_removes_stale_intentional(self, tmp_path: Path):
        """stale intentional entry（id 不在 scan 结果）被移除。"""
        yml = tmp_path / "echo-guard.yml"
        self._write_yml_with_acknowledged(yml)
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        # scan 结果只含 fresh（stale 不在）
        scan_ids = {"fresh.py:fn:newhash||other.py:fn:newhash"}
        success, error, removed = adapter.prune(scan_finding_ids=scan_ids)
        assert success, f"prune 失败: {error}"
        assert removed == 1  # stale 被移除
        from ruamel.yaml import YAML

        data = YAML().load(yml.read_text(encoding="utf-8"))
        ids = [e["id"] for e in data["acknowledged"]]
        assert "stale.py:fn:oldhash||other.py:fn:oldhash" not in ids  # stale 移除
        assert "fresh.py:fn:newhash||other.py:fn:newhash" in ids  # fresh 保留

    def test_prune_preserves_dismissed(self, tmp_path: Path):
        """dismissed entry 保留（不因 id 不在 scan 结果而移除）。"""
        yml = tmp_path / "echo-guard.yml"
        self._write_yml_with_acknowledged(yml)
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        scan_ids: set[str] = set()  # 空 scan——所有 intentional stale
        success, _, removed = adapter.prune(scan_finding_ids=scan_ids)
        assert success
        from ruamel.yaml import YAML

        data = YAML().load(yml.read_text(encoding="utf-8"))
        ids = [e["id"] for e in data["acknowledged"]]
        assert "dismissed.py:fn:h1||other.py:fn:h2" in ids  # dismissed 保留
        assert removed == 2  # 2 个 intentional 都 stale，dismissed 不计

    def test_prune_preserves_comments(self, tmp_path: Path):
        """prune 后 echo-guard.yml 注释保留（治本验证）。"""
        yml = tmp_path / "echo-guard.yml"
        self._write_yml_with_acknowledged(yml)
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        adapter.prune(scan_finding_ids=set())
        content = yml.read_text(encoding="utf-8")
        assert "# Echo Guard 配置——注释应保留" in content

    def test_prune_no_acknowledged_returns_zero(self, tmp_path: Path):
        """无 acknowledged 段 → (True, None, 0)。"""
        yml = tmp_path / "echo-guard.yml"
        yml.write_text("min_function_lines: 3\n", encoding="utf-8")
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        success, error, removed = adapter.prune(scan_finding_ids=set())
        assert success
        assert error is None
        assert removed == 0

    def test_prune_explicit_scan_ids_skips_scan_call(self, tmp_path: Path):
        """传入 scan_finding_ids 时不调 self.scan()。"""
        yml = tmp_path / "echo-guard.yml"
        yml.write_text("acknowledged: []\n", encoding="utf-8")
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        with patch.object(adapter, "scan") as mock_scan:
            adapter.prune(scan_finding_ids={"F-001"})
        mock_scan.assert_not_called()  # 显式传 ids 不调 scan

    def test_prune_scan_degraded_returns_error(self, tmp_path: Path):
        """scan 降级（degraded=True）→ (False, error, 0)。"""
        yml = tmp_path / "echo-guard.yml"
        yml.write_text("acknowledged: []\n", encoding="utf-8")
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        with patch.object(adapter, "scan", return_value=([], True)):
            success, error, removed = adapter.prune()  # 不传 ids，触发自 scan
        assert success is False
        assert removed == 0
        assert "scan 降级" in error

    def test_prune_echo_guard_disabled(self, tmp_path: Path):
        """echo_guard_enabled=False → (False, error, 0)。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig(echo_guard_enabled=False))
        success, error, removed = adapter.prune(scan_finding_ids=set())
        assert success is False
        assert removed == 0


# ---------------------------------------------------------------------------
# _embedding_lock 跨进程文件锁测试（OOB 治本 P2 #ARCH-ECHO-GUARD-EMBEDDING-OOB）
# ---------------------------------------------------------------------------


class TestEmbeddingLockSerialization:
    """_embedding_lock 跨进程文件锁测试——OOB 治本（P2 #ARCH-ECHO-GUARD-EMBEDDING-OOB）。

    验证三个不变量：
    - 锁正常获取 → CLI 在锁内执行（序列化），锁文件路径/超时正确
    - 锁超时 → degraded（不执行 CLI，防无锁竞态 OOB）
    - filelock 未安装/锁目录不可写 → fail-open（无锁执行，守 _GlobalCommitLock 先例）
    - subprocess 异常时锁仍释放（finally 块）
    - health_check 不加锁（--version 不触碰 EmbeddingStore）
    """

    def test_detect_acquires_lock_with_correct_path_and_timeout(self, tmp_path: Path):
        """detect 用 .ailocks/echo_guard_embedding.lock（60s 超时）序列化 CLI 调用。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"findings": []}), stderr="")
        with patch("filelock.FileLock") as mock_filelock_cls:
            mock_lock = MagicMock()
            mock_filelock_cls.return_value = mock_lock
            with patch("subprocess.run", return_value=mock_result):
                adapter.detect(["src/foo.py"])
        mock_filelock_cls.assert_called_once()
        args, kwargs = mock_filelock_cls.call_args
        assert "echo_guard_embedding.lock" in args[0]
        assert ".ailocks" in args[0]
        assert kwargs["timeout"] == 60.0
        mock_lock.acquire.assert_called_once()
        mock_lock.release.assert_called_once()

    def test_detect_lock_timeout_degraded(self, tmp_path: Path):
        """锁超时 → detect 降级（[], True），不执行 CLI（防无锁竞态 OOB）。"""
        from filelock import Timeout

        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        with patch("filelock.FileLock") as mock_filelock_cls:
            mock_lock = MagicMock()
            mock_lock.acquire.side_effect = Timeout("lock busy")
            mock_filelock_cls.return_value = mock_lock
            with patch("subprocess.run") as mock_run:
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True
        mock_run.assert_not_called()  # 锁超时不执行 CLI

    def test_scan_lock_timeout_degraded(self, tmp_path: Path):
        """锁超时 → scan 降级（[], True），不执行 CLI。"""
        from filelock import Timeout

        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        with patch("filelock.FileLock") as mock_filelock_cls:
            mock_lock = MagicMock()
            mock_lock.acquire.side_effect = Timeout("lock busy")
            mock_filelock_cls.return_value = mock_lock
            with patch("subprocess.run") as mock_run:
                findings, degraded = adapter.scan()
        assert findings == []
        assert degraded is True
        mock_run.assert_not_called()

    def test_acknowledge_cli_lock_timeout_returns_error(self, tmp_path: Path):
        """锁超时 → acknowledge(CLI) 返回 (False, error)，不执行 CLI。"""
        from filelock import Timeout

        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig(acknowledge_via_cli=True))
        with patch("filelock.FileLock") as mock_filelock_cls:
            mock_lock = MagicMock()
            mock_lock.acquire.side_effect = Timeout("lock busy")
            mock_filelock_cls.return_value = mock_lock
            with patch("subprocess.run") as mock_run:
                success, error = adapter.acknowledge("F-001", "intentional", "x")
        assert success is False
        assert error is not None
        assert "锁超时" in error
        mock_run.assert_not_called()

    def test_detect_filelock_missing_fail_open(self, tmp_path: Path):
        """filelock 未安装 → fail-open（无锁执行 CLI，正常返回 degraded=False）。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"findings": []}), stderr="")
        with patch.dict("sys.modules", {"filelock": None}):
            with patch("subprocess.run", return_value=mock_result) as mock_run:
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is False  # fail-open 正常执行
        mock_run.assert_called_once()

    def test_scan_filelock_missing_fail_open(self, tmp_path: Path):
        """filelock 未安装 → scan fail-open（无锁执行，正常返回）。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"findings": []}), stderr="")
        with patch.dict("sys.modules", {"filelock": None}):
            with patch("subprocess.run", return_value=mock_result) as mock_run:
                findings, degraded = adapter.scan()
        assert degraded is False
        mock_run.assert_called_once()

    def test_detect_lock_dir_not_writable_fail_open(self, tmp_path: Path):
        """锁目录不可写 → fail-open（无锁执行 CLI，正常返回 degraded=False）。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"findings": []}), stderr="")
        with patch("pathlib.Path.mkdir", side_effect=OSError("permission denied")):
            with patch("subprocess.run", return_value=mock_result) as mock_run:
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is False  # fail-open 正常执行
        mock_run.assert_called_once()

    def test_lock_released_on_subprocess_exception(self, tmp_path: Path):
        """subprocess.run 抛异常时锁仍被释放（finally 块，防死锁）。"""
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        with patch("filelock.FileLock") as mock_filelock_cls:
            mock_lock = MagicMock()
            mock_filelock_cls.return_value = mock_lock
            with patch("subprocess.run", side_effect=FileNotFoundError):
                adapter.detect(["src/foo.py"])
        mock_lock.acquire.assert_called_once()
        mock_lock.release.assert_called_once()  # 异常后锁仍释放

    def test_health_check_does_not_acquire_lock(self, tmp_path: Path):
        """health_check（--version）不触碰 EmbeddingStore，不获取 embedding 锁。"""
        (tmp_path / ".echo-guard").mkdir(parents=True)
        (tmp_path / ".echo-guard" / "index.duckdb").touch()
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        mock_result = MagicMock(returncode=0)
        with patch("filelock.FileLock") as mock_filelock_cls:
            with patch("subprocess.run", return_value=mock_result):
                adapter.health_check()
        mock_filelock_cls.assert_not_called()  # health_check 不加锁


# ---------------------------------------------------------------------------
# _make_stable_key / _parse_finding_id_hashes 单元测试
# ---------------------------------------------------------------------------


class TestStableKeyAndHashParsing:
    """_make_stable_key + _parse_finding_id_hashes 单元测试（复现 echo-guard 逻辑）。"""

    def test_make_stable_key_normal(self):
        """标准 finding_id → 排序两侧 filepath:name，|| 连接。"""
        fid = "a.py:func:hash1||b.py:func:hash2"
        assert EchoGuardAdapter._make_stable_key(fid) == "a.py:func||b.py:func"

    def test_make_stable_key_order_independent(self):
        """两侧顺序无关——source/existing 互换产生相同 key。"""
        fid1 = "a.py:func:h1||b.py:func:h2"
        fid2 = "b.py:func:h2||a.py:func:h1"
        assert EchoGuardAdapter._make_stable_key(fid1) == EchoGuardAdapter._make_stable_key(fid2)

    def test_make_stable_key_single_side(self):
        """无 || 分隔 → 返回原值（容错）。"""
        fid = "a.py:func:hash1"
        assert EchoGuardAdapter._make_stable_key(fid) == fid

    def test_parse_hashes_normal(self):
        """标准 finding_id → (source_hash, existing_hash)。"""
        fid = "a.py:fn:abcdef12||b.py:fn:fedcba98"
        src, ext = EchoGuardAdapter._parse_finding_id_hashes(fid)
        assert src == "abcdef12"
        assert ext == "fedcba98"

    def test_parse_hashes_single_side(self):
        """无 || 分隔 → ("", "")（容错）。"""
        src, ext = EchoGuardAdapter._parse_finding_id_hashes("a.py:fn:hash1")
        assert src == ""
        assert ext == ""

    def test_matches_echo_guard_make_stable_key(self):
        """与 echo_guard.config.EchoGuardConfig.make_stable_key 输出一致（兼容性）。"""
        from echo_guard.config import EchoGuardConfig as EGConfig

        fid = "x.py:f:h1||y.py:g:h2"
        assert EchoGuardAdapter._make_stable_key(fid) == EGConfig.make_stable_key(fid)


# ---------------------------------------------------------------------------
# 平凡访问器族过滤测试（治本 AI-GOVFIX-ECHO-001）
# ---------------------------------------------------------------------------


class TestTrivialAccessorFilter:
    """平凡访问器族过滤测试——extract 级假阳性族引擎级治本（AI-GOVFIX-ECHO-001）。

    根因（实证）：
    - echo-guard 行数口径 = tree-sitter function_definition 跨度（def→末行，
      含 docstring、不含 decorator）——``@property+def+docstring+return`` = 3 行
      恰过 min_function_lines=3 入库；
    - Tier-1 归一化 AST 哈希对 ``return self._X`` 模板 100% 撞车（Type-2 口径）；
    - echo-guard ``_is_trivial_function`` 按物理行计 body，docstring 被计入，
      带注释单行访问器逃逸"单语句体=平凡"抑制 → 3+ 副本聚组 = extract 硬阻断
      （实证 agent_id/traces/links/core_writer/initial_capital 五 hub 82+ 对全假阳性）。

    治本：适配器 AST 层重判——函数体剥 docstring 后 ≤1 条语句 = 平凡访问器
    （getter/setter/单行表达式同族），source/existing 两侧皆平凡则剔除 finding；
    判定失败（文件缺失/解析失败/定位失败/歧义）一律保守保留；
    多语句函数（真克隆检测面）不受影响。
    """

    # ── fixture 文件内容（def 行号必须与 finding JSON 的 lineno 一致）──
    _GETTER_A = (
        "class Lock:\n"
        "    @property\n"
        "    def agent_id(self) -> str:\n"  # def = line 3
        '        """agent_id implementation."""\n'
        "        return self._agent_id\n"
    )
    _GETTER_B = (
        "class Tracker:\n"
        "    @property\n"
        "    def traces(self):\n"  # def = line 3
        '        """只读：traces。"""\n'
        "        return self._traces\n"
    )
    _GETTER_C = (
        "class Ctx:\n"
        "    @property\n"
        "    def links(self):\n"  # def = line 3
        '        """只读：links。"""\n'
        "        return self._links\n"
    )
    _GETTER_D = (
        "class Exec:\n"
        "    @property\n"
        "    def core_writer(self):\n"  # def = line 3
        '        """只读：core_writer。"""\n'
        "        return self._core_writer\n"
    )
    _GETTER_E = (
        "class Portfolio:\n"
        "    @property\n"
        "    def initial_capital(self):\n"  # def = line 3
        '        """初始资金"""\n'
        "        return self._initial_capital\n"
    )
    _SETTER_A = (
        "class Writer:\n"
        "    @core_writer.setter\n"
        "    def core_writer(self, value):\n"  # def = line 3
        '        """写入：core_writer。"""\n'
        "        self._core_writer = value\n"
    )
    _SETTER_B = (
        "class Store:\n"
        "    @storage_dir.setter\n"
        "    def storage_dir(self, value):\n"  # def = line 3
        '        """写入：storage_dir。"""\n'
        "        self._storage_dir = value\n"
    )
    _MULTILINE_DOC_GETTER = (
        "class Cfg:\n"
        "    @property\n"
        "    def base_dir(self):\n"  # def = line 3
        '        """只读：base_dir。\n'
        "\n"
        "        多行注释压测——docstring 跨行不影響语句计数。\n"
        '        """\n'
        "        return self._base_dir\n"
    )
    _REAL_A = (
        "def compute_total(items):\n"  # def = line 1
        '    """合计正值。"""\n'
        "    total = 0\n"
        "    for it in items:\n"
        "        if it > 0:\n"
        "            total += it\n"
        "    return total\n"
    )
    _REAL_B = (
        "def sum_positive(values):\n"  # def = line 1
        '    """合计正值。"""\n'
        "    result = 0\n"
        "    for v in values:\n"
        "        if v > 0:\n"
        "            result += v\n"
        "    return result\n"
    )
    _AMBIGUOUS = (
        "class Dual:\n"
        "    @property\n"
        "    def traces(self):\n"  # def = line 3
        "        return self._traces\n"
        "    @traces.setter\n"
        "    def traces(self, value):\n"  # def = line 6（同名第二定义）
        "        self._traces = value\n"
    )

    def _write(self, repo: Path, name: str, content: str) -> None:
        (repo / name).write_text(content, encoding="utf-8")

    def _seed_repo(self, repo: Path) -> None:
        """写入全部 fixture 文件。"""
        for name, content in {
            "alpha.py": self._GETTER_A,
            "beta.py": self._GETTER_B,
            "zeta.py": self._GETTER_C,
            "eta.py": self._GETTER_D,
            "theta.py": self._GETTER_E,
            "gamma.py": self._SETTER_A,
            "sigma.py": self._SETTER_B,
            "omega.py": self._MULTILINE_DOC_GETTER,
            "delta.py": self._REAL_A,
            "epsilon.py": self._REAL_B,
            "ambiguous.py": self._AMBIGUOUS,
        }.items():
            self._write(repo, name, content)

    @staticmethod
    def _match_raw(src: tuple[str, str, int], ext: tuple[str, str, int], severity: str = "extract") -> dict:
        """构造 type=match 的 echo-guard JSON。tuple=(filepath, name, lineno)。"""
        return {
            "findings": [
                {
                    "type": "match",
                    "finding_id": "F-T1",
                    "severity": severity,
                    "clone_type": "T2",
                    "similarity_score": 1.0,
                    "source": {"filepath": src[0], "name": src[1], "lineno": src[2]},
                    "existing": {"filepath": ext[0], "name": ext[1], "lineno": ext[2]},
                }
            ]
        }

    def _detect(self, adapter: EchoGuardAdapter, raw: dict, files: list[str]):
        mock_result = MagicMock(returncode=1, stdout=json.dumps(raw), stderr="")
        with patch("subprocess.run", return_value=mock_result):
            return adapter.detect(files)

    # ── 假阳性族清零（五 hub 锁定）──

    def test_trivial_getter_pair_dropped(self, tmp_path: Path):
        """带 docstring 的单 return @property 对（agent_id↔traces 形态）被剔除。"""
        self._seed_repo(tmp_path)
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        raw = self._match_raw(("alpha.py", "agent_id", 3), ("beta.py", "traces", 3))
        findings, degraded = self._detect(adapter, raw, ["alpha.py"])
        assert degraded is False
        assert findings == []

    def test_five_hub_group_dropped(self, tmp_path: Path):
        """五 hub 形态（agent_id/traces/links/core_writer/initial_capital）extract 组全灭。"""
        self._seed_repo(tmp_path)
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        raw = {
            "findings": [
                {
                    "type": "group",
                    "finding_id": "G-HUB",
                    "severity": "extract",
                    "clone_type": "T2",
                    "similarity_score": 1.0,
                    "functions": [
                        {"filepath": "alpha.py", "name": "agent_id", "lineno": 3},
                        {"filepath": "beta.py", "name": "traces", "lineno": 3},
                        {"filepath": "zeta.py", "name": "links", "lineno": 3},
                        {"filepath": "eta.py", "name": "core_writer", "lineno": 3},
                        {"filepath": "theta.py", "name": "initial_capital", "lineno": 3},
                    ],
                }
            ]
        }
        findings, degraded = self._detect(adapter, raw, ["alpha.py"])
        assert degraded is False
        assert findings == []

    def test_trivial_setter_pair_dropped(self, tmp_path: Path):
        """setter 族（docstring + 单赋值语句）同族剔除——min=3 回退后不复发。"""
        self._seed_repo(tmp_path)
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        raw = self._match_raw(("gamma.py", "core_writer", 3), ("sigma.py", "storage_dir", 3))
        findings, degraded = self._detect(adapter, raw, ["gamma.py"])
        assert degraded is False
        assert findings == []

    def test_multiline_docstring_accessor_dropped(self, tmp_path: Path):
        """多行 docstring 的单 return 访问器仍判平凡（语句计数≠物理行计数）。"""
        self._seed_repo(tmp_path)
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        raw = self._match_raw(("omega.py", "base_dir", 3), ("beta.py", "traces", 3))
        findings, degraded = self._detect(adapter, raw, ["omega.py"])
        assert degraded is False
        assert findings == []

    def test_review_severity_pair_also_dropped(self, tmp_path: Path):
        """review 级平凡对同样剔除（过滤与 severity 无关——噪声在任何级别都是噪声）。"""
        self._seed_repo(tmp_path)
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        raw = self._match_raw(("alpha.py", "agent_id", 3), ("beta.py", "traces", 3), severity="review")
        findings, degraded = self._detect(adapter, raw, ["alpha.py"])
        assert degraded is False
        assert findings == []

    def test_scan_path_also_filters(self, tmp_path: Path):
        """scan()（L2 审计）与 detect() 共用过滤漏斗。"""
        self._seed_repo(tmp_path)
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        raw = self._match_raw(("alpha.py", "agent_id", 3), ("beta.py", "traces", 3))
        mock_result = MagicMock(returncode=1, stdout=json.dumps(raw), stderr="")
        with patch("subprocess.run", return_value=mock_result):
            findings, degraded = adapter.scan()
        assert degraded is False
        assert findings == []

    # ── 真克隆检测面不动 ──

    def test_real_clone_pair_kept(self, tmp_path: Path):
        """≥6 行多语句实质重复对（重命名 Type-2）仍保留——extract 阻断面不受影响。"""
        self._seed_repo(tmp_path)
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        raw = self._match_raw(("delta.py", "compute_total", 1), ("epsilon.py", "sum_positive", 1))
        findings, degraded = self._detect(adapter, raw, ["delta.py"])
        assert degraded is False
        assert len(findings) == 1
        assert findings[0].severity == "extract"
        assert findings[0].source_function == "compute_total"

    def test_trivial_vs_real_kept(self, tmp_path: Path):
        """一侧平凡、一侧多语句 → 保守保留（两侧皆平凡才剔除）。"""
        self._seed_repo(tmp_path)
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        raw = self._match_raw(("alpha.py", "agent_id", 3), ("delta.py", "compute_total", 1))
        findings, degraded = self._detect(adapter, raw, ["alpha.py"])
        assert degraded is False
        assert len(findings) == 1

    def test_missing_file_side_kept(self, tmp_path: Path):
        """一侧文件缺失（无法 AST 判定）→ 保守保留。"""
        self._seed_repo(tmp_path)
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        raw = self._match_raw(("alpha.py", "agent_id", 3), ("ghost.py", "traces", 3))
        findings, degraded = self._detect(adapter, raw, ["alpha.py"])
        assert degraded is False
        assert len(findings) == 1

    def test_lineno_shift_unique_name_still_dropped(self, tmp_path: Path):
        """索引后文件被编辑致 lineno 偏移：唯一函数名回退定位仍正确剔除。"""
        self._seed_repo(tmp_path)
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        raw = self._match_raw(("alpha.py", "agent_id", 99), ("beta.py", "traces", 3))
        findings, degraded = self._detect(adapter, raw, ["alpha.py"])
        assert degraded is False
        assert findings == []

    def test_ambiguous_name_lineno_miss_kept(self, tmp_path: Path):
        """同名多定义（property+setter）且 lineno 未命中 → 歧义保守保留。"""
        self._seed_repo(tmp_path)
        adapter = EchoGuardAdapter(tmp_path, CloneGuardConfig())
        raw = self._match_raw(("ambiguous.py", "traces", 999), ("beta.py", "traces", 3))
        findings, degraded = self._detect(adapter, raw, ["ambiguous.py"])
        assert degraded is False
        assert len(findings) == 1
