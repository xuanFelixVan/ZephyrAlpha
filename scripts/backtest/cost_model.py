# [BLUEPRINT] MOD-BT-191 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.cost_model
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] os; pathlib; typing
# [CONSUMERS] scripts/backtest/translated/_c4_engine.py（_cost_model_adapter/_net_line）；C4 批测/考试产线
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] legacy 缺席路径=零行为（resolve_from_env→None=引擎冻结土规 verbatim）；未知档 fail-closed 禁自创口径
# [MODIFY-GUARD] tests/backtest/test_c4_batch_smoke.py; tests/backtest/test_c4_deflated_sharpe_runner.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(未知成本档名)
# [TESTS] tests/backtest/test_c4_batch_smoke.py
# [A_module] module_id=MOD-BT-191 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C4 成本档适配器（W1-4 可插拔成本档接口面——遗失重建件，2026-10-05）。

事故与重建声明: 本文件被 _c4_engine._cost_model_adapter 按文件路径硬引用（引擎
INVARIANTS 写明"缺省/legacy→None=冻结土规 verbatim 路径"），但原字节遗失——git 全
历史零提交、全部 80+ 会话 worktree 与悬空 blob 均无、仅 docs/04_research_records/backtest/campaigns/fullscore_night
03_integrated_backtest/prereg_v2.md §附录A 残留指纹 sha256[:16]=daebf3bed4c0fdd6
（2026-10-01 实测，现盘面 engine 指纹亦已漂移=该 prereg 快照整体失效，已在其域内留证）。
本重建=接口面最小恢复：legacy 缺席路径零行为（返回 None 走引擎冻结土规逐位原式）；
非 legacy 档名 fail-closed 抛 RuntimeError（禁凭记忆伪造 calibrated/participation 语义
——原档位语义不可考，伪造=第二真源）。原指纹不可恢复匹配，prereg_v2 域主须重锁。

[KNOWLEDGE_EFFECTIVE_FROM] 2026-10-05 | 源=遗失重建生成日 | 生成=AI 会话（EXEC-F2/st-datasop-20260930）
"""

from __future__ import annotations

import os
from typing import Any

_ENV_KEY = "ZEPHYR_C4_COST_MODEL"
_KNOWN_LEGACY = {"", "legacy"}


class LegacyPassthroughCostModel:
    """缺省档占位——resolve_from_env 缺席时不会被构造（None=引擎 verbatim 冻结土规）。"""

    def round_trip_bps(self, slippage_bp: float | None = None) -> float:
        raise RuntimeError("legacy 档不走适配器标量路径（引擎 verbatim 分支承担）")


def resolve_from_env() -> Any | None:
    """按环境变量选成本档；缺省/legacy→None（引擎冻结土规 verbatim，零漂移红线）。

    非 legacy 档名（原件曾支持 calibrated/participation，语义不可考）→fail-closed：
    禁止凭记忆伪造标定口径，须恢复原件或按新裁定重建档位语义后再扩本表。
    """
    raw = os.environ.get(_ENV_KEY, "").strip().lower()
    if raw in _KNOWN_LEGACY:
        return None
    raise RuntimeError(
        f"{_ENV_KEY}={raw!r} 为未知成本档：原件遗失（prereg_v2 指纹 daebf3bed4c0fdd6 不可考），"
        "fail-closed 禁伪造档位语义；恢复原件或经裁定重建后扩 _KNOWN_LEGACY"
    )
