# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §16
# [MODULE] scripts.record_session_start_commit
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS] project_rules.md 进门流程; PostDocReviewScanner._get_session_start_commit()
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] session_start_commit.txt 必须是 40 位十六进制 commit hash
# [MODIFY-GUARD] post_doc_review_check.py R1 防御依赖此脚本输出的文件
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] git 不可用 → exit 1; session_id 为空 → exit 1
# [TESTS] tests/test_post_doc_review.py
# [A_module] module_id=MOD-SCRIPT-record_session_start_commit | layer=script | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
记录 session 起点 commit hash——R1 防御数据流起点。

Session 开始时执行此脚本，将当前 git HEAD commit hash 写入
session_logs/<session_id>/session_start_commit.txt。

PostDocReviewScanner 在 session 关门时读取此文件，用 git diff
获取权威修改文件列表，对比 modified_files.json 自报告列表，
检测篡改（删除修改记录/虚报告）。

用法:
    python scripts/record_session_start_commit.py <session_id>
"""

import re
import subprocess
import sys
from pathlib import Path

# bootstrap: 定位 scripts/governance/ 以 import _shared.constants（REPO_ROOT SSoT 真源）
_GOV_DIR = str(Path(__file__).resolve().parent / "governance")
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT as PROJECT_ROOT  # noqa: E402

_COMMIT_HASH_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: python scripts/record_session_start_commit.py <session_id>")
        return 1

    session_id = sys.argv[1]

    # 校验 session_id（防路径遍历）
    if not re.match(r"^[A-Za-z0-9_\-]+$", session_id):
        print(f"ERROR: session_id 含非法字符: {session_id!r}")
        return 1

    # 获取当前 git HEAD commit hash
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode != 0:
            print(f"ERROR: git rev-parse HEAD 失败: {result.stderr}")
            return 1
        commit_hash = result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        print(f"ERROR: git 不可用: {exc}")
        return 1

    # 校验 commit hash 格式（40 位十六进制）
    if not _COMMIT_HASH_PATTERN.match(commit_hash):
        print(f"ERROR: commit hash 格式非法: {commit_hash!r}")
        return 1

    # 写入 session_logs/<session_id>/session_start_commit.txt
    session_dir = PROJECT_ROOT / "session_logs" / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    commit_file = session_dir / "session_start_commit.txt"
    commit_file.write_text(commit_hash, encoding="utf-8")

    print(f"OK: session_start_commit.txt 已写入 {commit_file}")
    print(f"     session_id: {session_id}")
    print(f"     commit: {commit_hash}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
