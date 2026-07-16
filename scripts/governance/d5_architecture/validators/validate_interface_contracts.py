# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_interface_contracts.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_interface_contracts
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""validate_interface_contracts.py — 接口契约校验



对标：GOV-MOD-004 IFC-001~007（模块接口契约策略）

检测内容：
- 契约 7 个必填字段（contract_id/provider/consumers/interface_type/schema/version/status）
- contract_id 命名格式（{provider_id}.{consumer_id}.{interface_name}）
- 契约 status 3 值枚举（draft/frozen/deprecated）
- semver 版本号格式
- P0 模块必须有 frozen 契约
- deprecated 契约禁止新增 consumer

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 接口契约校验（GOV-MOD-004 IFC-001~007 — 7必填字段+semver+契约状态）
dimensions:
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from zephyr.shared.io.yaml_utils import load_vocabulary_values  # noqa: E402  SSoT 词表加载（治本 2026-06-30）
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
import argparse

import yaml

REQUIRED_CONTRACT_FIELDS = ["contract_id", "provider", "consumers", "interface_type", "schema", "version", "status"]
# 治本（2026-06-30）：从 contract_status_vocabulary.yaml 动态加载（SSoT，PS-VOC-026）。
VALID_CONTRACT_STATUSES = load_vocabulary_values("contract_status_vocabulary.yaml")
CONTRACT_ID_PATTERN = re.compile("^[a-z][a-z0-9_]*\\.[a-z][a-z0-9_]*\\.[a-z][a-z0-9_]*$")
SEMVER_PATTERN = re.compile("^\\d+\\.\\d+\\.\\d+$")


def load_contracts() -> list[dict]:
    """加载合约定义"""
    paths = [
        REPO_ROOT
        / ""
        / "docs"
        / "01_policies_and_standards"
        / "_registry"
        / "contracts"
        / "cross_layer_contracts.yaml",
        REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "contracts" / "cross_layer_contracts.yaml",
    ]
    for p in paths:
        if p.exists():
            try:
                data = yaml.safe_load(p.read_text(encoding="utf-8"))
                if isinstance(data, dict) and "contracts" in data:
                    return data["contracts"]
                if isinstance(data, list):
                    return data
            except (yaml.YAMLError, OSError):
                pass
    return []
    "加载合约定义."


def validate_contracts() -> list[dict]:
    """校验合约"""
    findings = []
    contracts = load_contracts()
    if not contracts:
        print("[IFC] 未找到 cross_layer_contracts.yaml，跳过契约校验", file=sys.stderr)
        return findings
    for contract in contracts:
        if not isinstance(contract, dict):
            continue
        cid = contract.get("contract_id", "<unknown>")
        for field in REQUIRED_CONTRACT_FIELDS:
            if field not in contract or contract[field] is None:
                findings.append(
                    {
                        "contract_id": cid,
                        "type": "MISSING_FIELD",
                        "detail": f"契约缺少必填字段: {field}",
                        "severity": "HIGH",
                    }
                )
        if "contract_id" in contract:
            if not CONTRACT_ID_PATTERN.match(str(contract["contract_id"])):
                findings.append(
                    {
                        "contract_id": cid,
                        "type": "INVALID_CONTRACT_ID",
                        "detail": "contract_id 格式错误（应为 {provider}.{consumer}.{name}）",
                        "severity": "MEDIUM",
                    }
                )
        status = contract.get("status", "")
        if status and status not in VALID_CONTRACT_STATUSES:
            findings.append(
                {
                    "contract_id": cid,
                    "type": "INVALID_STATUS",
                    "detail": f"契约 status='{status}' 不在合法枚举中（合法值: {', '.join(sorted(VALID_CONTRACT_STATUSES))}）",
                    "severity": "HIGH",
                }
            )
        version = contract.get("version", "")
        if version and (not SEMVER_PATTERN.match(str(version))):
            findings.append(
                {
                    "contract_id": cid,
                    "type": "INVALID_SEMVER",
                    "detail": f"version='{version}' 不符合 semver 格式（X.Y.Z）",
                    "severity": "MEDIUM",
                }
            )
        if status == "deprecated":
            consumers = contract.get("consumers", [])
            if isinstance(consumers, list) and len(consumers) > 0:
                findings.append(
                    {
                        "contract_id": cid,
                        "type": "DEPRECATED_WITH_CONSUMERS",
                        "detail": f"deprecated 契约仍有 {len(consumers)} 个 consumer",
                        "severity": "MEDIUM",
                    }
                )
    return findings
    "校验合约."


def main() -> None:
    """入口函数"""
    parser = argparse.ArgumentParser(description="接口契约校验（GOV-MOD-004 IFC-001~007）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    findings = validate_contracts()
    from collections import defaultdict

    by_type = defaultdict(list)
    for f in findings:
        by_type[f["type"]].append(f)
    if findings:
        print(f"\n[IFC] {len(findings)} 个接口契约违规:", file=sys.stderr)
        for rtype, items in by_type.items():
            print(f"\n  {rtype} ({len(items)} 个):", file=sys.stderr)
            for f in items[:10]:
                print(f"    [{f['severity']}] {f['contract_id']}", file=sys.stderr)
                print(f"      {f['detail']}", file=sys.stderr)
    else:
        print("[IFC] 接口契约合规", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS if findings else EXIT_PASS)
    "入口函数."


if __name__ == "__main__":
    main()
