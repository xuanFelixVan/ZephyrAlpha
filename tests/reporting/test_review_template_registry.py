# [BLUEPRINT] MOD-RPT-032 | 待统筹登记（55 号 §6 模板引擎外化行） | §test
# [MODULE] tests.reporting.test_review_template_registry
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.reporting.review_template_registry; zephyr.reporting.ai_review_summary
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme;tmp_path 夹具零真实配置改写
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] test_review_template_registry.py
# [A_test] module_id: MOD-RPT-032 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""MOD-RPT-032 单元测试: 复盘模板注册表（55 号 §6 模板引擎固化外化）。

覆盖：
- 打包默认注册表：三类模板齐、default_version=v1、占位符完整；
- 版本可切换：v1/v2 并存按版本取、默认版本回退（缺失版本→default+notes）；
- schema fail-closed：缺 default_version/templates 非映射/版本空/body 空/
  默认版本缺席/必需占位符缺失/未声明占位符；
- 文件加载：REVIEW_TEMPLATES_PATH 在档可载、在档文件 v1 == 打包默认 v1
  （双向一致性锁）、文件缺失→打包默认回退、畸形 YAML→fail-closed；
- GAP-F-40 集成：ai_review_summary 经注册位渲染战报/prompt/兜底结语
  （v2 自定义模板生效、不传注册表行为与迁移前一致）；
- 契约：frozen、to_dict JSON 可序列化。
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from zephyr.reporting.ai_review_summary import (
    ReviewContext,
    generate_review_summary,
    render_war_report,
)
from zephyr.reporting.review_template_registry import (
    REVIEW_TEMPLATES_PATH,
    ReviewTemplateRegistry,
    ReviewTemplateRegistryError,
    TemplateSpec,
    TEMPLATE_FALLBACK_SUMMARY,
    TEMPLATE_PROMPT_SUMMARY,
    TEMPLATE_WAR_REPORT,
)


def _ctx() -> ReviewContext:
    return ReviewContext(
        trade_date="2026-08-21",
        market_overview="上证涨 0.8%，两市成交 1.1 万亿放量",
        sector_highlights=("机器人主线再强化",),
        plan_outcomes=("预案命中高开高走格",),
        risk_events=("D3 撤单比 0.42 未越线",),
    )


def _v2_registry() -> ReviewTemplateRegistry:
    return ReviewTemplateRegistry.from_dict(
        {
            "default_version": "v1",
            "templates": {
                TEMPLATE_WAR_REPORT: {
                    "versions": {
                        "v1": {
                            "body": "# 每日战报 {trade_date}\n\n## 1. 市场回顾\n{market_overview}\n\n## 2. 板块亮点\n{sector_highlights}\n\n## 3. 预案执行\n{plan_outcomes}\n\n## 4. 风险事件\n{risk_events}\n\n## 5. AI 结语\n{summary}\n"
                        },
                        "v2": {
                            "body": "# 战报V2 {trade_date}\n市场：{market_overview}\n板块：{sector_highlights}\n预案：{plan_outcomes}\n风险：{risk_events}\n结语：{summary}",
                            "status": "active",
                        },
                    }
                },
                TEMPLATE_PROMPT_SUMMARY: {
                    "versions": {
                        "v1": {
                            "body": "P1 {trade_date} {market_overview} {sector_highlights} {plan_outcomes} {risk_events} {max_chars}"
                        },
                        "v2": {
                            "body": "P2-自定义 {trade_date} {market_overview} {sector_highlights} {plan_outcomes} {risk_events} {max_chars}"
                        },
                    }
                },
                TEMPLATE_FALLBACK_SUMMARY: {
                    "versions": {
                        "v1": {
                            "body": "F1 {trade_date} {market_overview} {sector_highlights} {plan_outcomes} {risk_events}"
                        },
                        "v2": {
                            "body": "F2-兜底 {trade_date} {market_overview} {sector_highlights} {plan_outcomes} {risk_events}"
                        },
                    }
                },
            },
        }
    )


# ----------------------------------------------------------------------
# 打包默认注册表
# ----------------------------------------------------------------------


class TestEmbeddedDefault:
    def test_three_kinds_present(self) -> None:
        reg = ReviewTemplateRegistry.embedded_default()
        assert reg.kinds() == [TEMPLATE_FALLBACK_SUMMARY, TEMPLATE_PROMPT_SUMMARY, TEMPLATE_WAR_REPORT]
        assert reg.default_version == "v1"
        assert reg.source == "embedded_default"

    def test_war_body_has_six_sections(self) -> None:
        reg = ReviewTemplateRegistry.embedded_default()
        body = reg.get(TEMPLATE_WAR_REPORT).body
        for marker in (
            "{trade_date}",
            "{market_overview}",
            "{sector_highlights}",
            "{plan_outcomes}",
            "{risk_events}",
            "{summary}",
        ):
            assert marker in body

    def test_get_default_equals_v1(self) -> None:
        reg = ReviewTemplateRegistry.embedded_default()
        assert reg.get(TEMPLATE_WAR_REPORT).body == reg.get(TEMPLATE_WAR_REPORT, "v1").body


# ----------------------------------------------------------------------
# 版本可切换 + 默认模板回退
# ----------------------------------------------------------------------


class TestVersionSwitch:
    def test_explicit_v2_served(self) -> None:
        reg = _v2_registry()
        spec = reg.get(TEMPLATE_WAR_REPORT, "v2")
        assert spec.version == "v2"
        assert spec.body.startswith("# 战报V2")
        assert spec.status == "active"

    def test_default_version_when_none(self) -> None:
        reg = _v2_registry()
        assert reg.get(TEMPLATE_WAR_REPORT).version == "v1"

    def test_missing_version_falls_back_with_note(self) -> None:
        reg = _v2_registry()
        spec = reg.get(TEMPLATE_WAR_REPORT, "v9")
        assert spec.version == "v1"
        assert any("v9" in n and "回退" in n for n in spec.notes)

    def test_unknown_kind_raises(self) -> None:
        reg = _v2_registry()
        with pytest.raises(ReviewTemplateRegistryError):
            reg.get("war_report_v3_evolution")

    def test_versions_listing(self) -> None:
        reg = _v2_registry()
        assert reg.versions(TEMPLATE_WAR_REPORT) == ["v1", "v2"]


# ----------------------------------------------------------------------
# schema fail-closed
# ----------------------------------------------------------------------


class TestSchemaValidation:
    @pytest.mark.parametrize(
        "raw",
        [
            {},
            {"default_version": "", "templates": {"k": {"versions": {"v1": {"body": "x"}}}}},
            {"default_version": "v1"},
            {"default_version": "v1", "templates": "not-a-mapping"},
            {"default_version": "v1", "templates": {"k": {}}},
            {"default_version": "v1", "templates": {"k": {"versions": {}}}},
            {"default_version": "v1", "templates": {"k": {"versions": {"v1": {}}}}},
            {"default_version": "v1", "templates": {"k": {"versions": {"v1": {"body": "  "}}}}},
            # 默认版本缺席该 kind
            {"default_version": "v2", "templates": {"k": {"versions": {"v1": {"body": "x"}}}}},
        ],
    )
    def test_malformed_schema_raises(self, raw) -> None:
        with pytest.raises(ReviewTemplateRegistryError):
            ReviewTemplateRegistry.from_dict(raw)

    def test_missing_required_placeholder_raises(self) -> None:
        with pytest.raises(ReviewTemplateRegistryError):
            ReviewTemplateRegistry.from_dict(
                {
                    "default_version": "v1",
                    "templates": {
                        TEMPLATE_WAR_REPORT: {"versions": {"v1": {"body": "# {trade_date} {market_overview}"}}}
                    },
                }
            )

    def test_undeclared_placeholder_raises(self) -> None:
        with pytest.raises(ReviewTemplateRegistryError):
            ReviewTemplateRegistry.from_dict(
                {
                    "default_version": "v1",
                    "templates": {
                        TEMPLATE_WAR_REPORT: {
                            "versions": {
                                "v1": {
                                    "body": "{trade_date}{market_overview}{sector_highlights}{plan_outcomes}{risk_events}{summary}{secret_field}"
                                }
                            }
                        }
                    },
                }
            )


# ----------------------------------------------------------------------
# 文件加载
# ----------------------------------------------------------------------


class TestFileLoading:
    def test_committed_config_loadable(self) -> None:
        assert REVIEW_TEMPLATES_PATH.is_file()
        reg = ReviewTemplateRegistry.load(REVIEW_TEMPLATES_PATH)
        assert reg.source == "registry_file"
        assert set(reg.kinds()) == {TEMPLATE_WAR_REPORT, TEMPLATE_PROMPT_SUMMARY, TEMPLATE_FALLBACK_SUMMARY}

    def test_committed_config_v1_matches_embedded(self) -> None:
        """在档注册表 v1 与打包默认 v1 双向一致性锁（防双真源漂移）。"""
        file_reg = ReviewTemplateRegistry.load(REVIEW_TEMPLATES_PATH)
        embedded = ReviewTemplateRegistry.embedded_default()
        for kind in (TEMPLATE_WAR_REPORT, TEMPLATE_PROMPT_SUMMARY, TEMPLATE_FALLBACK_SUMMARY):
            assert file_reg.get(kind).body == embedded.get(kind).body

    def test_missing_file_falls_back_embedded(self, tmp_path) -> None:
        reg = ReviewTemplateRegistry.load(tmp_path / "no_such_templates.yaml")
        assert reg.source == "embedded_default"
        spec = reg.get(TEMPLATE_WAR_REPORT)
        assert any("回退" in n or "缺失" in n for n in spec.notes)

    def test_malformed_yaml_raises(self, tmp_path) -> None:
        bad = tmp_path / "bad.yaml"
        bad.write_text("templates: [unclosed\n  - x: {", encoding="utf-8")
        with pytest.raises(ReviewTemplateRegistryError):
            ReviewTemplateRegistry.load(bad)

    def test_custom_file_served(self, tmp_path) -> None:
        custom = tmp_path / "custom.yaml"
        custom.write_text(
            "default_version: v9\n"
            "templates:\n"
            "  war_report:\n"
            "    versions:\n"
            "      v9:\n"
            "        body: 'W9 {trade_date} {market_overview} {sector_highlights} {plan_outcomes} {risk_events} {summary}'\n",
            encoding="utf-8",
        )
        reg = ReviewTemplateRegistry.load(custom)
        assert reg.default_version == "v9"
        assert reg.get(TEMPLATE_WAR_REPORT).body.startswith("W9")


# ----------------------------------------------------------------------
# GAP-F-40 ai_review_summary 集成
# ----------------------------------------------------------------------


class TestAiReviewSummaryIntegration:
    def test_render_war_report_uses_registry_v2(self) -> None:
        reg = _v2_registry()
        summary = generate_review_summary(_ctx())  # 无网关 → 兜底结语
        md = render_war_report(_ctx(), summary, template_registry=reg, template_version="v2")
        assert md.startswith("# 战报V2 2026-08-21")
        assert "板块：机器人主线再强化" in md

    def test_render_war_report_default_registry_v1_compatible(self) -> None:
        # 不传注册表 → 打包默认 v1（与迁移前五段结构一致）
        summary = generate_review_summary(_ctx())
        md = render_war_report(_ctx(), summary)
        assert md.startswith("# 每日战报 2026-08-21")
        assert "## 5. AI 结语" in md

    def test_fallback_summary_uses_registry_v2(self) -> None:
        # default_version 切换到 v2 → 兜底结语走 v2 模板（版本可切换口径）
        reg = ReviewTemplateRegistry.from_dict(
            {
                "default_version": "v2",
                "templates": {
                    TEMPLATE_FALLBACK_SUMMARY: {
                        "versions": {
                            "v1": {
                                "body": "F1 {trade_date} {market_overview} {sector_highlights} {plan_outcomes} {risk_events}"
                            },
                            "v2": {
                                "body": "F2-兜底 {trade_date} {market_overview} {sector_highlights} {plan_outcomes} {risk_events}"
                            },
                        }
                    },
                },
            }
        )
        res = generate_review_summary(_ctx(), template_registry=reg)
        assert res.source == "template_fallback"
        assert res.summary_text.startswith("F2-兜底 2026-08-21")

    def test_prompt_uses_registry_v2(self) -> None:
        reg = ReviewTemplateRegistry.from_dict(
            {
                "default_version": "v2",
                "templates": {
                    TEMPLATE_PROMPT_SUMMARY: {
                        "versions": {
                            "v1": {
                                "body": "P1 {trade_date} {market_overview} {sector_highlights} {plan_outcomes} {risk_events} {max_chars}"
                            },
                            "v2": {
                                "body": "P2-自定义 {trade_date} {market_overview} {sector_highlights} {plan_outcomes} {risk_events} {max_chars}"
                            },
                        }
                    },
                },
            }
        )
        seen: dict[str, str] = {}

        def gw(prompt: str) -> str:
            seen["prompt"] = prompt
            return "主线清晰，控仓执行。"

        res = generate_review_summary(_ctx(), llm_gateway=gw, template_registry=reg)
        assert res.source == "llm"
        assert seen["prompt"].startswith("P2-自定义 2026-08-21")

    def test_missing_version_fallback_in_render(self) -> None:
        reg = _v2_registry()
        summary = generate_review_summary(_ctx())
        md = render_war_report(_ctx(), summary, template_registry=reg, template_version="v9")
        assert md.startswith("# 每日战报 2026-08-21")  # 回退 v1


# ----------------------------------------------------------------------
# 契约
# ----------------------------------------------------------------------


class TestContract:
    def test_template_spec_frozen_and_json(self) -> None:
        spec = ReviewTemplateRegistry.embedded_default().get(TEMPLATE_WAR_REPORT)
        assert isinstance(spec, TemplateSpec)
        with pytest.raises(dataclasses.FrozenInstanceError):
            spec.body = "x"  # type: ignore[misc]
        json.dumps(spec.to_dict(), ensure_ascii=False)
