# [A_test] module_id=MOD-GATE_ENGINE_POOL_REGRESSION_DIRECTION_TEST | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.gov.governance.test_pool_regression_direction_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; dataclasses; zephyr.gov_enforcement.commit_gates.registry_mass_deletion_gate（POOL-REGRESSION-DIRECTION 双工厂共台宿主）
# [CONSUMERS] pytest 自动发现；批令二 L3 提交层红绿自证（本门 2026-10-12 首装）
# [STARTUP] python -m pytest tests/gov/governance/test_pool_regression_direction_gate.py
# [MATURITY] testing
# [INVARIANTS] FakeGateway 直供 HEAD/staged 字节，绝不碰真仓与真队列；每台判据先证"能红"（纯驱逐必阻断）再证不误伤（正当改代码/CRLF 口径/新增件/tests/ 一律不得拦）；降级臂必须断言留痕（读不动却不记日志＝闸门静默失效）；越闸头寸必断言留痕（越过无痕＝白名单化）
# [MODIFY-GUARD] 放宽任一臂（strict_subset 不拦 / fail-open 不记日志 / ack 无长度下限）即红
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] tests/gov/governance/test_pool_regression_direction_gate.py
# [TTL] permanent
"""test_pool_regression_direction_gate.py — POOL-REGRESSION-DIRECTION 提交层方向闸测试（批令二 L3）。

病根（实测 2026-10-11 夜，案卷 docs/_working/maint3_campaign/30_pool_rollback_rootcause_casefile.md）：
主区池面发生一次逐件"拍回自己旧版本"的回退弹，28 件里 5 件是 HEAD 的严格真子集；当时
没有任何一台门看得见"字节的方向"，所以写者可以是任何人、账上却查不到。本文件把该形态
钉成能红判据，并钉住四条防假红臂（正当编辑/换行口径/新增件/tests 豁免）。

工厂住在 registry_mass_deletion_gate.py（与 REGISTRY-MASS-DELETION 双工厂共台）——
原因＝commit_gates/ 与 tests/gov/governance/commit_gates/ 平铺件数实测均已达 T_soft=120
硬上限，新建门件即被 FOLDER-CAPACITY-HARD-LIMIT 阻断；测试件落 tests/gov/governance/
（103 件，有余量）而非深目录，是本仓"一级豁免、二级受限"判据下的合法落位。
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from zephyr.gov_enforcement.commit_gates.registry_mass_deletion_gate import (
    _POOL_GATE_ID,
    _pool_direction_pair,
    classify_pool_regression_direction,
    make_pool_regression_direction_gate,
)

HEAD_TEXT = "a\nb\nc\nd\ne\n"  # HEAD 五行
STAGED_PURE_EVICT = "a\nb\n"  # 纯驱逐：删了 3 行、一行没加
STAGED_LEGIT_EDIT = "a\nb\nc\nd\ne\nf\n"  # 只加不删
STAGED_WITH_EXCHANGE = "a\nb\nX\n"  # 有删有加＝mixed


@dataclass
class _Result:
    returncode: int
    stdout: str = ""


class FakeGateway:
    """只实现本门用到的三个 git 面：diff --cached 清单、HEAD 字节、staged 字节（不碰真仓）。"""

    def __init__(self, staged_list: list[str], head: dict[str, str], staged: dict[str, str]) -> None:
        self._list = staged_list
        self._head = head
        self._staged = staged
        self.calls: list[list[str]] = []

    def run_git(self, args: list[str]):
        self.calls.append(list(args))
        joined = " ".join(args)
        if "--diff-filter=M" in joined:
            return _Result(0, "\n".join(self._list))
        if args[-1].startswith("HEAD:"):
            rel = args[-1][len("HEAD:") :]
            return _Result(0, self._head[rel]) if rel in self._head else _Result(1, "")
        if args[-1].startswith(":"):
            rel = args[-1][1:]
            return _Result(0, self._staged[rel]) if rel in self._staged else _Result(1, "")
        return _Result(1, "")


def _gate():
    return make_pool_regression_direction_gate()


def test_direction_pair_and_four_arms():
    """纯函数臂：三档语义 + CRLF 不得被算成驱逐（行尾是第四把口径，在册教训）。"""
    assert _pool_direction_pair(HEAD_TEXT, STAGED_PURE_EVICT) == (3, 0)
    assert classify_pool_regression_direction(HEAD_TEXT, STAGED_PURE_EVICT) == "strict_subset"
    assert classify_pool_regression_direction(HEAD_TEXT, STAGED_LEGIT_EDIT) == "clean"
    assert classify_pool_regression_direction(HEAD_TEXT, STAGED_WITH_EXCHANGE) == "mixed"
    # 近子集：HEAD 独有 24 行、staged 只加 1 行（比值 0.041 ≤0.05）
    big = "".join(f"L{i}\n" for i in range(24))
    assert classify_pool_regression_direction(big, "L0\n") == "strict_subset"
    assert classify_pool_regression_direction(big, "L0\nbrand_new_line\n") == "near_subset"
    # 加了 10 行（比值 0.42）＝mixed，不拦也不 warn
    assert classify_pool_regression_direction(big, "L0\n" + "".join(f"N{i}\n" for i in range(10))) == "mixed"
    assert classify_pool_regression_direction("x\ny\n", "x\r\ny\r\n") == "clean", "纯行尾口径差异被算成驱逐＝假红第四坑"


def test_pure_eviction_blocks_with_prescription():
    gw = FakeGateway(["src/f.py"], {"src/f.py": HEAD_TEXT}, {"src/f.py": STAGED_PURE_EVICT})
    passed, detail = _gate().check(gw, ["src/f.py"], session_id="st-maint3-20261011", commit_message="fix: x")
    assert passed is False, "纯驱逐不拦＝本门白装"
    assert _POOL_GATE_ID in detail and "纯驱逐" in detail
    assert "git checkout HEAD --" in detail, "处方必须先给『改喂闸的输入指向』，不是教人加旗"
    assert "pool-regression-ack" in detail


def test_legit_edit_and_mixed_not_blocked():
    for staged in (STAGED_LEGIT_EDIT, STAGED_WITH_EXCHANGE):
        gw = FakeGateway(["src/f.py"], {"src/f.py": HEAD_TEXT}, {"src/f.py": staged})
        passed, detail = _gate().check(gw, ["src/f.py"], session_id="s", commit_message="feat: x")
        assert passed is True, f"{staged!r} 被误拦＝假红：{detail[:120]}"


def test_new_file_and_unreadable_side_fail_open(caplog):
    """新增件（HEAD 无字节）与读不动一律放行，但**必须留一行**——降级态不得伪装成"无回退"。"""
    gw = FakeGateway(["src/new.py"], {}, {"src/new.py": "only\n"})
    assert _gate().check(gw, ["src/new.py"], session_id="s", commit_message="feat: 新文件")[0] is True
    gw2 = FakeGateway(["src/g.py"], {"src/g.py": HEAD_TEXT}, {})  # staged 读不到
    assert _gate().check(gw2, ["src/g.py"], session_id="s", commit_message="feat: x")[0] is True
    assert any("不可读" in r.getMessage() for r in caplog.records), "读不动却不记日志＝闸门静默失效"


def test_ack_escapes_but_leaves_trace(caplog):
    gw = FakeGateway(["src/f.py"], {"src/f.py": HEAD_TEXT}, {"src/f.py": STAGED_PURE_EVICT})
    passed, _ = _gate().check(
        gw,
        ["src/f.py"],
        session_id="s",
        commit_message="revert: 有意回退 [pool-regression-ack:与属主车道逐件对过账并留档]",
    )
    assert passed is True
    assert any("越过留痕" in r.getMessage() for r in caplog.records), "越过无痕＝白名单化"


def test_short_ack_reason_does_not_escape():
    """理由 <10 字不算申报（防"写个标记就算交代"，形状对齐宿主模块 allow-mass-deletion）。"""
    gw = FakeGateway(["src/f.py"], {"src/f.py": HEAD_TEXT}, {"src/f.py": STAGED_PURE_EVICT})
    passed, _ = _gate().check(gw, ["src/f.py"], session_id="s", commit_message="x [pool-regression-ack:看过]")
    assert passed is False


def test_tests_tree_is_exempt():
    gw = FakeGateway(
        ["tests/research/test_x.py"], {"tests/research/test_x.py": HEAD_TEXT}, {"tests/research/test_x.py": "a\n"}
    )
    assert _gate().check(gw, ["tests/research/test_x.py"], session_id="s", commit_message="test: x")[0] is True
    assert not any("HEAD:tests" in " ".join(c) for c in gw.calls), "tests/ 应根本不进入判定"


def test_no_staged_files_short_circuits():
    assert _gate().check(FakeGateway([], {}, {}), [], session_id="s", commit_message="chore: 空")[0] is True


def test_gate_spec_shape_and_registration_surface():
    """装载面自证：gate_id/priority 在册形态（撞号由 commit_gate_registry 抛错，priority 唯一性另有测）。"""
    spec = _gate()
    assert spec.gate_id == _POOL_GATE_ID
    assert spec.priority == 161, "161＝治理簇尾 160 之后的实测空段，换号须重查占用"
    assert callable(spec.check)


@pytest.mark.parametrize(
    "bad",
    [
        ("x\ny\nz\n", "x\n"),
        (HEAD_TEXT, STAGED_PURE_EVICT),
        (HEAD_TEXT, ""),
    ],
)
def test_classify_never_returns_clean_when_head_lines_are_missing(bad):
    head, staged = bad
    assert classify_pool_regression_direction(head, staged) in {"strict_subset", "near_subset", "mixed"}


def test_duplicate_lines_do_not_manufacture_a_regression():
    """行集合口径与在册三方尺同源：重复行不产生"HEAD 独有行"，有新增行即非纯驱逐。"""
    assert classify_pool_regression_direction("\n".join(["a"] * 3) + "\n", "a\nb\n") == "clean"
