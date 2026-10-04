# [A_test] module_id: MOD-GOV_register_asset_cli | layer=test | stability=evolving
# [TTL] task_bound
"""test_register_asset_cli —— 上户口合一命令 CLI smoke 测试（裁定#480 C-2 手术1）。

全部用例零副作用：--help 干跑 / 内部函数 tmp_path 单测 / monkeypatch 子进程
替身（绝不真写 token 册/翻译册/depgraph DB）。
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = REPO_ROOT / "scripts" / "governance" / "register_asset.py"

_spec = importlib.util.spec_from_file_location("register_asset", _SCRIPT)
ra = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("register_asset", ra)
_spec.loader.exec_module(ra)


def test_cli_help_smoke() -> None:
    """CLI smoke：--help 退出 0 且暴露五步/逃生参数。"""
    r = subprocess.run(
        [sys.executable, str(_SCRIPT), "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(REPO_ROOT),
    )
    assert r.returncode == 0
    for kw in ("--path", "--session", "--plain", "--capability", "--skip"):
        assert kw in r.stdout


def test_header_check_missing_fields_prints_template(tmp_path: Path) -> None:
    """⑤ 头校验：缺字段 .py 检出缺失+按真源机生模板（判据动态读非手写）。"""
    py = tmp_path / "mymod.py"
    py.write_text(
        "# [BLUEPRINT] MOD-X | x | §\n# [MODULE] mymod\n# [DOMAIN] D_GOV_SCRIPTS\nprint(1)\n",
        encoding="utf-8",
    )
    missing, template = ra.check_module_header(py)
    assert missing  # 只有 3 字段必缺
    assert all(t.startswith("# [") for t in template)
    assert len(template) == len(ra.header_required_fields())  # 模板=真源全字段
    # 非 .py 无头契约 → 通过
    md = tmp_path / "notes.md"
    md.write_text("hello", encoding="utf-8")
    assert ra.check_module_header(md)[0] == []


def test_skip_all_dry_run_zero_side_effect() -> None:
    """全 --skip：五步留痕跳过、exit 0（零子进程副作用的干跑通道）。"""
    rc = ra.register_asset(
        "src/zephyr/governance/never_made.py",
        "st-test-cli",
        "大白话：这是测试用假路径，只验证编排不验证登记。",
        skips=ra.STEP_ORDER,
    )
    assert rc == 0


def test_step_failure_nonzero_with_done_echo(monkeypatch) -> None:
    """任一步失败=exit 2+已办步骤回显+后续步骤不跑（半程状态可见）。"""
    calls: list[str] = []

    def fake_token(*a, **k):
        calls.append("token")
        return 0, "OK token"

    def fake_translation(*a, **k):
        calls.append("translation")
        return 2, "VALIDATION_ERROR plain_zh 校验失败"

    monkeypatch.setattr(ra, "_step_token", fake_token)
    monkeypatch.setattr(ra, "_step_translation", fake_translation)
    monkeypatch.setattr(ra, "_step_depgraph", lambda *a, **k: (_ for _ in ()).throw(AssertionError("不应到达")))
    monkeypatch.setattr(ra, "_step_generate", lambda: (_ for _ in ()).throw(AssertionError("不应到达")))
    monkeypatch.setattr(ra, "_step_header", lambda p: (_ for _ in ()).throw(AssertionError("不应到达")))

    rc = ra.register_asset(
        "src/zephyr/governance/fake.py",
        "st-test-cli",
        "大白话：验证失败路径的编排行为。",
        domain="D_GOV_SCRIPTS",
    )
    assert rc == ra.EXIT_STEP_FAILED
    assert calls == ["token", "translation"]  # 失败即止，depgraph/generate/header 未跑


def test_bad_skip_name_rejected() -> None:
    """--skip 未知步骤名=usage 失败（exit 1），防手滑逃生。"""
    rc = ra.main(
        [
            "--path",
            "src/x.py",
            "--session",
            "st-t",
            "--plain",
            "大白话：参数校验测试。",
            "--skip",
            "nonsense",
        ]
    )
    assert rc == ra.EXIT_USAGE
