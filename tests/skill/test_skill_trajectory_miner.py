# [A_test] module_id: MOD-INF-019 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.skill.test_skill_trajectory_miner
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/skill/test_skill_trajectory_miner.py
# [TTL] task_bound

"""skill_trajectory_miner（MOD-INF-059 候选 / 11号文 §4.4 P2-1）测试。

覆盖：空输入优雅降级 / supported 假设加载 / 聚类归纳 / SKILL.md 三级格式 /
退役指纹库查重拒绝（相似度>90%）/ 契约违反 ZA-AC-0008。
"""

from __future__ import annotations

import json

import pytest

from zephyr.autonomy_core.skills.skill_trajectory_miner import (
    SkillTrajectoryMiner,
    SkillTrajectoryMinerError,
    TrajectoryRecord,
    validate_skill_md,
)


def _rec(record_id: str, statement: str, *, tags=(), steps=(), status="supported", regime=""):
    return TrajectoryRecord(
        record_id=record_id,
        statement=statement,
        status=status,
        tags=tuple(tags),
        steps=tuple(steps),
        regime=regime,
        source="hypothesis",
    )


# 两条语义高度重合的动量类记录（应聚为一簇）
MOMENTUM_A = _rec(
    "HYP-0001",
    "动量因子在趋势 regime 下截面选股有效，IC 显著为正",
    tags=("factor", "momentum"),
    steps=("计算20日动量因子", "按因子值分组回测", "检验IC与分组收益"),
    regime="trending",
)
MOMENTUM_B = _rec(
    "HYP-0002",
    "动量因子在趋势 regime 下截面选股有效，IC 显著为正且单调",
    tags=("factor", "momentum"),
    steps=("计算20日动量因子", "按因子值分组回测", "检验IC单调性"),
    regime="trending",
)
# 与动量完全不同的主题（应独立成簇）
VOL_A = _rec(
    "HYP-0003",
    "波动率择时在震荡市降低回撤，仓位随已实现波动率反向调整",
    tags=("volatility", "timing"),
    steps=("估计已实现波动率", "波动率分位数映射仓位", "回测最大回撤"),
    regime="ranging",
)


class TestEmptyInputDegradation:
    def test_mine_empty_input_graceful(self, tmp_path):
        miner = SkillTrajectoryMiner(output_dir=tmp_path / "drafts")
        result = miner.mine([])
        assert result["status"] == "empty_input"
        assert result["drafts"] == []
        assert result["rejected"] == []
        assert not (tmp_path / "drafts").exists() or list((tmp_path / "drafts").iterdir()) == []

    def test_load_supported_hypotheses_missing_store(self, tmp_path):
        miner = SkillTrajectoryMiner(output_dir=tmp_path / "drafts")
        assert miner.load_supported_hypotheses(store_dir=tmp_path / "nonexistent") == []

    def test_load_supported_hypotheses_filters_supported_only(self, tmp_path):
        store = tmp_path / "evidence"
        store.mkdir()
        payload = {
            "schema_version": "1.0.0",
            "hypotheses": [
                {
                    "hypothesis_id": "HYP-0001",
                    "statement": "动量因子在趋势 regime 下有效",
                    "status": "supported",
                    "proposed_at": "2026-08-01T10:00:00+08:00",
                    "updated_at": "2026-08-02T10:00:00+08:00",
                    "tags": ["factor", "momentum"],
                    "notes": "验证过程：分组回测+IC检验",
                    "status_history": [],
                },
                {
                    "hypothesis_id": "HYP-0002",
                    "statement": "反转因子在震荡市有效",
                    "status": "proposed",
                    "proposed_at": "2026-08-03T10:00:00+08:00",
                    "updated_at": "2026-08-03T10:00:00+08:00",
                    "tags": ["factor", "reversal"],
                    "notes": "",
                    "status_history": [],
                },
            ],
        }
        (store / "hypotheses.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        miner = SkillTrajectoryMiner(output_dir=tmp_path / "drafts")
        records = miner.load_supported_hypotheses(store_dir=store)
        assert [r.record_id for r in records] == ["HYP-0001"]
        assert records[0].source == "hypothesis"


class TestMining:
    def test_mine_generates_draft_with_three_level_format(self, tmp_path):
        out = tmp_path / "drafts"
        miner = SkillTrajectoryMiner(output_dir=out)
        result = miner.mine([MOMENTUM_A, MOMENTUM_B])
        assert result["status"] == "mined"
        assert len(result["drafts"]) == 1
        skill_md = out / result["drafts"][0]["path"]
        content = skill_md.read_text(encoding="utf-8")
        assert "## Discovery" in content
        assert "## Activation" in content
        assert "## Execution" in content
        assert "unverified_draft" in content
        # 来源可追溯（P2-4 入库要求前置：草稿即带假设 ID）
        assert "HYP-0001" in content and "HYP-0002" in content

    def test_mine_clusters_distinct_topics_separately(self, tmp_path):
        miner = SkillTrajectoryMiner(output_dir=tmp_path / "drafts")
        result = miner.mine([MOMENTUM_A, MOMENTUM_B, VOL_A])
        assert len(result["drafts"]) == 2

    def test_draft_marked_unverified_and_outside_production(self, tmp_path):
        out = tmp_path / "drafts"
        miner = SkillTrajectoryMiner(output_dir=out)
        result = miner.mine([MOMENTUM_A, MOMENTUM_B])
        draft = result["drafts"][0]
        assert draft["status"] == "unverified_draft"
        # 人工门禁卫：草稿只落 output_dir（.runtime/skill_drafts 语义），不进生产 skills 目录
        assert "skills" not in draft["path"].replace("skill_drafts", "")
        content = (out / draft["path"]).read_text(encoding="utf-8")
        assert "未验证" in content

    def test_manifest_records_drafts_and_rejections(self, tmp_path):
        out = tmp_path / "drafts"
        miner = SkillTrajectoryMiner(output_dir=out)
        miner.mine([MOMENTUM_A, MOMENTUM_B, VOL_A])
        manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
        assert len(manifest["drafts"]) == 2
        assert manifest["schema_version"] == "1.0.0"
        for d in manifest["drafts"]:
            assert d["status"] == "unverified_draft"
            assert d["fingerprint"]


class TestRetiredFingerprintGate:
    def test_similar_reregistration_rejected(self, tmp_path):
        fp_path = tmp_path / "retired_fingerprints.json"
        miner = SkillTrajectoryMiner(output_dir=tmp_path / "drafts1", fingerprint_store_path=fp_path)
        first = miner.mine([MOMENTUM_A, MOMENTUM_B])
        assert len(first["drafts"]) == 1
        # 退役该草稿（指纹入库归档）
        miner.retire_draft(first["drafts"][0]["draft_id"], reason="连续30天未调用")

        miner2 = SkillTrajectoryMiner(output_dir=tmp_path / "drafts2", fingerprint_store_path=fp_path)
        second = miner2.mine([MOMENTUM_A, MOMENTUM_B])
        assert second["drafts"] == []
        assert len(second["rejected"]) == 1
        rej = second["rejected"][0]
        assert rej["similarity"] > 0.90
        assert "退役指纹" in rej["reason"]

    def test_dissimilar_fingerprint_allows_draft(self, tmp_path):
        fp_path = tmp_path / "retired_fingerprints.json"
        miner = SkillTrajectoryMiner(output_dir=tmp_path / "drafts1", fingerprint_store_path=fp_path)
        first = miner.mine([MOMENTUM_A, MOMENTUM_B])
        miner.retire_draft(first["drafts"][0]["draft_id"], reason="性能衰退")

        miner2 = SkillTrajectoryMiner(output_dir=tmp_path / "drafts2", fingerprint_store_path=fp_path)
        second = miner2.mine([VOL_A])
        assert len(second["drafts"]) == 1
        assert second["rejected"] == []

    def test_fingerprint_store_corruption_fail_fast(self, tmp_path):
        fp_path = tmp_path / "retired_fingerprints.json"
        fp_path.write_text("{ not valid json", encoding="utf-8")
        with pytest.raises(SkillTrajectoryMinerError) as exc_info:
            SkillTrajectoryMiner(output_dir=tmp_path / "drafts", fingerprint_store_path=fp_path)
        assert exc_info.value.error_code == "ZA-AC-0008"


class TestFormatValidation:
    def test_validate_generated_draft_passes(self, tmp_path):
        out = tmp_path / "drafts"
        miner = SkillTrajectoryMiner(output_dir=out)
        result = miner.mine([MOMENTUM_A, MOMENTUM_B, VOL_A])
        for d in result["drafts"]:
            report = validate_skill_md((out / d["path"]).read_text(encoding="utf-8"))
            assert report["valid"], report["issues"]

    def test_validate_missing_section_rejected(self):
        bad = "---\nname: x\nstatus: unverified_draft\n---\n# x\n## Discovery\nfoo\n"
        report = validate_skill_md(bad)
        assert not report["valid"]
        assert any("Activation" in i for i in report["issues"])

    def test_validate_discovery_over_budget_rejected(self):
        discovery_body = "触发词 " * 300
        content = (
            "---\nname: x\nstatus: unverified_draft\n---\n# x\n"
            f"## Discovery\n{discovery_body}\n## Activation\n步骤\n## Execution\n引用\n"
        )
        report = validate_skill_md(content)
        assert not report["valid"]
        assert any("Discovery" in i for i in report["issues"])


class TestContract:
    def test_empty_statement_record_rejected(self, tmp_path):
        miner = SkillTrajectoryMiner(output_dir=tmp_path / "drafts")
        with pytest.raises(SkillTrajectoryMinerError) as exc_info:
            miner.mine([_rec("HYP-0099", "   ")])
        assert exc_info.value.error_code == "ZA-AC-0008"

    def test_unsupported_status_record_skipped(self, tmp_path):
        miner = SkillTrajectoryMiner(output_dir=tmp_path / "drafts")
        result = miner.mine([_rec("HYP-0100", "未验证假设不入矿", status="proposed")])
        assert result["status"] == "empty_input"
        assert result["drafts"] == []
