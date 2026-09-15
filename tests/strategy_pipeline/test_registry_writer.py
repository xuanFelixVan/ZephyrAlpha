# [BLUEPRINT] MOD-BT-192 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.strategy_pipeline.test_registry_writer
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.registry_writer
# [CONSUMERS] MOD-BT-192 循环验收
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 测试隔离零生产 IO（registry 落 tmp_path）；only-add 断言红蓝必测
# [MODIFY-GUARD] src/zephyr/strategy_pipeline/registry_writer.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-192 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""registry_writer 测试——渲染确定性/EOF 追加 only-add/CAS 冲突红蓝/写后复核（交接清单③验收）。"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.strategy_pipeline import registry_writer as rw  # noqa: E402

_REAL_REGISTRY = Path(rw.REGISTRY)


@pytest.fixture()
def registry_copy(tmp_path):
    """真注册表副本（隔离写；模板字段漂移即红）。"""
    dst = tmp_path / "strategy_registry.yaml"
    shutil.copy(_REAL_REGISTRY, dst)
    return dst


def _entry(sid="STR-AUTO-001", **kw):
    base = {
        "strategy_id": sid, "name": "测试条目", "name_zh": "测试条目",
        "strategy_class": "value_reversal", "holding_period": "波段",
        "entry_logic": "入场逻辑 '带引号' 测试", "exit_logic": "出场",
        "doc_ref": "docs/_working/x.md", "code_path": "scripts/backtest/translated/c4_x.py",
        "lifecycle_status": "candidate", "created_at": "2026-09-15", "updated_at": "2026-09-15",
        "last_evaluated_at": "2026-09-15", "baseline_sharpe": 0.5, "baseline_max_drawdown": -0.2,
        "evidence": "双窗及格；auto_intake B1。",
        "code_symbol": "scripts/backtest/translated/c4_x.py::build",
    }
    base.update(kw)
    return base


class TestRender:
    def test_render_full_block_parse(self):
        text = rw.render_entry(_entry())
        # 条目块（含 `  - ` 标记）直接挂在 strategies 键下可解析
        doc = yaml.safe_load("strategies:\n" + text)
        e = doc["strategies"][0]
        assert e["strategy_id"] == "STR-AUTO-001"
        assert e["sleeve"] == "alpha" and e["direction"] == "long"
        assert e["data_quality_policy"]["null_rate"]["threshold"] == 0.02
        assert "'" not in e["entry_logic"] and '"' not in e["entry_logic"]  # 防注入
        assert e["family_redundancy"] is None

    def test_family_redundancy_block(self):
        text = rw.render_entry(_entry(family_redundancy={
            "role": "cluster_head",
            "absorbed": [{"candidate_id": "CAND-abc", "name": "bluechip_ma", "correlation": 0.713}],
            "ruling_ref": "docs/_working/r.md"}))
        doc = yaml.safe_load("strategies:\n" + text)
        blk = doc["strategies"][0]["family_redundancy"]
        assert blk["absorbed"][0]["correlation"] == 0.713


class TestAppend:
    def test_append_only_add_and_verify(self, registry_copy):
        before_ids = [e["strategy_id"] for e in yaml.safe_load(
            registry_copy.read_text(encoding="utf-8"))["strategies"]]
        r = rw.append_entries([_entry("STR-VREV-099")], registry_copy)
        assert r["new_sids"] == ["STR-VREV-099"] and r["total_after"] == len(before_ids) + 1
        back = yaml.safe_load(registry_copy.read_text(encoding="utf-8"))["strategies"]
        assert [e["strategy_id"] for e in back][: len(before_ids)] == before_ids  # 既有零触碰

    def test_dry_run_zero_write(self, registry_copy):
        before = registry_copy.read_bytes()
        r = rw.append_entries([_entry()], registry_copy, dry_run=True)
        assert r["dry_run"] and registry_copy.read_bytes() == before

    def test_post_verify_fails_on_tamper(self, registry_copy, monkeypatch):
        # 红蓝：写后复核——篡改既有条目必须被抓（only-add 语义的机器断言）
        real_sw = rw.safe_write_text

        def tampering_write(path, text, **kw):
            text = text.replace('strategy_id: "STR-VREV-025"', 'strategy_id: "STR-VREV-XXX"')
            return real_sw(path, text, **kw)

        monkeypatch.setattr(rw, "safe_write_text", tampering_write)
        with pytest.raises((AssertionError, RuntimeError)):
            rw.append_entries([_entry()], registry_copy)

    def test_cas_conflict_raises(self, registry_copy, monkeypatch):
        # 红蓝：CAS 竞争（他会话先写）→ fail-closed 异常，事件留调用方重试
        def conflict_write(path, text, **kw):
            class R:
                written = False
            return R()

        monkeypatch.setattr(rw, "safe_write_text", conflict_write)
        with pytest.raises(RuntimeError, match="CAS"):
            rw.append_entries([_entry()], registry_copy)
