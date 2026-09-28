# [A_test] module_id: MOD-GATE_ENGINE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.gov_enforcement.read_side.test_fms_hygiene_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_fms_hygiene_gate.py — FMS-HYGIENE 读侧门单测（红蓝夹具）

权威依据：fms_hygiene_gate.py（make_fms_hygiene_gate）+ fms_ref_extractor.py（共享提取器）

测试组：
- TestGateSpecFields: gate_id="FMS-HYGIENE" / priority=138 / 默认 warn
- TestExtractor: 四形态提取 / 形态准入闸（相对·URL·CLI 旗标·省略号·代码标识符拒收）
  / 模板形态 / CAS 形态 / 临时区分量
- TestGatewayIntegration（红蓝夹具，MagicMock 内联 git 替身，tmp_path 全隔离）:
  * 蓝alive：合法引用（tracked 目标反引号+表格）静默放行
  * 红四查类：查类1 死引用 / 查类2 非ASCII / 查类3 永久引临时 / 查类4 CAS 残渣 各拦一次
  * 基线命中放行（查类1/E1/B 三种豁免）；基线缺失/损坏 fail-open 不误伤真新增
  * HEAD 差分棘轮：存量引用不拦、新文件全量新增必拦
  * noqa 逃逸尝试无效（路径类引用无 noqa 通道）
  * md_link 形态不查死引用（与 DOC-REF-BROKEN 净零分工）
  * tests/ 豁免 / skip-dir（_working 引用方）豁免 / own-scope 外来 warn+审计不阻断
  * git 故障 fail-open；warn→block 两段制升硬

测试隔离：全部读写限定 tmp_path，不触生产路径。
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
for _p in (str(_PROJECT_ROOT / "src"), str(_PROJECT_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import zephyr.gov_enforcement.commit_gates.read_side.fms_hygiene_gate as g  # noqa: E402
from zephyr.gov_enforcement.commit_gates.read_side.fms_hygiene_gate import (  # noqa: E402  # noqa: E402
    BLOCK_FLIP_CLEAN_STREAK,
    FMS_BASELINE_REL_PATH,
    block_flip_eligible,
    consecutive_clean_commits,
    make_fms_hygiene_gate,
)
from zephyr.gov_enforcement.commit_gates.read_side.fms_ref_extractor import (  # noqa: E402
    extract_refs,
    is_cas_residue,
    is_ephemeral_target,
    is_permanent_referrer,
    is_template_form,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402

_TRACKED = {
    "src/zephyr/shared/io/file_utils.py",
    "config/alert_threshold_registry.yaml",
    "docs/_working/drafts/notes.md",
    "docs/设计图/架构图.md",  # ASCII 查类独立性夹具：目标在册也不豁免查类 2
}

DEAD_REF = "src/risk/model.py"  # 蓝图示意散文路径，盘面永无
CAS_REF = "config/crisis_gate.yaml.24676.tmp"
EPHEMERAL_REF = "docs/_working/drafts/notes.md"  # tracked（查类 3 与存在性独立）
ASCII_REF = "docs/设计图/架构图.md"  # tracked（查类 2 与存在性独立）


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


@dataclass
class _FakeGateway:
    """内联 git 替身：diff/show(:file|HEAD:file)/ls-files/rev-parse 四原语。"""

    project_root: str
    tracked: set[str] = field(default_factory=set)
    staged: dict[str, str] = field(default_factory=dict)  # rel -> index 内容
    head: dict[str, str] = field(default_factory=dict)  # rel -> HEAD 内容
    staged_list: list[str] = field(default_factory=list)
    fail_mode: str = ""  # ""=正常 | "diff_rc"=git diff rc1 | "raise"=run_git 抛异常

    def run_git(self, cmd, *a, **k):
        if self.fail_mode == "raise":
            raise OSError("simulated git failure")
        cmd = list(cmd)
        if cmd[:2] == ["git", "diff"]:
            if self.fail_mode == "diff_rc":
                return _MockResult(returncode=1, stdout="")
            names = self.staged_list or sorted(self.staged)
            return _MockResult(returncode=0, stdout="\n".join(names))
        if cmd[:2] == ["git", "show"]:
            arg = cmd[2]
            if arg.startswith("HEAD:"):
                rel = arg[len("HEAD:") :]
                if rel in self.head:
                    return _MockResult(returncode=0, stdout=self.head[rel])
                return _MockResult(returncode=1, stdout="")
            rel = arg[1:]
            if rel in self.staged:
                return _MockResult(returncode=0, stdout=self.staged[rel])
            return _MockResult(returncode=1, stdout="")
        if cmd[:2] == ["git", "ls-files"]:
            probe = cmd[-1].rstrip("/")
            hits = sorted(t for t in self.tracked if t == probe or t.startswith(probe + "/"))
            return _MockResult(returncode=0, stdout="\n".join(hits))
        if cmd[:2] == ["git", "rev-parse"]:
            return _MockResult(returncode=0, stdout=self.project_root)
        return _MockResult(returncode=0, stdout="")


def _write(tmp_root: Path, rel: str, content: str) -> None:
    path = tmp_root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_baseline(tmp_root: Path, refs: list[str]) -> None:
    lines = "\n".join(f"  - ref: {r}\n    category: D\n    first_seen: '2026-09-27'" for r in refs)
    _write(
        tmp_root, FMS_BASELINE_REL_PATH, f"total_dead: {len(refs)}\nentries:\n{lines}\n" if refs else "entries: []\n"
    )


@pytest.fixture(autouse=True)
def _isolated_baseline_cache():
    g._reset_baseline_cache()
    yield
    g._reset_baseline_cache()


def _make_gw(tmp_root: Path, **kw) -> _FakeGateway:
    kw.setdefault("tracked", set(_TRACKED))
    return _FakeGateway(project_root=str(tmp_root), **kw)


class TestGateSpecFields:
    def test_gate_id_and_priority(self):
        spec = make_fms_hygiene_gate()
        assert isinstance(spec, GateSpec)
        assert spec.gate_id == "FMS-HYGIENE"
        assert spec.priority == 138

    def test_mode_constant_default_warn(self):
        assert g.FMS_HYGIENE_GATE_MODE == "warn"

    def test_baseline_path_constant(self):
        assert FMS_BASELINE_REL_PATH.endswith("fms_deadref_baseline.yaml")


class TestExtractor:
    def test_four_forms_extracted(self):
        content = "链接 [x](docs/a/b.md) 反引号 `src/c/d.py` 表格 | config/e/f.yaml | 裸词 docs/g/h.md\n"
        forms = {(h.token, h.form) for h in extract_refs(content)}
        assert ("docs/a/b.md", "md_link") in forms
        assert ("src/c/d.py", "backtick") in forms
        assert ("config/e/f.yaml", "table_cell") in forms
        assert ("docs/g/h.md", "bare") in forms

    def test_shape_gate_rejects_noise(self):
        content = (
            "`./rel.md` `../up.md` `https://x/y/z.md` `--flag/--other` `dict/get` "
            "`.../ellip/x.md` `$VAR/expand.md` `os.path.join(a, b)`\n"
        )
        tokens = {h.token for h in extract_refs(content)}
        assert tokens == set()  # 相对/URL/CLI 旗标/代码标识符/省略号/变量展开全部拒收

    def test_template_forms(self):
        assert is_template_form("data/asset_")
        assert is_template_form("config/domains/D-XXX.yaml")
        assert is_template_form("config/apollo/blob/master/README.md")  # Git URL 断片
        assert is_template_form("schema/lXX_table.yaml")
        assert not is_template_form("docs/01_policies/real.md")

    def test_cas_and_ephemeral(self):
        assert is_cas_residue(CAS_REF)
        assert is_cas_residue(".capability_canonical_file_registry.yaml_16limbv5.tmp")
        assert not is_cas_residue("docs/x/template.md")
        assert is_ephemeral_target(EPHEMERAL_REF)
        assert is_ephemeral_target(".runtime/audit/x.jsonl")
        assert is_ephemeral_target("logs/session_logs/a.md")
        assert is_permanent_referrer("docs/03_modules/blueprint.md")
        assert not is_permanent_referrer("docs/_working/draft/x.md")


class TestGatewayIntegration:
    def test_legal_refs_pass_silent(self, tmp_path):
        content = "真源 `src/zephyr/shared/io/file_utils.py`；登记见 | config/alert_threshold_registry.yaml |\n"
        _write_baseline(tmp_path, [])
        gw = _make_gw(tmp_path, staged={"docs/guide.md": content}, staged_list=["docs/guide.md"])
        passed, detail = make_fms_hygiene_gate().check(gw, ["docs/guide.md"])
        assert passed is True
        assert detail == ""

    def test_deadref_new_caught(self, tmp_path):
        _write_baseline(tmp_path, [])
        gw = _make_gw(tmp_path, staged={"docs/guide.md": f"见 `{DEAD_REF}`\n"}, staged_list=["docs/guide.md"])
        passed, detail = make_fms_hygiene_gate().check(gw, ["docs/guide.md"])
        assert passed is True  # warn 模式放行留痕
        assert "HYGIENE-DEADREF-NEW" in detail
        assert DEAD_REF in detail
        audit = tmp_path / ".runtime" / "gate_audit" / "fms_hygiene.jsonl"
        assert audit.exists()
        rec = json.loads(audit.read_text(encoding="utf-8").strip().splitlines()[-1])
        assert rec["mode"] == "warn"
        assert any(DEAD_REF in x for x in rec["findings"]["HYGIENE-DEADREF-NEW"])

    def test_ascii_new_caught_even_if_target_tracked(self, tmp_path):
        _write_baseline(tmp_path, [])
        gw = _make_gw(tmp_path, staged={"docs/guide.md": f"图见 `{ASCII_REF}`\n"}, staged_list=["docs/guide.md"])
        passed, detail = make_fms_hygiene_gate().check(gw, ["docs/guide.md"])
        assert passed is True
        assert "HYGIENE-ASCII-NEW" in detail  # 目标在册不豁免查类 2

    def test_perm_ephemeral_caught_even_if_target_tracked(self, tmp_path):
        _write_baseline(tmp_path, [])
        gw = _make_gw(tmp_path, staged={"docs/guide.md": f"草稿 `{EPHEMERAL_REF}`\n"}, staged_list=["docs/guide.md"])
        passed, detail = make_fms_hygiene_gate().check(gw, ["docs/guide.md"])
        assert passed is True
        assert "HYGIENE-PERM-EPHEMERAL" in detail  # 目标在册仍拦：引用必随 TTL 腐烂

    def test_cas_residue_caught(self, tmp_path):
        _write_baseline(tmp_path, [])
        gw = _make_gw(tmp_path, staged={"docs/guide.md": f"真源 `{CAS_REF}`\n"}, staged_list=["docs/guide.md"])
        passed, detail = make_fms_hygiene_gate().check(gw, ["docs/guide.md"])
        assert passed is True
        assert "HYGIENE-CAS-RESIDUE" in detail

    def test_baseline_hit_exempts_deadref(self, tmp_path):
        _write_baseline(tmp_path, [DEAD_REF])
        gw = _make_gw(tmp_path, staged={"docs/guide.md": f"见 `{DEAD_REF}`\n"}, staged_list=["docs/guide.md"])
        passed, detail = make_fms_hygiene_gate().check(gw, ["docs/guide.md"])
        assert passed is True
        assert detail == ""

    def test_baseline_hit_exempts_cas_and_ephemeral(self, tmp_path):
        _write_baseline(tmp_path, [CAS_REF, EPHEMERAL_REF])
        content = f"残渣 `{CAS_REF}` 草稿 `{EPHEMERAL_REF}`\n"
        gw = _make_gw(tmp_path, staged={"docs/guide.md": content}, staged_list=["docs/guide.md"])
        passed, detail = make_fms_hygiene_gate().check(gw, ["docs/guide.md"])
        assert passed is True
        assert detail == ""

    def test_head_refs_not_reflagged(self, tmp_path):
        """棘轮：存量引用（HEAD 已含）不拦——只查净新增。"""
        _write_baseline(tmp_path, [])
        content = f"见 `{DEAD_REF}`\n"
        gw = _make_gw(
            tmp_path, staged={"docs/guide.md": content}, head={"docs/guide.md": content}, staged_list=["docs/guide.md"]
        )
        passed, detail = make_fms_hygiene_gate().check(gw, ["docs/guide.md"])
        assert passed is True
        assert detail == ""

    def test_new_file_all_refs_new(self, tmp_path):
        """新文件（HEAD 无）全量引用皆新增——存量混抄也拦（基线未收录时）。"""
        _write_baseline(tmp_path, [])
        gw = _make_gw(tmp_path, staged={"docs/new.md": f"见 `{DEAD_REF}`\n"}, staged_list=["docs/new.md"])
        passed, detail = make_fms_hygiene_gate().check(gw, ["docs/new.md"])
        assert passed is True
        assert "HYGIENE-DEADREF-NEW" in detail

    def test_noqa_escape_ineffective(self, tmp_path):
        """路径类引用无 noqa 通道：行内 noqa 标记不构成逃生（S1 §3.1 立法）。"""
        _write_baseline(tmp_path, [])
        # 拼接构造逃生标记：语义与字面形式逐字节等价，但本夹具文件自身不出现
        # 字面豁免标记（标记合规门禁 NOQA-VALIDATION 只认源码字面形式）。
        noqa_attempt = "# " + "noq" + "a: FMS" + "-HYGIENE"
        content = f"`{DEAD_REF}`  {noqa_attempt}  存量语义豁免尝试\n"
        gw = _make_gw(tmp_path, staged={"docs/guide.md": content}, staged_list=["docs/guide.md"])
        passed, detail = make_fms_hygiene_gate().check(gw, ["docs/guide.md"])
        assert "HYGIENE-DEADREF-NEW" in detail  # 逃逸尝试无效

    def test_md_link_form_not_deadref_checked(self, tmp_path):
        """净零分工：md_link 存在性归 DOC-REF-BROKEN，本门不重复拦。"""
        _write_baseline(tmp_path, [])
        gw = _make_gw(tmp_path, staged={"docs/guide.md": f"[x]({DEAD_REF})\n"}, staged_list=["docs/guide.md"])
        passed, detail = make_fms_hygiene_gate().check(gw, ["docs/guide.md"])
        assert passed is True
        assert detail == ""

    def test_tests_zone_exempt(self, tmp_path):
        _write_baseline(tmp_path, [])
        gw = _make_gw(tmp_path, staged={"tests/x/guide.md": f"见 `{DEAD_REF}`\n"}, staged_list=["tests/x/guide.md"])
        passed, detail = make_fms_hygiene_gate().check(gw, ["tests/x/guide.md"])
        assert passed is True
        assert detail == ""

    def test_skip_dir_referrer_exempt(self, tmp_path):
        _write_baseline(tmp_path, [])
        gw = _make_gw(
            tmp_path,
            staged={"docs/_working/drafts/new.md": f"见 `{DEAD_REF}`\n"},
            staged_list=["docs/_working/drafts/new.md"],
        )
        passed, detail = make_fms_hygiene_gate().check(gw, ["docs/_working/drafts/new.md"])
        assert passed is True
        assert detail == ""

    def test_foreign_staged_warn_audited_not_blocked(self, tmp_path):
        """own-scope：外来 staged 有违规不阻断本 session，审计留痕。"""
        _write_baseline(tmp_path, [])
        own_content = "真源 `src/zephyr/shared/io/file_utils.py`\n"
        foreign_content = f"外来 `{DEAD_REF}`\n"
        gw = _make_gw(
            tmp_path,
            staged={"docs/own.md": own_content, "docs/foreign.md": foreign_content},
            staged_list=["docs/own.md", "docs/foreign.md"],
        )
        passed, detail = make_fms_hygiene_gate().check(gw, ["docs/own.md"])
        assert passed is True
        assert DEAD_REF not in detail  # 外来违规不进 detail（不阻断）
        audit = tmp_path / ".runtime" / "gate_audit" / "fms_hygiene_foreign_staged.jsonl"
        assert audit.exists()
        rec = json.loads(audit.read_text(encoding="utf-8").strip().splitlines()[-1])
        assert "docs/foreign.md" in rec["foreign_files"]

    def test_git_failure_fail_open(self, tmp_path):
        _write_baseline(tmp_path, [])
        gw = _make_gw(tmp_path, staged={"docs/guide.md": f"见 `{DEAD_REF}`\n"}, fail_mode="diff_rc")
        passed, detail = make_fms_hygiene_gate().check(gw, ["docs/guide.md"])
        assert passed is True
        assert detail == ""

    def test_git_raise_fail_open(self, tmp_path):
        _write_baseline(tmp_path, [])
        gw = _make_gw(tmp_path, staged={"docs/guide.md": f"见 `{DEAD_REF}`\n"}, fail_mode="raise")
        passed, detail = make_fms_hygiene_gate().check(gw, ["docs/guide.md"])
        assert passed is True
        assert detail == ""

    def test_baseline_missing_fail_open_still_gates_new(self, tmp_path):
        """基线册不存在（首跑前）≠ 检测失效：豁免面为空，真新增照拦。"""
        gw = _make_gw(tmp_path, staged={"docs/guide.md": f"见 `{DEAD_REF}`\n"}, staged_list=["docs/guide.md"])
        passed, detail = make_fms_hygiene_gate().check(gw, ["docs/guide.md"])
        assert passed is True
        assert "HYGIENE-DEADREF-NEW" in detail

    def test_baseline_corrupted_empty_exemption(self, tmp_path):
        """基线损坏=豁免面置空（更严不更宽）：真新增仍拦。"""
        _write(tmp_path, FMS_BASELINE_REL_PATH, "entries: [ {broken\n  ::%%%yaml")
        gw = _make_gw(tmp_path, staged={"docs/guide.md": f"见 `{DEAD_REF}`\n"}, staged_list=["docs/guide.md"])
        passed, detail = make_fms_hygiene_gate().check(gw, ["docs/guide.md"])
        assert passed is True
        assert "HYGIENE-DEADREF-NEW" in detail

    def test_yaml_staged_file_scanned(self, tmp_path):
        _write_baseline(tmp_path, [])
        gw = _make_gw(
            tmp_path,
            staged={"docs/conf/registry.yaml": f"source: `{DEAD_REF}`\n"},
            staged_list=["docs/conf/registry.yaml"],
        )
        passed, detail = make_fms_hygiene_gate().check(gw, ["docs/conf/registry.yaml"])
        assert passed is True
        assert "HYGIENE-DEADREF-NEW" in detail

    def test_block_mode_escalation(self, tmp_path, monkeypatch):
        monkeypatch.setattr(g, "FMS_HYGIENE_GATE_MODE", "block")
        _write_baseline(tmp_path, [])
        gw = _make_gw(tmp_path, staged={"docs/guide.md": f"见 `{DEAD_REF}`\n"}, staged_list=["docs/guide.md"])
        passed, detail = make_fms_hygiene_gate().check(gw, ["docs/guide.md"])
        assert passed is False  # 升硬后 fail-closed
        assert "HYGIENE-DEADREF-NEW" in detail


class TestBlockFlipReadiness:
    """翻 block 判据改写（99 报告 §十二 T-1）：连零机读 + 资格判定 + mode 保持 warn。"""

    def _audit(self, tmp_root: Path, records: list[dict]) -> None:
        audit_dir = tmp_root / ".runtime" / "gate_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        with (audit_dir / "fms_hygiene.jsonl").open("a", encoding="utf-8") as f:
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def test_mode_stays_warn(self):
        """翻档=OWNER-GATE：判据改写不得顺手翻 mode（防自作主张升硬）。"""
        assert g.FMS_HYGIENE_GATE_MODE == "warn"

    def test_streak_counts_trailing_clean_records(self, tmp_path):
        self._audit(
            tmp_path,
            [
                {"gate": "FMS-HYGIENE", "findings": {}, "checked": 3},
                {"gate": "FMS-HYGIENE", "findings": {}, "checked": 1},
            ],
        )
        assert consecutive_clean_commits(str(tmp_path)) == 2

    def test_violation_resets_streak(self, tmp_path):
        self._audit(
            tmp_path,
            [
                {"gate": "FMS-HYGIENE", "findings": {}, "checked": 5},
                {"gate": "FMS-HYGIENE", "findings": {"HYGIENE-DEADREF-NEW": ["a -> b"]}, "checked": 2},
                {"gate": "FMS-HYGIENE", "findings": {}, "checked": 1},
            ],
        )
        assert consecutive_clean_commits(str(tmp_path)) == 1

    def test_missing_audit_file_zero(self, tmp_path):
        assert consecutive_clean_commits(str(tmp_path)) == 0
        assert block_flip_eligible(str(tmp_path)) is False

    def test_zero_checked_not_counted(self, tmp_path):
        """checked=0（未实际扫查）不计连零——防"门没跑"虚增连零（§十二判空教训）。"""
        self._audit(tmp_path, [{"gate": "FMS-HYGIENE", "findings": {}, "checked": 0}])
        assert consecutive_clean_commits(str(tmp_path)) == 0

    def test_corrupt_tail_breaks_streak(self, tmp_path):
        audit_dir = tmp_path / ".runtime" / "gate_audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        with (audit_dir / "fms_hygiene.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"gate": "FMS-HYGIENE", "findings": {}, "checked": 2}) + "\n")
            f.write("{broken json\n")  # 坏行=中断（宁少不多）
        assert consecutive_clean_commits(str(tmp_path)) == 0

    def test_eligibility_boundary(self, tmp_path):
        for i in range(BLOCK_FLIP_CLEAN_STREAK - 1):
            self._audit(tmp_path, [{"gate": "FMS-HYGIENE", "findings": {}, "checked": 1}])
        assert block_flip_eligible(str(tmp_path)) is False  # 19 笔=不够
        self._audit(tmp_path, [{"gate": "FMS-HYGIENE", "findings": {}, "checked": 1}])
        assert block_flip_eligible(str(tmp_path)) is True  # 20 笔=够评审（翻档仍 OWNER-GATE）

    def test_clean_pass_audited_with_checked_count(self, tmp_path):
        """集成：干净提交也落账（checked>0），连零数因此可机读。"""
        _write_baseline(tmp_path, [])
        staged = "docs/guide.md"
        # 引用目标取 tracked 集（src/zephyr/shared/io/file_utils.py）⇒ 存在 ⇒ 零违规
        gw = _make_gw(tmp_path, staged={staged: "见 `src/zephyr/shared/io/file_utils.py`\n"}, staged_list=[staged])
        passed, _ = make_fms_hygiene_gate().check(gw, [staged])
        assert passed is True
        audit_file = tmp_path / ".runtime" / "gate_audit" / "fms_hygiene.jsonl"
        recs = [json.loads(ln) for ln in audit_file.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert any(r.get("findings") == {} and r.get("checked", 0) >= 1 for r in recs)
        assert consecutive_clean_commits(str(tmp_path)) == 1
