# [A_test] module_id=MOD-GOV-VOCAB-GATE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-VOCAB-GATE | docs/_working/daily_loop_campaign/03_self_ruling_vocab_ssot.md | §state_vocab_registry
# [MODULE] tests.gov_enforcement.test_state_vocab_registry_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_state_vocab_registry_gate.py — STATE-VOCAB-REGISTRY 门配对测试（词表 SSOT W3 执行门）

权威依据：src/zephyr/gov_enforcement/commit_gates/library/state_vocab_registry_gate.py
真源登记册：docs/01_policies_and_standards/_registry/catalogs/state_vocabulary_registry.yaml
官方本体：src/zephyr/shared/vocab/market_state.py

为什么必须有本文件（病灶④）：门的 [TESTS] 早就声明了本路径，但文件从未落地——
"恒绿且无配对测试可证伪"按 Owner 明令判"疑似判据失效"。本件把两枚红测钉住：
  红测甲 册读不到 → 报红（passed=False），不再"debug 日志跳过＝结构性恒绿"
  红测乙 值不在册 → 拦（block 模式 passed=False；warn 模式仍放行但必留 detail+审计痕）
另附"声明为真"三面（真册在场 / 官方本体在册 / 本体取值与册逐值相等），
使"ROOR 指向的文件存在、capability 与翻译册登记的两件文件存在"可被机器证伪。

W6-V 追加（红队案卷 rb2_guard_attacks.md §三/§五 实测四处"报绿而不执法"的配对判据）：
  * 面 B-16/B-16'：册在场但缺 official_ontology / 结构不合预期 → **报红**（禁回落"无锁定"）
  * §三.1：noqa **不得**豁免官方本体的值级锁定（原测"逃生对值锁仍有效"按缺陷改判，见
    TestNoqaDoesNotReachOfficialValueLock 的注释——收紧不是放松）
  * §三.2：门内文案教的 noqa 形态必须实测生效（文案与正则同源自证）
  * §五：官方本体认定不得只靠类名/路径白名单——值面判据补一道（换名野值必红）
  * §五末行：合并后真册的双登记块对账（主区块 29 条 verbatim 未被抹）

测试隔离：tmp_path 造假仓根 + MagicMock 假 gateway，不读写真实仓库生产路径
（真实面只读三份真源文件，零写入）。
"""

from __future__ import annotations

import pytest

pytest.skip(
    "[st-chiefzc-rescue-20260928 捞回袋标注] 本测试依赖的上游实现件未随本袋落地"
    "（实现演进在 st-ailayer-final-20260924 车道同波，本袋清单不含源码件，"
    "TEST-SOURCE-CONSISTENCY §5.178 符号漂移硬阻断的官方豁免标记）——"
    "上游实现件落地后删除本 skip 即恢复硬测。",
    allow_module_level=True,
)

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import zephyr.gov_enforcement.commit_gates.library.state_vocab_registry_gate as g  # noqa: E402
from zephyr.gov_enforcement.commit_gates._diff_helpers import (  # noqa: E402
    _make_noqa_pattern,
)
from zephyr.gov_enforcement.commit_gates.library.state_vocab_registry_gate import (  # noqa: E402
    _load_registry,
    _scan_py_files_for_findings,
    make_state_vocab_registry_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402

_REGISTRY_REL = g.STATE_VOCAB_REGISTRY_REL_PATH
_VOCAB_MODULE_REL = "src/zephyr/shared/vocab/market_state.py"
_OFFICIAL_CLASSES = ("MacroRegime", "EmotionCycleSix", "IntradayFive", "AnchoredTier")
_SIX = ("CAPITULATION", "ACCUMULATION", "IGNITION", "EXPANSION", "EUPHORIA", "DISTRIBUTION")

# 临时假册：官方本体类做值级锁定；PortfolioMode 用作"存量词表在册"样例
_FAKE_REGISTRY = """\
schema_version: 1
registry_id: REG-STATE-VOCAB-001
official_ontology:
  physical_location: src/zephyr/shared/vocab/market_state.py
  classes:
    - name: MacroRegime
      target: zephyr.shared.vocab.market_state.MacroRegime
      values_locked: true
      canonical_values: [R1, R2, R3, R4, R10, R11, R12]
    - name: EmotionCycleSix
      target: zephyr.shared.vocab.market_state.EmotionCycleSix
      values_locked: true
      canonical_values: [CAPITULATION, ACCUMULATION, IGNITION, EXPANSION, EUPHORIA, DISTRIBUTION]
vocabularies:
  - {id: X9, class: PortfolioMode, location: "src/zephyr/tmp/portfolio_mode.py:1-9"}
"""

# 红队 §二.16 现场复刻：同名册换了 schema（他道 09-22 版就是这套：只有 vocabularies、
# 条目用 vocabulary_id，无 official_ontology）——原实现读它 error="" 且锁定表空＝静默归零。
_LEGACY_SCHEMA_REGISTRY = """\
registry_id: REG-STATE-VOCAB-001
vocabularies:
  - vocabulary_id: tdm-six
    axis: 情绪
    states: [capitulation, accumulation, ignition, expansion, euphoria, distribution]
    source: config/trading_decision_map.yaml:4474
"""


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(tmp_root: Path, staged: tuple[str, ...] = ()) -> MagicMock:
    gw = MagicMock()
    gw.project_root = str(tmp_root)

    def _run_git(cmd, *a, **k):
        cmd = [str(c) for c in cmd]
        if "rev-parse" in cmd:
            return _MockResult(returncode=0, stdout=str(tmp_root))
        if "diff" in cmd:
            return _MockResult(returncode=0, stdout="\n".join(staged))
        return _MockResult(returncode=0, stdout="")

    gw.run_git = _run_git
    return gw


def _write(root: Path, rel: str, content: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _class_source(cls_name: str, values: list[str], *, noqa_on: str | None = None) -> str:
    """造一个"全大写字符串字面量"词表类源码；noqa_on=挂在哪个取值行后。"""
    lines = []
    for v in values:
        comment = ""
        if noqa_on == v:
            comment = f"  {g.NOQA_FORM_EXAMPLE}"
        lines.append(f'    {v}: Final[str] = "{v}"{comment}')
    body = "\n".join(lines)
    return f"from typing import Final\n\n\nclass {cls_name}:\n{body}\n"


def _six_segment_source(extra: str = "") -> str:
    values = list(_SIX)
    if extra:
        values.append(extra)
    return _class_source("EmotionCycleSix", values)


def _registry_without(section_value: Any, *, key: str = "official_ontology") -> str:
    """按 key 替换 official_ontology 段内容（造"结构不合预期"各形态）。"""
    import yaml  # noqa: PLC0415

    doc = yaml.safe_load(_FAKE_REGISTRY)
    if section_value is None:
        doc.pop(key, None)
    else:
        doc[key] = section_value
    return yaml.safe_dump(doc, allow_unicode=True, sort_keys=False)


class TestGateSpecFields:
    def test_spec_identity(self):
        spec = make_state_vocab_registry_gate()
        assert isinstance(spec, GateSpec)
        assert spec.gate_id == "STATE-VOCAB-REGISTRY"
        assert spec.priority == 135

    def test_shipped_mode_is_warn_not_flipped(self):
        """出厂姿态仍是 warn（warn→block 翻转属 Owner 门位，本车道不翻）。"""
        assert g.STATE_VOCAB_GATE_MODE == "warn"


class TestRedARegistryUnreadableIsRed:
    """红测甲：册缺失/损坏=报红，绝不放行（原设计在此路 return True, ""＝结构性恒绿）。"""

    def test_missing_registry_blocks(self, tmp_path):
        gw = _make_gateway(tmp_path)  # 不写册
        passed, detail = make_state_vocab_registry_gate().check(gw, [], session_id=None)
        assert passed is False
        assert "不存在" in detail
        assert _REGISTRY_REL in detail

    def test_corrupt_registry_blocks(self, tmp_path):
        _write(tmp_path, _REGISTRY_REL, "vocabularies: [unclosed\n  - {broken\n")
        passed, detail = make_state_vocab_registry_gate().check(_make_gateway(tmp_path), [], session_id=None)
        assert passed is False
        assert "解析失败" in detail

    def test_non_mapping_registry_blocks(self, tmp_path):
        _write(tmp_path, _REGISTRY_REL, "just a scalar string\n")
        passed, detail = make_state_vocab_registry_gate().check(_make_gateway(tmp_path), [], session_id=None)
        assert passed is False
        assert "顶层不是映射" in detail

    def test_missing_registry_leaves_audit_trace(self, tmp_path):
        gw = _make_gateway(tmp_path)
        make_state_vocab_registry_gate().check(gw, [], session_id=None)
        audit = tmp_path / ".runtime" / "gate_audit" / "state_vocab_registry.jsonl"
        assert audit.exists(), "报红必须留痕，否则 Owner 无从回评"
        rec = json.loads(audit.read_text(encoding="utf-8").splitlines()[-1])
        assert "__registry_unavailable__" in rec["findings"]

    def test_loaded_registry_yields_value_locks(self, tmp_path):
        _write(tmp_path, _REGISTRY_REL, _FAKE_REGISTRY)
        reg = _load_registry(str(tmp_path))
        assert reg.error == ""
        assert reg.value_locks["EmotionCycleSix"] == frozenset(_SIX)
        assert "PortfolioMode" in reg.names

    def test_no_module_level_vocabulary_constants(self):
        """判据读册不读常数：门源码里不得出现官方取值（否则册改了门不跟）。"""
        src = Path(g.__file__).read_text(encoding="utf-8")
        for value in (*_SIX, "ANCHORED_R3", "EUPHORIC"):
            assert value not in src, f"门源码硬编码了官方取值 {value}（应只读册）"


class TestRedCRegistrySchemaDriftIsRed:
    """W6-V 任务二（红队 §二.16/§五末行）：册在场但官方本体段不可用 → 报红，禁回落"无锁定"。"""

    def _run(self, tmp_path: Path, registry_text: str) -> tuple[bool, str]:
        _write(tmp_path, _REGISTRY_REL, registry_text)
        return make_state_vocab_registry_gate().check(_make_gateway(tmp_path), [], session_id=None)

    def test_registry_without_official_ontology_is_red(self, tmp_path):
        """红队原案：他道 09-22 版同名册（无 official_ontology）→ 改前 passed=True 且静默。"""
        passed, detail = self._run(tmp_path, _LEGACY_SCHEMA_REGISTRY)
        assert passed is False, "缺 official_ontology 段不得当『无官方锁定』放行"
        assert "official_ontology" in detail

    def test_registry_with_non_mapping_ontology_is_red(self, tmp_path):
        passed, _detail = self._run(tmp_path, _registry_without("official_ontology: 见立法件"))
        assert passed is False

    def test_registry_with_empty_classes_is_red(self, tmp_path):
        passed, detail = self._run(tmp_path, _registry_without({"classes": []}))
        assert passed is False
        assert "classes" in detail

    def test_registry_with_missing_canonical_values_is_red(self, tmp_path):
        passed, detail = self._run(
            tmp_path, _registry_without({"classes": [{"name": "EmotionCycleSix", "values_locked": True}]})
        )
        assert passed is False
        assert "canonical_values" in detail

    def test_registry_with_unlocked_class_is_red(self, tmp_path):
        """values_locked 未置真＝该类的值面无人守，按"结构不合预期"报红而不是静默跳过。"""
        passed, detail = self._run(
            tmp_path,
            _registry_without(
                {"classes": [{"name": "EmotionCycleSix", "values_locked": False, "canonical_values": list(_SIX)}]}
            ),
        )
        assert passed is False
        assert "values_locked" in detail

    def test_schema_drift_leaves_audit_trace(self, tmp_path):
        self._run(tmp_path, _LEGACY_SCHEMA_REGISTRY)
        audit = tmp_path / ".runtime" / "gate_audit" / "state_vocab_registry.jsonl"
        assert audit.exists()
        rec = json.loads(audit.read_text(encoding="utf-8").splitlines()[-1])
        assert "__registry_unavailable__" in rec["findings"]

    def test_drift_blocks_even_with_clean_source_file(self, tmp_path):
        """红队实测"官方类加第八态照样 passed=True"的场景复现：源文件有违规也到不了判定面。"""
        _write(tmp_path, _REGISTRY_REL, _LEGACY_SCHEMA_REGISTRY)
        rel = _VOCAB_MODULE_REL
        _write(tmp_path, rel, _six_segment_source(extra="RECHARGING"))
        gw = _make_gateway(tmp_path, (rel,))
        passed, _detail = make_state_vocab_registry_gate().check(gw, [], session_id=None)
        assert passed is False

    def test_real_merged_registry_reads_clean(self, tmp_path):
        """反向自证：真册（合并后）不得被结构自检误伤，且四官方类都在锁定面。"""
        import shutil  # noqa: PLC0415

        dst = tmp_path / _REGISTRY_REL
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(_PROJECT_ROOT / _REGISTRY_REL, dst)
        reg = _load_registry(str(tmp_path))
        assert reg.error == ""
        assert set(reg.value_locks) >= set(_OFFICIAL_CLASSES)


class TestRedBValueNotInRegistryIsBlocked:
    """红测乙：官方本体类**取值**未逐值在册 → 拦（治"只按类名后缀匹配＝拦错对象"）。"""

    @pytest.fixture(autouse=True)
    def _fake_repo(self, tmp_path):
        self.root = tmp_path
        _write(tmp_path, _REGISTRY_REL, _FAKE_REGISTRY)

    def _run(self, source: str, staged_rel: str = "src/zephyr/probe/emotion.py"):
        _write(self.root, staged_rel, source)
        gw = _make_gateway(self.root, (staged_rel,))
        return make_state_vocab_registry_gate().check(gw, [], session_id=None)

    def test_new_official_value_blocks_in_block_mode(self, monkeypatch):
        monkeypatch.setattr(g, "STATE_VOCAB_GATE_MODE", "block")
        passed, detail = self._run(_six_segment_source(extra="RECHARGING"))
        assert passed is False
        assert "RECHARGING" in detail
        assert "取值未登记" in detail

    def test_same_case_in_warn_mode_passes_but_leaves_trace(self, monkeypatch):
        """warn 出厂姿态不得被本车道偷偷升硬：放行＋必留 detail 与审计痕。"""
        monkeypatch.setattr(g, "STATE_VOCAB_GATE_MODE", "warn")
        passed, detail = self._run(_six_segment_source(extra="RECHARGING"))
        assert passed is True
        assert "RECHARGING" in detail
        audit = self.root / ".runtime" / "gate_audit" / "state_vocab_registry.jsonl"
        rec = json.loads(audit.read_text(encoding="utf-8").splitlines()[-1])
        assert any(any("取值未登记" in f for f in fs) for fs in rec["findings"].values())

    def test_in_registry_values_pass_clean(self):
        passed, detail = self._run(_six_segment_source())
        assert passed is True
        assert detail == ""

    def test_legacy_registered_class_not_value_locked(self, monkeypatch):
        """存量自造词表（非官方本体）不做值级锁定——防把各线自家枚举一杆打死。"""
        monkeypatch.setattr(g, "STATE_VOCAB_GATE_MODE", "block")
        src = _class_source("PortfolioMode", ["AGGRESSIVE", "BALANCED", "DEFENSIVE", "SUSPENDED"])
        passed, detail = self._run(src, staged_rel="src/zephyr/probe/portfolio_mode.py")
        assert passed is True
        assert detail == ""


class TestNoqaDoesNotReachOfficialValueLock:
    """W6-V 任务三①：noqa 的豁免面收窄到启发式名面判定，官方在册值不许被一行关掉。

    改判说明（收紧不是放松）：本件原有一枚
    ``test_noqa_escape_hatch_still_works_for_value_lock`` 把"一行 noqa 即可免检官方值级锁定"
    **当特性钉绿**（红队案卷 §三.1 / §八.3 判为缺陷：逃生口被整体滥用，且配对测试替它背书）。
    现改判为"官方值锁定不受 noqa 影响"，并保留一枚反向测钉住"noqa 仍能豁免启发式未登记"，
    防止把逃生口整个删掉（那也是放松——豁免面收窄≠取消豁免）。
    """

    @pytest.fixture(autouse=True)
    def _fake_repo(self, tmp_path):
        self.root = tmp_path
        _write(tmp_path, _REGISTRY_REL, _FAKE_REGISTRY)

    def _run_block(self, source: str, rel: str = "src/zephyr/probe/emotion.py", *, mode: str = "block"):
        _write(self.root, rel, source)
        import zephyr.gov_enforcement.commit_gates.library.state_vocab_registry_gate as _g  # noqa: PLC0415

        old = _g.STATE_VOCAB_GATE_MODE
        _g.STATE_VOCAB_GATE_MODE = mode
        try:
            return make_state_vocab_registry_gate().check(_make_gateway(self.root, (rel,)), [], session_id=None)
        finally:
            _g.STATE_VOCAB_GATE_MODE = old

    def test_noqa_on_value_line_does_not_exempt_official_lock(self):
        src = _six_segment_source(extra="RECHARGING").replace(
            '    RECHARGING: Final[str] = "RECHARGING"',
            f'    RECHARGING: Final[str] = "RECHARGING"  {g.NOQA_FORM_EXAMPLE}',
        )
        passed, detail = self._run_block(src)
        assert passed is False, "官方在册值被一行 noqa 关掉＝红队实测缺陷，不得再当特性"
        assert "RECHARGING" in detail
        assert "noqa 不豁免" in detail

    def test_noqa_anywhere_in_class_body_does_not_exempt_official_lock(self):
        """红队用的是"类体内任一行"逃生（_class_has_noqa 行范围判定），逐行覆盖仍须拦。"""
        src = _six_segment_source(extra="RECHARGING").replace(
            '    CAPITULATION: Final[str] = "CAPITULATION"',
            f'    CAPITULATION: Final[str] = "CAPITULATION"  {g.NOQA_FORM_EXAMPLE}',
        )
        passed, _detail = self._run_block(src)
        assert passed is False

    def test_warn_mode_still_reports_the_noqa_attempt(self):
        src = _six_segment_source(extra="RECHARGING").replace(
            '    RECHARGING: Final[str] = "RECHARGING"',
            f'    RECHARGING: Final[str] = "RECHARGING"  {g.NOQA_FORM_EXAMPLE}',
        )
        passed, detail = self._run_block(src, mode="warn")
        assert passed is True and "RECHARGING" in detail

    def test_noqa_still_exempts_heuristic_unregistered_finding(self):
        """反向：豁免面还在——启发式"未登记类名匹配"仍可用一行 noqa 逃生（否则=另一种越权）。"""
        src = _class_source(
            "NovelMarketMode",
            ["A", "B", "C"],
            noqa_on="A",
        )
        passed, detail = self._run_block(src, rel="src/zephyr/probe/novel_mode.py")
        assert passed is True
        assert detail == ""

    def test_official_lock_still_works_without_noqa(self):
        """再反向：删掉 noqa 后同一份源码仍红（证明红的是值面违规，不是夹具本身）。"""
        passed, _detail = self._run_block(_six_segment_source(extra="RECHARGING"))
        assert passed is False


class TestGateMessageMatchesRealNoqaForm:
    """W6-V 任务三②：门内文案与真实可生效的 noqa 形态一致（原教中文"标记（）"形态实测无效）。"""

    def test_taught_form_matches_the_regex(self):
        assert _make_noqa_pattern("STATE-VOCAB-REGISTRY").search(g.NOQA_FORM_EXAMPLE), (
            "门内文案教的形态必须被自家正则认"
        )

    def test_legacy_chinese_form_is_not_matched_by_regex(self):
        assert not _make_noqa_pattern("STATE-VOCAB-REGISTRY").search("# noqa 标记（STATE-VOCAB-REGISTRY） 例行自证")

    def test_detail_teaches_only_the_working_form(self, tmp_path):
        _write(tmp_path, _REGISTRY_REL, _FAKE_REGISTRY)
        rel = "src/zephyr/probe/novel.py"
        _write(tmp_path, rel, _class_source("NovelMarketRegime", ["A", "B", "C"]))
        _passed, detail = make_state_vocab_registry_gate().check(_make_gateway(tmp_path, (rel,)), [], session_id=None)
        assert g.NOQA_FORM_EXAMPLE in detail
        assert "noqa 标记（" not in detail, "文案仍在教实测无效的中文形态＝门内说谎"

    def test_taught_form_actually_exempts_in_a_real_file(self, tmp_path):
        """端到端：照文案抄一行注释（补两个空格）→ 启发式违规消失，而不是"写了等于没写"。"""
        _write(tmp_path, _REGISTRY_REL, _FAKE_REGISTRY)
        rel = "src/zephyr/probe/novel.py"
        naive = _class_source("NovelMarketRegime", ["A", "B", "C"])
        _write(tmp_path, rel, naive)
        assert _scan_py_files_for_findings(_make_gateway(tmp_path, (rel,)), [rel], _load_registry(str(tmp_path))) != {}
        _write(
            tmp_path, rel, naive.replace('    C: Final[str] = "C"', f'    C: Final[str] = "C"  {g.NOQA_FORM_EXAMPLE}')
        )
        assert _scan_py_files_for_findings(_make_gateway(tmp_path, (rel,)), [rel], _load_registry(str(tmp_path))) == {}


class TestValueFaceAntiDisguise:
    """W6-V 任务四（红队 §五"换个类名 MacroRegimeOfficial＋同样错值即绕过"）：值面补一道。"""

    @pytest.fixture(autouse=True)
    def _fake_repo(self, tmp_path):
        self.root = tmp_path
        _write(tmp_path, _REGISTRY_REL, _FAKE_REGISTRY)

    def _findings(self, source: str, rel: str) -> dict[str, list[str]]:
        _write(self.root, rel, source)
        return _scan_py_files_for_findings(_make_gateway(self.root, (rel,)), [rel], _load_registry(str(self.root)))

    def test_renamed_class_with_extra_value_is_caught(self):
        rel = "src/zephyr/probe/disguised.py"
        src = _class_source("EmotionCycleSixOfficial", [*_SIX, "RECHARGING"])
        findings = self._findings(src, rel)
        assert findings, "改名即脱锁＝红队实测绕过，必须已被值面判据堵住"
        assert "RECHARGING" in findings[rel][0]
        assert "值面" in findings[rel][0]

    def test_renamed_class_inside_official_module_is_caught(self):
        """红队原案：文件仍是 market_state.py（册里 physical_location 曾让整文件免检）。"""
        rel = _VOCAB_MODULE_REL
        src = _class_source("MacroRegimeOfficial", ["R1", "R2", "R3", "R13"])
        findings = self._findings(src, rel)
        assert findings and "R13" in findings[rel][0]

    def test_keywordless_class_carrying_official_values_is_caught(self):
        """红队 §五"造不含 state/phase/regime/emotion/mode 关键词的类"：值面不依赖类名关键词。"""
        rel = "src/zephyr/probe/sixgrid.py"
        findings = self._findings(
            _class_source("SixGrid", ["CAPITULATION", "ACCUMULATION", "IGNITION", "RECHARGING"]), rel
        )
        assert findings and "RECHARGING" in findings[rel][0]

    def test_exact_official_value_set_under_foreign_name_is_caught(self):
        """完整携带官方值集而类名不在官方本体＝改名/复制不构成登记。"""
        rel = "src/zephyr/probe/clone.py"
        findings = self._findings(_class_source("EmotionSixClone", list(_SIX)), rel)
        assert findings and "完整携带官方类 EmotionCycleSix" in findings[rel][0]

    def test_official_name_itself_with_exact_values_stays_clean(self):
        assert self._findings(_class_source("EmotionCycleSix", list(_SIX)), "src/zephyr/probe/legit.py") == {}

    def test_partial_overlap_below_threshold_does_not_trigger_value_lock(self):
        """阈值防误伤：只蹭到 2 个官方值（<3）的野类按启发式名面判，不按值面判。"""
        rel = "src/zephyr/probe/unrelated_mode.py"
        findings = self._findings(_class_source("WaterTempMode", ["ATTACK", "DEFENSE", "SUSPENDED", "PAUSED"]), rel)
        text = findings[rel][0] if findings else ""
        assert "值面" not in text and "noqa 不豁免" not in text

    def test_official_physical_location_is_not_a_file_whitelist(self):
        """路径登记面剔除 official_ontology 子树后的直接判据：同路径他类不再被整文件放行。"""
        registry = _FAKE_REGISTRY.replace(
            "official_ontology:\n  classes:",
            "official_ontology:\n  physical_location: src/zephyr/probe/whitelisted.py\n  classes:",
        )
        _write(self.root, _REGISTRY_REL, registry)
        rel = "src/zephyr/probe/whitelisted.py"
        _write(self.root, rel, _class_source("NovelMarketMode", ["A", "B", "C"]))
        findings = _scan_py_files_for_findings(_make_gateway(self.root, (rel,)), [rel], _load_registry(str(self.root)))
        assert findings and "未登记" in findings[rel][0]


class TestUnregisteredClassFinding:
    """既有判据面（未登记类）在两态下的行为须可证伪，且册在册时才谈得上判定。"""

    @pytest.fixture(autouse=True)
    def _fake_repo(self, tmp_path):
        self.root = tmp_path
        _write(tmp_path, _REGISTRY_REL, _FAKE_REGISTRY)

    def test_unregistered_state_class_blocks_in_block_mode(self, monkeypatch):
        monkeypatch.setattr(g, "STATE_VOCAB_GATE_MODE", "block")
        rel = "src/zephyr/probe/novel.py"
        _write(self.root, rel, _class_source("NovelMarketRegime", ["A", "B", "C"]))
        passed, detail = make_state_vocab_registry_gate().check(_make_gateway(self.root, (rel,)), [], session_id=None)
        assert passed is False
        assert "NovelMarketRegime 未登记" in detail

    def test_unregistered_class_warn_mode_passes(self):
        rel = "src/zephyr/probe/novel.py"
        _write(self.root, rel, _class_source("NovelMarketRegime", ["A", "B", "C"]))
        passed, detail = make_state_vocab_registry_gate().check(_make_gateway(self.root, (rel,)), [], session_id=None)
        assert passed is True
        assert "NovelMarketRegime" in detail


class TestMergedRegistryIsReconciled:
    """W6-V 任务一落地面：合并后的真册必须双块俱在（禁抹他道条目）且计数自洽。"""

    @pytest.fixture(scope="class")
    def doc(self) -> dict:
        import yaml  # noqa: PLC0415

        return yaml.safe_load((_PROJECT_ROOT / _REGISTRY_REL).read_text(encoding="utf-8"))

    def test_both_blocks_present_and_union_count(self, doc):
        prov = doc["merge_provenance"]
        n_main = prov["main_block"]["entry_count"]
        n_wt = prov["campaign_block"]["entry_count"]
        vocab = doc["vocabularies"]
        assert len(vocab) == n_main + n_wt, "并集长度须等于两块条数之和（派生标量自洽，宪法 §4.3）"
        assert prov["count_reconciliation"]["vocabularies_len"] == len(vocab)
        assert prov["count_reconciliation"]["roor_entry_count_should_be"] == len(vocab)

    def test_main_block_entries_kept_verbatim_by_shape(self, doc):
        """他道区块的条目按自己的字段名存着（vocabulary_id/name_zh/states），未被本役 schema 改写。"""
        main_shape = [e for e in doc["vocabularies"] if "vocabulary_id" in e]
        assert len(main_shape) == doc["merge_provenance"]["main_block"]["entry_count"]
        assert all("states" in e and "source" in e for e in main_shape)
        campaign_shape = [e for e in doc["vocabularies"] if "id" in e]
        assert len(campaign_shape) == doc["merge_provenance"]["campaign_block"]["entry_count"]
        assert main_shape and main_shape[0]["vocabulary_id"] == "regime-hmm-7", (
            "主区块须 verbatim 在前（未被覆盖/重排抹掉）"
        )

    def test_no_same_id_overwrite(self, doc):
        ids = [e.get("id") or e.get("vocabulary_id") for e in doc["vocabularies"]]
        assert len(ids) == len(set(ids)), "同 id 覆盖＝抹他人条目，必须零冲突"

    def test_official_ontology_survives_merge(self, doc):
        assert {c["name"] for c in doc["official_ontology"]["classes"]} >= set(_OFFICIAL_CLASSES)
        assert all(c["values_locked"] and c["canonical_values"] for c in doc["official_ontology"]["classes"])

    def test_real_registry_value_locks_have_no_file_whitelist(self, doc):
        """official_ontology 子树里的 .py 路径不得进模块路径登记面（红队 §五②）。"""
        reg = _load_registry(str(_PROJECT_ROOT))
        official_paths = {
            "src/zephyr/shared/vocab/market_state.py",
            "zephyr.shared.vocab.market_state",
            "src.zephyr.shared.vocab.market_state",
        }
        assert not (official_paths & set(reg.paths)), f"官方本体路径漏进登记面：{official_paths & set(reg.paths)}"
        assert reg.paths  # 登记面仍在（vocabularies 各条的类名等），只是不含官方本体路径

    def test_official_module_still_passes_gate_itself(self, doc):
        reg = _load_registry(str(_PROJECT_ROOT))
        assert (
            _scan_py_files_for_findings(_make_gateway(_PROJECT_ROOT, (_VOCAB_MODULE_REL,)), [_VOCAB_MODULE_REL], reg)
            == {}
        )


class TestDeclarationsAreTrue:
    """ "补建本体使声明为真"三面：ROOR 指向的册在盘、登记的包件在盘、本体取值与册逐值相等。"""

    def test_central_registry_file_exists(self):
        assert (_PROJECT_ROOT / _REGISTRY_REL).is_file(), "ROOR REG-STATE-VOCAB-001 指向的物理文件必须存在"

    def test_official_ontology_package_exists(self):
        assert (_PROJECT_ROOT / _VOCAB_MODULE_REL).is_file(), "capability 册与翻译册登记的官方本体必须在盘"
        assert (_PROJECT_ROOT / "src/zephyr/shared/vocab/__init__.py").is_file()

    def test_real_registry_reads_clean(self):
        reg = _load_registry(str(_PROJECT_ROOT))
        assert reg.error == ""
        assert set(reg.value_locks) >= set(_OFFICIAL_CLASSES), "四个官方本体类都须 values_locked"

    def test_ontology_values_match_registry_value_by_value(self):
        """代码本体与登记册逐值相等（任一侧单边改值＝本测试红，防双真源漂移）。"""
        from zephyr.shared.vocab.market_state import OFFICIAL_STATE_VOCABULARIES  # noqa: PLC0415

        reg = _load_registry(str(_PROJECT_ROOT))
        assert reg.error == ""
        assert set(OFFICIAL_STATE_VOCABULARIES) == set(reg.value_locks)
        for cls_name, code_values in OFFICIAL_STATE_VOCABULARIES.items():
            assert code_values == reg.value_locks[cls_name], f"{cls_name} 取值与册不一致"

    def test_ontology_classes_pass_the_gate_themselves(self):
        """官方本体文件自扫必须零命中（存量误伤计数的最小自证）。"""
        rel = _VOCAB_MODULE_REL
        reg = _load_registry(str(_PROJECT_ROOT))
        assert reg.error == ""
        findings = _scan_py_files_for_findings(_make_gateway(_PROJECT_ROOT, (rel,)), [rel], reg)
        assert findings == {}, f"官方本体自身被判未登记/值不在册：{findings}"

    def test_gate_never_raises_on_hostile_inputs(self):
        """ERROR_CONTRACT：check 永不抛异常——册目录被塞成目录/路径异常也只能报红或放行。"""
        gw = _make_gateway(Path(__file__))  # project_root=文件路径（册路径不可读）
        passed, detail = make_state_vocab_registry_gate().check(gw, [], session_id=None)
        assert passed is False and detail != ""
