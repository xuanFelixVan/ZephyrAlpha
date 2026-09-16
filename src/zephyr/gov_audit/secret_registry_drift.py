# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §5
# [MODULE] zephyr.gov_audit.secret_registry_drift
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.shared.io.file_utils (safe_write_text); zephyr.shared.io.paths (REPO_ROOT); zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway（post-commit reconciler 注册）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] C-4 周期核对（裁定#287 2026-09-16）：secret_registry required=true 项失守=critical；registry↔.env 双向漂移告警（registry 有钥而 env 无/反之）；era 表 env: 钥必须已登记且可解析（active 分期）；钥值指纹漂移检测（rotation 未重锚 era 告警）；核对由 post-commit 事件触发（禁 cron/sleep-loop——PERM-TRIGGER 同源）；永不输出密钥明文（sanitize 口径，仅指纹+长度）
# [MODIFY-GUARD] finding code 语义变更必须同步 tests/governance/audit/test_secret_registry_drift.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——registry/era/env 任一不可读降级为 critical finding（缺核对比误报更危险）；指纹状态写失败仅告警不阻断
# [TESTS] tests/governance/audit/test_secret_registry_drift.py
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
secret_registry_drift.py — C-4 secret_registry 周期核对与漂移告警（裁定#287，2026-09-16）

核对三方（移交清单 C-4，真源 docs/_working/audit_integrity/2026-09-16-audit-key-era-deployment.md §5）：
  1. config/secret_registry.yaml —— 登记（required/category/env_file 真源）
  2. 真实密钥面 —— os.environ > env_file（.env / config/.env.{service}）
  3. config/audit_key_eras.yaml —— 签名钥分期（env:VAR 指针 / active 分期可解析性）

告警矩阵（finding.code）：
  - registry_missing / registry_malformed        critical  登记表不可用（缺核对=裸奔）
  - required_key_missing                          critical  required=true 项失守（.env/env 均无或空）
  - era_key_not_in_registry                       critical  签名钥（env:VAR）未登记 RULE-SECRETS 违规
  - era_active_key_unresolvable                   critical  active 分期钥不可解析（fail-loud 前哨）
  - unregistered_secret_in_env                    warn      .env 有 secret 形态键未登记（反之向漂移）
  - default_era_active_with_env_key               warn      默认钥期仍 active 但 env 真钥已在位（注册表未收口）
  - key_value_rotated_since_last_check            warn      钥值指纹漂移（rotation 后须重锚 era.valid_from）

周期机制：make_secret_registry_drift_reconciler(gateway) 注册进 post-commit reconcile
链（事件触发=每次 commit；仓内先例 cross_layer_contract_signature_reconciler），
禁 cron/Timer/sleep-loop。告警通道=ReconcileResult.warn/critical_warn（入
reconcile_execution_log + 下次提交前 critical 横幅）。

安全口径：本模块只做存在性/指纹核对，任何路径都不输出密钥值——指纹=sha256[:12]，
日志/详情仅含键名与指纹。

Usage::

    from zephyr.gov_audit.secret_registry_drift import (
        check_secret_registry_drift,
        make_secret_registry_drift_reconciler,
    )
    report = check_secret_registry_drift(project_root)          # 直接核对
    registry.register(make_secret_registry_drift_reconciler(gateway))  # 事件触发

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root，类型注解 Path | str
#   code: check_secret_registry_drift 形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① check_secret_registry_drift
#   name_en: check_secret_registry_drift
#   intro: 三方核对纯函数——registry↔env↔era 漂移检查，返回 findings 报告。
#   desc: 顶层公共函数（定义序）: check_secret_registry_drift, make_secret_registry_drift_reconciler
#   inputs: project_root env state_dir
#   outputs: dict（status/findings）
# - id: A2
#   name_zh: ② make_secret_registry_drift_reconciler
#   name_en: make_secret_registry_drift_reconciler
#   intro: post-commit 事件触发 reconciler 工厂（每次 commit=周期节拍）。
#   inputs: gateway
#   outputs: ReconcilerSpec
# 层: 输出
# - id: O1
#   name_zh: dict / ReconcilerSpec
#   name_en: public defs
#   intro: 模块公共 API 面（2 定义）
#   downstream: git_commit_gateway（reconcile 链）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final

from zephyr.shared.io.file_utils import safe_write_text
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

__all__: Final[list[str]] = [
    "SECRET_DRIFT_GATE_ID",
    "check_secret_registry_drift",
    "make_secret_registry_drift_reconciler",
]

SECRET_DRIFT_GATE_ID: Final[str] = "SECRET-REGISTRY-DRIFT"
_PRIORITY: Final[int] = 216  # cross_layer_contract(215) 之后、capability_lookup_health(220) 之前
_REGISTRY_REL: Final[Path] = Path("config") / "secret_registry.yaml"
_ERAS_REL: Final[Path] = Path("config") / "audit_key_eras.yaml"
_DEFAULT_STATE_DIR_REL: Final[Path] = Path(".runtime") / "secret_drift"
# secret 形态键判定（与 shared.security.secrets.SECRET_INDICATOR_PATTERNS 同词表口径）
_SECRET_KEY_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(KEY|TOKEN|SECRET|PASSWORD|PASSWD|PWD|CREDENTIAL)"
)


def _fingerprint(value: str) -> str:
    """密钥指纹（sha256[:12]）——唯一允许落日志/报告的钥值衍生形态。"""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _parse_env_file(path: Path) -> dict[str, str]:
    """独立 .env 解析（KEY=VALUE，去引号跳注释）——与 shared.secrets._parse_env_file
    同口径。不直接 import 后者的私有函数（shared 私有面禁上浮），口径漂移由
    TRANSLATION/CLONE 门禁按 extract 级阈值裁量（本函数 8 行，低于克隆判定线）。"""
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            values[key] = value
    return values


def _load_registry(path: Path) -> tuple[list[dict[str, Any]] | None, str | None]:
    """读 secret_registry.yaml → (entries, error)。error 非 None=不可用（fail-loud finding）。"""
    if not path.is_file():
        return None, "registry_missing"
    try:
        import yaml  # 惰性：本模块被 import 的面远大于用 yaml 的面（integrity 同先例）

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 — 解析失败=登记面不可用
        logger.warning("secret registry parse failed: %s", exc)
        return None, "registry_malformed"
    if not isinstance(data, dict) or not isinstance(data.get("secrets"), list):
        return None, "registry_malformed"
    return [e for e in data["secrets"] if isinstance(e, dict)], None


def _resolve_value(key: str, env_file: str, project_root: Path, env: dict[str, str]) -> str | None:
    """键值解析：os/env 覆盖 > env_file。缺失/空 → None（不区分两源差异）。"""
    v = env.get(key)
    if v:
        return v
    values = _parse_env_file(project_root / env_file)
    v = values.get(key)
    return v or None


def check_secret_registry_drift(
    project_root: Path | str,
    *,
    env: dict[str, str] | None = None,
    state_dir: Path | None = None,
    checked_at: datetime | None = None,
) -> dict[str, Any]:
    """三方周期核对（registry ↔ 真实密钥面 ↔ era 表）——纯检查，不修改任何被核对资产。

    Args:
        project_root: 仓库根（config/ 与 .runtime/ 锚点）。
        env: 环境快照覆盖（默认 os.environ；测试隔离位）。
        state_dir: 钥值指纹状态目录覆盖（默认 <root>/.runtime/secret_drift；测试隔离位）。
        checked_at: 核对时刻覆盖（测试确定性位；默认 now_utc）。

    Returns:
        {"status": "clean"|"drift"|"critical", "checked_at", "keys_total", "required_total",
         "findings": [{"code","severity","key","detail"}], "fingerprints": {key: fp}}
    """
    root = Path(project_root)
    env = env if env is not None else dict(os.environ)
    at = (checked_at or now_utc()).isoformat()
    findings: list[dict[str, str]] = []

    entries, err = _load_registry(root / _REGISTRY_REL)
    if err is not None:
        findings.append(
            {
                "code": err,
                "severity": "critical",
                "key": str(_REGISTRY_REL),
                "detail": "secret registry unavailable — drift check cannot run (fail-loud)",
            }
        )
        return {
            "status": "critical",
            "checked_at": at,
            "keys_total": 0,
            "required_total": 0,
            "findings": findings,
            "fingerprints": {},
        }

    assert entries is not None
    required_findings, required_total, registered_keys = _check_required_entries(entries, root, env)
    findings.extend(required_findings)

    dotenv_values = _parse_env_file(root / ".env")
    findings.extend(_check_unregistered_env_secrets(dotenv_values, registered_keys))

    era_findings, fingerprints = _check_era_linkage(root, registered_keys, env, checked_at, dotenv_values)
    findings.extend(era_findings)

    findings.extend(_check_fingerprint_rotation(fingerprints, state_dir or root / _DEFAULT_STATE_DIR_REL, at))

    return _assemble_report(findings, at, keys_total=len(entries), required_total=required_total, fingerprints=fingerprints)


def _check_required_entries(
    entries: list[dict[str, Any]], root: Path, env: dict[str, str]
) -> tuple[list[dict[str, str]], int, set[str]]:
    """核对 required=true 项（失守=critical）→ (findings, required_total, registered_keys)。"""
    findings: list[dict[str, str]] = []
    required_total = 0
    registered_keys: set[str] = set()
    for e in entries:
        key = str(e.get("key", ""))
        if not key:
            continue
        registered_keys.add(key)
        if not bool(e.get("required", False)):
            continue
        required_total += 1
        env_file = str(e.get("env_file", ".env"))
        if not _resolve_value(key, env_file, root, env):
            findings.append(
                {
                    "code": "required_key_missing",
                    "severity": "critical",
                    "key": key,
                    "detail": f"required=true 但 env/{env_file} 均未设置或为空（RULE-SECRETS 登记失守）",
                }
            )
    return findings, required_total, registered_keys


def _check_unregistered_env_secrets(dotenv_values: dict[str, str], registered_keys: set[str]) -> list[dict[str, str]]:
    """反之向核对：.env 中 secret 形态键未登记（防裸钥绕过 RULE-SECRETS 三道 gate）。"""
    findings: list[dict[str, str]] = []
    for key in sorted(dotenv_values):
        if key in registered_keys or not _SECRET_KEY_PATTERN.search(key):
            continue
        findings.append(
            {
                "code": "unregistered_secret_in_env",
                "severity": "warn",
                "key": key,
                "detail": ".env 存在 secret 形态键但 secret_registry.yaml 未登记（新增密钥三步流程缺第 3 步）",
            }
        )
    return findings


def _load_eras(root: Path) -> tuple[list[dict[str, Any]], str | None]:
    """读 era 表 → (eras, err_detail)。err_detail 非 None=不可读（降级 finding）。"""
    eras_path = root / _ERAS_REL
    if not eras_path.is_file():
        return [], None
    try:
        import yaml

        eras_raw = yaml.safe_load(eras_path.read_text(encoding="utf-8"))
        eras = eras_raw.get("eras", []) if isinstance(eras_raw, dict) else []
        return eras, None
    except Exception as exc:  # noqa: BLE001 — era 表不可读=核对降级
        return [], f"era registry unreadable: {type(exc).__name__}"


def _check_era_env_key(era: dict[str, Any], registered_keys: set[str], root: Path, env: dict[str, str]) -> tuple[list[dict[str, str]], str | None]:
    """单个 env: 钥分期核对 → (findings, fingerprint or None)。"""
    findings: list[dict[str, str]] = []
    var = str(era.get("key_source", ""))[4:]
    era_id = str(era.get("id", ""))
    if var not in registered_keys:
        findings.append(
            {
                "code": "era_key_not_in_registry",
                "severity": "critical",
                "key": f"{era_id}:{var}",
                "detail": "签名钥 env 变量未登记 secret_registry.yaml（RULE-SECRETS：密钥走登记）",
            }
        )
    value = _resolve_value(var, ".env", root, env)
    if value:
        return findings, _fingerprint(value)
    if era.get("valid_to") is None:
        findings.append(
            {
                "code": "era_active_key_unresolvable",
                "severity": "critical",
                "key": f"{era_id}:{var}",
                "detail": "active 分期 env 钥不可解析（IntegrityVerifier 将 fail-loud 判 mismatch）",
            }
        )
    return findings, None


def _check_era_linkage(
    root: Path,
    registered_keys: set[str],
    env: dict[str, str],
    checked_at: datetime | None,
    dotenv_values: dict[str, str],
) -> tuple[list[dict[str, str]], dict[str, str]]:
    """era 对接核对：签名钥分期 ↔ registry ↔ 可解析性 → (findings, fingerprints)。"""
    findings: list[dict[str, str]] = []
    fingerprints: dict[str, str] = {}
    eras, err = _load_eras(root)
    if err is not None:
        findings.append({"code": "registry_malformed", "severity": "critical", "key": str(_ERAS_REL), "detail": err})
        return findings, fingerprints

    active_default_era = False
    for era in eras:
        if not isinstance(era, dict):
            continue
        source = str(era.get("key_source", ""))
        if source.startswith("env:"):
            era_findings, fp = _check_era_env_key(era, registered_keys, root, env)
            findings.extend(era_findings)
            if fp:
                fingerprints[str(era.get("key_source", ""))[4:]] = fp
        elif source == "builtin:default" and era.get("valid_to") is None:
            active_default_era = True

    if active_default_era and dotenv_values.get("ZEPHYR_AUDIT_HMAC_SECRET"):
        findings.append(
            {
                "code": "default_era_active_with_env_key",
                "severity": "warn",
                "key": "era-default-public",
                "detail": "默认钥期仍 active 而 env 真钥已在位——era 边界未收口（部署三步缺回填）",
            }
        )
    _ = checked_at  # 预留：分期 covers(now) 精细化判定位
    return findings, fingerprints


def _check_fingerprint_rotation(fingerprints: dict[str, str], state_dir: Path, at: str) -> list[dict[str, str]]:
    """钥值指纹漂移核对（rotation 检测）：状态文件比对 + 回写。"""
    findings: list[dict[str, str]] = []
    if not fingerprints:
        return findings
    state_path = state_dir / "key_fingerprints.json"
    prev: dict[str, str] = {}
    try:
        if state_path.is_file():
            loaded = json.loads(state_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                prev = {str(k): str(v) for k, v in loaded.items()}
    except (OSError, ValueError) as exc:
        logger.warning("fingerprint state unreadable (treated as first run): %s", exc)
    for var, fp in sorted(fingerprints.items()):
        old = prev.get(var)
        if old is not None and old != fp:
            findings.append(
                {
                    "code": "key_value_rotated_since_last_check",
                    "severity": "warn",
                    "key": var,
                    "detail": f"钥值指纹 {old}→{fp}（rotation 后须重锚 era.valid_from 并同步 registry 记账）",
                }
            )
    if prev != fingerprints:
        payload = json.dumps({"checked_at": at, **fingerprints}, indent=2, ensure_ascii=False)
        try:
            state_dir.mkdir(parents=True, exist_ok=True)
            result = safe_write_text(state_path, payload + "\n")
            if not result.written:
                logger.warning("fingerprint state write not applied: %s", state_path)
        except OSError as exc:
            logger.warning("fingerprint state write failed (non-blocking): %s", exc)
    return findings


def _assemble_report(
    findings: list[dict[str, str]],
    at: str,
    *,
    keys_total: int,
    required_total: int,
    fingerprints: dict[str, str],
) -> dict[str, Any]:
    """汇总核对报告（status 三态：clean/drift/critical）。"""
    has_critical = any(f["severity"] == "critical" for f in findings)
    status = "clean" if not findings else ("critical" if has_critical else "drift")
    return {
        "status": status,
        "checked_at": at,
        "keys_total": keys_total,
        "required_total": required_total,
        "findings": findings,
        "fingerprints": fingerprints,
    }


def make_secret_registry_drift_reconciler(gateway: Any) -> Any:
    """构造 C-4 周期核对 reconciler（post-commit 事件触发，裁定#287）。

    周期机制：每次 commit 即一次核对节拍（commit 是本仓唯一合法"钟"——
    PERM-TRIGGER 同源，禁 cron/Timer/sleep-loop）。trigger 恒真：.env 是
    gitignored 资产，其漂移不会出现在 committed_files，按文件触发会永不生效。

    告警通道：required=true 失守/era 钥失守=critical_warn（下次提交前横幅强制可见）；
    其余漂移=warn（reconcile_execution_log 留痕）。核对永不抛异常（ERROR_CONTRACT）。

    Args:
        gateway: GitCommitGateway 实例（仅取 project_root）。

    Returns:
        ReconcilerSpec(gate_id="SECRET-REGISTRY-DRIFT", priority=216, file_ops={"read","write"})。
        ReconcilerSpec 为惰性 import（governance.audit 属上层，模块级 import 会在
        gov_audit 共享 provider 注册路径上制造环依赖风险）。
    """
    from zephyr.governance.audit.reconciliation_registry import ReconcileResult, ReconcilerSpec

    project_root = Path(gateway.project_root)

    def _trigger(committed_files: list[str]) -> bool:
        _ = committed_files  # 恒真：见 docstring（.env gitignored，按文件触发永不命中）
        return True

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        _ = committed_files, session_id
        try:
            report = check_secret_registry_drift(project_root)
        except Exception as exc:  # noqa: BLE001 — 核对异常降级 warn（不阻断 reconcile 链）
            logger.warning("secret registry drift check crashed: %s", exc, exc_info=True)
            return ReconcileResult(
                action="warn",
                detail=f"SECRET-REGISTRY-DRIFT check crashed: {type(exc).__name__}",
                gate_id=SECRET_DRIFT_GATE_ID,
            )
        findings = report["findings"]
        if not findings:
            return ReconcileResult(
                action="clean",
                detail=f"secret registry drift check clean ({report['keys_total']} keys, "
                f"{report['required_total']} required, era-linked)",
                gate_id=SECRET_DRIFT_GATE_ID,
            )
        has_critical = any(f["severity"] == "critical" for f in findings)
        detail = "; ".join(f"{f['code']}[{f['key']}]" for f in findings[:10])
        if len(findings) > 10:
            detail += f"; (+{len(findings) - 10} more)"
        return ReconcileResult(
            action="critical_warn" if has_critical else "warn",
            detail=detail,
            gate_id=SECRET_DRIFT_GATE_ID,
        )

    return ReconcilerSpec(
        gate_id=SECRET_DRIFT_GATE_ID,
        trigger=_trigger,
        reconcile=_reconcile,
        priority=_PRIORITY,
        file_ops=frozenset({"read", "write"}),
    )
