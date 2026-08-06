# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
# [MODULE] tests.governance.test_algo_quality
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.check_algo_quality
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 测试目录隔离：不读真实项目文件，所有输入为内联字符串；阴性测试用真实 chip_distribution_engine.py
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""tests for check_algo_quality.py — GATE-ALGO-QUALITY 6类糊弄pattern检测器。

阳性测试：用 15 处已修糊弄点的旧实现/描述做输入，应全检出。
阴性测试：用修正后的前沿算法代码/描述做输入，不误报。
端到端测试：跑 main() 的 exit code 行为（--ci vs --warn-only）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CHECKER_DIR = _REPO_ROOT / "scripts" / "governance" / "d5_architecture" / "checkers"
if str(_CHECKER_DIR) not in sys.path:
    sys.path.insert(0, str(_CHECKER_DIR))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import check_algo_quality as caq  # noqa: E402

# ============================================================================
# 公共辅助
# ============================================================================


def _patterns(findings: list[caq.Finding], pattern: str) -> list[caq.Finding]:
    """从 findings 中筛出指定 pattern。"""
    return [f for f in findings if f.pattern == pattern]


# ============================================================================
# P1 代理替代
# ============================================================================


class TestP1ProxyCode:
    """P1 代码层检测——代理替代。"""

    def test_ast_function_name_vs_impl(self):
        """函数名声称计算 chip_distribution，body 仅用 turnover → 违规。"""
        code = "def compute_chip_distribution(ohlcv):\n    return ohlcv['turnover_rate'] / 100.0\n"
        fs = caq.audit_code_str(code, "fake_proxy.py")
        assert len(_patterns(fs, "P1_proxy")) >= 1
        # AST 路径产出 error 级
        assert any(f.severity == "error" for f in _patterns(fs, "P1_proxy"))

    def test_regex_proxy_keyword_in_algo_context(self):
        """注释含代理词且在算法上下文 → 违规。"""
        code = "# 用换手率代理筹码分布\ndef calc_distribution(ohlcv):\n    return ohlcv['turnover_rate']\n"
        fs = caq.audit_code_str(code, "fake_regex.py")
        assert len(_patterns(fs, "P1_proxy")) >= 1

    def test_negation_context_not_flagged(self):
        """显式否定（'非换手率代理'）不应误报。"""
        code = '"""从 OHLCV 自建筹码分布（非换手率代理），供 regime 使用。"""\ndef calc():\n    pass\n'
        fs = caq.audit_code_str(code, "negated.py")
        assert len(_patterns(fs, "P1_proxy")) == 0

    def test_correct_chip_distribution_not_flagged(self):
        """华泰VWAP三角分布实现 → 不应误报 P1。"""
        engine_path = _REPO_ROOT / "src" / "zephyr" / "regime" / "features" / "chip_distribution_engine.py"
        if not engine_path.exists():
            pytest.skip("chip_distribution_engine.py not built yet")
        fs = caq.audit_code(engine_path)
        # 实际文件可能因注释含'换手率'被 P1 regex 误判，但 AST 路径不应误报
        ast_findings = [f for f in fs if f.pattern == "P1_proxy" and f.severity == "error"]
        assert len(ast_findings) == 0, f"AST 路径误报：{ast_findings}"


class TestP1ProxyBlueprint:
    """P1 blueprint 层检测——代理替代。"""

    def test_proxy_word_in_algo_section(self):
        bp = "## 3. 核心算法\n\n#12 筹码结构：换手率代理（省事写法）\n"
        fs = caq.audit_blueprint_str(bp, "fake_bp.md")
        assert len(_patterns(fs, "P1_proxy")) >= 1

    def test_negated_proxy_not_flagged(self):
        """显式否定（'非换手率代理'）不应误报。"""
        bp = "## 3. 核心算法\n\n#12 筹码结构：自建（非换手率代理）\n"
        fs = caq.audit_blueprint_str(bp, "negated_bp.md")
        assert len(_patterns(fs, "P1_proxy")) == 0


# ============================================================================
# P2 定性词无量化
# ============================================================================


class TestP2Qualitative:
    """P2 检测——定性词无量化。"""

    def test_code_keyword_list_no_classifier(self):
        """代码中定义关键词列表但无分类函数 → 违规。"""
        code = 'POLICY_KEYWORDS = ["降准", "降息", "MLF", "喊话"]\nscore = 0\n'
        fs = caq.audit_code_str(code, "fake_p2.py")
        assert len(_patterns(fs, "P2_qualitative")) >= 1

    def test_code_keyword_list_with_classifier_not_flagged(self):
        """关键词列表 + classify 函数 → 不违规。"""
        code = 'POLICY_KEYWORDS = ["降准", "降息", "MLF"]\ndef classify_policy(text):\n    return 40\n'
        fs = caq.audit_code_str(code, "ok_p2.py")
        assert len(_patterns(fs, "P2_qualitative")) == 0

    def test_blueprint_keyword_to_score_no_algo(self):
        """blueprint '关键词→分值' 但无算法步骤词 → 违规。"""
        bp = "## 4. 维度评分\n\n- 降准/降息/MLF → 40分\n"
        fs = caq.audit_blueprint_str(bp, "fake_p2_bp.md")
        assert len(_patterns(fs, "P2_qualitative")) >= 1

    def test_blueprint_keyword_to_score_with_algo_not_flagged(self):
        """blueprint '关键词→分值' 但配套算法步骤词 → 不违规。"""
        bp = (
            "## 4. 维度评分\n\n"
            "降准/降息/MLF → 40分\n\n"
            "算法：NLP 三层管道五元组精分类，classify_policy() 返回事件类型与方向\n"
        )
        fs = caq.audit_blueprint_str(bp, "ok_p2_bp.md")
        assert len(_patterns(fs, "P2_qualitative")) == 0


# ============================================================================
# P3 伪精确
# ============================================================================


class TestP3FalsePrecision:
    """P3 检测——伪精确（量纲依赖阈值）。"""

    def test_code_angle_threshold(self):
        """if angle > 45 → 违规（量纲依赖）。"""
        code = "def check(angle):\n    if angle > 45:\n        return True\n    return False\n"
        fs = caq.audit_code_str(code, "fake_p3.py")
        assert len(_patterns(fs, "P3_false_precision")) >= 1

    def test_code_hurst_threshold_not_flagged(self):
        """if hurst > 0.5 → 不违规（hurst 已无量纲）。"""
        code = "def check(hurst):\n    if hurst > 0.5:\n        return True\n    return False\n"
        fs = caq.audit_code_str(code, "ok_p3.py")
        assert len(_patterns(fs, "P3_false_precision")) == 0

    def test_code_angle_threshold_with_normalize_not_flagged(self):
        """if angle > 45 + normalize 调用 → 不违规。"""
        code = (
            "def check(angle, hist):\n"
            "    angle = (angle - hist.mean()) / hist.std()  # normalize\n"
            "    if angle > 45:\n"
            "        return True\n"
            "    return False\n"
        )
        fs = caq.audit_code_str(code, "ok_p3_norm.py")
        assert len(_patterns(fs, "P3_false_precision")) == 0

    def test_blueprint_angle_threshold(self):
        """blueprint '均线角度>45°' 无量纲化 → 违规。"""
        bp = "## 5. 核心算法\n\n- 均线角度>45° → 趋势确立\n"
        fs = caq.audit_blueprint_str(bp, "fake_p3_bp.md")
        assert len(_patterns(fs, "P3_false_precision")) >= 1


# ============================================================================
# P4 死数据
# ============================================================================


class TestP4DeadData:
    """P4 检测——死数据源引用。"""

    def test_code_import_dead_data(self):
        """from zephyr.data import hk_connect_flow → 违规。"""
        code = "from zephyr.data import hk_connect_flow\n"
        fs = caq.audit_code_str(code, "fake_p4.py")
        assert len(_patterns(fs, "P4_dead_data")) >= 1

    def test_code_query_dead_data_table(self):
        """query('hk_connect_daily') → 违规。"""
        code = 'def fetch():\n    return query("hk_connect_daily")\n'
        fs = caq.audit_code_str(code, "fake_p4_query.py")
        assert len(_patterns(fs, "P4_dead_data")) >= 1

    def test_code_northbound_alias(self):
        """northbound_flow 别名 → 违规。"""
        code = 'def calc(nb):\n    # 北向资金计算\n    flow = nb.get("northbound_flow")\n    return flow\n'
        fs = caq.audit_code_str(code, "fake_p4_alias.py")
        assert len(_patterns(fs, "P4_dead_data")) >= 1

    def test_code_dead_data_marker_exempted(self):
        """DEAD_DATA_SOURCES 清单定义自身不误报。"""
        code = 'DEAD_DATA_SOURCES = {"hk_connect_flow": {"stopped": "2024-08-19"}}\n'
        fs = caq.audit_code_str(code, "self_ref.py")
        assert len(_patterns(fs, "P4_dead_data")) == 0

    def test_blueprint_dead_data_in_data_source(self):
        """blueprint 数据源表引用死数据 → 违规。"""
        bp = "## 3. 数据源\n\n| 数据源 | 用途 |\n|---|---|\n| hk_connect_flow | 北向资金回流 |\n"
        fs = caq.audit_blueprint_str(bp, "fake_p4_bp.md")
        assert len(_patterns(fs, "P4_dead_data")) >= 1

    def test_blueprint_dead_data_with_deprecation_marker_not_flagged(self):
        """blueprint 死数据 + '已停发'说明 → 不违规（文档债务标注）。"""
        bp = "## 3. 数据源\n\n| hk_connect_flow | 北向资金（已停发 2024-08-19，已替代） |\n"
        fs = caq.audit_blueprint_str(bp, "debt_p4_bp.md")
        assert len(_patterns(fs, "P4_dead_data")) == 0


# ============================================================================
# P5 名词堆砌无算法
# ============================================================================


class TestP5Buzzword:
    """P5 检测——名词堆砌无算法。"""

    def test_code_buzzword_stub(self):
        """docstring 含 ≥3 缩写 + body 为 pass → 违规。"""
        code = 'def detect_wyckoff():\n    """识别 PS/SC/AR/ST/Spring/SOS 结构。"""\n    pass\n'
        fs = caq.audit_code_str(code, "fake_p5.py")
        assert len(_patterns(fs, "P5_buzzword")) >= 1

    def test_code_buzzword_with_implementation_not_flagged(self):
        """docstring 含缩写但 body 有算法实现 → 不违规。"""
        code = (
            "def detect_wyckoff(candles):\n"
            '    """识别 PS/SC/AR/ST/Spring/SOS 结构。"""\n'
            "    tr = _identify_tr(candles)\n"
            "    sc = _detect_selling_climax(candles)\n"
            "    spring = _detect_spring(candles, tr)\n"
            '    return {"TR": tr, "SC": sc, "Spring": spring}\n'
        )
        fs = caq.audit_code_str(code, "ok_p5.py")
        assert len(_patterns(fs, "P5_buzzword")) == 0

    def test_code_two_abbrevs_not_flagged(self):
        """docstring 仅 2 个缩写 → 不违规（阈值 <3）。"""
        code = 'def detect():\n    """检测 SOS 和 LPS。"""\n    pass\n'
        fs = caq.audit_code_str(code, "ok_p5_two.py")
        assert len(_patterns(fs, "P5_buzzword")) == 0

    def test_blueprint_buzzword_no_algo(self):
        """blueprint 算法章节 ≥3 缩写 + 无算法步骤词 → 违规。"""
        bp = "## 4. 维度评分\n\n- PS/SC/AR/ST/SOS 结构识别 → 60分\n"
        fs = caq.audit_blueprint_str(bp, "fake_p5_bp.md")
        assert len(_patterns(fs, "P5_buzzword")) >= 1

    def test_blueprint_buzzword_with_algo_step_not_flagged(self):
        """blueprint 算法章节 ≥3 缩写 + 配套算法步骤词 → 不违规。"""
        bp = "## 4. 维度评分\n\n规则法 TR 识别 + 4 触发器 + 5 态 FSM：PS/SC/AR/ST/SOS 事件触发\n"
        fs = caq.audit_blueprint_str(bp, "ok_p5_bp.md")
        assert len(_patterns(fs, "P5_buzzword")) == 0


# ============================================================================
# P6 逻辑错位
# ============================================================================


class TestP6Logical:
    """P6 检测——逻辑错位（否决条件当正向评分）。"""

    def test_code_not_x_then_score(self):
        """if not X: score += 60 → 违规。"""
        code = "def calc(has_x):\n    score = 0\n    if not has_x:\n        score += 60\n    return score\n"
        fs = caq.audit_code_str(code, "fake_p6.py")
        assert len(_patterns(fs, "P6_logical")) >= 1
        assert any(f.severity == "error" for f in _patterns(fs, "P6_logical"))

    def test_code_positive_condition_not_flagged(self):
        """if X: score += 60 → 不违规（正向条件 + 正向评分）。"""
        code = "def calc(has_x):\n    score = 0\n    if has_x:\n        score += 60\n    return score\n"
        fs = caq.audit_code_str(code, "ok_p6.py")
        assert len(_patterns(fs, "P6_logical")) == 0

    def test_blueprint_no_x_to_score(self):
        """blueprint '无虹吸 → 60分' → 违规。"""
        bp = "## 4. 维度评分\n\n- 无虹吸 → 60分\n"
        fs = caq.audit_blueprint_str(bp, "fake_p6_bp.md")
        assert len(_patterns(fs, "P6_logical")) >= 1

    def test_blueprint_positive_condition_not_flagged(self):
        """blueprint '有虹吸 → 60分' → 不违规。"""
        bp = "## 4. 维度评分\n\n- 有主线 → 60分\n"
        fs = caq.audit_blueprint_str(bp, "ok_p6_bp.md")
        assert len(_patterns(fs, "P6_logical")) == 0


# ============================================================================
# 端到端测试——15 处已修糊弄全检出
# ============================================================================


class TestFifteenFixedFraudsAllDetected:
    """15 处已修糊弄点的旧实现/描述，应全检出。

    这是对设计文档 §验证方案 的落实：用 15 处旧糊弄文本做输入，
    确认 6 类 pattern 检测器全部命中。
    """

    @pytest.mark.parametrize(
        "idx, text, expected_pattern",
        [
            # 1. F2 均线斜率（量纲依赖）→ P3
            (1, "## 5. 核心算法\n\nF2: 均线斜率 > 0.5 → 趋势确立\n", "P3_false_precision"),
            # 2. #8 主板vs板块涨幅差（未定义）→ 文档层无指标算法，但定性词模式 → P2
            (2, "## 4. 评分\n\n- 涨幅差 → 40分\n", "P2_qualitative"),
            # 3. #9 KDJ>90+价未超前高（非数学化）→ P2 定性词
            (3, "## 4. 评分\n\n- KDJ>90 + 价未超前高 → 40分\n", "P2_qualitative"),
            # 4. #10 均线角度>45°（伪精确）→ P3
            (4, "## 5. 算法\n\n均线角度>45° → 趋势确立\n均线角度<30° → 趋势衰竭\n", "P3_false_precision"),
            # 5. #12 换手率代理（筹码分布）→ P1
            (5, "## 5. 算法\n\n#12 筹码结构：换手率代理\n", "P1_proxy"),
            # 6. S2 capitulation 加密货币指标 → 不属本检测器范围（指标错配，需 LLM 兜底）
            # 跳过——本规则引擎仅检测文本 pattern，语义错配留 Phase 2 LLM
            # 7. S2 wyckoff 名词堆砌 → P5
            (7, "## 4. 评分\n\n- PS/SC/AR/ST/SOS 结构识别 → 60分\n", "P5_buzzword"),
            # 8. S2 fund 北向回流（死数据）→ P4
            (8, "## 3. 数据源\n\n| 北向资金回流 | 实时特征 |\n", "P4_dead_data"),
            # 9. S2 spring 模糊算法 → P2 定性词无算法
            (9, "## 4. 评分\n\n- 震仓后拉升 → 60分\n", "P2_qualitative"),
            # 10. S2 policy 定性词 → P2
            (10, "## 4. 评分\n\n- 降准降息/MLF/喊话 → 40分\n", "P2_qualitative"),
            # 11. S2 bad_news_flat 定性词 → P2
            (11, "## 4. 评分\n\n- 重大利空后低开拉回 → 40分\n", "P2_qualitative"),
            # 12. #11 news_ghost 定性词 → P2
            (12, "## 4. 评分\n\n- 鬼故事密集 → 40分\n", "P2_qualitative"),
            # 13. T3 mainline 无虹吸=主线 → P6 逻辑错位
            (13, "## 4. 评分\n\n- 无虹吸 → 60分\n", "P6_logical"),
            # 14. T3 sentiment 北向回流（死数据）→ P4
            (14, "## 3. 数据源\n\n- 北向资金回流 → 50分\n", "P4_dead_data"),
            # 15. S1/S2 VIX IV>35（伪精确/量纲未明）→ P3
            (15, "## 5. 算法\n\n- IV>35 → VIX 高位\n", "P3_false_precision"),
        ],
    )
    def test_fraud_detected(self, idx, text, expected_pattern):
        """15 处已修糊弄点（除 #6 需 LLM）应被规则引擎检出。"""
        fs = caq.audit_blueprint_str(text, f"fraud_{idx}.md")
        matching = _patterns(fs, expected_pattern)
        assert len(matching) >= 1, (
            f"Fraud #{idx} 未被 {expected_pattern} 检出；实际 findings: {[(f.pattern, f.detail) for f in fs]}"
        )


# ============================================================================
# 阴性测试——修正后的算法不误报
# ============================================================================


class TestCorrectAlgorithmsNotFlagged:
    """修正后的前沿算法描述，不应触发任何 pattern。"""

    def test_correct_chip_distribution_blueprint(self):
        """华泰VWAP三角分布描述 → 无误报。"""
        bp = (
            "## 3. 核心算法\n\n"
            "筹码分布采用华泰2026前沿算法：VWAP 中心三角分布 + 换手递推公式 + "
            "筹码龄分层（ultra_short/short/medium/long）+ 32 相对网格映射。\n\n"
            "核心公式：C_t = (1-τ)×C_{t-1} + τ×D_t\n"
        )
        fs = caq.audit_blueprint_str(bp, "correct_chip.md")
        # 关键 pattern 不应误报
        assert len(_patterns(fs, "P1_proxy")) == 0
        assert len(_patterns(fs, "P5_buzzword")) == 0

    def test_correct_hurst_blueprint(self):
        """Hurst(DFA) + Kalman 自适应斜率描述 → 无误报。"""
        bp = (
            "## 3. 核心算法\n\n"
            "F2 趋势特征：Hurst 指数（DFA 法计算）+ Kalman 滤波自适应斜率。\n"
            "Hurst > 0.5 趋势持久性；< 0.5 均值回归。\n"
            "Kalman 斜率归一化 [-1,1]，不依赖固定窗口或量纲。\n"
        )
        fs = caq.audit_blueprint_str(bp, "correct_hurst.md")
        # P3 不应误报（hurst 无量纲，kalman 已归一化）
        assert len(_patterns(fs, "P3_false_precision")) == 0

    def test_correct_acsi_blueprint(self):
        """ACSI A股投降指数描述 → 无误报。"""
        bp = (
            "## 4. 维度评分\n\n"
            "ACSI = 量能极端(3×均量) + 价格跌幅(10日ROC<-10%) + 广度崩塌(跌停>5%) + "
            "杠杆出清(两融5日缩水≥5%) + 流动性枯竭(地量换手)\n"
            "加权 [0,100]，≥60 分 → 60分\n"
        )
        fs = caq.audit_blueprint_str(bp, "correct_acsi.md")
        # 关键 pattern 不应误报
        assert len(_patterns(fs, "P2_qualitative")) == 0
        assert len(_patterns(fs, "P5_buzzword")) == 0

    def test_correct_vix_blueprint(self):
        """CBOE 方差互换合成 VIX 描述 → 无误报。"""
        bp = (
            "## 5. 核心算法\n\n"
            "VIX 构建：CBOE 方差互换公式，300ETF 期权 IV 曲面 + SVI 参数化校准 + 7日展期。\n"
            "滚动分位阈值（>90分位 → 高位）+ 期限结构修复（Backwardation → Contango）。\n"
        )
        fs = caq.audit_blueprint_str(bp, "correct_vix.md")
        # P3 不应误报（分位阈值无量纲）
        assert len(_patterns(fs, "P3_false_precision")) == 0
        # P5 不应误报（CBOE/SVI 是缩写但有算法步骤词）
        assert len(_patterns(fs, "P5_buzzword")) == 0


# ============================================================================
# main() 端到端测试
# ============================================================================


class TestMainExitCodes:
    """main() 退出码行为。"""

    def test_clean_code_exit_zero_ci(self, monkeypatch, tmp_path):
        """干净代码 --ci 模式 → exit 0。"""
        clean_py = tmp_path / "clean.py"
        clean_py.write_text("x = 1\n", encoding="utf-8")
        monkeypatch.setattr(caq, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(sys, "argv", ["check_algo_quality.py", "--ci", str(clean_py)])
        assert caq.main() == 0

    def test_fraud_code_warn_only_exit_zero(self, monkeypatch, tmp_path):
        """有糊弄 --warn-only → exit 0（仅报告）。"""
        fraud_py = tmp_path / "fraud.py"
        fraud_py.write_text("from zephyr.data import hk_connect_flow\n", encoding="utf-8")
        monkeypatch.setattr(caq, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(sys, "argv", ["check_algo_quality.py", "--warn-only", str(fraud_py)])
        assert caq.main() == 0

    def test_fraud_code_ci_exit_one(self, monkeypatch, tmp_path):
        """有糊弄 --ci 模式 → exit 1（硬阻断）。"""
        fraud_py = tmp_path / "fraud.py"
        fraud_py.write_text("from zephyr.data import hk_connect_flow\n", encoding="utf-8")
        monkeypatch.setattr(caq, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(sys, "argv", ["check_algo_quality.py", "--ci", str(fraud_py)])
        assert caq.main() == 1

    def test_missing_file_exit_two(self, monkeypatch, tmp_path):
        """文件不存在 → exit 2。"""
        monkeypatch.setattr(caq, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(sys, "argv", ["check_algo_quality.py", "--ci", str(tmp_path / "nonexistent.py")])
        assert caq.main() == 2


# ============================================================================
# blueprint 章节抽取测试
# ============================================================================


class TestBlueprintSectionExtraction:
    """blueprint 算法章节抽取逻辑。"""

    def test_extracts_section_3_4_5(self):
        text = (
            "# Blueprint\n\n"
            "## 1. 概述\n内容1\n\n"
            "## 3. 核心算法\n算法A\n\n"
            "## 4. 维度评分\n评分B\n\n"
            "## 5. 数据源\n数据C\n\n"
            "## 6. 接口\n接口D\n"
        )
        section = caq._extract_blueprint_algo_sections(text)
        assert "算法A" in section
        assert "评分B" in section
        assert "数据C" in section
        # §1/§6 不在算法章节范围
        assert "内容1" not in section
        assert "接口D" not in section

    def test_no_algo_section_returns_full_text(self):
        """无 §3/4/5 章节时返回全文（兜底）。"""
        text = "# Blueprint\n\n## 1. 概述\n内容\n"
        section = caq._extract_blueprint_algo_sections(text)
        assert "内容" in section
