# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.risk_mitigator
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/risk/test_risk_mitigator.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_risk_mitigator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""R1-R45全量风险缓解执行器 — 逐条检查缓解措施 + mitigation_tracker.yaml.

职责：
  - 逐条遍历 R1-R45 风险项
  - 检查对应的缓解代码块是否存在 -> mitigation_status
  - 生成 mitigation_tracker.yaml
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import yaml


@dataclass
class RiskMitigation:
    risk_id: str = ""
    title: str = ""
    module: str = ""
    status: str = "pending"
    evidence: str = ""
    verified_at: str = ""


class RiskMitigator:
    """R1-R45风险缓解执行器."""

    _RISKS: dict[str, dict] = {
        "R01": {"title": "项目规模>5000行", "module": "config.py"},
        "R02": {"title": "test_coverage<20%", "module": "behavioral_sampler.py"},
        "R03": {"title": "pyproject.toml缺失", "module": "pyproject.toml"},
        "R04": {"title": "ZephyrAlpha导入险", "module": "function_discovery.py"},
        "R05": {"title": "引擎修复后崩溃", "module": "atomic_fixer.py"},
        "R06": {"title": "pre-commit未部署", "module": "verify_dedup.py"},
        "R07": {"title": "去回归执混乱", "module": "decision_auditor.py"},
        "R08": {"title": "导入路径混乱", "module": "import_surface_tracker.py"},
        "R09": {"title": "修复后AI覆盖", "module": "codegen_guard.py"},
        "R10": {"title": "门禁不执行", "module": "verify_dedup.py"},
        "R11": {"title": "R2 Manifest依赖", "module": "recovery_manifest_writer.py"},
        "R12": {"title": "行为异常3种混合", "module": "behavioral_trust_checker.py"},
        "R13": {"title": "dangerous热迁", "module": "cross_boundary.py"},
        "R14": {"title": "频发大pattern", "module": "report.py"},
        "R15": {"title": "重复债务指数上升", "module": "debt_projector.py"},
        "R16": {"title": "Litigation需求", "module": "decision_auditor.py"},
        "R17": {"title": "CLI启动失败", "module": "config.py"},
        "R18": {"title": "VS Code干扰", "module": ".vscode/settings.json"},
        "R19": {"title": "修复混乱无回滚", "module": "atomic_fixer.py"},
        "R20": {"title": "常见误报", "module": "policy_tree_validator.py"},
        "R21": {"title": "config.py被误触", "module": "test_config.py"},
        "R22": {"title": "项目初始化散乱", "module": "__init__.py"},
        "R23": {"title": "Git Hook损坏", "module": "verify_dedup.py"},
        "R24": {"title": "文档分析滞后", "module": "contract_consistency_checker.py"},
        "R25": {"title": "格式化冲突", "module": "pre-commit-config"},
        "R26": {"title": "静态分析失控", "module": "ast_comparator.py"},
        "R27": {"title": "CI链条混沌", "module": "phase_executor.py"},
        "R28": {"title": "数据拷贝进出混淆", "module": "symbol_index.py"},
        "R29": {"title": "自测试不足", "module": "test_self_scan_integrity.py"},
        "R30": {"title": "CLI失败panic", "module": "cli.py"},
        "R31": {"title": "开源许可证", "module": "license_check.py"},
        "R32": {"title": "513代码健康度", "module": "health-monitor.py"},
        "R33": {"title": "每月SAS班车", "module": "simplicity_auditor.py"},
        "R34": {"title": "修复时丢参数", "module": "behavioral_sampler.py"},
        "R35": {"title": "修复行为出乎OC", "module": "canary_register.py"},
        "R36": {"title": "大型防御攻击", "module": "monoculture_guard.py"},
        "R37": {"title": "超出上班时间崩溃", "module": "atomic_fixer.py"},
        "R38": {"title": "两空间互锁", "module": "multi_session_state.py"},
        "R39": {"title": "代码搜索索引", "module": "symbol_index.py"},
        "R40": {"title": "不建新区新new", "module": "function_discovery.py"},
        "R41": {"title": "引擎被限速", "module": "simplicity_auditor.py"},
        "R42": {"title": "semgrep规则审计", "module": "ast_comparator.py"},
        "R43": {"title": "缺乏impact评估", "module": "monoculture_guard.py"},
        "R44": {"title": "阴井暗道复尔", "module": "temporal_drift_tracker.py"},
        "R45": {"title": "conventional_comment", "module": "verify_dedup.py"},
    }

    def audit_all(self, package_dir: str | Path | None = None) -> list[RiskMitigation]:
        """审计所有45个风险项——检查对应模块是否存在."""
        if package_dir is None:
            package_dir = Path("src/zephyr/testing/code_dedup")
        pkg = Path(package_dir)

        results: list[RiskMitigation] = []
        for risk_id in sorted(self._RISKS.keys(), key=lambda x: int(x[1:])):
            info = self._RISKS[risk_id]
            module_name = info["module"]

            path = pkg / module_name if module_name.endswith(".py") else module_name

            if module_name.endswith(".toml") or module_name.startswith("."):
                path = Path(module_name)
                status = "verified" if path.exists() else "pending"
            elif module_name.endswith(".py"):
                status = "verified" if (pkg / module_name).exists() else "pending"
            else:
                status = "verified" if (pkg / module_name).exists() else "pending"

            results.append(
                RiskMitigation(
                    risk_id=risk_id,
                    title=info["title"],
                    module=module_name,
                    status=status,
                    evidence=f"Module {module_name} {'exists' if status == 'verified' else 'not found'}",
                )
            )

        return results

    def generate_tracker(self, output_path: str | Path | None = None) -> dict:
        """生成 mitigation_tracker.yaml."""
        if output_path is None:
            output_path = Path("data/cache/mitigation_tracker.yaml")
        path = Path(output_path)

        results = self.audit_all()

        verified = sum(1 for r in results if r.status == "verified")
        total = len(results)

        data = {
            "version": "1.0.0",
            "generated_at": datetime.now(UTC).isoformat(),
            "summary": f"{verified}/{total} risks mitigated ({verified / total * 100:.0f}%)",
            "risks": [
                {
                    "risk_id": r.risk_id,
                    "title": r.title,
                    "module": r.module,
                    "status": r.status,
                    "evidence": r.evidence,
                }
                for r in results
            ],
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.dump(data, allow_unicode=True, default_flow_style=False),
            encoding="utf-8",
        )

        return data
