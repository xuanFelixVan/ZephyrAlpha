# [BLUEPRINT] MOD-DATSEC-003 | docs/03_modules/_domain_data_security/data_masking_engine/blueprint.md
# [MODULE] zephyr.data_security.data_masking_engine
# [DOMAIN] D_DATA_SEC
# [DEPENDENCIES] 无（引擎核心纯内存；cipher/rng 全注入）
# [CONSUMERS] 运行时装配批（身份证/账号出库加密装配点 / 按角色查询出参动态脱敏 / 统计输出差分隐私）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 掩码词表闭合(none|full|partial|hash); FPE 格式保留(数字→数字/小写→小写/大写→大写，其余字符原样); 默认伪FPE确定性可逆且非密码学安全; 角色策略表未注册 Fail-Closed; 拉普拉斯噪声 ε>0 且 sensitivity>0，随机源注入; 同输入必同输出(随机源固定时)
# [MODIFY-GUARD] docs/03_modules/_domain_data_security/data_masking_engine/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DataMaskingError(占位 ZA-DSEC-UNREGISTERED-DATA-MASKING)——空key/空文本/未注册角色字段策略/非法掩码类型/ε或sensitivity非正/非法随机源输出时抛
# [TESTS] tests/data_security/test_data_masking_engine.py
# [A_module] module_id=MOD-DATSEC-003 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""



DataMaskingEngine — 数据脱敏引擎（MOD-DATSEC-003）。

B13-04295（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATSEC-003，A3数据架构）：
**格式保留加密 FPE**（身份证/账号：注入 cipher 回调，默认**确定性伪 FPE 占
位实现——非密码学安全**，仅限占位联调，上线必须注入真 cipher）+ **动态脱
敏**（按查询角色策略表：同字段不同角色不同掩码）+ **差分隐私噪声**（统计
输出拉普拉斯噪声，ε 可配，随机源注入）。策略表与 MOD-DATSEC-001 共用 schema
语义（Mapping 键查表、未注册 Fail-Closed）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: key 参数
#   fields: 参数 key（无注解）
#   code: data_masking_engine.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: cipher 参数
#   fields: 参数 cipher（无注解）
#   code: data_masking_engine.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: rng 参数
#   fields: 参数 rng（无注解）
#   code: data_masking_engine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① DataMaskingEngine
#   name_en: DataMaskingEngine
#   intro: 脱敏引擎（FPE + 角色动态脱敏 + 拉普拉斯差分隐私噪声）。
#   desc: 脱敏引擎（FPE + 角色动态脱敏 + 拉普拉斯差分隐私噪声）。；公共方法（定义序）: fpe_encrypt, fpe_decrypt, register_policy, policy_of, mask_field,…
#   inputs: key cipher rng
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: DataMaskingEngine
#   downstream: 运行时装配批（身份证/账号出库加密装配点 / 按角色查询出参动态脱敏 / 统计输出差分隐私）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import logging
import math
import random
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "DataMaskingEngine",
    "DataMaskingError",
    "MaskKind",
]

#: FPE 格式保留字符类（类内置换，类外字符原样保留）
_CLASS_DIGITS: Final = "0123456789"
_CLASS_LOWER: Final = "abcdefghijklmnopqrstuvwxyz"
_CLASS_UPPER: Final = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

#: rng 输出端点保护（避免 log(0)）
_EPS_GUARD: Final = 1e-12


class DataMaskingError(Exception):
    """脱敏引擎输入/策略非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-DSEC-UNREGISTERED-DATA-MASKING。
    """


class MaskKind(str, Enum):
    """动态脱敏掩码类型（词表闭合）。"""

    NONE = "none"
    FULL = "full"
    PARTIAL = "partial"
    HASH = "hash"


class DataMaskingEngine:
    """脱敏引擎（FPE + 角色动态脱敏 + 拉普拉斯差分隐私噪声）。"""

    def __init__(
        self,
        *,
        key: str = "zephyr-pseudo-fpe",
        cipher: Callable[[str, str, bool], str] | None = None,
        rng: Callable[[], float] | None = None,
    ) -> None:
        if not key:
            raise DataMaskingError("key 为空")
        self._key = key
        self._cipher = cipher
        self._rng = rng or random.random
        self._policies: dict[tuple[str, str], MaskKind] = {}

    # ── 格式保留加密（默认伪 FPE 占位，非密码学安全） ─────────────────────

    def _keystream_byte(self, class_id: str, index: int) -> int:
        digest = hashlib.sha256(f"{self._key}|{class_id}|{index}".encode()).digest()
        return int.from_bytes(digest[:4], "big")

    def _fpe_default(self, text: str, encrypt: bool) -> str:
        """默认确定性伪 FPE：类内位移置换，可逆；⚠ 非密码学安全占位实现。"""
        counters = {_CLASS_DIGITS: 0, _CLASS_LOWER: 0, _CLASS_UPPER: 0}
        out: list[str] = []
        for ch in text:
            for class_id, alphabet in (
                ("digits", _CLASS_DIGITS),
                ("lower", _CLASS_LOWER),
                ("upper", _CLASS_UPPER),
            ):
                if ch in alphabet:
                    i = counters[alphabet]
                    counters[alphabet] += 1
                    shift = self._keystream_byte(class_id, i) % len(alphabet)
                    idx = alphabet.index(ch)
                    idx = (idx + shift) % len(alphabet) if encrypt else (idx - shift) % len(alphabet)
                    out.append(alphabet[idx])
                    break
            else:
                out.append(ch)
        return "".join(out)

    def fpe_encrypt(self, text: str) -> str:
        """格式保留加密（注入 cipher 则委托，否则默认伪 FPE 占位）。"""
        if not isinstance(text, str) or not text:
            raise DataMaskingError("text 为空（无可加密载荷）")
        if self._cipher is not None:
            return self._cipher(text, self._key, True)
        return self._fpe_default(text, True)

    def fpe_decrypt(self, text: str) -> str:
        """格式保留解密（与 fpe_encrypt 互逆）。"""
        if not isinstance(text, str) or not text:
            raise DataMaskingError("text 为空（无可解密载荷）")
        if self._cipher is not None:
            return self._cipher(text, self._key, False)
        return self._fpe_default(text, False)

    # ── 动态脱敏（角色策略表） ────────────────────────────────────────────

    def register_policy(self, role: str, field: str, kind: MaskKind) -> None:
        """登记角色字段掩码策略（覆盖式；非法输入 Fail-Closed）。"""
        if not role:
            raise DataMaskingError("role 为空")
        if not field:
            raise DataMaskingError("field 为空")
        if not isinstance(kind, MaskKind):
            raise DataMaskingError(f"非法掩码类型: {kind!r}")
        self._policies[(role, field)] = kind

    def policy_of(self, role: str, field: str) -> MaskKind:
        """角色字段策略查询（未注册 → Fail-Closed 拒绝放行）。"""
        kind = self._policies.get((role, field))
        if kind is None:
            raise DataMaskingError(f"未注册策略: role={role!r} field={field!r}")
        return kind

    def mask_field(self, role: str, field: str, value: str) -> str:
        """按角色策略动态脱敏（同字段不同角色不同掩码）。"""
        kind = self.policy_of(role, field)
        if not isinstance(value, str):
            raise DataMaskingError(f"value 非字符串: {type(value).__name__}")
        if kind is MaskKind.NONE:
            return value
        if kind is MaskKind.FULL:
            return "*" * len(value)
        if kind is MaskKind.HASH:
            return "h:" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:8]
        # PARTIAL：保首保尾，中间掩码
        if len(value) >= 3:
            return f"{value[0]}{'*' * (len(value) - 2)}{value[-1]}"
        if len(value) == 2:
            return f"{value[0]}*"
        return "*" * len(value)

    # ── 差分隐私（拉普拉斯噪声） ──────────────────────────────────────────

    def add_laplace_noise(self, value: float, epsilon: float, sensitivity: float = 1.0) -> float:
        """拉普拉斯机制：value + Lap(0, sensitivity/ε)，随机源注入可复现。"""
        if not isinstance(value, (int, float)):
            raise DataMaskingError(f"value 非数值: {type(value).__name__}")
        if epsilon <= 0:
            raise DataMaskingError(f"epsilon 非正: {epsilon}")
        if sensitivity <= 0:
            raise DataMaskingError(f"sensitivity 非正: {sensitivity}")
        u = self._rng()
        if not isinstance(u, (int, float)) or not 0.0 <= u < 1.0:
            raise DataMaskingError(f"rng 输出越界 [0,1): {u!r}")
        u = min(max(u, _EPS_GUARD), 1.0 - _EPS_GUARD) - 0.5
        scale = sensitivity / epsilon
        # 逆 CDF：noise = -scale·sign(u)·ln(1-2|u|)（u>0 取正侧，u<0 取负侧）
        noise = -scale * math.log(1.0 - 2.0 * abs(u)) * math.copysign(1.0, u)
        out = value + noise
        _log.debug("差分隐私噪声: value=%s eps=%s sens=%s -> %s", value, epsilon, sensitivity, out)
        return out
