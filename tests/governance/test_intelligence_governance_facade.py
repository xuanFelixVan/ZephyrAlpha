# [A_test] module_id: MOD-GOV-intelligence_governance | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_intelligence_governance_facade
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] __all__ 每符号与子模块唯一真实定义同一对象；包级 import 零 eager 子模块加载；幻影名/双义名不导出
# [MODIFY-GUARD] Changes must sync with src/zephyr/governance/intelligence_governance/__init__.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None
# [TESTS] python -m pytest tests/governance/test_intelligence_governance_facade.py -q
# [TTL] task_bound
"""契约测试：intelligence_governance 包入口 PEP 562 惰性外观（AI-ADJ-001 裁定1）。

历史病灶：旧 __init__.py 裸 __all__ 33 项零 import 绑定，含 6 个包内无定义的
幻影名（DriftConfig/DriftType/KnowledgeEntry/KnowledgeIndex/get_drift_config/
get_index），且 DebateRound 在 agent_debate（BaseModel）与
multi_model_consensus（str, Enum）双义。治本：PEP 562 __getattr__ 惰性外观，
__all__ 只保留真实存在且无歧义的公开符号（42 项）。

契约：
1. __all__ 每个名字 getattr(pkg, name) 可导入，且与唯一持有真实定义的子模块
   为同一对象（不依赖 facade 自有映射，独立扫描全子模块验证无歧义）。
2. __all__ 无重复名。
3. 包级 import zephyr.governance.intelligence_governance 不 eager import 任何
   子模块（子进程内 sys.modules 差集断言，排除父包 zephyr.governance 既有加载）。
4. 幻影六名与双义 DebateRound 不在 __all__。
"""

from __future__ import annotations

import importlib
import pkgutil
import subprocess
import sys

import zephyr.governance.intelligence_governance as ig_pkg

_PHANTOM_NAMES = (
    "DriftConfig",
    "DriftType",
    "KnowledgeEntry",
    "KnowledgeIndex",
    "get_drift_config",
    "get_index",
)

_IG_PREFIX = "zephyr.governance.intelligence_governance"


def _submodule_names() -> list[str]:
    return sorted(m.name for m in pkgutil.iter_modules(ig_pkg.__path__))


class TestFacadeExports:
    def test_every_export_matches_unique_submodule_definition(self):
        for name in ig_pkg.__all__:
            owners = []
            for sub in _submodule_names():
                mod = importlib.import_module(f"{_IG_PREFIX}.{sub}")
                if name in mod.__dict__:
                    owners.append(mod.__dict__[name])
            assert len(owners) == 1, f"{name}: 持有定义的子模块数={len(owners)}（须唯一）"
            assert getattr(ig_pkg, name) is owners[0], name

    def test_all_has_no_duplicates(self):
        assert len(ig_pkg.__all__) == len(set(ig_pkg.__all__))

    def test_phantom_and_ambiguous_names_not_exported(self):
        for name in _PHANTOM_NAMES:
            assert name not in ig_pkg.__all__, name
        assert "DebateRound" not in ig_pkg.__all__

    def test_package_import_is_lazy(self):
        code = (
            "import sys;"
            "import zephyr.governance;"
            "before = set(sys.modules);"
            "import zephyr.governance.intelligence_governance;"
            "new = {m for m in set(sys.modules) - before"
            " if m.startswith('zephyr.governance.intelligence_governance.')};"
            "assert not new, f'eager submodule imports: {sorted(new)}'"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
