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
