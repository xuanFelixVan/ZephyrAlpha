# [BLUEPRINT] MOD-INF-037 | scripts/governance/next_ruling_id.py | §三件断言尺
# [TTL] permanent
# [MODULE] tests.governance.test_next_ruling_id
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.next_ruling_id
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] tmp_path 假册测取号器三件断言尺（Z-38）：--next 递增（在册 max+1）、在途占号感知（claim 文件跳号）、--claim O_EXCL 原子占号（并发同候选号仅一成）、--release 仅本 session、--check 悬空检出（主号缺/后缀缺两态）+ 干净面 rc=0 + 豁免区不扫 + 名册缺失 rc=2
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-TEST_NEXT_RULING_ID | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_next_ruling_id.py — 裁定#NNN 取号器单元测试（Z-38 / 波 5.2）

覆盖（全部 tmp_path 假册，零生产路径写入）：
- read_registered_numbers: 号段计算锚定 ruling_id 声明键（related_rulings 引用不误入）
- cmd_next: 在册最大号+1；在途占号感知跳号
- cmd_claim: O_EXCL 原子占号；并发同候选号败者递增；payload 留痕字段
- cmd_release: 仅本 session 可释放；他 session 拒绝 rc=2
- cmd_check: 悬空号检出（main-missing / suffix-missing）；干净面 rc=0；tests/ 与非扫描后缀豁免
- 名册缺失: rc=2 fail-closed（不猜测号段）
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "governance"))

import next_ruling_id as nri  # noqa: E402

REGISTRY_SUB = Path("docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml")

REGISTRY_BODY = """\
module_id: REG-RULING-001
entries:
- ruling_id: '裁定#19'
- ruling_id: '裁定#19-A'
- ruling_id: "裁定#413"
  related_rulings: ['裁定#999']
"""


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    reg = tmp_path / REGISTRY_SUB
    reg.parent.mkdir(parents=True)
    reg.write_text(REGISTRY_BODY, encoding="utf-8")
    return tmp_path


def _write_doc(repo_root: Path, rel: str, text: str) -> Path:
    p = repo_root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


# ── read_registered_numbers ──


def test_read_registered_numbers_anchored_to_declaration_key(repo: Path) -> None:
    ids, max_main, count = nri.read_registered_numbers(repo)
    assert max_main == 413
    assert count == 3  # related_rulings 里的 裁定#999 引用不计入条目数
    assert "413" in ids and "19-A" in ids
    assert "999" not in ids  # 册内引用不误入在册集合（grep-and-claim 旧病反噬防护）


def test_registry_missing_raises_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        nri.read_registered_numbers(tmp_path)


# ── --next ──


def test_next_is_registry_max_plus_one(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert nri.cmd_next(repo) == 0
    out = capsys.readouterr().out
    assert "在册最大主号: #413" in out
    assert "下一可用号: 裁定#414" in out


def test_next_json_payload(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert nri.cmd_next(repo, as_json=True) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["next_candidate"] == 414
    assert payload["max_registered_main"] == 413


def test_next_skips_inflight_claims(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    claim_dir = repo / nri.CLAIM_DIR_REL
    claim_dir.mkdir(parents=True)
    (claim_dir / "claim_414.json").write_text(json.dumps({"session": "s1"}), encoding="utf-8")
    assert nri.cmd_next(repo) == 0
    out = capsys.readouterr().out
    assert "在途占号 1 个" in out
    assert "下一可用号: 裁定#415" in out


# ── --claim ──


def test_claim_creates_o_excl_claim_file(repo: Path) -> None:
    rc = nri.cmd_claim(repo, "sess-a")
    assert rc == 0
    f = repo / nri.CLAIM_DIR_REL / "claim_414.json"
    payload = json.loads(f.read_text(encoding="utf-8"))
    assert payload["session"] == "sess-a"
    assert payload["ruling_id"] == "裁定#414"
    assert payload["pid"] > 0


def test_claim_second_session_gets_next_number(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert nri.cmd_claim(repo, "sess-a") == 0
    capsys.readouterr()
    assert nri.cmd_claim(repo, "sess-b") == 0
    out = capsys.readouterr().out
    assert "裁定#415" in out  # 在途占号感知：被占即递增（O_EXCL 败者通道语义）


def test_claim_requires_session(repo: Path) -> None:
    assert nri.cmd_claim(repo, "") == 2
    assert nri.cmd_claim(repo, "  ") == 2


# ── --release ──


def test_release_own_session_only(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert nri.cmd_claim(repo, "sess-a") == 0
    assert nri.cmd_release(repo, 414, "sess-b") == 2  # 他 session 占号拒绝代删
    capsys.readouterr()
    assert nri.cmd_release(repo, 414, "sess-a") == 0
    assert not (repo / nri.CLAIM_DIR_REL / "claim_414.json").exists()
    assert nri.cmd_release(repo, 414, "sess-a") == 0  # 幂等：不存在=已释放


# ── --check ──


def test_check_detects_dangling_refs(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _write_doc(repo, "case1/note.md", "依据 裁定#413 正规；但 裁定#999 悬空；子号 裁定#413-X 也悬空")
    assert nri.cmd_check(repo, [repo / "case1"]) == 1
    out = capsys.readouterr().out
    assert "裁定#999" in out and "main-missing" in out
    assert "裁定#413-X" in out and "suffix-missing" in out
    assert "裁定#413  [" not in out  # 在册主号本体不报（后缀悬空行 裁定#413-X 不算主号命中）


def test_check_clean_face_returns_zero(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _write_doc(repo, "case2/clean.md", "只有 裁定#413 与 裁定#19-A，全在册")
    assert nri.cmd_check(repo, [repo / "case2"]) == 0
    assert "悬空裁定号: 无" in capsys.readouterr().out


def test_check_excludes_tests_dir_and_non_scan_suffix(repo: Path, tmp_path: Path) -> None:
    # 独立净册（无 related_rulings 干扰项），扫描 scope=整个假仓，验证豁免区/后缀过滤
    reg = repo / REGISTRY_SUB
    reg.write_text("entries:\n- ruling_id: '裁定#19'\n- ruling_id: \"裁定#413\"\n", encoding="utf-8")
    _write_doc(repo, "tests/test_x.py", "裁定#777")  # 豁免区
    _write_doc(repo, "docs/x.txt", "裁定#778")  # 非扫描后缀
    assert nri.cmd_check(repo, [repo]) == 0  # 两者都不进扫描面


def test_check_alignment_checklist_current_face_is_clean(repo: Path) -> None:
    """Z-33 首跑判据镜像：只含在册号的对账清单面必须判净（悬空号清雷验收口径）。"""
    _write_doc(repo, "sop/governance_sop/alignment_checklist.md", "十一图升级 裁定#413（正式通道）")
    assert nri.cmd_check(repo, [repo / "sop"]) == 0


# ── main 模式互斥 ──


def test_main_rejects_multiple_modes(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(nri, "REPO_ROOT", repo)
    with pytest.raises(SystemExit) as ei:
        nri.main(["--next", "--check", "docs"])
    assert ei.value.code == 2


def test_main_check_exit_code(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(nri, "REPO_ROOT", repo)
    _write_doc(repo, "docs/dangling.md", "悬空 裁定#999")
    assert nri.main(["--check", "docs"]) == 1
