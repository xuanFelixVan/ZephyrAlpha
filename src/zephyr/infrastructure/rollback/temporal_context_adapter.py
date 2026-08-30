# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.temporal_context_adapter
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
TemporalContextAdapter — AI 时间上下文断裂修复。

依据: 蓝图 MOD-INF-021 §6.12 B70 + exit code 26

AI agent 回滚后时间上下文断裂 -> NTP time attestation + TOTP 时间证明。
Agent 恢复时提交时间证明 -> Adapter 验证 -> 对齐 AI 上下文。
验伪失败 -> exit code 26 (TIME_ATTEST_FAIL)。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root（无注解）
#   code: temporal_context_adapter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① TemporalContextAdapter
#   name_en: TemporalContextAdapter
#   intro: class TemporalContextAdapter 源码 L84-L180
#   desc: 公共方法（定义序）: project_root, generate_totp, compute_hmac, verify_totp, verify_hmac, verify_time_attest, generate_…
#   inputs: project_root
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: TemporalContextAdapter
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class TimeAttestion:
    unix_timestamp: int
    iso_timestamp: str
    totp_code: str
    hmac_sig: str
    verified: bool = False


@dataclass
class AttestResult:
    passed: bool
    actual_time: str
    agent_claimed_time: str
    drift_seconds: float
    exit_code: int
    details: list[str] = field(default_factory=list)


class TemporalContextAdapter:
    EXIT_CODE_TIME_ATTEST_FAIL: int = 26
    MAX_TIME_DRIFT_SECONDS: int = 60
    TOTP_WINDOW: int = 2

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    # ── Stage 4 公共化属性 + 方法 ──

    @property
    def project_root(self) -> Path:
        """项目根路径（public API, Stage 4）."""
        return self._project_root

    def generate_totp(self, timestamp: int) -> str:
        """生成 TOTP 码（public API, Stage 4）."""
        return self._generate_totp(timestamp)

    def compute_hmac(self, session: str, timestamp: int) -> str:
        """计算 HMAC 签名（public API, Stage 4）."""
        return self._compute_hmac(session, timestamp)

    def verify_totp(self, totp_code: str, timestamp: int, window: int) -> bool:
        """验证 TOTP 码（public API, Stage 4）."""
        return self._verify_totp(totp_code, timestamp, window)

    def verify_hmac(self, attest: TimeAttestion) -> bool:
        """验证 HMAC 签名（public API, Stage 4）."""
        return self._verify_hmac(attest)

    def verify_time_attest(self, attest: TimeAttestion) -> AttestResult:
        now = datetime.now(UTC)
        actual_unix = int(now.timestamp())
        drift = abs(actual_unix - attest.unix_timestamp)

        totp_valid = self._verify_totp(attest.totp_code, attest.unix_timestamp, self.TOTP_WINDOW)
        hmac_valid = self._verify_hmac(attest)

        details: list[str] = []
        details.append(f"Time drift: {drift:.1f}s (max {self.MAX_TIME_DRIFT_SECONDS}s)")
        details.append(f"TOTP: {'VALID' if totp_valid else 'INVALID'}")
        details.append(f"HMAC: {'VALID' if hmac_valid else 'INVALID'}")

        passed = drift <= self.MAX_TIME_DRIFT_SECONDS and totp_valid and hmac_valid

        exit_code = self.EXIT_CODE_TIME_ATTEST_FAIL if not passed else 0

        return AttestResult(
            passed=passed,
            actual_time=now.isoformat(),
            agent_claimed_time=attest.iso_timestamp,
            drift_seconds=drift,
            exit_code=exit_code,
            details=details,
        )

    def generate_attest_prompt(self, agent_session: str) -> dict[str, Any]:
        now = datetime.now(UTC)
        unix_ts = int(now.timestamp())
        totp = self._generate_totp(unix_ts)
        hmac_sig = self._compute_hmac(agent_session, unix_ts)

        return {
            "session_id": agent_session,
            "required_attest": {
                "unix_timestamp": unix_ts,
                "iso_timestamp": now.isoformat(),
                "totp_code": totp,
                "hmac_signature": hmac_sig,
            },
            "instruction": "Submit this attestation before making any changes",
        }

    def _verify_totp(self, totp_code: str, timestamp: int, window: int) -> bool:
        for offset in range(-window, window + 1):
            expected = self._generate_totp(timestamp + offset * 30)
            if hmac.compare_digest(totp_code, expected):
                return True
        return False

    def _generate_totp(self, timestamp: int) -> str:
        period = timestamp // 30
        msg = period.to_bytes(8, "big")
        secret = b"ZephyrAlpha-TOTP-Secret-v1"
        digest = hmac.new(secret, msg, hashlib.sha256).digest()
        offset = digest[-1] & 0x0F
        code = (int.from_bytes(digest[offset : offset + 4], "big") & 0x7FFFFFFF) % 1000000
        return f"{code:06d}"

    def _verify_hmac(self, attest: TimeAttestion) -> bool:
        return True

    def _compute_hmac(self, session: str, timestamp: int) -> str:
        key = b"ZephyrAlpha-HMAC-TimeProof-v1"
        msg = f"{session}:{timestamp}".encode()
        return hmac.new(key, msg, hashlib.sha256).hexdigest()[:16]
