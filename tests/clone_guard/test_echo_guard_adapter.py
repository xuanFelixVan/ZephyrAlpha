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
