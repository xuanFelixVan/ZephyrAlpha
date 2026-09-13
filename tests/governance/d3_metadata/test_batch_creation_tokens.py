# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/batch_creation_tokens.py | §
# [MODULE] tests.governance.d3_metadata.test_batch_creation_tokens
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; yaml; scripts.governance.d3_metadata.batch_creation_tokens
# [CONSUMERS] 批量 token 工具质量守卫（纯插入/幂等/锚点 fail-closed）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 全部用例构造于 tmp 副本 registry（monkeypatch _REGISTRY，不碰生产）
# [MODIFY-GUARD] 与工具同批演进
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""batch_creation_tokens 工具测试——极限红蓝对抗 F1 治本守卫。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

import scripts.governance.d3_metadata.batch_creation_tokens as bct

_REPO = Path(__file__).resolve().parents[3]

_REG_BODY = """creation_tokens:
- file: docs/existing/anchor.md
  token: anchor-token-20260913
  created_by: someone
  capability: anchor_cap
- file: docs/existing/other.md
  token: other-token-20260913
  created_by: someone
  capability: anchor_cap
di_seam_exemptions:
- module_path: fake.Thing
  reason: test
- file: src/stray/dead_entry.py
  token: stray-token-20260913
  created_by: someone
  capability: stray_cap_zone
"""


@pytest.fixture()
def lab(tmp_path: Path, monkeypatch):
    """tmp 副本 registry + 假 git 扫描（不走真 git）。"""
    reg = tmp_path / "capability_canonical_file_registry.yaml"
    reg.write_text(_REG_BODY, encoding="utf-8")
    monkeypatch.setattr(bct, "_REGISTRY", reg)
    monkeypatch.setattr(bct, "_REPO", tmp_path)
    fake_files = [
        "docs/_working/lab/a/seg_001.md",
        "docs/_working/lab/a/seg_002.md",
        "docs/_working/lab/b/seg_003.md",
    ]
    monkeypatch.setattr(bct, "_git_output", lambda *a: fake_files if "ls-files" in a else [])
    return reg, fake_files


def test_batch_insert_and_yaml_valid(lab):
    reg, files = lab
    rc = bct.main() if False else None  # noqa: F633 — 直接调内部保证 argv 隔离
    block = bct.build_block(files, "sess-A", "lab_cap", "20260913")
    bct.insert_block(block, "anchor_cap")
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    toks = [e for e in data["creation_tokens"] if e["capability"] == "lab_cap"]
    assert len(toks) == 3
    assert all(e["created_by"] == "sess-A" for e in toks)
    assert toks[0]["file"] == "docs/_working/lab/a/seg_001.md"
    # token 内 capability 归一化（lab_cap→lab-cap，token 正则只允许小写字母数字连字符）
    assert toks[0]["token"] == "lab-cap-seg-001-20260913"
    # 纯插入：既有条目不动（含死区条目原样保留——本工具不治理历史死区）
    assert any(e["token"] == "anchor-token-20260913" for e in data["creation_tokens"])
    assert len(data["di_seam_exemptions"]) == 2


def test_idempotent_skip_registered(lab):
    reg, files = lab
    registered = bct.load_registered()
    assert bct.scan_unregistered("docs/_working/lab", registered) == files
    # 登记 a/seg_001 后重扫只剩 2
    block = bct.build_block(files[:1], "sess-A", "lab_cap", "20260913")
    bct.insert_block(block, "anchor_cap")
    registered2 = bct.load_registered()
    assert bct.scan_unregistered("docs/_working/lab", registered2) == files[1:]


def test_anchor_missing_fail_closed(lab, capsys):
    with pytest.raises(SystemExit) as ei:
        bct.insert_block("- file: x\n  token: y\n  created_by: z\n  capability: c\n", "no_such_anchor")
    assert ei.value.code == 1
    assert "fail-closed" in capsys.readouterr().err


def test_cli_dry_run_zero_write(lab, monkeypatch, capsys):
    monkeypatch.setattr(
        sys, "argv",
        ["bct", "--prefix", "docs/_working/lab", "--created-by", "sess-A", "--capability", "lab_cap", "--dry-run"],
    )
    rc = bct.main()
    assert rc == 0
    assert "DRY-RUN" in capsys.readouterr().out
    # registry 零变化
    assert "lab_cap" not in lab[0].read_text(encoding="utf-8")


def test_cli_real_run(lab, monkeypatch, capsys):
    monkeypatch.setattr(
        sys, "argv",
        ["bct", "--prefix", "docs/_working/lab", "--created-by", "sess-A", "--capability", "lab_cap"],
    )
    rc = bct.main()
    assert rc == 0
    data = yaml.safe_load(lab[0].read_text(encoding="utf-8"))
    assert len([e for e in data["creation_tokens"] if e["capability"] == "lab_cap"]) == 3
    assert "已插入 3 条" in capsys.readouterr().out
    # 回退锚点（lab_cap 段内不存在→回退段内最后一条 anchor_cap）后仍须落位正确段，
    # 不得落入尾部死区（2026-09-13 实弹教训：旧版全文件 findall 取到死区锚）
    dse = [e for e in data["di_seam_exemptions"] if e.get("capability") == "lab_cap"]
    assert dse == [], "回退锚点不得命中尾部死区"


def test_anchor_never_lands_in_trailing_dead_zone(lab):
    """实弹教训回归（2026-09-13 factory-bottleneck 批）：registry 尾部 di_seam_exemptions
    段混有 capability 行（历史错位死区）——锚点 MUST 限定 creation_tokens 段内，
    条目落进死区=YAML 合法但 CREATE-GUARD 读不到（登记静默丢失）。"""
    reg, files = lab
    block = bct.build_block(files, "sess-A", "lab_cap", "20260913")
    bct.insert_block(block, "anchor_cap")  # 段内锚
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    toks = [e for e in data["creation_tokens"] if e["capability"] == "lab_cap"]
    assert len(toks) == 3, "条目必须落位 creation_tokens 段"
    dse = [e for e in data["di_seam_exemptions"] if e.get("capability") == "lab_cap"]
    assert dse == [], "条目不得落入 di_seam_exemptions 死区"
    # 死区锚点显式拒写（fail-closed——stray_cap_zone 只存在于死区）
    with pytest.raises(SystemExit) as ei:
        bct.insert_block("- file: x\n  token: y\n  created_by: z\n  capability: c\n", "stray_cap_zone")
    assert ei.value.code == 1
