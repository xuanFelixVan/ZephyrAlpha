# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.read_side
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] —
# [CONSUMERS] zephyr.gov_enforcement.commit_gates.read_side.fms_hygiene_gate; zephyr.gov_enforcement.commit_gates.read_side.fms_ref_extractor
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 读侧（docs 引用面）commit gate 子包——FMS 文件管理体系读侧执法门的命名空间；与写侧（.py 代码面）门禁家族正交
# [MODIFY-GUARD] 子包公开面=fms_hygiene_gate.make_fms_hygiene_gate / fms_ref_extractor 共享提取器
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] —（纯命名空间，无逻辑）
# [TESTS] tests/gov_enforcement/read_side/test_fms_hygiene_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""read_side — FMS 读侧执法门子包（死引用棘轮/ASCII/生命周期隔离/CAS 残渣四查）。

文件管理体系（FMS）大改造战役 B1 批交付：读侧=文档/登记面对盘面路径的**引用**
卫生执法；写侧（.py 代码面）由既有 gate 家族承担，两者正交。

- :mod:`fms_ref_extractor`——共享仓内路径 token 提取器（门与基线生成器单写者共用，
  口径漂移防线）。
- :mod:`fms_hygiene_gate`——FMS-HYGIENE 读侧门（priority=138，warn→block 两段制）。

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/r/read_side_fms_hygiene_gate.yaml
"""

from typing import Final

from zephyr.gov_enforcement.commit_gates.read_side import fms_ref_extractor  # noqa: E402
from zephyr.gov_enforcement.commit_gates.read_side.fms_hygiene_gate import make_fms_hygiene_gate  # noqa: E402

__all__: Final = ["make_fms_hygiene_gate", "fms_ref_extractor"]
