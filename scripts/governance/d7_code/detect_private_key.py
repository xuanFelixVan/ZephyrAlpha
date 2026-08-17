# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/detect_private_key.py | §
# [MODULE] scripts.governance.d7_code.detect_private_key
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d7_code.__init__
# [CONSUMERS] .pre-commit-config.yaml hook detect-private-key-local
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 纯 stdlib；检测 staged 文件中 PEM/SSH/PGP 私钥标记；pass_filenames=false；exit 0=pass / 1=findings / 2=error；含 secrets.py 等豁免清单
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 永不抛异常——git 失败/I/O 异常降级为 exit 2 + stderr 提示
# [TESTS] tests/governance/test_detect_private_key.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""detect_private_key.py — 私钥意外提交检测（local 替代 external pre-commit-hooks）

裁定 #ARCH-PRECOMMIT-OFFLINE-001 Phase 1 治本：
原 .pre-commit-config.yaml 引用外部 GitHub repo `pre-commit/pre-commit-hooks`
的 `detect-private-key` hook，导致 pre-commit 工具在缓存失效/首次安装时
尝试 `git fetch origin --tags` 拉取远程 repo——代理（127.0.0.1:10808）未启动
或离线环境会卡死所有 commit。

本脚本用纯 stdlib 等价替代，无任何网络依赖。检测 staged 文件中的
PEM/SSH/PGP 私钥标记（BEGIN PRIVATE KEY / BEGIN OPENSSH PRIVATE KEY 等）。

exit codes: 0=pass, 1=findings(发现私钥标记), 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: >
  检测 staged 文件中意外提交的私钥标记（BEGIN PRIVATE KEY / BEGIN OPENSSH PRIVATE KEY 等）。
  纯 stdlib 替代 external pre-commit-hooks detect-private-key（裁定 #ARCH-PRECOMMIT-OFFLINE-001）。
dimensions:
- D7
priority: P1
timeout_seconds: 10
warn_only: false
"""

import re
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS  # noqa: E402

# 私钥标记正则——对标 pre-commit-hooks detect-private-key
# 匹配 PEM 头 / SSH 头 / PGP 头（大小写敏感，PEM 标准规定大写）
_PRIVATE_KEY_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"),
    re.compile(r"-----BEGIN (?:ENCRYPTED )?PRIVATE KEY-----"),
    re.compile(r"-----BEGIN PGP PRIVATE KEY BLOCK-----"),
]

# 豁免清单（对标原 .pre-commit-config.yaml 的 exclude）
# 这些文件本身是 secrets 检测模式的真源 / 测试 fixture，必然含私钥样例字符串
_EXEMPT_PATHS: set[str] = {
    "src/zephyr/security/llm_defense/llm_security/patterns/secrets.py",
    "tests/test_fix_safety.py",
    "tests/fix/test_auto_fix_core.py",
    "tests/llm_security/test_secrets.py",
    "tests/test_credential_rotation_trigger.py",
}


def _get_staged_files_for_key_detection() -> list[str]:
    """获取 staged 文件列表（新增/修改/重命名后）。"""
    try:
        r = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        print(f"[ERR] git diff 失败: {type(e).__name__}: {e}", file=sys.stderr)
        return []
    if r.returncode != 0:
        print(f"[ERR] git diff rc={r.returncode}: {r.stderr}", file=sys.stderr)
        return []
    return [f for f in r.stdout.strip().split("\n") if f]


def _is_likely_text(filepath: Path) -> bool:
    """快速判断是否为文本文件（避免扫描二进制）。"""
    if not filepath.is_file():
        return False
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(8192)
        if b"\x00" in chunk:
            return False
        chunk.decode("utf-8")
        return True
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return False


def _is_exempt(rel: str) -> bool:
    """判断文件是否在豁免清单中（POSIX 路径归一化）。"""
    normalized = rel.replace("\\", "/")
    return normalized in _EXEMPT_PATHS


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    files = _get_staged_files_for_key_detection()
    if not files:
        return EXIT_PASS

    findings: list[str] = []
    for rel in files:
        if _is_exempt(rel):
            continue
        path = Path(rel)
        if not _is_likely_text(path):
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            print(f"[WARN] 跳过不可读文件 {rel}: {type(e).__name__}: {e}", file=sys.stderr)
            continue
        for pattern in _PRIVATE_KEY_PATTERNS:
            matches = pattern.findall(content)
            if matches:
                findings.append(f"  {rel}: 发现 {len(matches)} 处私钥标记 ({pattern.pattern})")
                break  # 同文件多模式只报一次

    if findings:
        print("[ERR] 发现意外提交的私钥标记（PRIVATE_KEY_DETECTED）:")
        for f in findings:
            print(f)
        print("")
        print("修复：从文件中移除私钥内容，或将文件加入 _EXEMPT_PATHS（仅限 secrets 真源/测试 fixture）。")
        return EXIT_FINDINGS

    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
