# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/generate_rule_catalog.py | §generate_catalog
# [MODULE] tests.governance.d3_metadata.test_generate_rule_catalog_idempotent
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; yaml; scripts.governance.d3_metadata.generate_rule_catalog (generate_catalog)
# [CONSUMERS] 生成器幂等性守卫（内容零变更必跳过写入=时间戳噪音治本的回归防线）；保育语义守卫（非生成器输入产出条目透传保留=#11.4-W2 剪除事故回归防线）
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


def test_unmanaged_entry_survives_regeneration(tmp_path: Path):
    """保育语义（#11.4-W2）：既有输出中非生成器输入产出的条目，再生成后原样保留。

    事故背景（2026-09-16 02:58:54 write_audit 取证）：工具经 YAML 侧合法通道
    （add_module_translation / batch_creation_tokens）登记的条目不在生成器扫描
    输入里，原实现整体替换 files 列表将其剪除、reconciler 自动提交固化。
    """
    out = tmp_path / "rule_catalog_registry.yaml"
    generate_catalog(_ENTRIES, str(out))

    # 注入"孤儿条目"：模拟工具合法登记——生成器输入不含此 path，且带额外字段
    orphan = {
        "path": "docs/01_policies_and_standards/_registry/module_translation_registry.yaml",
        "module_id": "MOD-XLATE-FAKE",
        "title": "工具登记条目（生成器输入不含）",
        "extra_tool_field": {"source": "add_module_translation"},
    }
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    data["files"].append(orphan)
    out.write_text(
        yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )

    generate_catalog(_ENTRIES, str(out))  # 同输入再生成——孤儿不得被剪

    after = yaml.safe_load(out.read_text(encoding="utf-8"))
    kept = next(f for f in after["files"] if f["path"] == orphan["path"])
    assert kept == orphan, "保育=原样透传（字段不改写）"
    assert after["total_files"] == len(after["files"]) == 3, "计数必须描述落盘列表"
    assert after["total_rules"] == 2, "孤儿无 tier 不计入 total_rules"

    # 稳态回归：保育合并确定性 → 第三次同输入再生成走幂等跳过
    before = out.read_text(encoding="utf-8")
    mtime_before = out.stat().st_mtime_ns
    generate_catalog(_ENTRIES, str(out))
    assert out.read_text(encoding="utf-8") == before, "保育合并不得破坏幂等跳过"


def test_managed_entry_update_wins_over_stale_copy(tmp_path: Path):
    """回归：生成器管辖条目正常更新——同 path 以本次输入为准（保育不阻更新）。"""
    out = tmp_path / "rule_catalog_registry.yaml"
    generate_catalog(_ENTRIES, str(out))

    # 把管辖 path 换成陈旧副本 + 追加一个孤儿：再生成后前者被刷新、后者保育
    stale = dict(_ENTRIES[0], title="过期标题", version="0.0.1")
    orphan = {"path": "docs/01_policies_and_standards/rules/orphan.md", "module_id": "R-ORPHAN-1"}
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    data["files"][0] = stale
    data["files"].append(orphan)
    out.write_text(
        yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )

    generate_catalog(
        _ENTRIES + [{"path": "docs/01_policies_and_standards/rules/new_rule.md", "module_id": "R-FAKE-003", "tier": "L2"}],
        str(out),
    )

    after = yaml.safe_load(out.read_text(encoding="utf-8"))
    managed = next(f for f in after["files"] if f["path"] == _ENTRIES[0]["path"])
    assert managed == _ENTRIES[0], "管辖条目必须整体以本次输入为准（含新增条目落盘）"
    assert sum(1 for f in after["files"] if f["path"] == "docs/01_policies_and_standards/rules/new_rule.md") == 1
    kept = next(f for f in after["files"] if f["path"] == orphan["path"])
    assert kept == orphan, "孤儿条目在管辖条目更新时仍保育"
