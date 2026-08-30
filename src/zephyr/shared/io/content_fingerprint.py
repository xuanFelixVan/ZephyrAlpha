# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.io.content_fingerprint
# [DOMAIN] D_SHARED
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
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
SHA-256 content fingerprint computation and verification.

Provides file-level SHA-256 fingerprinting for scaffold legacy marking
and beta migration verification.

Task: T-1-10 | experimental | Composer 2
ADR ref: ADR-0037 (pending Opus authoring)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: path 参数
#   fields: 参数 path，类型注解 str | Path
#   code: content_fingerprint.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: expected 参数
#   fields: 参数 expected，类型注解 str
#   code: content_fingerprint.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: paths 参数
#   fields: 参数 paths，类型注解 list[str | Path]
#   code: content_fingerprint.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① compute_hash
#   name_en: compute_hash
#   intro: compute_hash(path) 源码 L128-L142
#   desc: 源码 L128-L142
#   inputs: path
#   outputs: str
# - id: A2
#   name_zh: ② verify_hash
#   name_en: verify_hash
#   intro: verify_hash(path, expected) 源码 L145-L147
#   desc: 源码 L145-L147
#   inputs: path expected
#   outputs: bool
# - id: A3
#   name_zh: ③ compute_bulk
#   name_en: compute_bulk
#   intro: compute_bulk(paths) 源码 L150-L157
#   desc: 源码 L150-L157
#   inputs: paths
#   outputs: dict[str, str | None]
#   （注：A3 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import hashlib
from pathlib import Path


class FingerprintError(Exception):
    """内容指纹系统异常基类（所有指纹相关异常由此派生）。"""

    error_code = "ZA-SH-0038"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class FingerprintNotFoundError(FingerprintError):
    """请求的指纹 key 在指纹库中不存在。"""

    error_code = "ZA-SH-0039"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class FingerprintPermissionError(FingerprintError):
    """无权读取或写入指定路径的指纹文件（文件系统权限不足）。"""

    error_code = "ZA-SH-0040"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


_CHUNK_SIZE = 8192


def compute_hash(path: str | Path) -> str:
    path = Path(path)
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while True:
                chunk = f.read(_CHUNK_SIZE)
                if not chunk:
                    break
                h.update(chunk)
    except FileNotFoundError:
        raise FingerprintNotFoundError("File not found") from None
    except PermissionError:
        raise FingerprintPermissionError("Permission denied") from None
    return h.hexdigest()


def verify_hash(path: str | Path, expected: str) -> bool:
    actual = compute_hash(path)
    return actual == expected.lower()


def compute_bulk(paths: list[str | Path]) -> dict[str, str | None]:
    results: dict[str, str | None] = {}
    for p in paths:
        try:
            results[str(p)] = compute_hash(p)
        except FingerprintError:
            results[str(p)] = None
    return results
