# [A_test] module_id: zephyr.ai_layer.redline.no_delete_manifest | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_no_delete_manifest
# [MODULE] tests.ai_layer.redline.test_no_delete_manifest
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; zephyr.ai_layer.redline.no_delete_manifest
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/ai_layer/redline/test_no_delete_manifest.py
# [MATURITY] testing
# [INVARIANTS] 验收标准（DESIGN 红蓝 R1-F4）：产出与 DDL 真源/ROOR 逐条一致（幂等再生）；
#              真源输入用 tmp 合成（DDL 目录+ROOR 文件），零生产路径写
# [MODIFY-GUARD] —
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_no_delete_manifest.py — S4 禁删清单生成器×2 单测（AST 枚举/ROOR tier 0-2/幂等再生）。"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from zephyr.ai_layer.redline.no_delete_manifest import (
    ManifestInputError,
    generate_all,
    generate_registries_manifest,
    generate_tables_manifest,
    iter_ddl_table_names,
    main,
)

DDL_A = (
    '# [MODULE] schemas.categories.sim_like\n'
    '"""sim_like 表 DDL。"""\n'
    'TABLE_NAME = "c1_backtest.sim_like"\n'
    'DDL = """CREATE TABLE IF NOT EXISTS c1_backtest.sim_like (x UInt8)"""\n'
)
DDL_B = 'TABLE_NAME = "c1_backtest.sim_trade_log"\n'
DDL_C = 'TABLE_NAME = "c1_backtest.sim_pocket_daily"\n'
DDL_BAD = "TABLE_NAME = (broken syntax\n"


def _make_ddl_root(tmp_path: Path) -> Path:
    ddl_root = tmp_path / "categories"
    ddl_root.mkdir(exist_ok=True)
    (ddl_root / "sim_like.py").write_text(DDL_A, encoding="utf-8")
    (ddl_root / "sim_trade_log.py").write_text(DDL_B, encoding="utf-8")
    (ddl_root / "sim_pocket_daily.py").write_text(DDL_C, encoding="utf-8")
    (ddl_root / "__init__.py").write_text("", encoding="utf-8")
    return ddl_root


def _make_roor(tmp_path: Path) -> Path:
    roor = tmp_path / "registry_of_registries.yaml"
    roor.write_text(
        yaml.safe_dump(
            {
                "tiers": [
                    {
                        "tier": 0,
                        "registries": [
                            {
                                "registry_id": "REG-GATE-001",
                                "physical_path": "src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml",
                            },
                            {
                                "registry_id": "REG-PG-001",
                                "physical_path": "postgresql://localhost:5432/depgraph",
                            },
                        ],
                    },
                    {
                        "tier": 3,
                        "registries": [
                            {"registry_id": "REG-T3", "physical_path": "should_not_appear.yaml"}
                        ],
                    },
                ]
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return roor


def test_iter_ddl_table_names_ast_enum_and_bad_file_skip(tmp_path: Path):
    ddl_root = tmp_path / "categories"
    ddl_root.mkdir()
    (ddl_root / "sim_like.py").write_text(DDL_A, encoding="utf-8")
    (ddl_root / "sim_trade_log.py").write_text(DDL_B, encoding="utf-8")
    (ddl_root / "broken.py").write_text(DDL_BAD, encoding="utf-8")
    (ddl_root / "__init__.py").write_text('TABLE_NAME = "c1_backtest.ignored"\n', encoding="utf-8")
    entries, bad = iter_ddl_table_names(ddl_root)
    names = [entry["name"] for entry in entries]
    assert names == ["c1_backtest.sim_like", "c1_backtest.sim_trade_log"]
    assert bad == ["broken.py"], "坏文件跳过计数留痕（fail-open 读）"
    assert "__init__.py" not in {entry["source"].split("/")[-1] for entry in entries}


def test_tables_manifest_required_coverage_ok(tmp_path: Path):
    manifest = generate_tables_manifest(_make_ddl_root(tmp_path))
    assert manifest["coverage"]["missing"] == []
    names = {entry["name"] for entry in manifest["entries"]}
    assert {"c1_backtest.sim_trade_log", "c1_backtest.sim_pocket_daily"} <= names
    assert manifest["total_entries"] == len(manifest["entries"]) == 3


def test_tables_manifest_missing_coverage_reported_honestly(tmp_path: Path):
    ddl_root = tmp_path / "only_one"
    ddl_root.mkdir()
    (ddl_root / "sim_like.py").write_text(DDL_A, encoding="utf-8")
    manifest = generate_tables_manifest(ddl_root)
    assert "c1_backtest.sim_pocket_daily" in manifest["coverage"]["missing"]
    assert "c1_backtest.sim_trade_log" in manifest["coverage"]["missing"]


def test_tables_manifest_missing_ddl_root_fail_closed(tmp_path: Path):
    with pytest.raises(ManifestInputError):
        generate_tables_manifest(tmp_path / "nope")


def test_roor_tier0_2_collected_tier3_excluded(tmp_path: Path):
    manifest = generate_registries_manifest(_make_roor(tmp_path))
    names = {entry["name"] for entry in manifest["entries"]}
    assert "src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml" in names
    assert "postgresql://localhost:5432/depgraph" in names
    assert "should_not_appear.yaml" not in names, "tier>2 不在禁删清单（DESIGN §2 档 A 原文 tier 0-2）"
    kinds = {entry["kind"] for entry in manifest["entries"]}
    assert "roor_self" in kinds and "db_dsn" in kinds


def test_roor_must_cover_files_present(tmp_path: Path):
    """必须覆盖点名件：gate_registry/risk_tier/secret/immutable/audit_key_eras/ruling/ROOR 本体。"""
    manifest = generate_registries_manifest(_make_roor(tmp_path))
    assert manifest["coverage"]["missing"] == []
    by_name = {Path(entry["name"]).name for entry in manifest["entries"]}
    assert {
        "registry_of_registries.yaml",
        "gate_registry.yaml",
        "risk_tier_registry.yaml",
        "secret_registry.yaml",
        "immutable_core.yaml",
        "audit_key_eras.yaml",
        "ruling_registry.yaml",
    } <= by_name


def test_roor_missing_fail_closed(tmp_path: Path):
    with pytest.raises(ManifestInputError):
        generate_registries_manifest(tmp_path / "nope.yaml")


def test_idempotent_regeneration_entries_identical(tmp_path: Path):
    """幂等再生：同输入两次生成（不含 generated_at）逐条一致。"""
    out = tmp_path / "gen"
    summary1 = generate_all(_make_ddl_root(tmp_path), _make_roor(tmp_path), out)
    first_tables = yaml.safe_load((out / "no_delete_tables.yaml").read_text(encoding="utf-8"))
    first_registries = yaml.safe_load((out / "no_delete_registries.yaml").read_text(encoding="utf-8"))
    summary2 = generate_all(_make_ddl_root(tmp_path), _make_roor(tmp_path), out)
    second_tables = yaml.safe_load((out / "no_delete_tables.yaml").read_text(encoding="utf-8"))
    second_registries = yaml.safe_load((out / "no_delete_registries.yaml").read_text(encoding="utf-8"))
    assert summary1["tables_total"] == summary2["tables_total"]
    for fresh, cached in ((second_tables, first_tables), (second_registries, first_registries)):
        fresh.pop("generated_at")
        cached.pop("generated_at")
        assert fresh == cached, "除 generated_at 外逐字段一致（幂等再生）"


def test_cli_generate_to_tmp(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    rc = main(
        [
            "--ddl-root", str(_make_ddl_root(tmp_path)),
            "--roor", str(_make_roor(tmp_path)),
            "--out", str(tmp_path / "out"),
        ]
    )
    assert rc == 0
    assert "tables_manifest" in capsys.readouterr().out
