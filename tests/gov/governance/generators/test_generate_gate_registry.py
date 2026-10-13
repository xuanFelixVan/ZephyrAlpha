# [BLUEPRINT] MOD-GOV_GENERATE_ALGO_OVERVIEW | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] tests.governance.generators.test_generate_gate_registry
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.generators.generate_gate_registry
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 测试 generate_gate_registry.py 核心函数（extract_commit_gates/generate）覆盖 CommitGate 同步治本（2026-07-17）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-TEST_GATE_REGISTRY_GEN | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_generate_gate_registry.py — generate_gate_registry.py 单元测试（CommitGate 同步治本 2026-07-17）

覆盖：
- extract_commit_gates: 扫描 commit_gates/*.py 提取 GateSpec 元数据（gate_id/priority/description）
- generate: 三源合并（pre-commit hooks + CommitGates + MANUAL_GATES）+ source 字段
- three_account_diff: 三账对账（F98 G1 / M3 03，2026-09-27）——gate_registry.active ↔
  in_process.enabled ↔ pre-commit hooks；红/绿样例 + 字段自洽 + 字节兼容守卫

治本背景：原生成器只读 .pre-commit-config.yaml（33 个 pre-commit hooks），漏掉全部 ~50 个
CommitGates（in-process gate 注册在 GitCommitGateway）。本次扩展后 gate_registry.yaml 覆盖
全部门禁，消除手工 blueprint §0.1 表的漂移风险。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

# 添加项目根到 sys.path 以便 import 生成器模块
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.governance.generators.generate_gate_registry import (  # noqa: E402
    EXIT_PASS,
    extract_commit_gates,
    format_three_account_report,
    generate,
    three_account_diff,
)


def test_extract_commit_gates_returns_nonempty():
    """extract_commit_gates 应返回非空列表（实际 50 个 CommitGate）。"""
    gates = extract_commit_gates()
    assert len(gates) >= 40, f"CommitGate 数量异常少：{len(gates)}（预期 ~50）"


def test_extract_commit_gates_has_pure_assertion():
    """应含 PURE-ASSERTION（gate_id + priority=69）——治本触发用例。"""
    gates = extract_commit_gates()
    ids = [g["gate_id"] for g in gates]
    assert "PURE-ASSERTION" in ids, f"PURE-ASSERTION 缺失，实际 gate_ids: {ids[:10]}..."
    pa = next(g for g in gates if g["gate_id"] == "PURE-ASSERTION")
    assert "priority=69" in pa["name"], f"PURE-ASSERTION priority 异常：{pa['name']}"
    assert pa["source"] == "commit-gate"
    assert pa["category"] == "commit_gate"
    assert pa["entry"] == "in-process (GitCommitGateway)"


def test_extract_commit_gates_excludes_helpers():
    """应排除 __init__.py / _diff_helpers.py / gate_repo.py（无 GateSpec）。

    数量动态变化（其他会话可能新增 gate），用下限断言而非硬编码。
    """
    gates = extract_commit_gates()
    # 至少 50 个 GateSpec gate（治本时基准值，其他会话新增 gate 会更多）
    assert len(gates) >= 50, f"CommitGate 数量异常少：{len(gates)}（预期 >=50）"
    # 验证辅助文件确实被排除：_diff_helpers.py 无 GateSpec 会被自然跳过


def test_generate_merges_three_sources():
    """generate() 应合并三源：pre-commit + commit-gate + manual。"""
    output = generate()
    sources = {g.get("source") for g in output["gates"]}
    assert "pre-commit" in sources, "缺 pre-commit 源"
    assert "commit-gate" in sources, "缺 commit-gate 源"
    assert "manual" in sources, "缺 manual 源（MANUAL_GATES）"


def test_generate_no_duplicate_gate_id():
    """全量 gate_id 应无重复（pre-commit 与 CommitGate 命名空间不重叠）。"""
    output = generate()
    ids = [g["gate_id"] for g in output["gates"]]
    duplicates = {i for i in ids if ids.count(i) > 1}
    assert not duplicates, f"重复 gate_id: {duplicates}"


def test_generate_total_gates_increased():
    """total_gates 应 >=80（33 pre-commit + 50 commit-gate + 1 manual = 84）。"""
    output = generate()
    assert output["total_gates"] >= 80, f"total_gates 异常：{output['total_gates']}（预期 84）"
    assert output["total_gates"] == len(output["gates"]), "total_gates 与 gates 列表长度不一致"


def test_generate_source_field_in_output_dict():
    """输出 dict 的 source 字段应声明三源。"""
    output = generate()
    assert "commit_gates" in output["source"], f"输出 source 字段未声明 commit_gates：{output['source']}"
    assert "MANUAL_GATES" in output["source"], f"输出 source 字段未声明 MANUAL_GATES：{output['source']}"


def test_extract_commit_gates_all_have_required_fields():
    """每条 CommitGate 应含全部必需字段。"""
    gates = extract_commit_gates()
    required = {
        "gate_id",
        "name",
        "entry",
        "description",
        "files_trigger",
        "always_run",
        "category",
        "status",
        "source",
    }
    for g in gates:
        missing = required - set(g.keys())
        assert not missing, f"gate {g.get('gate_id')} 缺字段: {missing}"


def test_extract_commit_gates_recursive_scans_library_subdir():
    """递归扫描应覆盖 library/ 子目录三台（st-gslim-20260923 P1 漂移修复回归）。

    病根：glob 非递归漏扫 commit_gates/library/，BLOOD-FLESH/TAG-VOCAB/
    STATE-VOCAB-REGISTRY 三台未入统一册（in_process 117 vs 统一 114 漂移，
    gate_audit_report_v1 §A1 SSOT 事故隐患）。
    """
    gates = extract_commit_gates()
    ids = {g["gate_id"] for g in gates}
    for required in ("BLOOD-FLESH", "TAG-VOCAB", "STATE-VOCAB-REGISTRY"):
        assert required in ids, f"library/ 子目录门禁 {required} 未入统一册（递归扫描失效）"


def test_extract_commit_gates_no_duplicate_gate_id_across_subdirs():
    """迁移过渡态（旧路径未删+新路径已在）不得产生重复 gate_id 条目。"""
    gates = extract_commit_gates()
    ids = [g["gate_id"] for g in gates]
    duplicates = {i for i in ids if ids.count(i) > 1}
    assert not duplicates, f"commit-gate 条目重复 gate_id: {duplicates}"


# ---------------------------------------------------------------------------
# 三账对账（F98 G1 / M3 03 G1 治本，2026-09-27）：three_account_diff 配对测试
# 三账 = gate_registry.active ↔ in_process.enabled ↔ pre-commit hooks
# ---------------------------------------------------------------------------

_REGISTRY_YAML_TEMPLATE = """\
module_id: PS-REG-014
total_gates: {reg_total}
gates:
{reg_gates}
"""

_IN_PROCESS_YAML_TEMPLATE = """\
module_id: IN-PROC-TEST
total_gates: {ip_total}
gates:
{ip_gates}
"""

_PRECOMMIT_YAML_TEMPLATE = """\
repos:
  - repo: local
    hooks:
{hooks}
"""


def _write_three_accounts(
    tmp_path,
    reg_gates: list[str],
    ip_entries: list[tuple[str, bool]],
    hook_ids: list[str] | None = None,
    reg_total=None,
    ip_total=None,
):
    """在 tmp_path 写三账合成文件，返回三路径（全程不触生产目录）。

    hook_ids 缺省取 reg_gates 全集（三账对齐绿样基线）；差集场景显式传子集。
    """
    reg_body = "\n".join(f"  - gate_id: {gid}\n    status: active" for gid in reg_gates)
    reg_total = len(reg_gates) if reg_total is None else reg_total
    reg_text = _REGISTRY_YAML_TEMPLATE.format(reg_total=reg_total, reg_gates=reg_body)

    ip_body = "\n".join(f"  - gate_id: {gid}\n    enabled: {str(en).lower()}" for gid, en in ip_entries)
    ip_total = len(ip_entries) if ip_total is None else ip_total
    ip_text = _IN_PROCESS_YAML_TEMPLATE.format(ip_total=ip_total, ip_gates=ip_body)

    hook_ids = reg_gates if hook_ids is None else hook_ids
    hook_body = "\n".join(
        f'      - id: gate-{hid.lower()}\n        name: "{hid}: test hook"\n'
        f'        entry: "python -m test_gate"\n        language: system'
        for hid in hook_ids
    )

    reg_p = tmp_path / "gate_registry.yaml"
    ip_p = tmp_path / "in_process_gate_registry.yaml"
    pc_p = tmp_path / ".pre-commit-config.yaml"
    reg_p.write_text(reg_text, encoding="utf-8")
    ip_p.write_text(ip_text, encoding="utf-8")
    pc_p.write_text(_PRECOMMIT_YAML_TEMPLATE.format(hooks=hook_body), encoding="utf-8")
    return reg_p, ip_p, pc_p


class TestThreeAccountDiff:
    """three_account_diff 红/绿样例（F98 G1 对账闭环配对测试）。"""

    def test_green_sample_full_agreement(self, tmp_path):
        """绿样：三账完全一致 -> red=False，所有两账差集为空，三账交集=全集。"""
        reg_p, ip_p, pc_p = _write_three_accounts(
            tmp_path,
            reg_gates=["GATE-99", "GATE-ZR"],
            ip_entries=[("GATE-99", True), ("GATE-ZR", True)],
        )
        diff = three_account_diff(registry_path=reg_p, in_process_path=ip_p, precommit_path=pc_p)
        assert diff["red"] is False
        for key, items in diff["diffs"].items():
            if key == "triple_agreement":
                assert items == ["GATE-99", "GATE-ZR"]
            else:
                assert items == [], f"{key} 应为空，实际 {items}"
        assert all(c["ok"] for c in diff["field_self_check"].values())
        assert diff["counts"] == {"registry_active": 2, "in_process_enabled": 2, "precommit_hooks": 2}

    def test_red_sample_drift_and_field_mismatch(self, tmp_path):
        """红样：三向漂移 + in_process total_gates 字段错 -> red=True 且逐向定位。"""
        reg_p, ip_p, pc_p = _write_three_accounts(
            tmp_path,
            reg_gates=["GATE-99", "GATE-ZR", "GATE-GHOST"],  # GATE-GHOST 仅账1 有
            ip_entries=[("GATE-99", True), ("GATE-IP-ONLY", True)],  # 账2 独有 GATE-IP-ONLY
            hook_ids=["GATE-99"],  # 账3 缺 GATE-ZR/GATE-GHOST
            ip_total=3,  # 字段写 3，实数 2 -> MISMATCH
        )
        diff = three_account_diff(registry_path=reg_p, in_process_path=ip_p, precommit_path=pc_p)
        assert diff["red"] is True
        assert "GATE-GHOST" in diff["diffs"]["registry_active_minus_inprocess_enabled"]
        assert "GATE-GHOST" in diff["diffs"]["registry_active_minus_precommit_hooks"]
        assert "GATE-IP-ONLY" in diff["diffs"]["inprocess_enabled_minus_registry_active"]
        assert "GATE-ZR" in diff["diffs"]["registry_active_minus_precommit_hooks"]
        assert diff["diffs"]["precommit_hooks_minus_registry_active"] == []  # 钩子面是账1 子集
        assert "GATE-IP-ONLY" in diff["diffs"]["inprocess_enabled_minus_precommit_hooks"]
        ip_check = diff["field_self_check"]["in_process_registry"]
        assert ip_check["ok"] is False
        assert ip_check["total_gates_field"] == 3 and ip_check["actual"] == 2

    def test_virtual_claim_class(self, tmp_path):
        """虚报分类镜头：账1 active 但账2 enabled=false（F98 缺口 G2 对位）。"""
        reg_p, ip_p, pc_p = _write_three_accounts(
            tmp_path,
            reg_gates=["GATE-99", "GATE-DISABLED"],
            ip_entries=[("GATE-99", True), ("GATE-DISABLED", False)],
        )
        diff = three_account_diff(registry_path=reg_p, in_process_path=ip_p, precommit_path=pc_p)
        assert diff["diffs"]["virtual_claim_active_but_disabled"] == ["GATE-DISABLED"]
        assert diff["red"] is True  # 账1−账2 差集含 GATE-DISABLED

    def test_dangling_no_mount_class(self, tmp_path):
        """悬空分类镜头：账1 有名但账2 全无、账3 无钩子（F98 缺口 G3 对位）。"""
        reg_p, ip_p, pc_p = _write_three_accounts(
            tmp_path,
            reg_gates=["GATE-99", "GATE-ORPHAN"],
            ip_entries=[("GATE-99", True)],
            hook_ids=["GATE-99"],  # GATE-ORPHAN 无钩子
        )
        diff = three_account_diff(registry_path=reg_p, in_process_path=ip_p, precommit_path=pc_p)
        assert diff["diffs"]["dangling_no_mount"] == ["GATE-ORPHAN"]

    def test_real_catalogs_structure_and_self_check(self):
        """真源册对账冒烟：结构完整、三账计数为正、两册 total_gates 字段自洽（当前在产态）。"""
        diff = three_account_diff()
        assert set(diff.keys()) == {"counts", "diffs", "field_self_check", "red"}
        assert diff["counts"]["registry_active"] > 0
        assert diff["counts"]["in_process_enabled"] > 0
        assert diff["counts"]["precommit_hooks"] > 0
        assert all(c["ok"] for c in diff["field_self_check"].values()), (
            f"真源册 total_gates 字段漂移: {diff['field_self_check']}"
        )

    def test_report_is_deterministic_and_contains_verdict(self, tmp_path):
        """报告渲染确定性（排序输出）且含红/绿判定行。"""
        reg_p, ip_p, pc_p = _write_three_accounts(tmp_path, reg_gates=["GATE-99"], ip_entries=[("GATE-99", True)])
        d1 = three_account_diff(registry_path=reg_p, in_process_path=ip_p, precommit_path=pc_p)
        d2 = three_account_diff(registry_path=reg_p, in_process_path=ip_p, precommit_path=pc_p)
        r1, r2 = format_three_account_report(d1), format_three_account_report(d2)
        assert r1 == r2, "同输入两次渲染应逐字节一致"
        assert "GREEN" in r1
        assert "三账对账" in r1

    def test_generate_output_has_no_diff_section_byte_compat(self):
        """字节兼容守卫：generate() 编排段不得混入对账段——diff 只走 --diff 只读通道。"""
        output = generate()
        assert "three_account" not in output, "对账段泄漏进 generate() 输出（破坏既有输出编排）"
        assert set(output.keys()) == {
            "module_id",
            "doc_type",
            "ttl",
            "title",
            "status",
            "generated_at",
            "generated_by",
            "maintenance",
            "source",
            "total_gates",
            "gates",
        }


class TestThreeAccountDiffCli:
    """--diff CLI 语义：纯只读 + 红证退出码（EXIT_FINDINGS）。"""

    def test_cli_diff_green_exits_pass(self, tmp_path, monkeypatch, capsys):
        import scripts.governance.generators.generate_gate_registry as gen

        reg_p, ip_p, pc_p = _write_three_accounts(tmp_path, reg_gates=["GATE-99"], ip_entries=[("GATE-99", True)])
        monkeypatch.setattr(gen, "DEFAULT_OUTPUT", reg_p)
        monkeypatch.setattr(gen, "IN_PROCESS_REGISTRY_PATH", ip_p)
        monkeypatch.setattr(gen, "PRE_COMMIT_PATH", pc_p)
        monkeypatch.setattr(sys, "argv", ["generate_gate_registry.py", "--diff"])
        with pytest.raises(SystemExit) as ei:
            gen.main()
        assert ei.value.code == EXIT_PASS
        assert "GREEN" in capsys.readouterr().out

    def test_cli_diff_red_exits_findings(self, tmp_path, monkeypatch, capsys):
        import scripts.governance.generators.generate_gate_registry as gen
        from scripts.governance._shared.constants import EXIT_FINDINGS

        reg_p, ip_p, pc_p = _write_three_accounts(
            tmp_path,
            reg_gates=["GATE-99", "GATE-GHOST"],
            ip_entries=[("GATE-99", True)],
        )
        monkeypatch.setattr(gen, "DEFAULT_OUTPUT", reg_p)
        monkeypatch.setattr(gen, "IN_PROCESS_REGISTRY_PATH", ip_p)
        monkeypatch.setattr(gen, "PRE_COMMIT_PATH", pc_p)
        monkeypatch.setattr(sys, "argv", ["generate_gate_registry.py", "--diff"])
        with pytest.raises(SystemExit) as ei:
            gen.main()
        assert ei.value.code == EXIT_FINDINGS
        assert "RED" in capsys.readouterr().out

    def test_cli_diff_never_writes_registry(self, tmp_path, monkeypatch):
        """只读铁律：--diff 运行前后统一册 mtime+内容不变（对账不修册）。"""
        import scripts.governance.generators.generate_gate_registry as gen

        reg_p, ip_p, pc_p = _write_three_accounts(
            tmp_path,
            reg_gates=["GATE-99", "GATE-GHOST"],  # 有漂移仍不得写
            ip_entries=[("GATE-99", True)],
        )
        before = (reg_p.read_text(encoding="utf-8"), reg_p.stat().st_mtime)
        monkeypatch.setattr(gen, "DEFAULT_OUTPUT", reg_p)
        monkeypatch.setattr(gen, "IN_PROCESS_REGISTRY_PATH", ip_p)
        monkeypatch.setattr(gen, "PRE_COMMIT_PATH", pc_p)
        monkeypatch.setattr(sys, "argv", ["generate_gate_registry.py", "--diff"])
        with pytest.raises(SystemExit):
            gen.main()
        after = (reg_p.read_text(encoding="utf-8"), reg_p.stat().st_mtime)
        assert before == after, "--diff 修改了统一册（违反只读对账铁律）"

    def test_real_cli_diff_red_now(self, monkeypatch, capsys):
        """实弹配对（2026-09-27 基线）：真源三账当前为 RED——差集即审计待办。"""
        import scripts.governance.generators.generate_gate_registry as gen

        monkeypatch.setattr(sys, "argv", ["generate_gate_registry.py", "--diff"])
        with pytest.raises(SystemExit) as ei:
            gen.main()
        out = capsys.readouterr().out
        assert ei.value.code == 1  # EXIT_FINDINGS
        assert "RED" in out
        assert "虚报" in out and "悬空" in out


def test_manual_tombstones_override_disk_shadowed_entries():
    """墓碑覆盖回归（st-nightsweep-sw15-20260929，92 册 G-81 治本）。

    病根：extract_commit_gates 每文件只取首个 gate_id——吸收台薄工厂独立成文件时
    （如 ruling_reference_gate.py），MANUAL_GATES 墓碑被盘上扫描条目遮蔽，统一册
    恒为假 active，post-commit 重生成自我复活（实测 15 台"声明在册、无人装载"）。
    不变量：MANUAL_GATES 中未回装 in_process 名册的 gate_id，在 generate() 输出中
    必须呈现 MANUAL_GATES 自带 status（deprecated 墓碑胜出）；已回装者不受墓碑影响。
    修前此测试红（RULING-REFERENCE 等 15 台 active），修后绿。
    """
    from scripts.governance.generators.generate_gate_registry import (  # noqa: PLC0415
        IN_PROCESS_REGISTRY_PATH,
        MANUAL_GATES,
        generate,
        load_yaml,
    )

    roster_ids = {g.get("gate_id") for g in (load_yaml(IN_PROCESS_REGISTRY_PATH).get("gates") or [])}
    output = generate()
    by_id = {}
    for g in output["gates"]:
        by_id.setdefault(g["gate_id"], []).append(g)

    for mg in MANUAL_GATES:
        gid = mg["gate_id"]
        entries = by_id.get(gid)
        assert entries, f"MANUAL_GATES 条目 {gid} 在 generate() 输出中缺失"
        assert len(entries) == 1, f"{gid} 出现重复条目: {len(entries)}"
        if gid in roster_ids:
            continue  # 已回装名册：装载事实优先，墓碑让位
        assert entries[0]["status"] == mg["status"], (
            f"{gid} 统一册 status={entries[0]['status']} ≠ 墓碑 status={mg['status']}"
            "（盘上扫描条目遮蔽墓碑=假 active 复活）"
        )
        if mg.get("redirect_to"):
            assert entries[0].get("redirect_to") == mg["redirect_to"], (
                f"{gid} redirect_to 漂移: {entries[0].get('redirect_to')}"
            )


# ─── K8 姊妹台补登（一文件多工厂，st-libstale-20261013）═══════════════════════
# 病根实证：POOL-REGRESSION-DIRECTION 在 in_process 名册 enabled:true 且
# auto_register_gates 真装载（priority=161），但旧尺 `_RE_GATE_ID.search()` 每台只取
# 首个 gate_id ⇒ 统一册每次重生把它蒸发 ⇒ 手工条目撑着机生册；GATE-21 又要求
# commit_gates/*.py 变更时总册同步 ⇒ 谁装新门谁撞"不重生被拦／重生即净删他人行"死锁。

_TEXT_TWO_FACTORIES = '''
_GATE_ID = "DEMO-PRIMARY"
_SECOND_GATE_ID = "DEMO-SIBLING"


def make_demo_primary_gate() -> GateSpec:
    """构造 DEMO-PRIMARY 门禁（priority=901）。"""
    return GateSpec(
        gate_id=_GATE_ID,
        check=_check,
        priority=901,
    )


def make_demo_sibling_gate() -> GateSpec:
    """构造 DEMO-SIBLING 门禁（own-scope 观察型，priority=902）。"""
    return GateSpec(gate_id=_SECOND_GATE_ID, check=_check2, priority=902)
'''


def test_gatespec_calls_collects_literal_and_variable_ids() -> None:
    """两种在册写法都要收齐：字面 gate_id="X" 与常量绑定 gate_id=_X（POOL 即后者）。"""
    from scripts.governance.generators.generate_gate_registry import _gatespec_calls

    got = _gatespec_calls(_TEXT_TWO_FACTORIES)
    assert [g[0] for g in got] == ["DEMO-PRIMARY", "DEMO-SIBLING"], got
    assert [g[1] for g in got] == [901, 902], got
    assert got[1][2] == "构造 DEMO-SIBLING 门禁（own-scope 观察型，priority=902）", got[1][2]


def test_gatespec_calls_skips_unresolvable_binding() -> None:
    """gate_id 绑到解析不出的名字时跳过而非崩（也不得凭空造一台门）。"""
    from scripts.governance.generators.generate_gate_registry import _gatespec_calls

    text = 'def make_x() -> GateSpec:\n    """构造 X。"""\n    return GateSpec(gate_id=UNKNOWN_CONST, check=c, priority=7)\n'
    assert _gatespec_calls(text) == []


def test_pool_regression_direction_is_now_derivable() -> None:
    """真树回归：POOL 台次必须从代码导出，不再靠统一册手抄条目。"""
    gates = {g["gate_id"]: g for g in extract_commit_gates()}
    assert "POOL-REGRESSION-DIRECTION" in gates, "POOL 台次再次蒸发——姊妹台补登被回退"
    row = gates["POOL-REGRESSION-DIRECTION"]
    assert "priority=161" in row["name"], row["name"]
    assert row["entry"] == "in-process (GitCommitGateway)"


def test_ghost_row_tombstone_emitted_as_deprecated() -> None:
    """无源行（策略卡生命周期图）以墓碑形式在册且 status=deprecated，不再伪装 active。"""
    rows = [g for g in generate()["gates"] if g.get("gate_id") == "STRATEGY-CARD-LIFECYCLE-MAP"]
    assert len(rows) == 1, f"墓碑行数异常: {len(rows)}"
    assert rows[0]["status"] == "deprecated", rows[0]
    assert str(rows[0]["entry"]).startswith("N/A"), rows[0]["entry"]


def test_sibling_pass_never_reattributes_existing_rows(monkeypatch) -> None:
    """只增不改契约：姊妹台一遍不得改动第一遍任何行的字节（含同名跨模块 id）。"""
    from scripts.governance.generators import generate_gate_registry as gen

    with_sibling = extract_commit_gates()
    monkeypatch.setattr(gen, "_gatespec_calls", lambda text: [])
    only_primary = extract_commit_gates()

    primary_ids = {g["gate_id"] for g in only_primary}
    sib_ids = {g["gate_id"] for g in with_sibling}
    assert primary_ids <= sib_ids, f"补登反而丢行: {sorted(primary_ids - sib_ids)}"
    by_sib = {g["gate_id"]: g for g in with_sibling}
    drift = [g["gate_id"] for g in only_primary if by_sib[g["gate_id"]] != g]
    assert drift == [], f"既有行被姊妹台改写归属/措辞: {drift}"
    # MAP-ALIGNMENT 同名跨三模块＝归属最易被抢的一台，单点名复核
    assert by_sib["MAP-ALIGNMENT"] == next(g for g in only_primary if g["gate_id"] == "MAP-ALIGNMENT")


def test_generation_idempotent() -> None:
    """幂等：连跑两次 generate() 必须逐字节相同（否则 total_gates 会自己漂）。"""
    first, second = generate(), generate()
    assert first["total_gates"] == second["total_gates"]
    assert [g["gate_id"] for g in first["gates"]] == [g["gate_id"] for g in second["gates"]]
    assert first["gates"] == second["gates"]
