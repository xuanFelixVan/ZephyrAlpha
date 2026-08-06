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
"""VendetectAdapter 单元测试——mock subprocess 调用，针对真实 vendetect_sample.csv fixture 断言。

验证后集成纪律（clone-guard-engine-verification-ruling.md §2.3）：解析器针对
已捕获的真实 CSV 输出样本编写（Vendetect v0.0.3 JSON 含 numpy int64 序列化崩溃，故用 CSV）。
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.vendetect_adapter import VendetectAdapter

# Vendetect 真实输出为 CSV 格式，但 tests/ 目录契约仅允许 .txt/.json/.yaml/.py
# （directory_contract.yaml L305），故 fixture 以 .txt 扩展名存放 CSV 内容。
_FIXTURE = Path(__file__).parent / "fixtures" / "vendetect_sample.txt"
_REMOTE = "https://github.com/example/source-repo"


def _load_fixture() -> str:
    """加载真实 Vendetect CSV 输出样本（.txt 扩展名存 CSV 内容，守目录契约）。"""
    return _FIXTURE.read_text(encoding="utf-8")


def _cfg(**kwargs) -> CloneGuardConfig:
    """构造启用 Vendetect 的配置。"""
    return CloneGuardConfig(vendetect_enabled=True, vendetect_remote_url=_REMOTE, **kwargs)


def _mock_result(stdout: str, returncode: int = 1) -> MagicMock:
    return MagicMock(returncode=returncode, stdout=stdout, stderr="")


class TestVendetectAdapterHealthCheck:
    """health_check 测试。"""

    def test_cli_missing_returns_false(self, tmp_path: Path):
        adapter = VendetectAdapter(tmp_path, CloneGuardConfig(vendetect_remote_url=_REMOTE))
        with patch("shutil.which", return_value=None):
            assert adapter.health_check() is False

    def test_cli_present_no_remote_returns_false(self, tmp_path: Path):
        adapter = VendetectAdapter(tmp_path, CloneGuardConfig())  # vendetect_remote_url=None
        with patch("shutil.which", return_value="/fake/vendetect"):
            assert adapter.health_check() is False

    def test_cli_and_remote_present_returns_true(self, tmp_path: Path):
        adapter = VendetectAdapter(tmp_path, CloneGuardConfig(vendetect_remote_url=_REMOTE))
        with patch("shutil.which", return_value="/fake/vendetect"):
            assert adapter.health_check() is True


class TestVendetectAdapterDetectDegradation:
    """detect 降级路径测试。"""

    def test_empty_files(self, tmp_path: Path):
        adapter = VendetectAdapter(tmp_path, CloneGuardConfig())
        findings, degraded = adapter.detect([])
        assert findings == []
        assert degraded is False

    def test_disabled_in_config(self, tmp_path: Path):
        adapter = VendetectAdapter(tmp_path, CloneGuardConfig(vendetect_enabled=False))
        findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_cli_not_found_degraded(self, tmp_path: Path):
        adapter = VendetectAdapter(tmp_path, _cfg())
        with patch("shutil.which", return_value=None):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_no_remote_url_degraded(self, tmp_path: Path):
        adapter = VendetectAdapter(tmp_path, CloneGuardConfig(vendetect_enabled=True))  # remote=None
        with patch("shutil.which", return_value="/fake/vendetect"):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_timeout_degraded(self, tmp_path: Path):
        adapter = VendetectAdapter(tmp_path, _cfg())
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="vendetect", timeout=600)):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_generic_exception_degraded(self, tmp_path: Path):
        adapter = VendetectAdapter(tmp_path, _cfg())
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", side_effect=OSError("boom")):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_bad_exit_code_degraded(self, tmp_path: Path):
        adapter = VendetectAdapter(tmp_path, _cfg())
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", return_value=_mock_result("", returncode=2)):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_empty_stdout_returns_empty(self, tmp_path: Path):
        """空输出 → 空结果（非降级）。"""
        adapter = VendetectAdapter(tmp_path, _cfg())
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", return_value=_mock_result("", returncode=0)):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is False


class TestVendetectCommandBuilding:
    """_build_command 命令构造测试（位置参数 TEST_REPO SOURCE_REPO + --format csv）。"""

    def test_positional_args_and_csv_format(self, tmp_path: Path):
        adapter = VendetectAdapter(tmp_path, _cfg())
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", return_value=_mock_result("", returncode=0)) as mock_run:
                adapter.detect(["src/foo.py"])
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "vendetect"
        # 位置参数：TEST_REPO (repo_root) + SOURCE_REPO (remote_url)
        assert str(tmp_path) in cmd
        assert _REMOTE in cmd
        assert "--format" in cmd
        assert "csv" in cmd
        assert "--min-similarity" in cmd
        assert "--type" in cmd
        assert "py" in cmd
        # 不应再有旧的 --local/--remote/--json
        assert "--local" not in cmd
        assert "--remote" not in cmd
        assert "--json" not in cmd

    def test_env_injected(self, tmp_path: Path):
        adapter = VendetectAdapter(tmp_path, _cfg(env={"CUSTOM_VAR": "1"}))
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", return_value=_mock_result("", returncode=0)) as mock_run:
                adapter.detect(["src/foo.py"])
        _, kwargs = mock_run.call_args
        assert kwargs["env"]["CUSTOM_VAR"] == "1"


class TestVendetectFixtureParsing:
    """针对真实 vendetect_sample.csv 的解析测试（验证后集成纪律）。"""

    def test_fixture_parses_two_findings(self, tmp_path: Path):
        """真实样本：2 个 (Test, Source) 对 → 2 findings。"""
        adapter = VendetectAdapter(tmp_path, _cfg())
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", return_value=_mock_result(_load_fixture(), returncode=1)):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert degraded is False
        assert len(findings) == 2

    def test_high_similarity_maps_to_extract(self, tmp_path: Path):
        """相似度 1.0000 ≥ 0.95 → extract（vendored 高相似 = 合规风险）。"""
        adapter = VendetectAdapter(tmp_path, _cfg())
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", return_value=_mock_result(_load_fixture(), returncode=1)):
                findings, _ = adapter.detect(["src/foo.py"])
        for f in findings:
            assert f.severity == "extract"
            assert f.clone_type == "vendored"
            assert f.similarity == pytest.approx(1.0, abs=0.0001)

    def test_finding_fields_from_csv(self, tmp_path: Path):
        """finding 字段取自 CSV（路径归一化斜杠）。"""
        adapter = VendetectAdapter(tmp_path, _cfg())
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", return_value=_mock_result(_load_fixture(), returncode=1)):
                findings, _ = adapter.detect(["src/foo.py"])
        f0 = findings[0]
        assert f0.source_file == "src/agg_test.py"  # 反斜杠归一化
        assert f0.existing_file == "src/agg_orig.py"
        assert f0.source_function == "unknown"  # CSV 无函数名
        assert f0.existing_function == "unknown"
        assert f0.source_lineno == 861  # Test Slice Start
        assert f0.import_suggestion == _REMOTE  # 远程 URL 作溯源

    def test_finding_id_format(self, tmp_path: Path):
        """finding_id 格式 VD-{idx}-{test}-{source}。"""
        adapter = VendetectAdapter(tmp_path, _cfg())
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", return_value=_mock_result(_load_fixture(), returncode=1)):
                findings, _ = adapter.detect(["src/foo.py"])
        assert findings[0].finding_id == "VD-0-src/agg_test.py-src/agg_orig.py"
        assert findings[1].finding_id == "VD-1-src/cfg_test.py-src/cfg_orig.py"


class TestVendetectCsvAggregation:
    """CSV 切片聚合测试。"""

    def test_multiple_slices_same_pair_aggregated(self, tmp_path: Path):
        """同一 (test, source) 对多行切片 → 1 finding，相似度取最大。"""
        adapter = VendetectAdapter(tmp_path, _cfg())
        csv_text = (
            "Test File,Source File,Test Slice Start,Test Slice End,"
            "Source Slice Start,Source Slice End,Similarity\n"
            "src/a.py,src/b.py,10,20,10,20,0.80\n"
            "src/a.py,src/b.py,30,40,30,40,0.99\n"
        )
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", return_value=_mock_result(csv_text, returncode=1)):
                findings, _ = adapter.detect(["src/a.py"])
        assert len(findings) == 1
        assert findings[0].similarity == pytest.approx(0.99, abs=0.001)
        assert findings[0].severity == "extract"  # 0.99 >= 0.95

    def test_malformed_row_skipped(self, tmp_path: Path):
        """列数不足的行被跳过，不阻断解析。"""
        adapter = VendetectAdapter(tmp_path, _cfg())
        csv_text = (
            "Test File,Source File,Test Slice Start,Test Slice End,"
            "Source Slice Start,Source Slice End,Similarity\n"
            "src/a.py,src/b.py,10,20,10,20,0.99\n"
            "bad,row\n"  # 列数不足
        )
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", return_value=_mock_result(csv_text, returncode=1)):
                findings, _ = adapter.detect(["src/a.py"])
        assert len(findings) == 1  # 仅合法行解析


class TestVendetectSeverityMapping:
    """_severity_for 相似度分档测试（CSV 无 license）。"""

    def test_high_sim_extract(self):
        assert VendetectAdapter._severity_for(0.95) == "extract"
        assert VendetectAdapter._severity_for(0.99) == "extract"
        assert VendetectAdapter._severity_for(1.0) == "extract"

    def test_mid_sim_review(self):
        assert VendetectAdapter._severity_for(0.7) == "review"
        assert VendetectAdapter._severity_for(0.85) == "review"
        assert VendetectAdapter._severity_for(0.949) == "review"

    def test_low_sim_acknowledged(self):
        assert VendetectAdapter._severity_for(0.69) == "acknowledged"
        assert VendetectAdapter._severity_for(0.5) == "acknowledged"
        assert VendetectAdapter._severity_for(0.0) == "acknowledged"


class TestVendetectPathNormalization:
    """路径归一化测试。"""

    def test_absolute_test_file_converted_to_relative(self, tmp_path: Path):
        """test_file 绝对路径转为相对仓库根目录。"""
        adapter = VendetectAdapter(tmp_path, _cfg())
        abs_test = str(tmp_path / "src" / "new.py")
        csv_text = (
            "Test File,Source File,Test Slice Start,Test Slice End,"
            "Source Slice Start,Source Slice End,Similarity\n"
            f"{abs_test},vendor/lib.py,10,20,10,20,0.99\n"
        )
        with patch("shutil.which", return_value="/fake/vendetect"):
            with patch("subprocess.run", return_value=_mock_result(csv_text, returncode=1)):
                findings, _ = adapter.detect(["src/new.py"])
        assert findings[0].source_file == "src/new.py"
        assert findings[0].existing_file == "vendor/lib.py"  # source_file 归一化斜杠
