# [TTL] permanent
# [BLUEPRINT] MOD-GOV-116 | tests/governance/test_commit_claim_check.py | commit_claim_check 红蓝例
"""commit_claim_check 红蓝例：缺陷类拦截 + 四条逃生 + 边界不误报。"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from governance.commit_claim_check import (  # noqa: E402
    bag_code_files,
    check_message_claims,
    claimed_code_paths,
)


def test_red_bag_empty_but_message_claims_code():
    """红例：消息声称改 fire_grid.py，袋里只有 .md → 拦截并给处方。"""
    msg = "[st-x] F1 修复：scripts/backtest/fexam/grid_adapter/fire_grid.py 的 _t3series_logs_stale 改真源路径"
    out = check_message_claims(msg, ["docs/_working/notes.md"])
    assert out is not None
    assert "MESSAGE-CLAIMS-CODE-BAG-EMPTY" in out
    assert "fire_grid.py" in out
    assert "[docs-only]" in out  # 处方含逃生指令


def test_green_code_in_bag():
    """蓝例：袋里有代码文件 → 放行（不逐文件核对，v1 只拦袋零代码缺陷类）。"""
    msg = "[st-x] 修复 fire_grid.py 与 ch_data.py:212 regime_series"
    assert check_message_claims(msg, ["scripts/backtest/fexam/grid_adapter/fire_grid.py"]) is None


def test_green_tests_count_as_code():
    """蓝例：gate+自家测试同批合法——袋里只有 tests/*.py 也放行。"""
    msg = "[st-x] 新增 test_fire_grid_gates.py 回归"
    assert check_message_claims(msg, ["tests/backtest/fexam/test_fire_grid_gates.py"]) is None


def test_docs_only_marker_escape():
    """逃生①：[docs-only] 显式申报（大小写不敏感）→ 引用代码路径也放行。"""
    msg = "[DOCS-ONLY] 翻牌册：记录 6b3426c398 已落 fire_grid.py 18 件"
    assert check_message_claims(msg, ["docs/_working/matrix_campaign/master_backlog_v2.md"]) is None


def test_no_code_mention_no_trigger():
    """边界：消息不含代码路径（纯散文/无扩展名）→ 放行。"""
    msg = "[st-x] 文档更新：治理缺陷修复六车道战报与回执归档"
    assert check_message_claims(msg, ["docs/_working/notes.md"]) is None


def test_backtick_without_slash_still_claimed():
    """判据：反引号 token 不要求含 /——`fire_grid.py` 也算声称。"""
    assert claimed_code_paths("修复 `fire_grid.py` 的 G1 门") == ["fire_grid.py"]


def test_bare_token_requires_slash():
    """判据：裸 token 须含 /（防散文零散提及误报）；含 / 即捕获。"""
    assert claimed_code_paths("改动见 ch_data.py 与 scripts/backtest/fexam/ch_data.py") == [
        "scripts/backtest/fexam/ch_data.py"
    ]


def test_bag_code_files_extensions():
    """袋代码判定：.py/.yaml 算代码，.md/.txt/.log 不算；反斜杠路径归一。"""
    files = ["a\\b\\x.py", "cfg.yaml", "readme.md", "run.log", "notes.txt"]
    assert bag_code_files(files) == ["a\\b\\x.py", "cfg.yaml"]


def test_version_boundary_not_overmatched():
    """边界：:212 行号、版本号尾巴不破匹配（: 截断）。"""
    claims = claimed_code_paths("ch_data.py:212 regime_series 已修")
    assert claims == []  # 裸 token 无 / 不捕；反引号无 → 不触发

    claims2 = claimed_code_paths("`ch_data.py:212` 附近")
    assert claims2 == ["ch_data.py:212"] or claims2 == []
    # 无论哪种形态，袋零代码时该消息是否拦截取决于是否带斜杠——本例无斜杠不拦
    assert check_message_claims("ch_data.py:212 regime_series 已修", ["a.md"]) is None


def test_cli_exit_codes(tmp_path, monkeypatch):
    """CLI：违规 exit 3，放行 exit 0，[docs-only] exit 0。"""
    from governance.commit_claim_check import main

    mf = tmp_path / "msg.txt"
    mf.write_text("修复 scripts/x/y.py 的缺陷", encoding="utf-8")
    assert main(["--message-file", str(mf), "--files", "docs/a.md"]) == 3
    assert main(["--message-file", str(mf), "--files", "scripts/x/y.py"]) == 0
    mf2 = tmp_path / "msg2.txt"
    mf2.write_text("[docs-only] 记录 scripts/x/y.py 历史", encoding="utf-8")
    assert main(["--message-file", str(mf2), "--files", "docs/a.md"]) == 0
