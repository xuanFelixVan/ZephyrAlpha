# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | #reserved-void-gate
# [MODULE] tests.governance.test_casebook_reserved_void_gate
# [DOMAIN] D_GOV
# [DEPENDENCIES] stdlib(pytest/pathlib)；yaml
# [CONSUMERS] 案册 reserved_void 防重门（裁定#492 合同测试件，st-t3a-casebook 落地）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 三态：real 册无 reserved_void 注记段=skip（void 未落，断言不激活）；有注记段=激活
#   三断言（①casebook_id 全册唯一 ②voided 号段不可被活跃条目占用——伪造占 006 必显红
#   ③注记段机读契约可解析且覆盖 006/007/008）；红蓝注入攻击 fixture 全走 tmp_path，
#   禁写生产路径；本测试不修改任何生产文件（只读+内存 fixture）。
# [MODIFY-GUARD] 只读真源册；契约演进须随裁定批（同 casebook_registry 维护纪律）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=合同破坏显红；yaml 解析失败=显红（禁静默放行）
# [TTL] permanent
# [TESTS] tests/governance/test_casebook_reserved_void_gate.py
"""CASEBOOK reserved_void 防重门（Owner 裁定④：「006/007/008 因处方遗失作废，永不回填，
新册从下一新号顺延」——casebook_registry 头注所引 裁定#492 的机器可执行合同）。

设计：条件激活。void 注记段未落的过渡期本测试对 real 册 skip（不阻塞与其无关的提交）；
注记段落地即自动开始 enforcement——此后任何试图占用 006/007/008 的册条目都会在这里显红。
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REGISTRY = Path("docs/01_policies_and_standards/_registry/catalogs/casebook_registry.yaml")
VOIDED_EXPECTED = {"CASEBOOK-006", "CASEBOOK-007", "CASEBOOK-008"}


def _load(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"registry not a mapping: {path}"
    return data


def _extract_voided(section) -> set:
    """机读契约：reserved_void 段可解析为 voided 号集合（接受 id 列表或 dict 条目列表）。"""
    ids: set = set()
    if isinstance(section, dict):
        section = section.get("casebook_ids", section.get("voided", section.get("ids", [section])))
    if not isinstance(section, list):
        raise ValueError("reserved_void 段不可机读（既非列表也非可解析映射）")
    for item in section:
        if isinstance(item, str):
            ids.add(item)
        elif isinstance(item, dict):
            key = item.get("casebook_id") or item.get("id") or item.get("number")
            if not key:
                raise ValueError(f"reserved_void 条目缺号段字段: {item!r}")
            ids.add(str(key))
        else:
            raise ValueError(f"reserved_void 条目类型非法: {item!r}")
    return ids


def validate(doc: dict) -> tuple[bool, list[str]]:
    """对整册跑 void 合同：返回 (是否通过, 违规清单)。"""
    violations: list[str] = []
    if "reserved_void" not in doc:
        return True, []  # 未激活态由调用方 skip，不在此判红
    try:
        voided = _extract_voided(doc["reserved_void"])
    except ValueError as exc:
        return False, [f"机读契约破坏: {exc}"]
    missing = VOIDED_EXPECTED - voided
    if missing:
        violations.append(f"reserved_void 覆盖不全（缺 {sorted(missing)}）")
    seen: dict[str, int] = {}
    for entry in doc.get("casebooks") or []:
        cid = str(entry.get("casebook_id", "")) if isinstance(entry, dict) else ""
        seen[cid] = seen.get(cid, 0) + 1
        if cid in voided:
            violations.append(f"reserved_void 号被占用显红: {cid}（永不回填）")
    dupes = sorted(c for c, n in seen.items() if n > 1)
    if dupes:
        violations.append(f"casebook_id 同键重复: {dupes}")
    return (not violations), violations


# ---------- real 册面（条件激活） ----------


def test_real_registry_void_contract():
    data = _load(REGISTRY)
    if "reserved_void" not in data:
        pytest.skip("reserved_void 注记段未落地（裁定#492 主面由在册批承载）——断言不激活")
    ok, violations = validate(data)
    assert ok, f"casebook reserved_void 合同违规: {violations}"


# ---------- 红蓝注入攻击（tmp_path fixture，禁写生产路径） ----------


def _base_doc() -> dict:
    return {
        "casebooks": [
            {"casebook_id": "CASEBOOK-001", "name_zh": "甲", "status": "active"},
            {"casebook_id": "CASEBOOK-009", "name_zh": "顺延新册", "status": "active"},
        ],
        "reserved_void": [
            {"casebook_id": "CASEBOOK-006", "reason": "处方遗失作废"},
            {"casebook_id": "CASEBOOK-007", "reason": "处方遗失作废"},
            {"casebook_id": "CASEBOOK-008", "reason": "处方遗失作废"},
        ],
    }


def test_attack_forged_006_occupation_must_red(tmp_path: Path):
    """攻1：void 段在+伪造占用 006 的册条目 → 必须显红。"""
    doc = _base_doc()
    doc["casebooks"].append({"casebook_id": "CASEBOOK-006", "name_zh": "伪造册", "status": "active"})
    p = tmp_path / "casebook_registry.yaml"
    p.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    ok, violations = validate(_load(p))
    assert not ok, "伪造占用 reserved_void 号未被拦截——防重门失效"
    assert any("CASEBOOK-006" in v for v in violations)


def test_attack_legal_009_sequential_must_green(tmp_path: Path):
    """攻2（反向对照）：void 段在+合法 009 顺延新册 → 绿。"""
    doc = _base_doc()
    p = tmp_path / "casebook_registry.yaml"
    p.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    ok, violations = validate(_load(p))
    assert ok, f"合法顺延册被误拦: {violations}"


def test_attack_duplicate_casebook_id_must_red(tmp_path: Path):
    """攻3：同键 casebook_id 重复注入 → 必须显红。"""
    doc = _base_doc()
    doc["casebooks"].append({"casebook_id": "CASEBOOK-001", "name_zh": "重复注入", "status": "active"})
    p = tmp_path / "casebook_registry.yaml"
    p.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    ok, violations = validate(_load(p))
    assert not ok, "同键重复未被拦截——防重门失效"
    assert any("同键重复" in v for v in violations)


def test_attack_unreadable_void_section_must_red(tmp_path: Path):
    """攻4：注记段被改成不可机读形态（散文）→ 必须显红（禁静默放行）。"""
    doc = _base_doc()
    doc["reserved_void"] = "006-008 作废（自由散文，机器读不了）"
    p = tmp_path / "casebook_registry.yaml"
    p.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    ok, violations = validate(_load(p))
    assert not ok, "不可机读注记段未被拦截"
    assert any("机读契约" in v for v in violations)
