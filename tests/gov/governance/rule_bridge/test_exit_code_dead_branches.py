"""D11-G01 退出码死分支回归钉（st-sO2-probe-20261004 手术2-G01）。

考古结论（2026-10-04，车道O）：
- scripts/git_commit.py _COMMIT_RESULT_MAP 中 SSOT_VIOLATION→4 与 STASH_CONFLICT→2
  两支零生产者（全仓无 CommitStatus 构造点；gateway 枚举 STASH_CONFLICT 行自述
  「阶段3 已弃用，保留向后兼容」）。
- task_repo.py 的 elif STASH_CONFLICT 分派=孤儿消费支（永不触发）。
- 处置=注记不修：退役/补生产者决策权在总包（内收判据「零触发零消费→退役」适用）。

本套件把上述事实钉死：
1. 专码映射钉——SSOT_VIOLATION=4、STASH_CONFLICT=2、OK=0（有人改码必须过这里）；
2. 零生产者守卫——复用图11 生成器单源扫描器 scan_commit_status_producers（同口径
   =图11 machine_facts.exit_code_producers，禁第二真源）；一旦有人补生产者，本测变红
   ⇒ 提醒同步更新图11 D11-G01 gap 节点档案；
3. 注记锚钉——三处 [D11-G01 注记] 在盘（git_commit.py/gateway 枚举/task_repo 孤儿支）。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]


def _import_cli_map():
    sys.path.insert(0, str(_REPO / "scripts"))
    import git_commit as cli

    return cli


def _import_generator():
    sys.path.insert(0, str(_REPO / "scripts" / "governance" / "d5_architecture" / "generators"))
    sys.path.insert(0, str(_REPO / "scripts" / "governance" / "d5_architecture" / "validators"))
    sys.path.insert(0, str(_REPO / "scripts" / "governance"))
    import generate_dev_delivery_map as gen

    return gen


def test_green_dead_branch_exit_codes_pinned():
    """专码钉：SSOT_VIOLATION→4、STASH_CONFLICT→2、OK→0（改动必须显式过测）。"""
    from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import CommitStatus

    cli = _import_cli_map()
    m = cli._COMMIT_RESULT_MAP
    assert m[CommitStatus.SSOT_VIOLATION][0] == 4, "SSOT_VIOLATION 专码=4（图11 exit_codes 面）"
    assert m[CommitStatus.STASH_CONFLICT][0] == 2, "STASH_CONFLICT 专码=2（与 LOCK_TIMEOUT 同码段）"
    assert m[CommitStatus.OK][0] == 0
    # 模板占位符完整性（死分支也是已登记契约面，模板坏了 CLI 渲染会 KeyError）
    assert "SSOT_VIOLATION: {message}" in m[CommitStatus.SSOT_VIOLATION][1]
    assert "stash_ref={stash_ref}" in m[CommitStatus.STASH_CONFLICT][2]


def test_green_zero_producers_guard():
    """零生产者守卫：复用图11 单源扫描器——两状态生产者计数恒 0。

    变红含义：有人给 SSOT_VIOLATION/STASH_CONFLICT 补了生产者（status=CommitStatus.X
    构造）⇒ 死分支复活 ⇒ 必须同步更新图11 D11-G01 gap 节点与三处注记再过测。
    """
    gen = _import_generator()
    counts = gen.scan_commit_status_producers(_REPO)
    assert counts.get("SSOT_VIOLATION") == 0, (
        f"SSOT_VIOLATION 出现生产者={counts['SSOT_VIOLATION']}——D11-G01 档案需同步"
    )
    assert counts.get("STASH_CONFLICT") == 0, (
        f"STASH_CONFLICT 出现生产者={counts['STASH_CONFLICT']}——D11-G01 档案需同步"
    )


def test_green_d11_g01_annotations_anchored():
    """注记锚钉：三处 [D11-G01 注记] 在盘（考古结论不许静默蒸发）。"""
    spots = {
        "scripts/git_commit.py": r"\[D11-G01 死分支注记.*零生产者",
        "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py": r"SSOT_VIOLATION.*\[D11-G01 死分支\].*零构造点",
        "src/zephyr/governance/persistence/task_repo.py": r"\[D11-G01 孤儿消费支.*零生产者",
    }
    for rel, pat in spots.items():
        text = (_REPO / rel).read_text(encoding="utf-8")
        assert re.search(pat, text, re.DOTALL), f"{rel} 缺 D11-G01 注记（或注记被删）"
