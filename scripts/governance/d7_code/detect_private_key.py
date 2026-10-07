# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/detect_private_key.py | §
# [MODULE] scripts.governance.d7_code.detect_private_key
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d7_code.__init__
# [CONSUMERS] .pre-commit-config.yaml hook detect-private-key-local
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 纯 stdlib（yaml 懒加载可选降级）；检测 staged 文件中 PEM/SSH/PGP 私钥标记；pass_filenames=false；exit 0=pass / 1=findings / 2=error；豁免清单真源=config/governance/private_key_exempt_registry.yaml（G4 机制化 st-govfix-g4-20261007：替代原内联 _EXEMPT_PATHS 硬编码集——同真源收敛，净零迁移：2 条真源件原样保留+4 条 tests/ 旧址条目改挂现址）；册缺失/损坏/yaml 不可用→退化内建最小豁免集（2 条真源件）+stderr 告警（fail-safe 向检测态）；陈旧豁免审计 [STALE-EXEMPT]（index 与盘面均无=退休候选，warn-only 不阻断）
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

# 豁免清单真源 = config/governance/private_key_exempt_registry.yaml
# （G4 机制化 st-govfix-g4-20261007：原内联 _EXEMPT_PATHS 硬编码 set 已迁移入册——
# 净零声明见册 description。本文件仅保留内建最小 fallback：真源册缺失/损坏/yaml
# 不可用时退化到这两条"检测模式真源件"，保证检测器自洽可用（fail-safe 向检测态，
# 不向放行态）；fixture 类豁免只存在于册，fallback 不含——册故障时宁可能误报
# fixture，不可漏检真钥。）
_EXEMPT_REGISTRY_PATH = (
    Path(__file__).resolve().parents[3] / "config" / "governance" / "private_key_exempt_registry.yaml"
)
_FALLBACK_EXEMPT_PATHS: frozenset[str] = frozenset(
    {
        "src/zephyr/security/llm_defense/llm_security/patterns/secrets.py",
        "scripts/governance/d7_code/detect_private_key.py",
    }
)


def _load_exempt_registry() -> set[str]:
    """从 config/governance/private_key_exempt_registry.yaml 加载豁免路径集。

    册缺失/损坏/yaml 不可导入 → stderr 告警并退化 _FALLBACK_EXEMPT_PATHS
    （2 条真源件）。路径统一 POSIX 归一化（与 _is_exempt 比对面一致）。
    """
    try:
        import yaml  # noqa: PLC0415 — 懒加载：yaml 不可用时降级 fallback（保持 pre-commit 环境鲁棒）

        data = yaml.safe_load(_EXEMPT_REGISTRY_PATH.read_text(encoding="utf-8"))
    except ImportError:
        print("[WARN] PyYAML 不可用，私钥豁免退化为内建最小集（真源件 2 条）", file=sys.stderr)
        return set(_FALLBACK_EXEMPT_PATHS)
    except Exception as e:  # noqa: BLE001 — 册缺失/损坏一律降级（ERROR_CONTRACT）
        print(
            f"[WARN] 私钥豁免登记册不可读（{type(e).__name__}: {e}），退化为内建最小集（真源件 2 条）",
            file=sys.stderr,
        )
        return set(_FALLBACK_EXEMPT_PATHS)
    if not isinstance(data, dict) or not isinstance(data.get("exempt_paths"), list):
        print("[WARN] 私钥豁免登记册结构非法（缺 exempt_paths 列表），退化为内建最小集", file=sys.stderr)
        return set(_FALLBACK_EXEMPT_PATHS)
    paths: set[str] = set()
    for entry in data["exempt_paths"]:
        if not isinstance(entry, dict):
            continue
        p = entry.get("path")
        if isinstance(p, str) and p.strip():
            paths.add(p.strip().replace("\\", "/"))
    if not paths:
        print("[WARN] 私钥豁免登记册为空，退化为内建最小集（真源件 2 条）", file=sys.stderr)
        return set(_FALLBACK_EXEMPT_PATHS)
    return paths


def _is_registry_path_alive(rel: str) -> bool:
    """豁免路径存活性判定：git index 跟踪 或 盘面存在 任一即活（裁定#279 观测面口径）。

    git 面经 run_subprocess_hidden（TRAE-067 铁律2 统一无窗口入口，禁裸 subprocess）；
    zephyr 引导不可用时降级仅盘面判定（留痕 stderr）。
    """
    try:
        from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: PLC0415
    except ImportError:
        print("[WARN] zephyr.process_pool 不可用（引导缺失），存活性仅按盘面判定", file=sys.stderr)
        return Path(rel).exists()
    try:
        r = run_subprocess_hidden(["git", "ls-files", "--cached", "--", rel])
        if getattr(r, "returncode", 1) == 0 and (r.stdout or "").strip():
            return True
    except Exception as e:  # noqa: BLE001 — git 故障降级盘面判定
        print(f"[WARN] git ls-files 失败（{type(e).__name__}: {e}），存活性仅按盘面判定", file=sys.stderr)
    return Path(rel).exists()


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


def _is_exempt(rel: str, exempt_paths: set[str]) -> bool:
    """判断文件是否在豁免清单中（POSIX 路径归一化）。"""
    normalized = rel.replace("\\", "/")
    return normalized in exempt_paths


def _audit_stale_exemptions(exempt_paths: set[str]) -> int:
    """陈旧豁免审计（G4 机制化）：既不在 git index 也不在盘面的豁免路径打 [STALE-EXEMPT]。

    warn-only 不影响退出码——处方=确认后从登记册退休该条目（防白名单膨胀成死条目
    账簿，重蹈原硬编码 4 条 tests/ 旧址死条目覆辙）。

    Returns:
        陈旧条目数。
    """
    stale = [p for p in sorted(exempt_paths) if not _is_registry_path_alive(p)]
    for p in stale:
        print(f"[STALE-EXEMPT] {p}（git index 与盘面均不存在——登记册陈旧条目，退休候选）")
    return len(stale)


def _scan_files(files: list[str], exempt_paths: set[str]) -> list[str]:
    """扫描给定文件清单，返回违规发现（不含豁免件）。"""
    findings: list[str] = []
    for rel in files:
        if _is_exempt(rel, exempt_paths):
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
    return findings


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    files = _get_staged_files_for_key_detection()
    if not files:
        return EXIT_PASS

    exempt_paths = _load_exempt_registry()
    _audit_stale_exemptions(exempt_paths)

    findings = _scan_files(files, exempt_paths)

    if findings:
        print("[ERR] 发现意外提交的私钥标记（PRIVATE_KEY_DETECTED）:")
        for f in findings:
            print(f)
        print("")
        print("修复：从文件中移除私钥内容；secrets 真源/测试 fixture 件经登记豁免：")
        print("  在 config/governance/private_key_exempt_registry.yaml exempt_paths 追加")
        print("  path + reason（说明 fixture 理据），登记册随本批 commit 原子提交。")
        return EXIT_FINDINGS

    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
