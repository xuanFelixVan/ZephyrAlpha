# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.io.content_fingerprint
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_content_fingerprint | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""SHA-256 content fingerprint computation and verification.

Provides file-level SHA-256 fingerprinting for scaffold legacy marking
and beta migration verification.

Task: T-1-10 | experimental | Composer 2
ADR ref: ADR-0037 (pending Opus authoring)
"""

from __future__ import annotations

import hashlib
from pathlib import Path


class FingerprintError(Exception):
    """内容指纹系统异常基类（所有指纹相关异常由此派生）。"""

    pass


class FingerprintNotFoundError(FingerprintError):
    """请求的指纹 key 在指纹库中不存在。"""

    pass


class FingerprintPermissionError(FingerprintError):
    """无权读取或写入指定路径的指纹文件（文件系统权限不足）。"""

    pass


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
        raise FingerprintNotFoundError(f"File not found: {path}")
    except PermissionError:
        raise FingerprintPermissionError(f"Permission denied: {path}")
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
