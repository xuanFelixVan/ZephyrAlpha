# [TTL] permanent
"""热册陈旧快照抹条目守门测试（A-12 治本，st-chiefc-20261009）。

病情（死信专车实弹 2026-10-09）：capability 册 64k 行整档快照在「入队→落地」窗内
被别道陈旧字节压制——5 条 token 三次被抹，死信持续再产根因。两条封堵面：

1. 落地侧：three_way_merge_registry_yaml 严格快进短路（base==ours 字节相等→整文件
   取 theirs）加条目级守门——theirs 相对 base 丢条目 → 拒绝快进，落回条目级合并
   （ours/base 条目保留）。能红证据：修复前 base==ours 时直接返回 theirs（Y 被抹）。
2. 直提侧：REGISTRY-YAML-PARSE 对 capability 册加 token 级只增不减守门——HEAD 顶层
   creation_tokens 复合身份（file|token=）相对 staged 差集非空 → 阻断（投影指纹只证
   staged==PG 投影，不证投影未落后 HEAD）；白名单=[allow-mass-deletion:reason≥10字]。
   能红证据：修复前该门只查结构+指纹，陈旧 render 直提整档覆盖照过。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))  # noqa: E402

from commit_queue_landing import (  # noqa: E402
    _split_registry_entries,
    _theirs_drops_base_entries,
    three_way_merge_registry_yaml,
)

_REL = "docs/01_policies_and_standards/_registry/catalogs/_stale_guard_test_registry.yaml"

# 场景基元（总队令原样）：base 有 X+Y，theirs=陈旧快照只有 X，ours=X+Y
_BASE_XY = """module_id: REG-STALE-GUARD
items:
- key: x
  value: shared
- key: y
  value: landed_by_other_lane
"""
_THEIRS_X = """module_id: REG-STALE-GUARD
items:
- key: x
  value: shared
"""


# ── 落地侧：快进守门 ──────────────────────────────────────────────────────────
def test_stale_snapshot_ff_refused_entry_y_kept() -> None:
    """base==ours 且 theirs 丢条目 → 拒绝整文件快进，条目级合并保住 Y（修复前返回 theirs=Y 被抹）。"""
    merged, err = three_way_merge_registry_yaml(_BASE_XY, _BASE_XY, _THEIRS_X, rel_path=_REL)
    assert not err, f"守门后应落回条目级合并不死信: {err}"
    assert "key: y" in merged, "陈旧快照不得抹掉他道已落条目（修复前此处置直接被抹）"
    assert merged == _BASE_XY, "纯陈旧袋（只丢不增）合并结果应等于 ours（合法 noop 载体）"


def test_stale_snapshot_with_addition_keeps_y_and_adds_z() -> None:
    """theirs=陈旧快照+本袋真新增 → Y 保留且 Z 照插（守门不得误杀陈旧袋的合法增量）。"""
    theirs = _THEIRS_X + "- key: z\n  value: bag_new\n"
    merged, err = three_way_merge_registry_yaml(_BASE_XY, _BASE_XY, theirs, rel_path=_REL)
    assert not err, f"不应死信: {err}"
    assert "key: y" in merged, "Y 保留"
    assert "key: z" in merged and "bag_new" in merged, "本袋新增 Z 必须落地"


# 真形态合成样：capability 册 creation_tokens 条目（file+token → 复合身份 file=..|token=..）
_TOKENS_REL = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"
_TOKENS_BASE = """schema_version: 1
creation_tokens:
- file: docs/_working/a.md
  token: tok-a
- file: docs/_working/b.md
  token: tok-b
di_seam_exemptions: []
"""
_TOKENS_STALE = """schema_version: 1
creation_tokens:
- file: docs/_working/a.md
  token: tok-a
di_seam_exemptions: []
"""


def test_token_composite_identity_stale_snapshot_kept() -> None:
    """端到端（真形态复合身份）：陈旧快照抹他道 token → 快进拒绝落回条目合并，token 保留。"""
    merged, err = three_way_merge_registry_yaml(_TOKENS_BASE, _TOKENS_BASE, _TOKENS_STALE, rel_path=_TOKENS_REL)
    assert not err, f"守门后应落回条目级合并: {err}"
    assert "tok-b" in merged, "他道已落 token 不得被陈旧快照抹掉（修复前此处置整档覆盖直接抹）"


def test_ff_no_drops_still_whole_file() -> None:
    """theirs 相对 base 只增不减 → 快进整文件取 theirs（守门不拖慢合法快进主路径）。"""
    theirs = _BASE_XY + "- key: z\n  value: bag_new\n"
    merged, err = three_way_merge_registry_yaml(_BASE_XY, _BASE_XY, theirs, rel_path=_REL)
    assert not err and merged == theirs, "无丢条目 → 快进路径逐字节取 theirs 不变"


def test_guard_decision_function_shape() -> None:
    """判定函数直测：丢条目→missing 非空；只增→空；base 切不了→fail-open 语义。"""
    missing, err = _theirs_drops_base_entries(_BASE_XY, _THEIRS_X, None)
    assert err is None and missing == {"items:key=y"}, f"丢 Y 应被发现（x 仍在）: missing={missing}"
    missing2, err2 = _theirs_drops_base_entries(_BASE_XY, _BASE_XY + "- key: z\n  value: n\n", None)
    assert err2 is None and not missing2, "只增不减 → missing 空"
    anchored = "a: &k\n  - 1\nb:\n- x: *k\n"
    missing3, err3 = _theirs_drops_base_entries(anchored, _THEIRS_X, None)
    assert missing3 == set() and err3 is not None, "锚点 base 判不了 → err 非 None（调用方 fail-open 保快进）"


@pytest.mark.timeout(110)
def test_real_capability_registry_head_guard_detects_stale() -> None:
    """真册实测：以 HEAD capability 册为 base，陈旧快照抹掉末位 token → 判定函数发现丢失。

    真册 64k 行单侧切分 ~24s，端到端三向合并超单测时窗——全链路拒绝语义由上方
    合成真形态用例钉扎，此处钉「真册数据上判定函数发现真丢失」这一环。
    """
    rel = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"
    head = subprocess.run(
        ["git", "show", f"HEAD:{rel}"], capture_output=True, text=True, encoding="utf-8", check=True
    ).stdout
    head_fams, err = _split_registry_entries(head, None)
    assert not err and "creation_tokens" in head_fams, "HEAD 册应可切分"
    ct_fam = head_fams["creation_tokens"]
    assert ct_fam.blocks, "HEAD 册应有 token 条目"
    victim = ct_fam.blocks[-1]  # 末位 token 为假想「他道已落条目」
    assert victim.identity, "token 条目应有复合身份"
    lines = head.splitlines(keepends=True)
    stale_text = "".join(lines[: victim.start] + lines[victim.end + 1 :])  # 陈旧快照=抹掉该条
    missing, guard_err = _theirs_drops_base_entries(head, stale_text, None)
    assert guard_err is None, f"真册两侧应可切分: {guard_err}"
    assert missing == {f"creation_tokens:{victim.identity}"}, f"被抹 token 必须被发现: {sorted(missing)[:3]}"


# ── 直提侧：REGISTRY-YAML-PARSE token 级只增不减守门 ─────────────────────────
_WATCH = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"


def _reg_yaml(tokens: list[tuple[str, str]]) -> str:
    """最小合法 capability 册（exemptions 末位+creation_tokens list 结构断言全过）。"""
    entries = "".join(f"  - file: {f}\n    token: {t}\n" for f, t in tokens)
    return f"schema_version: 1\ncapabilities: []\ncreation_tokens:\n{entries}di_seam_exemptions: []\n"


class _FakeGateway:
    """run_git 三应答：staged 清单 / staged 内容 / HEAD 内容；project_root=tmp（审计落 tmp）。"""

    def __init__(self, root: Path, head_text: str | None, staged_text: str):
        self.project_root = root
        self._head = head_text
        self._staged = staged_text

    def run_git(self, args: list[str]):
        class _R:
            def __init__(self, returncode: int, stdout: str = ""):
                self.returncode = returncode
                self.stdout = stdout

        if args[:2] == ["git", "diff"] and "--cached" in args:
            return _R(0, _WATCH + "\n")
        if args[:2] == ["git", "show"] and args[2].startswith("HEAD:"):
            if self._head is None:
                return _R(1)
            return _R(0, self._head)
        if args[:2] == ["git", "show"] and args[2].startswith(":"):
            return _R(0, self._staged)
        return _R(1)


def _run_gate(tmp_path: Path, head: str | None, staged: str, message: str = "") -> tuple[bool, str]:
    from zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate import make_registry_yaml_parse_gate

    gate = make_registry_yaml_parse_gate()
    return gate.check(_FakeGateway(tmp_path, head, staged), [_WATCH], commit_message=message)  # type: ignore[attr-defined]


def test_direct_commit_wiping_head_token_blocked(tmp_path: Path) -> None:
    """HEAD 有 T1+T2，staged 投影只 render 出 T1（PG 滞后）→ 直提阻断。"""
    passed, msg = _run_gate(
        tmp_path, _reg_yaml([("docs/a.md", "tok-1"), ("docs/b.md", "tok-2")]), _reg_yaml([("docs/a.md", "tok-1")])
    )
    assert not passed, "抹 token 的直提必须阻断"
    assert "相对 HEAD 少 1 条" in msg and "tok-2" in msg, f"阻断信息应指认被抹 token: {msg}"


def test_direct_commit_with_marker_allowed(tmp_path: Path) -> None:
    """合法退役（PG retire 已对账）→ [allow-mass-deletion:reason≥10字] 放行。"""
    passed, msg = _run_gate(
        tmp_path,
        _reg_yaml([("docs/a.md", "tok-1"), ("docs/b.md", "tok-2")]),
        _reg_yaml([("docs/a.md", "tok-1")]),
        message="[allow-mass-deletion:PG已retire的tok-2账实同步退役]",
    )
    assert passed, f"标记放行失败: {msg}"


def test_direct_commit_superset_staged_passes(tmp_path: Path) -> None:
    """staged 相对 HEAD 只增（新 token 到位）→ 放行（正常 render-sync 主路径）。"""
    passed, msg = _run_gate(
        tmp_path,
        _reg_yaml([("docs/a.md", "tok-1")]),
        _reg_yaml([("docs/a.md", "tok-1"), ("docs/c.md", "tok-3")]),
    )
    assert passed, f"只增提交不应阻断: {msg}"


def test_direct_commit_head_missing_fail_open(tmp_path: Path) -> None:
    """HEAD 无此文件（首挂）/读取失败 → fail-open 不误报。"""
    passed, msg = _run_gate(tmp_path, None, _reg_yaml([("docs/a.md", "tok-1")]))
    assert passed, f"fail-open 失败: {msg}"


@pytest.mark.parametrize(
    "text,expect_ids",
    [
        pytest.param(_reg_yaml([("docs/a.md", "tok-1")]), {"docs/a.md|token=tok-1"}, id="normal_token"),
        pytest.param("schema_version: 1\ncapabilities: []\n", None, id="no_creation_tokens"),
        pytest.param("broken: [unclosed\n", None, id="unparseable"),
    ],
)
def test_creation_token_identities_shape(text: str, expect_ids: set[str] | None) -> None:
    from zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate import _creation_token_identities

    got = _creation_token_identities(text)
    if expect_ids is None:
        assert got is None or got == {}, f"应判不了: {got}"
    else:
        assert got is not None and set(got) == expect_ids
