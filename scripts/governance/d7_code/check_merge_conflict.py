# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/check_merge_conflict.py | §
# [MODULE] scripts.governance.d7_code.check_merge_conflict
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d7_code.__init__
# [CONSUMERS] .pre-commit-config.yaml hook check-merge-conflict-marker
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 纯 stdlib；检测 staged 文件中 <<<<<<< / ======= / >>>>>>> 合并冲突标记；pass_filenames=false；exit 0=pass / 1=findings / 2=error
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 永不抛异常——git 失败/I/O 异常降级为 exit 2 + stderr 提示
# [TESTS] tests/governance/test_check_merge_conflict.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""check_merge_conflict.py — 合并冲突标记检测（local 替代 external pre-commit-hooks）

裁定 #ARCH-PRECOMMIT-OFFLINE-001 Phase 1 治本：
原 .pre-commit-config.yaml 引用外部 GitHub repo `pre-commit/pre-commit-hooks`
的 `check-merge-conflict` hook，导致 pre-commit 工具在缓存失效/首次安装时
尝试 `git fetch origin --tags` 拉取远程 repo——代理（127.0.0.1:10808）未启动
或离线环境会卡死所有 commit（包括合法 gateway 路径外的兜底场景）。

本脚本用纯 stdlib 等价替代，无任何网络依赖。检测 staged 文件中的
<<<<<<< / ======= / >>>>>>> 合并冲突标记（标准 git conflict markers）。

exit codes: 0=pass, 1=findings(发现冲突标记), 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: >
  检测 staged 文件中未解决的合并冲突标记（<<<<<<< / ======= / >>>>>>>）。
  纯 stdlib 替代 external pre-commit-hooks check-merge-conflict（裁定 #ARCH-PRECOMMIT-OFFLINE-001）。
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

# 合并冲突标记正则：
# - <<<<<<< ...（冲突开始，7 个 <）
# - =======    （分隔符，必须独占一行——避免误匹配代码中的 === 注释）
# - >>>>>>> ...（冲突结束，7 个 >）
# 注：======= 必须独占一行，否则会误匹配 Python/JS 中的等号赋值
_CONFLICT_MARKER_RE = re.compile(
    r"^(<{7}|={7}|>{7})(?:\s.*)?$",
    re.MULTILINE,
)


def _get_staged_files_for_conflict_check() -> list[str]:
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


def _is_text_file(filepath: Path) -> bool:
    """快速判断是否为文本文件（避免扫描二进制）。"""
    if not filepath.is_file():
        return False
    # 常见文本扩展名白名单（对标 pre-commit-hooks check-merge-conflict 行为）
    text_exts = {
        ".py", ".md", ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg",
        ".txt", ".sh", ".bat", ".ps1", ".sql", ".html", ".css", ".xml",
        ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h", ".hpp",
        ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".scala",
        ".editorconfig", ".gitignore", ".dockerfile",
    }
    if filepath.suffix.lower() in text_exts:
        return True
    # 无扩展名或未知扩展名：读前 8KB 检测 NULL 字节
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(8192)
        if b"\x00" in chunk:
            return False
        chunk.decode("utf-8")
        return True
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return False


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    files = _get_staged_files_for_conflict_check()
    if not files:
        return EXIT_PASS

    findings: list[str] = []
    for rel in files:
        path = Path(rel)
        if not _is_text_file(path):
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            print(f"[WARN] 跳过不可读文件 {rel}: {type(e).__name__}: {e}", file=sys.stderr)
            continue
        matches = _CONFLICT_MARKER_RE.findall(content)
        if matches:
            findings.append(f"  {rel}: 发现 {len(matches)} 处合并冲突标记")

    if findings:
        print("[ERR] 发现未解决的合并冲突标记（MERGE_CONFLICT_MARKER）:")
        for f in findings:
            print(f)
        print("")
        print("修复：手动编辑文件解决冲突，移除 <<<<<<< / ======= / >>>>>>> 标记，")
        print("     然后 git add <file> 重新提交。")
        return EXIT_FINDINGS

    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
