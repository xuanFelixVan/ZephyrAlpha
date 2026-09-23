# [A_test] module_id: MOD-GATE_ENGINE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.test_preflight_bare_sql_alignment
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; zephyr.gov_enforcement.commit_gates.bare_sql_gate; zephyr.gov_enforcement.rule_bridge.commit_preflight; zephyr.gov_enforcement.rule_bridge.git_commit_gateway
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_preflight_bare_sql_alignment.py
# [MATURITY] testing
# [INVARIANTS] 全 tmp 隔离（tmp git 仓真 gateway）；红蓝两例钉住 Owner 追加令⑧（st-k4-20260923）：①只含 SQL_* 模块级常量的新增行→预检与锁内同判放行（修复前预检假拦=红）②函数体内裸 SQL f-string→两边同拦（防对齐方向搞反成双双放行）；同调共享判定器 find_bare_sql_violations 后零分裂
# [MODIFY-GUARD] 追加令⑧：bare_sql_gate.find_bare_sql_violations 共享判定器（豁免单点）；commit_preflight._check_inline_no_bare_sql 同调
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_preflight_bare_sql_alignment.py — NO-BARE-SQL 预检/锁内两判一致性红蓝（追加令⑧）。

病根（st-ailayer 批次2 实证）：预检快检只跑 _SQL_PATTERN 正则，缺锁内权威 gate 的
SQL_* 常量/docstring/noqa 豁免——同一个文件预检拦、锁内过，逼施工方 --skip-preflight
绕行（污染账面）。治本=共享判定器 find_bare_sql_violations，两边同调。
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from zephyr.gov_enforcement.commit_gates.bare_sql_gate import make_bare_sql_gate
from zephyr.gov_enforcement.rule_bridge import commit_preflight as cp
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway


def _git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, timeout=60)
    if check and r.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} -> rc={r.returncode}: {r.stderr.decode('utf-8', errors='replace')[:300]}"
        )
    return r


@pytest.fixture()
def gw(tmp_path: Path) -> GitCommitGateway:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "test")
    _git(repo, "config", "core.autocrlf", "false")
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "init")
    return GitCommitGateway(project_root=repo)


def _stage_new(repo: Path, name: str, content: str) -> Path:
    target = repo / name
    target.write_text(content, encoding="utf-8")
    _git(repo, "add", name)
    return target


class TestPreflightLockBareSqlAlignment:
    def test_sql_constant_lines_allowed_by_both(self, gw: GitCommitGateway):
        """红①：模块级 SQL_* 常量定义行=合法集中化——锁内放行，预检必须同判放行
        （修复前预检缺常量豁免假拦，逼 --skip-preflight 绕行）。"""
        repo = Path(gw.project_root)
        target = _stage_new(repo, "m_const.py", 'SQL_INSERT_USER = "INSERT INTO users VALUES (1)"\n')
        ok_lock, detail_lock = make_bare_sql_gate().check(gw, [str(target)])
        assert ok_lock, f"锁内权威判应放行: {detail_lock}"
        ok_pf, detail_pf = cp._check_inline_no_bare_sql(gw, [str(target)])
        assert ok_pf, f"预检必须与锁内同判放行: {detail_pf}"

    def test_function_body_bare_sql_blocked_by_both(self, gw: GitCommitGateway):
        """红②（方向安全钉）：函数体内裸 SQL f-string=真违规——两边必须同拦，
        防对齐搞反变成双双放行。"""
        repo = Path(gw.project_root)
        target = _stage_new(
            repo,
            "m_bad.py",
            'def go(db, uid):\n    return db.execute(f"SELECT * FROM users WHERE id={uid}")\n',
        )
        ok_lock, detail_lock = make_bare_sql_gate().check(gw, [str(target)])
        assert not ok_lock, "锁内权威判应阻断"
        ok_pf, detail_pf = cp._check_inline_no_bare_sql(gw, [str(target)])
        assert not ok_pf, "预检必须与锁内同判阻断"

    def test_docstring_sql_allowed_by_both(self, gw: GitCommitGateway):
        """docstring 中的 SQL 字样=豁免面（锁内 _extract_docstring_lines 同源）。"""
        repo = Path(gw.project_root)
        target = _stage_new(
            repo,
            "m_doc.py",
            'def go(db):\n    """示例: SELECT * FROM users（docstring 非可执行 SQL）"""\n    return db\n',
        )
        ok_lock, detail_lock = make_bare_sql_gate().check(gw, [str(target)])
        assert ok_lock, f"锁内应放行: {detail_lock}"
        ok_pf, detail_pf = cp._check_inline_no_bare_sql(gw, [str(target)])
        assert ok_pf, f"预检必须与锁内同判放行: {detail_pf}"
