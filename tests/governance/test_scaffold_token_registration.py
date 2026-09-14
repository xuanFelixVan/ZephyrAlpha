# [BLUEPRINT] MOD-INF-005 | scripts/scaffold.py | §_register_creation_token 硬化通道
# [MODULE] tests.governance.test_scaffold_token_registration
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; yaml; scripts.scaffold; scripts.governance.d3_metadata.batch_creation_tokens
# [CONSUMERS] scaffold creation_token 自动登记质量守卫（段内锚定/CAS/写后自检回滚/幂等）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 全部用例构造于 tmp 副本 registry（monkeypatch 双侧 _REGISTRY 常量，不碰生产）
# [MODIFY-GUARD] 与 scaffold._register_creation_token / batch_creation_tokens 硬化通道同批演进
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""scaffold._register_creation_token 硬化通道测试（2026-09-15 治理上报件1）。

病根回归：旧实现整文件 yaml.safe_load→yaml.dump 全文重写——读改写窗口被他会话
并发写交割（capability registry 12250/12112 行两次悬挂块炸全仓 parse 同族）。
硬化后与 batch_creation_tokens 共用段内锚定+safe_write_text CAS+写后双自检回滚。
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

import scripts.governance.d3_metadata.batch_creation_tokens as bct
import scripts.scaffold as scaffold

_REG_BODY = """schema_version: 1.1.0
title: 测试副本
creation_tokens:
- file: docs/existing/anchor.md
  token: anchor-token-20260915
  created_by: someone
  capability: anchor_cap
di_seam_exemptions: []
"""


@pytest.fixture()
def lab(tmp_path: Path, monkeypatch):
    """tmp 副本 registry；scaffold 与 batch tool 两侧常量同指一份（生产行为=同文件）。"""
    reg = tmp_path / "capability_canonical_file_registry.yaml"
    reg.write_text(_REG_BODY, encoding="utf-8")
    monkeypatch.setattr(scaffold, "CAPABILITY_REGISTRY", reg)
    monkeypatch.setattr(bct, "_REGISTRY", reg)
    new_module = tmp_path / "new_module.py"
    new_module.write_text('"""stub"""\n', encoding="utf-8")
    return reg, new_module


def test_register_token_lands_in_creation_tokens_section(lab):
    reg, new_module = lab
    scaffold._register_creation_token(str(new_module), "my_new_cap", dry_run=False)
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    toks = [e for e in data["creation_tokens"] if e["capability"] == "my_new_cap"]
    assert len(toks) == 1
    assert toks[0]["created_by"] == "scaffold.py"
    assert toks[0]["file"].endswith("new_module.py")
    assert toks[0]["token"].startswith("auto-scaffold-my_new_cap-")  # scaffold 惯例：capability 原文进 token
    # 段内锚定：不得落入尾部 di_seam_exemptions 死区（EOF 盲插病根回归）
    assert data["di_seam_exemptions"] == []


def test_register_token_idempotent(lab):
    reg, new_module = lab
    scaffold._register_creation_token(str(new_module), "my_new_cap", dry_run=False)
    scaffold._register_creation_token(str(new_module), "my_new_cap", dry_run=False)
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    assert len([e for e in data["creation_tokens"] if e["file"].endswith("new_module.py")]) == 1


def test_register_token_dry_run_zero_write(lab):
    reg, new_module = lab
    pre = reg.read_bytes()
    scaffold._register_creation_token(str(new_module), "my_new_cap", dry_run=True)
    assert reg.read_bytes() == pre


def test_register_token_missing_section_warns_and_skips(lab, capsys):
    """registry 无 creation_tokens 段 → 警告降级（best-effort 语义），绝不异常外泄。"""
    reg, new_module = lab
    reg.write_text("di_seam_exemptions: []\n", encoding="utf-8")
    scaffold._register_creation_token(str(new_module), "my_new_cap", dry_run=False)
    captured = capsys.readouterr()  # 一次性取全（二次调用返回空缓冲）
    output = captured.out + captured.err
    assert "WARNING" in output
    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    assert data["di_seam_exemptions"] == []  # 无段可插 → 零写入


def test_register_token_broken_registry_warns_and_skips(lab, capsys):
    """registry 本身 parse 炸（历史事故态）→ 警告降级，不雪上加霜。"""
    reg, new_module = lab
    reg.write_text("creation_tokens:\n  - [broken\n", encoding="utf-8")
    scaffold._register_creation_token(str(new_module), "my_new_cap", dry_run=False)
    out = capsys.readouterr().out
    assert "解析失败" in out
