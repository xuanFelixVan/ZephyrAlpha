# [A_test] module_id: zephyr.ai_layer.redline.negative_list_gates | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ai_layer.redline.test_negative_list_gates
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; zephyr.ai_layer.redline.negative_list_gates
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/ai_layer/redline/test_negative_list_gates.py
# [MATURITY] testing
# [INVARIANTS] 验收标准（DESIGN 红蓝 R1-F4）：S2 负面清单 gate=违例样例被拦；六条各有一条
#              样例（NL-2 QMT" "_REAL 引用/NL-5 判据字段结构变更/NL-3 宪法超行）+白名单放行+
#              fail-open+外来 staged 不阻断；审计经 project_root=tmp_path 隔离
# [MODIFY-GUARD] —
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_negative_list_gates.py — S2 负面清单 gate 组（三台）单测。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.ai_layer.redline.negative_list import REAL_KEY_MARKER
from zephyr.ai_layer.redline.negative_list_gates import (
    _REAL_KEY_ADMISSION,
    CONSTITUTION_LINE_LIMIT,
    RULING_REGISTRY_REL,
    make_constitution_line_limit_gate,
    make_real_key_reference_scan_gate,
    make_task_order_docs_lock_gate,
    scan_constitution_lines,
    scan_real_key_hits,
    structural_field_changes,
    task_order_lock_violation,
)

TASK_HEAD = (
    "task_id: TO-0001\ndefinition_of_done:\n  - 交付 A\nred_lines:\n  - 不碰 B\nacceptance:\n  tests_pass: true\n"
)
TASK_CHANGED = TASK_HEAD.replace("交付 A", "交付 A+顺手改判据")


def test_real_key_reference_blocked(tmp_path: Path, fake_gateway_factory):
    """NL-2 样例：own-diff 源码出现 QMT" "_REAL 引用 → 硬阻断+审计。"""
    gateway = fake_gateway_factory(staged={"src/zephyr/demo/loader.py": "KEY = '" + REAL_KEY_MARKER + "_PATH'\n"})
    passed, detail = make_real_key_reference_scan_gate().check(gateway, ["src/zephyr/demo/loader.py"], session_id="s1")
    assert passed is False
    assert REAL_KEY_MARKER in detail
    audit = tmp_path / ".runtime/gate_audit/real_key_reference_scan.jsonl"
    assert audit.exists()
    record = json.loads(audit.read_text(encoding="utf-8").splitlines()[0])
    assert record["action"] == "block" and record["rule_id"] == "NL-2"


def test_real_key_whitelist_secret_registry_and_secrets_md(fake_gateway_factory):
    """NL-2 白名单：secret_registry.yaml 本体与 SECRETS.md 文档行放行。"""
    gateway = fake_gateway_factory(
        staged={
            "config/secret_registry.yaml": REAL_KEY_MARKER + "_PATH: {category: config}\n",
            "docs/SECRETS.md": "# 实盘键现名 " + REAL_KEY_MARKER + "_PATH（文档行）\n",
        }
    )
    passed, detail = make_real_key_reference_scan_gate().check(
        gateway,
        ["config/secret_registry.yaml", "docs/SECRETS.md"],
        session_id="s1",
    )
    assert passed is True and detail == ""


def test_real_key_foreign_staged_not_blocking(fake_gateway_factory):
    """§3.1 own-scope：外来 staged 违规 warn+审计，不阻断无辜提交人。"""
    gateway = fake_gateway_factory(staged={"other_session/leak.py": "x = '" + REAL_KEY_MARKER + "_ACCOUNT'\n"})
    passed, detail = make_real_key_reference_scan_gate().check(gateway, ["mine.py"], session_id="s-mine")
    assert passed is True and detail == ""


def test_scan_real_key_hits_pure():
    hits = scan_real_key_hits(
        {
            "a.py": REAL_KEY_MARKER + " here",
            "SECRETS.md": REAL_KEY_MARKER + " doc",
            "b.py": "clean",
        }
    )
    assert hits == ["a.py"]


def test_task_order_docs_lock_blocked_when_judging_own_criteria(tmp_path: Path, fake_gateway_factory):
    """NL-5 样例：own-diff 同含施工产物与任务书判据字段结构变更 → 阻断。"""
    gateway = fake_gateway_factory(
        staged={
            "tasks/TO-0001.yaml": TASK_CHANGED,
            "src/zephyr/demo/feature.py": "print('artifact')\n",
        },
        head={"tasks/TO-0001.yaml": TASK_HEAD},
    )
    passed, detail = make_task_order_docs_lock_gate().check(
        gateway, ["tasks/TO-0001.yaml", "src/zephyr/demo/feature.py"], session_id="s1"
    )
    assert passed is False
    assert "definition_of_done" in detail


def test_task_order_change_without_artifacts_allowed_with_audit(tmp_path: Path, fake_gateway_factory):
    """NL-5 近傍：只改任务书不带施工产物 → 放行+near_miss 审计（供 S7/S8 消费）。"""
    gateway = fake_gateway_factory(
        staged={"tasks/TO-0002.yaml": TASK_CHANGED},
        head={"tasks/TO-0002.yaml": TASK_HEAD},
    )
    passed, detail = make_task_order_docs_lock_gate().check(gateway, ["tasks/TO-0002.yaml"], session_id="s1")
    assert passed is True and detail == ""
    audit = tmp_path / ".runtime/gate_audit/task_order_docs_lock.jsonl"
    record = json.loads(audit.read_text(encoding="utf-8").splitlines()[0])
    assert record["action"] == "near_miss_warn"


def test_task_order_new_card_is_preregistration_allowed(fake_gateway_factory):
    """新任务书（HEAD 无基线）=判据预注册动作 → 放行（结构性变更判据不适用）。"""
    gateway = fake_gateway_factory(
        staged={
            "tasks/TO-0003.yaml": TASK_HEAD,
            "src/zephyr/demo/feature.py": "x = 1\n",
        }
    )
    passed, _ = make_task_order_docs_lock_gate().check(
        gateway, ["tasks/TO-0003.yaml", "src/zephyr/demo/feature.py"], session_id="s1"
    )
    assert passed is True


def test_structural_field_changes_is_parse_level_not_string_level():
    """解析级 diff：键序重排等字符串级差异不判变更；字段值结构变化才判。"""
    reformatted = (
        "task_id: TO-0001\nred_lines:\n  - 不碰 B\ndefinition_of_done:\n  - 交付 A\nacceptance:\n  tests_pass: true\n"
    )
    assert structural_field_changes(TASK_HEAD, reformatted) == []
    assert structural_field_changes(TASK_HEAD, TASK_CHANGED) == ["definition_of_done"]
    assert structural_field_changes(None, TASK_HEAD) == [], "新任务书=预注册，返回空"
    assert structural_field_changes(TASK_HEAD, "\t: : :\n") == [], "YAML 坏 → fail-open 空"


def test_task_order_lock_violation_pure():
    assert task_order_lock_violation(["definition_of_done"], True) is True
    assert task_order_lock_violation(["definition_of_done"], False) is False
    assert task_order_lock_violation([], True) is False


def test_constitution_line_limit_blocked_over_300(tmp_path: Path, fake_gateway_factory):
    """NL-3 判据②样例：AGENTS.md 修改后 301 行 → 阻断。"""
    over = "\n".join(f"line {i}" for i in range(CONSTITUTION_LINE_LIMIT + 1))
    gateway = fake_gateway_factory(staged={"AGENTS.md": over})
    passed, detail = make_constitution_line_limit_gate().check(gateway, ["AGENTS.md"], session_id="s1")
    assert passed is False
    assert f">{CONSTITUTION_LINE_LIMIT}" in detail


def test_constitution_line_limit_allows_exactly_300(fake_gateway_factory):
    exact = "\n".join(f"line {i}" for i in range(CONSTITUTION_LINE_LIMIT))
    gateway = fake_gateway_factory(staged={"AGENTS.md": exact})
    passed, detail = make_constitution_line_limit_gate().check(gateway, ["AGENTS.md"], session_id="s1")
    assert passed is True and detail == ""


def test_constitution_lines_pure_counts():
    assert scan_constitution_lines("a\nb\nc") == 3
    assert scan_constitution_lines("") == 0


def test_git_failure_fail_open(fake_gateway_factory):
    """git diff 失败 → fail-open 放行（check 永不抛，交 gate 框架健康面）。"""

    class BrokenGateway:
        project_root = "."

        def run_git(self, args):  # noqa: ARG002
            raise RuntimeError("git unavailable")

    passed, detail = make_real_key_reference_scan_gate().check(BrokenGateway(), [], session_id="s1")
    assert passed is True and detail == ""


def test_gate_specs_shape():
    for factory, gate_id, priority in (
        (make_real_key_reference_scan_gate, "REAL-KEY-REFERENCE-SCAN", 149),
        (make_task_order_docs_lock_gate, "TASK-ORDER-DOCS-LOCK", 150),
        (make_constitution_line_limit_gate, "CONSTITUTION-LINE-LIMIT", 151),
    ):
        spec = factory()
        assert spec.gate_id == gate_id
        assert spec.priority == priority
        assert callable(spec.check)


def test_real_key_incremental_scope_no_new_ref_passes(fake_gateway_factory):
    """NL-2 增量口径（2026-09-27 判据原文对齐修）：存量正文行不连坐——HEAD 已含同数字样、
    own-diff 未新增引用 → 放行（此前整文件扫描使 OBJ_S DESIGN 等文档合法编辑恒被拦）。"""
    marker = REAL_KEY_MARKER + "_PATH"
    gateway = fake_gateway_factory(
        staged={"docs/_working/obj_s/DESIGN.md": f"# 设计稿\n验收行：含 {marker} 字样的环境应被拒。\n新增无关行。\n"},
        head={"docs/_working/obj_s/DESIGN.md": f"# 设计稿\n验收行：含 {marker} 字样的环境应被拒。\n"},
    )
    passed, detail = make_real_key_reference_scan_gate().check(
        gateway, ["docs/_working/obj_s/DESIGN.md"], session_id="s1"
    )
    assert passed is True, detail


def test_real_key_incremental_scope_new_ref_still_blocked(fake_gateway_factory):
    """NL-2 增量口径红证：own-diff 新增一处实盘键名字样 → 照旧硬阻断+审计。"""
    marker = REAL_KEY_MARKER + "_PATH"
    gateway = fake_gateway_factory(
        staged={
            "docs/_working/obj_s/DESIGN.md": f"# 设计稿\n验收行：含 {marker} 字样的环境应被拒。\n误加 {marker} 引用。\n"
        },
        head={"docs/_working/obj_s/DESIGN.md": f"# 设计稿\n验收行：含 {marker} 字样的环境应被拒。\n"},
    )
    passed, detail = make_real_key_reference_scan_gate().check(
        gateway, ["docs/_working/obj_s/DESIGN.md"], session_id="s1"
    )
    assert passed is False and "docs/_working/obj_s/DESIGN.md" in detail


# ═══════════════ 裁定#503 准入面三锁红证（内收批：同门同件，一件一 module_id 家法）═══════════════
# 原独立文件 tests/ai/ai_layer/redline/test_real_key_admission_surface.py 的两枚袋（-0014/-0018）都死于
# MODULE-ID-CONSISTENCY（dev 现测 2479 个 A_test module_id 仅 6 个重复＝一件一 id），故按内收判据并为本件的新增段，
# 不另起 module_id、不留第二声明位。红证三向语义一字未改。
ADMITTED = sorted(_REAL_KEY_ADMISSION)[0]
KEY_LINE = "KEY = '" + REAL_KEY_MARKER + "_ACCOUNT'\n"


def _write_ruling(root: Path, ruling_id: str, *, owner_sign: str = "", status: str = "active") -> None:
    """在 tmp 项目根造一面裁定册（只放被引用的那一条）。"""
    p = root / RULING_REGISTRY_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    entry = {"ruling_id": ruling_id, "status": status, "summary": "准入面授权链"}
    if owner_sign:
        entry["owner_sign"] = owner_sign
    p.write_text(
        "entries:\n" + __import__("yaml").safe_dump([entry], allow_unicode=True, sort_keys=False), encoding="utf-8"
    )


def _audit_records(tmp_path: Path) -> list[dict]:
    f = tmp_path / ".runtime/gate_audit/real_key_reference_scan.jsonl"
    assert f.exists(), "审计文件未生成=审计面失效"
    return [json.loads(ln) for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip()]


# ────────────────────────── 向①：封闭枚举 ──────────────────────────


def test_lock1_admission_list_is_closed_enumeration():
    """锁①本体：清单必须是精确路径封闭枚举——禁通配/禁目录前缀/禁模式字符。"""
    assert len(_REAL_KEY_ADMISSION) == 5
    for path, rid in _REAL_KEY_ADMISSION.items():
        assert "*" not in path and "?" not in path and not path.endswith("/"), path
        assert path == path.replace("\\", "/"), path
        assert rid == "裁定#503", path


def test_unlisted_path_with_marker_still_blocked_even_with_valid_ruling(tmp_path, fake_gateway_factory):
    """向①：裁定有效，但路径不在封闭枚举内 → 照样硬阻断（准入面不是通用豁免）。"""
    _write_ruling(tmp_path, "裁定#503", owner_sign="Owner 2026-10-10 回「按甲改门」")
    gateway = fake_gateway_factory(staged={"src/zephyr/demo/loader.py": KEY_LINE})
    passed, detail = make_real_key_reference_scan_gate().check(
        gateway, ["src/zephyr/demo/loader.py"], session_id="s-red-1"
    )
    assert passed is False
    assert REAL_KEY_MARKER in detail
    assert _audit_records(tmp_path)[0]["action"] == "block"


def test_directory_prefix_is_not_admitted(tmp_path, fake_gateway_factory):
    """向①补刀：列名件的**同目录兄弟件**不得被顺带放行（防目录级蔓延）。"""
    _write_ruling(tmp_path, "裁定#503", owner_sign="Owner 2026-10-10 回「按甲改门」")
    sibling = str(Path(ADMITTED).parent / "test_not_in_list.py")
    assert sibling not in _REAL_KEY_ADMISSION
    gateway = fake_gateway_factory(staged={sibling: KEY_LINE})
    passed, _ = make_real_key_reference_scan_gate().check(gateway, [sibling], session_id="s-red-1b")
    assert passed is False


# ─────────────────── 向②：伪造引用 / 无 owner_sign ───────────────────


def test_forged_ruling_reference_blocked(tmp_path, fake_gateway_factory):
    """向②a：枚举里的裁定号在面上根本不存在（册缺失）⇒ 拦（fail-closed）。"""
    gateway = fake_gateway_factory(staged={ADMITTED: KEY_LINE})
    passed, _ = make_real_key_reference_scan_gate().check(gateway, [ADMITTED], session_id="s-red-2a")
    assert passed is False


def test_ruling_without_owner_sign_blocked(tmp_path, fake_gateway_factory):
    """向②b：在册但**无 owner_sign**（＝AI 代裁）⇒ 拦。此锁专防自登裁定绕红线。"""
    _write_ruling(tmp_path, "裁定#503", owner_sign="")
    gateway = fake_gateway_factory(staged={ADMITTED: KEY_LINE})
    passed, _ = make_real_key_reference_scan_gate().check(gateway, [ADMITTED], session_id="s-red-2b")
    assert passed is False


def test_superseded_ruling_blocked(tmp_path, fake_gateway_factory):
    """向②c：有 owner_sign 但 status≠active（已被取代/已废弃）⇒ 拦。"""
    _write_ruling(tmp_path, "裁定#503", owner_sign="Owner 2026-10-10 回「按甲改门」", status="superseded")
    gateway = fake_gateway_factory(staged={ADMITTED: KEY_LINE})
    passed, _ = make_real_key_reference_scan_gate().check(gateway, [ADMITTED], session_id="s-red-2c")
    assert passed is False


def test_unparseable_ruling_registry_blocks(tmp_path, fake_gateway_factory):
    """向②d：册在但读不出结构（他人热册半写/坏面）⇒ 拦，不静默放行。"""
    p = tmp_path / RULING_REGISTRY_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("entries: [ this is not : valid : yaml", encoding="utf-8")
    gateway = fake_gateway_factory(staged={ADMITTED: KEY_LINE})
    passed, _ = make_real_key_reference_scan_gate().check(gateway, [ADMITTED], session_id="s-red-2d")
    assert passed is False


# ─────────────────── 向③：放行 + 审计行 ───────────────────


@pytest.mark.parametrize("rel", sorted(_REAL_KEY_ADMISSION))
def test_listed_path_with_owner_sign_ruling_passes_and_audits(rel, tmp_path, fake_gateway_factory):
    """向③：5 条列名件逐条放行，且每次放行写审计行（裁定号+路径+时间+会话）。"""
    _write_ruling(tmp_path, "裁定#503", owner_sign="Owner 2026-10-10 回「按甲改门」")
    gateway = fake_gateway_factory(staged={rel: KEY_LINE})
    passed, detail = make_real_key_reference_scan_gate().check(gateway, [rel], session_id="s-red-3")
    assert passed is True, detail
    rec = _audit_records(tmp_path)[-1]
    assert rec["action"] == "admit"
    assert rec["ruling_id"] == ["裁定#503"]
    assert rec["paths"] == [rel]
    assert rec["timestamp"] and rec["session_id"] == "s-red-3"


def test_admission_does_not_touch_other_scan_logic(tmp_path, fake_gateway_factory):
    """边界令（执行令第 5 条）：准入面只决定"这一条路放行不"，其他扫描口径零变化——
    同袋里既有列名件放行、又有未列名件被拦时，仍整体阻断且只报未列名者。"""
    _write_ruling(tmp_path, "裁定#503", owner_sign="Owner 2026-10-10 回「按甲改门」")
    other = "docs/01_policies_and_standards/sop/leak.md"
    gateway = fake_gateway_factory(staged={ADMITTED: KEY_LINE, other: KEY_LINE})
    passed, detail = make_real_key_reference_scan_gate().check(gateway, [ADMITTED, other], session_id="s-red-5")
    assert passed is False
    assert other in detail and ADMITTED not in detail
