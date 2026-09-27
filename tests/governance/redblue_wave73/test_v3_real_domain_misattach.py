# [TTL] permanent
# [MODULE] tests.governance.redblue_wave73.test_v3_real_domain_misattach
# [DOMAIN] D_GOV_CODE_QUALITY
"""wave7.3 缺陷①红/绿证明：真域错挂（GATE-DOMAIN-FK 归属判据）。

修前（红）：真实域 D_GOV_ENFORCEMENT 错挂到 src/zephyr/trading/ 文件——原门只做
存在性 FK，放行（st-c7-rb-20260927 V3b 在案发现的"越域挂载本体"）。
修后（绿）：归属判据（内嵌包域族表 _PKG_DOMAIN_RULES）阻断错挂；
同族/族前缀/豁免域放行；包不在册 fail-open 不判；假域 FK 行为不变。
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

_PROJECT_ROOT = Path(__file__).resolve().parents[3]

# 注册表 mock：只含真实域——被检 [DOMAIN] 全部"存在"，拦与放只取决于归属判据。
_YAML = (
    "- domain: D_GOV_ENFORCEMENT\n"
    "- domain: D_GOV_CODE_QUALITY\n"
    "- domain: D_GOVERNANCE\n"
    "- domain: D_TRADING\n"
    "- domain: D_INFRA_RUNTIME\n"
)


def _gateway(py_rel: str, domain_line: str):
    gw = MagicMock()
    gw.project_root = _PROJECT_ROOT

    def _run(cmd: list[str]):
        res = MagicMock()
        res.returncode = 0
        if cmd[:3] == ["git", "diff", "--cached"] and "--name-only" in cmd:
            res.stdout = py_rel + "\n"
        elif "--unified=0" in cmd:
            res.stdout = f"@@ -0,0 +1,1 @@\n+{domain_line}\n"
        elif cmd[:2] == ["git", "show"] and cmd[2].startswith(":"):
            res.stdout = _YAML if "functional_domain_registry" in cmd[2] else domain_line + "\n"
        else:
            res.returncode = 1
            res.stdout = ""
        return res

    gw.run_git = _run
    return gw


def _check(py_rel: str, domain: str) -> tuple[bool, str]:
    from zephyr.gov_enforcement.commit_gates.domain_fk_gate import make_domain_fk_gate

    return make_domain_fk_gate().check(_gateway(py_rel, f"# [DOMAIN] {domain}"), [py_rel])


class TestRealDomainMisattach:
    def test_wrong_real_domain_on_known_package_blocks(self):
        """红→绿主样本：trading 包挂 gov 真域，修前放行（红），修后阻断。"""
        passed, detail = _check("src/zephyr/trading/fake_gov_holder.py", "D_GOV_ENFORCEMENT")
        assert passed is False, "真域错挂（trading 包挂 gov 域）未阻断——归属判据缺位"
        assert "真域错挂" in detail

    def test_family_matching_domain_passes(self):
        passed, _ = _check("src/zephyr/gov_enforcement/legit_gate.py", "D_GOV_CODE_QUALITY")
        assert passed is True, "同包合法域被误伤——判据过宽"

    def test_family_prefix_domain_passes(self):
        """族前缀语义：D_GOV 规则放行 D_GOVERNANCE（gov_enforcement 现库行为）。"""
        passed, _ = _check("src/zephyr/gov_enforcement/legit2.py", "D_GOVERNANCE")
        assert passed is True

    def test_exact_and_exception_domains_pass(self):
        assert _check("src/zephyr/trading/legit.py", "D_TRADING")[0] is True
        assert _check("src/zephyr/trading/legit_runtime.py", "D_INFRA_RUNTIME")[0] is True

    def test_unknown_package_fail_open(self):
        """包不在册（新增包/根散文件）= 不判——fail-open 是文档化作用域边界。"""
        passed, _ = _check("src/zephyr/brand_new_pkg/holder.py", "D_GOV_ENFORCEMENT")
        assert passed is True, "包不在册应 fail-open 不判（误伤代价高于漏拦）"

    def test_fake_domain_fk_behavior_unchanged(self):
        passed, detail = _check("src/zephyr/trading/whatever.py", "D_NOT_A_REAL_DOMAIN")
        assert passed is False
        assert "不在 functional_domain_registry.yaml" in detail
