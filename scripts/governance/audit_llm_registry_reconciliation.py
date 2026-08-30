# [BLUEPRINT] MOD-GOVERNANCE | scripts/governance/audit_llm_registry_reconciliation.py | §reconcile
# [MODULE] scripts.governance.audit_llm_registry_reconciliation
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.constants; zephyr.orchestrator.governance.model_registry(MOD-INF-039); config/model_pricing.yaml(MOD-INF-002); docs/01_policies_and_standards/_registry/catalogs/model_registry.yaml(REG-ML-001)
# [CONSUMERS] 人工/CI/commit gate 挂载（10号文 §4 Phase 3.1）; tests/governance/test_llm_registry_reconciliation.py
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 纯对账不改写任何注册表/配置（不写 yaml 纪律）; fail-closed 于结构非法，放行于已登记已知偏差; 比对口径=docs/_archive/2026-08-22-llm-registry-reconciliation.md §一/§二 比对矩阵
# [MODIFY-GUARD] KNOWN_DEVIATIONS / EXPECTED_PRICES 的变更须附 Owner 裁定引用
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=PASS（零新增漂移）, exit 1=FINDINGS（检出未登记漂移）, exit 2=ERROR（源文件缺失/结构非法）
# [TESTS] tests/governance/test_llm_registry_reconciliation.py
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""audit_llm_registry_reconciliation.py — LLM 模型注册三向对账（10号文 §4 Phase 3.1）。

三向比对（10号文 §3.4 收敛裁定：三处收敛对账，不建第四套）：
  A = MOD-INF-039 运行时治理 dict（src/zephyr/orchestrator/governance/model_registry.py）
  B = model_pricing.yaml 定价真源（config/model_pricing.yaml，MOD-INF-002 锚定）
  D = REG-ML-001 ML 训练产物登记（docs/01_policies_and_standards/_registry/catalogs/model_registry.yaml）

校验维度：
  1. 模型名覆盖：A 有 B 无 / B 有 A 无（名称漂移经此成对暴露）。
  2. tier/结构：A 侧 tier 受控词表 + token_limit 正整数；B 侧价格非负数值 + provider 非空。
  3. 价格基线：B 侧每条价格须等于 EXPECTED_PRICES 快照（2026-08-22 对账报告 §二
     校准批钉死，改价=Owner 动作须同步快照——人为改一处价格即检出）。
  4. §3.4 治理字段（D 侧）：staging/production 条目必填 training_data_hash（64-hex）+
     版本四元组（version+code_hash+param_hash+training_data_hash）完整 + audit_hash_chain
     非空；任意阶段条目四元组字段缺一即判漂移。
  5. D 侧账实一致：entry_count == 实际条目数（对账报告 §2.3 口径）。

已知偏差登记（对账报告 §2.1/§2.2 归属裁定）：命中的发现不判漂移；未命中已知偏差
的新发现 = 新增漂移，exit 1。已登记但不再出现的偏差打印 STALE 提醒（不阻断，
防止上游已修复时误报；登记清单 hygiene 由人审跟进）。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Final

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import (  # noqa: E402
    CONFIG_DIR,
    EXIT_ERROR,
    EXIT_FINDINGS,
    EXIT_PASS,
    REPO_ROOT,
)
from _shared.encoding import ensure_utf8_stdout  # noqa: E402

ensure_utf8_stdout()

A_REGISTRY_PATH: Final[Path] = REPO_ROOT / "src" / "zephyr" / "orchestrator" / "governance" / "model_registry.py"
B_PRICING_PATH: Final[Path] = CONFIG_DIR / "model_pricing.yaml"
D_REGISTRY_PATH: Final[Path] = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "model_registry.yaml"
)

TIER_VOCAB: Final[frozenset[str]] = frozenset({"economy", "standard", "premium"})
_SHA256_RE: Final = re.compile(r"^[0-9a-f]{64}$")
# 版本四元组（10号文 §3.4）：语义化版本号 + code_hash + param_hash + training_data_hash
_VERSION_QUADRUPLE_FIELDS: Final[tuple[str, ...]] = (
    "version",
    "code_hash",
    "param_hash",
    "training_data_hash",
)
_GOV_REQUIRED_STAGES: Final[frozenset[str]] = frozenset({"staging", "production"})
_D_REQUIRED_KEYS: Final[tuple[str, ...]] = (
    "model_id",
    "name",
    "promotion_stage",
    "version",
    "status",
)

# 价格基线快照（元/千 token）——真源钉死自 2026-08-22 对账报告 §二矩阵 +
# config/model_pricing.yaml 2026_08_22 校准批（tracker #254，Owner 已批准）。
# 改价 = Owner 动作：先改本快照（附裁定引用）再改 yaml，顺序颠倒即被本对账检出。
EXPECTED_PRICES: Final[dict[str, tuple[float, float]]] = {
    "glm-4.5-free": (0.0, 0.0),
    "glm-4-plus": (0.007, 0.007),
    "glm-4-flash": (0.001, 0.001),
    "deepseek-chat-free": (0.0, 0.0),
    "deepseek-chat": (0.003, 0.009),
    "deepseek-reasoner": (0.003, 0.009),
    "qwen-flash": (0.00015, 0.0015),
    "gpt-4o-mini": (0.003, 0.015),
    "gpt-4o": (0.015, 0.060),
    "claude-3-5-haiku": (0.004, 0.020),
    "claude-3-5-sonnet": (0.020, 0.080),
}

# 已知偏差登记（对账报告 §2.1/§2.2 归属裁定逐条落地，(check, subject) 二元组）
KNOWN_DEVIATIONS: Final[dict[tuple[str, str], str]] = {
    ("A_NO_PRICING", "claude-opus-4"): "A 超前登记（设计态预留），启用前须先补 B（Owner 动作）",
    ("A_NO_PRICING", "gpt-5.2"): "A 超前登记（设计态预留），同 claude-opus-4 裁定",
    ("A_NO_PRICING", "claude-haiku-3.5"): "名称漂移：B 侧为 Anthropic 官方命名 claude-3-5-haiku，GP1 统一",
    ("B_UNREGISTERED", "claude-3-5-haiku"): "名称漂移对侧：A 侧别名体 claude-haiku-3.5 滞后，GP1 统一",
    ("B_UNREGISTERED", "glm-4-flash"): "A 滞后：降级链第二环未入治理登记（Owner/GP1 补登）",
    ("B_UNREGISTERED", "glm-4-plus"): "B 单方登记（可用非默认），一致登记非漂移",
    ("B_UNREGISTERED", "glm-4.5-free"): "B 单方登记（免费档），一致登记非漂移",
    ("B_UNREGISTERED", "deepseek-chat-free"): "B 单方登记（免费档），一致登记非漂移",
    ("B_UNREGISTERED", "gpt-4o"): "B 单方登记（可用非默认），一致登记非漂移",
    ("B_UNREGISTERED", "claude-3-5-sonnet"): "B 单方登记；C 侧 claude 默认模型成本错配已另案登记 GP1",
    ("B_UNREGISTERED", "qwen-flash"): "B 单方登记（百炼备用通道，2026-08-22 校准批新增），A 待 GP1 补登",
    (
        "PROVIDER_LABEL_MISMATCH",
        "gpt-4o-mini",
    ): "带理由已知偏差：A 记供应商族名 openai，B 记通道实证 openai_azure（Azure 代理），价以 B 为准",
}


def _finding(check: str, subject: str, detail: str) -> dict[str, str]:
    return {"check": check, "subject": subject, "detail": detail}


def check_a_structure(a_models: dict[str, Any]) -> list[dict[str, str]]:
    """A 侧（MOD-INF-039）结构校验：provider 非空 + tier 受控词表 + token_limit 正整数。"""
    findings: list[dict[str, str]] = []
    for name, cfg in a_models.items():
        if not isinstance(cfg, dict):
            findings.append(_finding("A_STRUCTURE", str(name), "条目非 mapping"))
            continue
        if not cfg.get("provider"):
            findings.append(_finding("A_STRUCTURE", str(name), "provider 缺失/为空"))
        tier = str(cfg.get("tier", ""))
        if tier not in TIER_VOCAB:
            findings.append(_finding("A_STRUCTURE", str(name), f"tier={tier!r} 不在受控词表 {sorted(TIER_VOCAB)}"))
        token_limit = cfg.get("token_limit")
        if not isinstance(token_limit, int) or isinstance(token_limit, bool) or token_limit <= 0:
            findings.append(_finding("A_STRUCTURE", str(name), f"token_limit={token_limit!r} 非正整数"))
    return findings


def check_b_structure_and_prices(b_pricing: dict[str, Any]) -> list[dict[str, str]]:
    """B 侧（model_pricing.yaml）结构校验 + 价格基线快照比对。"""
    findings: list[dict[str, str]] = []
    for name, cfg in b_pricing.items():
        if not isinstance(cfg, dict):
            findings.append(_finding("B_STRUCTURE", str(name), "条目非 mapping"))
            continue
        for field in ("input_price", "output_price"):
            v = cfg.get(field)
            if not isinstance(v, int | float) or isinstance(v, bool) or v < 0:
                findings.append(_finding("B_STRUCTURE", str(name), f"{field}={v!r} 非非负数值"))
        if not cfg.get("provider"):
            findings.append(_finding("B_STRUCTURE", str(name), "provider 缺失/为空"))
        if not cfg.get("updated_at"):
            findings.append(_finding("B_STRUCTURE", str(name), "updated_at 缺失/为空"))

        expected = EXPECTED_PRICES.get(str(name))
        if expected is None:
            findings.append(
                _finding("B_UNKNOWN_MODEL_BASELINE", str(name), "价格基线快照未覆盖该模型（新增须先钉基线）")
            )
        elif isinstance(cfg, dict):
            got = (float(cfg.get("input_price", -1)), float(cfg.get("output_price", -1)))
            if got != expected:
                findings.append(
                    _finding(
                        "PRICE_BASELINE_DRIFT",
                        str(name),
                        f"价格漂移: 实际 in/out={got} != 基线={expected}（改价须 Owner 裁定并同步快照）",
                    )
                )
    return findings


def check_ab_coverage(a_models: dict[str, Any], b_pricing: dict[str, Any]) -> list[dict[str, str]]:
    """A↔B 名称覆盖 + 双侧命中条目的 provider 标签一致性。"""
    findings: list[dict[str, str]] = []
    for name in a_models:
        if name not in b_pricing:
            findings.append(_finding("A_NO_PRICING", str(name), "A 有登记 B 无定价条目"))
    for name in b_pricing:
        if name not in a_models:
            findings.append(_finding("B_UNREGISTERED", str(name), "B 有定价 A 无治理登记"))
    for name in set(a_models) & set(b_pricing):
        a_prov = str(a_models[name].get("provider", ""))
        b_prov = str(b_pricing[name].get("provider", ""))
        if a_prov and b_prov and a_prov != b_prov:
            findings.append(
                _finding("PROVIDER_LABEL_MISMATCH", str(name), f"provider 标签漂移: A={a_prov} vs B={b_prov}")
            )
    return findings


def check_d_governance(d_registry: dict[str, Any]) -> list[dict[str, str]]:
    """D 侧（REG-ML-001）§3.4 治理字段校验 + 账实一致。

    口径：staging/production 条目必填 training_data_hash（64-hex）+ 版本四元组完整
    + audit_hash_chain 非空；任意阶段条目四元组字段缺一即判漂移。
    """
    findings: list[dict[str, str]] = []
    models = d_registry.get("models")
    if not isinstance(models, list):
        return [_finding("D_STRUCTURE", "models", "models 缺失或非 list")]

    declared = d_registry.get("entry_count")
    if declared != len(models):
        findings.append(_finding("D_ENTRY_COUNT_MISMATCH", "entry_count", f"声明={declared} 实际={len(models)}"))

    for entry in models:
        if not isinstance(entry, dict):
            findings.append(_finding("D_STRUCTURE", "?", "条目非 mapping"))
            continue
        mid = str(entry.get("model_id", "?"))
        for key in _D_REQUIRED_KEYS:
            if not entry.get(key):
                findings.append(_finding("D_SCHEMA_MISSING", mid, f"必填字段 {key} 缺失/为空"))

        # 四元组完整性判定只数三个治理哈希字段——version 是基础 schema 字段（全条目常备），
        # 计入会把所有 candidate 误判为部分四元组（零误报口径）。
        present_hashes = [f for f in _VERSION_QUADRUPLE_FIELDS if f != "version" and entry.get(f)]
        stage = str(entry.get("promotion_stage", ""))
        if stage in _GOV_REQUIRED_STAGES:
            if len(present_hashes) != len(_VERSION_QUADRUPLE_FIELDS) - 1 or not entry.get("version"):
                missing = [f for f in _VERSION_QUADRUPLE_FIELDS if not entry.get(f)]
                findings.append(
                    _finding(
                        "D_GOV_REQUIRED_FOR_STAGE",
                        mid,
                        f"{stage} 条目版本四元组缺 {missing}（10号文 §3.4 必填）",
                    )
                )
            if not entry.get("audit_hash_chain"):
                findings.append(_finding("D_GOV_REQUIRED_FOR_STAGE", mid, f"{stage} 条目 audit_hash_chain 缺失/为空"))
        elif present_hashes and len(present_hashes) != len(_VERSION_QUADRUPLE_FIELDS) - 1:
            missing = [f for f in _VERSION_QUADRUPLE_FIELDS if f != "version" and not entry.get(f)]
            findings.append(_finding("D_GOV_QUADRUPLE_INCOMPLETE", mid, f"四元组缺一即判漂移: 缺 {missing}"))

        tdh = entry.get("training_data_hash")
        if tdh and not _SHA256_RE.match(str(tdh)):
            findings.append(_finding("D_GOV_HASH_FORMAT", mid, "training_data_hash 非 64 位小写 hex（SHA-256）"))
    return findings


def collect_findings(
    a_models: dict[str, Any],
    b_pricing: dict[str, Any],
    d_registry: dict[str, Any],
) -> list[dict[str, str]]:
    """三向比对主入口（纯函数，供 CLI 与测试共用）。"""
    return (
        check_a_structure(a_models)
        + check_b_structure_and_prices(b_pricing)
        + check_ab_coverage(a_models, b_pricing)
        + check_d_governance(d_registry)
    )


def classify_findings(
    findings: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[tuple[tuple[str, str], str]]]:
    """按 KNOWN_DEVIATIONS 分类为 (新增漂移, 已登记已知偏差, 已登记但未再出现)。"""
    new_drift: list[dict[str, str]] = []
    known: list[dict[str, str]] = []
    hit_keys: set[tuple[str, str]] = set()
    for f in findings:
        key = (f["check"], f["subject"])
        if key in KNOWN_DEVIATIONS:
            hit_keys.add(key)
            known.append({**f, "known_reason": KNOWN_DEVIATIONS[key]})
        else:
            new_drift.append(f)
    stale = [(k, v) for k, v in KNOWN_DEVIATIONS.items() if k not in hit_keys]
    return new_drift, known, stale


def _load_a_models() -> dict[str, Any]:
    src = str(REPO_ROOT / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    from zephyr.orchestrator.governance.model_registry import MODELS

    return dict(MODELS)


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"YAML 顶层必须是 mapping: {path}")
    return data


def _load_b_pricing() -> dict[str, Any]:
    raw = _load_yaml(B_PRICING_PATH)
    return {k: v for k, v in raw.items() if k != "module_id" and isinstance(v, dict)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="LLM 模型注册三向对账（10号文 §4 Phase 3.1）")
    parser.parse_args(argv)

    try:
        for p in (A_REGISTRY_PATH, B_PRICING_PATH, D_REGISTRY_PATH):
            if not p.exists():
                print(f"[ERROR] 源文件缺失: {p}", file=sys.stderr)
                return EXIT_ERROR
        a_models = _load_a_models()
        b_pricing = _load_b_pricing()
        d_registry = _load_yaml(D_REGISTRY_PATH)
    except Exception as exc:  # noqa: BLE001 — CLI 兜底，错误打印+退出码
        print(f"[ERROR] 源加载失败: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ERROR

    findings = collect_findings(a_models, b_pricing, d_registry)
    new_drift, known, stale = classify_findings(findings)

    print("=== LLM 模型注册三向对账（MOD-INF-039 ↔ model_pricing.yaml ↔ REG-ML-001）===")
    print(f"A 条目={len(a_models)} B 条目={len(b_pricing)} D 条目={len(d_registry.get('models') or [])}")
    print(f"发现总数={len(findings)} 新增漂移={len(new_drift)} 已登记已知偏差={len(known)}")

    for f in new_drift:
        print(f"[DRIFT] {f['check']} | {f['subject']} | {f['detail']}")
    for f in known:
        print(f"[KNOWN] {f['check']} | {f['subject']} | {f['known_reason']}")
    for (check, subject), reason in stale:
        print(f"[STALE] 已登记偏差未再出现（上游或已修复，待人审清理登记）: {check} | {subject} | {reason}")

    if new_drift:
        print(f"[FAIL] 检出 {len(new_drift)} 项未登记漂移", file=sys.stderr)
        return EXIT_FINDINGS
    print("[PASS] 零新增漂移（已知偏差全部命中登记）")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
