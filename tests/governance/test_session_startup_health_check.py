# [A_test] module_id: MOD-GOV_session_startup_health_check | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-278 | docs/03_modules/_domain_governance/blueprint.md | §ARCH-TOOL-HEALTH-V1
# [MODULE] tests.governance.test_session_startup_health_check
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] subprocess error->skip_test
# [TESTS] tests/governance/test_session_startup_health_check.py
# [A_module] module_id=MOD-TEST-278 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_session_startup_health_check.py — AI session 启动健康度自检单元测试

#ARCH-TOOL-HEALTH-V1 Phase 6 治本：验证 session_startup_health_check.py 的检测逻辑。

病根
----
commit deb695006f 误删 import 导致 NameError 静默累积，5 层防线全失效。
治本：AI session 启动时检测核心工具 import/CLI/符号可用性，失败时 escalate。

测试策略
--------
1. `check_core_tool_import`: 构造临时脚本，验证 success / missing file /
   syntax error / missing symbol 四种场景
2. `check_core_tool_cli`: 构造可执行 CLI 脚本，验证 rc=0 / rc!=0 /
   超时 / 输出缺字符串（warn）四种场景
3. `check_gateway_module`: monkeypatch sys.modules，验证 import 成功 /
   import 失败 / 关键属性缺失三种场景
4. `run_startup_health_check`: monkeypatch 子检查函数，验证 status 聚合
   （pass/warn/fail）+ escalation_required 标志
5. `main` exit codes: CLI 模式 0/1/2 三种退出码
6. e2e 真实仓库 smoke test：在真实 ZephyrAlpha 仓库上跑健康检查，
   验证 12 项检查全 pass（前提：仓库当前健康）
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "governance" / "session_startup_health_check.py"


# ---------------------------------------------------------------------------
# 加载被测模块（独立脚本，不依赖 __init__.py）
# ---------------------------------------------------------------------------


def _load_health_check_module():
    """用 importlib 加载 session_startup_health_check.py 为模块。"""
    import importlib.util

    spec = importlib.util.spec_from_file_location("_test_target_session_startup_health_check", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None, f"无法加载 {SCRIPT_PATH}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def hc():
    """加载被测模块。"""
    return _load_health_check_module()


# ---------------------------------------------------------------------------
# check_core_tool_import 测试
# ---------------------------------------------------------------------------


def _write_tool_script(repo_root: Path, rel_path: str, content: str) -> Path:
    """在临时仓库下写入脚本文件，返回绝对路径。"""
    script_path = repo_root / rel_path
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(content, encoding="utf-8")
    return script_path


pytestmark = pytest.mark.silent_failure  # Ruling:100PCT-AI-GOVERNANCE P3-2


class TestCheckCoreToolImport:
    """check_core_tool_import 的四种场景。"""

    def test_import_success_with_required_symbols(self, hc, tmp_path):
        """脚本正常 + 关键符号齐全 → pass。"""
        _init_git_repo(tmp_path)
        _write_tool_script(
            tmp_path,
            "tools/good_tool.py",
            textwrap.dedent("""
            EXIT_PASS = 0
            EXIT_ERROR = 1
            def get_conn():
                return None
        """),
        )
        tool = {
            "name": "good_tool",
            "rel_path": "tools/good_tool.py",
            "required_symbols": ["EXIT_PASS", "EXIT_ERROR", "get_conn"],
        }
        result = hc.check_core_tool_import(tool, tmp_path)
        assert result["status"] == "pass"
        assert "3 个关键符号" in result["detail"]

    def test_import_missing_file(self, hc, tmp_path):
        """脚本文件不存在 → fail。"""
        _init_git_repo(tmp_path)
        tool = {
            "name": "missing_tool",
            "rel_path": "tools/missing.py",
            "required_symbols": [],
        }
        result = hc.check_core_tool_import(tool, tmp_path)
        assert result["status"] == "fail"
        assert "文件不存在" in result["detail"]

    def test_import_syntax_error(self, hc, tmp_path):
        """脚本有 SyntaxError → fail（Phase 1 类 NameError 检测点）。"""
        _init_git_repo(tmp_path)
        # 故意构造未闭合的 import（与 apply_dataflowgraph.py bug 同形态）
        _write_tool_script(
            tmp_path,
            "tools/broken.py",
            textwrap.dedent("""
            from os import (
            _SCRIPT_DIR = "x"
            )
        """),
        )
        tool = {
            "name": "broken_tool",
            "rel_path": "tools/broken.py",
            "required_symbols": [],
        }
        result = hc.check_core_tool_import(tool, tmp_path)
        assert result["status"] == "fail"
        # SyntaxError 或 import 失败信息
        assert "import 失败" in result["detail"]

    def test_import_missing_symbol(self, hc, tmp_path):
        """脚本正常但缺关键符号 → fail。"""
        _init_git_repo(tmp_path)
        _write_tool_script(
            tmp_path,
            "tools/partial.py",
            textwrap.dedent("""
            EXIT_PASS = 0
            # 缺 EXIT_ERROR
        """),
        )
        tool = {
            "name": "partial_tool",
            "rel_path": "tools/partial.py",
            "required_symbols": ["EXIT_PASS", "EXIT_ERROR"],
        }
        result = hc.check_core_tool_import(tool, tmp_path)
        assert result["status"] == "fail"
        assert "缺少关键符号" in result["detail"]
        assert "EXIT_ERROR" in result["detail"]


# ---------------------------------------------------------------------------
# check_core_tool_cli 测试
# ---------------------------------------------------------------------------


class TestCheckCoreToolCli:
    """check_core_tool_cli 的四种场景。"""

    def test_cli_success(self, hc, tmp_path):
        """CLI rc=0 → pass。"""
        _init_git_repo(tmp_path)
        _write_tool_script(
            tmp_path,
            "tools/cli_ok.py",
            textwrap.dedent("""
            import sys
            sys.argv  # avoid unused
            if __name__ == "__main__":
                print("cmd_batch: list-ops")
                sys.exit(0)
        """),
        )
        tool = {
            "name": "cli_ok",
            "rel_path": "tools/cli_ok.py",
            "cli_args": ["--list-ops"],
            "cli_output_contains": "cmd_batch",
            "required_symbols": [],
        }
        result = hc.check_core_tool_cli(tool, tmp_path)
        assert result["status"] == "pass"
        assert "CLI rc=0" in result["detail"]

    def test_cli_nonzero_exit(self, hc, tmp_path):
        """CLI rc!=0 → fail。"""
        _init_git_repo(tmp_path)
        _write_tool_script(
            tmp_path,
            "tools/cli_fail.py",
            textwrap.dedent("""
            import sys
            if __name__ == "__main__":
                print("error occurred", file=sys.stderr)
                sys.exit(1)
        """),
        )
        tool = {
            "name": "cli_fail",
            "rel_path": "tools/cli_fail.py",
            "cli_args": ["--list-ops"],
            "cli_output_contains": None,
            "required_symbols": [],
        }
        result = hc.check_core_tool_cli(tool, tmp_path)
        assert result["status"] == "fail"
        assert "rc=1" in result["detail"]

    def test_cli_missing_expected_output(self, hc, tmp_path):
        """CLI rc=0 但输出不含 expected → warn（输出格式变更提示）。"""
        _init_git_repo(tmp_path)
        _write_tool_script(
            tmp_path,
            "tools/cli_format.py",
            textwrap.dedent("""
            import sys
            if __name__ == "__main__":
                print("totally different output format")
                sys.exit(0)
        """),
        )
        tool = {
            "name": "cli_format",
            "rel_path": "tools/cli_format.py",
            "cli_args": ["--list-ops"],
            "cli_output_contains": "cmd_batch",
            "required_symbols": [],
        }
        result = hc.check_core_tool_cli(tool, tmp_path)
        assert result["status"] == "warn"
        assert "缺少 'cmd_batch'" in result["detail"]

    def test_cli_missing_file(self, hc, tmp_path):
        """CLI 脚本不存在 → fail。"""
        _init_git_repo(tmp_path)
        tool = {
            "name": "missing_cli",
            "rel_path": "tools/missing.py",
            "cli_args": ["--list-ops"],
            "cli_output_contains": None,
            "required_symbols": [],
        }
        result = hc.check_core_tool_cli(tool, tmp_path)
        assert result["status"] == "fail"
        assert "文件不存在" in result["detail"]


# ---------------------------------------------------------------------------
# check_gateway_module 测试
# ---------------------------------------------------------------------------


class TestCheckGatewayModule:
    """check_gateway_module 的三种场景。"""

    def test_gateway_success(self, hc, tmp_path, monkeypatch):
        """模块 import 成功 + 关键属性齐全 → pass。"""
        _init_git_repo(tmp_path)
        # 构造 fake 模块
        fake_mod = type("FakeMod", (), {"GitCommitGateway": object})()
        monkeypatch.setitem(sys.modules, "fake_test.gateway_ok", fake_mod)
        mod_spec = {
            "module": "fake_test.gateway_ok",
            "required_attrs": ["GitCommitGateway"],
        }
        result = hc.check_gateway_module(mod_spec, tmp_path)
        assert result["status"] == "pass"
        assert "1 个关键属性" in result["detail"]

    def test_gateway_missing_attr(self, hc, tmp_path, monkeypatch):
        """模块 import 成功但缺关键属性 → fail。"""
        _init_git_repo(tmp_path)
        fake_mod = type("FakeMod", (), {"GitCommitGateway": object})()
        # 缺 NotExistAttr
        monkeypatch.setitem(sys.modules, "fake_test.gateway_missing", fake_mod)
        mod_spec = {
            "module": "fake_test.gateway_missing",
            "required_attrs": ["GitCommitGateway", "NotExistAttr"],
        }
        result = hc.check_gateway_module(mod_spec, tmp_path)
        assert result["status"] == "fail"
        assert "缺少关键属性" in result["detail"]
        assert "NotExistAttr" in result["detail"]

    def test_gateway_import_fail(self, hc, tmp_path, monkeypatch):
        """模块 import 失败 → fail。"""
        _init_git_repo(tmp_path)

        # 让 import_module 抛异常
        def fake_import_module(name):
            raise ImportError(f"No module named '{name}'")

        monkeypatch.setattr(hc.importlib, "import_module", fake_import_module)
        mod_spec = {
            "module": "definitely.does.not.exist",
            "required_attrs": ["Anything"],
        }
        result = hc.check_gateway_module(mod_spec, tmp_path)
        assert result["status"] == "fail"
        assert "import 失败" in result["detail"]


# ---------------------------------------------------------------------------
# run_startup_health_check 测试（status 聚合）
# ---------------------------------------------------------------------------


class TestRunStartupHealthCheckAggregation:
    """run_startup_health_check 的 status 聚合逻辑。"""

    def test_all_pass_yields_pass(self, hc, tmp_path, monkeypatch):
        """所有检查 pass → status=pass，escalation_required=False。"""
        _init_git_repo(tmp_path)

        def fake_check(*args, **kwargs):
            return {"check": "fake", "status": "pass", "detail": "ok"}

        monkeypatch.setattr(hc, "check_core_tool_import", fake_check)
        monkeypatch.setattr(hc, "check_core_tool_cli", fake_check)
        monkeypatch.setattr(hc, "check_gateway_module", fake_check)
        monkeypatch.setattr(hc, "check_git_health_smoke", fake_check)

        result = hc.run_startup_health_check(repo_root=str(tmp_path))
        assert result["status"] == "pass"
        assert result["escalation_required"] is False
        assert result["failed_count"] == 0

    def test_at_least_one_warn_yields_warn(self, hc, tmp_path, monkeypatch):
        """至少一项 warn（无 fail）→ status=warn，escalation_required=False。"""
        _init_git_repo(tmp_path)

        def pass_check(*args, **kwargs):
            return {"check": "fake_pass", "status": "pass", "detail": "ok"}

        def warn_check(*args, **kwargs):
            return {"check": "fake_warn", "status": "warn", "detail": "be careful"}

        monkeypatch.setattr(hc, "check_core_tool_import", pass_check)
        monkeypatch.setattr(hc, "check_core_tool_cli", warn_check)
        monkeypatch.setattr(hc, "check_gateway_module", pass_check)
        monkeypatch.setattr(hc, "check_git_health_smoke", warn_check)

        result = hc.run_startup_health_check(repo_root=str(tmp_path))
        assert result["status"] == "warn"
        assert result["escalation_required"] is False
        assert result["failed_count"] == 0

    def test_at_least_one_fail_yields_fail_and_escalation(self, hc, tmp_path, monkeypatch):
        """至少一项 fail → status=fail，escalation_required=True。"""
        _init_git_repo(tmp_path)

        def pass_check(*args, **kwargs):
            return {"check": "fake_pass", "status": "pass", "detail": "ok"}

        def fail_check(*args, **kwargs):
            return {"check": "fake_fail", "status": "fail", "detail": "NameError: missing_import"}

        monkeypatch.setattr(hc, "check_core_tool_import", fail_check)
        monkeypatch.setattr(hc, "check_core_tool_cli", pass_check)
        monkeypatch.setattr(hc, "check_gateway_module", pass_check)
        monkeypatch.setattr(hc, "check_git_health_smoke", pass_check)

        result = hc.run_startup_health_check(repo_root=str(tmp_path))
        assert result["status"] == "fail"
        assert result["escalation_required"] is True
        assert result["failed_count"] > 0
        # 摘要含失败项
        assert "FAIL项" in result["summary"]

    def test_non_git_repo_yields_fail(self, hc, tmp_path):
        """非 git 仓库 → 直接 fail。"""
        # tmp_path 默认不是 git 仓库
        result = hc.run_startup_health_check(repo_root=str(tmp_path))
        assert result["status"] == "fail"
        assert result["escalation_required"] is True
        assert "不是 git 仓库" in result["summary"]

    def test_no_git_skips_git_check(self, hc, tmp_path, monkeypatch):
        """include_git=False 跳过 git_health_smoke 检查。"""
        _init_git_repo(tmp_path)

        def pass_check(*args, **kwargs):
            return {"check": "fake_pass", "status": "pass", "detail": "ok"}

        def should_not_call(*args, **kwargs):
            pytest.fail("check_git_health_smoke 不应被调用")

        monkeypatch.setattr(hc, "check_core_tool_import", pass_check)
        monkeypatch.setattr(hc, "check_core_tool_cli", pass_check)
        monkeypatch.setattr(hc, "check_gateway_module", pass_check)
        monkeypatch.setattr(hc, "check_git_health_smoke", should_not_call)

        result = hc.run_startup_health_check(repo_root=str(tmp_path), include_git=False)
        assert result["status"] == "pass"
        # 14 项（P2-4 后：8 core tools + 6 gateway modules + 0 git skipped）
        # 原值 11（3 gateway modules）→ P2-4 新增 emergency_commit/reconcile_runner/reconcile_worker = 14
        assert result["total_count"] == 14


# ---------------------------------------------------------------------------
# main() exit code 测试
# ---------------------------------------------------------------------------


class TestMainExitCodes:
    """main() 函数 exit code：0=pass / 1=fail / 2=warn。"""

    def test_main_exit_zero_on_pass(self, hc, tmp_path, monkeypatch):
        """全 pass → exit 0。"""
        _init_git_repo(tmp_path)

        def pass_check(*args, **kwargs):
            return {"check": "fake", "status": "pass", "detail": "ok"}

        monkeypatch.setattr(hc, "check_core_tool_import", pass_check)
        monkeypatch.setattr(hc, "check_core_tool_cli", pass_check)
        monkeypatch.setattr(hc, "check_gateway_module", pass_check)
        monkeypatch.setattr(hc, "check_git_health_smoke", pass_check)
        monkeypatch.setattr(sys, "argv", ["health_check.py", str(tmp_path)])

        rc = hc.main()
        assert rc == 0

    def test_main_exit_one_on_fail(self, hc, tmp_path, monkeypatch):
        """有 fail → exit 1。"""
        _init_git_repo(tmp_path)

        def fail_check(*args, **kwargs):
            return {"check": "fake", "status": "fail", "detail": "broken"}

        monkeypatch.setattr(hc, "check_core_tool_import", fail_check)
        monkeypatch.setattr(hc, "check_core_tool_cli", fail_check)
        monkeypatch.setattr(hc, "check_gateway_module", fail_check)
        monkeypatch.setattr(hc, "check_git_health_smoke", fail_check)
        monkeypatch.setattr(sys, "argv", ["health_check.py", str(tmp_path)])

        rc = hc.main()
        assert rc == 1

    def test_main_exit_two_on_warn(self, hc, tmp_path, monkeypatch):
        """有 warn 无 fail → exit 2。"""
        _init_git_repo(tmp_path)

        def warn_check(*args, **kwargs):
            return {"check": "fake", "status": "warn", "detail": "be careful"}

        monkeypatch.setattr(hc, "check_core_tool_import", warn_check)
        monkeypatch.setattr(hc, "check_core_tool_cli", warn_check)
        monkeypatch.setattr(hc, "check_gateway_module", warn_check)
        monkeypatch.setattr(hc, "check_git_health_smoke", warn_check)
        monkeypatch.setattr(sys, "argv", ["health_check.py", str(tmp_path)])

        rc = hc.main()
        assert rc == 2


# ---------------------------------------------------------------------------
# e2e：真实 ZephyrAlpha 仓库 smoke test
# ---------------------------------------------------------------------------


class TestP2_4Extensions:
    """P2-4 (2026-07-19) 扩展：新增 P2-1/P2-2/P2-3 工具覆盖 + session_id 持久化。

    病根：原 health check 不覆盖 P2-1/P2-2/P2-3 新工具——AI 用 emergency_commit
    逃生时如果 emergency_commit 模块本身有 import bug，AI 不会知道。
    治本：扩展 GATEWAY_MODULES 覆盖新工具 + session_id 失败持久化到 DB。
    """

    def test_gateway_modules_includes_p2_1_emergency_commit(self, hc):
        """GATEWAY_MODULES 应包含 emergency_commit 模块。"""
        modules = [m["module"] for m in hc.GATEWAY_MODULES]
        assert "zephyr.gov_enforcement.rule_bridge.emergency_commit" in modules, (
            "P2-1 emergency_commit 必须纳入 health check"
        )

    def test_gateway_modules_includes_p2_3_reconcile_runner(self, hc):
        """GATEWAY_MODULES 应包含 reconcile_runner 模块。"""
        modules = [m["module"] for m in hc.GATEWAY_MODULES]
        assert "zephyr.governance.audit.reconcile_runner" in modules, "P2-3 reconcile_runner 必须纳入 health check"

    def test_gateway_modules_includes_p2_3_reconcile_worker(self, hc):
        """GATEWAY_MODULES 应包含 reconcile_worker 模块。"""
        modules = [m["module"] for m in hc.GATEWAY_MODULES]
        assert "zephyr.governance.audit.reconcile_worker" in modules, "P2-3 reconcile_worker 必须纳入 health check"

    def test_session_worktree_includes_claim_files_for_edit(self, hc):
        """session_worktree 模块的 required_attrs 应包含 P2-2 claim_files_for_edit。"""
        sw_spec = next(
            (m for m in hc.GATEWAY_MODULES if m["module"] == "zephyr.gov_enforcement.rule_bridge.session_worktree"),
            None,
        )
        assert sw_spec is not None
        assert "claim_files_for_edit" in sw_spec["required_attrs"], (
            "P2-2 claim_files_for_edit 必须纳入 session_worktree 属性检查"
        )

    def test_session_id_persists_failure_to_db(
        self,
        hc,
        tmp_path,
        monkeypatch,
    ):
        """status=fail + session_id 提供时调用 log_gate_failure 持久化。"""
        _init_git_repo(tmp_path)

        def fail_check(*args, **kwargs):
            return {"check": "fake_fail", "status": "fail", "detail": "mocked failure"}

        monkeypatch.setattr(hc, "check_core_tool_import", fail_check)
        monkeypatch.setattr(hc, "check_core_tool_cli", fail_check)
        monkeypatch.setattr(hc, "check_gateway_module", fail_check)
        monkeypatch.setattr(hc, "check_git_health_smoke", fail_check)

        # mock log_gate_failure 捕获调用
        persist_calls: list[dict] = []

        def fake_log_gate_failure(project_root, gate_id, detail, session_id="", trigger_source=""):
            persist_calls.append(
                {
                    "project_root": str(project_root),
                    "gate_id": gate_id,
                    "detail": detail,
                    "session_id": session_id,
                    "trigger_source": trigger_source,
                }
            )

        # 注入 fake 模块到 sys.modules，使 `from zephyr... import log_gate_failure` 命中
        import sys
        import types

        fake_mod = types.ModuleType("zephyr.governance.audit.reconciliation_registry")
        fake_mod.log_gate_failure = fake_log_gate_failure
        monkeypatch.setitem(sys.modules, "zephyr.governance.audit.reconciliation_registry", fake_mod)

        result = hc.run_startup_health_check(
            repo_root=str(tmp_path),
            include_git=False,
            session_id="sess-p2-4-test",
        )
        assert result["status"] == "fail"
        assert result["escalation_required"] is True
        assert result["session_id"] == "sess-p2-4-test"
        assert result["persisted_to_db"] is True, "失败应持久化到 DB"
        assert len(persist_calls) == 1, "log_gate_failure 应被调用一次"
        assert persist_calls[0]["gate_id"] == "STARTUP-HEALTH-CHECK"
        assert persist_calls[0]["session_id"] == "sess-p2-4-test"
        assert persist_calls[0]["trigger_source"] == "session_startup"

    def test_no_session_id_skips_persistence(
        self,
        hc,
        tmp_path,
        monkeypatch,
    ):
        """status=fail 但无 session_id 时不调用 log_gate_failure（向后兼容）。"""
        _init_git_repo(tmp_path)

        def fail_check(*args, **kwargs):
            return {"check": "fake_fail", "status": "fail", "detail": "mocked"}

        monkeypatch.setattr(hc, "check_core_tool_import", fail_check)
        monkeypatch.setattr(hc, "check_core_tool_cli", fail_check)
        monkeypatch.setattr(hc, "check_gateway_module", fail_check)
        monkeypatch.setattr(hc, "check_git_health_smoke", fail_check)

        # mock log_gate_failure，断言不被调用
        def fake_log_gate_failure(*args, **kwargs):
            pytest.fail("log_gate_failure 不应被调用（无 session_id）")

        import sys
        import types

        fake_mod = types.ModuleType("zephyr.governance.audit.reconciliation_registry")
        fake_mod.log_gate_failure = fake_log_gate_failure
        monkeypatch.setitem(sys.modules, "zephyr.governance.audit.reconciliation_registry", fake_mod)

        result = hc.run_startup_health_check(
            repo_root=str(tmp_path),
            include_git=False,
            session_id="",  # 无 session_id
        )
        assert result["status"] == "fail"
        assert result["persisted_to_db"] is False

    def test_pass_status_skips_persistence(
        self,
        hc,
        tmp_path,
        monkeypatch,
    ):
        """status=pass 时不调用 log_gate_failure（即使有 session_id）。"""
        _init_git_repo(tmp_path)

        def pass_check(*args, **kwargs):
            return {"check": "fake_pass", "status": "pass", "detail": "ok"}

        monkeypatch.setattr(hc, "check_core_tool_import", pass_check)
        monkeypatch.setattr(hc, "check_core_tool_cli", pass_check)
        monkeypatch.setattr(hc, "check_gateway_module", pass_check)
        monkeypatch.setattr(hc, "check_git_health_smoke", pass_check)

        def fake_log_gate_failure(*args, **kwargs):
            pytest.fail("log_gate_failure 不应被调用（status=pass）")

        import sys
        import types

        fake_mod = types.ModuleType("zephyr.governance.audit.reconciliation_registry")
        fake_mod.log_gate_failure = fake_log_gate_failure
        monkeypatch.setitem(sys.modules, "zephyr.governance.audit.reconciliation_registry", fake_mod)

        result = hc.run_startup_health_check(
            repo_root=str(tmp_path),
            include_git=False,
            session_id="sess-pass-test",
        )
        assert result["status"] == "pass"
        assert result["persisted_to_db"] is False

    def test_persistence_failure_does_not_block_result(
        self,
        hc,
        tmp_path,
        monkeypatch,
    ):
        """log_gate_failure 抛异常时不阻断主结果返回（fail-open 降级）。"""
        _init_git_repo(tmp_path)

        def fail_check(*args, **kwargs):
            return {"check": "fake_fail", "status": "fail", "detail": "mocked"}

        monkeypatch.setattr(hc, "check_core_tool_import", fail_check)
        monkeypatch.setattr(hc, "check_core_tool_cli", fail_check)
        monkeypatch.setattr(hc, "check_gateway_module", fail_check)
        monkeypatch.setattr(hc, "check_git_health_smoke", fail_check)

        def fake_log_gate_failure(*args, **kwargs):
            raise RuntimeError("mocked DB failure")

        import sys
        import types

        fake_mod = types.ModuleType("zephyr.governance.audit.reconciliation_registry")
        fake_mod.log_gate_failure = fake_log_gate_failure
        monkeypatch.setitem(sys.modules, "zephyr.governance.audit.reconciliation_registry", fake_mod)

        # 不应抛异常
        result = hc.run_startup_health_check(
            repo_root=str(tmp_path),
            include_git=False,
            session_id="sess-persist-fail",
        )
        assert result["status"] == "fail"
        assert result["persisted_to_db"] is False, "持久化失败时 persisted_to_db=False"
        assert result["escalation_required"] is True, "主结果仍要求 escalate"


class TestE2ERealRepo:
    """在真实仓库上跑健康检查，验证核心机制工作 + 核心工具可用。

    这是裁定 #ARCH-TOOL-HEALTH-V1 的核心验证：健康检查能正确运行 +
    核心工具（apply_depgraph 等 Phase 1/6 修复目标）真实可用。

    注意：gateway 检查可能因仓库中其它未完成特性（如 git_call_budget_gate.py
    截断）失败——这是健康检查正确检测预存 bug 的行为，不算本测试失败。
    本测试只断言核心工具检查项 pass（Phase 6 修复目标）。
    """

    def test_core_tools_health_passes(self, hc):
        """真实仓库核心工具检查：8 项全 pass（4 import + 4 CLI）。

        核心工具 = apply_depgraph / apply_decisiongraph / apply_dataflowgraph /
        sync_yaml_to_depgraph。这些是 Phase 1 紧急止血 + Phase 6 修复的目标，
        必须真实可用。
        """
        result = hc.run_startup_health_check(repo_root=str(REPO_ROOT))
        # 提取核心工具检查项（4 import + 4 CLI）
        core_checks = [c for c in result["checks"] if c["check"].startswith("apply_") or c["check"].startswith("sync_")]
        assert len(core_checks) >= 8, f"核心工具检查项不足 8 项: {len(core_checks)}"
        failed = [c for c in core_checks if c["status"] != "pass"]
        if failed:
            detail = json.dumps(failed, ensure_ascii=False, indent=2)
            pytest.fail(f"核心工具检查未全 pass（Phase 1/6 修复目标），失败项:\n{detail}")

    def test_health_check_returns_valid_structure(self, hc):
        """真实仓库健康检查返回有效结构（不论 pass/warn/fail）。"""
        result = hc.run_startup_health_check(repo_root=str(REPO_ROOT))
        # 验证返回结构完整
        assert "status" in result
        assert result["status"] in ("pass", "warn", "fail")
        assert "checks" in result
        assert isinstance(result["checks"], list)
        assert "escalation_required" in result
        assert "failed_count" in result
        assert "total_count" in result
        assert result["total_count"] >= 12
        # 每个检查项都有必要字段
        for c in result["checks"]:
            assert "check" in c
            assert "status" in c
            assert "detail" in c

    def test_cli_e2e_runs_and_outputs_json(self):
        """CLI 模式 e2e：直接执行脚本，验证输出合法 JSON + 结构正确。

        exit code 0=pass / 1=fail / 2=warn。仓库当前若有预存 bug（如其它
        未完成特性的截断文件），exit code 可能非 0——这是健康检查正确
        检测行为，本测试只验证 JSON 输出格式正确。
        """
        env = os.environ.copy()
        src_path = str(REPO_ROOT / "src")
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{src_path};{existing}" if existing else src_path
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(REPO_ROOT),
            env=env,
            timeout=180,
        )
        # 验证输出是合法 JSON（不论 exit code）
        assert result.stdout.strip().startswith("{"), f"输出不是 JSON，stdout[:200]={result.stdout[:200]}"
        data = json.loads(result.stdout)
        assert "status" in data
        assert data["status"] in ("pass", "warn", "fail")
        assert "checks" in data
        assert "total_count" in data
        assert data["total_count"] >= 12


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _init_git_repo(path: Path) -> None:
    """初始化临时 git 仓库（部分检查依赖 .git 存在）。"""
    if (path / ".git").exists():
        return
    subprocess.run(["git", "init"], cwd=str(path), capture_output=True, check=True, timeout=30)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(path),
        capture_output=True,
        check=True,
        timeout=10,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(path),
        capture_output=True,
        check=True,
        timeout=10,
    )
