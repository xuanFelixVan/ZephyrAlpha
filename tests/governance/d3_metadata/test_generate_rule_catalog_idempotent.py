# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/generate_rule_catalog.py | §generate_catalog
# [MODULE] tests.governance.d3_metadata.test_generate_rule_catalog_idempotent
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; yaml; scripts.governance.d3_metadata.generate_rule_catalog (generate_catalog)
# [CONSUMERS] 生成器幂等性守卫（内容零变更必跳过写入=时间戳噪音治本的回归防线）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 全部用例构造于 tmp_path（不碰生产 rule_catalog_registry.yaml）
# [MODIFY-GUARD] 与 generate_catalog 幂等逻辑同批演进
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""generate_catalog 幂等性测试——2026-09-13 Owner 指令"内容没变就不刷时间戳"治本的守卫。

背景：生成器被 reconciler 周期触发（约 12min/次），原实现每次必刷 generated_at
=工作区永久漂移噪音（08:59→09:12 零内容变更实证）。幂等化后：内容零变更→跳过
写入；内容真变更→落盘+刷新时间戳。
"""

from __future__ import annotations

from pathlib import Path

import yaml

from scripts.governance.d3_metadata.generate_rule_catalog import generate_catalog

_ENTRIES = [
    {"path": "docs/01_policies_and_standards/rules/fake_rule.md", "module_id": "R-FAKE-001", "tier": "L0"},
    {"path": "docs/01_policies_and_standards/sop/fake_sop.md", "module_id": "R-FAKE-002", "tier": "L1"},
]


def test_first_run_writes(tmp_path: Path):
    out = tmp_path / "rule_catalog_registry.yaml"
    generate_catalog(_ENTRIES, str(out))
    assert out.exists()
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert data["total_files"] == 2
    assert data["tier_distribution"] == {"L0": 1, "L1": 1}


def test_unchanged_content_skips_rewrite(tmp_path: Path, capsys):
    """同 entries 二次生成 → 跳过写入（时间戳与文件内容逐字节不变）。"""
    out = tmp_path / "rule_catalog_registry.yaml"
    generate_catalog(_ENTRIES, str(out))
    capsys.readouterr()  # 清首次输出
    before = out.read_text(encoding="utf-8")
    mtime_before = out.stat().st_mtime_ns

    generate_catalog(_ENTRIES, str(out))

    assert out.read_text(encoding="utf-8") == before, "零变更重跑不得改文件内容"
    assert out.stat().st_mtime_ns == mtime_before, "零变更重跑不得触碰文件（skip 路径禁写）"
    assert "skip rewrite" in capsys.readouterr().err, "必须走幂等跳过分支并留痕 stderr"


def test_changed_content_rewrites_with_fresh_timestamp(tmp_path: Path, capsys):
    """entries 变化 → 正常落盘且时间戳刷新（freshness 信号保留）。"""
    out = tmp_path / "rule_catalog_registry.yaml"
    generate_catalog(_ENTRIES, str(out))
    old_ts = yaml.safe_load(out.read_text(encoding="utf-8"))["generated_at"]
    capsys.readouterr()

    bigger = _ENTRIES + [
        {"path": "docs/01_policies_and_standards/rules/new_rule.md", "module_id": "R-FAKE-003", "tier": "L2"},
    ]
    generate_catalog(bigger, str(out))

    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert data["total_files"] == 3, "新条目必须落盘"
    assert data["generated_at"] >= old_ts, "真内容变更必须刷新时间戳"
    assert "Generated catalog" in capsys.readouterr().err


def test_legacy_format_drift_self_heals(tmp_path: Path):
    """历史文件渲染格式漂移（非本生成器输出）→ 重写一次后恢复稳态。"""
    out = tmp_path / "rule_catalog_registry.yaml"
    out.write_text("generated_at: '2020-01-01T00:00:00Z'\nlegacy_junk: true\n", encoding="utf-8")
    generate_catalog(_ENTRIES, str(out))
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert "legacy_junk" not in data, "格式漂移文件必须被规范重写"
    assert data["generated_at"] != "2020-01-01T00:00:00Z"
    # 第二次进入稳态：跳过
    before = out.read_text(encoding="utf-8")
    generate_catalog(_ENTRIES, str(out))
    assert out.read_text(encoding="utf-8") == before
