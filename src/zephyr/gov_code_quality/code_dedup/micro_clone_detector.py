# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.micro_clone_detector
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.intelligence_governance.self_benchmark; tests/governance/drift/test_micro_clone_detector.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
微型克隆检测器 — n-gram频率计数, 1-2行高频模式聚合.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: micro_clone_detector.py
# 层: 算法
# - id: A1
#   name_zh: ① MicroCloneDetector
#   name_en: MicroCloneDetector
#   intro: 1-2行微克隆检测.
#   desc: 1-2行微克隆检测.；公共方法（定义序）: detect, compute_density；源码 L51-L80
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: MicroCloneDetector
#   downstream: zephyr.governance.intelligence_governance.self_benchmark; tests/governance/drif…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from collections import Counter


class MicroCloneDetector:
    """1-2行微克隆检测."""

    _NGRAM_SIZE: int = 3
    _MIN_FREQ: int = 2

    def detect(self, source_lines: list[str]) -> list[tuple[str, int]]:
        """n-gram频率分析."""
        if len(source_lines) < self._NGRAM_SIZE:
            return []

        ngrams: list[str] = []
        for i in range(len(source_lines) - self._NGRAM_SIZE + 1):
            ngram = "\n".join(l.strip() for l in source_lines[i : i + self._NGRAM_SIZE])
            ngrams.append(ngram)

        freq = Counter(ngrams)
        micro_clones = [(ng, c) for ng, c in freq.items() if c >= self._MIN_FREQ]
        micro_clones.sort(key=lambda x: x[1], reverse=True)

        return micro_clones[:20]

    def compute_density(self, source: str) -> float:
        """微克隆密度 = 高频n-grams数 / 总行数."""
        lines = source.splitlines()
        if len(lines) < self._NGRAM_SIZE:
            return 0.0

        clones = self.detect(lines)
        return round(len(clones) / len(lines), 4)
