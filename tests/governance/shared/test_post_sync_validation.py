# [A_test] module_id: SRC-TST-2116 | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-DATABASE | docs/03_modules/_cross_layer/database/blueprint.md | §task-system
# [MODULE] tests.unit.test_post_sync_validation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
36-scenario permanent regression test for post_sync_validator (SSoT).

守门对象：src/zephyr/governance/post_sync_validator.py —— L1(task_repo) 与
L3(audit_post_sync_commands) 共同复用的 post_sync_standard 校验逻辑唯一真源。

每个场景编码一个红队攻击面；一旦 validate_post_sync_command 发生漂移，
本应 FAIL 的场景会开始返回 None（假阴性），本套件立即捕获。

6 类攻击面 × 4 场景 = 24（R01-R24）：
  - flag 校验精度 (R01-R04)
  - 链式命令拆分 && / || / 换行 (R05-R08)
  - pytest / py_compile 跳过 (R09-R12)
  - 非 .py 命令边界 (R13-R16)
  - 路径绕过 相对/绝对 × 存在/不存在 (R17-R20)
  - shell 解析与 --help 超时 (R21-R24)

W3-T1 扩展（R28-R36，共 9 场景）：
  - post_sync_specific 委托验证 (R28-R30)
  - rollback_instructions 语义校验 (R31-R36)

加载说明：
  SSoT 经 importlib 从文件路径直接加载，绕过 zephyr.governance.__init__
  （其 import 链当前因缺失 zephyr.integration.events 模块而断裂——既有问题，
   非本改造引入）。SSoT 仅依赖 stdlib，直接文件加载合法且印证其解耦价值。

历史根因：D-SIGNAL 改名 20 卡死锁事故——建卡 AI 臆造 apply_depgraph.py
--diagnose，argparse 从未注册该 flag，导致所有卡无法 transition(COMPLETED)。
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest
from zephyr.shared.io.paths import REPO_ROOT

# ----------------------------------------------------------------------------
# SSoT 加载（绕过 zephyr.governance.__init__ import 链断裂）
# ----------------------------------------------------------------------------
# PSV_UNDER_TEST seam：mutation 测试可重定向到变异副本；缺省指向真源。
# 正常 pytest 运行不受影响（加载 src 下真源）。
_PROJECT_ROOT = REPO_ROOT
_DEFAULT_SSOt = _PROJECT_ROOT / "src" / "zephyr" / "governance" / "architecture_governance" / "post_sync_validator.py"
_SSoT_PATH = Path(os.environ.get("PSV_UNDER_TEST", str(_DEFAULT_SSOt)))

_spec = importlib.util.spec_from_file_location(
    "post_sync_validator_under_test", _SSoT_PATH
)
assert _spec is not None and _spec.loader is not None, f"无法加载 SSoT: {_SSoT_PATH}"
_psv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_psv)

validate_post_sync_command = _psv.validate_post_sync_command
validate_post_sync_commands = _psv.validate_post_sync_commands
validate_post_sync_specific = _psv.validate_post_sync_specific
validate_rollback_instructions = _psv.validate_rollback_instructions

# ----------------------------------------------------------------------------
# fixture 路径（注册 --foo / --bar / --baz 三个 flag 的 mock argparse 脚本）
# ----------------------------------------------------------------------------
_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "psv_mock_script.py"
_FIXTURE_REL = "tests/fixtures/psv_mock_script.py"  # 相对于 _PROJECT_ROOT
_SELF_REL = "tests/governance/shared/test_post_sync_validation.py"  # 本文件相对路径（R09 用）
# 第二 fixture：仅注册 --foo（用于 R27 验证链内子命令各自校验自身 --help）
_FIXTURE_ALT = Path(__file__).resolve().parents[1] / "fixtures" / "psv_mock_script_alt.py"


def test_ssoT_module_loaded() -> None:
    """sanity：SSoT 加载成功且导出符合预期。"""
    assert callable(validate_post_sync_command)
    assert callable(validate_post_sync_commands)
    assert callable(validate_post_sync_specific)
    assert callable(validate_rollback_instructions)
    # fixture 必须存在，否则 R01-R08/R11/R17/R19/R22/R24 全部误判
    assert _FIXTURE.exists(), f"fixture 缺失: {_FIXTURE}"


def test_fixture_registers_known_flags() -> None:
    """fixture 的 --help 必须列出 --foo/--bar/--baz。

    若 fixture 被误改导致 flag 丢失，本断言先于 R01-R08 失败，给出明确归因，
    而非让 R02/R03 等场景莫名失败。
    """
    import subprocess

    result = subprocess.run(
        [sys.executable, str(_FIXTURE), "--help"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, f"fixture --help 失败: {result.stderr}"
    help_text = result.stdout + result.stderr
    for flag in ("--foo", "--bar", "--baz"):
        assert flag in help_text, f"fixture 未注册 {flag}"


# ----------------------------------------------------------------------------
# 26 场景 parametrize（R01-R23 + R25-R27）；R24 因需 monkeypatch 单列；
# W3 孪生字段 R28-R36 见 _W3_SCENARIOS（独立 test_w3_scenario，异型 validator）
# ----------------------------------------------------------------------------
# (cmd, expected_none, expected_substr)
#   expected_none=True  → reason 必须 None（命令合法/跳过）
#   expected_none=False → reason 必须非 None，且包含 expected_substr（失败归因）
_SCENARIOS = [
    # === 类1：flag 校验精度 (R01-R04) ===
    pytest.param(
        f"python {_FIXTURE} --nonexistent",
        False,
        "未注册",
        id="R01-hallucinated-flag-rejected",
    ),
    pytest.param(
        f"python {_FIXTURE} --foo value",
        True,
        None,
        id="R02-registered-flag-passes",
    ),
    pytest.param(
        f"python {_FIXTURE} --bar=value",
        True,
        None,
        id="R03-flag-eq-value-format-passes",
    ),
    pytest.param(
        f"python {_FIXTURE}",
        True,
        None,
        id="R04-no-flag-script-passes",
    ),
    # === 类2：链式命令拆分 (R05-R08) ===
    pytest.param(
        f"python {_FIXTURE} --hallucinated && python {_FIXTURE} --foo",
        False,
        "未注册",
        id="R05-chain-and-first-subcommand-fails",
    ),
    pytest.param(
        f"python {_FIXTURE} --foo && python {_FIXTURE} --hallucinated",
        False,
        "未注册",
        id="R06-chain-and-second-subcommand-fails",
    ),
    pytest.param(
        f"python {_FIXTURE} --foo || python {_FIXTURE} --bar",
        True,
        None,
        id="R07-chain-or-both-valid-passes",
    ),
    pytest.param(
        f"python {_FIXTURE} --foo\npython {_FIXTURE} --bar",
        True,
        None,
        id="R08-newline-chain-both-valid-passes",
    ),
    # === 类3：pytest / py_compile 跳过 (R09-R12) ===
    pytest.param(
        f"python -m pytest {_SELF_REL} -v --tb=short",
        True,
        None,
        id="R09-pytest-existing-file-passes",
    ),
    pytest.param(
        "python -m pytest tests/nonexistent_file_xyz.py",
        False,
        "文件不存在",
        id="R10-pytest-missing-file-rejected",
    ),
    pytest.param(
        f"python -m py_compile {_FIXTURE_REL}",
        True,
        None,
        id="R11-py-compile-existing-file-passes",
    ),
    pytest.param(
        "python -m pytest --version",
        True,
        None,
        id="R12-pytest-no-py-target-passes",
    ),
    # === 类4：非 .py 命令边界 (R13-R16) ===
    pytest.param(
        'echo "hello world"',
        True,
        None,
        id="R13-echo-command-passes",
    ),
    pytest.param(
        "git status",
        True,
        None,
        id="R14-git-command-passes",
    ),
    pytest.param(
        "",
        True,
        None,
        id="R15-empty-command-passes",
    ),
    pytest.param(
        "    ",
        True,
        None,
        id="R16-whitespace-only-command-passes",
    ),
    # === 类5：路径绕过 (R17-R20) ===
    pytest.param(
        f"python {_FIXTURE_REL} --foo",
        True,
        None,
        id="R17-relative-existing-path-passes",
    ),
    pytest.param(
        "python tests/fixtures/nonexistent_xyz.py --foo",
        False,
        "脚本不存在",
        id="R18-relative-missing-path-rejected",
    ),
    pytest.param(
        f"python {_FIXTURE} --foo",
        True,
        None,
        id="R19-absolute-existing-path-passes",
    ),
    pytest.param(
        f"python {_FIXTURE.parent / 'nonexistent_xyz.py'} --foo",
        False,
        "脚本不存在",
        id="R20-absolute-missing-path-rejected",
    ),
    # === 类6：shell 解析 (R21-R23)；R24 单列 ===
    pytest.param(
        'python "unterminated quote --foo',
        False,
        "shell 解析失败",
        id="R21-shlex-parse-error-rejected",
    ),
    pytest.param(
        f'python "{_FIXTURE}" --foo',
        True,
        None,
        id="R22-quoted-path-passes",
    ),
    pytest.param(
        "python tests\\fixtures\\psv_mock_script.py --foo",
        True,
        None,
        id="R23-windows-backslash-path-passes",
        marks=pytest.mark.skipif(
            sys.platform != "win32",
            reason="Windows 反斜杠路径语义仅在 win32 下成立",
        ),
    ),
    # === 类7：mutation-testing 反馈加固（R25-R27）===
    # 这三个场景由 W1-T3 mutation testing 暴露的存活变异反推而来，
    # 专门杀灭 M08（链式不拆分）/ M10（单短横误判 flag）/ M14（引号 strip 移除）。
    pytest.param(
        'python "tests/fixtures/nonexistent_xyz.py" --foo',
        False,
        "脚本不存在",
        id="R25-quoted-missing-path-rejected-kills-M14",
    ),
    pytest.param(
        f"python {_FIXTURE} -x",
        True,
        None,
        id="R26-single-dash-token-not-flagged-kills-M10",
    ),
    pytest.param(
        f"python {_FIXTURE} --foo && python {_FIXTURE_ALT} --bar",
        False,
        "未注册",
        id="R27-chain-per-subcommand-flag-isolation-kills-M08",
    ),
]


# ----------------------------------------------------------------------------
# W3 孪生字段场景（R28-R36，共 9 条；独立 parametrize，因 validator 异型）
# (validator_name, text, expected_none, expected_substr)
#   validator_name="specific"  → validate_post_sync_specific（委托 standard）
#   validator_name="rollback"  → validate_rollback_instructions（轻量语义校验）
# ----------------------------------------------------------------------------
_W3_SCENARIOS = [
    # === R28-R30: validate_post_sync_specific（委托 validate_post_sync_command）===
    pytest.param(
        "specific",
        f"python {_FIXTURE} --foo",
        True,
        None,
        id="R28-specific-valid-passes",
    ),
    pytest.param(
        "specific",
        f"python {_FIXTURE} --hallucinated",
        False,
        "未注册",
        id="R29-specific-hallucinated-flag-rejected",
    ),
    pytest.param(
        "specific",
        "git status",
        True,
        None,
        id="R30-specific-non-py-passes",
    ),
    # === R31-R36: validate_rollback_instructions ===
    pytest.param(
        "rollback",
        "",
        False,
        "为空",
        id="R31-rollback-empty-rejected",
    ),
    pytest.param(
        "rollback",
        "回滚",
        False,
        "过短",
        id="R32-rollback-too-short-rejected",
    ),
    pytest.param(
        "rollback",
        "执行 git checkout 撤销所有变更并删除临时文件",
        True,
        None,
        id="R33-rollback-descriptive-passes",
    ),
    pytest.param(
        "rollback",
        "git checkout -- D:\\repo\\file.py 然后恢复备份",
        True,
        None,
        id="R34-rollback-git-command-passes",
    ),
    pytest.param(
        "rollback",
        "运行 python tests/fixtures/nonexistent_xyz.py 重置数据库",
        False,
        "不存在",
        id="R35-rollback-missing-py-rejected",
    ),
    pytest.param(
        "rollback",
        f"运行 python {_FIXTURE_REL} 重置数据库",
        True,
        None,
        id="R36-rollback-existing-py-passes",
    ),
]


@pytest.mark.parametrize("cmd,expected_none,expected_substr", _SCENARIOS)
def test_scenario(cmd: str, expected_none: bool, expected_substr: str | None) -> None:
    """执行单个红队场景。

    expected_none=True  → SSoT 应判定合法，返回 None。
    expected_none=False → SSoT 应判定非法，返回非 None 字符串且含 expected_substr。
    """
    reason = validate_post_sync_command(cmd, _PROJECT_ROOT)
    if expected_none:
        assert reason is None, (
            f"预期通过（reason=None），实际被拒：{reason!r}\n命令: {cmd!r}"
        )
    else:
        assert reason is not None, (
            f"预期拒绝（reason 非 None），实际通过——假阴性！命令: {cmd!r}"
        )
        assert expected_substr is not None
        assert expected_substr in reason, (
            f"失败原因未命中预期子串 {expected_substr!r}；实际: {reason!r}\n命令: {cmd!r}"
        )


@pytest.mark.parametrize("validator_name,text,expected_none,expected_substr", _W3_SCENARIOS)
def test_w3_scenario(
    validator_name: str, text: str, expected_none: bool, expected_substr: str | None
) -> None:
    """W3 孪生字段场景：按 validator_name 路由到 specific / rollback 校验。

    R28-R30 走 validate_post_sync_specific（委托 standard，同型同语义）。
    R31-R36 走 validate_rollback_instructions（轻量语义校验，非命令级）。
    """
    if validator_name == "specific":
        reason = validate_post_sync_specific(text, _PROJECT_ROOT)
    else:
        reason = validate_rollback_instructions(text, _PROJECT_ROOT)
    if expected_none:
        assert reason is None, (
            f"预期通过（reason=None），实际被拒：{reason!r}\n输入: {text!r}"
        )
    else:
        assert reason is not None, (
            f"预期拒绝（reason 非 None），实际通过——假阴性！输入: {text!r}"
        )
        assert expected_substr is not None
        assert expected_substr in reason, (
            f"失败原因未命中预期子串 {expected_substr!r}；实际: {reason!r}\n输入: {text!r}"
        )


def test_R24_help_timeout_does_not_block(monkeypatch: pytest.MonkeyPatch) -> None:
    """--help subprocess 超时不阻断（仅 flag 缺失与脚本不存在阻断）。

    SSoT 设计原则：--help 超时/失败视为不可校验，返回 None 不阻断，
    避免误杀启动慢但有合法 flag 的脚本。用 monkeypatch 注入 TimeoutExpired
    确定性触发该分支，避免真实 15s 超时拖慢套件。
    """
    import subprocess as _sp

    def _fake_run(*args: object, **kwargs: object) -> object:
        raise _sp.TimeoutExpired(
            cmd=args[0] if args and isinstance(args[0], list) else [],
            timeout=0.01,
        )

    monkeypatch.setattr(_psv.subprocess, "run", _fake_run)
    reason = validate_post_sync_command(
        f"python {_FIXTURE} --foo", _PROJECT_ROOT
    )
    assert reason is None, f"--help 超时应不阻断，实际拒绝: {reason!r}"


def test_scenario_count_is_exactly_36() -> None:
    """元测试：场景数必须恰好 36，防止后续误删/误增场景而不自知。

    _SCENARIOS 共 26 条（R01-R23 + R25-R27，走 validate_post_sync_command）；
    _W3_SCENARIOS 共 9 条（R28-R36，走 validate_post_sync_specific / validate_rollback_instructions）；
    R24 因需 monkeypatch 单列为独立函数；合计 36。
    """
    assert len(_SCENARIOS) == 26, (
        f"parametrize 场景数应为 26（R01-R23 + R25-R27），实际 {len(_SCENARIOS)}；"
        f"R24 为独立函数"
    )
    assert len(_W3_SCENARIOS) == 9, (
        f"W3 孪生字段场景数应为 9（R28-R36），实际 {len(_W3_SCENARIOS)}"
    )


def test_validate_post_sync_commands_batch() -> None:
    """批量接口语义：返回 [(cmd, reason|None), ...]，与输入一一对应。"""
    cmds = [
        f"python {_FIXTURE} --foo",                     # pass
        f"python {_FIXTURE} --hallucinated",            # fail
        "echo ok",                                      # pass (non-.py)
    ]
    results = validate_post_sync_commands(cmds, _PROJECT_ROOT)
    assert len(results) == 3
    assert results[0][1] is None, f"R0 应通过: {results[0]!r}"
    assert results[1][1] is not None, "R1 应拒绝（臆造 flag）"
    assert "未注册" in results[1][1]  # type: ignore[operator]
    assert results[2][1] is None, f"R2 应通过: {results[2]!r}"
    # 输入顺序与输出一一对应
    assert [c for c, _ in results] == cmds
