# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] tests.clone_guard.test_redup_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/clone_guard/test_redup_adapter.py
# [A_test] module_id: MOD-CLONE_GUARD | layer=test | stability=volatile | safety=L | ai_modifiable
# [TTL] permanent
"""RedupAdapter 单元测试——mock subprocess 调用，针对真实 redup_sample.json fixture 断言。

验证后集成纪律（clone-guard-engine-verification-ruling.md §2.3）：解析器针对
已捕获的真实输出样本编写，禁止基于假设实现。
"""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.redup_adapter import RedupAdapter

_FIXTURE = Path(__file__).parent / "fixtures" / "redup_sample.json"


def _load_fixture() -> dict:
    """加载真实 reDUP 输出样本。"""
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


def _mock_result(stdout: str, returncode: int = 1) -> MagicMock:
    return MagicMock(returncode=returncode, stdout=stdout, stderr="")


class TestRedupAdapterHealthCheck:
    """health_check 测试。"""

    def test_cli_missing_returns_false(self, tmp_path: Path):
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value=None):
            assert adapter.health_check() is False

    def test_cli_present_returns_true(self, tmp_path: Path):
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/redup"):
            assert adapter.health_check() is True


class TestRedupAdapterDetectDegradation:
    """detect 降级路径测试。"""

    def test_empty_files_returns_empty_no_degraded(self, tmp_path: Path):
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        findings, degraded = adapter.detect([])
        assert findings == []
        assert degraded is False

    def test_disabled_in_config_degraded(self, tmp_path: Path):
        adapter = RedupAdapter(tmp_path, CloneGuardConfig(redup_enabled=False))
        findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_cli_not_found_degraded(self, tmp_path: Path):
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value=None):
            findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_timeout_degraded(self, tmp_path: Path):
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="redup", timeout=30)):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_file_not_found_degraded(self, tmp_path: Path):
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", side_effect=FileNotFoundError):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_generic_exception_degraded(self, tmp_path: Path):
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", side_effect=OSError("boom")):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_bad_exit_code_degraded(self, tmp_path: Path):
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=_mock_result("", returncode=2)):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_json_decode_error_degraded(self, tmp_path: Path):
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=_mock_result("not json{", returncode=0)):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_no_groups_returns_empty(self, tmp_path: Path):
        """正常执行但无 groups（exit 0）。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=_mock_result(json.dumps({"groups": []}), returncode=0)):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is False


class TestRedupCommandBuilding:
    """_build_command 命令构造测试。"""

    def test_changed_only_mode_command(self, tmp_path: Path):
        """L1 changed-only 模式构造正确命令（--format json + --changed-only + --base-ref）。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig(redup_mode="changed-only", redup_base_ref="main"))
        with patch("shutil.which", return_value="/fake/redup"):
            with patch(
                "subprocess.run", return_value=_mock_result(json.dumps({"groups": []}), returncode=0)
            ) as mock_run:
                adapter.detect(["src/foo.py"])
        cmd = mock_run.call_args[0][0]
        assert "redup" in cmd
        assert "scan" in cmd
        assert "--format" in cmd
        assert "json" in cmd
        assert "--changed-only" in cmd
        assert "--base-ref" in cmd
        assert "main" in cmd  # redup_base_ref
        assert "--min-sim" in cmd
        assert "--semantic" not in cmd

    def test_semantic_mode_command(self, tmp_path: Path):
        """L2 semantic 模式构造正确命令（--semantic + --semantic-threshold，无 --changed-only）。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig(redup_mode="semantic"))
        with patch("shutil.which", return_value="/fake/redup"):
            with patch(
                "subprocess.run", return_value=_mock_result(json.dumps({"groups": []}), returncode=0)
            ) as mock_run:
                adapter.detect(["src/foo.py"])
        cmd = mock_run.call_args[0][0]
        assert "--semantic" in cmd
        assert "--semantic-threshold" in cmd
        assert "--changed-only" not in cmd
        assert "--base-ref" not in cmd

    def test_max_groups_in_command(self, tmp_path: Path):
        """redup_max_groups > 0 时加入 --max-groups。"""
        cfg = CloneGuardConfig(redup_max_groups=5)
        adapter = RedupAdapter(tmp_path, cfg)
        with patch("shutil.which", return_value="/fake/redup"):
            with patch(
                "subprocess.run", return_value=_mock_result(json.dumps({"groups": []}), returncode=0)
            ) as mock_run:
                adapter.detect(["src/foo.py"])
        cmd = mock_run.call_args[0][0]
        assert "--max-groups" in cmd
        assert "5" in cmd

    def test_repo_root_in_command(self, tmp_path: Path):
        """命令包含仓库根目录作为 scan 的位置参数。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/redup"):
            with patch(
                "subprocess.run", return_value=_mock_result(json.dumps({"groups": []}), returncode=0)
            ) as mock_run:
                adapter.detect(["src/foo.py"])
        cmd = mock_run.call_args[0][0]
        assert str(tmp_path) in cmd

    def test_env_injected(self, tmp_path: Path):
        """detect 调用 subprocess.run 时注入 config.env。"""
        cfg = CloneGuardConfig(env={"CUSTOM_VAR": "1"})
        adapter = RedupAdapter(tmp_path, cfg)
        with patch("shutil.which", return_value="/fake/redup"):
            with patch(
                "subprocess.run", return_value=_mock_result(json.dumps({"groups": []}), returncode=0)
            ) as mock_run:
                adapter.detect(["src/foo.py"])
        _, kwargs = mock_run.call_args
        assert kwargs["env"]["CUSTOM_VAR"] == "1"


class TestRedupFixtureParsing:
    """针对真实 redup_sample.json 的解析测试（验证后集成纪律）。"""

    def test_fixture_parses_to_four_findings(self, tmp_path: Path):
        """真实样本：3 groups（3+2+2 fragments）→ 2+1+1 = 4 findings。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        data = _load_fixture()
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=_mock_result(json.dumps(data), returncode=1)):
                findings, degraded = adapter.detect(["src/foo.py"])
        assert degraded is False
        assert len(findings) == 4  # grp-001(3frag→2) + grp-002(2frag→1) + grp-003(2frag→1)

    def test_actionability_refactor_maps_to_extract(self, tmp_path: Path):
        """grp-001 actionability=refactor → extract（3 fragments → 2 findings）。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        data = _load_fixture()
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=_mock_result(json.dumps(data), returncode=1)):
                findings, _ = adapter.detect(["src/foo.py"])
        grp1 = [f for f in findings if f.finding_id.startswith("RD-grp-001")]
        assert len(grp1) == 2
        for f in grp1:
            assert f.severity == "extract"
            assert f.clone_type == "structural"
            assert f.similarity == pytest.approx(0.92, abs=0.001)

    def test_actionability_review_maps_to_review(self, tmp_path: Path):
        """grp-002 actionability=review → review（2 fragments → 1 finding）。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        data = _load_fixture()
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=_mock_result(json.dumps(data), returncode=1)):
                findings, _ = adapter.detect(["src/foo.py"])
        grp2 = [f for f in findings if f.finding_id.startswith("RD-grp-002")]
        assert len(grp2) == 1
        assert grp2[0].severity == "review"
        assert grp2[0].clone_type == "exact"

    def test_actionability_generated_maps_to_acknowledged(self, tmp_path: Path):
        """grp-003 actionability=generated → acknowledged。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        data = _load_fixture()
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=_mock_result(json.dumps(data), returncode=1)):
                findings, _ = adapter.detect(["src/foo.py"])
        grp3 = [f for f in findings if f.finding_id.startswith("RD-grp-003")]
        assert len(grp3) == 1
        assert grp3[0].severity == "acknowledged"

    def test_finding_fields_from_fragments(self, tmp_path: Path):
        """finding 的 source/existing 字段取自 fragments[0]/[1+]。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        data = _load_fixture()
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=_mock_result(json.dumps(data), returncode=1)):
                findings, _ = adapter.detect(["src/foo.py"])
        grp1 = [f for f in findings if f.finding_id.startswith("RD-grp-001")]
        # source = fragments[0] (src/auth.py:validate_input @ line_start=10)
        assert grp1[0].source_file == "src/auth.py"
        assert grp1[0].source_function == "validate_input"
        assert grp1[0].source_lineno == 10
        # existing[0] = fragments[1] (src/api.py:validate_request @ 50)
        assert grp1[0].existing_file == "src/api.py"
        assert grp1[0].existing_function == "validate_request"
        assert grp1[0].existing_lineno == 50
        # existing[1] = fragments[2] (src/utils.py:validate_data @ 5)
        assert grp1[1].existing_file == "src/utils.py"
        assert grp1[1].existing_function == "validate_data"

    def test_import_suggestion_from_refactor_suggestions(self, tmp_path: Path):
        """grp-001 有 refactor_suggestion → import_suggestion 为 from src.validators import validate_input。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        data = _load_fixture()
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=_mock_result(json.dumps(data), returncode=1)):
                findings, _ = adapter.detect(["src/foo.py"])
        grp1 = [f for f in findings if f.finding_id.startswith("RD-grp-001")]
        assert grp1[0].import_suggestion == "from src.validators import validate_input"
        # grp-002/003 无 refactor_suggestion → None
        grp2 = [f for f in findings if f.finding_id.startswith("RD-grp-002")]
        assert grp2[0].import_suggestion is None

    def test_finding_id_format(self, tmp_path: Path):
        """finding_id 格式为 RD-{group_id}-{idx}。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        data = _load_fixture()
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=_mock_result(json.dumps(data), returncode=1)):
                findings, _ = adapter.detect(["src/foo.py"])
        ids = {f.finding_id for f in findings}
        assert "RD-grp-001-1" in ids
        assert "RD-grp-001-2" in ids
        assert "RD-grp-002-1" in ids
        assert "RD-grp-003-1" in ids


class TestRedupSeverityFallback:
    """无 actionability 字段时的 fallback 推断。"""

    def test_three_occurrences_fallback_extract(self, tmp_path: Path):
        """无 actionability + 3 occurrences → extract。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        group = {
            "id": "g1",
            "type": "structural",
            "similarity_score": 0.9,
            "occurrences": 3,
            "fragments": [
                {"file": "src/a.py", "line_start": 1, "function_name": "f1"},
                {"file": "src/b.py", "line_start": 2, "function_name": "f2"},
                {"file": "src/c.py", "line_start": 3, "function_name": "f3"},
            ],
        }
        data = {"groups": [group]}
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=_mock_result(json.dumps(data), returncode=1)):
                findings, _ = adapter.detect(["src/a.py"])
        assert findings[0].severity == "extract"

    def test_two_occurrences_fallback_review(self, tmp_path: Path):
        """无 actionability + 2 occurrences + sim<0.95 → review。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        group = {
            "id": "g2",
            "type": "exact",
            "similarity_score": 0.88,
            "occurrences": 2,
            "fragments": [
                {"file": "src/a.py", "line_start": 1, "function_name": "f1"},
                {"file": "src/b.py", "line_start": 2, "function_name": "f2"},
            ],
        }
        data = {"groups": [group]}
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=_mock_result(json.dumps(data), returncode=1)):
                findings, _ = adapter.detect(["src/a.py"])
        assert findings[0].severity == "review"

    def test_single_fragment_skipped(self, tmp_path: Path):
        """单 fragment（无克隆对）被跳过。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        group = {
            "id": "g3",
            "type": "exact",
            "similarity_score": 1.0,
            "occurrences": 1,
            "fragments": [{"file": "src/a.py", "line_start": 1, "function_name": "f1"}],
        }
        data = {"groups": [group]}
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=_mock_result(json.dumps(data), returncode=1)):
                findings, _ = adapter.detect(["src/a.py"])
        assert findings == []


class TestRedupPathNormalization:
    """路径归一化测试。"""

    def test_absolute_path_converted_to_relative(self, tmp_path: Path):
        """绝对路径转为相对仓库根目录。"""
        adapter = RedupAdapter(tmp_path, CloneGuardConfig())
        abs_a = str(tmp_path / "src" / "new.py")
        abs_b = str(tmp_path / "src" / "old.py")
        group = {
            "id": "g",
            "type": "exact",
            "similarity_score": 0.9,
            "occurrences": 2,
            "fragments": [
                {"file": abs_a, "line_start": 1, "function_name": "calc"},
                {"file": abs_b, "line_start": 2, "function_name": "compute"},
            ],
        }
        data = {"groups": [group]}
        with patch("shutil.which", return_value="/fake/redup"):
            with patch("subprocess.run", return_value=_mock_result(json.dumps(data), returncode=1)):
                findings, _ = adapter.detect(["src/new.py"])
        assert findings[0].source_file == "src/new.py"
        assert findings[0].existing_file == "src/old.py"
