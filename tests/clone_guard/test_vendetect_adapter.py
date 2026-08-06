# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] tests.clone_guard.test_vendetect_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/clone_guard/test_vendetect_adapter.py
# [A_test] module_id: MOD-CLONE_GUARD | layer=test | stability=volatile | safety=L | ai_modifiable
# [TTL] permanent
"""VendetectAdapter 单元测试——mock subprocess 调用，不依赖真实 Vendetect CLI。"""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.vendetect_adapter import VendetectAdapter


def _make_vendored(similarity=0.97, license="AGPL-3.0", local_file="src/new.py",
                   local_function="calc", local_line=10, remote_file="vendor/lib.py",
                   remote_function="compute", remote_line=20, remote_url="https://github.com/x/y"):
    return {"local_file": local_file, "local_function": local_function, "local_line": local_line,
            "remote_file": remote_file, "remote_function": remote_function, "remote_line": remote_line,
            "similarity": similarity, "license": license, "remote_url": remote_url}


class TestVendetectAdapterHealthCheck:
    """health_check 测试。"""

    def test_cli_missing_returns_false(self, tmp_path: Path):
        """Vendetect CLI 未安装时返回 False。"""
        adapter = VendetectAdapter(tmp_path, CloneGuardConfig(vendetect_remote_url="https://github.com/example/repo"))
        with patch("shutil.which", return_value=None):
            assert adapter.health_check() is False

    def test_cli_present_no_remote_returns_false(self, tmp_path: Path):
        """CLI 存在但未配 remote_url 时返回 False。"""
        adapter = VendetectAdapter(tmp_path, CloneGuardConfig())  # vendetect_remote_url=None
        with patch("shutil.which", return_value="/fake/vendetect"):
            assert adapter.health_check() is False

    def test_cli_and_remote_present_returns_true(self, tmp_path: Path):
        """CLI 存在且已配 remote_url 时返回 True。"""
        adapter = VendetectAdapter(tmp_path, CloneGuardConfig(vendetect_remote_url="https://github.com/example/repo"))
        with patch("shutil.which", return_value="/fake/vendetect"):
            assert adapter.health_check() is True


class TestVendetectAdapterDetect:
    """detect 测试——覆盖降级路径和正常路径。"""

    def test_empty_files(self, tmp_path: Path):
        """空文件列表直接返回（不调用 CLI）。"""
        adapter = VendetectAdapter(tmp_path, CloneGuardConfig())
        findings, degraded = adapter.detect([])
        assert findings == []
        assert degraded is False

    def test_disabled_in_config(self, tmp_path: Path):
        """vendetect_enabled=False 时降级。"""
        adapter = VendetectAdapter(tmp_path, CloneGuardConfig(vendetect_enabled=False))
        findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_cli_not_found_degraded(self, tmp_path: Path):
        """CLI 未安装时降级。"""
        cfg = CloneGuardConfig(vendetect_enabled=True, vendetect_remote_url="https://github.com/example/repo")
        adapter = VendetectAdapter(tmp_path, cfg)
        with patch("shutil.which", return_value=None):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_no_remote_url_degraded(self, tmp_path: Path):
        """已启用但未配 remote_url 时降级。"""
        cfg = CloneGuardConfig(vendetect_enabled=True)  # vendetect_remote_url=None
        adapter = VendetectAdapter(tmp_path, cfg)
        with patch("shutil.which", return_value="/fake/vendetect"):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_timeout_degraded(self, tmp_path: Path):
        """CLI 超时时降级。"""
        cfg = CloneGuardConfig(vendetect_enabled=True, vendetect_remote_url="https://github.com/example/repo")
        adapter = VendetectAdapter(tmp_path, cfg)
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="vendetect", timeout=600)):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_generic_exception_degraded(self, tmp_path: Path):
        """subprocess.run 抛非预期异常时降级。"""
        cfg = CloneGuardConfig(vendetect_enabled=True, vendetect_remote_url="https://github.com/example/repo")
        adapter = VendetectAdapter(tmp_path, cfg)
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", side_effect=OSError("boom")):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_bad_exit_code_degraded(self, tmp_path: Path):
        """退出码非 0/1 时降级。"""
        cfg = CloneGuardConfig(vendetect_enabled=True, vendetect_remote_url="https://github.com/example/repo")
        adapter = VendetectAdapter(tmp_path, cfg)
        mock_result = MagicMock(returncode=2, stdout="", stderr="error")
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_json_decode_error_degraded(self, tmp_path: Path):
        """JSON 解析失败时降级。"""
        cfg = CloneGuardConfig(vendetect_enabled=True, vendetect_remote_url="https://github.com/example/repo")
        adapter = VendetectAdapter(tmp_path, cfg)
        mock_result = MagicMock(returncode=0, stdout="not json{", stderr="")
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_no_vendored_returns_empty(self, tmp_path: Path):
        """正常执行但无发现（exit 0）。"""
        cfg = CloneGuardConfig(vendetect_enabled=True, vendetect_remote_url="https://github.com/example/repo")
        adapter = VendetectAdapter(tmp_path, cfg)
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"vendored": []}), stderr="")
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is False

    def test_vendored_parsed_to_finding(self, tmp_path: Path):
        """正常 vendored 正确解析为 Finding。"""
        cfg = CloneGuardConfig(vendetect_enabled=True, vendetect_remote_url="https://github.com/example/repo")
        adapter = VendetectAdapter(tmp_path, cfg)
        data = {"vendored": [_make_vendored(similarity=0.97, license="AGPL-3.0")]}
        mock_result = MagicMock(returncode=1, stdout=json.dumps(data), stderr="")
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", return_value=mock_result):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert degraded is False
        assert len(findings) == 1
        f = findings[0]
        assert f.severity == "extract"  # AGPL + sim>=0.95 → extract
        assert f.clone_type == "vendored"
        assert f.similarity == 0.97
        assert f.source_file == "src/new.py"
        assert f.source_function == "calc"
        assert f.source_lineno == 10
        assert f.existing_file == "vendor/lib.py"
        assert f.existing_function == "compute"
        assert f.existing_lineno == 20
        assert f.import_suggestion == "https://github.com/x/y"
        assert f.finding_id == "VD-0-src/new.py-vendor/lib.py"

    def test_agpl_license_extract(self, tmp_path: Path):
        """AGPL + sim>=0.95 → extract（合规硬阻断）。"""
        cfg = CloneGuardConfig(vendetect_enabled=True, vendetect_remote_url="https://github.com/example/repo")
        adapter = VendetectAdapter(tmp_path, cfg)
        data = {"vendored": [_make_vendored(similarity=0.99, license="AGPL-3.0")]}
        mock_result = MagicMock(returncode=1, stdout=json.dumps(data), stderr="")
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", return_value=mock_result):
                findings, _ = adapter.detect(["src/foo.py"])
        assert findings[0].severity == "extract"

    def test_compatible_license_review(self, tmp_path: Path):
        """MIT + sim>=0.95 → review（兼容许可但需 attribution）。"""
        cfg = CloneGuardConfig(vendetect_enabled=True, vendetect_remote_url="https://github.com/example/repo")
        adapter = VendetectAdapter(tmp_path, cfg)
        data = {"vendored": [_make_vendored(similarity=0.96, license="MIT")]}
        mock_result = MagicMock(returncode=1, stdout=json.dumps(data), stderr="")
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", return_value=mock_result):
                findings, _ = adapter.detect(["src/foo.py"])
        assert findings[0].severity == "review"

    def test_low_similarity_acknowledged(self, tmp_path: Path):
        """低相似度 → acknowledged。"""
        cfg = CloneGuardConfig(vendetect_enabled=True, vendetect_remote_url="https://github.com/example/repo")
        adapter = VendetectAdapter(tmp_path, cfg)
        data = {"vendored": [_make_vendored(similarity=0.5, license="MIT")]}
        mock_result = MagicMock(returncode=1, stdout=json.dumps(data), stderr="")
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", return_value=mock_result):
                findings, _ = adapter.detect(["src/foo.py"])
        assert findings[0].severity == "acknowledged"

    def test_env_injected(self, tmp_path: Path):
        """detect 调用 subprocess.run 时注入 config.env。"""
        cfg = CloneGuardConfig(
            vendetect_enabled=True,
            vendetect_remote_url="https://github.com/example/repo",
            env={"CUSTOM_VAR": "1"},
        )
        adapter = VendetectAdapter(tmp_path, cfg)
        mock_result = MagicMock(returncode=0, stdout=json.dumps({"vendored": []}), stderr="")
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", return_value=mock_result) as mock_run:
                adapter.detect(["src/foo.py"])
        _, kwargs = mock_run.call_args
        assert kwargs["env"]["CUSTOM_VAR"] == "1"

    def test_absolute_path_converted_to_relative(self, tmp_path: Path):
        """local_file 绝对路径转为相对仓库根目录（remote_file 保持原样）。"""
        cfg = CloneGuardConfig(vendetect_enabled=True, vendetect_remote_url="https://github.com/example/repo")
        adapter = VendetectAdapter(tmp_path, cfg)
        abs_local = str(tmp_path / "src" / "new.py")
        v = _make_vendored(local_file=abs_local, remote_file="vendor/lib.py")
        mock_result = MagicMock(returncode=1, stdout=json.dumps({"vendored": [v]}), stderr="")
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", return_value=mock_result):
                findings, _ = adapter.detect(["src/new.py"])
        assert findings[0].source_file == "src/new.py"
        assert findings[0].existing_file == "vendor/lib.py"  # 远程文件保持原样


class TestVendetectSeverityMapping:
    """_severity_for 合规 severity 判定测试。"""

    def test_agpl_hard_block(self):
        """AGPL-3.0 + sim>=0.95 → extract。"""
        assert VendetectAdapter._severity_for("AGPL-3.0", 0.95) == "extract"
        assert VendetectAdapter._severity_for("AGPL-3.0", 0.99) == "extract"

    def test_unknown_license_hard_block(self):
        """Unknown/空许可证 + sim>=0.95 → extract。"""
        assert VendetectAdapter._severity_for("Unknown", 0.97) == "extract"
        assert VendetectAdapter._severity_for("unknown", 0.97) == "extract"
        assert VendetectAdapter._severity_for("", 0.97) == "extract"

    def test_gpl_hard_block(self):
        """GPL-3.0 + sim>=0.95 → extract。"""
        assert VendetectAdapter._severity_for("GPL-3.0", 0.95) == "extract"
        assert VendetectAdapter._severity_for("GPL-3.0-only", 0.98) == "extract"

    def test_mit_high_sim_review(self):
        """MIT（兼容许可） + sim>=0.95 → review。"""
        assert VendetectAdapter._severity_for("MIT", 0.95) == "review"
        assert VendetectAdapter._severity_for("MIT", 0.99) == "review"

    def test_low_sim_acknowledged(self):
        """低相似度 → acknowledged。"""
        assert VendetectAdapter._severity_for("AGPL-3.0", 0.6) == "acknowledged"
        assert VendetectAdapter._severity_for("MIT", 0.5) == "acknowledged"
        assert VendetectAdapter._severity_for("MIT", 0.69) == "acknowledged"
