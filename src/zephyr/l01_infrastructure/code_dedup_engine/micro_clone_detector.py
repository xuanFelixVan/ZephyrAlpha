# [BLUEPRINT] MOD-INF-017 | 03_modules/l01_infrastructure/code-dedup-engine/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.code_dedup_engine.micro_clone_detector

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""微型克隆检测器 — n-gram频率计数, 1-2行高频模式聚合."""

from __future__ import annotations

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
            ngram = "\n".join(l.strip() for l in source_lines[i:i + self._NGRAM_SIZE])
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
